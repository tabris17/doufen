# encoding: utf-8
import datetime
import json
import logging
import re
from abc import abstractmethod
from collections import OrderedDict
from time import sleep, time
from urllib.parse import urljoin
from http import cookies

from pyquery import PyQuery
import requests
from requests.exceptions import TooManyRedirects

import db
from db import dbo
from .exceptions import *


DOUBAN_URL = 'https://www.douban.com/'
REQUEST_TIMEOUT = 5
REQUEST_RETRY_TIMES = 5
FAKE_API_KEY = '04f1ddfc67bddc4a0ed599f5373994de'

# type: {music|book|movie}; status: {mark|doing|done}
URL_INTERESTS_API = 'https://m.douban.com/rexxar/api/v2/user/{uid}/interests?type={type}&status={status}&start={{start}}&count=50&ck={ck}&for_mobile=1'


class Task:
    """
    工作任务
    """
    _id = 1
    _name = '任务'

    def __init__(self, account):
        class_type = type(self)
        self._name = '{name}#{id}'.format(name=class_type._name, id=class_type._id)
        class_type._id += 1

        self._account = account

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name

    def __call__(self, **kwargs):
        self._settings = kwargs
        self._proxy = {
            'http': kwargs['proxy'],
            'https': kwargs['proxy'],
        } if 'proxy' in kwargs else None
        requests_per_minute = kwargs['requests_per_minute']
        self._min_request_interval = 60 / requests_per_minute
        self._local_object_duration = kwargs['local_object_duration']
        self._last_request_at = time()
        session = requests.Session()
        session.headers.update({
            'Cookie': self._account.session,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.105 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Referer': 'https://www.douban.com/',
        })
        self._session = session

        cookie = cookies.SimpleCookie()
        cookie.load(self._account.session)
        self._account_cookie = cookie

        try:
            return self.run()
        except (TooManyRedirects, Forbidden):
            logging.debug('Login session maybe forbidden')
            self._account.is_invalid = True
            self._account.save()
            return False
        #except Exception as e:
        #    logging.debug(e)
        #    return False
        finally:
            session.close()
    
    def is_oject_expired(self, obj):
        now = datetime.datetime.now()
        return (now - obj.updated_at).seconds > self._local_object_duration

    def get_setting(self, name, default=None):
        return self._settings.get(name, default)

    def fetch_url_content(self, url, base_url=DOUBAN_URL):
        url = urljoin(base_url, url)

        error_count = 0
        while error_count < REQUEST_RETRY_TIMES:
            now = time()
            remaining = self._min_request_interval + self._last_request_at - now
            if remaining > 0:
                sleep(remaining)
            self._last_request_at = now

            try:
                logging.info('fetch URL {0}'.format(url))
                response = self._session.get(url, proxies=self._proxy, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                logging.error('fetch URL "{0}" error, response code: {1}'.format(url, response.status_code))
                break
            except Exception as e:
                error_count += 1
                logging.warn('fetch URL "{0}" error: {1}'.format(url, e))

        logging.error('fetch URL "{0}" error: retries exceeded'.format(url))

    @property
    def account(self):
        return self._account

    @abstractmethod
    def run(self):
        raise NotImplementedError()

    def equals(self, task):
        """
        比较两个任务是否相同
        """
        return isinstance(task, type(self)) and self._account.id == task._account.id

    @dbo.atomic()
    def save_user(self, detail):
        """
        用户信息入库
        """
        douban_id = detail['id']
        detail['douban_id'] = douban_id
        detail['unique_name'] = detail['uid']
        detail['version'] = 1
        detail['updated_at'] = datetime.datetime.now()
        del detail['id']
        del detail['uid']

        try:
            user = db.User.safe_create(**detail)
            logging.debug('create user: ' + user.unique_name)
        except db.IntegrityError:
            user = db.User.get(db.User.douban_id == douban_id)
            
            if not user.equals(detail):
                db.UserHistorical.clone(user)
                detail['version'] = db.User.version + 1
                db.User.safe_update(**detail).where(db.User.id == user.id).execute()
        return user

    @dbo.atomic()
    def save_movie(self, detail):
        douban_id = detail['id']
        detail['douban_id'] = douban_id
        detail['version'] = 1
        detail['updated_at'] = datetime.datetime.now()
        del detail['id']

        try:
            movie = db.Movie.safe_create(**detail)
            logging.debug('create movie: ' + movie.title)
        except db.IntegrityError:
            movie = db.Movie.get(db.Movie.douban_id == douban_id)
            
            if not movie.equals(detail):
                db.MovieHistorical.clone(movie)
                detail['version'] = db.Movie.version + 1
                db.Movie.safe_update(**detail).where(db.Movie.id == movie.id).execute()
        return movie

    def fetch_user(self, name):
        """
        尝试从本地获取用户信息，如果没有则从网上抓取
        """
        try:
            user = db.User.get(db.User.unique_name == name)
            if self.is_oject_expired(user):
                raise db.User.DoesNotExist()
        except db.User.DoesNotExist:
            user = self.fetch_user_by_api(name)

        return user

    def fetch_user_by_api(self, name):
        """
        通过豆瓣API获取用户信息
        """
        url = 'https://api.douban.com/v2/user/{0}?apikey={1}'.format(name, FAKE_API_KEY)
        response = self.fetch_url_content(url)
        if not response:
            return None

        detail = json.loads(response.text)
        return self.save_user(detail)

    def fetch_movie_by_api(self, id):
        """
        通过豆瓣API获取电影信息
        """
        url = 'https://api.douban.com/v2/movie/subject/{0}?apikey={1}'.format(id, FAKE_API_KEY)
        response = self.fetch_url_content(url)
        if not response:
            return None

        detail = json.loads(response.text)
        return self.save_movie(detail)

    def sync_account(self):
        """
        同步当前帐号信息
        """
        account = self._account
        user = self.fetch_user(account.name)
        if account.user is None:
            account.user = user
            account.save()
        return account

    def fetch_interests(self, media_type, status):
        interests_list = []
        url = URL_INTERESTS_API.format(
            status=status,
            type=media_type,
            uid=self.account.user.douban_id,
            ck=self._account_cookie['ck'].value
        )
        response = self.fetch_url_content(url.format(start=0))
        result = json.loads(response.text)
        total = result['total']
        interests_list.extend(result['interests'])

        for start in range(50, total, 50):
            response = self.fetch_url_content(url.format(start=start))
            result = json.loads(response.text)
            interests_list.extend(result['interests'])

        return interests_list


class FollowingFollowerTask(Task):
    _name = '我的友邻'

    def fetch_follow_list(self, user, action):
        url = 'https://api.douban.com/shuo/v2/users/{user}/{action}?count=50&page={page}'

        user_list = []
        page_count = 1
        while True:
            response = self.fetch_url_content(url.format(action=action, user=user, page=page_count))
            if not response:
                break
            user_list_partial = json.loads(response.text)
            if len(user_list_partial) == 0:
                break
            user_list.extend([user['uid'] for user in user_list_partial])
            page_count += 1

        user_list.reverse()
        return user_list

    def fetch_block_list(self):
        response = self.fetch_url_content('https://www.douban.com/contacts/blacklist')
        dom = PyQuery(response.text)
        strip_username = lambda el: re.findall(r'^http(?:s?)://www\.douban\.com/people/(.+)/$', PyQuery(el).attr('href')).pop(0)
        return [strip_username(item) for item in dom('dl.obu>dd>a')]

    @dbo.atomic()
    def save_following(self, account_user, following_users):
        now = datetime.datetime.now()
        for following_username, following_user in following_users.items():
            real_following_username = following_user.unique_name if following_user else following_username
            try:
                kwargs = {
                    'user': account_user,
                    'following_user': following_user,
                    'following_username': real_following_username,
                    'updated_at': now,
                }   
                db.Following(**kwargs).save()
            except db.IntegrityError:
                fw = db.Following.get(
                    db.Following.user == account_user,
                    db.Following.following_username == real_following_username
                )
                if not fw.following_user and following_user is not None :
                    fw.following_user = following_user
                if following_user and fw.following_username != following_user.unique_name:
                    fw.following_username = following_user.unique_name
                fw.updated_at = now
                fw.save()

        db.FollowingHistorical.insert_from(
            db.Following.select(
                db.Following.user,
                db.Following.following_user,
                db.Following.following_username,
                db.Following.created_at,
                db.Following.updated_at,
                db.fn.DATETIME('now')
            ).where(
                db.Following.user == account_user,
                db.Following.updated_at < now
            ),
            [
                db.FollowingHistorical.user,
                db.FollowingHistorical.following_user,
                db.FollowingHistorical.following_username,
                db.FollowingHistorical.created_at,
                db.FollowingHistorical.updated_at,
                db.FollowingHistorical.deleted_at,
            ]
        ).execute()

        db.Following.delete().where(
            db.Following.user == account_user, 
            db.Following.updated_at < now
        ).execute()

    @dbo.atomic()
    def save_followers(self, account_user, followers):
        now = datetime.datetime.now()
        for follower_username, follower in followers.items():
            try:
                kwargs = {
                    'user': account_user,
                    'follower': follower,
                    'follower_username': follower_username,
                    'updated_at': now,
                }   
                db.Follower(**kwargs).save()
            except db.IntegrityError:
                fw = db.Follower.get(
                    db.Follower.user == account_user,
                    db.Follower.follower_username == follower_username
                )
                if not fw.follower and follower is not None :
                    fw.follower = follower
                fw.updated_at = now
                fw.save()

        db.FollowerHistorical.insert_from(
            db.Follower.select(
                db.Follower.user,
                db.Follower.follower,
                db.Follower.follower_username,
                db.Follower.created_at,
                db.Follower.updated_at,
                db.fn.DATETIME('now')
            ).where(
                db.Follower.user == account_user,
                db.Follower.updated_at < now
            ),
            [
                db.FollowerHistorical.user,
                db.FollowerHistorical.follower,
                db.FollowerHistorical.follower_username,
                db.FollowerHistorical.created_at,
                db.FollowerHistorical.updated_at,
                db.FollowerHistorical.deleted_at,
            ]
        ).execute()

        db.Follower.delete().where(
            db.Follower.user == account_user, 
            db.Follower.updated_at < now
        ).execute()

    @dbo.atomic()
    def save_block_list(self, account_user, block_users):
        now = datetime.datetime.now()
        for block_username, block_user in block_users.items():
            try:
                kwargs = {
                    'user': account_user,
                    'block_user': block_user,
                    'block_username': block_username,
                    'updated_at': now,
                }   
                db.BlockUser(**kwargs).save()
            except db.IntegrityError:
                new_block_user = db.BlockUser.get(
                    db.BlockUser.user == account_user,
                    db.BlockUser.block_username == block_username
                )
                if not new_block_user.block_user and block_user is not None :
                    new_block_user.block_user = block_user
                new_block_user.updated_at = now
                new_block_user.save()

        db.BlockUserHistorical.insert_from(
            db.BlockUser.select(
                db.BlockUser.user,
                db.BlockUser.block_user,
                db.BlockUser.block_username,
                db.BlockUser.created_at,
                db.BlockUser.updated_at,
                db.fn.DATETIME('now')
            ).where(
                db.BlockUser.user == account_user,
                db.BlockUser.updated_at < now
            ),
            [
                db.BlockUserHistorical.user,
                db.BlockUserHistorical.block_user,
                db.BlockUserHistorical.block_username,
                db.BlockUserHistorical.created_at,
                db.BlockUserHistorical.updated_at,
                db.BlockUserHistorical.deleted_at,
            ]
        ).execute()

        db.BlockUser.delete().where(
            db.BlockUser.user == account_user, 
            db.BlockUser.updated_at < now
        ).execute()

    def run(self):
        account = self.sync_account()
        following_user_list = self.fetch_follow_list(account.name, 'following')
        following_users = {username: self.fetch_user(username) for username in following_user_list}
        self.save_following(account.user, following_users)
        
        follower_list = self.fetch_follow_list(account.name, 'followers')
        follower_users = {username: self.fetch_user(username) for username in follower_list}
        self.save_followers(account.user, follower_users)

        block_list = self.fetch_block_list()
        block_users = {username: self.fetch_user(username) for username in block_list}
        self.save_block_list(account.user, block_users)


class BookTask(Task):
    _name = '我的书'

    def run(self):
        wish_list = self.fetch_interests('book', 'mark')
        doing_list = self.fetch_interests('book', 'doing')
        done_list = self.fetch_interests('book', 'done')


class MovieTask(Task):
    _name = '我的影视'

    def run(self):
        user = self.fetch_user_by_api('tabris17')


class MusicTask(Task):
    _name = '我的音乐'

    def run(self):
        user = self.fetch_user_by_api('tabris17')


class BroadcastTask(Task):
    _name = '我的广播'

    def run(self):
        user = self.fetch_user_by_api('tabris17')


class NoteTask(Task):
    _name = '我的日记'

    def run(self):
        user = self.fetch_user_by_api('tabris17')


class PhotoAlbumTask(Task):
    _name = '我的相册'

    def run(self):
        user = self.fetch_user_by_api('tabris17')


class ReviewTask(Task):
    _name = '我的评论'

    def run(self):
        user = self.fetch_user_by_api('tabris17')


class DoulistTask(Task):
    _name = '我的豆列'

    def run(self):
        user = self.fetch_user_by_api('tabris17')


ALL_TASKS = OrderedDict([(cls._name, cls) for cls in [
    FollowingFollowerTask,
    #BroadcastTask,
    #BookMovieMusicTask,
    #NoteTask,
    #PhotoAlbumTask,
    #ReviewTask,
    #DoulistTask,
]])

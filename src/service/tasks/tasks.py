# encoding: utf-8
import datetime
import json
import logging
from abc import abstractmethod
from collections import OrderedDict
from time import sleep, time
from urllib.parse import urljoin

import pyquery
import requests
from requests.exceptions import TooManyRedirects

import db
from db import dbo


DOUBAN_URL = 'https://www.douban.com/'
REQUEST_TIMEOUT = 5
REQUEST_RETRY_TIMES = 5
LOCAL_OBJECT_DURATION = 86400

class Forbidden(Exception):
    """
    登录会话或IP被屏蔽了
    """
    pass

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
        self._last_request_at = time()
        session = requests.Session()
        session.headers.update({
            'Cookie': self._account.session,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.105 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        })
        self._session = session

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

    def fetch_user(self, name, duration):
        """
        尝试从本地获取用户信息，如果没有则从网上抓取
        """
        try:
            user = db.User.get(db.User.unique_name == name)
            now = datetime.datetime.now()
            if (now - user.updated_at).seconds > duration:
                raise db.User.DoesNotExist()
        except db.User.DoesNotExist:
            user = self.fetch_user_by_api(name)

        return user

    def fetch_user_by_api(self, name):
        """
        通过豆瓣API获取用户信息
        """
        url = 'https://api.douban.com/v2/user/{0}'.format(name)
        response = self.fetch_url_content(url)
        if not response:
            return None

        detail = json.loads(response.text)
        return self.save_user(detail)

    def fetch_movie_by_api(self, id):
        """
        通过豆瓣API获取电影信息
        """
        url = 'https://api.douban.com/v2/movie/subject/{0}'.format(id)
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
        user = self.fetch_user(account.name, LOCAL_OBJECT_DURATION)
        if account.user is None:
            account.user = user
            account.save()
        return account


class FollowingFollowerTask(Task):
    _name = '我的友邻'

    def get_follow_list(self, user, action):
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

        return user_list

    @dbo.atomic()
    def save_following(self, account_user, following_users):
        now = datetime.datetime.now()
        for following_username, following_user in following_users.items():
            try:
                db.Following(user=account_user, following_user=following_user, following_username=following_username, updated_at=now).save()
            except db.IntegrityError:
                fw = db.Following.get(db.Following.user == account_user, db.Following.following_username == following_username)
                fw.updated_at = now
                fw.save()

    def run(self):
        account = self.sync_account()
        following_user_list = self.get_follow_list(account.name, 'following')
        following_users = {username: self.fetch_user(username, LOCAL_OBJECT_DURATION) for username in following_user_list}
        self.save_following(account.user, following_users)
        
        #user_list = self.get_follow_list(account.name, 'followers')
        #logging.debug(user_list)


class ShuoTask(Task):
    _name = '我的广播'

    def run(self):
        user = self.fetch_user_by_api('tabris17')


class BookMovieMusicTask(Task):
    _name = '我的书影音'

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
    #ShuoTask,
    #BookMovieMusicTask,
    #NoteTask,
    #PhotoAlbumTask,
    #ReviewTask,
    #DoulistTask,
]])

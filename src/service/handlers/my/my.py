# encoding: utf-8
import math

import handlers
import db


_PAGE_SIZE_ = 50


def require_login(func):
    """
    用户登录装饰器
    """
    def wrapper(self, *args, **kwargs):
        try:
            db.Account.getDefault()
        except db.Account.DoesNotExist:
            self.redirect(self.reverse_url('settings.accounts.login'))
            return
        return func(self, *args, **kwargs)

    return wrapper


class BaseRequestHandler(handlers.BaseRequestHandler):
    def get_current_user(self):
        try:
            return db.Account.getDefault().user
        except db.Account.DoesNotExist:
            pass

    def prepare(self):
        user = self.get_current_user()
        if not user:
            self.redirect(self.reverse_url('settings.accounts.login'))

    def list(self, query, template):
        try:
            page = int(self.get_query_argument('page', 1))
        except:
            page = 1
        total_rows = query.count()
        total_pages = int(math.ceil(total_rows / _PAGE_SIZE_))

        rows = query.paginate(page, _PAGE_SIZE_)
        self.render(template, rows=rows, page=page, total_pages=total_pages, total_rows=total_rows, page_size=_PAGE_SIZE_)


class Index(BaseRequestHandler):
    def get(self):
        self.redirect(self.reverse_url('my.following'))


class Following(BaseRequestHandler):
    def get(self):
        query = db.Following.select(db.Following, db.User).join(
            db.User, on=db.Following.following_user
        ).where(db.Following.user == self.get_current_user()).order_by(db.Following.id.desc())
        self.list(query, 'my/following.html')


class Followers(BaseRequestHandler):
    def get(self):
        query = db.Follower.select(db.Follower, db.User).join(
            db.User, on=db.Follower.follower
        ).where(db.Follower.user == self.get_current_user()).order_by(db.Follower.id.desc())
        self.list(query, 'my/followers.html')


class Blocklist(BaseRequestHandler):
    def get(self):
        query = db.BlockUser.select(db.BlockUser, db.User).join(
            db.User, on=db.BlockUser.block_user
        ).where(db.BlockUser.user == self.get_current_user()).order_by(db.BlockUser.id.desc())
        self.list(query, 'my/blocklist.html')


class FollowingHistorical(BaseRequestHandler):
    def get(self):
        query = db.FollowingHistorical.select(db.FollowingHistorical, db.User).join(
            db.User, on=db.FollowingHistorical.following_user
        ).where(db.FollowingHistorical.user == self.get_current_user()).order_by(db.FollowingHistorical.id.desc())
        self.list(query, 'my/following_historical.html')


class FollowersHistorical(BaseRequestHandler):
    def get(self):
        query = db.FollowerHistorical.select(db.FollowerHistorical, db.User).join(
            db.User, on=db.FollowerHistorical.follower
        ).where(db.FollowerHistorical.user == self.get_current_user()).order_by(db.FollowerHistorical.id.desc())
        self.list(query, 'my/followers_historical.html')


class BlocklistHistorical(BaseRequestHandler):
    def get(self):
        query = db.BlockUserHistorical.select(db.BlockUserHistorical, db.User).join(
            db.User, on=db.BlockUserHistorical.block_user
        ).where(db.BlockUserHistorical.user == self.get_current_user()).order_by(db.BlockUserHistorical.id.desc())
        self.list(query, 'my/blocklist_historical.html')




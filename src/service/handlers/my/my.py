# encoding: utf-8
import handlers
import db


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


class Index(BaseRequestHandler):
    def get(self):
        self.redirect(self.reverse_url('my.following'))


class Following(BaseRequestHandler):
    def get(self):
        user = self.get_current_user()
        following = (db.Following.select(db.Following, db.User).join(db.User, on=db.Following.following_user).where(
            db.Following.user == user
        ).order_by(db.Following.id.desc()))
        self.render('my/following.html', following=following)


class Followers(BaseRequestHandler):
    def get(self):
        self.write('sadsad')
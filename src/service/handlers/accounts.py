# encoding: utf-8
from tornado.web import RequestHandler
from .handlers import BaseRequestHandler

class Login(BaseRequestHandler):
    """
    主页
    """

    def get(self):
        self.render('accounts/login.html')


class Add(BaseRequestHandler):
    """
    添加帐号
    """

    def post(self):
        cookie = self.get_argument('cookie')
        
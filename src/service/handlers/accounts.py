# encoding: utf-8
from tornado.web import RequestHandler
from .handlers import BaseRequestHandler

class Login(BaseRequestHandler):
    """
    主页
    """

    def get(self):
        self.render('accounts/login.html')
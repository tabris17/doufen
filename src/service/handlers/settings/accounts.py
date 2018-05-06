# encoding: utf-8
from ..handlers import BaseRequestHandler
from db import Account

class Login(BaseRequestHandler):
    """
    登录豆瓣
    """

    def get(self):
        self.render('settings/accounts/login.html')


class Index(BaseRequestHandler):
    """
    管理帐号
    """

    def get(self):
        self.render('settings/accounts/index.html')


class Add(BaseRequestHandler):
    """
    添加帐号
    """

    def post(self):
        session_cookie = self.get_argument('sess')
        account = Account()
        account.session = session_cookie
        account.save()

        self.write('OK')
        
        
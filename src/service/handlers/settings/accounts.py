# encoding: utf-8
import re
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
        self.render('settings/accounts/index.html', rows=Account.select())


class Add(BaseRequestHandler):
    """
    添加帐号
    """

    def post(self):
        session = self.get_argument('session')
        homepage = self.get_argument('homepage')
        result = re.findall(r'^https://www\.douban\.com/people/(.+)/$', 'https://www.douban.com/people/tabris17/')
        try:
            Account(
                session=session,
                name=result[0]
            ).save()
        except IndexError:
            pass

        self.write('OK')
        
        
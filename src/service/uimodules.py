# encoding: utf-8
import tornado
import db

class Account(tornado.web.UIModule):
    """
    登录帐号模块
    """

    def render(self):
        try:
            account = db.Account.getDefault()
        except db.Account.DoesNotExist:
            account = None
        return self.render_string('modules/account.html', account=account)
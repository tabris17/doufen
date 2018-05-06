# encoding: utf-8
from ..handlers import BaseRequestHandler


class Index(BaseRequestHandler):
    """
    设置
    """

    def get(self):
        self.render('settings/index.html', db='self.get_db()')

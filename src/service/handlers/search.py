# encoding: utf-8
import logging

from .handlers import BaseRequestHandler


class Index(BaseRequestHandler):
    """
    搜索主页
    """
    def get(self):
        
        self.render('search.html')
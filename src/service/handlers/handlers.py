# encoding: utf-8
import json
import logging

import tornado
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
from server import BaseRequestHandler


class Notifier(WebSocketHandler):
    """
    用于后台向前台图形程序发送通知
    """

    def check_origin(self, origin):
        return origin == 'localhost'

    def on_message(self, message):
        logging.debug('receive message: "{0}"'.format(message))

    def open(self):
        logging.debug('websocket open')
        self.application.register_client(self)

    def on_close(self):
        logging.debug('websocket close')
        self.application.unregister_client(self)


class Main(BaseRequestHandler):
    """
    主页
    """

    def get(self):
        self.render('index.html')


class Manual(BaseRequestHandler):
    """
    使用手册
    """

    def get(self):
        self.render('manual.html')


class Settings(BaseRequestHandler):
    """
    使用手册
    """

    def get(self):
        self.render('settings.html', db='self.get_db()')

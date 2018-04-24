# encoding: utf-8
import json
import logging

from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler


class Notifier(WebSocketHandler):
    """
    用于后台向前台图形程序发送通知
    """

    def check_origin(self, origin):
        return True

    def write_message(self, message, binary=False):
        logging.debug('send message: "{0}"'.format(message))
        return super().write_message(message, binary)

    def open(self):
        logging.debug('websocket open')

    def on_close(self):
        logging.debug('websocket close')
        pass

    def on_message(self, message):
        logging.debug('receive message: "{0}"'.format(message))
        data = json.loads(message)
        data.get('type')
        data.get('session')
        data.get('body')

    def on_connection_close(self):
        logging.debug('connection close')


class BaseRequestHandler(RequestHandler):
    """
    默认继承
    """

    pass


class Main(BaseRequestHandler):
    """
    主页
    """

    def get(self):
        self.render('index.html')


class Dashborad(BaseRequestHandler):
    """
    控制台
    """

    def get(self):
        self.render('index.html')


class About(BaseRequestHandler):
    """
    关于
    """

    def get(self):
        self.render('about.html')


class Help(BaseRequestHandler):
    """
    帮助
    """

    def get(self):
        self.render('help.html')
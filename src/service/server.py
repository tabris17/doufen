# encoding: utf-8
import logging

import tornado
from tornado.web import RequestHandler

import db


class Client:
    """
    客户端
    """

    def __init__(self, handler):
        if (isinstance(handler, tornado.websocket.WebSocketHandler)):
            pass
        elif (isinstance(handler, tornado.web.RequestHandler)):
            pass
        else:
            raise Exception('Invalid handler type')

        self.handler = handler

    def send(self, message):
        handler = self.handler
        if (isinstance(handler, tornado.websocket.WebSocketHandler)):
            handler.write_message(message)
        else:
            handler.write(message)


class BaseRequestHandler(RequestHandler):
    """
    默认继承
    """

    def get_db(self):
        """
        取得数据库对象
        """
        return self.application.database


class Application(tornado.web.Application):
    """
    Application 继承类
    """

    clients = dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.debug('init database')
        dbo = db.instance(self.settings['_database_path'])
        db.init(dbo)
        self.database = dbo

    def register_client(self, handler):
        """
        注册客户端
        """
        self.clients[handler] = Client(handler)

    def unregister_client(self, handler):
        """
        注销客户端
        """
        del self.clients[handler]

    def broadcast(self, message):
        """
        向客户端广播
        """
        for client in self.clients:
            client.send(message)

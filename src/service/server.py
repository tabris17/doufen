# encoding: utf-8

import tornado

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
        pass


class Application(tornado.web.Application):
    """
    Application 继承类
    """

    clients = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database = db.instance(self.settings['_database_path'])

    def register_client(self, handler):
        """
        注册客户端
        """
        self.clients.append(Client(handler))

    def unregister_client(self, handler):
        """
        注销客户端
        """
        self.clients.remove(Client(handler))

    def broadcast(self, message):
        """
        向客户端广播
        """
        for client in self.clients:
            client.send(message)

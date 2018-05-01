# encoding: utf-8
import logging
import os
import sys
from multiprocessing import Queue, Process
from multiprocessing import queues

import tornado

import db
import urls
from worker import Worker


class Client:
    """
    客户端
    """

    def __init__(self, handler):
        if (isinstance(handler, tornado.websocket.WebSocketHandler)):
            self.send = self.send_websocket
        elif (isinstance(handler, tornado.web.RequestHandler)):
            self.send = self.send_http_request
        else:
            raise Exception('Invalid handler type')

        self.handler = handler

    def send_websocket(self, message):
        self.handler.write_message(message)

    def send_http_request(self, message):
        self.handler.write(message)


class Application(tornado.web.Application):
    """
    Application 继承类
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.clients = dict()
        self.database = None

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
        向所有在线客户端发送广播
        """
        for client in self.clients:
            client.send(message)


def run(port, address=''):
    """
    运行接口服务
    """
    base_path = os.path.dirname(__file__)
    settings = {
        'autoreload': __debug__,
        'debug': __debug__,
        'template_path': os.path.join(base_path, 'views'),
        'static_path': os.path.join(base_path, 'static'),
        'static_url_prefix': '/static/'
    }

    application = Application(urls.patterns, **settings)
    application.listen(port, address)

    try:
        logging.debug('start ioloop')
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.debug('stop ioloop')
        tornado.ioloop.IOLoop.instance().stop()


class Server:
    """
    主服务
    """

    def __init__(self, port, address, db_path):
        base_path = os.path.dirname(__file__)
        settings = {
            'autoreload': __debug__,
            'debug': __debug__,
            'template_path': os.path.join(base_path, 'views'),
            'static_path': os.path.join(base_path, 'static'),
            'static_url_prefix': '/static/',
            'db_path': db_path,
        }

        application = Application(urls.patterns, **settings)
        application.listen(port, address)
        self.application = application

        self.__worker_output = Queue()
        self.__worker_input = Queue()
        self.__workers = []

    @tornado.gen.coroutine
    def __watch_worker(self):
        queue = self.__worker_output
        while True:
            try:
                item = queue.get_nowait()
                print(item)
            except queues.Empty:
                pass
            yield

    def add_worker(self, routine, args):
        worker = Worker(routine, self.__worker_input, self.__worker_output)
        process = Process(target=worker, args=args)
        self.__workers.append(process)

    def start_workers(self):
        for worker in self.__workers:
            worker.start()

    def stop_workers(self):
        for worker in self.__workers:
            worker.stop()

    def run(self):
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.add_callback(self.__watch_worker)

        try:
            logging.debug('start workers')
            self.start_workers()
            logging.debug('start ioloop')
            ioloop.start()
        except KeyboardInterrupt:
            logging.debug('stop workers')
            self.stop_workers()
            logging.debug('stop ioloop')
            ioloop.stop()

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
        self._db_path = kwargs['db_path']
        self._server = kwargs['server']

    def get_server(self):
        """
        获得 server 对象
        """
        return self._server

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
            'server': self,
        }

        application = Application(urls.patterns, **settings)
        application.listen(port, address)
        self.application = application

        self._worker_output = Queue()
        self._worker_input = Queue()
        self.workers = []

    @tornado.gen.coroutine
    def _watch_worker(self):
        """
        写成这样我也很绝望啊：
        multiprocessing 的 Queue 不支持异步读，而 tornodo 的 Queue 不支持跨进/线程
        也许用 socket 才是正途吧
        """
        queue = self._worker_output
        while True:
            try:
                ret = queue.get_nowait()
                if isinstance(ret, logging.LogRecord):
                    logging.root.handle(ret)
                else:
                    logging.debug(ret)
                    self._worker_input.put('received:' + str(ret))
                    for w in self.workers:
                        print(w.name if hasattr(w, 'name') else 'NULL')
                    pass
            except queues.Empty:
                pass
            yield tornado.gen.sleep(1)
            # yield

    def add_task(self, routine, args=()):
        worker = Worker(routine, self._worker_input, self._worker_output, args=args)
        self.workers.append(worker)
        return worker

    def start_workers(self):
        for worker in self.workers:
            if worker.is_pending():
                worker.start()

    def stop_workers(self):
        for worker in self.workers:
            if worker.is_running():
                worker.stop()

    def run(self):
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.add_callback(self._watch_worker)

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

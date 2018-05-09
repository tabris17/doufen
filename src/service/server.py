# encoding: utf-8
import logging
import os
import sys
from collections import deque
from multiprocessing import Queue, Process
from multiprocessing import queues

import tornado

import db
import urls
import setting
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

        self._clients = dict()
        self._server = kwargs['server']

    @property
    def server(self):
        """
        获得 server 对象
        """
        return self._server

    def register_client(self, handler):
        """
        注册客户端
        """
        self._clients[handler] = Client(handler)

    def unregister_client(self, handler):
        """
        注销客户端
        """
        del self._clients[handler]

    def broadcast(self, message):
        """
        向所有在线客户端发送广播
        """
        for client in self._clients:
            client.send(message)


class Server:
    """
    主服务
    """

    def __init__(self, port, address):
        base_path = os.path.dirname(__file__)
        settings = {
            'autoreload': __debug__,
            'debug': __debug__,
            'template_path': os.path.join(base_path, 'views'),
            'static_path': os.path.join(base_path, 'static'),
            'static_url_prefix': '/static/',
            'server': self,
        }

        application = Application(urls.patterns, **settings)
        application.listen(port, address)
        self.application = application

        self._worker_output = Queue()
        self._worker_input = Queue()
        self._workers = dict()
        self._tasks = deque()

    def _create_workers(self):
        worker_name = '工作进程#1'
        self._workers[worker_name] = Worker(
            worker_name,
            self._worker_input,
            self._worker_output
        )
        proxies = setting.get('worker.proxies', 'json')
        if not proxies:
            return
        index = 1
        for proxy in  proxies:
            index += 1
            worker_name = '工作进程#' + str(index)
            self._workers[worker_name] = Worker(
                worker_name,
                self._worker_input,
                self._worker_output,
                proxy=proxy
            )

    def _launch_task(self):
        try:
            task = self._tasks.popleft()
            self._worker_input.put(task)
            self.application.broadcast('开始执行"{0}"任务'.format(task))
        except IndexError:
            pass

    @tornado.gen.coroutine
    def _watch_worker(self):
        """
        写成这样我也很绝望啊：
        multiprocessing 的 Queue 不支持异步读，而 tornodo 的 Queue 不支持跨进/线程
        也许用 socket 才是正途吧
        """
        while True:
            try:
                ret = self._worker_output.get_nowait()
                if isinstance(ret, logging.LogRecord):
                    logging.root.handle(ret)
                elif isinstance(ret, Worker.ReturnReady):
                    logging.debug('"{0}" is ready'.format(ret.name))
                    self._launch_task()
                elif isinstance(ret, Worker.ReturnDone):
                    logging.debug('"{0}" has done'.format(ret.name))
                    self._workers[ret.name].toggle_task()
                    self.application.broadcast('任务"{0}"执行完毕'.format(ret.name))
                    self._launch_task()
                elif isinstance(ret, Worker.ReturnWorking):
                    logging.debug('"{0}" is working for "{1}"'.format(ret.name, ret.task))
                    self._workers[ret.name].toggle_task(ret.task)
                elif isinstance(ret, Worker.ReturnError):
                    self.application.broadcast('"{0}"发生错误并退出: {1}'.format(ret.name, str(ret.exception)))
                    logging.debug('Worker error:' + str(ret.exception))
            except queues.Empty:
                pass
            # 每隔0.5秒读取一下队列
            yield tornado.gen.sleep(0.5)

    def add_task(self, task, priority=False):
        if len(self._tasks) == 0:
            for worker in self._workers:
                if worker.is_suspended():
                    self._worker_input.put(task)
                    return
        
        if priority:
            self._tasks.appendleft(task)
        else:
            self._tasks.append(task)
        logging.debug('add "{0}" to task list'.format(task))

    def start_workers(self):
        for worker in self._workers.values():
            if worker.is_pending():
                worker.start()

    def stop_workers(self):
        for worker in self._workers.values():
            if worker.is_running():
                worker.stop()

    def run(self):
        self._create_workers()

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
            raise

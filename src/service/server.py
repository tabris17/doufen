# encoding: utf-8
import logging
import os
import sys
import json
from collections import deque
from multiprocessing import Queue
from multiprocessing import queues

import tornado

import db
import urls
import setting
import uimodules
from worker import Worker, REQUESTS_PER_MINUTE, LOCAL_OBJECT_DURATION, BROADCAST_ACTIVE_DURATION, BROADCAST_INCREMENTAL_BACKUP, IMAGE_LOCAL_CACHE
from setting import settings
from tasks import Task
from handlers import NotFound


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
            client.write_message(message)


class Server:
    """
    主服务
    """

    def __init__(self, port, address, cache_path):
        # PyInstaller patch
        base_path = sys.path[0] if not hasattr(sys, 'frozen') else getattr(sys, '_MEIPASS')
        app_settings = {
            'debug': settings.get('debug'),
            'template_path': os.path.join(base_path, 'views'),
            'static_path': os.path.join(base_path, 'static'),
            'static_url_prefix': '/static/',
            'server': self,
            'ui_modules': uimodules,
            'default_handler_class': NotFound,
        }

        urls.patterns.append(    
            (r'/cache/(.*)', tornado.web.StaticFileHandler, {'path': cache_path}, 'cache')
        )
        application = Application(urls.patterns, **app_settings)
        try:
            application.listen(port, address)
        except OSError:
            logging.error('system already running.')
            sys.exit(0)
        self.application = application

        self._worker_output = Queue()
        self._worker_input = Queue()
        self._workers = dict()
        self._tasks = deque()

    @property
    def workers(self):
        """
        返回所有工作进程
        """
        return self._workers.values()

    @property
    def tasks(self):
        return list(self._tasks)

    def _create_workers(self):
        self._workers.clear()
        requests_per_minute = setting.get('worker.requests-per-minute', int, REQUESTS_PER_MINUTE)
        local_object_duration = setting.get('worker.local-object-duration', int, LOCAL_OBJECT_DURATION)
        broadcast_incremental_backup = setting.get('worker.broadcast-incremental-backup', bool, BROADCAST_INCREMENTAL_BACKUP)
        broadcast_active_duration = setting.get('worker.broadcast-active-duration', int, BROADCAST_ACTIVE_DURATION)
        image_local_cache = setting.get('worker.image-local-cache', bool, IMAGE_LOCAL_CACHE)
        
        self._worker_input = Queue()
        worker_args = {
            'debug': settings.get('debug'),
            'queue_in': self._worker_input,
            'queue_out': self._worker_output,
            'requests_per_minute': requests_per_minute,
            'local_object_duration': local_object_duration,
            'broadcast_incremental_backup': broadcast_incremental_backup,
            'image_local_cache': image_local_cache,
            'broadcast_active_duration': broadcast_active_duration,
            'db_path': db.DATEBASE_PATH,
        }
        worker = Worker(**worker_args)
        self._workers[worker.name] = worker
        proxies = setting.get('worker.proxies', 'json')
        if not proxies:
            return
        for proxy in proxies:
            worker_args['proxy'] = proxy
            worker = Worker(**worker_args)
            self._workers[worker.name] = worker

    def _launch_task(self):
        try:
            task = self._tasks.popleft()
            self._worker_input.put(task)
            self.application.broadcast(json.dumps({
                'sender': 'logger',
                'message': '开始执行"{0}"任务'.format(task),
                'level': 'INFO',
            }))
        except IndexError:
            pass

    @tornado.gen.coroutine
    def _watch_worker(self):
        """
        监控工作队列
        """
        while True:
            try:
                ret = self._worker_output.get_nowait()
                if isinstance(ret, logging.LogRecord):
                    logging.root.handle(ret)
                    self.application.broadcast(json.dumps({
                        'sender': 'logger',
                        'message': ret.getMessage(),
                        'level': ret.levelname,
                    }))
                elif isinstance(ret, Worker.ReturnReady):
                    logging.info('"{0}" is ready'.format(ret.name))
                    self.application.broadcast(json.dumps({
                        'sender': 'worker',
                        'src': ret.name,
                        'event': 'ready',
                    }))
                    self._launch_task()
                elif isinstance(ret, Worker.ReturnDone):
                    logging.info('"{0}" has done'.format(ret.name))
                    self._workers[ret.name].toggle_task()
                    self.application.broadcast(json.dumps({
                        'sender': 'worker',
                        'src': ret.name,
                        'event': 'done',
                    }))
                    self._launch_task()
                elif isinstance(ret, Worker.ReturnWorking):
                    logging.info('"{0}" is working for "{1}"'.format(ret.name, ret.task))
                    self._workers[ret.name].toggle_task(ret.task)
                    self.application.broadcast(json.dumps({
                        'sender': 'worker',
                        'src': ret.name,
                        'event': 'working',
                        'target': str(ret.task),
                    }))
                elif isinstance(ret, Worker.ReturnError):
                    logging.error('"{0}" error: {1}'.format(ret.name, ret.exception))
                    self._workers[ret.name].toggle_task()
                    self.application.broadcast(json.dumps({
                        'sender': 'worker',
                        'src': ret.name,
                        'event': 'error',
                        'message': str(ret.exception),
                    }))
                    self._launch_task()
                elif isinstance(ret, Worker.ReturnHeartbeat):
                    logging.info('"{0}" heartbeat:{1}'.format(ret.name, ret.sequence))
            except queues.Empty:
                pass
            # 每隔0.1秒读取一下队列
            yield tornado.gen.sleep(0.1)

    def add_task(self, task, priority=False):
        """
        添加任务
        """
        if not isinstance(task, Task):
            raise RuntimeError('task 参数必须是 Task 对象')
        if list(filter(lambda t: task.equals(t), self._tasks)):
            logging.warn('添加任务 "{0}" 失败: 任务重复'.format(task))
            return False

        if priority:
            self._tasks.appendleft(task)
        else:
            self._tasks.append(task)
        logging.info('添加任务 "{0}" 到任务队列'.format(task))
        return True

    def push_task(self):
        """
        尝试推送任务到工作进程
        """
        if len(self._tasks) > 0:
            for worker in self._workers.values():
                if worker.is_suspended():
                    self._launch_task()


    def start_workers(self):
        self._create_workers()
        for worker in self._workers.values():
            if worker.is_pending():
                worker.start()

    def stop_workers(self):
        """
        停止工作进程
        """
        for worker in self._workers.values():
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
            raise

# encoding: utf-8
import logging
from enum import Enum
from inspect import isgeneratorfunction
from logging.handlers import QueueHandler
from multiprocessing import Process, Queue, queues

import db
import tasks

REQUESTS_PER_MINUTE = 60
LOCAL_OBJECT_DURATION = 60 * 60 * 24 * 30
BROADCAST_ACTIVE_DURATION = 60 * 60 * 24 * 30
BROADCAST_INCREMENTAL_BACKUP = False
IMAGE_LOCAL_CACHE = True


class Worker:
    """
    工作进程封装
    """

    _id = 1
    _name = '工作进程'

    class ReturnError:
        """
        工作进程发生异常
        """

        def __init__(self, name, exception):
            self.name = name
            self.exception = exception

    class ReturnDone:
        """
        任务完成
        """

        def __init__(self, name, value):
            self.name = name
            self.value = value

    class ReturnHeartbeat:
        """
        心跳
        """

        def __init__(self, name, sequence):
            self.name = name
            self.sequence = sequence

    class ReturnReady:
        """
        工作进程准备完毕
        """

        def __init__(self, name):
            self.name = name

    class ReturnWorking():
        """
        接收到任务准备工作
        """

        def __init__(self, name, task):
            self.name = name
            self.task = task

    class State(Enum):
        """
        工作进程状态
        """
        PENDING = 0
        RUNNING = 1
        TERMINATED = 2

    class RuntimeError(Exception):
        """
        运行时错误
        """
        def __init__(self, message):
            self.message = message

    def __init__(self, debug=False, queue_in=None, queue_out=None, **settings):
        class_type = type(self)
        self._name = '{name}#{id}'.format(name=class_type._name, id=class_type._id)
        class_type._id += 1

        self._status = Worker.State.PENDING
        self._queue_in = queue_in
        self._queue_out = queue_out
        self._settings = settings
        self._current_task = None
        self._debug = debug

    @property
    def queue_in(self):
        if self._queue_in is None:
            self._queue_in = Queue()
        return self._queue_in

    @property
    def queue_out(self):
        if self._queue_out is None:
            self._queue_out = Queue()
        return self._queue_out

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name

    def _ready(self):
        self.queue_out.put(Worker.ReturnReady(self._name))

    def _work(self, task):
        self.queue_out.put(Worker.ReturnWorking(self._name, task))

    def _done(self, result):
        self.queue_out.put(Worker.ReturnDone(self._name, result))
        
    def _error(self, exception):
        self.queue_out.put(Worker.ReturnError(self._name, exception))

    def _heartbeat(self, sequence):
        self.queue_out.put(Worker.ReturnHeartbeat(self._name, sequence))

    def __call__(self, *args, **kwargs):
        queue_in = self.queue_in
        queue_out = self.queue_out
        logger = logging.getLogger()
        logger.addHandler(QueueHandler(queue_out))
        logger.setLevel(logging.DEBUG if self._debug else logging.INFO)
        db.init(self._settings['db_path'], False)

        self._ready()

        heartbeat_sequence = 1
        while True:
            try:
                task = queue_in.get(timeout=1)
                if isinstance(task, tasks.Task):
                    self._work(str(task))
                    self._done(task(**self._settings))
            except queues.Empty:
                self._heartbeat(heartbeat_sequence)
                heartbeat_sequence += 1
            except Exception as e:
                self._error(e)
            except KeyboardInterrupt:
                break

    def start(self):
        if self.is_pending():
            self._status = Worker.State.RUNNING
            self._process = Process(target=self)
            self._process.start()
            logging.info('{0}启动'.format(self.name))
        else:
            raise Worker.RuntimeError('Can not start worker. The worker is ' + (
                'running' if self._status == Worker.State.RUNNING else 'terminated'))

    def stop(self):
        if self.is_running():
            self._status = Worker.State.TERMINATED
            self._process.terminate()
            logging.info('{0}停止'.format(self.name))
        else:
            raise Worker.RuntimeError('Can not stop worker. The worker is ' + (
                'pending' if self._status == Worker.State.PENDING else 'terminated'))

    def reset(self):
        if self.is_terminated():
            del self._process
            self._status = Worker.State.PENDING
        else:
            raise Worker.RuntimeError('Can not reset worker. The worker is ' + (
                'pending' if self._status == Worker.State.PENDING else 'running'))

    @property
    def status(self):
        if self._status == Worker.State.RUNNING:
            if not self._process.is_alive():
                self._status = Worker.State.TERMINATED
        return self._status

    @property
    def status_text(self):
        status = self.status
        if status == Worker.State.PENDING:
            return '等待'
        elif status == Worker.State.RUNNING:
            if self.is_suspended():
                return '挂起'
            return '运行'
        elif status == Worker.State.TERMINATED:
            return '停止'
        else:
            return '未知'

    def is_running(self):
        return self.status == Worker.State.RUNNING

    def is_pending(self):
        return self.status == Worker.State.PENDING

    def is_terminated(self):
        return self.status == Worker.State.TERMINATED

    def toggle_task(self, task=None):
        self._current_task = task

    def is_suspended(self):
        return self._current_task is None

    @property
    def current_task(self):
        """
        当前工作进程正在执行的任务    
        """
        return self._current_task

# encoding: utf-8
import logging
from enum import Enum
from inspect import isgeneratorfunction
from logging.handlers import QueueHandler
from multiprocessing import Queue, Process


class Worker:
    """
    工作进程封装
    """

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

    def __init__(self, name, queue_in=None, queue_out=None, **settings):
        self._status = Worker.State.PENDING
        self._name = name
        self._queue_in = queue_in
        self._queue_out = queue_out
        self._settings = settings

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

    def _ready(self):
        self.queue_out.put(Worker.ReturnReady(self._name))

    def _work(self, task):
        self.queue_out.put(Worker.ReturnWorking(self._name, task))

    def _done(self, result):
        self.queue_out.put(Worker.ReturnDone(self._name, result))
        
    def _error(self, exception):
        self.queue_out.put(Worker.ReturnError(self._name, exception))

    def __call__(self, *args, **kwargs):
        queue_in = self.queue_in
        queue_out = self.queue_out
        logger = logging.getLogger()
        logger.addHandler(QueueHandler(queue_out))
        logger.setLevel(logging.DEBUG if __debug__ else logging.INFO)

        try:
            self._ready()
            while True:
                task = queue_in.get()
                self._work(str(task))
                self._done(task(**self._settings))

        except Exception as e:
            """
            TODO: 处理错误
            """
            self._error(e)

    def start(self):
        if self.is_pending():
            self._status = Worker.State.RUNNING
            self._process = Process(target=self)
            self._process.start()
        else:
            raise Worker.RuntimeError('Can not start worker. The worker is ' + (
                'running' if self._status == Worker.State.RUNNING else 'terminated'))

    def stop(self):
        if self.is_running():
            self._status = Worker.State.TERMINATED
            self._process.terminate()
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

    def is_running(self):
        return self.status == Worker.State.RUNNING

    def is_pending(self):
        return self.status == Worker.State.PENDING

    def is_terminated(self):
        return self.status == Worker.State.TERMINATED

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
    
    class Return:
        """
        Worker 运行结束返回的对象
        """

        def __init__(self, name, value):
            self.name = name
            self.value = value

    class Error:
        """
        Worker 运行发生异常返回的对象
        """

        def __init__(self, name, exception):
            self.name = name
            self.exception = exception

    class Yield:
        """
        Worker 挂起返回的对象
        """

        def __init__(self, name, value):
            self.name = name
            self.value = value

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

    def __init__(self, queue_in=None, queue_out=None):
        self._status = Worker.State.PENDING
        self._queue_in = queue_in
        self._queue_out = queue_out

    @property
    def input(self):
        if self._queue_in is None:
            self._queue_in = Queue()
        return self._queue_in

    @property
    def output(self):
        if self._queue_out is None:
            self._queue_out = Queue()
        return self._queue_out

    def __call__(self, *args, **kwargs):
        queue_in = self.input
        queue_out = self.output

        logger = logging.getLogger()
        logger.addHandler(QueueHandler(queue_out))
        logger.setLevel(logging.DEBUG if __debug__ else logging.INFO)

        try:
            pass

        except Exception as e:
            """
            TODO: 处理错误
            """
            queue_out.put(Worker.Error(self._name, e))

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

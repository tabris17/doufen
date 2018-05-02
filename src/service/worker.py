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
        def __init__(self, code, message):
            self.code = code
            self.message = message

    class Yield:
        """
        Worker 挂起返回的对象
        """
        pass

    class State(Enum):
        PENDING = 0
        RUNNING = 1
        TERMINATED = 2
        SUSPENDED = 3

    class RuntimeError(Exception):
        """
        运行时错误
        """
        def __init__(self, message):
            self.message = message

    def __init__(self, routine, input_queue=None, output_queue=None, name=None, args=(), kwargs={}):
        self._status = Worker.State.PENDING
        self._routine = routine
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._process_kwargs = {
            'target': self,
            'name': name,
            'args': args,
            'kwargs': kwargs,
        }

    @property
    def input(self):
        if self._input_queue is None:
            self._input_queue = Queue()
        return self._input_queue

    @property
    def output(self):
        if self._output_queue is None:
            self._output_queue = Queue()
        return self._output_queue

    def __call__(self, *args, **kwargs):
        input_queue = self.input
        output_queue = self.output

        logger = logging.getLogger()
        logger.addHandler(QueueHandler(output_queue))
        logger.setLevel(logging.DEBUG if __debug__ else logging.INFO)

        try:
            if isgeneratorfunction(self._routine):
                gen = self._routine(*args, **kwargs)
                output_queue.put(next(gen))
                while True:
                    try:
                        output_queue.put(
                            gen.send(
                                input_queue.get()
                            )
                        )
                    except StopIteration:
                        break
            else:
                kwargs['input_queue'] = input_queue
                kwargs['output_queue'] = output_queue
                self._routine(*args, **kwargs)
        except Exception as e:
            """
            TODO: 处理错误
            """
            pass

    def start(self):
        if self.is_pending():
            self._status = Worker.State.RUNNING
            self._process = Process(**self._process_kwargs)
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

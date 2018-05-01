# encoding: utf-8
import logging
from logging.handlers import QueueHandler
from multiprocessing import Queue


class Worker:
    """
    工作进程封装
    """

    def __init__(self, routine, input_queue, output_queue, name=''):
        self.__name = name
        self.__routine = routine
        self.__input_queue = input_queue
        self.__output_queue = output_queue

    @property
    def name(self):
        return self.__name

    def __call__(self, *args, **kwargs):
        logger = logging.getLogger()
        logger.addHandler(QueueHandler(self.__output_queue))
        logger.setLevel(logging.DEBUG if __debug__ else logging.INFO)
        self.__routine(*args, **kwargs)

    def start(self):
        pass

    def stop(self):
        pass


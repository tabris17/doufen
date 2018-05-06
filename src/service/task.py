# encoding: utf-8


class Task:
    """
    工作任务
    """
    def __str__(self):
        return getattr(self, 'name', '<UNKNOWN TASK>')

    def __call__(self, **kwargs):
        proxy = kwargs.get('proxy', None)
        try:
            self.run(proxy)
        except KeyboardInterrupt:
            pass

    def run(self, proxy):
        raise NotImplementedError()

class Test(Task):
    name = '测试任务'

    def run(self, proxy):
        import time, logging
        while True:
            time.sleep(2)
            logging.debug('test task is running')
# encoding: utf-8
import requests
import pyquery

class Task:
    """
    工作任务
    """
    name = '任务'

    def __str__(self):
        return self.name

    def __call__(self, **kwargs):
        self._settings = kwargs
        try:
            self.run()
        except KeyboardInterrupt:
            pass

    def get_setting(self, name, default=None):
        return self._settings.get(name, default)

    def run(self):
        raise NotImplementedError()


class Test(Task):
    name = '测试'

    def run(self):
        import time, logging
        while True:
            requests.get('https://www.douban.com/', headers={'Cookie': ''})
            time.sleep(2)
            logging.debug('test task is running')
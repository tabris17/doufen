# encoding: utf-8
import requests
import pyquery
import logging
from abc import abstractmethod
from requests.exceptions import TooManyRedirects
from time import time, sleep
from urllib.parse import urljoin
from collections import OrderedDict



DOUBAN_URL = 'https://www.douban.com/'

class Forbidden(Exception):
    """
    登录会话或IP被屏蔽了
    """
    pass

class Task:
    """
    工作任务
    """
    _id = 1
    _name = '任务'

    def __init__(self, account):
        class_type = type(self)
        self._name = '{name}#{id}'.format(name=class_type._name, id=class_type._id)
        class_type._id += 1

        self._account = account

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name

    def __call__(self, **kwargs):
        self._settings = kwargs
        self._proxy = {
            kwargs['proxy']: kwargs['proxy']
        } if 'proxy' in kwargs else None
        requests_per_minute = kwargs['requests_per_minute']
        self._min_request_interval = 60 / requests_per_minute
        self._last_request_at = time()
        session = requests.Session()
        session.headers.update({
            'Cookie': self._account.session,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.105 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
        })
        self._session = session
        try:
            return self.run()
        except (TooManyRedirects, Forbidden):
            logging.debug('Login session maybe forbidden')
            self._account.is_invalid = True
            self._account.save()
            return False
        except Exception as e:
            logging.debug(e)
            return False
        finally:
            session.close()

    def get_setting(self, name, default=None):
        return self._settings.get(name, default)

    def get_url(self, url, base_url=DOUBAN_URL):
        url = urljoin(base_url, url)

        now = time()
        remaining = now - self._last_request_at - self._min_request_interval
        if remaining > 0:
            sleep(remaining)

        self._last_request_at = now
        response = self._session.get(url, proxies=self._proxy)
        return response.text, response.headers

    @abstractmethod
    def run(self):
        raise NotImplementedError()

    def equals(self, task):
        """
        比较两个任务是否相同
        """
        return isinstance(task, type(self)) and self._account.id == task._account.id


class Test(Task):
    _name = '测试'

    def run(self):
        sleep(10)
        self.get_url('https://www.douban.com/')


ALL_TASKS = OrderedDict([
    ('测试', Test),
])
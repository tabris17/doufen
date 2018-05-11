# encoding: utf-8
from ..handlers import BaseRequestHandler
import setting
from worker import REQUESTS_PER_MINUTE


class General(BaseRequestHandler):
    """
    设置
    """

    def get(self):
        requests_per_minute = setting.get('worker.requests-per-minute', int, REQUESTS_PER_MINUTE)
        self.render('settings/general.html', requests_per_minute=requests_per_minute)

    def post(self):
        requests_per_minute = self.get_argument('requests-per-minute')
        setting.set('worker.requests-per-minute', requests_per_minute, int)
        return self.get()


class Network(BaseRequestHandler):
    """
    设置
    """

    def get(self):
        
        
        self.render('settings/network.html', db='self.get_db()')

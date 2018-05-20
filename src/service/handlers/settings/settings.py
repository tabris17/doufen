# encoding: utf-8
from ..handlers import BaseRequestHandler
import setting
from worker import REQUESTS_PER_MINUTE, LOCAL_OBJECT_DURATION


class General(BaseRequestHandler):
    """
    设置
    """

    def get(self):
        requests_per_minute = setting.get('worker.requests-per-minute', int, REQUESTS_PER_MINUTE)
        local_object_duration = setting.get('worker.local-object-duration', int, LOCAL_OBJECT_DURATION)
        self.render(
            'settings/general.html',
            requests_per_minute=requests_per_minute,
            local_object_duration=int(local_object_duration / (60 * 60 *24))
        )

    def post(self):
        requests_per_minute = self.get_argument('requests-per-minute')
        setting.set('worker.requests-per-minute', requests_per_minute, int)
        local_object_duration_days = int(self.get_argument('local-object-duration'))
        local_object_duration = local_object_duration_days * 60 * 60 *24
        setting.set('worker.local-object-duration', local_object_duration, int)
        return self.get()


class Network(BaseRequestHandler):
    """
    设置
    """

    def get(self):
        
        proxies = setting.get('worker.proxies', 'json', [])
        self.render('settings/network.html', proxies='\n'.join(proxies))

    def post(self):
        proxies = self.get_argument('proxies').split('\n')
        proxies = [proxy.strip() for proxy in list(set(proxies)) if proxy.strip()]
        setting.set('worker.proxies', proxies, 'json')
        return self.get()

# encoding: utf-8
from ..handlers import BaseRequestHandler
import setting
from worker import REQUESTS_PER_MINUTE, LOCAL_OBJECT_DURATION, BROADCAST_ACTIVE_DURATION, BROADCAST_INCREMENTAL_BACKUP, IMAGE_LOCAL_CACHE


class General(BaseRequestHandler):
    """
    设置
    """

    def get(self, flash=''):
        requests_per_minute = setting.get('worker.requests-per-minute', int, REQUESTS_PER_MINUTE)
        local_object_duration = setting.get('worker.local-object-duration', int, LOCAL_OBJECT_DURATION)
        broadcast_active_duration = setting.get('worker.broadcast-active-duration', int, BROADCAST_ACTIVE_DURATION)
        broadcast_incremental_backup = setting.get('worker.broadcast-incremental-backup', bool, BROADCAST_INCREMENTAL_BACKUP)
        image_local_cache = setting.get('worker.image-local-cache', bool, IMAGE_LOCAL_CACHE)
        self.render(
            'settings/general.html',
            requests_per_minute=requests_per_minute,
            local_object_duration=int(local_object_duration / (60 * 60 *24)),
            broadcast_active_duration=int(broadcast_active_duration / (60 * 60 *24)),
            broadcast_incremental_backup=broadcast_incremental_backup,
            image_local_cache=image_local_cache,
            flash=flash
        )

    def post(self):
        requests_per_minute = self.get_argument('requests-per-minute')
        setting.set('worker.requests-per-minute', requests_per_minute, int)

        local_object_duration_days = int(self.get_argument('local-object-duration'))
        local_object_duration = local_object_duration_days * 60 * 60 *24
        setting.set('worker.local-object-duration', local_object_duration, int)

        broadcast_active_duration_days = int(self.get_argument('broadcast-active-duration'))
        broadcast_active_duration = broadcast_active_duration_days * 60 * 60 *24
        setting.set('worker.broadcast-active-duration', broadcast_active_duration, int)

        broadcast_incremental_backup = int(self.get_argument('broadcast-incremental-backup'))
        setting.set('worker.broadcast-incremental-backup', broadcast_incremental_backup, bool)

        image_local_cache = int(self.get_argument('image-local-cache'))
        setting.set('worker.image-local-cache', image_local_cache, bool)

        return self.get('需要重启工作进程或者程序才能使设置生效')


class Network(BaseRequestHandler):
    """
    设置
    """

    def get(self, flash=''):
        proxies = setting.get('worker.proxies', 'json', [])
        self.render('settings/network.html', proxies='\n'.join(proxies), flash=flash)

    def post(self):
        proxies = self.get_argument('proxies').split('\n')
        proxies = [proxy.strip() for proxy in list(set(proxies)) if proxy.strip()]
        setting.set('worker.proxies', proxies, 'json')
        return self.get('需要重启工作进程或者程序才能使设置生效')

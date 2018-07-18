#encoding: utf-8
import logging

import db
import tasks


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] (%(pathname)s:%(lineno)s) [%(levelname)s] %(name)s: %(message)s',
    datefmt='%m-%d %H:%M'
)
db.init('var/data/graveyard.db')


class DownloadPictureTask(tasks.LikeTask):
    """
    下载图片任务
    """

    def run(self):
        if self._image_local_cache:
            while self.fetch_attachment():
                pass


class TestTask(tasks.BroadcastTask):
    """
    测试任务
    """
    def run(self):
        self.fetch_photo_album(1671066229)


#task = tasks.FollowingFollowerTask(db.Account.get_by_id(1))
#task = tasks.BroadcastCommentTask(db.Account.get_by_id(1))
#task = tasks.PhotoAlbumTask(db.Account.get_by_id(1))
#task = tasks.NoteTask(db.Account.get_by_id(1))
#task = tasks.LikeTask(db.Account.get_by_id(1))
#task = tasks.ReviewTask(db.Account.get_by_id(1))
#task = DownloadPictureTask(db.Account.get_by_id(1))
task = TestTask(db.Account.get_by_id(1))
#task = tasks.BroadcastTask(db.Account.get_by_id(1))

result = task(
    requests_per_minute=30,
    local_object_duration=60*60*24*300,
    broadcast_active_duration=60*60*24*10,
    broadcast_incremental_backup=True,
    image_local_cache=True
)
print(result)

# encoding: utf-8
import db
import tasks
import logging


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] (%(pathname)s:%(lineno)s) [%(levelname)s] %(name)s: %(message)s',
    datefmt='%m-%d %H:%M'
)
db.init('var/data/graveyard.db')


task = tasks.FollowingFollowerTask(db.Account.get_by_id(1))

task = tasks.BroadcastTask(db.Account.get_by_id(1))

result = task(
    requests_per_minute=30, 
    local_object_duration=60*60*24*300,
    broadcast_active_duration=60*60*24*300,
    broadcast_incremental_backup=True,
    image_local_cache=True
)
print(result)

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


task = tasks.MovieTask(db.Account.get_by_id(1))

#task(requests_per_minute=50, local_object_duration = 60*60*24*7, proxy='http://127.0.0.1:8118')
result = task(requests_per_minute=30, local_object_duration = 60*60*24*7)
print(result)

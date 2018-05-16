# encoding: utf-8
import db
import tasks
import logging


logging.basicConfig(
    level=logging.DEBUG if __debug__ else logging.INFO,
    format='[%(asctime)s] (%(pathname)s:%(lineno)s) [%(levelname)s] %(name)s: %(message)s',
    datefmt='%m-%d %H:%M'
)
db.init('var/data/graveyard.db')


task = tasks.FetchAccountUser(db.Account.get_by_id(1))

task(requests_per_minute=120)
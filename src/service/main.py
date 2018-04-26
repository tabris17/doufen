# encoding: utf-8
import argparse
import logging
import os
import sys
import time
from distutils.version import StrictVersion

import tornado

import urls
import db

PROG_NAME = 'gravekeeper'
PROG_DESCRIPTION = ''
PROG_VERSION = '0.1.0'
DEFAULT_SERVICE_PORT = 8398
DEFAULT_SERVICE_ADDRESS = '127.0.0.1'
DEFAULT_DATEBASE = 'var/data/graveyard.db'

__VERSION__ = '0.1.0'


def parse_args(args):
    """
    解析命令参数
    """
    parser = argparse.ArgumentParser(
        prog=PROG_NAME, description=PROG_DESCRIPTION)
    parser.add_argument('-d', '--debug', action='store_true',
                        default=False, help='print debug information')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + PROG_VERSION)
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_SERVICE_PORT,
                        metavar='port', help='specify the port to listen')
    parser.add_argument('-b', '--bind', default=DEFAULT_SERVICE_ADDRESS,
                        metavar='address', dest='address', help='specify the IP address to bind')
    parser.add_argument('-s', '--save', default=DEFAULT_DATEBASE,
                        metavar='database', dest='database', help='specify the database file')
    return parser.parse_args(args)


def init_db(path):
    """
    初始化数据库
    """
    with db.get_instance(path) as db_instance:
        try:
            data_verion = db_instance['version']
            if StrictVersion(data_verion) < StrictVersion(__VERSION__) and \
                not db.upgrade(db_instance, data_verion, __VERSION__):
                raise Exception('升级数据库失败')
        except KeyError:
            db_instance['version'] = __VERSION__

        return db_instance


def main(args):
    """
    程序主函数
    """
    parsed_args = parse_args(args)

    logging.basicConfig(
        level=logging.DEBUG if parsed_args.debug else logging.INFO,
        format='[%(asctime)s] (%(pathname)s:%(lineno)s) %(name)s[%(levelname)s]: %(message)s',
        datefmt='%m-%d %H:%M'
    )

    logging.debug('initiliaze database')
    db_instance = init_db(parsed_args.database)

    base_path = os.path.dirname(__file__)
    settings = {
        'autoreload': parsed_args.debug,
        'debug': parsed_args.debug,
        'template_path': os.path.join(base_path, 'views'),
        'static_path': os.path.join(base_path, 'static'),
        'static_url_prefix': '/static/',
        '_database': db_instance,
    }

    application = tornado.web.Application(urls.patterns, **settings)
    application.listen(parsed_args.port, parsed_args.address)

    logging.debug('start ioloop')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main(sys.argv[1:])

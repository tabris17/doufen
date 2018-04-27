# encoding: utf-8
import argparse
import logging
import os
import sys
import time

import tornado

import urls
import version
import server

DEFAULT_SERVICE_PORT = 8398
DEFAULT_SERVICE_HOST = '127.0.0.1'
DEFAULT_DATEBASE = 'var/data/graveyard.db'


def parse_args(args):
    """
    解析命令参数
    """
    parser = argparse.ArgumentParser(
        prog=version.__prog_name__, description=version.__description__)
    parser.add_argument('-d', '--debug', action='store_true',
                        default=False, help='print debug information')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + version.__version__)
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_SERVICE_PORT,
                        metavar='port', help='specify the port to listen')
    parser.add_argument('-s', '--save', default=DEFAULT_DATEBASE,
                        metavar='database', dest='database', help='specify the database file')
    return parser.parse_args(args)


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

    base_path = os.path.dirname(__file__)
    settings = {
        'autoreload': parsed_args.debug,
        'debug': parsed_args.debug,
        'template_path': os.path.join(base_path, 'views'),
        'static_path': os.path.join(base_path, 'static'),
        'static_url_prefix': '/static/',
        '_database_path': parsed_args.database,
    }

    application = server.Application(urls.patterns, **settings)
    application.listen(parsed_args.port, DEFAULT_SERVICE_HOST)

    logging.debug('start ioloop')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main(sys.argv[1:])

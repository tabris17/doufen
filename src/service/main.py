# encoding: utf-8
import argparse
import logging
import os
import sys
import time

import db
import version
from server import Server
from worker import Worker
from setting import settings, DEFAULT_SERVICE_PORT, DEFAULT_DATEBASE, DEFAULT_CACHE_PATH, DEFAULT_SERVICE_HOST


def parse_args(args):
    """
    解析命令参数
    """
    parser = argparse.ArgumentParser(
        prog=version.__prog_name__,
        description=version.__description__
    )
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + version.__version__)
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_SERVICE_PORT,
                        metavar='port', help='specify the port to listen')
    parser.add_argument('-s', '--save', default=DEFAULT_DATEBASE,
                        metavar='database', dest='database', help='specify the database file')
    parser.add_argument('-c', '--cache', default=DEFAULT_CACHE_PATH,
                        metavar='cache', dest='cache', help='specify the cache path')
    return parser.parse_args(args)


def main(args):
    """
    程序主函数
    """
    parsed_args = parse_args(args)

    settings.update({
        'cache': parsed_args.cache,
        'database': parsed_args.database,
        'port': parsed_args.port,
    })

    logging.basicConfig(
        level=logging.DEBUG if settings.get('debug') else logging.INFO,
        format='[%(asctime)s] (%(pathname)s:%(lineno)s) [%(levelname)s] %(name)s: %(message)s',
        datefmt='%m-%d %H:%M'
    )

    db.init(parsed_args.database)

    server = Server(parsed_args.port, DEFAULT_SERVICE_HOST, parsed_args.cache)
    server.run()


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('exit')

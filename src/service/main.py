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

DEFAULT_SERVICE_PORT = 8398
DEFAULT_SERVICE_HOST = '127.0.0.1'
DEFAULT_DATEBASE = 'var/data/graveyard.db'


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
    return parser.parse_args(args)


def main(args):
    """
    程序主函数
    """
    parsed_args = parse_args(args)

    logging.basicConfig(
        level=logging.DEBUG if __debug__ else logging.INFO,
        format='[%(asctime)s] (%(pathname)s:%(lineno)s) [%(levelname)s] %(name)s: %(message)s',
        datefmt='%m-%d %H:%M'
    )

    db.init(parsed_args.database)

    server = Server(parsed_args.port, DEFAULT_SERVICE_HOST)
    server.run()


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('exit')

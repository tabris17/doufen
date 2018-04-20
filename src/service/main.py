#!/usr/bin/env python
# encoding: utf-8

import sys
import time
import tornado
import argparse
import logging
from controller import Controller

SERVICE_PORT = 8398
SERVICE_HOST = '127.0.0.1'
DATEBASE_CONNECTION = 'mysql://127.0.0.1:8399'

def parse_args(args):
    """
    parse program arguments
    """
    parser = argparse.ArgumentParser(description='pixian service')
    parser.add_argument('-d', '--debug', action='store_true',
                        default=False, help='print debug information')
    parser.add_argument('-p', '--port', type=int, default=SERVICE_PORT,
                        help='specify the port to listen')
    parser.add_argument('-a', '--address', default=SERVICE_HOST,
                        metavar='IP', help='specify the address to listen')
    parser.add_argument('-db', default=DATEBASE_CONNECTION,
                        metavar='CONNECTION', help='specify the database connection')
    return parser.parse_args(args)


def main(args):
    """
    main entry
    """
    parsed_args = parse_args(args[1:])

    logging.basicConfig(
        level=logging.DEBUG if parsed_args.debug else logging.INFO,
        format='[%(asctime)s] (%(pathname)s:%(lineno)s) %(name)s:%(levelname)s: %(message)s',
        datefmt='%m-%d %H:%M'
    )

    application = tornado.web.Application([
        (r'/controller', Controller),
    ])
    application.listen(parsed_args.port, parsed_args.address)
    logging.debug('start ioloop')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main(sys.argv)

#!/usr/bin/env python
# encoding: utf-8

import sys
import time
import tornado
import argparse
import logging
from controller import Controller


def parse_args(args):
    """
    parse program arguments
    """
    parser = argparse.ArgumentParser(description='pixian service')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='print debug information')
    parser.add_argument('-p', '--port', type=int, default=8398, help='specify the port to listen')
    parser.add_argument('-a', '--address', default='127.0.0.1', metavar='IP', help='specify the address to listen')
    parser.add_argument('-db', default='localhost:8399', metavar='CONNECTION', help='specify the mysql connection')
    return parser.parse_args(args)


def main(args):
    """
    main entry
    """
    options = parse_args(args[1:])

    logging.basicConfig(
        level=logging.DEBUG if options.debug else logging.INFO,
        format='[%(asctime)s] (%(pathname)s:%(lineno)s) %(name)s:%(levelname)s: %(message)s',
        datefmt='%m-%d %H:%M'
    )

    application = tornado.web.Application([
        (r'/controller', Controller),
    ])
    application.listen(options.port, options.address)
    logging.debug('start ioloop')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        logging.info('catch keyboard interrupt')


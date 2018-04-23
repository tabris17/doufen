# encoding: utf-8
import argparse
import logging
import sys
import time

import tornado
import handlers


PROG_NAME = 'gravekeeper'
PROG_DESCRIPTION = ''
PROG_VERSION = '0.1.0'
DEFAULT_SERVICE_PORT = 8398
DEFAULT_SERVICE_ADDRESS = '127.0.0.1'
DEFAULT_DATEBASE = 'graves.db'


def parse_args(args):
    """
    parse program arguments
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


def main(args):
    """
    main entry
    """
    parsed_args = parse_args(args)

    logging.basicConfig(
        level=logging.DEBUG if parsed_args.debug else logging.INFO,
        format='[%(asctime)s] (%(pathname)s:%(lineno)s) %(name)s:%(levelname)s: %(message)s',
        datefmt='%m-%d %H:%M'
    )

    application = tornado.web.Application([
        (r'/', handlers.Main),
        (r'/notify', handlers.Notifier),
    ], debug=parsed_args.debug)
    application.listen(parsed_args.port, parsed_args.address)
    logging.debug('start ioloop')
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main(sys.argv[1:])

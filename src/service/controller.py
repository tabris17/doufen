# encoding: utf-8
import logging
import json
from tornado.websocket import WebSocketHandler


class Controller(WebSocketHandler):
    """
    Controller class
    """

    def check_origin(self, origin):
        return True

    def write_message(self, message, binary=False):
        logging.debug('send message: "{0}"'.format(message))
        return super().write_message(message, binary)

    def open(self):
        logging.debug('websocket open')

    def on_close(self):
        logging.debug('websocket close')
        pass

    def on_message(self, message):
        logging.debug('receive message: "{0}"'.format(message))
        data = json.loads(message)
        data.get('type')
        data.get('session')
        data.get('body')

    def on_connection_close(self):
        logging.debug('connection close')

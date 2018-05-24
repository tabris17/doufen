# encoding: utf-8
import json
import logging

import tornado
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler

import db


class BaseRequestHandler(RequestHandler):
    """
    默认继承
    """

    @property
    def server(self):
        return self.application.server


class Notifier(WebSocketHandler):
    """
    用于后台向前台图形程序发送通知
    """

    def check_origin(self, origin):
        return origin == 'localhost'

    def on_message(self, message):
        logging.debug('receive message: "{0}"'.format(message))

    def open(self):
        logging.debug('websocket open')
        self.application.register_client(self)

    def on_close(self):
        logging.debug('websocket close')
        self.application.unregister_client(self)


class Main(BaseRequestHandler):
    """
    主页
    """

    def get(self):
        self.render('index.html')


class Manual(BaseRequestHandler):
    """
    使用手册
    """

    def get(self):
        self.render('manual.html')


class Book(BaseRequestHandler):
    """
    书
    """
    def get(self, douban_id):
        try:
            subject = db.Book.get(db.Book.douban_id == douban_id)
            history = db.BookHistorical.select().where(db.BookHistorical.id == subject.id)
        except db.Book.DoesNotExist:
            raise tornado.web.HTTPError(404)
        try:
            mine = db.MyBook.get(db.MyBook.book == subject)
        except db.MyBook.DoesNotExist:
            mine = None
        self.render('book.html', subject=subject, history=history, mine=mine)


class Music(BaseRequestHandler):
    """
    音乐
    """
    def get(self, douban_id):
        try:
            subject = db.Music.get(db.Music.douban_id == douban_id)
            history = db.MusicHistorical.select().where(db.MusicHistorical.id == subject.id)
        except db.Music.DoesNotExist:
            raise tornado.web.HTTPError(404)
        try:
            mine = db.MyMusic.get(db.MyMusic.music == subject)
        except db.MyMusic.DoesNotExist:
            mine = None
        self.render('music.html', subject=subject, history=history, mine=mine)


class Movie(BaseRequestHandler):
    """
    电影
    """
    def get(self, douban_id):
        try:
            subject = db.Movie.get(db.Movie.douban_id == douban_id)
            history = db.MovieHistorical.select().where(db.MovieHistorical.id == subject.id)
        except db.Movie.DoesNotExist:
            raise tornado.web.HTTPError(404)
        try:
            mine = db.MyMovie.get(db.MyMovie.movie == subject)
        except db.MyMovie.DoesNotExist:
            mine = None
        self.render('movie.html', subject=subject, history=history, mine=mine)

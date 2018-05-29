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

    
    def get_current_user(self):
        """
        获取当前用户，没有则返回None
        """
        try:
            return db.Account.getDefault().user
        except db.Account.DoesNotExist:
            pass


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
            mine = db.MyBook.get(db.MyBook.book == subject, db.MyBook.user == self.get_current_user())
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
            mine = db.MyMusic.get(db.MyMusic.music == subject, db.MyMusic.user == self.get_current_user())
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
            mine = db.MyMovie.get(db.MyMovie.movie == subject, db.MyMovie.user == self.get_current_user())
        except db.MyMovie.DoesNotExist:
            mine = None
        self.render('movie.html', subject=subject, history=history, mine=mine)


class Broadcast(BaseRequestHandler):
    """
    广播
    """
    def get(self, douban_id):
        try:
            subject = db.Broadcast.get(db.Broadcast.douban_id == douban_id)
        except db.Broadcast.DoesNotExist:
            raise tornado.web.HTTPError(404)

        self.render('broadcast.html', subject=subject)



class User(BaseRequestHandler):
    """
    用户
    """
    def get(self, douban_id):
        try:
            subject = db.User.get(db.User.douban_id == douban_id)
            history = db.UserHistorical.select().where(db.UserHistorical.id == subject.id)
        except db.User.DoesNotExist:
            raise tornado.web.HTTPError(404)

        is_follower = db.Follower.select().where(
            db.Follower.follower == subject,
            db.Follower.user == self.get_current_user()
        ).exists()

        is_following = db.Following.select().where(
            db.Following.following_user == subject,
            db.Following.user == self.get_current_user()
        ).exists()

        self.render('user.html', subject=subject, history=history, is_follower=is_follower, is_following=is_following)

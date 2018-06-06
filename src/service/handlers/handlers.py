# encoding: utf-8
import json
import logging

import tornado
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
from pyquery import PyQuery

import db


class NotFound(RequestHandler):
    """
    默认404页
    """
    def get(self):
        self.render('errors/404.html')


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

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('errors/404.html')
        else:
            self.write('Error')


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


class Shutdown(BaseRequestHandler):
    """
    退出系统
    """
    def shutdown(self):
        self.server.stop_workers()
        tornado.ioloop.IOLoop.current().stop()

    def get(self):
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.add_callback(self.shutdown)
        self.write('OK')


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

        comments = db.Comment.select().join(db.User).where(
            db.Comment.target_type == 'broadcast',
            db.Comment.target_douban_id == subject.douban_id
        )

        self.render('broadcast.html', subject=subject, comments=comments)



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


class Attachment(BaseRequestHandler):
    """
    从本地缓存载入附件
    """

    def get(self, url):
        try:
            attachment = db.Attachment.get(db.Attachment.url == url)
            if attachment.local:
                self.redirect(self.reverse_url('cache', attachment.local))
                return
        except db.Attachment.DoesNotExist:
            pass

        self.redirect(url)


class Note(BaseRequestHandler):
    """
    日记
    """
    def get(self, douban_id):
        try:
            subject = db.Note.get(db.Note.douban_id == douban_id)
            history = db.NoteHistorical.select().where(db.NoteHistorical.id == subject.id)
        except db.User.DoesNotExist:
            raise tornado.web.HTTPError(404)

        comments = db.Comment.select().join(db.User).where(
            db.Comment.target_type == 'note',
            db.Comment.target_douban_id == subject.douban_id
        )

        dom = PyQuery(subject.content)
        dom_iframe = dom('iframe')
        dom_iframe.before('<p class="title"><a href="{0}" class="external-link">站外视频</a></p>'.format(dom_iframe.attr('src')))
        dom_iframe.remove()
        dom('a').add_class('external-link')

        self.render('note.html', note=subject, comments=comments, content=dom)


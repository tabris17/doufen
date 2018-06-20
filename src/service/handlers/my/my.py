# encoding: utf-8
import math

import handlers
import db

import tornado


_PAGE_SIZE_ = 50


def require_login(func):
    """
    用户登录装饰器
    """
    def wrapper(self, *args, **kwargs):
        try:
            db.Account.get_default()
        except db.Account.DoesNotExist:
            # 未登录
            self.redirect(self.reverse_url('settings.accounts.login'))
            return
        except db.User.DoesNotExist:
            # 已登录，未抓取
            self.redirect(self.reverse_url('dashboard'))
            return
        return func(self, *args, **kwargs)

    return wrapper


class BaseRequestHandler(handlers.BaseRequestHandler):
    """
    基础类
    """
    def prepare(self):
        try:
            db.Account.get_default()
        except db.Account.DoesNotExist:
            # 未登录
            self.redirect(self.reverse_url('settings.accounts.login'))
        except db.User.DoesNotExist:
            # 已登录，未抓取
            self.redirect(self.reverse_url('dashboard'))

    def list(self, query, template, **kwargs):
        try:
            page = int(self.get_query_argument('page', 1))
        except:
            page = 1
        total_rows = query.count()
        total_pages = int(math.ceil(total_rows / _PAGE_SIZE_))

        rows = query.paginate(page, _PAGE_SIZE_)
        self.render(template, rows=rows, page=page, total_pages=total_pages, total_rows=total_rows, page_size=_PAGE_SIZE_, **kwargs)


class Index(BaseRequestHandler):
    def get(self):
        self.redirect(self.reverse_url('my.following'))


class Following(BaseRequestHandler):
    def get(self):
        query = db.Following.select(db.Following, db.User).join(
            db.User, on=db.Following.following_user
        ).where(db.Following.user == self.get_current_user()).order_by(db.Following.id.desc())
        self.list(query, 'my/following.html')


class Followers(BaseRequestHandler):
    def get(self):
        query = db.Follower.select(db.Follower, db.User).join(
            db.User, on=db.Follower.follower
        ).where(db.Follower.user == self.get_current_user()).order_by(db.Follower.id.desc())
        self.list(query, 'my/followers.html')


class Blocklist(BaseRequestHandler):
    def get(self):
        query = db.BlockUser.select(db.BlockUser, db.User).join(
            db.User, on=db.BlockUser.block_user
        ).where(db.BlockUser.user == self.get_current_user()).order_by(db.BlockUser.id.desc())
        self.list(query, 'my/blocklist.html')


class FollowingHistorical(BaseRequestHandler):
    def get(self):
        query = db.FollowingHistorical.select(db.FollowingHistorical, db.User).join(
            db.User, on=db.FollowingHistorical.following_user
        ).where(db.FollowingHistorical.user == self.get_current_user()).order_by(db.FollowingHistorical.id.desc())
        self.list(query, 'my/following_historical.html')


class FollowersHistorical(BaseRequestHandler):
    def get(self):
        query = db.FollowerHistorical.select(db.FollowerHistorical, db.User).join(
            db.User, on=db.FollowerHistorical.follower
        ).where(db.FollowerHistorical.user == self.get_current_user()).order_by(db.FollowerHistorical.id.desc())
        self.list(query, 'my/followers_historical.html')


class BlocklistHistorical(BaseRequestHandler):
    def get(self):
        query = db.BlockUserHistorical.select(db.BlockUserHistorical, db.User).join(
            db.User, on=db.BlockUserHistorical.block_user
        ).where(db.BlockUserHistorical.user == self.get_current_user()).order_by(db.BlockUserHistorical.id.desc())
        self.list(query, 'my/blocklist_historical.html')


class Movie(BaseRequestHandler):
    def get(self, status):
        query = db.MyMovie.select(db.MyMovie, db.Movie).join(
            db.Movie, on=db.MyMovie.movie
        ).where(db.MyMovie.user == self.get_current_user(), db.MyMovie.status == status).order_by(db.MyMovie.id.desc())
        self.list(query, 'my/movie.html', status=status)


class MovieHistorical(BaseRequestHandler):
    def get(self):
        query = db.MyMovieHistorical.select(db.MyMovieHistorical, db.Movie).join(
            db.Movie, on=db.MyMovieHistorical.movie
        ).where(db.MyMovieHistorical.user == self.get_current_user()).order_by(db.MyMovieHistorical.id.desc())
        self.list(query, 'my/movie_historical.html')


class Book(BaseRequestHandler):
    def get(self, status):
        query = db.MyBook.select(db.MyBook, db.Book).join(
            db.Book, on=db.MyBook.book
        ).where(db.MyBook.user == self.get_current_user(), db.MyBook.status == status).order_by(db.MyBook.id.desc())
        self.list(query, 'my/book.html', status=status)


class BookHistorical(BaseRequestHandler):
    def get(self):
        query = db.MyBookHistorical.select(db.MyBookHistorical, db.Book).join(
            db.Book, on=db.MyBookHistorical.book
        ).where(db.MyBookHistorical.user == self.get_current_user()).order_by(db.MyBookHistorical.id.desc())
        self.list(query, 'my/book_historical.html')


class Music(BaseRequestHandler):
    def get(self, status):
        query = db.MyMusic.select(db.MyMusic, db.Music).join(
            db.Music, on=db.MyMusic.music
        ).where(db.MyMusic.user == self.get_current_user(), db.MyMusic.status == status).order_by(db.MyMusic.id.desc())
        self.list(query, 'my/music.html', status=status)


class MusicHistorical(BaseRequestHandler):
    def get(self):
        query = db.MyMusicHistorical.select(db.MyMusicHistorical, db.Music).join(
            db.User, on=db.MyMusicHistorical.music
        ).where(db.MyMusicHistorical.user == self.get_current_user()).order_by(db.MyMusicHistorical.id.desc())
        self.list(query, 'my/music_historical.html')


class Broadcast(BaseRequestHandler):
    def get(self):
        query = db.Timeline.select(
            db.Timeline, 
            db.Broadcast, 
            db.User
        ).join(db.Broadcast).join(db.User, db.JOIN.LEFT_OUTER, on=db.Timeline.broadcast.user).where(db.Timeline.user == self.get_current_user()).order_by(db.Timeline.id.desc())
        self.list(query, 'my/broadcast.html')


class Note(BaseRequestHandler):
    def get(self):
        query = db.Note.select().where(db.Note.user == self.get_current_user()).order_by(db.Note.created.desc())
        self.list(query, 'my/note.html')


class Photo(BaseRequestHandler):
    def get(self):
        query = db.PhotoAlbum.select().where(db.PhotoAlbum.user == self.get_current_user())
        self.list(query, 'my/photo.html')


class Favorite(BaseRequestHandler):
    def get(self, category):
        if not category:
            category = 'note'

        categories = {
            'note': '1015',
            #'picture': '1025',
            'photo': '1026',
        }

        if category not in categories:
            raise tornado.web.HTTPError(404)
        target_type = categories[category]

        def get_user(subject):
            if subject.user_id == 0:
                return
            try:
                return subject.user
            except db.User.DoesNotExist:
                pass

        if category == 'note':
            query = db.Favorite.select(
                db.Favorite,
                db.Note,
                db.User
            ).where(
                (db.Favorite.user == self.get_current_user()) & (db.Favorite.target_type == target_type)
            ).join(
                db.Note,
                db.JOIN.INNER,
                on=(db.Favorite.target_douban_id == db.Note.douban_id).alias('note')
            ).join(db.User, db.JOIN.LEFT_OUTER, on=db.Note.user)
        elif category == 'photo':
            query = db.Favorite.select(
                db.Favorite,
                db.PhotoAlbum
            ).where(
                (db.Favorite.user == self.get_current_user()) & (db.Favorite.target_type == target_type)
            ).join(
                db.PhotoAlbum, 
                db.JOIN.INNER, 
                on=(db.Favorite.target_douban_id == db.PhotoAlbum.douban_id).alias('photo_album')
            ).join(db.User, db.JOIN.LEFT_OUTER, on=db.PhotoAlbum.user)
        elif category == 'picture':
            query.join(db.PhotoAlbum, db.JOIN.INNER)

        self.list(query, 'my/favorite/{0}.html'.format(category), get_user=get_user)


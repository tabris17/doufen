# encoding: utf-8
from peewee import *
import datetime


DATEBASE_PATH = ''

dbo = SqliteDatabase(None)

def init(db_path, create_tables=True):
    """
    初始化数据库
    """
    global DATEBASE_PATH
    DATEBASE_PATH = db_path
    dbo.init(db_path)

    if create_tables:
        with dbo:
            dbo.create_tables([
                Account,
                User,
                UserHistorical,
                Movie,
                MovieHistorical,
                Book,
                BookHistorical,
                Music,
                MusicHistorical,
                Setting,
                Following,
                FollowingHistorical,
                Follower,
                FollowerHistorical,
                BlockUser,
                BlockUserHistorical,
                MyMovie,
                MyBook,
                MyMusic,
                MyMovieHistorical,
                MyBookHistorical,
                MyMusicHistorical,
            ])


class BaseModel(Model):
    class Meta:
        database = dbo

    _attrs_to_compare_ = []

    def equals(self, field_values):
        """
        比较两个模型的值是否相等
        """
        for attr in self._attrs_to_compare_:
            if str(getattr(self, attr)) != str(field_values.get(attr)):
                return False
        return True

    @classmethod
    def safe_create(cls, **kwargs):
        fields = cls._meta.sorted_field_names
        return cls.create(**{k: v for k, v in kwargs.items() if k in fields})

    @classmethod
    def safe_update(cls, **kwargs):
        fields = cls._meta.sorted_field_names
        return cls.update(**{k: v for k, v in kwargs.items() if k in fields})

    @classmethod
    def clone(cls, model, defaults=dict()):
        """
        从另一个模型对象中复制数据
        """
        fields = list(cls._meta.sorted_field_names)
        primary_key_name = cls._meta.primary_key.name
        fields.remove(primary_key_name)
        field_values = {}

        for field_name in fields:
            field_values[field_name] = getattr(model, field_name) if hasattr(model, field_name) else defaults.get(field_name)
        field_values[model._meta.table_name + '_id'] = getattr(model, primary_key_name)
        
        return cls.create(**field_values)


class User(BaseModel):
    """
    用户
    """
    _attrs_to_compare_ = [
        'unique_name',
        'name',
        'created',
        'desc',
        'type',
        'loc_id',
        'loc_name',
        'signature',
        'avatar',
        'large_avatar',
        'alt',
        'is_banned',
        'is_suicide',
    ]

    douban_id = IntegerField(unique=True, help_text='豆瓣ID')
    unique_name = CharField(unique=True, help_text='豆瓣域名')
    name = CharField(help_text='用户名称', null=True)
    created = CharField(help_text='加入时间', null=True)
    desc = TextField(help_text='描述', null=True)
    type = CharField(help_text='类型。已知有user类型', null=True)
    loc_id = IntegerField(help_text='所在地ID', null=True)
    loc_name = CharField(help_text='所在地', null=True)
    signature = TextField(help_text='签名', null=True)
    avatar = CharField(help_text='头像', null=True)
    large_avatar = CharField(help_text='头像大图', null=True)
    alt = CharField(help_text='用户主页', null=True)
    is_banned = BooleanField(help_text='是否被封禁', null=True)
    is_suicide = BooleanField(help_text='是否已主动注销', null=True)
    version = IntegerField(help_text='当前版本')
    updated_at = DateTimeField(help_text='抓取时间', default=datetime.datetime.now())


class UserHistorical(User):
    """
    用户历史数据
    """
    class Meta:
        table_name = 'user_historical'

    douban_id = IntegerField(help_text='豆瓣ID')
    unique_name = CharField(help_text='豆瓣域名')
    user = ForeignKeyField(User, field=User.id, help_text='原始对象ID')


class Account(BaseModel):
    """
    豆瓣帐号
    """

    name = CharField(null=True, help_text='帐号显示名称，对应豆瓣域名')
    user = ForeignKeyField(User, default=None, null=True, help_text='对应的用户')
    session = CharField(help_text='登录会话的Cookie')
    created = TimestampField(help_text='创建时间')
    is_activated = BooleanField(default=False, help_text='是否已激活')
    is_invalid = BooleanField(default=False, help_text='是否失效')

    @classmethod
    def getDefault(cls):
        return cls.select().where(
            cls.is_invalid == False,
            cls.user is not None
        ).order_by(
            cls.is_activated.desc()
        ).get()


class BlockUser(BaseModel):
    """
    黑名单用户
    """
    class Meta:
        table_name = 'block_user'
        indexes = (
            (('user', 'block_user'), True),
        )

    user = ForeignKeyField(User, help_text='用户')
    block_user = ForeignKeyField(User, help_text='黑名单用户', null=True)
    block_username = CharField(help_text='黑名单用户名')
    created_at = DateTimeField(help_text='创建时间', default=datetime.datetime.now())
    updated_at = DateTimeField(help_text='最后一次抓取时间', default=datetime.datetime.now())
    

class BlockUserHistorical(BlockUser):
    """
    黑名单用户历史
    """
    class Meta:
        table_name = 'block_user_historical'
        indexes = (
            (('user',), False),
        )

    deleted_at = DateTimeField(help_text='删除时间', default=datetime.datetime.now())


class Follower(BaseModel):
    """
    被关注
    """
    class Meta:
        indexes = (
            (('user', 'follower_username'), True),
        )

    user = ForeignKeyField(User, help_text='用户')
    follower = ForeignKeyField(User, help_text='用户的关注者', null=True)
    follower_username = CharField(help_text='关注者用户名')
    created_at = DateTimeField(help_text='创建时间', default=datetime.datetime.now())
    updated_at = DateTimeField(help_text='最后一次抓取时间', default=datetime.datetime.now())


class FollowerHistorical(Follower):
    """
    已经取消的关注
    """
    class Meta:
        table_name = 'follower_historical'
        indexes = (
            (('user',), False),
        )

    deleted_at = DateTimeField(help_text='删除时间', default=datetime.datetime.now())


class Following(BaseModel):
    """
    关注
    """
    class Meta:
        indexes = (
            (('user', 'following_username'), True),
        )

    user = ForeignKeyField(User, help_text='用户')
    following_user = ForeignKeyField(User, help_text='用户的关注对象', null=True)
    following_username = CharField(help_text='关注对象用户名')
    created_at = DateTimeField(help_text='创建时间', default=datetime.datetime.now())
    updated_at = DateTimeField(help_text='最后一次抓取时间', default=datetime.datetime.now())


class FollowingHistorical(Following):
    """
    已经取消的关注
    """
    class Meta:
        table_name = 'following_historical'
        indexes = (
            (('user',), False),
        )

    deleted_at = DateTimeField(help_text='删除时间', default=datetime.datetime.now())


class Movie(BaseModel):
    """
    电影
    """
    _attrs_to_compare_ = [
        'rating',
        'author',
        'alt_title',
        'image',
        'title',
        'summary',
        'attrs',
        'alt',
        'tags',
    ]

    douban_id = CharField(unique=True, help_text='豆瓣ID')
    rating = TextField(help_text='评分', null=True)
    author = TextField(help_text='作者', null=True)
    alt_title = TextField(help_text='又名', null=True)
    image = CharField(help_text='电影海报', null=True)
    title = CharField(help_text='中文名')
    summary = TextField(help_text='简介', null=True)
    attrs = TextField(help_text='属性', null=True)
    alt = CharField(help_text='条目页URL', null=True)
    tags = TextField(help_text='标签', null=True)
    version = IntegerField(help_text='当前版本')
    updated_at = DateTimeField(help_text='抓取时间', default=datetime.datetime.now())


class MovieHistorical(Movie):
    """
    电影历史数据
    """
    class Meta:
        table_name = 'movie_historical'
    
    douban_id = CharField(help_text='豆瓣ID')
    movie = ForeignKeyField(Movie, field=Movie.id)


class Book(BaseModel):
    """
    书
    """
    _attrs_to_compare_ = [
        'title',
        'rating',
        'subtitle',
        'author',
        'pubdate',
        'tags',
        'origin_title',
        'image',
        'binding',
        'translator',
        'catalog',
        'pages',
        'images',
        'alt',
        'publisher',
        'isbn10',
        'isbn13',
        'url',
        'alt_title',
        'author_intro',
        'summary',
        'price',
    ]

    douban_id = CharField(unique=True, help_text='豆瓣ID')
    title = CharField(help_text='标题', null=True)
    rating = TextField(help_text='评分', null=True)
    subtitle = CharField(help_text='副标题', null=True)
    author = TextField(help_text='作者', null=True)
    pubdate = CharField(help_text='上映日期', null=True)
    tags = TextField(help_text='标签', null=True)
    origin_title = CharField(help_text='标题', null=True)
    image = CharField(help_text='图片', null=True)
    binding = CharField(help_text='装帧', null=True)
    translator = TextField(help_text='翻译', null=True)
    catalog = TextField(help_text='目录', null=True)
    pages = CharField(help_text='页数', null=True)
    images = TextField(help_text='图片', null=True)
    alt = CharField(help_text='条目页URL', null=True)
    publisher = CharField(help_text='出版社', null=True)
    isbn10 = CharField(help_text='ISBN', null=True)
    isbn13 = CharField(help_text='ISBN', null=True)
    url = CharField(help_text='URL地址', null=True)
    alt_title = CharField(help_text='标题', null=True)
    author_intro = TextField(help_text='作者介绍', null=True)
    summary = TextField(help_text='介绍', null=True)
    price = CharField(help_text='价格', null=True)
    version = IntegerField(help_text='当前版本')
    updated_at = DateTimeField(help_text='抓取时间', default=datetime.datetime.now())


class BookHistorical(Book):
    """
    书历史数据
    """
    class Meta:
        table_name = 'book_historical'
    
    douban_id = CharField(help_text='豆瓣ID')
    book = ForeignKeyField(Book, field=Book.id)


class Music(BaseModel):
    """
    音乐
    """
    _attrs_to_compare_ = [
        'rating'
        'author',
        'alt_title', 
        'image',
        'title',
        'summary',
        'attrs',
        'alt',
        'tags',
    ]

    douban_id = CharField(unique=True, help_text='豆瓣ID')
    rating = TextField(help_text='评分', null=True)
    author = TextField(help_text='作者', null=True)
    alt_title = CharField(help_text='标题', null=True)
    image = CharField(help_text='图片', null=True)
    title = CharField(help_text='标题', null=True)
    summary = TextField(help_text='介绍', null=True)
    attrs = TextField(help_text='属性', null=True)
    alt = CharField(help_text='地址', null=True)
    tags = TextField(help_text='标签', null=True)
    version = IntegerField(help_text='当前版本')
    updated_at = DateTimeField(help_text='抓取时间', default=datetime.datetime.now())


class MusicHistorical(Music):
    """
    音乐历史数据
    """
    class Meta:
        table_name = 'music_historical'
    
    douban_id = CharField(help_text='豆瓣ID')
    music = ForeignKeyField(Music, field=Music.id)


class BaseMyInterest(BaseModel):
    class Meta:
        indexes = (
            (('user', 'subject_id'), True),
            (('user', 'status'), False),
        )

    _attrs_to_compare_ = [
        'rating',
        'tags',
        'comment',
        'create_time',
        'status',
    ]

    subject_id = CharField(help_text='豆瓣对象ID')
    user = ForeignKeyField(User, help_text='用户')
    rating = CharField(null=True, help_text='评分')
    tags = CharField(null=True, help_text='标签')
    create_time = CharField(null=True, help_text='创建时间')
    comment = CharField(null=True, help_text='评论')
    status = CharField(help_text='状态')
    created_at = DateTimeField(help_text='创建时间', default=datetime.datetime.now())
    updated_at = DateTimeField(help_text='最后一次抓取时间', default=datetime.datetime.now())


class MyBook(BaseMyInterest):
    """
    我看的书
    """
    class Meta:
        table_name = 'my_book'

    book = ForeignKeyField(Book, help_text='书')


class MyBookHistorical(MyBook):
    class Meta:
        table_name = 'my_book_historical'
        indexes = (
            (('user', 'subject_id'), False),
        )
    
    deleted_at = DateTimeField(help_text='删除时间', default=datetime.datetime.now())


class MyMovie(BaseMyInterest):
    """
    我看的电影
    """
    class Meta:
        table_name = 'my_movie'

    movie = ForeignKeyField(Movie, help_text='电影')


class MyMovieHistorical(MyMovie):
    class Meta:
        table_name = 'my_movie_historical'
        indexes = (
            (('user', 'subject_id'), False),
        )
    
    deleted_at = DateTimeField(help_text='删除时间', default=datetime.datetime.now())


class MyMusic(BaseMyInterest):
    """
    我听的音乐
    """
    class Meta:
        table_name = 'my_music'

    music = ForeignKeyField(Music, help_text='音乐')


class MyMusicHistorical(MyMusic):
    class Meta:
        table_name = 'my_music_historical'
        indexes = (
            (('user', 'subject_id'), False),
        )
    
    deleted_at = DateTimeField(help_text='删除时间', default=datetime.datetime.now())


class Setting(BaseModel):
    """
    配置信息
    """
    name = CharField(unique=True, help_text='名称')
    value = TextField(help_text='值')

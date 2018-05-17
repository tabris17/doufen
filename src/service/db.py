# encoding: utf-8
from peewee import *
import datetime


__all__ = ['dbo', 'init', 'Setting', 'Account', 'Following',
           'User', 'UserHistorical',
           'Movie', 'MovieHistorical',
           'DATEBASE_PATH']

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
                Setting,
                Following,
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
    name = CharField(help_text='用户名称')
    created = CharField(help_text='加入时间')
    desc = TextField(help_text='描述')
    type = CharField(help_text='类型。已知有user类型')
    loc_id = IntegerField(help_text='所在地ID')
    loc_name = CharField(help_text='所在地')
    signature = TextField(help_text='签名')
    avatar = CharField(help_text='头像')
    large_avatar = CharField(help_text='头像大图')
    alt = CharField(help_text='用户主页')
    is_banned = BooleanField(help_text='是否被封禁')
    is_suicide = BooleanField(help_text='是否已主动注销')
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
    user = ForeignKeyField(User, field=User.id, help_text='豆瓣ID')


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


class Follower(BaseModel):
    """
    被关注
    """
    class Meta:
        indexes = (
            (('user', 'follower'), True)
        )

    user = ForeignKeyField(User, help_text='用户')
    follower = ForeignKeyField(User, help_text='用户的关注者')
    updated_at = DateTimeField(help_text='抓取时间', default=datetime.datetime.now())


class FollowerHistorical(Follower):
    """
    已经取消的关注
    """
    class Meta:
        table_name = 'follower_historical'

    deleted_at = DateTimeField(help_text='删除时间', default=datetime.datetime.now())


class Following(BaseModel):
    """
    关注
    """
    class Meta:
        indexes = (
            (('user', 'following_user'), True)
        )

    user = ForeignKeyField(User, help_text='用户')
    following_user = ForeignKeyField(User, help_text='用户的关注对象', index=True)
    updated_at = DateTimeField(help_text='抓取时间', default=datetime.datetime.now())


class FollowingHistorical(Following):
    """
    已经取消的关注
    """
    class Meta:
        table_name = 'following_historical'

    deleted_at = DateTimeField(help_text='删除时间', default=datetime.datetime.now())


class Movie(BaseModel):
    """
    电影
    """
    _attrs_to_compare_ = [
        'title',
        'original_title',
        'aka',
        'rating',
        'ratings_count',
        'wish_count',
        'collect_count',
        'do_count',
        'images',
        'subtype',
        'directors',
        'casts',
        'writers',
        'website',
        'douban_site',
        'pubdates',
        'mainland_pubdate',
        'year',
        'languages',
        'durations',
        'genres',
        'countries',
        'summary',
        'comments_count',
        'reviews_count',
        'seasons_count',
        'current_season',
        'current_season',
        'episodes_count',
        'schedule_url',
        'schedule_url',
        'trailer_urls',
        'clip_urls',
        'blooper_urls',
        'photos',
        'popular_reviews',
    ]

    douban_id = CharField(unique=True, help_text='豆瓣ID')
    title = CharField(help_text='中文名')
    original_title = CharField(help_text='原名', null=True)
    aka = CharField(help_text='又名', null=True)
    alt = CharField(help_text='条目页URL', null=True)
    mobile_url = CharField(help_text='移动版条目页URL', null=True)
    rating = CharField(help_text='评分', null=True)
    ratings_count = IntegerField(help_text='评分人数', null=True)
    wish_count = IntegerField(help_text='想看人数', null=True)
    collect_count = IntegerField(help_text='看过人数', null=True)
    do_count = IntegerField(help_text='在看人数', null=True)
    images = CharField(help_text='电影海报图', null=True)
    subtype = CharField(help_text='条目分类', null=True)
    directors = CharField(help_text='导演', null=True)
    casts = CharField(help_text='主演', null=True)
    writers = CharField(help_text='编剧', null=True)
    website = CharField(help_text='官方网站', null=True)
    douban_site = CharField(help_text='豆瓣小站', null=True)
    pubdates = CharField(help_text='上映日期', null=True)
    mainland_pubdate = CharField(help_text='大陆上映日期', null=True)
    year = CharField(help_text='年代', null=True)
    languages = CharField(help_text='语言', null=True)
    durations = CharField(help_text='片长', null=True)
    genres = CharField(help_text='影片类型', null=True)
    countries = CharField(help_text='制片国家/地区', null=True)
    summary = CharField(help_text='简介', null=True)
    comments_count = IntegerField(help_text='短评数量', null=True)
    reviews_count = IntegerField(help_text='影评数量', null=True)
    seasons_count = IntegerField(help_text='总季数', null=True)
    current_season = IntegerField(help_text='当前季数', null=True)
    episodes_count = IntegerField(help_text='当前季的集数', null=True)
    schedule_url = CharField(help_text='影讯页URL', null=True)
    trailer_urls = CharField(help_text='预告片URL', null=True)
    clip_urls = CharField(help_text='片段URL', null=True)
    blooper_urls = CharField(help_text='花絮URL', null=True)
    photos = CharField(help_text='电影剧照', null=True)
    popular_reviews = CharField(help_text='影评', null=True)
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


class Setting(BaseModel):
    """
    配置信息
    """
    name = CharField(unique=True, help_text='名称')
    value = TextField(help_text='值')

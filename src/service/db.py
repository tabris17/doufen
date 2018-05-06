# encoding: utf-8
from peewee import *


__all__ = ['dbo', 'init', 'Account', 'User', 'Setting']

dbo = SqliteDatabase(None)

def init(db_path):
    """
    初始化数据库
    """
    dbo.init(db_path)
    with dbo:
        dbo.create_tables([
            Account,
            User,
            Setting
        ])


class BaseModel(Model):
    class Meta:
        database = dbo


class User(BaseModel):
    """
    用户
    """
    unique_name = IntegerField(unique=True, help_text='豆瓣域名')
    name = CharField(help_text='用户名称')
    created = DateTimeField(help_text='加入时间')
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


class Account(BaseModel):
    """
    豆瓣帐号
    """

    name = CharField(null=True, help_text='帐号显示名称')
    user = ForeignKeyField(model=User, null=True, unique=True, help_text='豆瓣用户')
    session = CharField(help_text='登录会话的Cookie')
    created = TimestampField(help_text='创建时间')
    is_activated = BooleanField(default=False, help_text='是否已激活')
    is_invalid = BooleanField(default=False, help_text='是否失效')


class Setting(BaseModel):
    """
    配置信息
    """
    name = CharField(unique=True, help_text='名称')
    value = TextField(help_text='值')
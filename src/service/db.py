# encoding: utf-8
from peewee import *


__all__ = ['dbo', 'init', 'Account', 'User', 'Setting', 'UserHistorical', 'DATEBASE_PATH']

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
                Setting
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
            if getattr(self, attr) != field_values.get(attr):
                return False
        return True

    @classmethod
    def clone(cls, model, defaults=dict()):
        """
        从另一个模型对象中复制数据
        """
        fields = cls._meta.sorted_field_names
        fields.remove(cls._meta.primary_key.name)
        field_values = {}

        for field_name in fields:
            field_values[field_name] = getattr(model, field_name) if hasattr(model, field_name) else defaults.get(field_name)
        
        return cls.create(**field_values)


class User(BaseModel):
    """
    用户
    """
    _attrs_to_compare_ = [
        'douban_id',
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
    version = IntegerField(help_text='当前版本')
    updated_at = DateTimeField(help_text='抓取时间')


class UserHistorical(User):
    """
    用户历史数据
    """
    class Meta:
        table_name = 'user_historical'
    
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


class Setting(BaseModel):
    """
    配置信息
    """
    name = CharField(unique=True, help_text='名称')
    value = TextField(help_text='值')

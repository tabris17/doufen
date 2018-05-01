# encoding: utf-8
import unqlite
from distutils.version import StrictVersion

import version


def init(dbo):
    """
    初始化数据库
    """
    with dbo:
        try:
            data_verion = dbo['version']
            if StrictVersion(data_verion) < StrictVersion(version.__version__) and \
                not upgrade(dbo, data_verion, version.__version__):
                raise Exception('升级数据库失败')
        except KeyError:
            collections = [
                'accounts',
                'users',
                'user_relationships',
                'books',
                'movies',
                'music',
                'likes',
                'doulists',
                'notes',
                'photos',
                'statuses'
            ]
            with dbo.transaction():
                for collection_name in collections:
                    collection = dbo.collection(collection_name)
                    if not collection.exists():
                        collection.create()
            dbo['version'] = version.__version__
            return dbo


def instance(path):
    """
    获取数据库实例
    """
    return unqlite.UnQLite(path, open_database=False)


def upgrade(dbo, src, dest):
    """
    升级数据库
    """
    return True

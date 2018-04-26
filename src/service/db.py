# encoding: utf-8
import unqlite


def get_instance(path, is_readonly=False):
    """
    获取数据库实例
    """
    return unqlite.UnQLite(path, unqlite.UNQLITE_OPEN_CREATE, False)


def upgrade(db_instance, src_version, dest_version):
    """
    升级数据库
    """
    return True

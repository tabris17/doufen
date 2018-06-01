# encoding: utf-8


class Forbidden(Exception):
    """
    登录会话或IP被屏蔽了
    """
    pass
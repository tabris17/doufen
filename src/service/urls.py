# encoding: utf-8
import handlers
import handlers.accounts

patterns = [
    (r'/', handlers.Main, None, 'index'),
    (r'/help', handlers.Help, None, 'help'),
    (r'/accounts/login', handlers.accounts.Login, None, 'accounts.login'),
    (r'/notify', handlers.Notifier, None, 'notify'),
]

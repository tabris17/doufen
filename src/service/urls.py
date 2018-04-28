# encoding: utf-8
import handlers
import handlers.accounts

patterns = [
    (r'/', handlers.Main, None, 'index'),
    (r'/settings', handlers.Settings, None, 'settings'),
    (r'/manual', handlers.Manual, None, 'manual'),
    (r'/accounts/login', handlers.accounts.Login, None, 'accounts.login'),
    (r'/notify', handlers.Notifier, None, 'notify'),
]

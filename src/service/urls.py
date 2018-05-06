# encoding: utf-8
import handlers
import handlers.settings
import handlers.settings.accounts

patterns = [
    (r'/', handlers.Main, None, 'index'),
    (r'/settings/', handlers.settings.Index, None, 'settings'),
    (r'/settings/accounts/', handlers.settings.accounts.Index, None, 'settings.accounts'),
    (r'/settings/accounts/login', handlers.settings.accounts.Login, None, 'settings.accounts.login'),
    (r'/settings/accounts/add', handlers.settings.accounts.Add, None, 'settings.accounts.add'),
    (r'/manual', handlers.Manual, None, 'manual'),
    (r'/notify', handlers.Notifier, None, 'notify'),
]

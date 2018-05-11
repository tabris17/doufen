# encoding: utf-8
import handlers
import handlers.settings
import handlers.settings.accounts

patterns = [
    (r'/', handlers.Main, None, 'index'),
    (r'/settings/', handlers.settings.General, None, 'settings'),
    (r'/settings/general', handlers.settings.General, None, 'settings.general'),
    (r'/settings/network', handlers.settings.Network, None, 'settings.network'),
    (r'/settings/accounts/', handlers.settings.accounts.Index, None, 'settings.accounts'),
    (r'/settings/accounts/login', handlers.settings.accounts.Login, None, 'settings.accounts.login'),
    (r'/settings/accounts/add', handlers.settings.accounts.Add, None, 'settings.accounts.add'),
    (r'/help/manual', handlers.Manual, None, 'help.manual'),
    (r'/notify', handlers.Notifier, None, 'notify'),
]

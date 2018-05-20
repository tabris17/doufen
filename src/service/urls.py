# encoding: utf-8
import handlers
import handlers.settings
import handlers.settings.accounts
import handlers.dashboard
import handlers.my

patterns = [
    (r'/', handlers.Main, None, 'index'),
    (r'/settings', handlers.settings.General, None, 'settings'),
    (r'/settings/general', handlers.settings.General, None, 'settings.general'),
    (r'/settings/network', handlers.settings.Network, None, 'settings.network'),
    (r'/settings/accounts/', handlers.settings.accounts.Index, None, 'settings.accounts'),
    (r'/settings/accounts/login', handlers.settings.accounts.Login, None, 'settings.accounts.login'),
    (r'/settings/accounts/add', handlers.settings.accounts.Add, None, 'settings.accounts.add'),
    (r'/dashboard', handlers.dashboard.Index, None, 'dashboard'),
    (r'/dashboard/workers/restart', handlers.dashboard.RestartWorkers, None, 'dashboard.workers.restart'),
    (r'/dashboard/tasks/add', handlers.dashboard.AddTask, None, 'dashboard.tasks.add'),
    (r'/help/manual', handlers.Manual, None, 'help.manual'),
    (r'/notify', handlers.Notifier, None, 'notify'),
    (r'/my', handlers.my.Index, None, 'my'),
    (r'/my/following', handlers.my.Following, None, 'my.following'),
    (r'/my/followers', handlers.my.Followers, None, 'my.followers'),
]

# encoding: utf-8
import handlers
import handlers.settings
import handlers.settings.accounts
import handlers.dashboard
import handlers.my


patterns = [
    (r'/', handlers.Main, None, 'index'),
    (r'/attachment/(.+)', handlers.Attachment, None, 'attachment'),
    (r'/settings', handlers.settings.General, None, 'settings'),
    (r'/settings/general', handlers.settings.General, None, 'settings.general'),
    (r'/settings/network', handlers.settings.Network, None, 'settings.network'),
    (r'/settings/accounts/', handlers.settings.accounts.Index, None, 'settings.accounts'),
    (r'/settings/accounts/login', handlers.settings.accounts.Login, None, 'settings.accounts.login'),
    (r'/settings/accounts/add', handlers.settings.accounts.Add, None, 'settings.accounts.add'),
    (r'/settings/accounts/remove', handlers.settings.accounts.Remove, None, 'settings.accounts.remove'),
    (r'/settings/accounts/activate', handlers.settings.accounts.Activate, None, 'settings.accounts.activate'),
    (r'/dashboard', handlers.dashboard.Index, None, 'dashboard'),
    (r'/dashboard/workers/restart', handlers.dashboard.RestartWorkers, None, 'dashboard.workers.restart'),
    (r'/dashboard/tasks/add', handlers.dashboard.AddTask, None, 'dashboard.tasks.add'),
    (r'/help/manual', handlers.Manual, None, 'help.manual'),
    (r'/notify', handlers.Notifier, None, 'notify'),
    (r'/my', handlers.my.Index, None, 'my'),
    (r'/my/following', handlers.my.Following, None, 'my.following'),
    (r'/my/following/historical', handlers.my.FollowingHistorical, None, 'my.following.historical'),
    (r'/my/followers', handlers.my.Followers, None, 'my.followers'),
    (r'/my/followers/historical', handlers.my.FollowersHistorical, None, 'my.followers.historical'),
    (r'/my/blocklist', handlers.my.Blocklist, None, 'my.blocklist'),
    (r'/my/blocklist/historical', handlers.my.BlocklistHistorical, None, 'my.blocklist.historical'),
    (r'/my/book/([^/]+)', handlers.my.Book, None, 'my.book'),
    (r'/my/book/historical', handlers.my.BookHistorical, None, 'my.book.historical'),
    (r'/my/music/([^/]+)', handlers.my.Music, None, 'my.music'),
    (r'/my/music/historical', handlers.my.MusicHistorical, None, 'my.music.historical'),
    (r'/my/movie/([^/]+)', handlers.my.Movie, None, 'my.movie'),
    (r'/my/movie/historical', handlers.my.MovieHistorical, None, 'my.movie.historical'),
    (r'/book/([^/]+)', handlers.Book, None, 'book'),
    (r'/movie/([^/]+)', handlers.Movie, None, 'movie'),
    (r'/music/([^/]+)', handlers.Music, None, 'music'),
    (r'/my/broadcast', handlers.my.Broadcast, None, 'my.broadcast'),
    (r'/broadcast/([^/]+)', handlers.Broadcast, None, 'broadcast'),
    (r'/user/([^/]+)', handlers.User, None, 'user'),
]

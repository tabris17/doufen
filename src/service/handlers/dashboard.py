# encoding: utf-8
import json

from db import Account
from tasks import ALL_TASKS

from .handlers import BaseRequestHandler


class Index(BaseRequestHandler):
    """
    控制台
    """
    def get(self):
        workers = self.server.workers
        pedding_tasks = self.server.tasks
        accounts = Account.select().where(Account.is_invalid == False)

        if not accounts.count():
            self.redirect(self.reverse_url('settings.accounts.login'))
        
        self.render('dashboard.html', workers=workers,
                    pedding_tasks=pedding_tasks, accounts=accounts, all_tasks=ALL_TASKS.keys())


class RestartWorkers(BaseRequestHandler):
    """
    重启工作进程
    """
    def post(self):
        self.server.stop_workers()
        self.server.start_workers()
        self.write('OK')


class AddTask(BaseRequestHandler):
    """
    添加任务
    """
    def post(self):
        tasks = json.loads(self.get_argument('tasks'))
        task_names = tasks['tasks']
        account_ids = tasks['accounts']

        if isinstance(task_names, list) and isinstance(account_ids, list):
            for task_name in task_names:
                task_type = ALL_TASKS.get(task_name)
                for account_id in account_ids:
                    try:
                        account = Account.get(Account.id == account_id)
                        task = task_type(account)
                        self.server.add_task(task)
                    except Account.DoesNotExist:
                        pass
            self.server.push_task()
        self.write('OK')

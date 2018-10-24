# pylint: disable=R0201

from eva.management.common import EvaManagementCommand

from codebase.utils.sqlalchemy import dbc, load_models


class Command(EvaManagementCommand):
    def __init__(self):
        super(Command, self).__init__()

        self.cmd = "syncdb"
        self.help = "同步数据库(如果表不存在，则创建之)"

    def run(self):
        load_models()
        dbc.create_all()

import sys

from eva.management.common import EvaManagementCommand

from codebase.utils.sqlalchemy import dbc, load_models


class Command(EvaManagementCommand):
    def __init__(self):
        super(Command, self).__init__()

        self.cmd = "dropdb"
        self.help = "清空数据库"

    def run(self):

        if not self.args.ignore_env_check:
            print("dropdb 只能在开发/测试环境中使用!")
            sys.exit(1)

        load_models()
        dbc.drop_all()

# pylint: disable=W0223,W0221

from codebase.web import (
    APIRequestHandler,
    HTTPError
)
from codebase.models import (
    User,
    Role
)


class _Base(APIRequestHandler):

    def get_user(self, _id):
        user = self.db.query(User).filter_by(uuid=_id).first()
        if user:
            return user
        raise HTTPError(400, reason="not-found")

    def get_roles(self, role_ids):
        """通过给定的角色ID列表，查询对应的角色对象

        返回：
        1. `roles` : 找到的角色对象列表
        2. `notexist` : 没有找到的角色ID列表
        """
        notexsit = []
        roles = []
        for role_id in role_ids:
            role = self.db.query(Role).filter_by(uuid=role_id).first()
            if role:
                roles.append(role)
            else:
                notexsit.append(role_id)
        return roles, notexsit


class UserRoleHandler(_Base):

    def get(self, _id):
        """获取指定用户的角色列表
        """
        user = self.get_user(_id)
        self.success(data=[role.isimple for role in user.roles])


class UserRoleAppendHandler(_Base):

    def post(self, _id):
        """增加指定用户的角色
        """
        body = self.get_body_json()

        # 首先检查角色ID是否都存在
        roles, notexist = self.get_roles(body["roles"])
        if notexist:
            self.fail(error="have-not-exist", data=notexist)
            return

        # 如果 user 不存在，说明还未记录过，我们这里需要创建新的 User
        user = self.db.query(User).filter_by(uuid=_id).first()
        if not user:
            user = User(uuid=_id)
            self.db.add(user)
            self.db.commit()

        # append roles
        user.roles.extend(roles)
        self.db.commit()
        self.success()


class UserRoleRemoveHandler(_Base):

    def post(self, _id):
        """删除指定用户的角色
        """
        user = self.get_user(_id)
        body = self.get_body_json()

        roles, notexist = self.get_roles(body["roles"])
        if notexist:
            self.fail(error="have-not-exist", data=notexist)
            return

        # remove roles
        for role in roles:
            user.roles.remove(role)
        self.db.commit()
        self.success()

# pylint: disable=W0223,W0221

from codebase.web import (
    APIRequestHandler,
    HTTPError
)
from codebase.models import (
    User,
    Permission
)


class _Base(APIRequestHandler):

    def get_user(self, _id):
        user = self.db.query(User).filter_by(uuid=_id).first()
        if user:
            return user
        raise HTTPError(400, reason="invalid-user")

    def get_permission_by_id(self, _id):
        perm = self.db.query(Permission).filter_by(uuid=_id).first()
        if perm:
            return perm
        raise HTTPError(400, reason="invalid-permission")

    def get_permission_by_name(self, name):
        perm = self.db.query(Permission).filter_by(name=name).first()
        if perm:
            return perm
        raise HTTPError(400, reason="invalid-permission")


class HasPermissionHandler(_Base):
    """检查用户是否拥有某项权限
    """

    def get(self):
        user_id = self.get_query_argument("user_id")
        perm_name = self.get_query_argument("permission_name")
        self.do_has_permission(user_id, perm_name)

    def post(self):
        body = self.get_body_json()
        self.do_has_permission(body["user_id"], body["permission_name"])

    def do_has_permission(self, user_id, perm_name):
        user = self.get_user(user_id)
        perm = self.get_permission_by_name(perm_name)
        if user.has_permission(perm.name):
            self.success(status="yes")
        else:
            self.success(status="no")


class HasPermissionIDHandler(_Base):
    """检查用户是否拥有某项权限（使用权限ID）
    """

    def get(self):
        user_id = self.get_query_argument("user_id")
        perm_id = self.get_query_argument("permission_id")
        self.do_has_permission(user_id, perm_id)

    def post(self):
        body = self.get_body_json()
        self.do_has_permission(body["user_id"], body["permission_id"])

    def do_has_permission(self, user_id, perm_id):
        user = self.get_user(user_id)
        perm = self.get_permission_by_id(perm_id)
        if user.has_permission(perm.name):
            self.success(status="yes")
        else:
            self.success(status="no")

import uuid

from codebase.models import (
    User,
    Permission,
    Role
)
from codebase.utils.swaggerui import api

from .base import (
    BaseTestCase,
    get_body_json
)


class _Base(BaseTestCase):

    rs = api.spec.resources["authz"]

    def setUp(self):
        super().setUp()

        user = User(uuid=str(uuid.uuid4()))
        self.db.add(user)

        role = Role(name="test-role")
        self.db.add(role)
        user.roles.append(role)

        perm = Permission(name="test-permission")
        self.db.add(perm)
        role.permissions.append(perm)
        self.db.commit()

        self.user = user
        self.permission = perm


class HasPermissionGetTestCase(_Base):
    """使用 GET 方法查询用户是否拥有某项权限
    """

    def validate_response_200(self, user_id, permission_name, status):
        resp = self.api_get(
            f"/has_permission?user_id={user_id}"
            f"&permission_name={permission_name}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.assertEqual(body["status"], status)

    def validate_response_400(self, user_id, permission_name, status):
        resp = self.api_get(
            f"/has_permission?user_id={user_id}"
            f"&permission_name={permission_name}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        self.assertEqual(body["status"], status)

    def test_yes(self):
        """GET /has_permission - 检查权限存在
        """
        self.validate_response_200(
            self.user.uuid, self.permission.name, "yes")

    def test_no(self):
        """POST /has_permission - 检查权限不存在
        """
        perm = Permission(name="new-permission")
        self.db.add(perm)
        self.db.commit()

        self.validate_response_200(
            str(self.user.uuid), perm.name, "no")

    def test_user_notexist(self):
        """GET /has_permission - 指定的用户ID不存在
        """
        self.validate_response_400(
            str(uuid.uuid4()), self.permission.name, "invalid-user")

    def test_permission_notexist(self):
        """GET /has_permission - 指定的权限不存在
        """
        self.validate_response_400(
            self.user.uuid, "notexist", "invalid-permission")

    def test_permission_and_user_notexist(self):
        """GET /has_permission - 指定的用户和权限都不存在
        """
        self.validate_response_400(
            str(uuid.uuid4()), "notexist", "invalid-user")


class HasPermissionPostTestCase(_Base):
    """使用 POST 方法查询用户是否拥有某项权限
    """

    def validate_response_200(self, user_id, permission_name, status):
        resp = self.api_post("/has_permission", body={
            "user_id": user_id,
            "permission_name": permission_name})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.assertEqual(body["status"], status)

    def validate_response_400(self, user_id, permission_name, status):
        resp = self.api_post("/has_permission", body={
            "user_id": user_id,
            "permission_name": permission_name})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        self.assertEqual(body["status"], status)

    def test_yes(self):
        """POST /has_permission - 检查权限存在
        """
        self.validate_response_200(
            str(self.user.uuid), self.permission.name, "yes")

    def test_no(self):
        """POST /has_permission - 检查权限不存在
        """
        perm = Permission(name="new-permission")
        self.db.add(perm)
        self.db.commit()

        self.validate_response_200(
            str(self.user.uuid), perm.name, "no")

    def test_user_notexist(self):
        """GET /has_permission - 指定的用户ID不存在
        """
        self.validate_response_400(
            str(uuid.uuid4()), self.permission.name, "invalid-user")

    def test_permission_notexist(self):
        """GET /has_permission - 指定的权限不存在
        """
        self.validate_response_400(
            str(self.user.uuid), "notexist", "invalid-permission")

    def test_permission_and_user_notexist(self):
        """GET /has_permission - 指定的用户和权限都不存在
        """
        self.validate_response_400(
            str(uuid.uuid4()), "notexist", "invalid-user")


class HasPermissionIDGetTestCase(_Base):
    """使用 GET 方法查询用户是否拥有某项权限（使用权限ID）
    """

    def test_success(self):
        """GET /has_permission_id - 检查权限存在
        """

        user_id = str(self.user.uuid)
        perm_id = str(self.permission.uuid)
        resp = self.api_get(
            f"/has_permission_id?user_id={user_id}"
            f"&permission_id={perm_id}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.assertEqual(body["status"], "yes")

    def test_permission_notexist(self):
        """GET /has_permission_id - 指定的权限ID不存在
        """

        perm_id = str(uuid.uuid4())
        resp = self.api_get(
            f"/has_permission_id?user_id={self.user.uuid}"
            f"&permission_id={perm_id}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        self.assertEqual(body["status"], "invalid-permission")


class HasPermissionIDPostTestCase(_Base):
    """使用 POST 方法查询用户是否拥有某项权限（使用权限ID）
    """

    def test_success(self):
        """POST /has_permission_id - 检查权限存在
        """

        user_id = str(self.user.uuid)
        perm_id = str(self.permission.uuid)
        resp = self.api_post("/has_permission_id", body={
            "user_id": user_id,
            "permission_id": perm_id})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.assertEqual(body["status"], "yes")

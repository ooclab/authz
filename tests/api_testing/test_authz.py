import uuid

from eva.conf import settings

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

    def shortDescription(self):
        class_doc = self.__doc__
        doc = self._testMethodDoc
        first = class_doc.split("\n")[0].strip() if class_doc else None
        second = doc.split("\n")[0].strip() if doc else None
        return f"{self.method.upper(): <6} {first} : {second}"

    def validate_response_200(self, user_id, permission, status):
        resp = self.has_permission_request(user_id, permission)
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.assertEqual(body["status"], status)

    def validate_response_400(self, user_id, permission, status):
        resp = self.has_permission_request(user_id, permission)
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        self.assertEqual(body["status"], status)


def has_permission_class_factory(name, method):

    class _BaseHasPermission(_Base):
        """GET|POST /has_permission - 鉴权（使用权限名称）
        """

        def has_permission_request(self, user_id, permission_name):
            if self.method == "GET":
                return self.api_get(
                    f"/has_permission?user_id={user_id}"
                    f"&permission_name={permission_name}")

            return self.api_post("/has_permission", body={
                "user_id": user_id,
                "permission_name": permission_name})

        def test_yes(self):
            """检查权限存在
            """
            self.validate_response_200(
                str(self.user.uuid), self.permission.name, "yes")

        def test_admin_yes(self):
            """检查超级用户权限存在
            """
            perm = Permission(name="new-permission")
            self.db.add(perm)
            role = Role(name=settings.ADMIN_ROLE_NAME)
            self.user.roles.append(role)
            self.db.commit()

            self.validate_response_200(
                str(self.user.uuid), perm.name, "yes")

        def test_no(self):
            """检查权限不存在
            """
            perm = Permission(name="new-permission")
            self.db.add(perm)
            self.db.commit()

            self.validate_response_200(
                str(self.user.uuid), perm.name, "no")

        def test_user_notexist(self):
            """指定的用户ID不存在
            """
            self.validate_response_400(
                str(uuid.uuid4()), self.permission.name, "invalid-user")

        def test_permission_notexist(self):
            """指定的权限不存在
            """
            self.validate_response_400(
                str(self.user.uuid), "notexist", "invalid-permission")

        def test_permission_and_user_notexist(self):
            """指定的用户和权限都不存在
            """
            self.validate_response_400(
                str(uuid.uuid4()), "notexist", "invalid-user")

    def __init__(self, *args, **kwargs):
        _BaseHasPermission.__init__(self, *args, **kwargs)
        setattr(_BaseHasPermission, "method", method)
    newclass = type(name, (_BaseHasPermission,), {"__init__": __init__})
    newclass.__doc__ = "/has_permission - 鉴权（使用权限名称）"
    return newclass


HasPermissionGetTestCase = has_permission_class_factory(
    "HasPermissionGetTestCase", "GET")
HasPermissionPostTestCase = has_permission_class_factory(
    "HasPermissionPostTestCase", "POST")


def has_permission_id_class_factory(name, method):

    class _BaseHasPermission(_Base):

        def has_permission_request(self, user_id, permission_id):
            if self.method == "GET":
                return self.api_get(
                    f"/has_permission_id?user_id={user_id}"
                    f"&permission_id={permission_id}")

            return self.api_post("/has_permission_id", body={
                "user_id": user_id,
                "permission_id": permission_id})

        def test_yes(self):
            """检查权限存在
            """
            self.validate_response_200(
                str(self.user.uuid), str(self.permission.uuid), "yes")

        def test_admin_yes(self):
            """检查超级用户权限存在
            """
            perm = Permission(name="new-permission")
            self.db.add(perm)
            role = Role(name=settings.ADMIN_ROLE_NAME)
            self.user.roles.append(role)
            self.db.commit()

            self.validate_response_200(
                str(self.user.uuid), str(perm.uuid), "yes")

        def test_no(self):
            """检查权限不存在
            """
            perm = Permission(name="new-permission")
            self.db.add(perm)
            self.db.commit()

            self.validate_response_200(
                str(self.user.uuid), str(perm.uuid), "no")

        def test_user_notexist(self):
            """指定的用户ID不存在
            """
            self.validate_response_400(
                str(uuid.uuid4()), str(self.permission.uuid), "invalid-user")

        def test_permission_notexist(self):
            """指定的权限不存在
            """
            self.validate_response_400(
                str(self.user.uuid), str(uuid.uuid4()), "invalid-permission")

        def test_permission_and_user_notexist(self):
            """指定的用户和权限都不存在
            """
            self.validate_response_400(
                str(uuid.uuid4()), str(uuid.uuid4()), "invalid-user")

    def __init__(self, *args, **kwargs):
        _BaseHasPermission.__init__(self, *args, **kwargs)
        setattr(_BaseHasPermission, "method", method)
    newclass = type(name, (_BaseHasPermission,), {"__init__": __init__})
    newclass.__doc__ = "/has_permission_id - 鉴权（使用权限ID）"
    return newclass


HasPermissionIDGetTestCase = has_permission_id_class_factory(
    "HasPermissionIDGetTestCase", "GET")
HasPermissionIDPostTestCase = has_permission_id_class_factory(
    "HasPermissionIDPostTestCase", "POST")

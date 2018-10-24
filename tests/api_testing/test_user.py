import uuid

from codebase.models import (
    Role,
    User
)
from codebase.utils.swaggerui import api

from .base import (
    BaseTestCase,
    get_body_json
)


class _BaseTestCase(BaseTestCase):

    rs = api.spec.resources["user"]


class UserRoleListTestCase(_BaseTestCase):

    def test_success(self):
        """GET /user/{id}/role - 查看用户的角色列表正确
        """

        user = User(uuid=str(uuid.uuid4()))
        self.db.add(user)

        total = 10
        user_role_total = 5
        basename = "myrole"
        for i in range(total):
            role = Role(name=basename + str(i))
            self.db.add(role)
            if i < user_role_total:
                user.roles.append(role)
        self.db.commit()

        resp = self.api_get(f"/user/{user.uuid}/role")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        s = self.rs.get_user_id_role.op_spec["responses"]["200"]["schema"]
        api.validate_object(s, body)

        self.assertEqual(
            [basename + str(i) for i in range(user_role_total)],
            sorted([role["name"] for role in body["data"]]))


class UserRoleAppendTestCase(_BaseTestCase):
    """POST /user/{id}/role/append - 增加指定用户的角色
    """

    def append_roles(self, user_id):
        roles = []
        role_total = 12
        role_basename = "testrole"
        for i in range(role_total):
            role = Role(name=role_basename + str(i))
            self.db.add(role)
            self.db.commit()
            roles.append(str(role.uuid))

        resp = self.api_post(f"/user/{user_id}/role/append", body={
            "roles": roles})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        user = self.db.query(User).filter_by(uuid=user_id).one()
        self.assertEqual(
            sorted([role_basename+str(i) for i in range(role_total)]),
            sorted([role.name for role in user.roles]))

    def test_user_notexist(self):
        """POST /user/{id}/role/append - 使用不存在的用户ID
        """
        self.append_roles(str(uuid.uuid4()))

    def test_user_exist(self):
        """POST /user/{id}/role/append - 使用存在的用户ID
        """

        user = User(uuid=str(uuid.uuid4()))
        self.db.add(user)
        self.db.commit()
        self.append_roles(str(user.uuid))

    def test_notexist_roles(self):
        """POST /user/{id}/role/append - 使用不存在的角色ID
        """
        user_id = str(uuid.uuid4())
        notexist_total = 12
        resp = self.api_post(f"/user/{user_id}/role/append", body={
            "roles": [str(uuid.uuid4()) for i in range(notexist_total)],
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)

        s = self.rs.post_user_id_role_append.op_spec[
            "responses"]["default"]["schema"]
        api.validate_object(s, body)

        self.assertEqual(body["status"], "have-not-exist")
        self.assertEqual(len(body["data"]), notexist_total)


class UserRoleRemoveTestCase(_BaseTestCase):
    """POST /user/{id}/role/remove - 删除指定用户的角色
    """

    def test_not_found(self):
        """POST /user/{id}/role/remove - 使用不存在的用户ID
        """
        user_id = str(uuid.uuid4())
        resp = self.api_post(f"/user/{user_id}/role/remove")
        self.validate_not_found(resp)

    def test_remove_success(self):
        """POST /user/{id}/role/remove - 删除用户的角色成功
        """
        user = User(uuid=str(uuid.uuid4()))
        self.db.add(user)
        self.db.commit()

        remove_role_total = 3
        remove_role_list = []
        role_total = 12
        role_basename = "test-role"
        for i in range(role_total):
            role = Role(name=role_basename + str(i))
            self.db.add(role)
            user.roles.append(role)
            self.db.commit()
            if i < remove_role_total:
                remove_role_list.append(str(role.uuid))

        user_id = user.uuid
        del user

        resp = self.api_post(f"/user/{user_id}/role/remove", body={
            "roles": remove_role_list,
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        user = self.db.query(User).filter_by(uuid=user_id).one()
        self.assertEqual(
            len(user.roles),
            role_total - remove_role_total
        )

    def test_notexist_roles(self):
        """POST /user/{id}/role/remove - 使用不存在的角色ID
        """
        user_id = str(uuid.uuid4())
        user = User(uuid=user_id)
        self.db.add(user)
        self.db.commit()

        notexist_total = 12
        resp = self.api_post(f"/user/{user_id}/role/remove", body={
            "roles": [str(uuid.uuid4()) for i in range(notexist_total)],
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)

        s = self.rs.post_user_id_role_remove.op_spec[
            "responses"]["default"]["schema"]
        api.validate_object(s, body)

        self.assertEqual(body["status"], "have-not-exist")
        self.assertEqual(len(body["data"]), notexist_total)

import uuid

from eva.utils.time_ import utc_rfc3339_string

from codebase.models import (
    User,
    Permission,
    Role
)
from codebase.utils.sqlalchemy import dbc
from codebase.utils.swaggerui import api

from .base import (
    BaseTestCase,
    validate_default_error,
    get_body_json
)


class _Base(BaseTestCase):

    rs = api.spec.resources["permission"]


class MyPermissionListTestCase(_Base):
    """GET    /my/permission - 查看我的权限
    """

    def test_success(self):
        """返回正确
        """
        role_numbers = 10
        perm_numbers = 20
        role_basename = "myrole"
        permission_basename = "myperm"
        for i in range(role_numbers):
            role = Role(name=role_basename + str(i))
            for j in range(perm_numbers):
                perm = Permission(name=permission_basename + str(i) + str(j))
                self.db.add(perm)
                role.permissions.append(perm)
            self.db.add(role)
            self.current_user.roles.append(role)
        self.db.commit()

        resp = self.api_get("/my/permission")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_my_permission.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        self.assertEqual(len(body["data"]), role_numbers)
        for role_data in body["data"]:
            self.assertEqual(len(role_data["permissions"]), perm_numbers)

        role_names = [role_data["name"] for role_data in body["data"]]
        self.assertEqual(
            [role_basename + str(i) for i in range(role_numbers)],
            sorted(role_names))


class PermissionListTestCase(_Base):
    """GET    /permission - 获取权限列表
    """

    def setUp(self):
        super().setUp()
        total = 3
        basename = "fortest"
        for _ in range(total):
            user = User(uuid=str(uuid.uuid4()))
            self.db.add(user)
            self.db.commit()

            for i in range(total):
                role = Role(name=str(user.id) + basename + str(i))
                self.db.add(role)
                user.roles.append(role)
                self.db.commit()

                for j in range(total):
                    perm = Permission(
                        name=str(user.id) + basename + str(i) + str(j))
                    self.db.add(perm)
                    role.permissions.append(perm)
                self.db.commit()
        self.total = total * total * total

    def test_list_success(self):
        """返回正确
        """
        resp = self.api_get("/permission")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_permission.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        self.assertEqual(len(body["data"]), body["filter"]["page_size"])
        self.assertEqual(body["filter"]["total"], self.total)

    def test_no_such_page(self):
        """查无此页
        """
        for page in [-10, 10]:
            resp = self.api_get(f"/permission?page={page}")
            body = get_body_json(resp)
            self.assertEqual(resp.code, 400)
            validate_default_error(body)
            self.assertEqual(body["status"], f"no-such-page:{page}")


class PermissionCreateTestCase(_Base):
    """POST   /permission - 创建权限
    """

    def test_name_exist(self):
        """名字已经存在
        """
        name = "my-permission"
        perm = Permission(name=name)
        self.db.add(perm)
        self.db.commit()

        resp = self.api_post("/permission", body={"name": name})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "name-exist")

    def test_create_success(self):
        """创建成功
        """
        name = "my-permission"
        resp = self.api_post("/permission", body={
            "name": name,
            "summary": "my summary",
            "description": "my description",
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        perm = self.db.query(Permission).filter_by(name=name).one()
        self.assertEqual(str(perm.uuid), body["id"])


class PermissionViewTestCase(_Base):
    """GET    /permission/{id} - 查看指定权限详情
    """

    def test_not_found(self):
        """权限ID不存在
        """

        perm_id = str(uuid.uuid4())
        resp = self.api_get(f"/permission/{perm_id}")
        self.validate_not_found(resp)

    def test_get_success(self):
        """获取详情正确
        """
        name = "my-permission"
        summary = "my summary"
        perm = Permission(name=name, summary=summary)
        self.db.add(perm)
        self.db.commit()

        resp = self.api_get(f"/permission/{perm.uuid}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_permission_id.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        data = body["data"]
        self.assertEqual(data["summary"], summary)
        self.assertEqual(data["created"], utc_rfc3339_string(perm.created))
        self.assertEqual(data["updated"], utc_rfc3339_string(perm.updated))


class PermissionUpdateTestCase(_Base):
    """POST   /permission/{id} - 更新权限属性
    """

    def test_not_found(self):
        """权限不存在
        """

        perm_id = str(uuid.uuid4())
        resp = self.api_post(f"/permission/{perm_id}")
        self.validate_not_found(resp)

    def test_update_success(self):
        """更新成功
        """
        name = "my-permission"
        summary = "my summary"
        description = "my description"

        perm = Permission(name=name, summary=summary, description=description)
        self.db.add(perm)
        self.db.commit()
        old_updated = perm.updated
        perm_id = str(perm.uuid)
        del perm

        resp = self.api_post(f"/permission/{perm_id}", body={
            "summary": summary + ":new",
            "description": description + ":new"})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        perm = self.db.query(Permission).filter_by(uuid=perm_id).one()
        self.assertEqual(perm.summary, summary + ":new")
        self.assertEqual(perm.description, description + ":new")
        self.assertNotEqual(perm.updated, old_updated)


class PermissionDeleteTestCase(_Base):
    """DELETE /permission/{id} - 删除权限
    """

    def test_not_found(self):
        """权限不存在
        """
        perm_id = str(uuid.uuid4())
        resp = self.api_delete(f"/permission/{perm_id}")
        self.validate_not_found(resp)

    def test_delete_success(self):
        """删除成功
        """
        role_name = "my-role"
        role = Role(name=role_name)
        self.db.add(role)

        perm_name = "my-permission"
        perm = Permission(name=perm_name)
        perm.roles.append(role)
        self.db.add(perm)

        self.db.commit()

        resp = self.api_delete(f"/permission/{perm.uuid}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        dbc.remove()

        perm = self.db.query(Permission).filter_by(name=perm_name).first()
        self.assertIs(perm, None)

        role = self.db.query(Role).filter_by(name=role_name).one()
        self.assertNotIn(perm_name, [p.name for p in role.permissions])

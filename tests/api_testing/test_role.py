import uuid

from eva.utils.time_ import utc_rfc3339_string

from codebase.models import Permission, Role, User
from codebase.utils.sqlalchemy import dbc
from codebase.utils.swaggerui import api

from .base import (
    BaseTestCase,
    validate_default_error,
    get_body_json
)


class RoleBaseTestCase(BaseTestCase):

    rs = api.spec.resources["role"]


class MyRoleListTestCase(RoleBaseTestCase):
    """GET    /my/role - 查看我的角色列表
    """

    def test_success(self):
        """正确
        """
        numbers = 10
        basename = "myrole"
        for i in range(numbers):
            role = Role(name=basename + str(i))
            self.db.add(role)
            self.current_user.roles.append(role)
        self.db.commit()

        resp = self.api_get("/my/role")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_my_role.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        names = [role["name"] for role in body["data"]]
        self.assertEqual([basename + str(i)
                          for i in range(numbers)], sorted(names))


class RoleListTestCase(RoleBaseTestCase):
    """GET    /role - 查看所有角色列表
    """

    def setUp(self):
        super().setUp()

        total = 5
        basename = "fortest"
        for _ in range(total):
            user = User(uuid=str(uuid.uuid4()))
            self.db.add(user)
            self.db.commit()

            for j in range(total):
                role = Role(name=str(user.id) + basename + str(j))
                self.db.add(role)
                user.roles.append(role)
            self.db.commit()

        self.total = total * total

    def test_list_success(self):
        """正确
        """
        resp = self.api_get("/role")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_role.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        self.assertEqual(len(body["data"]), body["filter"]["page_size"])
        self.assertEqual(body["filter"]["total"], self.total)

    def test_no_such_page(self):
        """查无此页
        """
        for page in [-10, 10]:
            resp = self.api_get(f"/role?page={page}")
            body = get_body_json(resp)
            self.assertEqual(resp.code, 400)
            validate_default_error(body)
            self.assertEqual(body["status"], f"no-such-page:{page}")

    def test_unknown_sort(self):
        """错误过滤
        """
        for sort_by in ["updated", "summary"]:
            resp = self.api_get(f"/role?sort_by={sort_by}")
            body = get_body_json(resp)
            self.assertEqual(resp.code, 400)
            validate_default_error(body)
            self.assertEqual(body["status"], f"unknown-sort-by:{sort_by}")


class RoleCreateTestCase(RoleBaseTestCase):
    """POST   /role - 创建角色
    """

    def test_name_exist(self):
        """使用重复的名称
        """

        role_name = "my-role"
        role = Role(name=role_name)
        self.db.add(role)
        self.db.commit()

        resp = self.api_post("/role", body={"name": role_name})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "name-exist")

    def test_create_success(self):
        """创建成功
        """
        role_name = "my-role"
        resp = self.api_post("/role", body={
            "name": role_name,
            "summary": "my summary",
            "description": "my description",
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        role = self.db.query(Role).filter_by(name=role_name).first()
        self.assertIsNot(role, None)
        self.assertEqual(str(role.uuid), body["id"])


class SingleRoleViewTestCase(RoleBaseTestCase):
    """GET    /role/{id} - 查看指定的角色详情
    """

    def test_not_found(self):
        """角色ID不存在
        """

        role_id = str(uuid.uuid4())
        resp = self.api_get(f"/role/{role_id}")
        self.validate_not_found(resp)

    def test_get_success(self):
        """正确
        """
        role_name = "my-role"
        role_summary = "my summary"
        role = Role(name=role_name, summary=role_summary)
        self.db.add(role)
        self.db.commit()

        resp = self.api_get(f"/role/{role.uuid}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_role_id.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        data = body["data"]
        self.assertEqual(data["summary"], role_summary)
        self.assertEqual(data["created"], utc_rfc3339_string(role.created))
        self.assertEqual(data["updated"], utc_rfc3339_string(role.updated))


class RoleUpdateTestCase(RoleBaseTestCase):
    """POST   /role/{id} - 更新角色属性
    """

    def test_not_found(self):
        """角色ID不存在
        """
        role_id = str(uuid.uuid4())
        resp = self.api_post(f"/role/{role_id}")
        self.validate_not_found(resp)

    def test_update_success(self):
        """更新成功
        """

        name = "my-role"
        summary = "my summary"
        description = "my description"

        role = Role(name=name, summary=summary, description=description)
        self.db.add(role)
        self.db.commit()
        old_updated = role.updated
        role_id = str(role.uuid)
        del role

        resp = self.api_post(f"/role/{role_id}", body={
            "summary": summary + ":new",
            "description": description + ":new"})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        role = self.db.query(Role).filter_by(uuid=role_id).one()
        self.assertEqual(role.summary, summary + ":new")
        self.assertEqual(role.description, description + ":new")
        self.assertNotEqual(old_updated, role.updated)


class RoleDeleteTestCase(RoleBaseTestCase):
    """DELETE /role/{id} - 删除角色
    """

    def test_not_found(self):
        """角色ID不存在
        """
        role_id = str(uuid.uuid4())
        resp = self.api_delete(f"/role/{role_id}")
        self.validate_not_found(resp)

    def test_delete_success(self):
        """删除成功
        """
        user_id = self.current_user.id

        role_name = "my-role"
        role = Role(name=role_name)
        role.users.append(self.current_user)
        perm = Permission(name="my-permission")
        self.db.add(perm)
        role.permissions.append(perm)
        self.db.add(role)
        self.db.commit()

        role_id = str(role.uuid)
        resp = self.api_delete(f"/role/{role_id}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        dbc.remove()

        role = self.db.query(Role).filter_by(uuid=role_id).first()
        self.assertIs(role, None)

        user = self.db.query(User).get(user_id)
        self.assertNotIn(role_name, [r.name for r in user.roles])


class RolePermissionListTestCase(RoleBaseTestCase):
    """GET    /role/{id}/permission - 获取指定角色的权限列表
    """

    def test_not_found(self):
        """使用不存在的角色ID
        """
        role_id = str(uuid.uuid4())
        resp = self.api_get(f"/role/{role_id}/permission")
        self.validate_not_found(resp)

    def test_get_success(self):
        """正确
        """
        role_name = "my-role"
        role = Role(name=role_name)
        self.db.add(role)

        permission_total = 12
        permission_basename = "my-permission"
        for i in range(permission_total):
            perm = Permission(name=permission_basename + str(i))
            self.db.add(perm)
            role.permissions.append(perm)

        self.db.commit()

        resp = self.api_get(f"/role/{role.uuid}/permission")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_role_id_permission.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        self.assertEqual(len(body["data"]), permission_total)


class RolePermissionAppendTestCase(RoleBaseTestCase):
    """POST   /role/{id}/permission/append - 增加指定角色的权限
    """

    def test_not_found(self):
        """使用不存在的角色ID
        """
        role_id = str(uuid.uuid4())
        resp = self.api_post(f"/role/{role_id}/permission/append")
        self.validate_not_found(resp)

    def test_post_success(self):
        """增加权限成功
        """
        role_name = "my-role"
        role = Role(name=role_name)
        self.db.add(role)

        permission_total = 12
        permission_basename = "my-permission"
        for i in range(permission_total):
            perm = Permission(name=permission_basename + str(i))
            self.db.add(perm)
            role.permissions.append(perm)

        self.db.commit()

        append_permission_total = 12
        append_permission_basename = "append-permission"
        append_permission_list = []
        for i in range(append_permission_total):
            perm = Permission(name=append_permission_basename + str(i))
            self.db.add(perm)
            self.db.commit()
            append_permission_list.append(str(perm.uuid))

        resp = self.api_post(f"/role/{role.uuid}/permission/append", body={
            "permissions": append_permission_list,
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        role = self.db.query(Role).filter_by(name=role_name).one()
        self.assertEqual(
            len(role.permissions),
            permission_total + append_permission_total
        )

    def test_notexist_permissions(self):
        """使用不存在的权限ID
        """
        role_name = "my-role"
        role = Role(name=role_name)
        self.db.add(role)
        self.db.commit()

        notexist_total = 12
        resp = self.api_post(f"/role/{role.uuid}/permission/append", body={
            "permissions": [str(uuid.uuid4()) for i in range(notexist_total)],
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)

        spec = self.rs.post_role_id_permission_append.op_spec[
            "responses"]["default"]["schema"]
        api.validate_object(spec, body)

        self.assertEqual(body["status"], "have-not-exist")
        self.assertEqual(len(body["data"]), notexist_total)


class RolePermissionRemoveTestCase(RoleBaseTestCase):
    """POST   /role/{id}/permission/remove - 删除指定角色的权限
    """

    def test_not_found(self):
        """使用不存在的角色ID
        """
        role_id = str(uuid.uuid4())
        resp = self.api_post(f"/role/{role_id}/permission/remove")
        self.validate_not_found(resp)

    def test_post_success(self):
        """删除权限成功
        """
        role_name = "my-role"
        role = Role(name=role_name)
        self.db.add(role)

        remove_permission_total = 3
        remove_permission_list = []
        permission_total = 12
        permission_basename = "my-permission"
        for i in range(permission_total):
            perm = Permission(name=permission_basename + str(i))
            self.db.add(perm)
            role.permissions.append(perm)
            self.db.commit()
            if i < remove_permission_total:
                remove_permission_list.append(str(perm.uuid))

        resp = self.api_post(f"/role/{role.uuid}/permission/remove", body={
            "permissions": remove_permission_list,
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        role = self.db.query(Role).filter_by(name=role_name).one()
        self.assertEqual(
            len(role.permissions),
            permission_total - remove_permission_total
        )

    def test_notexist_permissions(self):
        """使用不存在的权限ID
        """
        role_name = "my-role"
        role = Role(name=role_name)
        self.db.add(role)
        self.db.commit()

        notexist_total = 12
        resp = self.api_post(f"/role/{role.uuid}/permission/remove", body={
            "permissions": [str(uuid.uuid4()) for i in range(notexist_total)],
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)

        spec = self.rs.post_role_id_permission_remove.op_spec[
            "responses"]["default"]["schema"]
        api.validate_object(spec, body)

        self.assertEqual(body["status"], "have-not-exist")
        self.assertEqual(len(body["data"]), notexist_total)


class RoleIDByNameTestCase(RoleBaseTestCase):
    """GET    /role/id - 通过角色名查看ID
    """

    def test_not_found(self):
        """角色名不存在
        """

        resp = self.api_get(f"/role/id?name=notexist")
        self.validate_not_found(resp)

    def test_get_success(self):
        """正确
        """
        role_name = "my-role"
        role_summary = "my summary"
        role = Role(name=role_name, summary=role_summary)
        self.db.add(role)
        self.db.commit()

        resp = self.api_get(f"/role/id?name={role.name}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_role_id.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        self.assertEqual(body["id"], str(role.uuid))

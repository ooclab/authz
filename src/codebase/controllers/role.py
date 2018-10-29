# pylint: disable=W0223,W0221,broad-except

import logging
from hashlib import md5

from tornado.web import HTTPError
from tornado.httpclient import AsyncHTTPClient
from eva.conf import settings

from codebase.web import (
    APIRequestHandler,
    authenticated
)
from codebase.models import (
    Permission,
    Role
)
from codebase.utils.sqlalchemy.page import get_list


def compute_checksum(v):
    if not isinstance(v, bytes):
        v = v.encode("utf8")
    return md5(bytes(v)).hexdigest()


def get_permission_role_key(role, permission):
    perm_checksum = compute_checksum(permission.name)
    role_checksum = compute_checksum(role.name)
    return f"/auth/permission/{perm_checksum}/role/{role_checksum}"


class MyRoleHandler(APIRequestHandler):

    @authenticated
    def get(self):
        """获取我的角色列表
        """
        self.success(**{"data": [x.isimple for x in self.current_user.roles]})


class RoleHandler(APIRequestHandler):

    def get(self):
        """获取角色列表
        """
        err, result, _filter = get_list(
            self,
            self.db.query(Role),
            allow_sort_by=["id", "created", "name"],
            model=Role,
        )
        if err:
            self.fail(err)
            return

        self.success(**{"data": [x.isimple for x in result], "filter": _filter})

    def post(self):
        """创建角色
        """
        body = self.get_body_json()

        role = self.db.query(Role).filter_by(name=body["name"]).first()
        if role:
            self.fail("name-exist")
            return

        role = Role(
            name=body["name"],
            summary=body.get("summary"),
            description=body.get("description"),
        )
        self.db.add(role)
        self.db.commit()
        self.success(id=str(role.uuid))


class _BaseSingleRoleHandler(APIRequestHandler):

    def get_role(self, _id):
        role = self.db.query(Role).filter_by(uuid=_id).first()
        if role:
            return role
        raise HTTPError(400, reason="not-found")

    def get_permissions(self, perm_ids):
        """通过给定的权限ID列表，查询对应的权限对象

        返回：
        1. `perms` : 找到的权限对象列表
        2. `notexist` : 没有找到的权限ID列表
        """
        notexsit = []
        perms = []
        for perm_id in perm_ids:
            perm = self.db.query(Permission).filter_by(uuid=perm_id).first()
            if perm:
                perms.append(perm)
            else:
                notexsit.append(perm_id)
        return perms, notexsit


class SingleRoleHandler(_BaseSingleRoleHandler):

    def get(self, _id):
        """获取角色详情
        """
        role = self.get_role(_id)
        self.success(data=role.ifull)

    def post(self, _id):
        """更新角色属性
        """
        role = self.get_role(_id)
        body = self.get_body_json()
        role.update(**body)
        self.db.commit()
        self.success()

    def delete(self, _id):
        """删除角色
        """
        role = self.get_role(_id)
        # TODO: how to rollback ?
        self._remove_role(role)
        self.success()

    def _remove_role(self, role):
        # 删除 User 依赖
        # role.users = []

        # 删除 Permission 依赖
        # TODO: 是否需要删除没有任何 Role 关联的 Permission ?
        role.permissions = []

        # 删除自身
        self.db.delete(role)

        self.db.commit()


class RolePermissionHandler(_BaseSingleRoleHandler):

    def get(self, _id):
        """获取指定角色的权限列表
        """
        role = self.get_role(_id)
        self.success(data=[p.isimple for p in role.permissions])


class RolePermissionAppendHandler(_BaseSingleRoleHandler):

    async def post(self, _id):
        """增加指定角色的权限
        """
        role = self.get_role(_id)
        body = self.get_body_json()

        perms, notexist = self.get_permissions(body["permissions"])
        if notexist:
            self.fail(error="have-not-exist", data=notexist)
            return

        # sync to etcd
        if settings.SYCN_ETCD:
            for perm in perms:
                key = get_permission_role_key(role, perm)
                url = settings.ETCD_URL_ENDPOINT + key
                http_client = AsyncHTTPClient()
                try:
                    await http_client.fetch(url, method="PUT", body=role.name)
                except Exception as e:
                    logging.error("add permission to role at etcd error: %s", e)

        # append permissions
        role.permissions.extend(perms)
        self.db.commit()
        self.success()


class RolePermissionRemoveHandler(_BaseSingleRoleHandler):

    async def post(self, _id):
        """删除指定角色的权限
        """
        role = self.get_role(_id)
        body = self.get_body_json()

        perms, notexist = self.get_permissions(body["permissions"])
        if notexist:
            self.fail(error="have-not-exist", data=notexist)
            return

        # sync to etcd
        if settings.SYCN_ETCD:
            for perm in perms:
                key = get_permission_role_key(role, perm)
                url = settings.ETCD_URL_ENDPOINT + key
                http_client = AsyncHTTPClient()
                try:
                    # FIXME: handle error
                    await http_client.fetch(url, method="DELETE", raise_error=False)
                except Exception as e:
                    logging.error("delete permission from role at etcd error: %s", e)

        # remove permissions
        for perm in perms:
            role.permissions.remove(perm)
        self.db.commit()
        self.success()


class RoleIDByNameHandler(APIRequestHandler):

    def get(self):
        name = self.get_query_argument("name")
        role = self.db.query(Role).filter_by(name=name).first()
        if not role:
            self.fail("not-found")
            return

        self.success(id=str(role.uuid))

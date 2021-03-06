# pylint: disable=W0221,W0223,broad-except

from tornado.web import HTTPError

from codebase.web import (
    APIRequestHandler,
    authenticated
)
from codebase.models import Permission
from codebase.utils.sqlalchemy.page import get_list


class MyPermissionHandler(APIRequestHandler):

    @authenticated
    def get(self):
        """获取我的权限列表
        """
        self.success(
            **{
                "data": [
                    {
                        "id": str(role.uuid),
                        "name": role.name,
                        "summary": role.summary,
                        "permissions": [p.isimple for p in role.permissions],
                    }
                    for role in self.current_user.roles
                ]
            }
        )


class PermissionHandler(APIRequestHandler):

    def get(self):
        """获取权限列表
        """
        error, result, _filter = get_list(
            self,
            self.db.query(Permission),
            allow_sort_by=["id", "created", "name"],
            model=Permission,
        )
        if error:
            self.fail(error)
            return

        self.success(**{"data": [x.isimple for x in result], "filter": _filter})

    def post(self):
        """创建权限
        """
        body = self.get_body_json()

        perm = self.db.query(Permission).filter_by(name=body["name"]).first()
        if perm:
            self.fail("name-exist")
            return

        perm = Permission(
            name=body["name"],
            summary=body.get("summary"),
            description=body.get("description"),
        )
        self.db.add(perm)
        self.db.commit()
        self.success(id=str(perm.uuid))


class _BaseSinglePermissionHandler(APIRequestHandler):

    def get_permission(self, _id):
        perm = self.db.query(Permission).filter_by(uuid=_id).first()
        if perm:
            return perm
        raise HTTPError(400, reason="not-found")


class SinglePermissionHandler(_BaseSinglePermissionHandler):

    def get(self, _id):
        """获取权限详情
        """
        perm = self.get_permission(_id)
        self.success(data=perm.ifull)

    def post(self, _id):
        """更新权限属性
        """
        perm = self.get_permission(_id)
        body = self.get_body_json()
        perm.update(**body)
        self.db.commit()
        self.success()

    def delete(self, _id):
        """删除权限
        """
        perm = self.get_permission(_id)
        # TODO: how to rollback ?
        self._remove_permission(perm)
        self.success()

    def _remove_permission(self, perm):
        # 删除 Role 依赖
        perm.roles = []

        # 删除自身
        self.db.delete(perm)

        self.db.commit()


class PermissionIDByNameHandler(APIRequestHandler):

    def get(self):
        name = self.get_query_argument("name")
        perm = self.db.query(Permission).filter_by(name=name).first()
        if not perm:
            self.fail("not-found")
            return

        self.success(id=str(perm.uuid))

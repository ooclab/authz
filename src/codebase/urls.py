from tornado.web import url

from codebase.controllers import (
    default,
    authz,
    permission,
    role,
    user
)


HANDLERS = [
    # TODO: 以下几个标准的接口应该工具层面统一提供, 务必显示定义

    url(r"/_spec",
        default.SpecHandler),

    url(r"/_health",
        default.HealthHandler),

    # Authorization
    url(r"/has_permission",
        authz.HasPermissionHandler),

    url(r"/has_permission_id",
        authz.HasPermissionIDHandler),

    # User

    url(r"/user/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        r"/role",
        user.UserRoleHandler),

    url(r"/user/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        r"/role/append",
        user.UserRoleAppendHandler),

    url(r"/user/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        r"/role/remove",
        user.UserRoleRemoveHandler),

    # Role

    url(r"/my/role",
        role.MyRoleHandler),

    url(r"/role",
        role.RoleHandler),

    url(r"/role/id",
        role.RoleIDByNameHandler),

    url(r"/role/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        role.SingleRoleHandler),

    url(r"/role/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        r"/permission",
        role.RolePermissionHandler),

    url(r"/role/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        r"/permission/append",
        role.RolePermissionAppendHandler),

    url(r"/role/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        r"/permission/remove",
        role.RolePermissionRemoveHandler),

    # Permission

    url(r"/my/permission",
        permission.MyPermissionHandler),

    url(r"/permission",
        permission.PermissionHandler),

    url(r"/permission/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        permission.SinglePermissionHandler),
]

#! /usr/bin/env python3

import logging
from importlib import import_module

import tornado.options
from eva.conf import settings

from codebase.app import make_app
from codebase.utils.sqlalchemy import dbc


def main():

    # sync database
    if settings.SYNC_DATABASE:
        import_module(settings.MODELS_MODULE)
        dbc.create_all()

    # 启动 Tornado
    app = make_app()
    server = tornado.httpserver.HTTPServer(app, xheaders=True)

    # 设置 options
    tornado.options.define("port", default=3000, help="listen port", type=int)
    if app.settings["debug"]:
        tornado.options.options.logging = "debug"
    tornado.options.parse_command_line()

    port = tornado.options.options.port
    sockets = tornado.netutil.bind_sockets(port)

    server.add_sockets(sockets)
    logging.info("api server is running at %d", port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

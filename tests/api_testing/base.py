import json
import uuid
import logging

import tornado.testing
from eva.conf import settings

from codebase.utils.sqlalchemy import dbc
from codebase.utils.swaggerui import api
from codebase.app import make_app
from codebase.models import User
from codebase.utils.common import scrub


def validate_default_error(body):
    spec = api.spec_dict["definitions"]["DefaultErrorResponse"]
    api.validate_object(spec, body)


def get_body_json(resp):
    return scrub(json.loads(resp.body))


class BaseTestCase(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        settings.DEBUG = False
        return make_app()

    @classmethod
    def setUpClass(cls):
        # TODO: 测试开始执行一次
        # 禁止 tornado 日志，如：WARNING:tornado.access:400
        logging.getLogger('tornado.access').disabled = True
        dbc.drop_all()

    @classmethod
    def tearDownClass(cls):
        # 测试结束执行一次
        dbc.drop_all()
        # dbc.close()

    def setUp(self):
        # 每个 testcase 执行前都会执行
        super().setUp()
        dbc.create_all()

        self.current_user = User(uuid=str(uuid.uuid4()))
        self.db.add(self.current_user)
        self.db.commit()

        self.http_request_headers = {"X-User-Id": str(self.current_user.uuid)}

    def tearDown(self):
        # 每个 testcase 执行后都会执行
        super().tearDown()
        # dbc.remove()
        dbc.drop_all()

    @property
    def db(self):
        return dbc.session()

    def _api_request(self, method, url, headers=None, body=None, **kwargs):
        _headers = self.http_request_headers
        if headers:
            _headers.update(headers)
        _headers.update(self.http_request_headers)
        if body:
            body = json.dumps(body)
        return self.fetch(
            url, method=method, body=body, headers=_headers,
            allow_nonstandard_methods=True,
            raise_error=False, **kwargs
        )

    def api_get(self, url, headers=None, **kwargs):
        return self._api_request("GET", url, headers=headers, **kwargs)

    def api_post(self, url, headers=None, body=None, **kwargs):
        return self._api_request("POST", url, headers=headers, body=body, **kwargs)

    def api_put(self, url, headers=None, body=None, **kwargs):
        return self._api_request("PUT", url, headers=headers, body=body, **kwargs)

    def api_delete(self, url, headers=None, **kwargs):
        return self._api_request("DELETE", url, headers=headers, **kwargs)

    def validate_default_success(self, body):
        self.assertEqual(body["status"], "success")

    def validate_not_found(self, resp):
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)

        self.assertEqual(body["status"], "not-found")

from .base import BaseTestCase


class HealthTestCase(BaseTestCase):

    def test_health(self):
        """GET /_health - 健康检查
        """

        resp = self.fetch("/_health")
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.body, b"ok")


class SpecTestCase(BaseTestCase):

    def test_spec(self):
        """GET / - SwaggerUI 文档
        """

        resp = self.fetch("/")
        self.assertEqual(resp.code, 200)

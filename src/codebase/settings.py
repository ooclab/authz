DEBUG = "false"
CORS = "false"
SECRET_KEY = "Unmy6tuxgIAPX7zxlp80MxcDz1mofni2chnrF4cxMQQjq"
SERVER_EMAIL = "info@ooclab.com"

SYNC_DATABASE = "true"
# http://docs.sqlalchemy.org/en/latest/core/engines.html
DB_URI = "sqlite://"
# DB_URI = "postgresql://root:password@postgres:5432/authz"

API_SCHEMA = "/work/codebase/schema.yml"

PAGE_SIZE = 10
ADMIN_ROLE_NAME = "admin"

# 默认测试关闭 ETCD 同步
SYCN_ETCD = False
ETCD_URL_ENDPOINT = "http://127.0.0.1:2379/v2/keys"

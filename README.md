# authz

The authorization (authz) service for service-oriented architecture


## 默认用户

我们需要为默认用户创建几个特殊账户（user_id），以方便系统初始化是可以精确匹配权限。

### anonymous

匿名用户

### authenticated

已验证的用户，也称登录用户

### admin

超级管理员


## 技术实现

当前基于 Tornado + SQLAlchemy 实现，通常只有一个权限查询接口需要被频繁访问。
如果涉及性能和分布式扩展的问题，可以考虑将其独立出来。当然，绝大部分的应用根本
达不到这个瓶颈，请勿“提前优化”！

# authz

[![Build Status](https://travis-ci.com/ooclab/authz.svg?branch=master)](https://travis-ci.com/ooclab/authz)

The authorization (authz) service for service-oriented architecture


## 特殊角色

我们需要为默认情况创建几个特殊角色（role name），以方便系统初始化是可以精确匹配权限。

### anonymous

匿名用户角色

### authenticated

已验证的用户角色，也称登录用户角色

### admin

超级管理员角色


## 技术实现

当前基于 Tornado + SQLAlchemy 实现，通常只有一个权限查询接口需要被频繁访问。
如果涉及性能和分布式扩展的问题，可以考虑将其独立出来。当然，绝大部分的应用根本
达不到这个瓶颈，请勿“提前优化”！

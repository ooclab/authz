# authz

[![Build Status](https://travis-ci.com/ooclab/authz.svg?branch=master)](https://travis-ci.com/ooclab/authz)
[![codecov](https://codecov.io/gh/ooclab/authz/branch/master/graph/badge.svg)](https://codecov.io/gh/ooclab/authz)

The authorization (authz) service for service-oriented architecture


## 简介

`authz` **提供** ：

1. 创建 **角色**
2. 创建 **权限**
3. 为 **用户** `增加` / `删除` **角色**
4. 为 **角色** `增加` / `删除` **权限**
5. 查询 **用户** 是否拥有指定的 **权限**

`authz` **不提供** ：

1. **用户** 管理：创建、删除、更新、登录、退出、...
2. **接口** 校验：如接口的访问权限，请求参数是否合规等， 需要和 [ga](https://github.com/ooclab/ga) （或类似的 API Gateway 软件）一起对外提供服务


## 文档目录

### 概念

- [角色](./docs/roles.md)

### 设计

- [性能](./docs/design-performance.md)

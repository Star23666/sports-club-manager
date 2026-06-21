# 前端 + Python 后端整合说明（完整功能）

## 结论

- 仅用“Python 后端 + 两个前端”可以实现完整业务功能。
- 但仍然必须配套 **MySQL**（后端数据源），否则无法运行。

> 现有仓库里根目录的 `docker-compose.yml` 默认起的是 Java 后端；Python 后端是另一套实现（FastAPI），接口路径与前端保持一致。

## 前端如何访问后端（不用改前端的关键）

两套前端都使用相对路径访问后端：

- 会员端：请求前缀是 `/api`
  - 代码里 `axios.defaults.baseURL = "/api"`
  - Docker 部署时由 Nginx 把 `/api` 反向代理到后端

- 管理端：请求前缀是 `/admin/api`
  - 代码里 `baseURL: "/admin/api"`
  - Docker 部署时由 Nginx 把 `/admin/api` 反向代理到后端

因此，只要保证容器内反代的目标“后端服务名 + 端口”正确，前端无需修改。

## Python 后端接口兼容性

Python（FastAPI）后端已按以下路径注册路由：

- 会员端：`/api/user`、`/api/action`、`/api/waiting`、`/api/transfer`、`/api/staff`、`/api/find`
- 管理端：`/admin/api/user`、`/admin/api/member`、`/admin/api/action`

参数风格保持与前端一致：大多数接口是 `POST` + QueryString，`token` 也通常通过 query 传递。

接口清单请参考：`docs/api-list.md`

## 依赖与常见坑

- MySQL：必须初始化表/视图/基础数据（仓库内有 `database/install.sql`）。
- 邮件（找回密码）：`/api/find/sendResetEmail` 依赖 SMTP 配置；未配置时可能会返回发送失败。

## Docker 一键跑“Python 后端 + MySQL + 两个前端”的要点

目前两套前端容器内的 Nginx 反代目标是 `http://backend:8081`。

想要把后端从 Java 切到 Python，有两种等价方式：

1) **推荐：让 Python 服务仍然叫 `backend` 且监听 `8081`**
- 这样两套前端的 Nginx 配置不用改。

2) 或者：保留 Python 服务名（例如 `python-backend`）
- 然后把两套前端的 Nginx `proxy_pass` 改为 `http://python-backend:8081`。

如果你希望我直接改 `docker-compose.yml` 做成默认起 Python 后端（服务名仍为 `backend`、端口仍为 8081），我可以继续帮你把 Compose 改好并附上启动命令。

## 与 Java 分开运行（你目前的需求）

我已经在项目根目录新增了 `docker-compose.python.yml`，用于单独启动 Python 后端版本。

注意：两套 compose 默认使用相同端口（8080/8081/8082/3306），因此**不能同时启动**；需要先停掉另一套再启动。

### 启动 Python 后端版本

- `docker compose -f docker-compose.python.yml up --build`

### 启动 Java 后端版本（原来的）

- `docker compose -f docker-compose.yml up --build`

### 停止并清理

- 停止：`docker compose -f docker-compose.python.yml down`
- 停止并删除数据卷（会清空 MySQL 数据）：`docker compose -f docker-compose.python.yml down -v`

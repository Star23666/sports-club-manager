# 🏸 Sports Club Manager / 体育俱乐部管理系统

<p align="center">
  <b>Open Source Member & Event Management System<br>开源会员与活动管理系统</b><br><br>
  <a href="https://github.com/JosephHu04/sports-club-manager/stargazers"><img src="https://img.shields.io/github/stars/JosephHu04/sports-club-manager?style=for-the-badge&color=yellow" alt="Stars"></a>
  <a href="https://github.com/JosephHu04/sports-club-manager/network/members"><img src="https://img.shields.io/github/forks/JosephHu04/sports-club-manager?style=for-the-badge&color=blue" alt="Forks"></a>
  <a href="https://github.com/JosephHu04/sports-club-manager/issues"><img src="https://img.shields.io/github/issues/JosephHu04/sports-club-manager?style=for-the-badge&color=red" alt="Issues"></a>
  <a href="https://github.com/JosephHu04/sports-club-manager/blob/main/LICENSE"><img src="https://img.shields.io/github/license/JosephHu04/sports-club-manager?style=for-the-badge" alt="License"></a>
  <br>
  <img src="https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/fastapi-0.115-009688.svg?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/vue-3.x-4FC08D.svg?style=flat-square&logo=vue.js&logoColor=white" alt="Vue 3">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg?style=flat-square" alt="MIT">
  <br>
  <img src="https://img.shields.io/badge/database-SQLite_|_MySQL-4479A1.svg?style=flat-square&logo=mysql&logoColor=white" alt="SQLite / MySQL">
  <img src="https://img.shields.io/badge/deploy-Docker_|_Bare_Metal-2496ED.svg?style=flat-square&logo=docker&logoColor=white" alt="Docker / Bare Metal">
  <img src="https://img.shields.io/badge/testing-pytest-0A9EDC.svg?style=flat-square&logo=pytest&logoColor=white" alt="pytest">
</p>

<p align="center">
  <b>Member registration · Event booking · Waitlist · QR-Code check-in · Admin dashboard<br>会员注册 · 活动预约 · 候补队列 · 扫码签到 · 管理后台</b><br>
  <sub>Clone → Configure → Deploy. Zero external dependencies in SQLite mode.<br>克隆 → 配置 → 部署。SQLite 模式零外部依赖。</sub>
</p>

---

## 📖 Table of Contents / 目录

- [What is this? / 这是什么？](#-what-is-this--这是什么)
- [Who is this for? / 谁适合用？](#-who-is-this-for--谁适合用)
- [Screenshots / 截图](#-screenshots--截图)
- [Features / 功能](#-features--功能)
- [Quick Start / 快速开始](#-quick-start--快速开始)
- [Demo Mode / 演示数据](#-demo-mode--演示数据)
- [Make It Yours / 定制你的系统](#-make-it-yours--定制你的系统)
- [Architecture / 架构](#-architecture--架构)
- [API Overview / API 概览](#-api-overview--api-概览)
- [Deployment / 部署](#-deployment--部署)
- [Tech Stack / 技术栈](#-tech-stack--技术栈)
- [Testing / 测试](#-testing--测试)
- [Security / 安全](#-security--安全)
- [Roadmap / 路线图](#-roadmap--路线图)
- [Contributing / 贡献](#-contributing--贡献)

---

## 💡 What is this? / 这是什么？

**English:** A full-stack club management web application that handles member registration, event booking, waitlist queuing, QR-code attendance, and admin dashboards. Designed to be customized — change the name, logo, and labels to fit your club.

**中文：** 一个全栈的俱乐部管理 Web 应用，涵盖会员注册、活动预约、候补队列、扫码签到、管理后台等功能。设计为可定制化——修改名称、Logo、标签即可适配你的俱乐部。

---

## 🎯 Who is this for? / 谁适合用？

| You are… / 你是… | You can… / 你可以… |
|---|---|
| 🎓 University club officer / 大学社团负责人 | Manage member signups & event attendance / 管理成员报名和活动出勤 |
| 🏋️ Community sports center / 社区体育中心 | Track class bookings with waitlist / 带候补的课程预约管理 |
| 💻 Full-stack learner / 全栈学习者 | Study a complete Vue + FastAPI project / 学习完整的 Vue + FastAPI 项目 |
| 🏫 CS student / 计算机专业学生 | Use as reference or base project / 作为参考或毕设基础 |
| 🔧 Hobbyist / 爱好者 | Self-host a free management tool / 自托管免费管理工具 |

---

## 📸 Screenshots / 截图

> *Add screenshots here — repos with screenshots get 3× more engagement.*
> *在此处添加截图 — 有截图的仓库互动量高 3 倍。*

Suggested shots / 建议截图：
- Member login & registration / 会员登录注册页
- Event booking interface / 活动预约界面
- QR-code check-in / 扫码签到
- Admin dashboard with stats / 管理后台统计面板

```markdown
![Member Portal](docs/screenshots/member-portal.png)
![Admin Dashboard](docs/screenshots/admin-dashboard.png)
```

---

## ✨ Features / 功能

### Member Portal / 会员端 (Vue 3 + Vant UI)

| English | 中文 |
|---|---|
| 📝 Register with email, phone, member ID | 📝 邮箱/手机/学号注册 |
| 🔑 Password login (device-only login temporarily disabled) | 🔑 密码登录（设备免密登录暂时停用） |
| 📅 Browse & register for events | 📅 浏览并报名活动 |
| ⏳ Auto waitlist when full | ⏳ 满员自动进入候补 |
| ↔️ Transfer spot to another member | ↔️ 名额转让给其他成员 |
| 📱 QR-code or manual-code check-in | 📱 扫码或手动输入签到码 |
| 🔍 Account recovery & password reset | 🔍 找回账号与重置密码 |

### Admin Dashboard / 管理端 (Vue 3 + LayUI)

| English | 中文 |
|---|---|
| 👥 Member CRUD, approve, reset password | 👥 成员增删改查、审核、重置密码 |
| 📊 Inbox stats dashboard | 📊 首页统计面板 |
| 🏟 Event create, release, stop, assign staff | 🏟 活动创建、发布、停止、分配工作人员 |
| 📋 Booking & attendance records | 📋 预约与出勤记录查询 |
| ⚠️ No-show tracking & auto-restriction | ⚠️ 失信追踪与自动限制 |

### Backend / 后端 (FastAPI)

| English | 中文 |
|---|---|
| 🗄️ Dual database: SQLite (dev) + MySQL (prod) | 🗄️ 双数据库：SQLite（开发）+ MySQL（生产） |
| 📧 SMTP email with HTML template | 📧 SMTP 邮件，可自定义 HTML 模板 |
| 🔐 UUID token auth with expiry | 🔐 UUID 令牌认证，含过期机制 |
| 🌐 Configurable CORS | 🌐 可配置的跨域支持 |
| 🧪 pytest suite with SQLite integration tests | 🧪 pytest 测试套件，SQLite 集成测试 |

---

## ⚡ Quick Start / 快速开始

```bash
# Clone / 克隆
git clone https://github.com/JosephHu04/sports-club-manager.git
cd sports-club-manager

# Windows
.\start.ps1

# macOS / Linux
bash start.sh
```

→ Open / 打开 <http://localhost:8081/docs> — backend live with SQLite.  
→ First administrator / 首位管理员：运行 `cd python && python -m app.bootstrap_admin`，按提示输入新密码（不会显示或写入命令历史）。旧版数据库若仍有公开的 `admin/admin`，此命令会要求设置新密码并轮换该账号。

> 安全提示：旧版 MySQL 数据库请先执行 `ALTER TABLE users MODIFY password VARCHAR(255);` 和 `database/upgrade_recovery_rate_limit.sql`，再升级服务。新建数据库已包含限流表；SQLite 会自动建表。现有用户的 MD5 密码仅在正确登录时迁移为 Argon2；公开的旧版管理员密码不能登录，必须通过上述本机命令轮换。密码、签到码和注册、联系等个人资料经 JSON 请求体传递，会话令牌通过 `Authorization: Bearer` 请求头传递。设备免密登录与新增设备入口已停用，旧设备可撤销。账户找回入口现有数据库固定时间窗限流。隔离 MySQL 8.0 库中的迁移和限流已验收，但完整权限审计、MySQL 全流程及摄像头扫码验收仍未完成，不要公开部署真实用户数据。

**Requirements / 环境要求:** Python 3.10+. That's it. No Docker, MySQL, or Node.js needed.

---

## 🎬 Demo Mode / 演示数据

```bash
# Fill database with sample data / 填充演示数据
.venv/bin/python python/seed_demo.py       # macOS / Linux
.venv\Scripts\python python/seed_demo.py    # Windows
```

Creates 6 members (password: `Aa1$abcd`), 3 events, and bookings.  
创建 6 个会员（密码 `Aa1$abcd`）、3 个活动和预约记录。

---

## 🎨 Make It Yours / 定制你的系统

**Step 1 — Configure branding / 配置品牌信息** (`python/.env`):

```env
APP_NAME="My Badminton Club"
ORG_NAME="My Badminton Club"
MEMBER_ID_LABEL="Student ID"        # or "Employee ID", "Member #"
EMAIL_DOMAIN="student.uni.edu"      # optional, for auto-generated emails
```

**Step 2 — Replace UI text / 替换界面文字:**  
Search `My Club` in the frontend and replace with your club name.  
在前端搜索 `My Club` 并替换为你的俱乐部名称。

**Step 3 — Replace logos / 替换 Logo:**  
- `admin-front-end/src/assets/badminton.png`
- `client-front-end/src/assets/badminton.png`

**Step 4 — Configure URLs / 配置 URL** (`admin-front-end/public/config.js`)

---

## 🏗 Architecture / 架构

```
Browser / 浏览器
  ├─ Member Portal (:8080) ─── /api/* ─────┐
  └─ Admin Dashboard (:8082) ─ /admin/api/* ─┤
                                             ▼
                                    FastAPI Backend (:8081)
                                    ├─ Auth (token-based)
                                    ├─ Booking + Waitlist
                                    ├─ Transfer Engine
                                    ├─ QR Sign-in
                                    └─ Admin CRUD
                                             │
                                    SQLAlchemy ORM
                                    ├─ SQLite (dev 开发)
                                    └─ MySQL 8 (prod 生产)
```

---

## 📮 API Overview / API 概览

All endpoints: `POST` + QueryString → `{ "status": int, "data": ... }`  
所有接口使用 `POST` + QueryString 传参。

| Prefix / 前缀 | Module / 模块 | Examples / 示例 |
|---|---|---|
| `/api/user` | Member Account / 会员账户 | login, register, verify, password, equipment |
| `/api/action` | Events & Booking / 活动与预约 | queryAction, attendAction, cancelAction |
| `/api/waiting` | Waitlist / 候补 | waitCreate, waitDelete, queryWaiting |
| `/api/transfer` | Spot Transfer / 名额转让 | queryTransfer, transferRecord, acceptTransfer |
| `/api/staff` | Check-in / 签到 | queryAction, startSign, querySign, finishSign |
| `/api/find` | Account Recovery / 账号找回 | queryUserName, sendResetEmail, resetPassword |
| `/admin/api/*` | Admin Panel / 管理后台 | member CRUD, event CRUD, inbox stats |

📄 Full list / 完整清单: [`docs/api-list.md`](docs/api-list.md)  
🧪 Interactive docs / 交互文档: <http://localhost:8081/docs>

---

## 🚢 Deployment / 部署

### Option A: Docker (full stack / 全家桶)

```bash
docker compose up --build -d
```

Launches MySQL + backend + member portal + admin dashboard.  
启动 MySQL + 后端 + 会员端 + 管理端。

### Option B: Bare metal / 裸机部署

```bash
# Backend / 后端
cd python && pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8081

# Frontend / 前端 (separate terminals / 分开终端)
cd admin-front-end && npm install && npm run build
cd client-front-end && npm install && npm run build
# Serve dist/ with Nginx / 用 Nginx 托管 dist/
```

### Option C: Cloud / 云部署 (Render / Railway / VPS)

1. Set `DB_TYPE=sqlite` for simple single-server / 单服务器用 SQLite
2. Or point `DB_HOST` to managed MySQL / 或指向云端 MySQL
3. Frontends are static — deploy to CDN / 前端是静态文件，可部署到 CDN

---

## 🛠 Tech Stack / 技术栈

| Layer / 层 | Technology / 技术 |
|---|---|
| Backend / 后端框架 | FastAPI 0.115 (Python 3.10+) |
| ORM | SQLAlchemy 2.0 |
| Databases / 数据库 | SQLite (dev) / MySQL 8 (prod) |
| Member UI / 会员端 | Vue 3 + Vant UI 4 |
| Admin UI / 管理端 | Vue 3 + LayUI Vue 2 |
| Auth / 认证 | UUID tokens (3-hour session / 3 小时有效期) |
| Email / 邮件 | SMTP with STARTTLS (port 587) |
| Testing / 测试 | pytest + httpx + SQLite |
| Container / 容器 | Docker + docker-compose |
| Reverse proxy / 反代 | Nginx (Alpine) |

---

## 🧪 Testing / 测试

```bash
pip install pytest httpx
pytest tests/ -v
```

Tests cover token verification, login, registration, password validation, utilities. Integration tests use SQLite in-memory — no setup needed.  
测试覆盖令牌验证、登录、注册、密码校验、工具函数。集成测试使用 SQLite 内存数据库，无需额外配置。

Frontend builds / 前端构建：分别在 `client-front-end` 和 `admin-front-end` 执行 `npm ci && npm run build`；PR 自动检查也会运行这两项。

---

## 🔒 Security / 安全

| Concern / 关注点 | Implementation / 实现 | Production Note / 生产环境建议 |
|---|---|---|
| Password hashing / 密码哈希 | 新密码使用 Argon2id；旧 MD5 在成功登录后升级 | 先轮换旧版公开管理员密码 |
| Auth / 认证 | UUID v4 token, 3h expiry；`Authorization: Bearer` 请求头；设备免密登录暂时停用 | 仍需完整权限审计，不可公开部署真实用户数据 |
| Account recovery / 账户找回 | 用户名查询、重置邮件和重置码提交按来源 IP 与账号/验证码分别限流，计数保存在数据库 | MySQL 旧库先建 `recovery_rate_limit` 表；反向代理后按直连地址限流，需评估共享 IP 的影响 |
| Sensitive data transport / 敏感数据传输 | 密码、签到码及注册/联系资料在 JSON 请求体中 | 部署时必须使用 HTTPS；其余接口仍需审计 |
| CORS | 显式配置 `CORS_ORIGINS` | 部署前设置实际前端域名 |
| SMTP | STARTTLS on port 587 | Use app-specific passwords |
| SQL injection / SQL 注入 | Parameterized queries / 参数化查询 | ✅ Safe / 安全 |

---

## 🗺️ Roadmap / 路线图

- [ ] 🌐 i18n / Internationalization / 国际化（英文界面）
- [x] 🔐 Argon2 password migration / 密码哈希迁移
- [ ] 🔑 JWT authentication with refresh tokens / JWT 认证
- [ ] 📊 Advanced statistics & charts dashboard / 高级统计图表看板
- [ ] 📱 PWA support / PWA 移动端支持
- [ ] 🔔 WebSocket real-time waitlist notifications / WebSocket 实时候补通知
- [ ] 📧 Email notification system / 邮件通知系统
- [ ] 🧪 Frontend e2e tests (Playwright/Cypress) / 前端端到端测试
- [ ] 🐳 One-click Docker deployment to cloud / 一键云部署

---

## 🤝 Contributing / 贡献

Pull requests welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md).  
欢迎提交 PR！详见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

### Contributors / 贡献者

<a href="https://github.com/JosephHu04/sports-club-manager/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=JosephHu04/sports-club-manager" alt="Contributors" />
</a>

---

## ⭐ Star History / 星标历史

<a href="https://star-history.com/#JosephHu04/sports-club-manager&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=JosephHu04/sports-club-manager&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=JosephHu04/sports-club-manager&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=JosephHu04/sports-club-manager&type=Date" />
  </picture>
</a>

If this helps you, give it a ⭐ — it helps others find it!  
如果对你有帮助，点个 ⭐ 让更多人看到！

---

## 📄 License / 许可证

MIT © see [LICENSE](LICENSE)

---

<p align="center">
  <sub>Built with ❤️ for clubs everywhere. Clone it. Customize it. Share it.<br>为所有俱乐部而建。克隆、定制、分享。</sub>
</p>

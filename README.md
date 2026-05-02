# TimberPlay 木质拼装玩具独立站

一个面向北美家庭、STEM 玩具和礼品场景的 wood puzzle 创意木质玩具独立站 Demo，包含：

- Python 标准库后端 API
- 原生 HTML/CSS/JavaScript 前端
- 商品展示、筛选、购物车、下单、邮件订阅
- 宣传方案文档

## 本地运行

无需安装第三方依赖，使用 Python 3 即可启动：

```bash
python3 backend/server.py
```

访问：

```text
http://localhost:8000
```

## Vercel 部署

仓库已包含 `vercel.json` 和 `api/*.py` serverless functions。将 GitHub 仓库导入 Vercel 后：

1. 在 Vercel 新建项目，选择 **Import Git Repository** 并连接这个 GitHub 仓库。
2. Framework Preset 选择 **Other**。
3. Build Command 留空，Output Directory 留空。
4. 每次 push 到 GitHub 分支后，Vercel 会自动生成 Preview Deployment；合并到主分支后会更新 Production Deployment。
5. 在 GitHub PR 页或 Vercel Dashboard 的 Deployments 里查看每次 git push 对应的最新预览链接。

部署后可访问：

```text
https://你的项目名.vercel.app
```

## API

- `GET /api/health`：健康检查
- `GET /api/products?q=&theme=`：商品列表、关键词和主题筛选
- `POST /api/orders`：创建订单
- `POST /api/newsletter`：订阅邮件优惠

## 项目结构

```text
api/*.py                Vercel serverless API
backend/server.py       后端 API 与静态资源服务
backend/store.py        商品、订阅、订单共享业务逻辑
frontend/index.html     独立站页面
frontend/styles.css     页面样式
frontend/app.js         商品、购物车、下单交互
docs/marketing-plan.md  宣传方案
vercel.json             Vercel 路由与静态资源配置
```

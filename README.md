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

## API

- `GET /api/health`：健康检查
- `GET /api/products?q=&theme=`：商品列表、关键词和主题筛选
- `POST /api/orders`：创建订单
- `POST /api/newsletter`：订阅邮件优惠

## 项目结构

```text
backend/server.py       后端 API 与静态资源服务
frontend/index.html     独立站页面
frontend/styles.css     页面样式
frontend/app.js         商品、购物车、下单交互
docs/marketing-plan.md  宣传方案
```

# 中国区量化交易全栈系统（Flask + HTML/CSS/JS）

本项目是一个可运行的示例级量化交易平台，面向中国市场（A股/指数示例），包含：

- 行情展示
- 策略管理
- 回测模块
- 模拟交易
- 订单管理
- 持仓与资金管理
- 风控与审计日志
- 可视化仪表盘
- 前后端解耦（REST API + 静态前端）
- SQLite 示例数据库与测试数据

## 1. 项目目录结构

```text
Trade/
├── README.md
├── docs/
│   ├── deployment.md
│   └── startup.md
├── data/
│   └── quant_trade.db             # 运行后自动创建
└── backend/
    ├── requirements.txt
    ├── run.py
    ├── seed_data.py
    ├── app/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── db.py
    │   ├── models.py
    │   ├── api/
    │   │   └── routes.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── audit_service.py
    │   │   ├── backtest_service.py
    │   │   ├── dashboard_service.py
    │   │   ├── market_service.py
    │   │   ├── risk_service.py
    │   │   ├── strategy_service.py
    │   │   └── trading_service.py
    │   ├── static/
    │   │   ├── css/style.css
    │   │   └── js/app.js
    │   └── templates/
    │       └── index.html
    └── tests/
        ├── conftest.py
        └── test_api.py
```

## 2. 启动方式

详见 `docs/startup.md`。

快速启动：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed_data.py
python run.py
```

访问：`http://localhost:5000`

## 3. REST API（核心）

- `GET /api/health`：健康检查
- `GET /api/market-data?symbol=000001.SZ`：行情
- `GET/POST /api/strategies`：策略列表/新增
- `GET /api/backtests`：回测结果列表
- `POST /api/backtests/run`：执行回测
- `GET/POST /api/orders` / `/api/orders/paper`：订单列表/模拟下单
- `GET /api/positions`：持仓
- `GET /api/account`：资金与权益
- `POST /api/risk/evaluate`：执行风控评估
- `GET /api/risk/events`：风控事件
- `GET /api/audit-logs`：审计日志
- `GET /api/dashboard/metrics`：仪表盘指标

## 4. 部署文档

详见 `docs/deployment.md`，包含 Gunicorn + Nginx 示例。

## 5. 测试

```bash
cd backend
pytest
```

## 6. 说明

- 本项目用于教学/演示，非生产交易系统。
- 回测与风控逻辑为简化模型，可按券商实盘/撮合规则扩展。

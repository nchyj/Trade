# 中国区量化交易全栈系统（Flask + HTML/CSS/JS）

本项目是一个可运行的示例级量化交易平台，参考 PTrade 的基础使用流程，支持：

- 策略编写（必须包含 `initialize` 与 `handle_data`）
- 参数化回测（开始时间、结束时间、回测资金、回测基准、回测频率）
- 回测指标（策略收益、最大回撤、胜率、盈亏比、Sharpe）
- 模拟交易、订单管理、持仓/资金管理
- 风控与审计日志
- 定时任务（策略定时执行 / 实时拉取 A 股大盘详情快照）
- 可视化仪表盘

## 1. 项目目录结构

```text
Trade/
├── README.md
├── docs/
│   ├── deployment.md
│   └── startup.md
├── data/
│   └── quant_trade.db
└── backend/
    ├── requirements.txt
    ├── run.py
    ├── check_env.py
    ├── seed_data.py
    ├── app/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── db.py
    │   ├── models.py
    │   ├── api/routes.py
    │   ├── services/
    │   │   ├── backtest_service.py
    │   │   ├── scheduler_service.py
    │   │   └── ...
    │   ├── static/
    │   │   ├── css/style.css
    │   │   └── js/app.js
    │   └── templates/index.html
    └── tests/
        ├── conftest.py
        └── test_api.py
```

## 2. 启动方式

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python check_env.py
pip install -r requirements.txt
python seed_data.py
python run.py
```

Windows PowerShell：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python check_env.py
pip install -r requirements.txt
python seed_data.py
python run.py
```

如果是中国大陆网络建议：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

访问：`http://localhost:5000`

## 3. PTrade 风格流程

1. 进入“策略编写界面”，加载策略并编辑代码（需包含 `initialize` 与 `handle_data`）。
2. 在“回测配置与执行”填写：开始时间、结束时间、回测资金、基准、频率。
3. 点击“回测”，查看收益、最大回撤、胜率、盈亏比。
4. 可配置定时任务：
   - `strategy_tick`：定时触发策略任务
   - `market_pull`：定时拉取 A 股大盘详情快照

## 4. 核心 API

- `GET /api/strategies` / `GET /api/strategies/<id>` / `PUT /api/strategies/<id>/code`
- `POST /api/backtests/run`（必填：`strategy_id/symbol/start_date/end_date/init_cash/benchmark/frequency`）
- `GET /api/scheduler/tasks` / `POST /api/scheduler/tasks`
- `POST /api/scheduler/tasks/<id>/start|stop|run-once`
- `GET /api/market-overview`

## 5. 测试

```bash
cd backend
pytest
```

## 6. 常见报错

### `ModuleNotFoundError: No module named 'flask'`
说明依赖未装到当前 Python 环境：

```bash
cd backend
python check_env.py
pip install -r requirements.txt
```

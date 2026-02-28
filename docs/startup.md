# 启动说明

## 环境要求
- Python 3.10+
- Linux / macOS / WSL / Windows PowerShell

## 快速启动（Linux/macOS）

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python check_env.py
pip install -r requirements.txt
python seed_data.py
python run.py
```

## 快速启动（Windows PowerShell）

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python check_env.py
pip install -r requirements.txt
python seed_data.py
python run.py
```

## 回测使用方式
1. 打开策略编写界面，编辑策略代码，必须有：
   - `initialize(context)`
   - `handle_data(context, data)`
2. 在回测面板配置：开始时间、结束时间、回测资金、回测基准、回测频率。
3. 点击回测后查看：策略收益、最大回撤、胜率、盈亏比、Sharpe。

## 定时任务使用方式
- 创建 `strategy_tick` 任务：用于定时执行策略任务。
- 创建 `market_pull` 任务：用于定时拉取 A 股大盘详情快照。
- 可对任务执行：启动 / 停止 / 立即执行。

## 常见问题
- 报错 `ModuleNotFoundError: No module named 'flask'`
  - 处理：先激活虚拟环境，再 `pip install -r requirements.txt`
  - 中国区网络可用：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

# 启动说明

## 环境要求
- Python 3.10+
- Linux / macOS / WSL

## 安装并运行

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed_data.py
python run.py
```

## 初始化内容
- SQLite 文件：`data/quant_trade.db`
- 默认账户：初始现金 1,000,000
- 示例策略：MA_Cross_A股 / RSI_Revert
- 示例行情：`000001.SZ`、`600519.SH`、`399001.SZ`

## 访问地址
- 前端页面：`http://localhost:5000/`
- API 示例：`http://localhost:5000/api/health`

# 部署文档（示例）

## 1. 安装依赖

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
python seed_data.py
```

## 2. Gunicorn 启动

```bash
cd backend
gunicorn -w 2 -b 0.0.0.0:5000 run:app
```

## 3. Nginx 反向代理示例

```nginx
server {
    listen 80;
    server_name your-domain;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 4. systemd 服务（可选）

```ini
[Unit]
Description=Quant Trade Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/Trade/backend
Environment="PATH=/opt/Trade/backend/.venv/bin"
ExecStart=/opt/Trade/backend/.venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

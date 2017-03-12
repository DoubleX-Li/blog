# 基于Flask的博客
## 
## 安装
```bash
git clone https://github.com/DoubleX-Li/Blog.git
cd Blog
pip install -r requirements.txt
pip install gunicorn
```
## 设置
### 环境变量
在`/etc/profile'中，添加如下信息：
```bash
MAIL_USERNAME=your_email_address
export MAIL_USERNAME
MAIL_PASSWORD=your_email_password
export MAIL_PASSWORD
LI_ADMIN=your_email_address
export LI_ADMIN
```
再执行
```bash
source /etc/profile
```
### config.py
修改数据库地址

### 数据库初始化
```bash
cd /path-to-Blog
python manage.py db init
python manage.py db migrate -m "initial migration"
python manage.py db upgrade
```
## 运行
### 启动gunicorn
gunicorn manage:app -p manage.pid -b 127.0.0.1:8000 -D

### 启动nginx
在`nginx.conf`文件中，添加
```shell
server {
        listen       80;
        server_name  ip_or_your_domain;

        location / {
			# Pass the request to Gunicorn
			proxy_pass http://127.0.0.1:8000;

			# Set some HTTP headers so that our app knows where the request really came from
			proxy_set_header Host $host;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		}
    }
```


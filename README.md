# 基于Flask的博客
## 安装
```bash
pip install -r requirements
python manage.py db init
python manage.py db -m "initial migration"
python manage.py db upgrade
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

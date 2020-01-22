# TOL_Trainer

1. 啟動python虛擬環境 (python > 3.6)

2. 安裝所需套件
```
$ pip install -r requirements.txt
```

3. 確認環境變數存在（可存成檔名為.env的檔案）
```
SECRET_KEY=''
SQLALCHEMY_DBURI='sqlite:///site.db'
FLASK_APP='run.py'
EMAIL_USER='要用來寄信的gmail信箱地址'
EMAIL_PASS='信箱的驗證密碼'
```

4. 讀進環境變數
```
$ source <環境變數檔案>
```

# 開發用

5. 啟動flask (開發用)
```
$ flask run
```

# 部署用

在server上實際是用nginx和uwsgi部署flask，因此對nginx和uwsgi都有做相關設定。

## uwsgi.ini 檔

```
$ uwsgi --ini uwsgi.ini
```

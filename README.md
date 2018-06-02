# 豆坟

用来备份豆瓣帐号的软件。目前支持备份关注、黑名单、书影音、广播。

开发环境要求：

- VSCode
- Python 3.6 
- virtualenv 15.2
- Nodejs 8.9
- npm 5.8
- git 2.16

## 开始

    > npm config set script-shell "C:\\Program Files\\Git\\usr\\bin\\bash.exe"
    > npm i

如果安装 peewee 组件提示『找不到sqlite3.h』错误，尝试使用如下方法安装：

    > set NO_SQLITE=1
    > pip install peewee

## 命令

调式 app：

    > npm run app

调试 service：

    > npm run service

打包 app：

    > npm run build:app

打包 service：

    > npm run build:service

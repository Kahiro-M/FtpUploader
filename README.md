# FTPアップローダー
指定したファイル、指定したディレクトリ配下のファイルをFTPサーバにアップロードします。

# 環境
- OS: Windows 11 23H2
- python: 3.11.1

# 設定ファイルの記述

```ini
;FTPサーバの設定関係
[FTP]
server_host = example.com      ;FTPサーバのホスト名
server_dir = /path/to/ftp/dir  ;FTPサーバのディレクトリ
ftp_user = ftp_user_name       ;FTPユーザ名
ftp_password = ftp_user_pw     ;FTPユーザのパスワード
ftp_tls = tlsv1.2              ;TLS1.2を使用する場合の指定('TLSv1.2','TLSv12','TLS1.2','TLS12','TLS'のどれかを指定可能)

;アップロードファイルの指定(カンマ区切りで複数ファイルの指定)
[FILES]
files_to_upload =
    example.txt,
    example.csv,
    example.jpg

;アップロードディレクトリの指定(カンマ区切りで複数ディレクトリの指定)
[DIRECTORIES]
directories_to_upload = 
    ./sample,
    ./sample2,
    ./sample3
```

# 使用方法
```sh
# デフォルトの設定ファイルを使用する場合)
FtpUploader.py

# 指定した設定ファイルを使用する場合)
FtpUploader.py [ファイルパス]
```

from ftplib import FTP_TLS
from ftplib import FTP
import ssl
import os
import configparser
import logging
import datetime

def print_log(str,log_level):
    print(str)
    if(log_level in ['0','info','INFO']):
        logging.info(str)
    if(log_level in ['1','warning','WARNING']):
        logging.warning(str)
    if(log_level in ['2','error','ERROR']):
        logging.error(str)


# FTP over TLSv1.2で接続するためのFTP_TLSのサブクラスを作成
class FTP_TLSv12(FTP_TLS):
    def __init__(self, host='', user='', passwd='', acct='', keyfile=None, certfile=None,
                 timeout=60, source_address=None, context=None):
        super().__init__(host, user, passwd, acct, keyfile, certfile, timeout, source_address)
        if context is None:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context = context

def read_config(config_path):
    config = configparser.ConfigParser()
    read_ret = config.read(config_path)
    if(len(read_ret) > 0):
        server_host = config.get('FTP', 'server_host')
        server_dir = config.get('FTP', 'server_dir')
        ftp_user = config.get('FTP', 'ftp_user')
        ftp_password = config.get('FTP', 'ftp_password')
        ftp_tls = config.get('FTP', 'ftp_tls')
    else:
        # ファイル読み取れない場合のデフォルト（テスト環境）
        print_log(config_path+'が読み取れないため、デフォルト接続設定で実行します。','warning')
        server_host = 'sample_host_name'
        server_dir = '/sample/dir/to/path'
        ftp_user = 'sample_user'
        ftp_password = 'sample_password'
        ftp_tls = 'TLSv1.2'
    return server_host, server_dir, ftp_user, ftp_password, ftp_tls

def upload_csv_to_ftp_tls(server_host, server_dir, ftp_user, ftp_password, local_csv_paths, ftp_tls):
    try:
        tls_type_list = [s.lower() for s in ['TLSv1.2','TLSv12','TLS1.2','TLS12','TLS']]

        # 接続とログイン
        if(ftp_tls.lower() in tls_type_list):
            ftp = FTP_TLSv12(server_host)
            print_log('TLSv1.2で接続します。','info')
        else:
            ftp = FTP(server_host)
            print_log('非暗号化通信で接続します','info')

        ftp.login(ftp_user, ftp_password)
        
        # サーバのディレクトリに移動
        print_log(server_dir+'に移動します。','info')
        ftp.cwd(server_dir)
        
        for local_csv_path in local_csv_paths:
            print_log(local_csv_path+'をアップロード中。。。','info')
            with open(local_csv_path, 'rb') as local_file:
                filename = os.path.basename(local_csv_path)
                ftp.storbinary(f'STOR {filename}', local_file)
        
        # 接続を閉じる
        ftp.quit()
        print_log('アップロードが完了しました。','info')
    except Exception as e:
        print_log(('エラー:',e),'error')

# ローカルファイルを読み取って実行
config_path = 'data.ini'
local_csv_paths = [
    './hanby.csv',
    './hnhp_jd.csv',
    './hnhp.csv',
    ]

# 日付を取得してYYYYMMDD形式の文字列を作成
current_date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
# ログの設定
log_file_path = f'ftp_upload_{current_date}.log'
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

server_host, server_dir, ftp_user, ftp_password, ftp_tls = read_config(config_path)
upload_csv_to_ftp_tls(server_host, server_dir, ftp_user, ftp_password, local_csv_paths, ftp_tls)

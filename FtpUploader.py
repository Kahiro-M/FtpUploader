from ftplib import FTP_TLS
from ftplib import FTP
import ssl
import os
import sys
import re
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
    read_ret = config.read(config_path, encoding='utf-8')
    if(len(read_ret) > 0):
        if(config.has_section('FTP')):
            if(config.has_option('FTP','server_host')):
                server_host = config.get('FTP', 'server_host')
            else:
                print_log(config_path+'の[server_host]オプションが読み取れないため、デフォルト接続設定で実行します。','warning')
                server_host = 'sample_host_name'

            if(config.has_option('FTP','server_dir')):
                server_dir = config.get('FTP', 'server_dir')
            else:
                print_log(config_path+'の[server_dir]オプションが読み取れないため、デフォルト接続設定で実行します。','warning')
                server_dir = '/sample/dir/to/path'

            if(config.has_option('FTP','ftp_user')):
                ftp_user = config.get('FTP', 'ftp_user')
            else:
                print_log(config_path+'の[ftp_user]オプションが読み取れないため、デフォルト接続設定で実行します。','warning')
                ftp_user = 'sample_user'

            if(config.has_option('FTP','ftp_password')):
                ftp_password = config.get('FTP', 'ftp_password')
            else:
                print_log(config_path+'の[ftp_password]オプションが読み取れないため、デフォルト接続設定で実行します。','warning')
                ftp_password = 'sample_password'

            if(config.has_option('FTP','ftp_tls')):
                ftp_tls = config.get('FTP', 'ftp_tls')
            else:
                print_log(config_path+'の[ftp_tls]オプションが読み取れないため、デフォルト接続設定で実行します。','warning')
                ftp_tls = 'tlsv1.2'
        else:
            print_log(config_path+'の[FTP]セクションが読み取れないため、デフォルト接続設定で実行します。','warning')
            server_host = 'sample_host_name'
            server_dir = '/sample/dir/to/path'
            ftp_user = 'sample_user'
            ftp_password = 'sample_password'
            ftp_tls = 'TLSv1.2'

        if(config.has_section('FILES')):
            if(config.has_option('FILES','files_to_upload')):
                files_to_upload = re.split(r',|\n', config.get('FILES','files_to_upload'))
                files_to_upload = [item for item in files_to_upload if item.strip() != ""]
                files_to_upload = [item.strip() for item in files_to_upload]
            else:
                print_log(config_path+'の[files_to_upload]オプションが読み取れないため、デフォルト接続設定で実行します。','warning')
                files_to_upload = [
                    './abc1.csv',
                    './abc2.csv',
                    './abc3.csv',
                ]
        else:
            print_log(config_path+'の[FILES]セクションが読み取れないため、デフォルト接続設定で実行します。','warning')
            files_to_upload = [
                './abc1.csv',
                './abc2.csv',
                './abc3.csv',
            ]
    else:
        # ファイル読み取れない場合のデフォルト（テスト環境）
        print_log(config_path+'が読み取れないため、デフォルト接続設定で実行します。','warning')
        server_host = 'sample_host_name'
        server_dir = '/sample/dir/to/path'
        ftp_user = 'sample_user'
        ftp_password = 'sample_password'
        ftp_tls = 'TLSv1.2'
        files_to_upload = [
            './abc1.csv',
            './abc2.csv',
            './abc3.csv',
            ]
    return server_host, server_dir, ftp_user, ftp_password, ftp_tls, files_to_upload

def upload_file_to_ftp_tls(server_host, server_dir, ftp_user, ftp_password, files_to_upload, ftp_tls):
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
        
        for file_to_upload in files_to_upload:
            print_log(file_to_upload+'をアップロード中。。。','info')
            with open(file_to_upload, 'rb') as local_file:
                filename = os.path.basename(file_to_upload)
                ftp.storbinary(f'STOR {filename}', local_file)
        
        # 接続を閉じる
        ftp.quit()
        print_log('アップロードが完了しました。','info')
    except Exception as e:
        print_log(('エラー:',e),'error')


def upload(input='data.ini'):
    # ローカルファイルを読み取って実行
    config_path = input

    # 日付を取得してYYYYMMDD形式の文字列を作成
    current_date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # ログの設定
    log_file_path = f'ftp_upload_{current_date}.log'
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print_log('============= FTPアップローダー =============','info')
    print_log('                                    Ver.1.0.2','info')
    server_host, server_dir, ftp_user, ftp_password, ftp_tls, files_to_upload = read_config(config_path)
    upload_file_to_ftp_tls(server_host, server_dir, ftp_user, ftp_password, files_to_upload, ftp_tls)
    print_log('=============================================','info')

def main(input):
    upload(input)

if __name__ == '__main__':
    args = sys.argv
    if(len(args)>1):
        main(args[1])
    else:
        main()

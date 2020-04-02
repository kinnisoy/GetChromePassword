# GetChromePassword
The way to get your password which has restored in your localhost by chrome.

##如果需要其他瀏覽器的密碼導出，修改其中的數據庫路徑即可。

可參考：https://www.secpulse.com/archives/124777.html

2020年2月，Google更新了Chrome瀏覽器中，關於cookies和保存的密碼的加密方式：
新的加密方式為：
        1.32字节DPAPI加密，2.5字节b’DPAPI’头，3.base64编码储存
        詳細可參考：https://blog.csdn.net/m0_46146791/article/details/104686060
        
Chrome_before_80ver文件夾中，可以一鍵導出80版本之前chrome瀏覽器中保存的所有密碼
chrome_after_80ver文件中，為修改加密方式后的80版本導出密碼的方式


Contact me: kinnisoy@gamil.com

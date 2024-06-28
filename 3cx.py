import pyperclip
import json
import os
import rumps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import subprocess
import threading

# URL of the 3CX web client
url = 'https://pegasoft-gmbh.on3cx.de:5001'

# Configuration file path
config_path = 'config.json'

def load_config():
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            return json.load(file)
    else:
        return {"username": "", "password": ""}

def save_config(config):
    with open(config_path, 'w') as file:
        json.dump(config, file)

def get_user_input(prompt):
    script = f'''
    set T to text returned of (display dialog "{prompt}" default answer "" with icon note buttons {{"OK"}} default button "OK")
    return T
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()

def get_password_input(prompt):
    script = f'''
    set T to text returned of (display dialog "{prompt}" default answer "" with hidden answer with icon note buttons {{"OK"}} default button "OK")
    return T
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()

def show_error_popup(message):
    script = f'''
    display dialog "{message}" with icon stop buttons {{"OK"}} default button "OK"
    '''
    subprocess.run(['osascript', '-e', script])

class PhoneMenuBarApp(rumps.App):
    def __init__(self):
        super(PhoneMenuBarApp, self).__init__("☎️")
        self.menu = ["Change Username", "Change Password", "Start Script"]
        self.config = load_config()
        self.username = self.config.get('username', '')
        self.password = self.config.get('password', '')

    @rumps.clicked("Change Username")
    def change_username(self, _):
        self.username = get_user_input("Enter your username:")
        self.config['username'] = self.username
        save_config(self.config)

    @rumps.clicked("Change Password")
    def change_password(self, _):
        self.password = get_password_input("Enter your password:")
        self.config['password'] = self.password
        save_config(self.config)

    @rumps.clicked("Start Script")
    def start_script(self, _):
        threading.Thread(target=run_script, args=(self.username, self.password)).start()

def run_script(username, password):
    try:
        options = webdriver.ChromeOptions()
        options.binary_location = '/path/to/chromedriver'  # Update the path to chromedriver

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        time.sleep(5)

        username_input = driver.find_element(By.ID, 'loginInput')
        password_input = driver.find_element(By.ID, 'passwordInput')

        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        time.sleep(10)

        dial_box = driver.find_element(By.ID, 'dialpad-input')

        try:
            while True:
                clipboard_content = pyperclip.paste()

                if clipboard_content.startswith('tel:'):
                    telephone_number = clipboard_content[4:]
                    dial_box.clear()
                    dial_box.send_keys(telephone_number)
                    pyperclip.copy('')

                time.sleep(1)
        finally:
            driver.quit()

    except Exception as e:
        show_error_popup(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    PhoneMenuBarApp().run()

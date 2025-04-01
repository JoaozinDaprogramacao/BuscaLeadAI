import os
import pickle
from selenium import webdriver

class WhatsappSession:
    def __init__(self):
        self.session_file = 'whatsapp_session.pkl'
        
    def save_session(self, driver):
        session_data = {
            'cookies': driver.get_cookies(),
            'local_storage': driver.execute_script('return Object.assign({}, window.localStorage);')
        }
        with open(self.session_file, 'wb') as f:
            pickle.dump(session_data, f)
            
    def load_session(self, driver):
        if not os.path.exists(self.session_file):
            return False
            
        with open(self.session_file, 'rb') as f:
            session_data = pickle.load(f)
            
        for cookie in session_data['cookies']:
            driver.add_cookie(cookie)
            
        for key, value in session_data['local_storage'].items():
            driver.execute_script(f"window.localStorage.setItem('{key}', '{value}')")
            
        return True 
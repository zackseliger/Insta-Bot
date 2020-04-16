from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from ImagePost import ImagePost
import time
import os
import pickle

class Bot():
	def __init__(self):
		#open up browser as a mobile device
		self.USER_AGENT = "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
		mobile_emulation = {
			"deviceMetrics": {
				"width": 360,
				"height": 640,
				"pixelRatio": 3.0
			},
			"userAgent": self.USER_AGENT
		}
		self.chrome_options = Options()
		self.chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
		self.chrome_options.add_experimental_option("detach", True)
		self.chrome_options.add_argument("window-size=360,900")
		
		self.accounts = []
		
	def addAccount(self, acc):
		self.accounts.append(acc)
	
	#removes the account 'acc' from list
	def removeAccount(self, acc):
		self.accounts.remove(acc)

	def start(self, **kwargs):
		#keyword arguments
		for key, value in kwargs.items():
			if key == "headless" and value:
				self.chrome_options.add_argument("--headless")
		
		#start webdriver
		self.browser = webdriver.Chrome(options = self.chrome_options)
		self.browser.implicitly_wait(10)

	def end(self):
		#close the webdriver
		self.browser.quit()

	def signIn(self):
		self.browser.get("https://www.instagram.com/accounts/login")

		if os.path.isfile(self.cookiesPath):
			self.load_cookies(self.cookiesPath)
			self.browser.get("https://www.instagram.com")
		else:
			#gets email/password input and inputs username/password
			emailInput = self.browser.find_elements_by_css_selector('form input')[0]
			passwordInput = self.browser.find_elements_by_css_selector('form input')[1]
			emailInput.send_keys(self.username)
			passwordInput.send_keys(self.password)
			#press enter
			passwordInput.send_keys(Keys.ENTER)
			#wait and save cookies
			time.sleep(3)
			self.save_cookies(self.cookiesPath)

	def deleteCookies(self):
		try:
			os.remove(self.cookiesPath)
		except e:
			print("couldn't remove cookies")

	def save_cookies(self, path):
		self.browser.execute_script('console.log(document.cookie);')
		with open(path, 'wb') as filehandler:
			pickle.dump(self.browser.get_cookies(), filehandler)

	def load_cookies(self, path):
		with open(path, 'rb') as cookiesfile:
			cookies = pickle.load(cookiesfile)
			for cookie in cookies:
				if 'expiry' in cookie:
					del cookie['expiry']
				self.browser.add_cookie(cookie)
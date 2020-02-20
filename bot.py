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
import json

class Bot():
	def __init__(self, filepath):
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

		#read information from file
		file = open(filepath, "r")
		lines = file.readlines()
		file.close()

		#username and password and file paths
		accountInfo = self.getParams(lines, "ACCOUNT")
		self.username = accountInfo[0]
		self.password = accountInfo[1]
		self.filepath = filepath
		self.cookiesPath = os.path.dirname(filepath)+"/"+self.username+".ck"

		#get hashtags
		self.hashtags = self.getParams(lines, "HASHTAGS")

		#general options
		options = self.getParams(lines, "OPTIONS")
		self.options = {}
		self.options['headless'] = True if int(options[0]) else False
		self.options['interval'] = float(options[1])
		self.options['toFollow'] = int(options[2].split()[0])
		self.options['toUnfollow'] = int(options[2].split()[1])

		#images
		self.images = []
		imageDict = self.getJson(lines, "IMAGES")
		for image in imageDict:
			self.images.append(ImagePost(image['path'], image['caption']))

	def getParams(self, lines, header):
		res = []
		for i in range(0,len(lines)):
			if lines[i].upper().strip() == header.upper():
				j = i+1
				while j < len(lines) and lines[j].strip():
					res.append(lines[j].strip())
					j += 1
				break
		return res

	def getJson(self, lines, header):
		res = []
		for i in range(0, len(lines)):
			if lines[i].upper().strip() == header.upper():
				res = json.loads(lines[i+1].strip())
				break
		return res


	def start(self, **kwargs):
		#keyword arguments
		for key, value in kwargs.items():
			if key == "headless" and value:
				self.chrome_options.add_argument("--headless")
		
		#start webdriver
		self.browser = webdriver.Chrome(options = self.chrome_options)

	def end(self):
		#close the webdriver
		self.browser.quit()

	def signIn(self):
		self.browser.get("https://www.instagram.com/accounts/login")
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'form input')))

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

	def getFollowersOf(self, username):
		self.browser.get("https://www.instagram.com/"+username)
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul li a')))
		followersLink = self.browser.find_element_by_css_selector('ul li a')
		try:
			followersLink.click()
		except:
			print("private account")
			return []

		#get the list of users there
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul div li')))
		followerDivs = self.browser.find_elements_by_css_selector('ul div li')
		followers = []
		for follower in followerDivs:
			try:
				followers.append(follower.find_elements_by_css_selector('div a')[1].text)
			except:
				pass
		return followers

	def getFollowing(self, username):
		self.browser.get("https://www.instagram.com/"+username)
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul li a')))
		links = self.browser.find_elements_by_css_selector('ul li a')
		try:
			links[1].click()
		except:
			print("private account")
			return []

		#get the list of users there
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul div li')))
		followingDivs = self.browser.find_elements_by_css_selector('ul div li')
		followings = []
		for following in followingDivs:
			try:
				followings.append(following.find_elements_by_css_selector('div a')[1].text)
			except:
				pass
		return followings

	def followUser(self, username):
		self.browser.get("https://www.instagram.com/"+username)
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button')))

		#figure out if it's a public or private account
		buttonIndex = 1
		if len(self.browser.find_elements_by_css_selector('span button')) == 0:
			buttonIndex = 2
		followButton = self.browser.find_elements_by_css_selector('button')[buttonIndex]#1 if public 2 if private
		#click follow if we're not already following
		try:
			if followButton.value_of_css_property("color") == "rgba(255, 255, 255, 1)":
				followButton.click()
		except:
			print("couldn't follower a user. Skipping...")

	def unfollowUser(self, username):
		self.browser.get("https://www.instagram.com/"+username)
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button')))
		unFollowButton = self.browser.find_elements_by_css_selector('button')[2]

		#click unfollow if we're not already unfollowed
		if unFollowButton.value_of_css_property("color") != "rgba(255, 255, 255, 1)":
			unFollowButton.click()
			confirmButton = self.browser.find_elements_by_css_selector('div button')[-2]
			confirmButton.click()

	def postImage(self, path, caption=""):
		self.browser.get("https://www.instagram.com/"+self.username)
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div div div')))
		uploadButton = self.browser.find_elements_by_css_selector('div div div[tabindex="0"]')[0]

		#click upload button because instagram makes us, but add an event which cancels the event
		self.browser.execute_script('document.addEventListener("click", function(e) {e.preventDefault();},{once:true});')
		uploadButton.click()

		#puts our file down
		input = self.browser.find_elements_by_css_selector('input[type="file"]')
		input[0].send_keys(path)

		#make sure meme is fullscreen or whatever and hit next
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button span')))
		time.sleep(0.1)
		spans = self.browser.find_elements_by_css_selector('button span')
		if len(spans) > 1:
			spans[0].click()

		#hit next, fill out caption, and post
		self.browser.execute_script('document.getElementsByTagName("button")[1].click();')
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea')))
		textarea = self.browser.find_element_by_css_selector('textarea')
		textarea.send_keys(caption)
		self.browser.execute_script('document.getElementsByTagName("button")[1].click();')

	def getHashtagPosts(self, hashtag):
		self.browser.get("https://www.instagram.com/explore/tags/"+hashtag)
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a div div img')))
		links = self.browser.find_elements_by_css_selector('a')
		res = []
		for link in links:
			if link.get_attribute('href').find('/p/') != -1:
				res.append(link.get_attribute('href'))
		return res

	def getPostId(self, postUrl):
		return postUrl[postUrl.find('/p/')+3:-1]

	def getPosterOf(self, postId):
		self.browser.get('https://www.instagram.com/p/'+postId+'/')
		WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div a')))
		poster = self.browser.find_elements_by_css_selector('div a')
		return poster[1].text

	def setOptions(self, options):
		if 'headless' in options:
			self.options['headless'] = options['headless']
		if 'interval' in options:
			self.options['interval'] = options['interval']
		if 'toFollow' in options:
			self.options['toFollow'] = options['toFollow']
		if 'toUnfollow' in options:
			self.options['toUnfollow'] = options['toUnfollow']

	def save(self):
		file = open(self.filepath, "w")
		file.write("ACCOUNT\n")
		file.write(self.username+"\n")
		file.write(self.password+"\n\n")

		file.write("OPTIONS\n")
		if self.options['headless']: file.write("1\n")
		else: file.write("0\n")
		file.write(str(self.options['interval'])+"\n")
		file.write(str(self.options['toFollow'])+" "+str(self.options['toUnfollow'])+"\n\n")

		file.write("HASHTAGS\n")
		for hashtag in self.hashtags:
			file.write(hashtag+"\n")

		file.write("\nIMAGES\n")
		#convert all ImagePosts to dictionaries
		imageDict = []
		for image in self.images:
			imageDict.append(image.__dict__)
		file.write(json.dumps(imageDict))
		file.close()

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
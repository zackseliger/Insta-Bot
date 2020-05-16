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

class InstaBrowser():
	def __init__(self):
		#open up browser as a mobile device
		self.USER_AGENT = "Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 Mobile Safari/537.36"
		self.options = webdriver.FirefoxOptions()
		self.options.add_argument("--width=405")
		self.options.add_argument("--height=720")
	
	# create and open the webdriver
	def start(self):
		self.profile = webdriver.FirefoxProfile()
		self.profile.set_preference("general.useragent.override", self.USER_AGENT)
		#start webdriver
		self.browser = webdriver.Firefox(self.profile, firefox_options = self.options)
		self.browser.implicitly_wait(10)

	# close the webdriver
	def end(self):
		self.browser.quit()

	# clears all cookies
	def clear_cookies(self):
		self.browser.delete_all_cookies()

	# saves cookies to a path
	def save_cookies(self, path):
		self.browser.execute_script('console.log(document.cookie);')
		with open(path, 'wb') as filehandler:
			pickle.dump(self.browser.get_cookies(), filehandler)

	# loads cookies from a path
	def load_cookies(self, path):
		with open(path, 'rb') as cookiesfile:
			cookies = pickle.load(cookiesfile)
			for cookie in cookies:
				if 'expiry' in cookie:
					del cookie['expiry']
				self.browser.add_cookie(cookie)

	# get usernames of people following this username
	def getFollowersOf(self, username):
		self.browser.get("https://www.instagram.com/"+username)
		links = self.browser.find_elements_by_css_selector('ul li a')
		try:
			links[1].click()
		except:
			print("not an account")
			return []

		#get the list of users there
		time.sleep(1)
		self.browser.execute_script('window.scrollBy(0,250);')
		followingDivs = self.browser.find_elements_by_css_selector('ul div li')
		followings = []
		for following in followingDivs:
			try:
				followings.append(following.find_elements_by_css_selector('div a')[1].text)
			except:
				pass
		return followings

	# unfollowers users from the account of the logged in user
	def unfollowUsersFromList(self, username, num):
		self.browser.get("https://www.instagram.com/"+username)
		self.browser.execute_script("a=document.getElementsByTagName('a');for(let i=0;i<a.length;i++)if(a[i].href&&a[i].href.indexOf('/following')!==-1)a[i].click();")
		time.sleep(1)
		self.browser.execute_script('window.scrollBy(0,250);')
		time.sleep(1)
		self.browser.execute_script("(async function(){d=document.getElementsByTagName.bind(document);a=d('button');nu=0;for(let i=0;i<a.length&&nu<"+str(num)+";i++){if(a[i].innerHTML=='Following'){a[i].click();b=d('button');for(let j=b.length-1;j>=0;j--) {if (b[j].innerHTML=='Unfollow'){b[j].click();await new Promise(r=>setTimeout(r,1000));nu++;break;}}}}})();")
		time.sleep(1)
	
	# follow users from the account of the given username
	def followUsersFromList(self, username, num):
		self.browser.get("https://www.instagram.com/"+username)
		self.browser.execute_script("a=document.getElementsByTagName('a');for(let i=0;i<a.length;i++)if(a[i].href&&a[i].href.indexOf('/followers')!==-1)a[i].click();")
		time.sleep(1)
		self.browser.execute_script('window.scrollBy(0,250);')
		time.sleep(1)
		self.browser.execute_script("(async function(){a=document.getElementsByTagName('button');nu=0;for(let i=0;i<a.length&&nu<"+str(num)+";i++){if(a[i].innerHTML=='Follow'){a[i].click();nu++;await new Promise(r=>setTimeout(r,1000));}}})();")
		time.sleep(1)

	# follow a user with the given username
	# returns: True if followed, False if not (non-existent account or already following or something else)
	def followUser(self, username):
		self.browser.get("https://www.instagram.com/"+username)

		#figure out if it's a public or private account
		buttonIndex = 1
		self.browser.implicitly_wait(0)
		if len(self.browser.find_elements_by_css_selector('span button')) == 0:
			buttonIndex = 2
		followButton = self.browser.find_elements_by_css_selector('button')[buttonIndex]#1 if public 2 if private
		self.browser.implicitly_wait(10)#turn off implicit waits then back on

		#click follow if we're not already following
		if followButton.value_of_css_property("color") == "rgba(255, 255, 255, 1)":
			followButton.click()
			return True
		
		return False

	# unfollow a user with the given username
	# returns: True if unfollowed, False if not (non-existent account or already not following)
	def unfollowUser(self, username):
		self.browser.get("https://www.instagram.com/"+username)
		unFollowButton = self.browser.find_elements_by_css_selector('button')[2]

		#click unfollow if we're not already unfollowed
		if unFollowButton.value_of_css_property("color") != "rgba(255, 255, 255, 1)":
			unFollowButton.click()
			confirmButton = self.browser.find_elements_by_css_selector('div button')[-2]
			confirmButton.click()
			return True
		
		return False

	# posts an image at the given path, with an optional caption
	def postImage(self, account, path, caption=""):
		self.browser.get("https://www.instagram.com/"+account.username)
		uploadButton = self.browser.find_elements_by_css_selector('div div div[tabindex="0"]')[0]

		#click upload button because instagram makes us, but add an event which cancels the event
		self.browser.execute_script('document.addEventListener("click", function(e) {e.preventDefault();},{once:true});')
		uploadButton.click()
		
		time.sleep(1)

		#puts our file down
		input = self.browser.find_elements_by_css_selector('input[type="file"]')
		input[0].send_keys(path)
		
		time.sleep(1)

		#make sure meme is fullscreen or whatever and hit next
		time.sleep(0.1)
		spans = self.browser.find_elements_by_css_selector('button span')
		if len(spans) > 1:
			spans[0].click()

		#hit next, fill out caption, and post
		self.browser.execute_script('document.getElementsByTagName("button")[1].click();')
		textarea = self.browser.find_element_by_css_selector('textarea')
		textarea.send_keys(caption)
		self.browser.execute_script('document.getElementsByTagName("button")[1].click();')

	# given the url of a post, get the id of that post
	def getPostId(self, postUrl):
		return postUrl[postUrl.find('/p/')+3:-1]

	# get posts at the hashtag. OCCASIONALLY GETS NON-POSTS
	def getHashtagPosts(self, hashtag):
		self.browser.get("https://www.instagram.com/explore/tags/"+hashtag)
		links = self.browser.find_elements_by_css_selector('a')
		res = []
		for link in links:
			if link.get_attribute('href').find('/p/') != -1:
				res.append(self.getPostId(link.get_attribute('href')))
		return res

	# gets the username of the poster given a post
	def getPosterOf(self, postId):
		self.browser.get('https://www.instagram.com/p/'+postId+'/')
		posterUrl = self.browser.find_element_by_css_selector('a').get_attribute('href')
		return posterUrl[posterUrl.find("instagram.com/")+14:-1]

	# sign an account in and save cookies
	def signIn(self, acc):
		self.clear_cookies()
		self.browser.get("https://www.instagram.com/accounts/login")

		if os.path.isfile(acc.cookiesPath):
			self.load_cookies(acc.cookiesPath)
			self.browser.get("https://www.instagram.com")
		else:
			#gets email/password input and inputs username/password
			emailInput = self.browser.find_elements_by_css_selector('form input')[0]
			passwordInput = self.browser.find_elements_by_css_selector('form input')[1]
			emailInput.send_keys(acc.username)
			passwordInput.send_keys(acc.password)
			#press enter
			passwordInput.send_keys(Keys.ENTER)
			#wait and save cookies
			time.sleep(3)
			self.save_cookies(acc.cookiesPath)
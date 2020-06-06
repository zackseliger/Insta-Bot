from InstaBrowser import InstaBrowser
from Account import Account
import os
import random
from reddit_scraper import save_top_images
from threading import Timer
import traceback
from time import sleep

class Manager():
	def __init__(self):
		self.accounts = []
		self.browser = InstaBrowser()
		self.accountQueue = []
		self.timer = None
		
	def addAccount(self, acc):
		self.accounts.append(acc)
	
	#removes the account 'acc' from list
	def removeAccount(self, acc):
		self.accounts.remove(acc)

	# adds all the accounts it finds in a folder
	def addAccountsFrom(self, path):
		files = os.listdir(path)
		for filename in files:
			if filename[filename.rfind('.'):] == '.acc':
				self.addAccount(Account(path+"/"+filename))

	# unfollow people according to the account's settings
	def unfollowUsers(self, account):
		numUnfollowed = 0
		self.browser.unfollowUsersFromList(account.username, account.options['toUnfollow'])

	# follow people according to the account's settings
	def followUsers(self, account):
		posts = self.browser.getHashtagPosts(random.choice(account.hashtags)) 
		peopleToFollow = []
		numFollowed = 0
		numFollowPerUser = int(account.options['toFollow']/4)

		while numFollowed < account.options['toFollow']:
			# get a new post if we're out
			if len(posts) == 0:
				posts = self.browser.getHashtagPosts(random.choice(account.hashtags))
				random.shuffle(posts)
			
			# follow 'numFollowPerUser' people from this guy
			post = posts.pop(0)
			# sleep(1)
			self.browser.followUsersFromLikeList(post, numFollowPerUser)
			numFollowed += numFollowPerUser
			sleep(2)

	# post an image if we have any queued
	def postImage(self, account):
		if len(account.images) > 0:
				self.browser.postImage(account, account.images[0].path, account.images[0].caption)
				image = account.images.pop(0)
				
				# delete image file and save to account
				os.remove(image.path)

	# gets new images if sources are defined
	def getImages(self, account):
		if len(account.sources) == 0: return

		source = random.choice(account.sources)
		filePaths = save_top_images(source, "posts/"+account.username+"/")

		for filepath in filePaths:
			caption = ""
			# add 5-8 random hashtags from 'postHashtags' to post
			if len(account.postHashtags) > 0:
				caption += "-\n-\n"
				random.shuffle(account.postHashtags)
				numTags = 5+random.random()*4
				for i in range(int(numTags)):
					caption += "#"+account.postHashtags[i]
					if i+1 < int(numTags): caption += " "

			# add post and caption to account
			account.addPost(filepath, caption)

	def openAccount(self, account):
		self.browser.start()
		self.browser.signIn(account)

	def runAccount(self, account) :
		# start browser and sign in
		self.browser.start()
		self.browser.signIn(account)

		# unfollow uers, follow new users, and post an image
		if len(account.images) == 0:
			self.getImages(account)
		self.postImage(account)
		sleep(10)
		self.unfollowUsers(account)
		self.followUsers(account)

		# save account and cookies and close
		account.save()
		self.browser.save_cookies(account.cookiesPath)
		self.browser.end()

	def runAccounts(self):
		# reset variables
		if self.timer is not None:
			self.timer.cancel()
		self.accountQueue = []

		# add accounts to queue and start
		for account in self.accounts:
			self.accountQueue.append(account)
		self.timer = Timer(0, lambda: handleAccountQueue(self))
		self.timer.start()

# this is seperate from manager. This is like the 'main loop' for it
def handleAccountQueue(manager):
	# get account
	acc = None
	if len(manager.accountQueue) > 0:
			acc = manager.accountQueue.pop(0)

	# try to run the account
	try:
		if acc is not None:
			manager.runAccount(acc)
	except Exception as error:
		# save stuff and close the browser
		acc.save()
		manager.browser.end()

		# print error
		print(traceback.format_exc())
		print("We were unable to run account "+acc.username)
	
	# set timer to add account to queue again
	if acc is not None:
		t = Timer(acc.options['interval']*3600, lambda: manager.accountQueue.append(acc))
		t.start()

	# set timer to call handleAccountQueue again (in 30 seconds)
	manager.timer = Timer(30, lambda: handleAccountQueue(manager))
	manager.timer.start()

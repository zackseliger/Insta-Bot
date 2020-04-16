from InstaBrowser import InstaBrowser
from Account import Account
import os
import random
from reddit_scraper import save_top_images

class Manager():
	def __init__(self):
		self.accounts = []
		self.browser = InstaBrowser()
		
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
		followingUs = self.browser.getFollowersOf(account.username)
		while numUnfollowed < account.options['toUnfollow']:
			# since 'getFollowersOf' only gets 30 or so users at a time
			if len(followingUs) == 0:
				followingUs = self.browser.getFollowersOf(account.username)
			# unfollow
			if self.browser.unfollowUser(followingUs.pop(0)) == True:
				numUnfollowed += 1

	# follow people according to the account's settings
	def followUsers(self, account):
		posts = self.browser.getHashtagPosts(random.choice(account.hashtags))
		peopleToFollow = []
		numFollowed = 0
		while numFollowed < account.options['toFollow']:
			# get a new post if we're out
			if len(posts) == 0:
				posts = self.browser.getHashtagPosts(random.choice(account.hashtags))
			
			# get a new person's followers if we're out of people to follow
			while len(peopleToFollow) == 0:
				post = posts.pop(0)
				poster = self.browser.getPosterOf(post)
				peopleToFollow = self.browser.getFollowersOf(poster)
			
			# follow
			person = peopleToFollow.pop(0)
			self.browser.followUser(person)

	# post an image if we have any queued
	def postImage(self, account):
		if len(account.images) > 0:
				self.browser.postImage(account, account.images[0].path, account.images[0].caption)
				image = account.images.pop(0)
				
				# delete image file and save to account
				os.remove(image.path)
				account.save()

	def runAccounts(self):
		self.browser.start()
		for account in self.accounts:
			# sign in
			self.browser.signIn(account)

			# unfollow uers, follow new users, and post an image
			self.unfollowUsers(account)
			self.followUsers(account)
			self.postImage(account)
			
			# save cookies
			self.browser.save_cookies(account.cookiesPath)

		# close browser
		self.browser.end()


manager = Manager()
manager.addAccountsFrom('accounts')

manager.runAccounts()
from bot import Bot
from threading import Timer
from ImagePost import ImagePost
import tkinter as tk
import tkinter.filedialog
import tkinter.simpledialog
import time
import random
import os

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		self.pack()
		self.create_widgets()
		self.filename = ""

		#bot runtime stuff
		self.bot = -1
		self.botTimer = -1
		self.currHashtag = 0
	
	def create_widgets(self):
		self.optionsLabel = tk.Label(self, text="General Options")
		self.headlessLabel = tk.Label(self, text="Headless Browser:")
		self.headlessVar = tk.IntVar()
		self.headlessCheckbox = tk.Checkbutton(self, variable=self.headlessVar)
		self.intervalLabel = tk.Label(self, text="Interval (hours):")
		self.intervalEntry = tk.Entry(self)
		self.fileButton = tk.Button(self, text="Get File", command=self.getFile)
		self.startButton = tk.Button(self, text="Start", command=self.startBot)
		self.saveButton = tk.Button(self, text="Save", command=self.saveBot)
		self.openButton = tk.Button(self, text="Open Account", command=self.openAccount)

		self.followOptionsLabel = tk.Label(self, text="Follow/Unfollow Options")
		self.followLabel = tk.Label(self, text="# to Follow:")
		self.followEntry = tk.Entry(self)
		self.unfollowLabel = tk.Label(self, text="# to Unfollow:")
		self.unfollowEntry = tk.Entry(self)

		self.imagesLabel = tk.Label(self, text="Images")
		self.addImageButton = tk.Button(self, text="Add", command=self.addImage)
		self.removeImageButton = tk.Button(self, text="Remove", command=self.removeImage)
		self.imagesText = tk.Text(self, height=4, width=30, highlightbackground="#222")

		self.optionsLabel.grid(row=0, column=0, columnspan=2)
		self.headlessLabel.grid(row=1, column=0)
		self.headlessCheckbox.grid(row=1, column=1)
		self.intervalLabel.grid(row=2, column=0)
		self.intervalEntry.grid(row=2, column=1)
		self.fileButton.grid(row=3, column=0)
		self.startButton.grid(row=3, column=1)
		self.saveButton.grid(row=4, column=0)
		self.openButton.grid(row=4, column=1)

		self.followOptionsLabel.grid(row=0, column=3, columnspan=2)
		self.followLabel.grid(row=1, column=3)
		self.followEntry.grid(row=1, column=4)
		self.unfollowLabel.grid(row=2, column=3)
		self.unfollowEntry.grid(row=2, column=4)

		self.imagesLabel.grid(row=0, column=5, columnspan=2)
		self.addImageButton.grid(row=1, column=5)
		self.removeImageButton.grid(row=1, column=6)
		self.imagesText.grid(row=2, column=5, columnspan=2)

	def updateImageText(self):
		result = ""
		for i in range(0, len(self.bot.images)):
			result += str(i+1)+". "+os.path.basename(self.bot.images[i].path)+"\n"
		#put text to entry
		self.imagesText.delete("1.0", tk.END)
		self.imagesText.insert("1.0", result)

	def addImage(self):
		file = tkinter.filedialog.askopenfile()
		if file:
			caption = tkinter.simpledialog.askstring("Caption", "What should the caption be?")
			self.bot.images.append(ImagePost(file.name, caption))

			#update images text
			self.updateImageText()

	def removeImage(self):
		index = tkinter.simpledialog.askinteger("Index", "Which number image should be removed?")
		try:
			self.bot.images.pop(index-1)
		except:
			print("error removing image at index "+str(index-1))
		
		#gotta update image text
		self.updateImageText()

	def openAccount(self):
		if self.bot:
			self.bot.start()
			self.bot.signIn()

	def getFile(self):
		file = tkinter.filedialog.askopenfile()
		if file:
			self.filename = file.name
			self.bot = Bot(self.filename)

			#clear text on entries
			self.intervalEntry.delete(0, tk.END)
			self.followEntry.delete(0, tk.END)
			self.unfollowEntry.delete(0, tk.END)

			#set entries
			self.headlessCheckbox.select() if self.bot.options['headless'] else self.headlessCheckbox.deselect()
			self.intervalEntry.insert(0, self.bot.options['interval'])
			self.followEntry.insert(0, self.bot.options['toFollow'])
			self.unfollowEntry.insert(0, self.bot.options['toUnfollow'])

			#image text
			self.updateImageText()

	def updateOptions(self):
		options = {}
		options['headless'] = True if self.headlessVar.get() else False
		options['interval'] = float(self.intervalEntry.get())
		options['toFollow'] = int(self.followEntry.get())
		options['toUnfollow'] = int(self.unfollowEntry.get())
		self.bot.setOptions(options)

	#should unfollow, follow, post picture if available, then re-queue for next interval
	def runBot(self):
		#variables
		numUnfollowed = 0
		shouldUnfollow = self.bot.options['toUnfollow']
		numFollowed = 0
		shouldFollow = self.bot.options['toFollow']

		#start bot and wait 2 secs to make sure everything loaded
		self.bot.start(headless=self.headlessVar.get())
		self.bot.signIn()
		time.sleep(2)

		#unfollow some people we're following
		ourFollowing = self.bot.getFollowing(self.bot.username)
		for following in ourFollowing:
			self.bot.unfollowUser(following)
			numUnfollowed += 1
			if numUnfollowed >= shouldUnfollow:
				break
		
		#follow people off of a hashtag
		posts = self.bot.getHashtagPosts(self.bot.hashtags[self.currHashtag])
		self.currHashtag += 1
		if self.currHashtag >= len(self.bot.hashtags):
			self.currHashtag = 0
		for post in posts:
			poster = self.bot.getPosterOf(self.bot.getPostId(post))
			followers = self.bot.getFollowersOf(poster)
			#follow followers of the people that posted the post ^
			for follower in followers:
				self.bot.followUser(follower)
				numFollowed += 1
				if numFollowed >= shouldFollow:
					break
			if numFollowed >= shouldFollow:
				break

		#post image if there's one in the array
		if len(self.bot.images) > 0:
			self.bot.postImage(self.bot.images[0].path, self.bot.images[0].caption)
			self.bot.images.pop(0)
			self.updateImageText()

		#save cookies, close browser
		time.sleep(1)
		self.bot.save_cookies(self.bot.cookiesPath)
		time.sleep(2)
		self.bot.end()
		self.bot.save()

		#re-queue in 'interval' time
		self.botTimer = Timer(self.bot.options['interval']*3600, self.runBot)
		self.botTimer.start()
		
	def postImage(self):
		#start bot and wait 2 secs to make sure everything loaded
		self.bot.start(headless=self.headlessVar.get())
		self.bot.signIn()
		time.sleep(2)
		
		#post image if there's one in the array
		if len(self.bot.images) > 0:
			self.bot.postImage(self.bot.images[0].path, self.bot.images[0].caption)
			self.bot.images.pop(0)
			self.updateImageText()

	def startBot(self):
		self.updateOptions()
		self.botTimer = Timer(1, self.runBot)
		self.botTimer.start()

	def saveBot(self):
		self.updateOptions()
		self.bot.save()

#create root and our thing
root = tk.Tk()
root.title("Instagram Bot")
app = Application(master=root)

#adding listeners for gracefully exiting
def on_close_default():
	if app.botTimer != -1:
		app.botTimer.cancel()
	root.destroy()
def on_close_key(e):
	on_close_default()
root.protocol("WM_DELETE_WINDOW", on_close_default)
root.bind("<Escape>", on_close_key)

#start
root.mainloop()
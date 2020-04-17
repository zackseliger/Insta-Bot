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

class Account():
	def __init__(self, filepath):
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
		self.options['interval'] = float(options[1])
		self.options['toFollow'] = int(options[2].split()[0])
		self.options['toUnfollow'] = int(options[2].split()[1])

		# sources for content
		self.sources = self.getParams(lines, "SOURCES")

		# haghtags to use with our posts
		self.postHashtags = self.getParams(lines, "POST_HASHTAGS")

		#images
		self.images = []
		imageDict = self.getJson(lines, "IMAGES")
		for image in imageDict:
			self.addPost(image['path'], image['caption'])

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

	def addPost(self, path, caption=""):
		self.images.append(ImagePost(path, caption))

	def setOptions(self, options):
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
		file.write("0\n")# TODO: I'm writing 0 so that it's headless, this should be totally removed and headless should be a property of the manager
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

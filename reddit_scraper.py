import requests
from html.parser import HTMLParser
import random
import string
import os
from get_image_size import get_image_size_from_bytesio
from io import BytesIO

# globals
mac_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:75.0) Gecko/20100101 Firefox/75.0'}

# 32 random ascii characters
def rand_string():
	return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

# get the file extension of a file
def get_ext(path):
	ext_end = path.rfind('?')
	ext = ''

	# different endings based on if there was a question mark at the end
	if ext_end == -1:
		ext = path[path.rfind('.'):]
	else:
		ext = path[path.rfind('.'):ext_end]

	return ext

class MyHTMLParser(HTMLParser):
	def __init__(self, path):
		HTMLParser.__init__(self)
		self.path = path
		self.filePaths = []

		# create directory if it doesn't exist
		if not os.path.exists(self.path):
			os.makedirs(self.path)

	def handle_starttag(self, tag, attrs):
		if tag == 'img':
			src = ''
			# look for src
			for attr in attrs:
				if attr[0] == 'src':
					src = attr[1]
					break
			
			# make sure this is a post image
			if src != '' and "://preview.redd.it" in src and src.count('/') == 3:
				# get image and save to /posts
				src = src.replace('preview.redd.it', 'i.redd.it')
				page = requests.get(src, headers=mac_headers)
				
				# get image size. We only save if it's aspect ratio fits instagram (y:x ratio less than 5:4)
				# also width has to be smaller than 2:1
				size = get_image_size_from_bytesio(BytesIO(page.content), len(page.content))
				if size[1]/size[0] <= 5/4 and size[0]/size[1] <= 2:
					filepath = self.path+rand_string()+get_ext(src)
					f = open(filepath, 'wb')
					f.write(page.content)
					self.filePaths.append(os.getcwd()+"/"+filepath)

def save_top_images(subreddit, path='posts/'):
	parser = MyHTMLParser(path)
	page = requests.get('https://reddit.com/r/'+subreddit+'/top', headers=mac_headers)
	parser.feed(page.text)
	return parser.filePaths
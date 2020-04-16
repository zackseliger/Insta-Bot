import requests
from html.parser import HTMLParser
import random
import string

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
				page = requests.get(src, headers=mac_headers)
				f = open('posts/'+rand_string()+get_ext(src), 'wb')
				f.write(page.content)

def save_top_images(subreddit):
	parser = MyHTMLParser()
	page = requests.get('https://reddit.com/r/'+subreddit+'/top', headers=mac_headers)
	parser.feed(page.text)

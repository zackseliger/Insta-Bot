from Account import Account
from time import sleep
from random import random
import pickle
import json
import requests

headers_get={}
headers_get["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
headers_get["Accept-Encoding"] = "gzip, deflate, br"
headers_get["Accept-Language"] = "en-US,en;q=0.5"
headers_get["Connection"] = "keep-alive"

headers_post={}
headers_post["Accept"] = "*/*"
headers_post["Accept-Encoding"] = "gzip, deflate, br"
headers_post["Accept-Language"] = "en-US,en;q=0.5"
headers_post["Connection"] = "keep-alive"
headers_post["Host"] = "www.instagram.com"
headers_post["Origin"] = "https://www.instagram.com"
headers_post["Referer"] = "https://www.instagram.com/accounts/activity/?followRequests=1"
headers_post["TE"] = "Trailers"
headers_post["Content-Length"] = "0"
headers_post["Content-Type"] = "application/x-www-form-urlencoded"
headers_post["X-Requested-With"] = "XMLHttpRequest"
headers_post["X-Instagram-AJAX"] = "62d0c4ff7fec"
headers_post["X-IG-WWW-CLAIM"] = "0"
headers_post["X-IG-App-ID"] = "1217981644879628"


cookies = {}
def update_cookies(cookie_dict):
	for cookie_name in cookie_dict:
		cookies[cookie_name] = cookie_dict[cookie_name]
		if cookie_name == "csrftoken":
			headers_post["X-CSRFToken"] = cookie_dict[cookie_name]

# cookies initialization
test_acc = Account("accounts/super_burner69.acc")
cookiesPickle = pickle.load(open(test_acc.cookiesPath, "rb"))
for cookie in cookiesPickle:
	cookies[cookie['name']] = cookie['value']

# get any follow requests that we have
while True:
	res = requests.get('https://www.instagram.com/accounts/activity/?__a=1', headers=headers_get, cookies=cookies)
	update_cookies(dict(res.cookies))
	requests_array = json.loads(res.text)['graphql']['user']['edge_follow_requests']['edges']
	for request in requests_array:
		res = requests.post('https://www.instagram.com/web/friendships/'+request['node']['id']+'/approve/', headers=headers_post, cookies=cookies)
		try:
			headers_post["X-IG-WWW-Claim"] = res.headers["x-ig-set-www-claim"]
		except:
			print("no set-www-claim header present")
		print(len(res.text))
		if len(res.text) < 2000:
			print(res.text)
		sleep(0.05+random()*0.05)
		if len(requests_array) == 0:
			sleep(0.5)

# f = open("test2.html", "w")
# f.write(res.text)
# f.close()

# with open(test_acc.cookiesPath, 'rb') as file:
# 	fileContent = file.read()
# 	# print(fileContent)
# 	print(fileContent.decode('utf-8'))

# get data url: https://www.instagram.com/accounts/activity/?__a=1
# accept friendship: https://www.instagram.com/web/friendships/4611357132/approve/

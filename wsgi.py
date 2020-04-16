import os
from bot import Bot
from PIL import Image
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
app = Flask(__name__)

@app.route('/')
def root():
	return "insta"
	
@app.route('/accounts/get')
def getAccounts():
	files = os.listdir('accounts')
	account_files = []
	for filename in files:
		if ".acc" in filename:
			bot = Bot("accounts/"+filename)
			account_files.append(bot.__dict__)
			#serialize image posts
			images = []
			for image in bot.images:
				images.append(image.__dict__)
			account_files[-1]['images'] = images
	return jsonify(account_files)

@app.route('/accounts/add', methods=['POST'])
def addAccount():
	#make sure they gave us everything we NEED
	args = request.args.to_dict()
	required_keys = ["username", "password", "follow", "unfollow", "interval"]
	for key in required_keys:
		if args.get(key) is None:
			return "Incomplete request. Required args: "+str(required_keys)
	
	#see if file already exists
	if os.path.exists("accounts/"+args['username']+".acc"):
		return "Account already exists"

	#make the bot .acc file
	file_data = "ACCOUNT\n"+args['username']+"\n"+args['password']+"\n\n"
	file_data += "OPTIONS\n0\n"+str(args['follow'])+" "+str(args['unfollow'])+"\n\n"
	if args.get('hashtag') is not None:
		file_data += "HASHTAGS\n"+args['hashtag']+"\n\n"
	file = open("accounts/"+args['username']+".acc", "w")
	file.write(file_data)
	file.close()

	return "ok"

@app.route('/posts/add', methods=['POST'])
def addPost():
	#get image and make sure dimensions are ok
	img = request.files['image']
	img.save('posts/'+secure_filename(img.filename)) # save to filesystem first bc pillow messes with it
	pillow_image = Image.open(request.files['image'])
	image_size = pillow_image.size
	if image_size[0] > image_size[1]*2:
		return "image is too wide. Can be at max 2:1"
	if image_size[1]*4 > image_size[0]*5:
		return "image is too tall. Can be at max 4:5"
	
	#make sure account exists and user provided a caption
	form_info = request.form.to_dict()
	bot_name = form_info.get('username')
	caption = form_info.get('caption')
	if caption is None:
		caption = ""
	if bot_name is None:
		return "username is a required field"
	try:
		bot = Bot("accounts/"+bot_name+".acc")
	except:
		return "account with that username does not exist"

	#save to bot with the caption
	bot.addPost(os.getcwd()+"/posts/"+secure_filename(img.filename), caption)
	bot.save()
	return "ok"

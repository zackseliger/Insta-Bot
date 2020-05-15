# Instagram Bot
Python Instagram Bot

## Requirements
Libraries: Selenium, Tkinter (Tkinter part not working right now)
Geckodriver for Selenium

## Setup
I would set aside a folder called 'accounts' for account files. Here is an example of the format:

```
ACCOUNT
<username>
<password>

OPTIONS
<0 or 1, 0=headless, 1=browser>
<interval btwn sessions, in hours>
<# accounts to follow per session> <# accounts to unfollow per session>

HASHTAGS
<hashtag1, without '#'>
<hashtag2>
<etc...>
```

## Running

### main.py
This is the intended way to run the program. Simply run `python main.py` with your .acc (and possibly .ck) files in '/accounts' and it will run the bots automatically.

### Server
If you are putting this program on a VPS, you should run the Flask server so that you can communicate with your program while it is running. To start the flask server run `python -m flask run` and you should be able to go to the server's ip and interact with it like a normal site.

### TKinter notes
This file should be opened via the GUI BEFORE any other action. For many actions, it is assumed that a file has been imported
NOTE 2: If you are having crashing issues when attempting to close the program, you can close it using ESCAPE, which should exit gracefully

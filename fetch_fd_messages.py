import os
from remotezip import RemoteZip
import mechanicalsoup
import re
import yaml

'''
Download the messages.json files from the huge zip archives Flowdock provides.
'''

def load_configuration():
    with open(config_file) as f:
        return yaml.safe_load(f)

config_file = 'config.yml'
config = load_configuration()

# First get a list of URLs from export emails
email_dir = 'input/emails/'
emails = os.listdir(email_dir)
fd_exports = []
for email in emails:
	with open(email_dir + email) as f:
		email_content = f.read()
		regex = r"(https://www.flowdock.com.*)=\n(.*)=\n(.*)\?"
		results = re.findall(regex, email_content)[0]
		url = ''.join(results)
		fd_exports.append(url)

download_dir = 'input/exports'
login_url = 'https://www.flowdock.com/login'
fd_username = config['flowdock_user']
fd_password = config['flowdock_password']

# To download the zip files we need to authenticate
browser = mechanicalsoup.StatefulBrowser()

browser.open(login_url)
login_form = browser.select_form() 

browser['user_session[email]'] = fd_username
browser['user_session[password]'] = fd_password

login_response = browser.submit_selected()
request_headers = login_response.request.headers

flow_name_regex = r"/([a-zA-Z-]+)-2020-"

for fd_export in fd_exports:
	print(fd_export)
	flow_name = re.findall(flow_name_regex, fd_export)[0]
	zip = RemoteZip(fd_export, headers=request_headers)
	messages_file = zip.getinfo('messages.json')
	output_dir = '%s/%s/' % (download_dir, flow_name)
	zip.extract(messages_file, output_dir)


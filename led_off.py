#!/usr/bin/python3

import xml.etree.ElementTree as ET
from urllib import request, parse
import hashlib

# configuration
FRITZBOX_PASSWORD = ''
FRITZBOX_USER = ''
FRITZBOX_BASE_URL = ''

# method to retrieve SID
def get_sid():
	fb = request.urlopen(FRITZBOX_BASE_URL + 'login_sid.lua')
	dom = ET.parse(fb)
	sid = dom.findtext('./SID')
	challenge = dom.findtext('Challenge')
	if sid == '0000000000000000':
		md5 = hashlib.md5()
		md5.update(challenge.encode('utf-16le'))
		md5.update('-'.encode('utf-16le'))
		md5.update(FRITZBOX_PASSWORD.encode('utf-16le'))
		response = challenge + '-' + md5.hexdigest()
		if FRITZBOX_USER:
			url = FRITZBOX_BASE_URL + 'login_sid.lua?username=' + FRITZBOX_USER + '&response=' + response
		else:
			url = FRITZBOX_BASE_URL + 'login_sid.lua?&response=' + response
		fb = request.urlopen(url)
		dom = ET.parse(fb)
		sid = dom.findtext('./SID')

	if sid == '0000000000000000':
		raise PermissionError('access denied')

	return sid

# get a valid SID
sid = get_sid()

# HTTP Post request body content
datadict = {'xhr': 1,
	'led_display': 2,
	'apply': '',
	'sid': sid,
	'lang': 'de',
	'page': 'led'}

data = parse.urlencode(datadict).encode()

req =  request.Request(FRITZBOX_BASE_URL + "data.lua", data=data)
# execute request to switch LEDs
resp = request.urlopen(req)

# log out
request.urlopen(FRITZBOX_BASE_URL + "home/home.lua?logout=1&sid=" + sid)
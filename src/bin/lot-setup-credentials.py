#!/usr/bin/env python3


import twython

APP_KEY = ''
APP_SECRET = ''

twitter = twython.Twython(APP_KEY, APP_SECRET)
auth = twitter.get_authentication_tokens()

OAUTH_TOKEN = auth['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

print("Log in to twitter and visit the following URL:")
print(auth['auth_url'])

del twitter
twitter = twython.Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
token = input('code: ').strip()

final_step = twitter.get_authorized_tokens(token)
OAUTH_TOKEN = final_step['oauth_token']
OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']

print("OAUTH_TOKEN: ", OAUTH_TOKEN)
print("OAUTH_TOKEN_SECRET: ", OAUTH_TOKEN_SECRET)

#!/usr/bin/python
import praw
import pdb
import re
import os
from pprint import pprint
import random
import time

if not os.path.isfile("exchanges_tracking.txt"):
	exchanges_tracking = []
else:
	exchanges_tracking_tmp=[]
	with open("exchanges_tracking.txt", "r") as f:
		exchanges_tracking_tmp = f.read()
		exchanges_tracking_tmp = exchanges_tracking_tmp.split('\n')

	exchanges_tracking = []
	for exchanges in exchanges_tracking_tmp:
		tmp_post = tuple(exchanges.strip().split(','))
		if tmp_post[0] != '':
			exchanges_tracking.append(tmp_post)		

reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit("minipaintingtest")

EXCHANGE_FLAIR_SIGNUP = u'exchangesignup'
EXCHANGE_FLAIR_MATCHING = u'exchangematching'
EXCHANGE_FLAIR_INPROGRESS = u'exchangeinprogress'
EXCHANGE_SIGNUP_TEXT=u'!signup'
EXCHANGE_SIGNUP_PROCESSED_TEXT=u'Thank you for participating!'
EXCHANGE_MATCH_MESSAGE_SUBJECT=u'/r/minipainting Exchange'
EXCHANGE_MATCH_MESSAGE_TEXT=u'/r/minipainting Exchange :: You are matched with /u/'

while True:
	print 'Beginning Run ----------'
	for submission in subreddit.search('flair:Exchange'):
		if submission.link_flair_css_class == EXCHANGE_FLAIR_SIGNUP or submission.link_flair_css_class == EXCHANGE_FLAIR_MATCHING:
			print 'Found Exchange: ' + submission.title
			same_id_match = [item for item in exchanges_tracking if item[0] == submission.id]
			if len(same_id_match) == 0:		
				print 'New Exchange: ' + submission.title
				exchanges_tracking.append((submission.id, submission.title))
				with open("exchanges_tracking.txt","w") as f:
					for posts in exchanges_tracking:
						f.write(posts[0] + "," + posts[1] + "\n")

	exchanges_to_match = []

	for exchanges in exchanges_tracking:
		users_in_exchange = []
		print 'Scanning exchange [' + exchanges[1] + ']'

		if os.path.isfile(exchanges[0] + ".txt"):
			with open(exchanges[0] + ".txt", "r") as f:
				users_in_exchange_tmp = f.read()
				users_in_exchange_tmp = users_in_exchange_tmp.split('\n')
				for users in users_in_exchange_tmp:
					users_in_exchange.append(tuple(users.strip().split(',')))
		users_in_current_scan = []

		reddit_post = reddit.submission(id=exchanges[0])
		
		for top_level_comment in reddit_post.comments:
			if top_level_comment.body == EXCHANGE_SIGNUP_TEXT:
				check_for_user = [item for item in users_in_exchange if item[0] == top_level_comment.author.fullname]
				check_for_user_in_current_scan = [item for item in users_in_current_scan if item[0] == top_level_comment.author.fullname]			
				if len(check_for_user) == 0:
					top_level_comment.reply(EXCHANGE_SIGNUP_PROCESSED_TEXT)
					users_in_exchange.append((top_level_comment.author.fullname,top_level_comment.author.name))
					print 'New user in exchange: ' + top_level_command.author.name
				if len(check_for_user_in_current_scan) == 0:
					users_in_current_scan.append((top_level_comment.author.fullname,top_level_comment.author.name))

		with open(exchanges[0] + ".txt", "w") as f:
			for users in users_in_current_scan:
				f.write(users[0] + "," + users[1] + "\n")

		if reddit_post.link_flair_css_class == EXCHANGE_FLAIR_MATCHING:
			exchanges_to_match.append((exchanges[0], users_in_current_scan))


	for matching_exchange in exchanges_to_match:
		print 'Matching ' + matching_exchange[0]
		print 'Users ' + matching_exchange[1]

		users = matching_exchange[1]
		reddit_post = reddit.submission(id=matching_exchange[0])
		exchange_file = open(matching_exchange[0] + "_matchup.txt", "w")
		if len(users) % 2 == 1:
			odd_man_out = random.choice(users)
			reddit.redditor('redpiano').message(EXCHANGE_MATCH_MESSAGE_SUBJECT, EXCHANGE_MATCH_MESSAGE_TEXT + odd_man_out[1])
			reddit.redditor(odd_man_out[1]).message(EXCHANGE_MATCH_MESSAGE_SUBJECT, EXCHANGE_MATCH_MESSAGE_TEXT + 'redpiano')
			users.remove(odd_man_out)
			exchange_file.write('redpiano : ' + odd_man_out[1] + '\n')
			time.sleep(2)
		while(len(users) > 0):
			match1 = random.choice(users)
			users.remove(match1)
			match2 = random.choice(users)
			users.remove(match2)
			exchange_file.write(match1[1] + ' : ' + match2[1] + '\n')
			reddit.redditor(match1[1]).message(EXCHANGE_MATCH_MESSAGE_SUBJECT, EXCHANGE_MATCH_MESSAGE_TEXT + match2[1])
			time.sleep(2)
			reddit.redditor(match2[1]).message(EXCHANGE_MATCH_MESSAGE_SUBJECT, EXCHANGE_MATCH_MESSAGE_TEXT + match1[1])
			time.sleep(2)
		exchange_file.close()		

		choices = reddit_post.flair.choices()
		for choice in choices:
			if choice['flair_css_class'] == EXCHANGE_FLAIR_INPROGRESS:
				reddit_post.flair.select(choice['flair_template_id'])

	print 'Finished Run ---------'
	time.sleep(600)

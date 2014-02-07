import configparser
from posf import posf
from posf import POSFRedis
from posf import POSFBot

# http://docs.python.org/2/library/configparser.html

def read_ini(ini='cfg_posfbot.ini'):
	global posf
	opts = {}
	ints = {
		'debug_level'   : 1,
		'get_n_comments': 1,
		'redis_db'      : 1,
		'redis_port'    : 1,
	}
	bools = {
		'debug'         : True,
		'mail_enabled'  : True,
	}
	conf = configparser.ConfigParser()
	conf.read_file(open(ini))
	for key, value in conf.items('posfbot'):
		if key in ints:
			opts[key] = int(value)
		elif key in bools:
			opts[key] = str(value) and True
		else:
			opts[key] = str(value)
	return opts

posf  = POSFBot.POSFBot(read_ini())
posf.get_comments()


#print '########## Obtaining PRAW...'
#
#r = praw.Reddit('/u/posfbot - /r/picsofsanfrancisco Bot 0.01 by /u/badmonkey0001')
#
#print '########## Logging in...'
#
#r.login(bot_user, bot_pass)
#
#get_comment_listing()
#
#print '########## ', found, 'found.'
#
#if found > 0 and message != '':
#	message = 'Found ' + str(found) + ' mentions of ' + search_name + '\n' + message
#
#	print '########## Sending message...'
#	print message
#
#	if mail_enabled:
#		r.send_message(recipients, ('Found mentions of ' + search_name), message)
#
#print '########## Done. Last comment:', last_comment, 'at', last_epoch, time.ctime(last_epoch)

# picsofsanfrancisco
# posfbot/p0s5dundundundundada

# http://www.reddit.com/r/sanfrancisco+bayarea/comments?count=100&after=t3_1wpbd5
# http://www.reddit.com/r/sanfrancisco+bayarea/comments/.json?count=100&after=t1_cf5o6ge
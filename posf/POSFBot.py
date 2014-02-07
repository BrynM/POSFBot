import calendar
import configparser
import os
import posf
import POSFRedis
import praw
import re
import time

def read_ini(ini=False):
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
	if not ini:
		ini = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/'+'cfg_posfbot.ini'
	conf = configparser.ConfigParser()
	conf.read_file(open(ini))
	for key, value in conf.items('posfbot'):
		value = value.encode('ascii', 'replace')
		if key in ints:
			opts[key] = int(value)
		elif key in bools:
			opts[key] = (int(value) > 0)
		else:
			opts[key] = str(value)
	return opts


class POSFBot(posf.POSFBase):
	def __init__(self, options={}):
		posf.POSFBase.__init__(self, options)

		self.body            = ''
		self.comments        = False
		self.comment_matches = False
		self.opts            = {}
		self.opts_default    = {
			'user'          : 'reddit_user',
			'pass'          : 'reddit_pass',
			'cache_prefix'  : 'posf_',
			'debug'         : False,
			'debug_level'   : 1,
			'get_n_comments': 20,
			'mail_enabled'  : False,
			'mention_name' : 'Ima chargin mah search code',
			'mention_regex' : 'looking\s*with\s*regular\s*extressions',
			'mention_subs'  : 'pics+wtf',
			'recipients'    : 'other_reddit_user',
			'redis_host'    : '127.0.0.1',
			'redis_port'    : 6379,
			'redis_db'      : 0,
			'redis_auth'    : '',
		}
		self.__comments      = False
		self.__last_comment  = False
		self.__last_epoch    = False
		self.__last_fetch    = False
		self.__praw          = False

		self.opts         = self.parse_opts(options)
		self.__appstring  = self.name()+' v'+self.version()+' by '+self.author()
		self.__cache      = POSFRedis.POSFRedis(self.opts)

		self.debug('Started '+self.__appstring)

	def __mention_match(self, body):
		return re.search(self.opts['mention_regex'], body, flags=re.IGNORECASE) and True

	def __p(self):
		if not self.__praw:
			self.debug('Connecting to Reddit via PRAW as "'+self.opts['user']+'"')
			self.__praw = praw.Reddit(self.__appstring)
			self.__praw.login(self.opts['user'], self.opts['pass'])
			self.debug('Connected to Reddit', 5)
		if not self.__praw:
				raise NameError('* PRAW CONNECTION FAILED *')
		return self.__praw

	def __comment_data(self, comment, color=False):
		post_score = self.__format_score(comment.submission, color)
		comm_score = self.__format_score(comment, color)
		res        = self.cfg('reset')
		if color:
			name = self.cfg('purple')+comment.author.name.encode('ascii', 'replace')+res
		else:
			name = comment.author.name.encode('ascii', 'replace')
		return {
			'Subreddit': comment.subreddit.title.encode('ascii', 'replace')+' (/r/'+comment.subreddit.display_name.encode('ascii', 'replace')+')',
			'Post'     : post_score+' '+comment.link_title.encode('ascii', 'replace'),
			'Author'   : name+' '+comm_score,
			'Time'     : time.ctime(comment.created_utc)+' '+self.pretty_date(int(comment.created_utc)),
			'Name'     : comment.name,
			'ID'       : comment.id,
			'Permalink': re.sub('[a-z]{2,}://[^/]+', '', comment.permalink),
			'Body'     : comment.body.encode('ascii', 'replace'),
		}

	def __comment_header(self, comment, color=False):
		post_score = self.__format_score(comment.submission, color)
		comm_score = self.__format_score(comment, color)
		res        = self.cfg('reset')
		if color:
			name = self.cfg('purple')+comment.author.name.encode('ascii', 'replace')+res
		else:
			name = comment.author.name.encode('ascii', 'replace')
		return {
			'Info'   : str(len(comment.body.encode('ascii', 'replace')))+' chars by '+name+' '+comm_score+' at '+self.pretty_date(int(comment.created_utc))+' ('+time.ctime(comment.created_utc)+')',
			'Post'   : post_score+' '+comment.link_title.encode('ascii', 'replace'),
		}

	def __format_score(self, thing, color=False):
		if not color:
			return str(thing.score)+' ('+str(thing.ups)+'/'+str(thing.downs)+')'
		out = self.cfg('black')
		res = self.cfg('reset')
		color = res
		if int(thing.score) > 0:
			color = self.cfg('green')
		elif int(thing.score) < 0:
			color = self.cfg('red')
		return color+str(thing.score)+res+' ('+self.cfg('uv')+str(thing.ups)+res+'/'+self.cfg('dv')+str(thing.downs)+res+')'

#str(comment.submission.score)+' ('+self.cfg('uv')+str(comment.submission.ups)+self.cfg('reset')+'/'+self.cfg('dv')+str(comment.submission.downs)+self.cfg('reset')+')'

	def __format_comment(self, comment, fmt='cli'):
		out      = ''
		has_body = False
		if fmt is 'cli':
			for key in comment:
				if key is str and key.lower() is 'body':
					has_body = key
				else:
					out += '# '+key+': '+str(comment[key])+'\n'
			if has_body:
				out += bod+'\n\n'
		else: # markdown
			out += '\n----\n'
			for key in comment:
				if key is str and key.lower() is 'body':
					has_body = key
				else:
					out += '* **'+key+':** '+str(comment[key])+'\n'
			if has_body:
				out += '\n> '+re.sub('\n\n', '\n\n> ', comment['has_body'])
		return out

	def get_comments(self, since=False):
		p                   = self.__p()
		self.__last_comment = self.__cache.cget('last_comment')
		self.__last_epoch   = self.__cache.cget('last_epoch')
		self.__last_fetch   = self.__cache.cget('last_fetch')

		if not since or not type(since) is float:
			since = self.__last_fetch

		get_comment_args = {
			'limit': self.opts['get_n_comments'],
			'after': since
		}
		self.debug('Getting '+str(self.opts['get_n_comments'])+' comment(s) from '+self.opts['mention_subs']+' since '+str(since)+' '+time.ctime(float(since)), 1)
		self.__comments = self.__p().get_comments(self.opts['mention_subs'], False, get_comment_args)
		self.debug('Gotten.', 2)

		return self.__comments

	def get_mentions(self, comments={}):
		count    = 0
		found    = 0
		mentions = {}
		message  = ''
		day      = 60 * 60 * 24
		day_ago  = time.gmtime()

		if not comments:
			if not self.__comments:
				self.get_comments()
				if not self.__comments:
					raise NameError('Could not get mention comments')

		for comment in self.__comments:
			summary    = ''
			bod        = comment.body.encode('ascii', 'replace')
			mention    = self.__mention_match(bod)
			count += 1
			if mention:
				found += 1
				comment_data = {
					'Subreddit': comment.subreddit.title.encode('ascii', 'replace')+' (/r/'+comment.subreddit.display_name.encode('ascii', 'replace')+')',
					'Post'     : comment.link_title.encode('ascii', 'replace'),
					'Author'   : comment.author.name.encode('ascii', 'replace')+' score '+str(comment.ups - comment.downs)+'('+str(comment.ups)+'/'+str(comment.downs)+')',
					'Time'     : time.ctime(comment.created_utc)+' '+self.pretty_date(int(comment.created_utc)),
					'Name'     : comment.name,
					'ID'       : comment.id,
					'Permalink': re.sub('[a-z]{2,}://[^/]+', '', comment.permalink)
				}
				summary += '\n########## Found!\n'
				summary += self.__format_comment(comment)
				message += self.__format_comment(comment, 'markdown')

			else:
				summary += '# Skipped '+comment.name+' '+time.ctime(comment.created_utc)+' '+self.pretty_date(int(comment.created_utc))+'\n'
#				summary += bod+'\n'

			print summary

			if comment.created_utc > self.__last_epoch:
				self.__last_epoch   = comment.created_utc
				self.__last_comment = comment.name

		time.sleep(2)

		if found > 0 and message != '':
			self.__cache.set('last_comment', self.__last_comment)
			self.__cache.set('last_epoch', self.__last_epoch)

		print '########## ', found, 'found out of', count

		if found > 0 and message != '':
			message = 'Found '+str(found)+' mention(s) of '+self.opts['mention_name']+'\n'+message
		
			print '########## Sending message...'
			print message
		
			if self.opts['mail_enabled']:
				self.__p().send_message(self.opts['recipients'], ('Found '+str(found)+' mention(s) of '+self.opts['mention_name']), message)

		self.__cache.set('last_fetch', self.__last_fetch)

		print '########## Done. Last comment:', self.__last_comment, 'at', self.__last_epoch, time.ctime(float(self.__last_epoch))

	def get_stream_mentions(self):
		for comment in praw.helpers.comment_stream(self.__p(), self.opts['mention_subs'], 100, 0):
			bod     = comment.body.encode('ascii', 'replace')
			mention = self.__mention_match(bod)
			if mention:
				self.spit('Match!!!', '##########')
				self.spit('Comment', '##########')
				print self.__format_comment(self.__comment_data(comment, True))
			else:
				print self.__format_comment(self.__comment_header(comment, True))



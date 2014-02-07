import configparser, praw, re, time
import posf
import POSFRedis

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
			'get_n_comments': 100,
			'mail_enabled'  : False,
			'mention_blurb' : 'Search for mentions',
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
		self.__praw          = False

		self.opts         = self.parse_opts(options)
		self.__appstring  = self.name() + ' v' + self.version() + ' by ' + self.author()
		self.__cache      = POSFRedis.POSFRedis(self.opts)

		self.debug('Started ' + self.__appstring)

	def __mention_match(self, body):
		return re.search(self.opts['mention_regex'], body, flags=re.IGNORECASE) and True

	def __p(self):
		if not self.__praw:
			self.debug('Connecting to Reddit via PRAW as "' + self.opts['user'] + '"')
			self.__praw = praw.Reddit(self.__appstring)
			self.__praw.login(self.opts['user'], self.opts['pass'])
			self.debug('Connected to Reddit', 5)
		if not self.__praw:
				raise NameError('* PRAW CONNECTION FAILED *')
		return self.__praw

	def get_mentions(self, comments={}):
		if not comments:
			if not self.__comments:
				self.get_comments()
				if not self.__comments:
					raise NameError('Could not get mention comments')

		for comment in self.__comments:
			summary    = ''
			bod        = comment.body.encode('ascii', 'replace')
			mention    = self.__mention_match(bod)
			if mention:
				found += 1
				comment_data = {
					'Subreddit': comment.subreddit.title.encode('ascii', 'replace') + ' (/r/' + comment.subreddit.display_name.encode('ascii', 'replace') + ')',
					'Post'     : comment.link_title.encode('ascii', 'replace'),
					'Author'   : comment.author.name.encode('ascii', 'replace') + ' score ' + str(comment.ups - comment.downs) + '(' + str(comment.ups) + '/' + str(comment.downs) + ')',
					'Time'     : time.ctime(comment.created_utc) + ' ' + self.pretty_date(int(comment.created_utc)),
					'Name'     : comment.name,
					'ID'       : comment.id,
					'Permalink': re.sub('[a-z]{2,}://[^/]+', '', comment.permalink)
				}
	
				summary += '\n########## Found!\n'
				message += '\n----\n'
	
				for key, value in comment_data.iteritems():
					message += '* **' + key + ':** ' + value + '\n'
					summary += '# ' + key + ': ' + value + '\n'
	
				message += '\n> ' + re.sub('\n\n', '\n\n> ', bod) + '\n\n'
				summary += bod + '\n\n'
	
			else:
				summary += '# Skipped ' + comment.name + ' ' + time.ctime(comment.created_utc) + ' ' + self.pretty_date(int(comment.created_utc))
	
			print summary
	
			if comment.created_utc < self.__last_epoch:
				self.__last_epoch   = comment.created_utc
				self.__last_comment = comment.name

	def get_comments(self):
		p                   = self.__p()
		self.__last_epoch   = self.__cache.cget('last_epoch')
		self.__last_comment = self.__cache.cget('last_comment')
		get_comment_args = {
			'count': self.opts['get_n_comments'],
			'after': self.__last_comment
		}
		self.__comments = p.get_comments(self.opts['mention_subs'], False, get_comment_args)
		return self.__comments


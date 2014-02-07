import sys, time
import pprint

class POSFBase(object):
	def __init__(self, options={}):
		self.__author       = '/u/badmonkey0001'
		self.__debug_prefix = '###'
		self.__name         = '/u/posfbot - /r/picsofsanfrancisco Bot'
		self.opts           = {}
		self.opts_default   = {
			'debug'      : False,
			'debug_level': 1
		}
		self.__spit_prefix  = '#'
		self.__version      = '0.01'

		self.opts = self.parse_opts(options)

		self.__debug        = self.opts['debug'] and True
		self.__debug_level  = self.opts['debug_level'] if self.opts['debug_level'] > 0 else 1

	def author(self):
		return self.__author

	def dump(self, thing):
		self.spit('this does not work')
		#pprint(vars(thing))

	def debug(self, thing, lvl=0):
		if self.__debug and self.__debug_level >= lvl:
			print self.__debug_prefix, thing

	def dump_opts(self):
		self.spit("Options")
		for key, value in self.opts_default.iteritems():
			print key, '=', self.opts[key]

	def name(self):
		return self.__name

	def parse_opts(self, options):
		for key, value in self.opts_default.iteritems():
			if key in options:
			#if key in options and type(options[key]) is type(self.opts_default[key]):
				self.opts[key] = options[key]
			else:
				self.opts[key] = self.opts_default[key]
		return self.opts

	def set_debug(self, dbg=False, lvl=1):
		self.__debug = True and dbg
		if type(lvl) is int:
			self.__debug_level = lvl
		else:
			self.__debug_level = 1
		return True and self.__debug

	def spit(self, thing):
		print self.__spit_prefix, thing

	def version(self):
		return self.__version

	def pretty_date(self, time=False):
		"""
		Get a datetime object or a int() Epoch timestamp and return a	pretty string
		like 'an hour ago', 'Yesterday', '3 months ago', 'just now', etc
		http://stackoverflow.com/questions/1551382/user-friendly-time-format-in-python
		"""
		from datetime import datetime
		now = datetime.now()
		if type(time) is int:
			diff = now - datetime.fromtimestamp(time)
		elif isinstance(time,datetime):
			diff = now - time 
		elif not time:
			diff = now - now
		second_diff = diff.seconds
		day_diff = diff.days
		if day_diff < 0:
			return ''
		if day_diff == 0:
			if second_diff < 10:
				return "just now"
			if second_diff < 60:
				return str(second_diff) + " seconds ago"
			if second_diff < 120:
				return  "a minute ago"
			if second_diff < 3600:
				return str( second_diff / 60 ) + " minutes ago"
			if second_diff < 7200:
				return "an hour ago"
			if second_diff < 86400:
				return str( second_diff / 3600 ) + " hours ago"
		if day_diff == 1:
			return "Yesterday"
		if day_diff < 7:
			return str(day_diff) + " days ago"
		if day_diff < 31:
			return str(day_diff/7) + " weeks ago"
		if day_diff < 365:
			return str(day_diff/30) + " months ago"
		return str(day_diff/365) + " years ago"

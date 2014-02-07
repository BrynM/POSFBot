import redis
import posf

class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance


if __name__ == '__main__':
    s1=Singleton()
    s2=Singleton()
    if(id(s1)==id(s2)):
        print "Same"
    else:
        print "Different"

class POSFRedis(posf.POSFBase):
	def __init__(self, options={}):
		posf.POSFBase.__init__(self, options)

		self.opts         = {}
		self.opts_default = {
			'redis_auth'  : '',
			'redis_bust'  : '1234abcd',
			'redis_db'    : 0,
			'redis_host'  : '127.0.0.1',
			'redis_port'  : 6379,
			'redis_prefix': 'posf_',
			'debug'       : False,
			'debug_level' : 1,
		}

		self.opts = self.parse_opts(options)

		self.auth       = self.opts['redis_auth']
		self.db         = self.opts['redis_db']
		self.host       = self.opts['redis_host']
		self.port       = self.opts['redis_port']
		self.__buster   = ''
		self.__redis    = False
		self.__prefix   = False
		self.__conn_str = False

		self.buster(self.opts['redis_bust'])
		self.prefix(self.opts['redis_prefix'])
		self.key()

	def __cache(self):
		if not self.__redis:
			if not self.__conn_str:
				self.__conn_str = self.host +':'+str(self.port)+'.'+str(self.db)
			if self.auth:
				self.debug('Connecting Redis '+self.__conn_str+' using authentication.')
				self.__redis = redis.Redis(host=self.host, port=self.port, db=self.db, password=self.auth)
			else:
				self.debug('Connecting Redis '+self.__conn_str)
				self.__redis = redis.Redis(host=self.host, port=self.port, db=self.db)
			if not self.__redis:
				raise NameError('* REDIS CONNECTION FAILED *')
			self.debug('Connected. Cache prefix '+self.prefix()+'.', 5)
		return self.__redis

	def buster(self, set_to=None):
		if set_to:
			self.__buster = set_to
		if not self.__buster:
			self.__buster = '_'
		return self.__buster

	def set(self, key, val):
		key = self.key(key)
		self.debug('Setting key '+key, 5)
		return self.__cache().set(key, val)

	def cget(self, key):
		key = self.key(key)
		self.debug('Retreiving key '+key, 5)
		return self.__cache().get(key)

	def delete(self, key):
		key = self.key(key)
		self.debug('Retreiving key '+key, 5)
		return self.__cache().delete(key)

	def key(self, key=''):
		return self.prefix()+'.'+key+'.'+self.buster()

	def prefix(self, set_to=None):
		if set_to:
			self.__prefix = set_to
		if not self.__prefix:
			self.__prefix = self.__class__.__name__+'_'
		return self.__prefix

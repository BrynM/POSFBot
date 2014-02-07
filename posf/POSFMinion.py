from multiprocessing import Pool
import posf
import POSFRedis

# http://stackoverflow.com/questions/1239035/asynchronous-method-call-in-python

class POSFMinion(posf.POSFBase):
	def __init__(self, options={}):
		posf.POSFBase.__init__(self, options)

	def minionize(cxt, callback):
		print 'do'
#from multiprocessing import Pool
#
#def f(x):
#    return x*x
#
#if __name__ == '__main__':
#    pool = Pool(processes=1)              # Start a worker processes.
#    result = pool.apply_async(f, [10], callback) # Evaluate "f(10)" asynchronously calling callback when finished.
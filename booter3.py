import os

from multiprocessing import Pool

processes = ('/home/pi/VernierTest4.py','/home/pi/i2c12.py')

def run_process(process):
	if(process=='/home/pi/VernierTest4.py'):
		os.system('python3 {}'.format(process))
	else:
		os.system('python {}'.format(process))

pool = Pool(processes=2)
pool.map(run_process, processes)


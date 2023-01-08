from multiprocessing import Process
import os
import argparse, sys
# import setproctitle
import copy
from this import d

import ccmutator
import ccgenerator
import ccparser
import ccsyscalls
import globalVar
import ccmounter
#多进程执行，进行种子生成，和种子变异
#以此实现共享testcases
#  ccgenerator.py---->种子生成
#  ccmutator.py----->种子变异
#  ccmounter.py---（在这里没有用到）-->取测试用例，并执行挂载。需要增加一个收集执行完状态＋比较环节
#  usage: python3 ccserver.py -k (is_kernel_fs) -T (target img) -t (fs-type) 
def p_generator(seedq, arglength):
	print("---------------generating seed by " + str(os.getpid()) + '\n')
	# setproctitle.setproctitle("p_generator")
	ccgenerator.cc_generator(seedq, arglength)
	seedq.join()

def p_mutator(seedq, testcaseq):
	print("---------------------mutating by" + str(os.getpid()) + '\n')
	# setproctitle.setproctitle("p_mutator")
	while True:
		cur_seed = seedq.get()
		# if cur_seed == None: break
		print("mutator: printing cur_seed")
		print(cur_seed)
		testcaseq.put(copy.deepcopy(cur_seed))
		ccmutator.ccmutate_syscalls(testcaseq, cur_seed)
		seedq.task_done()

if __name__ == '__main__':
	print("ccserver.py is running\n")
	mylength = 3
	outoftime = 4
	# 用户输入
	parser = argparse.ArgumentParser()
	parser.add_argument('-k', dest='is_kernel_fs',help='1 for kernel-fs; 0 for usrspace-fs')
	parser.add_argument('-T', dest='targetimg', help='the target device or img')
	# parser.add_argument('-i', dest='input', help='testcases')
	parser.add_argument('-t', dest='fs_type', help='specific fs type for kernel userspace fs')
	# parser.add_argument('-o', dest='output', help='path to save the testcaseq')

	args = parser.parse_args()

	if args.targetimg is None or args.fs_type is None or not args.is_kernel_fs in ['0', '1'] :
		print('Parameter-Error, check it out\n')
		sys.exit(1)
	iskfs = args.is_kernel_fs
	targetimg = args.targetimg
	fstype = args.fs_type
	# output = args.output
	# 多进程: generator, mutator
	gene_pro = Process(target = p_generator, args = (globalVar.SEED_QUEUE, mylength))
	muta_pro = Process(target = p_mutator, args = (globalVar.SEED_QUEUE, globalVar.TESTCASE_QUEUE), daemon = True)

	# p_l = [gene_pro, muta_pro, fuzzer_pro]
	p_l = [gene_pro, muta_pro]
	
	for p in p_l:
		p.start()
	'''
	for q in p_l:
		q.join()
	'''
	# fuzzer_pro.join()
	# muta_pro.join()
	gene_pro.join()
	

	print("the end+++++++++++++++++++")

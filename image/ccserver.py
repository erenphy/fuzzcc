from multiprocessing import Process
import os
import argparse, sys
# import setproctitle
import copy
# from this import d
import ccmutator
import ccgenerator
import ccparser
import ccsyscalls
import globalVar
import ccmounter
from ccinit import init_fs
# 多进程执行，进行种子生成，和种子变异
# 以此实现共享testcases
#  ccgenerator.py---->种子生成
#  ccmutator.py----->种子变异
#  ccmounter.py---（在这里没有用到）--> 取测试用例，并执行挂载。需要增加一个收集执行完状态＋比较环节
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
	# BUG 多进程全局变量隔离 --> 需要改多线程, 并对全局变量加锁 / 或者考虑将生成的种子写入文件，muta监听种子输出文件夹状态，读文件进行变异 / 或者依次进行，采用单线程
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

	# TODO 初始化文件系统
	# init_fs(fs01_filename, fs02_filename, init_files)

	# TODO 使用 ccmounter 挂载生成的文件系统

	# for () 把生成的queue交给ccarser解析并在挂载目录下执行
	# 	每次执行后调用hash校验对比两个img文件hash, 如果不一致则保存现场数据

	print("the end+++++++++++++++++++")

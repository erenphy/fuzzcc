from multiprocessing import Process
import os
import argparse, sys, tempfile
# import setproctitle
import copy
# from this import d
import ccmutator
import ccgenerator
import ccparser
import globalVar
import ccmounter
from cctools import file_md5_hash
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

# runner() input为单个操作序列， output为执行后的镜像
def runner(is_kernelfs, fs_type, input):
	# 初始化文件系统镜像
	# init_fs(fs01_filename, fs02_filename, init_files)
	init_files = " ".join(["fs.c", "hello.txt"])
	target_img = str(global_count) + '.img'
	adjoint_img = str(global_count) + '_adjoint.img'
	init_fs(target_img, adjoint_img, init_files)
	
	# 使用 ccmounter 挂载生成的文件系统
	if is_kernelfs == '1':
		#这里先不实现内核文件系统测试
		return
	elif is_kernelfs == '0':
		# 用户态文件系统测试
		# 生成挂载目录
		target_mnt = tempfile.mkdtemp()
		adjoint_mnt = tempfile.mkdtemp()
		seq_mnt = tempfile.mkdtemp()
		print('mount target dir: ' + target_mnt)
		print('mount adjoint dir: ' + adjoint_mnt)
		# 暂时不实现挂载第三个系统
		# print('mount sequential dir: ' + seq_mnt)

		# 挂载镜像到目录
		# usermount(specific fs path, img, mntdir,options(可选))
		ccmounter.usermount(fs_type, target_img, target_mnt)
		ccmounter.usermount(fs_type, adjoint_mnt, adjoint_mnt)
		for mnt_dir in [target_mnt, adjoint_mnt, seq_mnt]:
			ccmounter.chown(mnt_dir)
		# parser 解释执行input
		print("right here******************start parser\n")
		ccparser.cc_parser(target_mnt, input)
		ccmounter.userumount(target_mnt)
		ccmounter.usermount(fs_type, target_img, target_mnt)
		ccparser.cc_parser(adjoint_mnt, input)
		ccmounter.userumount(target_mnt)

		# 执行后调用hash校验对比两个img文件hash, 如果不一致则保存现场数据
		if file_md5_hash(target_img) != file_md5_hash(adjoint_img):
			print("Error: target_img and adjoint_img are not the same\n")
			# 设置发现不一致的信号
			diff_signal = 1

			# TODO:并将input加入seedqueue(这个加入是动态的，所以上边的初始种子和变异设置多线程阻塞，一旦mumator发现种子队列为空，阻塞等待，说不定能发现新种子)
			# 这里多线程里给seedqueue加, 可以直接用put吗?print('stopped!relatively consistency\n'),设置信号/flag
			globalVar.SEED_QUEUE.put(input)

			# TODO 将当前镜像target_img 和 adjoint_img的路径、和 input记录到logfile的一行

		else:
			diff_signal = 0
			#TODO 删除当前的镜像 target_img和adjoint_mnt
			#TODO 删除生成的随机目录： target_mnt和adjoint_mnt
			# 关于路径啥的python调用shell命令，我不会写
	return diff_signal

def morerunner(is_kernelfs, fs_type, input):
	diff_signal = 0
	# 暂时没找到合适的顺序文件系统，暂不实现
	return diff_signal

if __name__ == '__main__':
	print("ccserver.py is running\n")
	#暂时设置超时时间为4
	mylength = 3
	outoftime = 4

	#计数，同时也作为img的命名标志
	global global_count
	global_count = 1

	# 是否需要进一步判断目标文件系统与顺序文件系统执行的信号
	# 若目标和伴随的比较没有发现不一致，则信号设为1,需要继续比较
	# 否则，为0，不需要继续比较
	morecmp_signal = 1
	# 假设一开始具备strict-consistency
	strict_signal = 1

	# 用户输入
	parser = argparse.ArgumentParser()
	parser.add_argument('-k', dest='is_kernel_fs',help='1 for kernel-fs; 0 for usrspace-fs')
	# parser.add_argument('-T', dest='targetimg', help='the target device or img')
	# parser.add_argument('-i', dest='input', help='testcases')
	parser.add_argument('-t', dest='fs_type', help='specific fs type for kernel userspace fs')
	# parser.add_argument('-o', dest='output', help='path to save the testcaseq')

	args = parser.parse_args()

	if args.fs_type is None or not args.is_kernel_fs in ['0', '1'] :
		print('Parameter-Error, check it out\n')
		sys.exit(1)
	iskfs = args.is_kernel_fs
	# targetimg = args.targetimg
	fstype = args.fs_type
	# output = args.output
	# 多进程: generator, mutator
	# BUG 多进程全局变量隔离 --> 需要改多线程, 并对全局变量加锁 / 或者考虑将生成的种子写入文件，muta监听种子输出文件夹状态，读文件进行变异 / 或者依次进行，采用单线程 X --->因为想要有反馈的fuzz,将成功触发不一致的测试用例重新加入种子池，得是一个动态过程
	gene_pro = Process(target = p_generator, args = (globalVar.SEED_QUEUE, mylength))
	muta_pro = Process(target = p_mutator, args = (globalVar.SEED_QUEUE, globalVar.TESTCASE_QUEUE), daemon = True)

	# p_l = [gene_pro, muta_pro, fuzzer_pro]
	p_l = [gene_pro, muta_pro]
	
	
	# for () 把生成的queue交给ccarser解析并在挂载目录下执行
	for cur_seq in globalVar.TESTCASE_QUEUE:
		cur_result = runner(iskfs, fstype, cur_seq)
		if cur_result == 1:
			#比较的目标和伴随文件系统出现了不一致，则不需要进行目标文件系统和顺序文件系统的比较了
			# 也就不会进入下边的if
			morecmp_signal = 0
		# else: 
			# 没有发现不一致，把cur_seq从testcasequeue中移除就好了
			# TODO: 怎么移除

	# 在现存的testcase上重新执行
	if morecmp_signal == 1:
		for cur_seq in globalVar.TESTCASE_QUEUE:
			cur_result = morerunner(iskfs, fstype, cur_seq)
			if cur_result == 1:
				#比较的目标和顺序文件系统执行不一致，则不具备strictly consistency,设置信号/flag
				#TODO: 写日志 给出最后结果，可以把下面的输出保存到logfile里？或者程序界面
				strict_signal = 0
				print('stopped!relatively consistency\n')
		if strict_signal == 0:
			print('well done! strictly consistency\n')
	print("the end+++++++++++++++++++")
from multiprocessing import Process
import os
import argparse, sys, tempfile
# import setproctitle
import copy
# from this import d
import ccmutator
import ccgenerator
import ccparser
import ccsyscalls
import globalVar
import ccmounter
from cctools import file_md5_hash
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

# runner() input为单个操作序列， output为执行后的镜像
def runner(is_kernelfs, fs_type, input):
	# 初始化文件系统镜像
	# init_fs(fs01_filename, fs02_filename, init_files)
	init_files = " ".join(["fs.c", "hello.txt"])
	target_img = str(global_count) + '.img'
	adjoint_img = str(global_count) + '_adjoint.img'
	init_fs(target_img, adjoint_img, init_files)
	
	# 使用 ccmounter 挂载生成的文件系统
	if is_kernelfs == '1':
		#这里先不实现内核文件系统测试
		return
	elif is_kernelfs == '0':
		# 用户态文件系统测试
		# 生成挂载目录
		target_mnt = tempfile.mkdtemp()
		adjoint_mnt = tempfile.mkdtemp()
		seq_mnt = tempfile.mkdtemp()
		print('mount target dir: ' + target_mnt)
		print('mount adjoint dir: ' + adjoint_mnt)
		# 暂时不实现挂载第三个系统
		# print('mount sequential dir: ' + seq_mnt)

		# 挂载镜像到目录
		# usermount(specific fs path, img, mntdir,options(可选))
		ccmounter.usermount(fs_type, target_img, target_mnt)
		ccmounter.usermount(fs_type, adjoint_mnt, adjoint_mnt)
		for mnt_dir in [target_mnt, adjoint_mnt, seq_mnt]:
			ccmounter.chown(mnt_dir)
		# parser 解释执行input
		print("right here******************start parser\n")
		ccparser.cc_parser(target_mnt, input)
		ccmounter.userumount(target_mnt)
		ccmounter.usermount(fs_type, target_img, target_mnt)
		ccparser.cc_parser(adjoint_mnt, input)
		ccmounter.userumount(target_mnt)

		# 执行后调用hash校验对比两个img文件hash, 如果不一致则保存现场数据
		if file_md5_hash(target_img) != file_md5_hash(adjoint_img):
			print("Error: target_img and adjoint_img are not the same\n")
			# 设置发现不一致的信号
			diff_signal = 1

			# TODO:并将input加入seedqueue(这个加入是动态的，所以上边的初始种子和变异设置多线程阻塞，一旦mumator发现种子队列为空，阻塞等待，说不定能发现新种子)
			# 这里多线程里给seedqueue加, 可以直接用put吗?print('stopped!relatively consistency\n'),设置信号/flag
			globalVar.SEED_QUEUE.put(input)

			# TODO 将当前镜像target_img 和 adjoint_img的路径、和 input记录到logfile的一行

		else:
			diff_signal = 0
			#TODO 删除当前的镜像 target_img和adjoint_img
			#TODO 删除生成的随机目录： target_mnt和adjoint_mnt
			# 关于路径啥的python调用shell命令，我不会写
	return diff_signal

def morerunner(is_kernelfs, fs_type, input):
	diff_signal = 0
	# 暂时没找到合适的顺序文件系统，暂不实现
	return diff_signal

if __name__ == '__main__':
	print("ccserver.py is running\n")
	#暂时设置超时时间为4
	mylength = 3
	outoftime = 4

	#计数，同时也作为img的命名标志,这里需不需要设置成global?
	global_count = 1

	# 是否需要进一步判断目标文件系统与顺序文件系统执行的信号
	# 若目标和伴随的比较没有发现不一致，则信号设为1,需要继续比较
	# 否则，为0，不需要继续比较
	morecmp_signal = 1
	# 假设一开始具备strict-consistency
	strict_signal = 1

	# 用户输入
	parser = argparse.ArgumentParser()
	parser.add_argument('-k', dest='is_kernel_fs',help='1 for kernel-fs; 0 for usrspace-fs')
	# parser.add_argument('-T', dest='targetimg', help='the target device or img')
	# parser.add_argument('-i', dest='input', help='testcases')
	parser.add_argument('-t', dest='fs_type', help='specific fs type for kernel userspace fs')
	# parser.add_argument('-o', dest='output', help='path to save the testcaseq')

	args = parser.parse_args()

	if args.fs_type is None or not args.is_kernel_fs in ['0', '1'] :
		print('Parameter-Error, check it out\n')
		sys.exit(1)
	iskfs = args.is_kernel_fs
	# targetimg = args.targetimg
	fstype = args.fs_type
	# output = args.output
	# 多进程: generator, mutator
	# BUG 多进程全局变量隔离 --> 需要改多线程, 并对全局变量加锁 / 或者考虑将生成的种子写入文件，muta监听种子输出文件夹状态，读文件进行变异 / 或者依次进行，采用单线程 X --->因为想要有反馈的fuzz,将成功触发不一致的测试用例重新加入种子池，得是一个动态过程
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

	
	# for () 把生成的queue交给ccarser解析并在挂载目录下执行
	for cur_seq in globalVar.TESTCASE_QUEUE:
		cur_result = runner(iskfs, fstype, cur_seq)
		if cur_result == 1:
			#比较的目标和伴随文件系统出现了不一致，则不需要进行目标文件系统和顺序文件系统的比较了
			morecmp_signal = 0
		# else: 
			# 没有发现不一致，把cur_seq从testcasequeue中移除就好了
			# TODO: 怎么移除
		global_count = global_count + 1

	# 在现存的testcase上重新执行
	if morecmp_signal == 1:
		for cur_seq in globalVar.TESTCASE_QUEUE:
			cur_result = morerunner(iskfs, fstype, cur_seq)
			if cur_result == 1:
				#比较的目标和顺序文件系统执行不一致，则不具备strictly consistency,设置信号/flag
				#给出最后结果，可以把下面的输出保存到logfile里？或者程序界面
				strict_signal = 0
				print('stopped!relatively consistency\n')
			global_count = global_count + 1
		if strict_signal == 0:
			print('well done! strictly consistency\n')
		
	print("the end+++++++++++++++++++")

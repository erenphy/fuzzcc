import os
import argparse, sys, tempfile
import logging
import threading
# import setproctitle
import copy
import ccmutator
import ccparser
# import globalVar
import ccmounter
from globalVar import *
from cctools import file_md5_hash
from ccinit import init_fs
from ccgenerator import Generator

# TODO 待检查
class Mutator(threading.Thread):
	def __init__(self, thread_name):
		super(Mutator, self).__init__(name=thread_name)
		# self.length=arg_length
	def mutator(self):
		print(f"[+] {self.name} working...")
		global SEED_QUEUE
		global TESTCASE_QUEUE
		while not SEED_QUEUE.empty():
			MUTEX.acquire()
			cur_seed = SEED_QUEUE.get()
			MUTEX.release()
			# if cur_seed == None: break
			print("mutator: printing cur_seed")
			print(cur_seed)
			TESTCASE_QUEUE.put(copy.deepcopy(cur_seed))
			ccmutate_syscalls(TESTCASE_QUEUE, cur_seed)
		SEED_QUEUE.join()

# runner() input为单个操作序列， output为执行后的镜像
def runner(is_kernelfs, fs_type, input):
	# 初始化文件系统镜像
	# init_fs(fs01_filename, fs02_filename, init_files)
	init_files = " ".join(["1.txt"])   # 这里初始化的文件要能让脚本找到
	target_img = f"{GLOBAL_COUNT}.img"
	adjoint_img = f"{GLOBAL_COUNT}_adjoint.img"
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
			# -- 加锁操作
			# -- 感觉种子可以考虑写文件保存起来
			SEED_QUEUE.put(input)

			# TODO 将当前镜像target_img 和 adjoint_img的路径、和 input记录到logfile的一行
			# 日志记录看一下 logging 的使用: https://docs.python.org/zh-cn/3/howto/logging.html
			logging.info("Start logging...")


		else:
			diff_signal = 0
			#TODO 删除当前的镜像 target_img和adjoint_mnt
			#TODO 删除生成的随机目录： target_mnt和adjoint_mnt
			# 关于路径啥的python调用shell命令，我不会写
			# --> 参考： https://www.myfreax.com/python-delete-files-and-directories/
	return diff_signal

def morerunner(is_kernelfs, fs_type, input):
	diff_signal = 0
	# 暂时没找到合适的顺序文件系统，暂不实现
	return diff_signal

def arg_parse():
	# 参数解析
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
	
	return args

if __name__ == '__main__':
	# 计数，同时也作为img的命名标志
	# Q: 这个需要显式设置为global吗？我在py里的定义都没有显式设置全局...  --> 如果放在这的话确实要设置为global
	global GLOBAL_COUNT
	GLOBAL_COUNT = 1

	# 是否需要进一步判断目标文件系统与顺序文件系统执行的信号
	# 若目标和伴随的比较没有发现不一致，则信号设为1,需要继续比较
	# 否则，为0，不需要继续比较
	morecmp_signal = 1
	# 假设一开始具备strict-consistency
	strict_signal = 1

	args = arg_parse()
	iskfs = args.is_kernel_fs
	# targetimg = args.targetimg
	fstype = args.fs_type

	logging.warning("ccserver start running...")

	# # TODO：多线程加锁: generator, mutator
	# # BUG 多进程全局变量隔离 --> 需要改多线程, 并对全局变量加锁 / 或者考虑将生成的种子写入文件，muta监听种子输出文件夹状态，读文件进行变异 / 或者依次进行，采用单线程 X --->因为想要有反馈的fuzz,将成功触发不一致的测试用例重新加入种子池，得是一个动态过程

	gene_pro = Generator("generator", ARG_LENGTH)

	gene_pro.start()
	
	# 不知道为啥不执行变异线程
	muta_pro = Mutator("mutator")

	muta_pro.start()
	
	# # for () 把生成的queue交给ccarser解析并在挂载目录下执行
	# for cur_seq in TESTCASE_QUEUE:
	# 	cur_result = runner(iskfs, fstype, cur_seq)
	# 	if cur_result == 1:
	# 		#比较的目标和伴随文件系统出现了不一致，则不需要进行目标文件系统和顺序文件系统的比较了
	# 		# 也就不会进入下边的if
	# 		morecmp_signal = 0
	# 	# else: 
	# 		# 没有发现不一致，把cur_seq从testcasequeue中移除就好了  
	# 		# TODO: 怎么移除  --> queue的get操作是取出（直接删掉头部元素并返回，不需要移除

	# # 在现存的testcase上重新执行
	# if morecmp_signal == 1:
	# 	for cur_seq in TESTCASE_QUEUE:
	# 		cur_result = morerunner(iskfs, fstype, cur_seq)
	# 		if cur_result == 1:
	# 			#比较的目标和顺序文件系统执行不一致，则不具备strictly consistency,设置信号/flag
	# 			#TODO: 写日志 给出最后结果，可以把下面的输出保存到logfile里？或者程序界面
	# 			strict_signal = 0
	# 			print('stopped!relatively consistency\n')
	# 	if strict_signal == 0:
	# 		print('well done! strictly consistency\n')
	# print("the end+++++++++++++++++++")

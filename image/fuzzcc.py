import argparse, sys, tempfile
# import multiprocessing
from multiprocessing import Process
'''
把全局变量seed和testcase的类型改成queue.queue; deque不是进程安全的
afl的种子池是用什么实现的呢
像afl一样用共享内存保存在状态空间信息，可以吗

'''

import ccgenerator
import ccmutator
import ccparser
import ccsyscalls
import globalVar
from istat import kmount, kumount, usermount, userumount, chown

'''
python3 fuzzcc.py -l --max_syscalls_length -m --mountpoint -t --mutation_time
'''

if __name__ == '__main__':
	print("fuzzcc.py is called\n")

	parser = argparse.ArgumentParser()
	parser.add_argument('-l', dest='length', help='the max syscalls length')
	# parser.add_argument('-m', dest='mntpoint', help='mountpoint(absolute path), default /mnt/ext3pnt')
	# parser.add_argument('-t', dest='timer', help='mutation_time')
	parser.add_argument('-t', dest='type', help='k for kernel fs; u for usrspace fs')
	parser.add_argument('-T', dest='target', help='the target device or img')
	parser.add_argument('-p', dest='plus', help='specific fs type for kernel/userspace fs')
	parser.add_argument('-o', dest='output', help='the converted file')

	args = parser.parse_args()

	if args.length is None or args.type is None or args.plus is None or args.output is None or args.target is None:
		print('ERROR')
		sys.exit(1)
	
	if args.type == 'k':
		mnt_dir = tempfile.mkdtemp()
		print('mount dir: %s', mnt_dir)
		# kmount(fstype, device, mntdir)
		kmount(args.plus, args.target, mnt_dir)
		chown(mnt_dir)
	else:
		mnt_dir = tempfile.mkdtemp()
		print('mount dir: %s', mnt_dir)
		# kmount(fstype, device, mntdir)
		usermount(args.plus, args.target, mnt_dir)
		chown(mnt_dir)
	
	globalVar.MY_MNT_POINT = mnt_dir

	


	
	
 
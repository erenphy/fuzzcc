from mimetypes import init
import math
from random import randint, seed
from secrets import choice
import sys
from typing import Deque
from unittest import TestCase
from xml.etree.ElementPath import ops
from xeger import Xeger
import random
from os.path import join as pjoin

# my own module.py
import globalVar
import ccsyscalls


# ccgenerator.py: 生成初始测试用例集合
# 	main-func: ccgenerator(max_length)

# drop this method
def ccget_seed():
	num = math.pow(10, 20)
	ccpi = int(math.pi*num)
	return hex(ccpi)

# return: a random-dirpath
def ccgene_dir():
	if len(globalVar.MY_DIR_LIST) >= globalVar.DIR_FULL_SIZE:
		return random.choice(globalVar.MY_DIR_LIST)
	_x = Xeger(limit = 2)
	out = _x.xeger(r'(\./[AB](/[CD](/[EF])?)?)')
	if not out in globalVar.MY_DIR_LIST:
		globalVar.MY_DIR_LIST.append(out)
	return out

# return: a random-filename with full path
def ccgene_file():
	out = random.choice(globalVar.MY_FILE_LIST)
	# 增加genarate目录的频率
	ccgene_dir()
	pre_dir = random.choice(globalVar.MY_DIR_LIST)
	return pjoin(pre_dir, out)

def ccgene_wt_para():
	tmp = random.randint(0,15)
	return tmp
'''
func:
para: 允许生成的最大序列长度
return: 
'''
def cc_generator(q, max_length):
	# 初始测试用例随机数目
	init_size = randint(globalVar.INIT_TIME_MIN, globalVar.INIT_TIME_MAX)
	while init_size:
		# 每条测试用例的长度随机生成
		print("\niniting time left: " + str(init_size))
		cur_queue = []
		cur_length = randint(1,max_length)
		print("\ncur_length = " + str(cur_length))
		while cur_length:
			rdm = randint(0,globalVar.OPS_LENGTH - 1)
			print("\nrandom ops = " + str(rdm))
			if rdm == globalVar.ops.CREAT:
				print("\ncreating files")
				cur_op = 'creat'
				cur_name = ccgene_file()
				syscall_kv = [cur_op, cur_name]
				# ccsyscalls.cccreat(globalVar.MY_MNT_POINT, cur_para)
			elif rdm == globalVar.ops.APPEND:
				cur_op = 'append'
				cur_name = ccgene_file()
				cur_para = ccgene_wt_para()
				syscall_kv = [cur_op, cur_name, cur_para]
				# ccsyscalls.ccappend(globalVar.MY_MNT_POINT, cur_name, cur_para)
			elif rdm == globalVar.ops.HARDLN:
				cur_op = 'hardlink'
				cur_name1 = ccgene_file()
				cur_name2 = ccgene_file()
				syscall_kv = [cur_op, [cur_name1, cur_name2]]
				# ccsyscalls.cchdlink(globalVar.MY_MNT_POINT, cur_name)
			elif rdm == globalVar.ops.MKDIR:
				cur_op = 'mkdir'
				cur_name = ccgene_dir()
				syscall_kv = [cur_op, cur_name]
				# ccsyscalls.ccmkdir(globalVar.MY_MNT_POINT, cur_name)
			elif rdm == globalVar.ops.READ:
				cur_op = 'read'
				cur_name = ccgene_file()
				syscall_kv = [cur_op, cur_name]
				# ccsyscalls.ccread(globalVar.MY_MNT_POINT, cur_name)
			elif rdm == globalVar.ops.REMOVE:
				cur_op = 'remove'
				# 相当于unlink file 或 rmdir, 
				file_or_dir = [ccgene_file, ccgene_dir]
				# Q:返回值是空字符串怎么办
				# A:还没想到
				cur_name = random.choice(file_or_dir)()
				syscall_kv = [cur_op, cur_name]
				# ccsyscalls.ccremove(globalVar.MY_MNT_POINT, cur_name)
			elif rdm == globalVar.ops.RENAME:
				cur_op = 'rename'
				# haaa, 这里的方法好原始
				cur_name1 = ccgene_file()
				cur_name2 = ccgene_file()
				cur_name3 = ccgene_dir()
				cur_name4 = ccgene_dir()
				cur_name = random.choice([[cur_name1, cur_name2], [cur_name3, cur_name4]])
				syscall_kv= [cur_op, cur_name]
				# ccsyscalls.ccrename(globalVar.MY_MNT_POINT, cur_name1, cur_name2)
			elif rdm == globalVar.ops.SOFTLN:
				cur_op = 'softlink'
				cur_name1 = ccgene_file()
				cur_name2 = ccgene_file()
				cur_name3 = ccgene_dir()
				cur_name4 = random.choice([cur_name1, cur_name3])
				cur_name = [cur_name4, cur_name2]
				syscall_kv = [cur_op, cur_name]
				# ccsyscalls.ccsflink(globalVar.MY_MNT_POINT,cur_name)
			elif rdm == globalVar.ops.SYNC:
				cur_op = 'sync'
				syscall_kv = [cur_op]
			elif rdm == globalVar.ops.WRITE:
				cur_op = 'write'
				cur_name = ccgene_file()
				cur_para = ccgene_wt_para()
				syscall_kv = [cur_op, cur_name, cur_para]
				# ccsyscalls.ccwrite(globalVar.MY_MNT_POINT, cur_name, cur_para)
			else: pass
			cur_length = cur_length - 1
			cur_queue.append(syscall_kv)
		init_size = init_size - 1
		q.put(cur_queue)
	

if __name__ == '__main__':
	print('ccgenerator.py is running\n')

	'''
	ccgenerator(5)	
	for i in globalVar.TESTCASE_QUEUE:
		print(i)
		print("\n")
	ccgene_wt_para()
	
	for i in range(0, 5):
		filename1 = ccgene_file()
		print(filename1 + '\n')
	
	ccgenerator(2)
	print(globalVar.MY_DIR_LIST)
	
	testqueue = Deque()
	curname = 'creat'
	curfile = 'file1'
	testqueue.append([curname, curfile])
	print(testqueue)
	'''
	
# SYSCALL_STACK.append(syscall_name, syscall_args, syscall_ret)
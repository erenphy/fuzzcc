import os
from collections import deque


import ccsyscalls
import globalVar
'''
python3 ccparser.py 
最好增加个testcase剪枝
将syscalls_queue解析出来
队列 一头进一头出
'''
# 将write和append函数的para十进制数转化为二进制比特位列表，方便parse
def ccparser_convert_wtpara(para_num):
	bintmp = bin(para_num)[2:].zfill(4)
	# print(bintmp)
	para = []
	for i in range(0,4):
		para.append(bintmp[i])
	# print(para)
	return para

	
def cc_parser(mnt_point, syscalls):
	print("func: parser() is called\n")
	for cur_syscall in syscalls:
		if cur_syscall[0] == 'creat':
			try:
				ccsyscalls.cccreat(mnt_point, cur_syscall[1])
			except: pass
		elif cur_syscall[0] == 'write':
			try:
				para_list = ccparser_convert_wtpara(cur_syscall[2])
				ccsyscalls.ccwrite(mnt_point, cur_syscall[1], para_list[0], para_list[1],para_list[2], para_list[3])
			except: pass
		elif cur_syscall[0] == 'append':
			try:
				para_list = ccparser_convert_wtpara(cur_syscall[2])
				ccsyscalls.ccappend(mnt_point, cur_syscall[1], para_list[0], para_list[1],para_list[2], para_list[3])
			except: pass
		elif cur_syscall[0] == 'remove':
			try: 
				ccsyscalls.ccremove(mnt_point, cur_syscall[1])
			except: pass
		elif cur_syscall[0] == 'rename':
			try:
				ccsyscalls.ccrename(mnt_point, cur_syscall[1][0], cur_syscall[1][1])
			except: pass
		elif cur_syscall[0] == 'mkdir':
			try:
				ccsyscalls.ccmkdir(mnt_point, cur_syscall[1])
			except: pass
		elif cur_syscall[0] == 'hardlink':
			try:
				ccsyscalls.cchdlink(mnt_point, cur_syscall[1][0], cur_syscall[1][1])
			except: pass
		elif cur_syscall[0] == 'softlink':
			try:
				ccsyscalls.ccsflink(mnt_point, cur_syscall[1][0], cur_syscall[1][1])
			except: pass
		elif cur_syscall[0] == 'sync':
			try:
				ccsyscalls.ccsync()
			except: pass
		elif cur_syscall[0] == 'read':
			try: 
				ccsyscalls.ccread(mnt_point, cur_syscall[1])
			except: pass
		else: pass
'''
def cc_parser(mnt_point, syscalls):
	print("func: parser()\n")
	while len(globalVar.TESTCASE_QUEUE) > 0:
		# 取出测试用例：一条完整的操作序列
		cur_tc = globalVar.TESTCASE_QUEUE.get()
		for cur_syscall in cur_tc:
			if cur_syscall[0] == 'creat':
				try:
					ccsyscalls.cccreat(globalVar.MY_MNT_POINT, cur_syscall[1])
				except: pass
			elif cur_syscall[0] == 'write':
				try:
					para_list = ccparser_convert_wtpara(cur_syscall[2])
					ccsyscalls.ccwrite(globalVar.MY_MNT_POINT, cur_syscall[1], para_list[0], para_list[1],para_list[2], para_list[3])
				except: pass
			elif cur_syscall[0] == 'append':
				try:
					para_list = ccparser_convert_wtpara(cur_syscall[2])
					ccsyscalls.ccappend(globalVar.MY_MNT_POINT, cur_syscall[1], para_list[0], para_list[1],para_list[2], para_list[3])
				except: pass
			elif cur_syscall[0] == 'remove':
				try: 
					ccsyscalls.ccremove(globalVar.MY_MNT_POINT, cur_syscall[1])
				except: pass
			elif cur_syscall[0] == 'rename':
				try:
					ccsyscalls.ccrename(globalVar.MY_MNT_POINT, cur_syscall[1][0], cur_syscall[1][1])
				except: pass
			elif cur_syscall[0] == 'mkdir':
				try:
					ccsyscalls.ccmkdir(globalVar.MY_MNT_POINT, cur_syscall[1])
				except: pass
			elif cur_syscall[0] == 'hardlink':
				try:
					ccsyscalls.cchdlink(globalVar.MY_MNT_POINT, cur_syscall[1][0], cur_syscall[1][1])
				except: pass
			elif cur_syscall[0] == 'softlink':
				try:
					ccsyscalls.ccsflink(globalVar.MY_MNT_POINT, cur_syscall[1][0], cur_syscall[1][1])
				except: pass
			elif cur_syscall[0] == 'sync':
				try:
					ccsyscalls.ccsync()
				except: pass
			elif cur_syscall[0] == 'read':
				try: 
					ccsyscalls.ccread(globalVar.MY_MNT_POINT, cur_syscall[1])
				except: pass
			else: pass
'''

					





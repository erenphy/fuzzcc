#!/usr/bin/env python3
# from curses import newpad
# from asyncio.windows_events import NULL
from asyncore import write
from ctypes import pointer
from doctest import debug_script
from genericpath import isdir
import subprocess
# from turtle import ScrolledCanvas
import pytest
import os
import stat
import time
from os.path import join as pjoin
import sys
import re
import itertools
import tempfile
import random
import math

import ccsyscalls

basepath = pjoin(os.path.dirname(__file__), '..')
# print(basename)

# from 0 to a very-big number
seed_counter = 0

def wait_for_mnt(mnt_process, mnt_dir, test_fn=os.path.ismount):
	spendtime = 0
	while spendtime < 30:
		if test_fn(mnt_dir):
			return True
		if mnt_process.poll() is not None:
			pytest.fail('fs process terminated prematurely')
		time.sleep(0.1)
		spendtime += 0.1
	pytest.fail("mount failed")


def usermount(targetfs, initimg, mntpoint, option='-f'):
	# print(['sudo', targetfs, initimg, '-f', mntpoint])
	# print(basepath)
	print('Running usermount() in fusetest.py\n')
	print('Mounting ' + mntpoint + '\n')
	if targetfs == 'xv6fs':
		option = '-s'
	toolpath = pjoin(basepath, 'specificfuse', targetfs, 'fs') 
	initimgpath = pjoin(basepath, 'specificfuse', targetfs, initimg)
	mntcmd = toolpath + ' ' + initimgpath + ' ' + option + ' ' + mntpoint
	print(mntcmd)
	subprocess.Popen(mntcmd, stdout=subprocess.PIPE,
					 universal_newlines=True, shell=True)

def userumount(mntpoint):
	print('running userumount() in fusetest.py\n')
	print('unmounting ' + mntpoint + '\n')
	subprocess.check_call(['sudo','fusermount','-u', mntpoint] )
	assert not os.path.ismount(mntpoint)
	# subprocess.check_call(['sudo', 'rm', mntpoint])

def chown(mntpoint):
	print('Running chown() in fusetest.py\n')
	print('Changing owner of ' + mntpoint + ' to root\n')
	try:
		subprocess.check_call(['sudo', 'chown', '%s.%s'%(os.getuid, os.getgid), '-R', mntpoint])
	except:
		pass

def cclogging():
	global log_file_handle 
	log_file = 'logfiles/' + time.strftime('%m%d_%H:%M:%S') + '-syscalls.log'
	log_file_handle = open(log_file, 'w')
	log_file_handle.write('STARTING LOGGing\n')

def ccgetseed():
	num = math.pow(10, 20)
	seed = int(math.pi*num)
	return seed

def ccgenerator():
	ccpi = str(ccgetseed())
	


def cctest0(mntpoint, file):
	filepath = pjoin(mntpoint, file)
	fobj = open(filepath, 'a')
	fobj.write('---------s')
	fd = fobj.fileno()
	print('fd = ' + str(fd))
	fobj1 = open(filepath, 'r')
	# fobj.close()
	fd1 = fobj1.fileno()
	# print('\nreading fobj: ' + fobj.read())
	print('\nreading fobj1: ' + fobj1.read())
	#文件指针到尾部了，读不到数据
	print('\nreading fobj1: ' + fobj1.read())
	print("\nfd1 = " + str(fd1) + '\n')
	fobj2 = open(filepath, 'a')
	fobj2.write('opening file again\n')
	fd2 = fobj2.fileno()
	# print('\nreading fobj2: ' + fobj2.read())
	print('\nfd2 = ' + str(fd2))
	# fobj2.close()
	# time.sleep(3)
	# fobj2追加写并关闭后写入硬盘，文件指针正好指到fbj2开始的地方
	# fobj2未关闭，则只保存在内存中，文件指针已经读到最后了，再继续读只能返回空
	print('\nreading fobj1: ' + fobj1.read())
	fobj3 = open(filepath, 'r')
	fd3 = fobj3.fileno()
	# print('\nreading fobj: ' + fobj.read())
	print('\nreading fobj3: ' + fobj3.read())

def cctest(mntpoint, file):
	filepath = pjoin(mntpoint, file)
	fo = open(filepath, 'a')
	fd = fo.fileno()
	fo.write('fd0 is writing\n')
	print("fd0 = " + str(fd))
	fo.close()
	fo1 = open(filepath, 'r')
	fd1 = fo1.fileno()
	buf = fo1.read()
	print("fd1 = " + str(fd1))
	print('\n' + buf)
	
	fo2 = open(filepath, 'a')
	fd2 = fo2.fileno()
	fo2.write('fd2 is writing\n')
	print("fd2 = " + str(fd2))




if __name__ == '__main__':
	mntpnt = '/mnt/ext3pnt' 
	global log_file_handle
	# cclogging()
	# cctest(mntpnt, 'file2')
	ccgenerator()
	'''
	# 挂载用户态文件系统
	mnt_dir = tempfile.mkdtemp()

	usermount('xv6fs', 'fs.img', mnt_dir)
	chown(mnt_dir)
	
	# 写操作 测试
	file1 = pjoin(mnt_dir, 'file1')
	buf = 'abcdefg'
	testwrite(file1, buf)
	userumount(mnt_dir)

	# 链接操作 测试
	testfile = 'file2'
	testslink = 'file2_symlink'
	testslink2 = 'file2_symlink2'
	# 软链接 测试
	ccsflink(mntpnt, testfile, testslink)
	# 硬链接 测试
	ccsflink(mntpnt, testslink, testslink2)
	
	# 目录操作 测试
	testfile = 'file1'
	ccmkdir(mntpnt, 'subdir')
	time.sleep(1)
	ccremove(mntpnt, 'file3')
	time.sleep(1)
	ccmkdir(mntpnt, 'subdir/subsubdir')
	time.sleep(1)
	ccremove(mntpnt, 'subdir/subsubdir')
	
	test_buffer = 'hello_nothing_imporant writing to file1 and file2'
	cccreat(mntpnt, 'file1')
	ccwrite(mntpnt, 'file1', test_buffer.encode())
	ccwrite(mntpnt, 'file2', test_buffer.encode())
	ccsflink(mntpnt, 'file2', 'file2_symln')
	cchdlink(mntpnt, 'file2', 'file2_hdln')
	cchdlink(mntpnt, 'file2_hdln', 'file2_hdln2')
	ccrename(mntpnt, 'file2', 'file2_fake')
	ccremove(mntpnt, 'file2_hdln')
	ccremove(mntpnt, 'file2_hdln2')

	buf = ccread(mntpnt, 'file1')
	print("reading buf = " + buf.decode()+ "\n")
	ccappend(mntpnt, 'file6', buf, True)
	'''
	
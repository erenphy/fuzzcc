"""
	global variables defination
"""

from multiprocessing import JoinableQueue
from queue import Queue
from distutils.filelist import FileList
import enum, os
from enum import IntEnum
import logging
import time
import threading

# mkfs 所在路径
MKFS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "specificfs", "xv6fs", "mkfs")

# 日志记录相关，不知道为什么basicConfig它给我报错，就注释掉了
log_file = time.strftime('%m%d_%H:%M:%S') + '-syscalls.log'
# logging.basicConfig(filename=log_file, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 暂时设置超时时间为 4
OUT_OUT_TIME = 4
# 参数长度，对
ARG_LENGTH = 3

COUNT = 0

# 测试用例队列
# TESTCASE_QUEUE = Queue()
TESTCASE_QUEUE = JoinableQueue()

# 种子队列
SEED_QUEUE = JoinableQueue() 
# SEED_QUEUE = Queue() 
# 每条调用序列
SYSCALLS = []
#互斥锁
MUTEX = threading.Lock()

# log_file_handle = open(log_file, 'w')
# log_file_handle.write('STARTING LOGGing\n')

# 用16进制
@enum.unique
class ops(IntEnum):
	CREAT = 0
	WRITE = 1
	APPEND = 2
	READ = 3
	HARDLN = 4
	SOFTLN = 5
	REMOVE = 6
	MKDIR= 7
	SYNC = 8
	RENAME = 9
# 常量 一次赋值
OPS_LENGTH = len(list(ops))
DIR_FULL_SIZE = 15
INIT_TIME_MAX = 5
INIT_TIME_MIN = 3
SMALL_DATA = 'abcdefgijklmnopqrst1234567890asdfghjkl;zxcvbnmqwertyuopifromLXH'
BIG_DATA = 'a very very huge data size, waiting for appending, perheps from file'
# 作为系统调用的参数：file/dir
MY_FILE_LIST = ['foo', 'bar', 'baz']
MY_DIR_LIST = ['./', './A']

# 作为系统调用的参数：other
MY_MNT_POINT = '/mnt/ext3' 

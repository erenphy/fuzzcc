from multiprocessing import JoinableQueue
from queue import Queue
from distutils.filelist import FileList
import enum, os
from enum import IntEnum
import time
# global variables defination

# 测试用例队列
# TESTCASE_QUEUE = Queue()
TESTCASE_QUEUE = JoinableQueue()


# 种子队列
SEED_QUEUE = JoinableQueue() 
# SEED_QUEUE = Queue() 
# 每条调用序列
SYSCALLS = []

# 日志文件句柄
global log_file_handle 
log_file = './logfiles/' + time.strftime('%m%d_%H:%M:%S') + '-syscalls.log'
log_file_handle = open(log_file, 'w')
log_file_handle.write('STARTING LOGGing\n')

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

if __name__ == '__main__':
	print('hhhh')

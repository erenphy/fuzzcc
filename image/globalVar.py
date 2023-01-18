"""
    global variables defination
"""

from multiprocessing import JoinableQueue
from queue import Queue
from distutils.filelist import FileList
import enum, os
from enum import IntEnum
import logging
from time import strftime

# mkfs 所在路径
MKFS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../specificfs", "xv6fs", "mkfs")

# 日志记录相关
log_file = os.path.join("logfiles", strftime('%m%d_%H:%M:%S') + '-syscalls.log' ) 
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 暂时设置超时时间为 4
TIME_OUT = 10
# 参数长度
ARG_LENGTH = 3

# 文件系统镜像文件所在目录
IMAGES_DIR = "images"

# 全局计数器
GLOBAL_COUNT = 1

COUNT = 0

# 测试用例队列
TESTCASE_QUEUE = Queue()
# TESTCASE_QUEUE = JoinableQueue()
TESTCASE_QUEUE.put([['creat','./A/foo'],['sync'],['creat','A/bar'],['fsync','A']])
TESTCASE_QUEUE.put([['hardlink',['foo','bar']],['sync'],['remove','bar'],['creat','bar'],['fsync','bar']])
# 种子队列
# SEED_QUEUE = JoinableQueue() 
SEED_QUEUE = Queue() 
# 每条调用序列
SYSCALLS = []

# log_file_handle = open(log_file, 'w')
# log_file_handle.write('STARTING LOGGing\n')

# 用16进制
# 新增加了fsync和unlink
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
    FSYNC = 10
# 常量 一次赋值
OPS_LENGTH = len(list(ops))
DIR_FULL_SIZE = 15
INIT_TIME_MAX = 20
INIT_TIME_MIN = 10
SMALL_DATA = 'abcdefgijklmnopqrst1234567890asdfghjkl;zxcvbnmqwertyuopifromLXH'
BIG_DATA = 'a very very huge data size, waiting for appending, perheps from file'
# 作为系统调用的参数：file/dir
# MY_FILE_LIST = ['foo', 'bar', 'baz']
MY_FILE_LIST = ['foo', 'bar']
MY_DIR_LIST = ['./', './A']

MY_RECORD_LIST = Queue()

# 作为系统调用的参数：other
MY_MNT_POINT = '/mnt/ext3' 

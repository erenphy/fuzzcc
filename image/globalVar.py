"""
    global variables defination
"""

from multiprocessing import JoinableQueue
from queue import Queue
from distutils.filelist import FileList
import enum, os
from enum import IntEnum,auto
import logging
from time import strftime

# mkfs 所在路径
# MKFS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../specificfs", "xv6fs", "mkfs")
MKFS_PATH_PREFIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../specificfs")

# 日志记录相关
log_file = os.path.join("logfiles", strftime('%m%d_%H:%M:%S') + '-syscalls.log' ) 
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 暂时设置超时时间为 4
TIME_OUT = 10
# 产生序列的最大长度
ARG_LENGTH = 3

# 文件系统镜像文件所在目录
IMAGES_DIR = "images"

# 全局计数器,用作测试用例数目
GLOBAL_COUNT = 0
# 用作变异次数计数
GLOBAL_MUTATION_COUNT = 0
# 用作初始种子生成计数 
GLOBAL_SEED_COUNT = 0
# 用作发现的crash计数，同时还是反馈的新种子计数
GLOBAL_CRASH_COUNT = 0
# 总的种子池为seed_count + crash_count


# 测试用例队列
TESTCASE_QUEUE = Queue()
# TESTCASE_QUEUE = JoinableQueue()
TESTCASE_QUEUE.put([['creat','./A/foo'],['sync'],['creat','./A/bar'],['fsync','./A']])
TESTCASE_QUEUE.put([['hardlink',['./foo','./bar']],['sync'],['remove','./bar'],['creat','./bar'],['fsync','./bar']])
TESTCASE_QUEUE.put([['write',['./foo','9']],['sync'],['fsync','./foo']])
TESTCASE_QUEUE.put([['creat','./A/foo'],['sync'],['creat','./A/bar'],['fsync','./A']])
TESTCASE_QUEUE.put([['hardlink',['./foo','./bar']],['sync'],['remove','./bar'],['fsync','./foo']])
TESTCASE_QUEUE.put([['creat','./A/foo'],['sync'],['rename', ['./A','./B']],['mkdir','./A'],['fsync','./A']])
TESTCASE_QUEUE.put([['rename',['./foo','./bar']],['creat','./foo'],['fsync','./bar']])
TESTCASE_QUEUE.put([['creat','./foo'],['fsync','./foo'],['write',['./foo','9']],['fsync','./foo']])
TESTCASE_QUEUE.put([['hardlink',['./foo','./A/foo']], ['hardlink',['./bar','./A/bar']],['fsync','./bar']])
# generic 107 
TESTCASE_QUEUE.put([['hardlink',['./foo','./A/foo']],['hardlink',['./foo','./A/bar']],['sync'],['remove', './A/bar'], ['fsync','./foo']])
# generic 321
TESTCASE_QUEUE.put([['rename',['./foo','./A/foo']],['fsync','./A'],['fsync', './A/foo']])
# generic 322
TESTCASE_QUEUE.put([['rename',['./A/foo','./A/bar']],['fsync','./A/bar']])
# generic 335
TESTCASE_QUEUE.put([['rename',['./A/foo','./foo']],['creat','./bar'],['fsync','.']])
# generic 336
TESTCASE_QUEUE.put([['hardlink',['./A/foo','./B/foo']],['creat','./B/bar'],['sync'],['remove','./B/foo'],['rename',['./B/bar','C/bar']],['fsync','./A/foo']])
# generic 343
TESTCASE_QUEUE.put([['hardlink',['./A/foo','./A/bar']],['rename',['./B/baz','./A/baz'],['fsync', './A/foo']]])

# 种子队列
# SEED_QUEUE = JoinableQueue() 
SEED_QUEUE = Queue() 
# 每条调用序列
SYSCALLS = []

# log_file_handle = open(log_file, 'w')
# log_file_handle.write('STARTING LOGGing\n')

# 用16进制
# 新增加了fsync和unlink和rmdir
@enum.unique
class ops(IntEnum):
    CREAT = 0
    WRITE = 1
    READ = 2
    REMOVE = 3
    MKDIR = 4
    RENAME = 5
    UNLINK = 6
    RMDIR = 7
    APPEND = 8
    HARDLN = 9
    SOFTLN = 10
    SYNC = 11
    FSYNC =12

# 常量 一次赋值
OPS_LENGTH = len(list(ops))
DIR_FULL_SIZE = 15

# 可修改，确定初始生成种子池的大小
INIT_TIME_MAX = 40
INIT_TIME_MIN = 20

SMALL_DATA = 'abcdefgijklmnopqrst1234567890asdfghjkl;zxcvbnmqwertyuopifromLXH'
BIG_DATA = 'a very very huge data size, waiting for appending, perheps from file'
# 作为系统调用的参数：file/dir
# MY_FILE_LIST = ['./foo', './bar', './baz']
MY_FILE_LIST = ['foo', 'bar','baz']
MY_DIR_LIST = ['./', './A']

# MY_RECORD_LIST = Queue()

# 作为系统调用的参数：other
MY_MNT_POINT = '/mnt/ext3' 

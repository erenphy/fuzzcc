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
import logging
import threading

# my own module.py
import ccsyscalls
import globalVar
from globalVar import SEED_QUEUE
# ccgenerator.py: 生成初始测试用例集合
# 	main-func: ccgenerator(max_length)

# FIXME 待完善
class Generator(threading.Thread):
    def __init__(self, thread_name, arg_length):
        super(Generator, self).__init__(name=thread_name)
        self.length=arg_length
    
    def run(self):
        print(f"[+] {self.name} working...")
        global SEED_QUEUE
        # 初始测试用例随机数目
        init_size = randint(globalVar.INIT_TIME_MIN, globalVar.INIT_TIME_MAX)
        print("\nInit seedpool size = " + str(init_size))
        logging.debug(f"Totally Seeds generated count = : {init_size}")
        while init_size:
            # 每条测试用例的长度随机生成
            # print("\ninit seedpool countdown" + str(init_size))
            cur_queue = []
            cur_length = randint(1,self.length)
            # 0118:追踪过程中产生的新目录/文件，指导下一个文件操作的参数
            cur_exist_file = []
            cur_exist_dir = []
            # print("\ncur_length = " + str(cur_length))
            while cur_length:
                # rdm = randint(0, 7)
                rdm = randint(0, globalVar.ARG_LENGTH - 1)
                # print("\nrandom globalVar.ops.= " + str(rdm))
                syscall_kv = []
                if rdm == globalVar.ops.CREAT:
                    # print("\ncreating files")
                    cur_op = 'creat'
                    cur_name = ccgene_file()
                    cur_exist_file.append(cur_name)
                    syscall_kv = [cur_op, cur_name]
                    # ccsyscalls.cccreat(globalVar.MY_MNT_POINT, cur_para)
                elif rdm == globalVar.ops.APPEND:
                    cur_op = 'append'
                    if cur_exist_file:
                        cur_name = random.choice(cur_exist_file)
                    else:
                        cur_name = ccgene_file()
                        cur_exist_file.append(cur_name)
                    # cur_name = ccgene_file()
                    cur_para = ccgene_wt_para()
                    syscall_kv = [cur_op, cur_name, cur_para]
                    # ccsyscalls.ccappend(globalVar.MY_MNT_POINT, cur_name, cur_para)
                elif rdm == globalVar.ops.HARDLN:
                    cur_op = 'hardlink'
                    cur_name1 = ccgene_file()
                    cur_name2 = ccgene_file()
                    # name1最好存在，不存在的话在syscall里会创建 这里就不判断了
                    cur_exist_file.append(cur_name1)
                    cur_exist_file.append(cur_name2)
                    syscall_kv = [cur_op, [cur_name1, cur_name2]]
                    # ccsyscalls.cchdlink(globalVar.MY_MNT_POINT, cur_name)
                elif rdm == globalVar.ops.MKDIR:
                    cur_op = 'mkdir'
                    cur_name = ccgene_dir()
                    cur_exist_dir.append(cur_name)
                    syscall_kv = [cur_op, cur_name]
                    # ccsyscalls.ccmkdir(globalVar.MY_MNT_POINT, cur_name)
                elif rdm == globalVar.ops.READ:
                    cur_op = 'read'
                    if cur_exist_file:
                        # 读一些现有的文件
                        cur_name = random.choice(cur_exist_file)
                    else:
                        cur_name = ccgene_file()
                        cur_exist_file.append(cur_name)
                    syscall_kv = [cur_op, cur_name]
                    # ccsyscalls.ccread(globalVar.MY_MNT_POINT, cur_name)
                elif rdm == globalVar.ops.REMOVE:
                    cur_op = 'remove'
                    # 相当于unlink file, 
                    if cur_exist_file:
                        cur_name = random.choice(cur_exist_file)
                    else:
                        cur_name = ccgene_file()
                        cur_exist_file.append(cur_name)
                    syscall_kv = [cur_op, cur_name]
                    # ccsyscalls.ccremove(globalVar.MY_MNT_POINT, cur_name)
                elif rdm == globalVar.ops.UNLINK:
                    # lxh:删除文件
                    cur_op = 'unlink'
                    if cur_exist_file:
                        cur_name = random.choice(cur_exist_file)
                    else:
                        cur_name = ccgene_file()
                        cur_exist_file.append(cur_name)
                    syscall_kv = [cur_op, cur_name]
                    # ccsyscalls.ccunlink(globalVar.MY_MNT_POINT, cur_name)
                elif rdm == globalVar.ops.RMDIR:
                    # lxh:删除文件
                    cur_op = 'rmdir'
                    if cur_exist_dir:
                        cur_name = random.choice(cur_exist_dir)
                    else:
                        cur_name = ccgene_dir()
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
                    if cur_name[0] == cur_name1:
                        cur_exist_file.append(cur_name2)
                    syscall_kv = [cur_op, cur_name]
                    # ccsyscalls.ccrename(globalVar.MY_MNT_POINT, cur_name1, cur_name2)
                elif rdm == globalVar.ops.SOFTLN:
                    cur_op = 'softlink'
                    if cur_exist_file:
                        cur_name1 = random.choice(cur_exist_file)
                    else:
                        cur_name1 = ccgene_file()
                        cur_exist_file.append(cur_name1)
                    # cur_name1 = ccgene_file()
                    cur_name2 = ccgene_file()
                    cur_exist_file.append(cur_name2)
                    cur_name3 = ccgene_dir()
                    # 可能是给目录建立软连接 也可能是文件
                    cur_name4 = random.choice([cur_name1, cur_name3])
                    cur_name = [cur_name4, cur_name2]
                    syscall_kv = [cur_op, cur_name]
                    # ccsyscalls.ccsflink(globalVar.MY_MNT_POINT,cur_name)
                elif rdm == globalVar.ops.SYNC:
                    cur_op = 'sync'
                    syscall_kv = [cur_op]
                elif rdm == globalVar.ops.WRITE:
                    cur_op = 'write'
                    if cur_exist_file:
                        cur_name = random.choice(cur_exist_file)
                    else:
                        cur_name = ccgene_file()
                        cur_exist_file.append(cur_name)
                    # cur_name = ccgene_file()
                    cur_para = ccgene_wt_para()
                    syscall_kv = [cur_op, cur_name, cur_para]
                    # ccsyscalls.ccwrite(globalVar.MY_MNT_POINT, cur_name, cur_para)
                elif rdm == globalVar.ops.FSYNC:
                    cur_op = 'fsync'
                    if cur_exist_file:
                        cur_name = random.choice(cur_exist_file)
                        syscall_kv = [cur_op, cur_name]
                    else:
                        pass
                    # logging.debug(f"FSYNCing---cur_exist_file: {cur_exist_file}")
                    # syscall_kv = [cur_op, cur_name]
                else: pass
                # cur_length = cur_length - 1
                if syscall_kv:
                    cur_queue.append(syscall_kv)
                    cur_length = cur_length - 1
                # if syscall_kv:
                #    cur_length = cur_length - 1
                #    cur_queue.append(syscall_kv)
                # else: 
                #    print("likely fsync error\n")
            init_size = init_size - 1
            # logging.debug(f"cur_exist_file: {cur_exist_file}")
            logging.debug(f"cur_queue: {cur_queue}")
            globalVar.SEED_QUEUE.put(cur_queue)

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
#	out = _x.xeger(r'(\./[AB](/[CD](/[EF])?)?)')
#    out = _x.xeger(r'(\./[AB](/[CD])?)')
    out = _x.xeger(r'(\./[AB](/C)?)')
    
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

from os import pread
import random
from os.path import join as pjoin
from queue import Queue
import os
import copy
import time
from random import randint
import ccgenerator
import threading
import globalVar
from globalVar import SEED_QUEUE, TESTCASE_QUEUE, GLOBAL_MUTATION_COUNT, ARG_LENGTH

# 用于种子变异
# 种子池 pop
# 测试用例集合 push(种子+种子变异生成的testcase)

class Mutator(threading.Thread):
    def __init__(self, thread_name, fuzzer_event):
        super(Mutator, self).__init__(name=thread_name)
        self.event = threading.Event()
        self.fuzzer_event = fuzzer_event

    def run(self):
        print(f"[+] {self.name} working...")
        global SEED_QUEUE
        global TESTCASE_QUEUE
        while True:
            print("[-] mutator: getting SEED_QUEUE")
            # 一次性把种子队列里头的种子都取出来，然后阻塞等待信号
            while not SEED_QUEUE.empty():
                cur_seed = SEED_QUEUE.get()
                # if cur_seed == None: break
                # TESTCASE_QUEUE.put(copy.deepcopy(cur_seed))
                ccmutate_syscalls(TESTCASE_QUEUE, cur_seed)
                self.fuzzer_event.set()
            # 阻塞等待信号
            if not self.event.wait(timeout=globalVar.TIME_OUT):
                if TESTCASE_QUEUE.empty():
                    break
                time.sleep(1)
            self.event.clear()
        print("[-] Mutator work done.")
        print("Mutation counts = " + str(GLOBAL_MUTATION_COUNT))
        # globalVar.logging.debug(f"Totally Mutation counts = : {GLOBAL_MUTATION_COUNT}")


def ccmutate_wtname(file):
    # print("ccmutate_wtname() is running\n")
    pre_path = file.rsplit("/", 1)[0]
    post_file = file.rsplit("/", 1)[1]
    # print(post_file)
    bro_list = copy.deepcopy(globalVar.MY_FILE_LIST)
    if post_file in bro_list:
        bro_list.remove(post_file)
    bro = random.choice(bro_list)
    bro = pjoin(pre_path, bro)
    return bro

# totally 没有知识的变异
def ccmutate_wtpara(para_num):
    # print("ccmutate_wtpara() is running\n")
    ccnot = para_num ^ 0b1101
    return ccnot

def ccmutate_dir(dirpath):
    # print("ccmutate_dir(dirpath) is running\n")
    new_dir = ccgenerator.ccgene_dir()
    if new_dir == dirpath:
        # 运气不至于这么差，两次gene结果都一样
        new_dir = ccgenerator.ccgene_dir()
    return new_dir

# 例子：syscall_list  = [['hardlink',['./foo','./bar']],['sync'],['remove','./bar'],['creat','./bar'],['fsync','./bar']])
# 把变异后的每一个追加到testcaseq中
def ccmutate_syscalls(testcaseq, syscall_list):
    syscall_len = len(syscall_list)
    global GLOBAL_MUTATION_COUNT
    # 变异1：随机变换操作序列顺序
    rdmtime = randint(0, syscall_len - 1)
    if syscall_len >= 3:
        rdmtime +=2
    while rdmtime:
        random.shuffle(syscall_list)
        cur_syscalls = copy.deepcopy(syscall_list)
        testcaseq.put(cur_syscalls)
        GLOBAL_MUTATION_COUNT += 1
        # print("mutation 1 : counts = " + str(GLOBAL_MUTATION_COUNT))
        rdmtime = rdmtime - 1
    if syscall_len > ARG_LENGTH - 1:
        # 太长的话就不进来这个了
        pass
    else:
        # 变异2：顺序加入检查点
        rdmidx = randint(0, syscall_len - 1)
        for i in range(1, syscall_len - 1):
            filename = ccgenerator.ccgene_file()
            fsyncpnt = ['fsync', filename]
            syncpnt = ['sync']
            ckpnt = random.choice([fsyncpnt,syncpnt])
            syscall_list.insert(rdmidx, ckpnt)
            cur_syscalls = copy.deepcopy(syscall_list)
            testcaseq.put(cur_syscalls)
            GLOBAL_MUTATION_COUNT += 1
        # print("mutation 2 : counts = " + str(GLOBAL_MUTATION_COUNT))
        # 变异3：变异参数
        for syscall in syscall_list:
            if syscall[0] == 'write' or syscall[0] == 'append':
                syscall[1] = ccmutate_wtname(syscall[1])
                syscall[2] = ccmutate_wtpara(syscall[2])
            elif syscall[0] == 'hardlink' or syscall[0] == 'softlink':
                syscall[1][1] = ccmutate_wtname(syscall[1][1])
            elif syscall[0] == 'mkdir':
                syscall[1] = ccmutate_dir(syscall[1])
            elif syscall[0] == 'remove':
                if syscall[1].rsplit("/", 1)[1] in globalVar.MY_FILE_LIST:
                    syscall[1] = ccmutate_wtname(syscall[1])
                else: syscall[1] = ccmutate_dir(syscall[1])
            elif syscall[0] == 'unlink':
                syscall[1] = ccmutate_wtname(syscall[1])
            elif syscall[0] == 'rmdir':
                syscall[1] = ccmutate_dir(syscall[1])
            elif syscall[0] == 'rename':
                # 判断操作数是目录还是文件
                if not syscall[1][0].rsplit("/", 1)[1] in globalVar.MY_FILE_LIST:
                    syscall[1][1] = ccmutate_dir(syscall[1][1])
                else: syscall[1][1] = ccmutate_wtname(syscall[1][1])
            elif syscall[0] == 'fsync':
                syscall[1] = ccmutate_wtname(syscall[1])
            else:
                # 只给write和append变异参数
                pass
        cur_syscalls = copy.deepcopy(syscall_list)
        testcaseq.put(cur_syscalls)
        GLOBAL_MUTATION_COUNT += 1
        # print("mutation 3 : counts = " + str(GLOBAL_MUTATION_COUNT))
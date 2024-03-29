
import threading
import copy
import tempfile
import time
import csv
from datetime import datetime
from globalVar import *
import globalVar
import ccparser
import ccmounter
from cctools import file_md5_hash
from ccinit import init_fs

class Fuzzer(threading.Thread):
    def __init__(self, thread_name, iskfs, fstype, event):
        super(Fuzzer, self).__init__(name=thread_name)
        self.iskfs = iskfs
        self.fstype = fstype
        self.event = event
        self.done = threading.Event()

    def run(self):
        logging.critical(f"[+] {self.name} working...")
        global SEED_QUEUE
        global TESTCASE_QUEUE
        global TABLEINFO
        while True:
            # 一次性把种子队列里头的种子都取出来，然后阻塞等待信号
            while not TESTCASE_QUEUE.empty() and not self.done.is_set():
                cur_seq = TESTCASE_QUEUE.get()
                # print('current seq')
                # print(cur_seq)
                cur_result = runner(self.iskfs, self.fstype, cur_seq)
                if cur_result == 1:
                # 比较的目标和伴随文件系统出现了不一致，则不需要进行目标文件系统和顺序文件系统的比较了
                # 也就不会进入下边的if
                    morecmp_signal = 0
                # else: 
                    # 没有发现不一致，把cur_seq从testcasequeue中移除就好了  
                    # TODO: 怎么移除  --> queue的get操作是取出（直接删掉头部元素并返回，不需要移除
            if self.done.is_set():
                break
            logging.warning("Fuzz done. Waitting...")
            # 阻塞等待信号
            if not self.event.wait(timeout=TIME_OUT):
                break
            self.event.clear()

            # # 在现存的testcase上重新执行
            # if morecmp_signal == 1:
            #     while not TESTCASE_QUEUE.empty():
            #         cur_seq = TESTCASE_QUEUE.get()
            #         cur_result = morerunner(self.iskfs, self.fstype, cur_seq)
            #         if cur_result == 1:
            #             # 比较的目标和顺序文件系统执行不一致，则不具备strictly consistency,设置信号/flag
            #             # TODO: 写日志 给出最后结果，可以把下面的输出保存到logfile里？或者程序界面
            #             strict_signal = 0
            #             print('stopped!relatively consistency\n')
            #     if strict_signal == 0:
            #         print('well done! strictly consistency\n')
            # print("the end+++++++++++++++++++")
        logging.warning("[-] Fuzzer work done.")
        # print("Crash counts = " + str(GLOBAL_CRASH_COUNT))
        # # print("Seeds generated counts = " + str(GLOBAL_CRASH_COUNT + GLOBAL_SEED_COUNT))
        # print("Testcases counts = " + str(GLOBAL_COUNT))
        # logging.critical(f"Totally Testcases count = : {GLOBAL_COUNT}")
        # logging.critical(f"Totally Crash count = : {GLOBAL_CRASH_COUNT}")
        # # logging.debug(f"Totally Seeds generated count = : {GLOBAL_CRASH_COUNT + GLOBAL_SEED_COUNT}")
        # TABLEINFO.add_row("Totally Testcases count", str(GLOBAL_COUNT))
        # TABLEINFO.add_row("Totally Crash count", str(GLOBAL_CRASH_COUNT))

    def stop(self):
        self.done.set()
        self.event.set()

# runner() input为单个操作序列， output为执行后的镜像
def runner(is_kernelfs, fs_type, input):
    global GLOBAL_COUNT
    # 初始化文件系统镜像
    # 用法: init_fs(fs01_filename, fs02_filename, init_files)
    init_files = " ".join(["init.txt"])   # 这里初始化的文件要能让脚本找到
    target_img = os.path.join(IMAGES_DIR, f"{GLOBAL_COUNT}.img")
    adjoint_img = os.path.join(IMAGES_DIR, f"{GLOBAL_COUNT}_adjoint.img")
    GLOBAL_COUNT += 1
    globalVar.add_value("TOTAL_PATH")
    global GLOBAL_CRASH_COUNT
    # lxh0120:增加参数fstype
    init_fs(fs_type, target_img, adjoint_img, init_files)
    
    # 使用 ccmounter 挂载生成的文件系统
    if is_kernelfs == '1':
        #这里先不实现内核文件系统测试
        return
    elif is_kernelfs == '0':
        # 用户态文件系统测试
        # 生成挂载目录
        target_mnt = tempfile.mkdtemp()
        adjoint_mnt = tempfile.mkdtemp()
        seq_mnt = tempfile.mkdtemp()
        # print('mount target dir: ' + target_mnt)
        # print('mount adjoint dir: ' + adjoint_mnt)
        # 暂时不实现挂载第三个系统
        # print('mount sequential dir: ' + seq_mnt)

        # 挂载镜像到目录
        # usermount(specific fs path, img, mntdir,options(可选))
        ccmounter.usermount(fs_type, target_img, target_mnt)
        ccmounter.usermount(fs_type, adjoint_img, adjoint_mnt)
        # parser 解释执行input
        # print("[+] Starting parser......\n")
        # lxh:目标文件系统上执行完立即解挂
        ccparser.cc_parser(target_mnt, input)
        ccparser.cc_parser(adjoint_mnt, input)
        ccmounter.userumount(target_mnt)
        
        #lxh:伴随文件系统上 停1秒再解挂
        # ccparser.cc_parser(adjoint_mnt, input)
        # ccmounter.userumount(target_mnt)
        # time.sleep(1)
        ccmounter.userumount(adjoint_mnt)
        
        # lxh: 重新挂载 允许目标文件系统进行崩溃恢复
        # need to fix :执行下面两个挂载的话，会报错device busy。很奇怪明明上边已经解除挂载了
        # ccmounter.usermount(fs_type, target_img, target_mnt)
        # ccmounter.usermount(fs_type, adjoint_img, adjoint_mnt)
        

        # 执行后调用hash校验对比两个img文件hash, 如果不一致则保存现场数据
        if file_md5_hash(target_img) != file_md5_hash(adjoint_img):
            logging.error("Error: target_img and adjoint_img are not the same\n")
            # 设置发现不一致的信号
            diff_signal = 1
            GLOBAL_CRASH_COUNT += 1
            globalVar.add_value("UNIQ_CRASHES")
            SEED_QUEUE.put(input)
            globalVar.add_value("SEED_COUNT")
            globalVar.set_value("LAST_CRASH_TIME", datetime.now().timestamp()) 
            # 将当前镜像target_img 和 adjoint_img的路径、和 input记录到logfile的一行
            logging.info(f"logging path -- target_img: {target_img}; adjoint_img: {adjoint_img}; input: {input}")
            with open(globalVar.get_value("CSV_NAME"), "a+") as f:
                row_data = [f"{GLOBAL_COUNT}", f"{input}", f"{target_img}", f"{adjoint_img}"]
                writer = csv.writer(f)
                writer.writerow(row_data)
                f.close()

            # 还得删除，不然大实验跑不动
            umount_and_remove_path(target_img, target_mnt, adjoint_img, adjoint_mnt)

        else:
            diff_signal = 0
            umount_and_remove_path(target_img, target_mnt, adjoint_img, adjoint_mnt)
        
    return diff_signal

def umount_and_remove_path(target_img, target_mnt, adjoint_img, adjoint_mnt):
    while True:
        try:
            # 删除当前的镜像 target_img 和 adjoint_mnt
            if os.path.exists(target_img):
                os.remove(target_img)
            if os.path.exists(adjoint_img):
                os.remove(adjoint_img)
            # 删除生成的随机目录： target_mnt和adjoint_mnt
            if os.path.exists(target_mnt):
                os.rmdir(target_mnt)
            if os.path.exists(adjoint_mnt):
                os.rmdir(adjoint_mnt)
            break
        except OSError as e:
            logging.error("%s - %s. Retrying..." % (e.filename, e.strerror))
            ccmounter.userumount(e.filename)
            time.sleep(0.5)

def morerunner(is_kernelfs, fs_type, input):
    diff_signal = 0
    # 暂时没找到合适的顺序文件系统，暂不实现
    return diff_signal
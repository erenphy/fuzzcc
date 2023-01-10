
import threading
import copy
import tempfile
from globalVar import *
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

    def run(self):
        print(f"[+] {self.name} working...")
        global SEED_QUEUE
        global TESTCASE_QUEUE
        while True:
            # 一次性把种子队列里头的种子都取出来，然后阻塞等待信号
            while not TESTCASE_QUEUE.empty():
                cur_seq = TESTCASE_QUEUE.get()
                cur_result = runner(self.iskfs, self.fstype, cur_seq)
                if cur_result == 1:
                # 比较的目标和伴随文件系统出现了不一致，则不需要进行目标文件系统和顺序文件系统的比较了
                # 也就不会进入下边的if
                    morecmp_signal = 0
                # else: 
                    # 没有发现不一致，把cur_seq从testcasequeue中移除就好了  
                    # TODO: 怎么移除  --> queue的get操作是取出（直接删掉头部元素并返回，不需要移除
            logging.warning("Fuzz done. Waitting...")
            # 阻塞等待信号
            self.event.wait()
            self.event.clear()

            # # 在现存的testcase上重新执行
            # if morecmp_signal == 1:
            #     for cur_seq in TESTCASE_QUEUE:
            #         cur_result = morerunner(iskfs, fstype, cur_seq)
            #         if cur_result == 1:
            #             #比较的目标和顺序文件系统执行不一致，则不具备strictly consistency,设置信号/flag
            #             #TODO: 写日志 给出最后结果，可以把下面的输出保存到logfile里？或者程序界面
            #             strict_signal = 0
            #             print('stopped!relatively consistency\n')
            #     if strict_signal == 0:
            #         print('well done! strictly consistency\n')
            # print("the end+++++++++++++++++++")


# runner() input为单个操作序列， output为执行后的镜像
def runner(is_kernelfs, fs_type, input):
    # 初始化文件系统镜像
    # init_fs(fs01_filename, fs02_filename, init_files)
    init_files = " ".join(["init.txt"])   # 这里初始化的文件要能让脚本找到
    target_img = os.path.join(IMAGES_DIR, f"{GLOBAL_COUNT}.img")
    adjoint_img = os.path.join(IMAGES_DIR, f"{GLOBAL_COUNT}_adjoint.img")
    init_fs(target_img, adjoint_img, init_files)
    
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
        print('mount target dir: ' + target_mnt)
        print('mount adjoint dir: ' + adjoint_mnt)
        # 暂时不实现挂载第三个系统
        # print('mount sequential dir: ' + seq_mnt)

        # 挂载镜像到目录
        # usermount(specific fs path, img, mntdir,options(可选))
        ccmounter.usermount(fs_type, target_img, target_mnt)
        ccmounter.usermount(fs_type, adjoint_img, adjoint_mnt)
        # for mnt_dir in [target_mnt, adjoint_mnt, seq_mnt]:
        #     ccmounter.chown(mnt_dir)
        # parser 解释执行input
        print("right here******************start parser\n")
        ccparser.cc_parser(target_mnt, input)
        ccmounter.userumount(target_mnt)
        ccmounter.usermount(fs_type, target_img, target_mnt)
        ccparser.cc_parser(adjoint_mnt, input)
        ccmounter.userumount(target_mnt)

        # 执行后调用hash校验对比两个img文件hash, 如果不一致则保存现场数据
        if file_md5_hash(target_img) != file_md5_hash(adjoint_img):
            print("Error: target_img and adjoint_img are not the same\n")
            # 设置发现不一致的信号
            diff_signal = 1

            # TODO:并将input加入seedqueue(这个加入是动态的，所以上边的初始种子和变异设置多线程阻塞，一旦mumator发现种子队列为空，阻塞等待，说不定能发现新种子)
            # 这里多线程里给seedqueue加, 可以直接用put吗?print('stopped!relatively consistency\n'),设置信号/flag
            # -- 加锁操作
            # -- 感觉种子可以考虑写文件保存起来
            SEED_QUEUE.put(input)

            # TODO 将当前镜像target_img 和 adjoint_img的路径、和 input记录到logfile的一行
            # 日志记录看一下 logging 的使用: https://docs.python.org/zh-cn/3/howto/logging.html
            logging.info(f"logging path -- target_img: {target_img}; adjoint_img: {adjoint_img}; input: {input}")

        else:
            diff_signal = 0
            #TODO 删除当前的镜像 target_img和adjoint_mnt
            #TODO 删除生成的随机目录： target_mnt和adjoint_mnt
            # 关于路径啥的python调用shell命令，我不会写
            # --> 参考： https://www.myfreax.com/python-delete-files-and-directories/
    return diff_signal

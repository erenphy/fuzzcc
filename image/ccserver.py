import os
import argparse, sys
import logging
import threading
import time
from globalVar import ARG_LENGTH
from ccgenerator import *
from ccmutator import *
from ccfuzzer import *
from cctui import *


def arg_parse():
    # 参数解析
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', dest='is_kernel_fs',help='1 for kernel-fs; 0 for usrspace-fs')
    # parser.add_argument('-T', dest='targetimg', help='the target device or img')
    # parser.add_argument('-i', dest='input', help='testcases')
    parser.add_argument('-t', dest='fs_type', help='specific fs type for kernel userspace fs')
    # parser.add_argument('-o', dest='output', help='path to save the testcaseq')

    args = parser.parse_args()

    if args.fs_type is None or not args.is_kernel_fs in ['0', '1'] :
        print('Parameter-Error, check it out\n')
        sys.exit(1)
    
    return args


    # 是否需要进一步判断目标文件系统与顺序文件系统执行的信号
    # 若目标和伴随的比较没有发现不一致，则信号设为1,需要继续比较
    # 否则，为0，不需要继续比较
def main():
    morecmp_signal = 1
    # 假设一开始具备strict-consistency
    strict_signal = 1

    args = arg_parse()
    iskfs = args.is_kernel_fs
    # targetimg = args.targetimg
    fstype = args.fs_type
    TABLEINFO.add_row("FStype", fstype)
    logging.warning("ccserver start running...")

    gene_pro = Generator("generator", ARG_LENGTH)
    gene_pro.start()
    
    fuzzer_event = threading.Event()
    muta_pro = Mutator("mutator", fuzzer_event)
    muta_pro.start()

    print("[+] Waitting for generator work done...")
    gene_pro.join()
    logging.warning("[+] Generator work done.")
    muta_pro.event.set()
    
    fuzzer = Fuzzer("fuzzer", iskfs, fstype, fuzzer_event)
    fuzzer.start()
    
    # muta_pro.join()
    # fuzzer.join()
    start_tui([muta_pro, fuzzer])


if __name__ == '__main__':
    main()
    logging.warning("[+] All work done.")
    # console.print(table)
    # console.print("------------DONE-----------")
    # console.print(tableinfo)

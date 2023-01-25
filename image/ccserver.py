import os
import argparse, sys
import logging
import threading
import time
import csv
from globalVar import ARG_LENGTH
import globalVar
from ccgenerator import *
from ccmutator import *
from ccfuzzer import *
from cctui import *

def init():
    globalVar._init()
    # Init Testcase Queue
    global TESTCASE_QUEUE
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

    # Init csv file
    CSV_NAME = os.path.join(globalVar.get_value("CSV_PATH"), "csv_" + str(randint(0, 100000)) + ".csv")
    globalVar.set_value("CSV_NAME", CSV_NAME) 
    with open(CSV_NAME, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csv_header = ["No.testcase", "Inputs", "Target_mnt", "Adjoint_mnt"]
        csvwriter.writerow(csv_header)
        csvfile.close()
    
    globalVar.set_value("WORK_STATUS", "Init Done.")

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
    globalVar.set_value("WORK_STATUS", "Fuzzing")
    
    muta_pro.join()
    fuzzer.join()
    # start_tui([muta_pro, fuzzer])


if __name__ == '__main__':
    init()
    main()
    logging.warning("[+] All work done.")
    # console.print(table)
    # console.print("------------DONE-----------")
    # console.print(tableinfo)

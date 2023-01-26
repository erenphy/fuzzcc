#!/usr/local/bin/python3
import os
from subprocess import Popen, PIPE
from cctools import file_md5_hash
from globalVar import MKFS_PATH_PREFIX
import logging


def init_fs(fs_type, fs01_filename, fs02_filename, init_files):
    MKFS_PATH = os.path.join(MKFS_PATH_PREFIX, fs_type, "mkfs")
    if fs_type == 'xv6fs':
        proc_1 = Popen(f"{MKFS_PATH} {fs01_filename} {init_files}", shell=True, stdout=PIPE, stderr=PIPE)
        proc_2 = Popen(f"{MKFS_PATH} {fs02_filename} {init_files}", shell=True, stdout=PIPE, stderr=PIPE)
    elif fs_type == 'ffs':
        proc_1 = Popen(f"{MKFS_PATH} {fs01_filename}", shell=True, stdout=PIPE, stderr=PIPE)
        proc_2 = Popen(f"{MKFS_PATH} {fs02_filename}", shell=True, stdout=PIPE, stderr=PIPE)
    else:
        pass 
    _, stderr = proc_1.communicate()
    proc_2.communicate()
    if proc_1.returncode != 0 or proc_2.returncode != 0:
        # logging.error("initError: mkfs failed")
        logging.error(f"mkfs Error, stderr: {stderr}")
        exit(1)
    if file_md5_hash(fs01_filename) != file_md5_hash(fs02_filename):
        logging.error("initError: fs01 and fs02 are not the same")
        exit(1)
    # print("[+] Init Done.")


if __name__ == "__main__":
    # init_files = " ".join(["fs.c", "hello.txt"])
    init_fs('ffs',"fs_01.img", "fs_02.img", "init.txt")

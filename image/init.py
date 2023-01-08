#!/usr/local/bin/python3
import os
from subprocess import Popen, PIPE
from hashlib import md5

MKFS_PATH = "./mkfs"

def file_md5_hash(filename):
    with open(filename, "rb") as f:
        return md5(f.read()).hexdigest()

def init_fs(fs01_filename, fs02_filename, init_files):
    proc_1 = Popen(f"{MKFS_PATH} {fs01_filename} {init_files}", shell=True, stdout=PIPE, stderr=PIPE)
    proc_2 = Popen(f"{MKFS_PATH} {fs02_filename} {init_files}", shell=True, stdout=PIPE, stderr=PIPE)
    proc_1.communicate()
    proc_2.communicate()
    if proc_1.returncode != 0 or proc_2.returncode != 0:
        print("Error: mkfs failed")
        exit(1)
    if file_md5_hash(fs01_filename) != file_md5_hash(fs02_filename):
        print("Error: fs01 and fs02 are not the same")
        exit(1)
    print("[+] Init Done.")


if __name__ == "__main__":
    init_files = " ".join(["fs.c", "hello.txt"])
    init_fs("fs_01.img", "fs_02.img", init_files)

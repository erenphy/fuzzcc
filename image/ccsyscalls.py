import os
from os.path import join as pjoin
import time
import math
import random
import subprocess

import globalVar

# 全局变量 globalVar.log_file_handle----0119这个变量被删除了
# 各种文件操作功能函数的实现
# imported by fusetest.py


# globalVar.log_file_handle = 0 定义在globalVal.py文件中
def ccfsync(mntpoint, filename):
    filepath = pjoin(mntpoint, filename)
    # if not os.path.exists(filepath):
    #     print('fsync error: path not exist\n')
    #    return
    fd = os.open(filepath, os.O_CREAT | os.O_APPEND |os.O_RDWR)
    os.fsync(fd)
def ccunlink(mntpoint, filename):
    abspath = pjoin(mntpoint, filename)
    if os.path.isfile(abspath):
        # print("unlinking file " + filename)
        os.unlink(abspath)
        # log = 'remove file ' + file + '\n'
        # globalVar.log_file_handle.write(log)
def ccrmdir(mntpoint, dir):
    abspath = pjoin(mntpoint, dir)
    if os.path.isdir(abspath):
        # print("rming dir " + dir)
        os.rmdir(abspath)

def cccreat(mntpoint, filename):
    # print("Test CREAT\n")
    filepath = pjoin(mntpoint, filename)
    # if not os.path.exists(filepath):
    if not filename in globalVar.MY_FILE_LIST:
        pre_dir = filename.rsplit("/", 1)[0]
        ccmkdir(mntpoint, pre_dir)
    if not os.path.exists(filepath):
        try:
            # print('start creat' + filepath)
            fd = open(filepath, 'x')
            # print('creat done')
            fd.close()
        except:
            # print('creat--error --------------------missing creat')
            pass
    else: 
        # print("already existed, not need creat")
        pass
        # log = 'creat ' + filename + '\n'
        # globalVar.log_file_handle.write(log)	

def ccappend(mntpoint, filename, Buf = False, Lseek = False, Fdatasync = False, Fsync = False):
    # print("Test append\n")
    filepath = pjoin(mntpoint, filename)
    fd = os.open(filepath, os.O_CREAT | os.O_APPEND |os.O_RDWR)
    if Lseek:
        pos = random.randint(0, 2)
        how = random.randint(0, 2)
        # print(str(fd))
        os.lseek(fd, pos, how)
        # print('\n new fd = ' + str(fd))
        # log = 'lseek ' + filename + ' ' + str(pos) + ' ' + str(how) + '\n'
        # globalVar.log_file_handle.write(log)
    if Buf: 
        buf = globalVar.SMALL_DATA
    else: buf = globalVar.BIG_DATA
    # print(str(fd) + '\n')
    os.write(fd, buf)
    if Fdatasync:
        os.fdatasync(fd)
        # log = 'fdatasync ' + filename + '\n'
        # globalVar.log_file_handle.write(log) 
    if Fsync:
        os.fsync(fd)
        # log = 'fsync ' + filename + '\n'
        # globalVar.log_file_handle.write(log)
    os.close(fd)
    # log = 'append ' + filename + '\n'
    # globalVar.log_file_handle.write(log)

def ccwrite(mntpoint, filename, Buf = False, Lseek = False, Fdatasync = False, Fsync = False):
    # print("Testing WRITE\n")
    filepath = pjoin(mntpoint, filename)
    openmod = os.O_RDWR |os.O_CREAT
    # if not os.path.exists(filepath):	
    #    openmod = openmod | os.O_CREAT
    fd = os.open(filepath, openmod)
    #os.write(fd, buf)
    if Lseek:
        pos = random.randint(0, 2)
        how = random.randint(0, 2)
        os.lseek(fd, pos, how)
        # log = 'lseek ' + filename + ' ' + pos + ' ' + how + '\n'
        # globalVar.log_file_handle.write(log)
    if Buf: 
        buf = globalVar.SMALL_DATA
    else: buf = globalVar.BIG_DATA
    os.write(fd, buf)
    if Fdatasync:
        os.fdatasync(fd)
        # log = 'fdatasync ' + filename + '\n'
        # globalVar.log_file_handle.write(log) 
    if Fsync:
        os.fsync(fd)
        # log = 'fsync ' + filename + '\n'
        # globalVar.log_file_handle.write(log) 
    os.close(fd)
    # log = 'write ' + filename + '\n'
    # globalVar.log_file_handle.write(log)

# return buffer
def ccread(mntpoint, filename):
    # print("Testing READ\n")
    file = pjoin(mntpoint, filename)
    # 读取软链接文件，需要找到源文件
    if os.path.islink(file):
        file = os.readlink(file)
    # 源文件不存在的话，创建文件
    if not os.path.exists(file):
        cccreat(mntpoint, file)
    fd = os.open(file, os.O_RDONLY)
    file_size = os.path.getsize(file)
    if file_size == 0:
        return ' '
    buf = os.read(fd, file_size)
    os.close(fd)
    # log = 'cat ' + file + '\n'
    # globalVar.log_file_handle.write(log)
    return buf

def ccrename(mntpoint, old, new):
    # print("Test RENAME\n")
    oldpath = pjoin(mntpoint, old)
    newpath = pjoin(mntpoint, new)
    # print('rename decide: oldpath = ' + oldpath)
    is_file = oldpath.rsplit("/", 1)[1]
    # print('rename decide: ' + is_file)
    if is_file in globalVar.MY_FILE_LIST:
        # print('To rename file, first creat file')
        cccreat(mntpoint, is_file)
    else:
        # 不是文件，是目录
        # print('To rename dir, first mkdir')
        ccmkdir(mntpoint, is_file)
    # os.rename(oldpath, newpath)
    if os.path.exists(oldpath):
        try:
            # print('before rename ----------')
            # os.rename(oldpath, newpath)
            file1 = oldpath.rsplit("/",1)[1]
            file2 = newpath.rsplit("/",1)[1]
            op0 = 'cd ' + mntpoint + ' &&'
            op = 'rename'
            op1 = '\'s/' + file1 + '/' + file2 + '/gm\''
            op2 = '*'
            mntcmd = f"{op0} {op} {op1} {op2}"
            print(mntcmd)
            proc = subprocess.Popen(mntcmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
            proc.wait()
            # print('rename done!!')
        except:
            # print('error --------------missing------rename-------------- ')
            pass
    # log = 'rename ' + old + ' ' + new + '\n'
    # globalVar.log_file_handle.write(log)

# 可执行条件：源路径存在且不是目录，目标路径不存在  
# 硬链接的源操作数不能是目录  
def cchdlink(mntpoint, src, dst):
    # print("Test HARDLINK\n")
    srcpath = pjoin(mntpoint, src)
    dstpath = pjoin(mntpoint, dst)
    if not os.path.exists(srcpath):
        # print('hardlink decide: first creat+++++++++++++++' + srcpath)
        cccreat(mntpoint, src)
    if not os.path.exists(srcpath):
        print("-----------before hardlink creat failed!!!")
    if not os.path.exists(dstpath) and os.path.isfile(srcpath):
        try: 
            # print('do hardlink')
            os.link(srcpath, dstpath)
            # print('hardlink done')
        except:
            # print('hardlink error --------------missing -------')
            pass
    # log = 'ln ' + src + ' ' + dst + '\n'
    # globalVar.log_file_handle.write(log)

# if src is symlink, deal with it	
# 源路径不存在的话，需要创建
# 	源路径为文件， 则 create file
#	源路径为目录， 则 mkdir
# 目标路径为file!!!注意！！
def ccsflink(mntpoint, src, dst):
    # print("Test SOFTLINK\n")
    srcpath = pjoin(mntpoint, src)
    dstpath = pjoin(mntpoint, dst)
    if not os.path.exists(srcpath):
        may_file = srcpath.rsplit("/",1)[1]
        if may_file in globalVar.MY_FILE_LIST:
            cccreat(mntpoint, src)
        else:
            ccmkdir(mntpoint, src)
            # print("mkdir " + src)
    if os.path.islink(srcpath) and not os.path.exists(dstpath):
        # print("srcpath is a symlink\n")
        sflink = os.readlink(srcpath)
        os.symlink(sflink, dstpath)
    elif os.path.isfile(srcpath) and not os.path.exists(dstpath):
        # print("srcpath is a file\n")
        os.symlink(srcpath, dstpath)
    # log = 'ln -s ' + src + ' ' + dst + '\n'
    # globalVar.log_file_handle.write(log)

# if dir already exists, pass
def ccmkdir(mntpoint, dir):
    # print("Test MKDIR\n")
    dirpath = pjoin(mntpoint, dir)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
        # log = 'mkdir ' + dir + '\n'
        # globalVar.log_file_handle.write(log)

# 删除文件或 目录（递归删除目录）
def ccremove(mntpoint, file):
    # print("Test REMOVE\n")
    abspath = pjoin(mntpoint, file)
    if os.path.isfile(abspath):
        # print("removing file " + file)
        os.remove(abspath)
        # log = 'remove file ' + file + '\n'
        # globalVar.log_file_handle.write(log)
    elif os.path.isdir(abspath):
        print("\n" + abspath)
        os.removedirs(abspath)
        # log = 'rmdir ' + file + '\n'
        # globalVar.log_file_handle.write(log)

def cclseek(fd, pos = 0, how = 0):
    # print("Test LSEEK\n")
    os.lseek(fd, pos, how)
    # log = 'lseek ' + fd + '\n'
    # globalVar.log_file_handle.write(log)
    return fd

def ccsync():
    os.sync()
    # log = 'sync' + '\n'
    # globalVar.log_file_handle.write(log)

if __name__ == '__main__':
    # cchdlink(globalVar.MY_MNT_POINT,'file5', 'file5_hdln')
    '''
    ccsflink(globalVar.MY_MNT_POINT,'A/foo','B')
    if os.path.isdir(pjoin(globalVar.MY_MNT_POINT, 'B')):
        print("hhhhhhaaaaa")
    else: print("wwwwwwwwwwwwwww")
    '''
    # ccrename('./amnt', './A/bar', './ddd')
    # print('testing fsync\n')
    # ccfsync('./', 'testfsync')
    # print("ccsyscalls.py is calling\n")
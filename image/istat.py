#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, errno, os, shutil, pathlib2, subprocess, sys, tempfile, pwd, struct, xattr
from stat import *
from multiprocessing import Process
from os.path import join as pjoin

# B: unsigned char
def p8(x): return struct.pack('<B', x)
# I: unsigned int
def p32(x): return struct.pack('<I', x)
# Q: unsigned long long
def p64(x): return struct.pack('<Q', x)


FILE = 0x01
DIR = 0x02
SYMLINK = 0x03
FIFO = 0x04

basepath = pjoin(os.path.dirname(__file__),'..')

def kmount(fstype, device, mntpoint, options=[]):
    if fstype == 'gfs2':
        options += ['acl']
    elif fstype == 'reiserfs':
        options += ['acl', 'user_xattr']
    print(['sudo', 'mount', '-o', ','.join(['loop'] + options),
          '-t', fstype, device, mntpoint])
    subprocess.check_call(
        ['sudo', 'mount', '-o', ','.join(['loop'] + options), '-t', fstype, device, mntpoint])


def usermount(whichfuse, img, mntpoint,option='-f'):
    #print(['sudo', whichfuse, img, '-f', mntpoint])
    # print(basepath)
    if whichfuse == 'xv6fs':
        option = '-s' 
    toolpath = pjoin(basepath, 'specificfuse', whichfuse, 'fs')
    mntcmd = toolpath + ' ' + img + ' ' + option + ' ' + mntpoint
    print(mntcmd)
    subprocess.Popen(mntcmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    
def chown(mntpoint):
    try:
        subprocess.check_call(['sudo', 'chown', '%s.%s' %
                              (os.getuid(), os.getgid()), '-R', mntpoint])
    except:
        pass


def kumount(mntpoint):
    subprocess.check_call(['sudo', 'umount', mntpoint])
    assert not os.path.ismount(mntpoint)


def userumount(mntpoint):
    subprocess.check_call(['sudo', 'fusermount', '-u', mntpoint])
    assert not os.path.ismount(mntpoint) 


def xattrs(x):
    ret = []
    f = pathlib2.Path(x)
    print(x + ", " + str(f.exists()))
    if f.exists():
        try:
            output = subprocess.check_output(
                ['getfattr', '--absolute-names', '-d', '-m', '-', x])
            for xattr in output.split('\n'):
                index = xattr.find('=')
                if index != -1:
                    xattr_name = xattr[:index]
                    xattr_value = xattr[index + 1:]
                    ret.append([xattr_name, xattr_value])
        except:
            pass
    return ret

def stat(mntpoint, stat_file):

    result = []

    print(mntpoint)
    for dirpath, _, files in os.walk(mntpoint):

        # put dir
        if dirpath == mntpoint:
            real_dirpath = '.'
        else:
            real_dirpath = dirpath[dirpath.find(mntpoint) + len(mntpoint) + 1:]
        print(real_dirpath)
        result.append([real_dirpath, DIR, xattrs(dirpath)])

        # put file objects
        for f in files:
            real_filepath = os.path.join(real_dirpath, f)
            # print real_filepath

            mode = os.lstat(os.path.join(mntpoint, real_filepath)).st_mode
            _type = None

            if S_ISLNK(mode):
                _type = SYMLINK
            elif S_ISFIFO(mode):
                _type = FIFO
            else:
                _type = FILE

            result.append([real_filepath, _type, xattrs(
                os.path.join(mntpoint, real_filepath))])

    print(result)

    f = open(stat_file, 'wb')

    # file obj num
    f.write(p32(len(result)))

    for fobj in result:
        real_filepath = fobj[0]
        f.write(p32(len(real_filepath)))
        f.write(real_filepath.encode())

        _type = fobj[1]
        f.write(p8(_type))

        _xattrs = fobj[2]
        f.write(p32(len(_xattrs)))
        for x in _xattrs:
            f.write(p32(len(x[0])))
            f.write(x[0])
            # f.write(p32(len(x[1])))
            # f.write(x[1])

    f.close()

def diff_img(mntpnt1, mntpnt2):
    # mntpnt1即目标文件系统的image的mntdir
    # mntpnt2 伴随文件系统.....mntdir
    diffcmd = 'diff -r ' + mntpnt1 + ' ' +  mntpnt2
    returnstat, result = subprocess.getstatusoutput(diffcmd)
    print(returnstat)
    # 这里是不是应该 assert returnstat==0 ?
    # 一旦发现diff状态码为1，则表示两个fs的镜像有区别，不具备一致性
    if returnstat == 1:
        # 比较发现有不同
       return returnstat



# usage： python3 istat.py -t U -T ../specificfuse/xv6fs/fs2.img -p xv6fs -o 0108.output 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='type',
                        help='kernal file system (K) OR userspace file system (U)')
    parser.add_argument('-T', dest='target', help='the target device or img')
    parser.add_argument('-i', dest='input', help='testcases')
    parser.add_argument('-p', dest='plus',
                        help='specific fs type for kernel userspace fs')
    parser.add_argument('-o', dest='output', help='the converted file')

    args = parser.parse_args()

    if args.target is None or args.type is None or args.plus is None or args.output is None:
        print('ERROR')
        sys.exit(1)

    if args.type == 'K':

        '''
        tmp_img = tempfile.NamedTemporaryFile(delete=False)
        tmp_img_path = tmp_img.name
        tmp_img.close()
        print('tmp image in: %s', tmp_img_path)

        shutil.copyfile(args.img, tmp_img_path)
        '''

        mnt_dir = tempfile.mkdtemp()
        print('mount dir: %s', mnt_dir)

        # kmount(fstype, device, mntdir)
        kmount(args.plus, args.target, mnt_dir)

        chown(mnt_dir)
        

        # stat(mntdir,output)
        stat(mnt_dir, args.output)

        # os.unlink(tmp_img_path)
        kumount(mnt_dir)
        os.rmdir(mnt_dir)
    elif args.type == 'U':
        mnt_dir = tempfile.mkdtemp()
        print('mount dir: %s', mnt_dir)
        # usermount(specific fs path, mntdir,options)
        usermount(args.plus, args.target, mnt_dir)
        chown(mnt_dir) 
        stat(mnt_dir, args.output)
        # os.unlink(tmp_img_path)
        userumount(mnt_dir)
        os.rmdir(mnt_dir)

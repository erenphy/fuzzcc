import argparse, tempfile, os, sys, subprocess
from os.path import join as pjoin
import time
import istat

import globalVar
import ccparser
'''
python3 ccmounter.py -k 0 -t ext3 -T /dev/sda4 -o /output/file
后期需要补充input, 支持自定义输入，对自定义的输入格式可以严格限制
'''
BASEPATH = pjoin(os.path.dirname(__file__),'..')
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
    toolpath = pjoin(BASEPATH, 'specificfs', whichfuse, 'fs')
    if whichfuse =='xv6fs':
        # xv6fs usage: ./fs img -s /mntpnt
        mntcmd = f"{toolpath} {img} {option} {mntpoint}"
    elif whichfuse =='ffs':
        # ffs usage: ./fs -f /mntpnt img
        mntcmd = f"{toolpath} {option} {mntpoint} {img}"
    print(mntcmd)
    proc = subprocess.Popen(mntcmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    proc.wait()
    
def chown(mntpoint):
    try:
        subprocess.check_call(['chown', '%s.%s' %
                              (os.getuid(), os.getgid()), '-R', mntpoint])
    except:
        pass


def kumount(mntpoint):
    subprocess.check_call(['sudo', 'umount', mntpoint])
    assert not os.path.ismount(mntpoint)


def userumount(mntpoint):
    ret_code = 1
    while ret_code != 0:
        time.sleep(1)
        ret_code = subprocess.call(['fusermount', '-zu', mntpoint])


def cc_mounter(is_kernelfs, fs_type, target, input, output):
    if is_kernelfs == '1':

        '''
        tmp_img = tempfile.NamedTemporaryFile(delete=False)
        tmp_img_path = tmp_img.name
        tmp_img.close()
        print('tmp image in: %s', tmp_img_path)

        shutil.copyfile(args.img, tmp_img_path)
        '''
        mnt_target = tempfile.mkdtemp()
        mnt_adjoint = tempfile.mkdtemp()
        mnt_seq = tempfile.mkdtemp()
        print('mount target dir: ' + mnt_target)
        print('mount adjoint dir: ' + mnt_adjoint)
        print('mount sequential dir: ' + mnt_seq)
        # kmount(fstype, device, mntdir)
        kmount(fs_type, target, mnt_target)
        kmount(fs_type, target, mnt_adjoint)
        # kmount(fs_type, target, mnt_seq)
        # for mnt_dir in [mnt_target, mnt_adjoint, mnt_seq]:
        #     chown(mnt_dir)

        ccparser.cc_parser(mnt_target, input)
        kumount(mnt_target)
        kmount(fs_type, target, mnt_target)
        istat.stat(mnt_target, output)
        ccparser.cc_parser(mnt_adjoint, input)
        istat.stat(mnt_adjoint, output+'1')
        # 需要补充顺序文件系统的挂载和parser、stat以及解挂
        
        # stat(mntdir,output)
        # stat(mnt_dir, args.output)
        # os.unlink(tmp_img_path)
        for mnt_dir in [mnt_target, mnt_adjoint, mnt_seq]:
            kumount(mnt_dir)
        # os.rmdir(mnt_dir)
        return mnt_target

    elif is_kernelfs == '0':
        mnt_target = tempfile.mkdtemp()
        mnt_adjoint = tempfile.mkdtemp()
        mnt_seq = tempfile.mkdtemp()
        print('mount target dir: ' + mnt_target)
        print('mount adjoint dir: ' + mnt_adjoint)
        print('mount sequential dir: ' + mnt_seq)
        # usermount(specific fs path, mntdir,options)
        usermount(fs_type, target, mnt_target)
        # usermount(fs_type, target, mnt_adjoint)
        # for mnt_dir in [mnt_target, mnt_adjoint, mnt_seq]:
        #     chown(mnt_dir)
        print("right here******************start parser\n")
        ccparser.cc_parser(mnt_target, input)
        userumount(mnt_target)
        usermount(fs_type, target, mnt_target)
        istat.stat(mnt_target, output)
        
        # ccparser.cc_parser(mnt_adjoint, input)
        # istat.stat(mnt_adjoint, output+'1')
        # 需要补充顺序文件系统的挂载和parser、stat以及解挂

        # os.unlink(tmp_img_path)
        # for mnt_dir in [mnt_target, mnt_adjoint, mnt_seq]:
        #     userumount(mnt_dir)
        # os.rmdir(mnt_dir)
        return mnt_target
        # usermount(specific fs path, mntdir,options)
        # testwrite(pjoin(mnt_dir,'file2'))
        # testread(pjoin(mnt_dir,'file2'))# 
        # stat(mnt_dir, args.output)
        # os.unlink(tmp_img_path)
        userumount(mnt_dir)
        # os.rmdir(mnt_dir)
        return mnt_dir
'''
if __name__ == '__main__':
    cc_mounter('0', 'xv6fs', '../specificfuse/xv6fs/fs.img', [['creat','testfile0531'],['mkdir', './A'], ['creat', './A/foo0531']], './test')
    print("ccmounter.py is running\n")
'''
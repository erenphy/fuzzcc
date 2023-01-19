## xv6fs
；初始化镜像 通过 ./mkfs imgname.img init.txt 得到imgname.img
./specificfs/xv6fs/mkfs imgname.img init.txt

;挂载，先镜像再 -s加挂载点
./spcificfs/xv6fs/fs imgname.img -s /path/to/mntpnt

;umount fs
fusermount -u /path/to/mnmt/pnt

;备注
不支持同一个镜像下两个挂载点，会出问题

## ffs
;初始化镜像 通过 ./mkfs /path/to/imgname.img 不需要init.txt。
./specificfs/ffs/mkfs /path/to/imgname.img 

；挂载：先-f加挂载点 再 镜像
./specificfs/ffs/fs -f /path/to/mnt /path/to/img

;umount fs
fusermount -u /path/to/mntpnt

;也不支持同一个镜像下挂载第二个目录，第二个挂载点的数据最终不会保存到img中，umount第一个挂载点的时候还会显示device busy

;ffs实现的fops:[open, write, read, truncate, flush mkdir, unlink, rmdir, remove, mknod, chmod]
;[不支持 fsync]

## 
import time
import random
from multiprocessing import Process
from multiprocessing import JoinableQueue
 
def consumer(name,q):
    while True:
        res=q.get()
        time.sleep(random.randint(1,3))
        print('\033[43m消费者》》%s 准备开吃%s\033[0m'%(name,res))
        q.task_done()#发送信号给生产者的q.join()说，已经处理完从队列中拿走的一个项目
 
def producer(name,q):
    for i in range(5):
        time.sleep(random.randint(1,2))#模拟生产时间
        res='大虾%s'%i
        q.put(res)
        print('\033[40m生产者》》》%s 生产了%s\033[0m'%(name,res))
    q.join()#等到消费者把自己放入队列中的所有项目都取走处理完后调用task_done()之后，生产者才能结束
 
if __name__ == '__main__':
    q=JoinableQueue()#实例一个队列
 
    p1=Process(target=producer,args=('monicx1',q))
    p2=Process(target=producer,args=('monicx2',q))
 
    c1=Process(target=consumer,args=('lili1',q))
    c2=Process(target=consumer,args=('lili2',q))
    c3=Process(target=consumer,args=('lili3',q))
    c1.daemon=True
    c2.daemon=True
    c3.daemon=True
 
    p1.start()
    p2.start()
 
    c1.start()
    c2.start()
    c3.start()
 
    p1.join()
    p2.join() 
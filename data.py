import numpy as np 
from queue import Queue
#testdata = np.random.normal(size=10)


def initdata():
    testdata = np.random.normal(size=100)
    return testdata

global u, v
u = []
v = []
u_a = []
qmaxsize = 100
q = Queue(maxsize = qmaxsize)

def change_uv(uu, vv):
    u.append(uu)
    v.append(vv)
    print('装载u', u)

def obtain_uv():
    return u, v


def obtain_uv_a():
    return u_a


#print('data', testdata)
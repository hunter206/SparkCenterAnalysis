#/usr/bin/env python3
'''
A simple Program for grabing video from basler camera and converting it to opencv img.
Tested on Basler acA1300-200uc (USB3, linux 64bit , python 3.5)
by hunter 18222287661
'''
import os
from pypylon import pylon
import cv2 as cv
import copy
import datetime
import numpy as np
import data
from matplotlib import pyplot as plt
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time
import sys
import pyqtgraph.examples
import pyqtgraph as pg
import scrollingplots

'''
NAMED_PIPE = 'mypipe'
try:
    os.mkfifo(NAMED_PIPE)
except OSError: 
    raise

with open(NAMED_PIPE) as fifo:
    while True:
        data = fifo.read()
        if len(data) == 0:
            break
        print('[x] Data: {}'.format(data))
'''

class Plot(QThread):
    def __init__(self, parent=  None):
        super(Plot, self).__init__(parent)
    def run(self):
        os.system("python3 scrollingplots.py")

#pyqtgraph.examples.run()

global opencv_img, img
SizeX, SizeY = 1280, 1024
#load template
plot_thread = Plot()
plot_thread.start()
template = cv.imread('1.bmp', 0)

def template_matching(template, opencv_img, source_img):
    template_w, template_h = template.shape[::-1]
    # 模板匹配
    method = cv.TM_CCOEFF
    res = cv.matchTemplate(opencv_img, template, method)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    # 使用不同的比较方法，对结果的解释不同
    if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
    x = top_left[0]
    y = top_left[1]
    width = template_w
    height = template_h
    w = width
    h = height
    x = x - 10
    y = y - 10
    w = w + 20
    h = h + 20
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x + w > SizeX:
        w = SizeX - x
    if y + h > SizeY:
        h = SizeY - y
    all = 0
    xAll = 0
    yAll = 0
    gray = cv.cvtColor(source_img, cv.COLOR_RGB2GRAY)
    for i in range(w):
        for j in range(h):
            all += gray[y + j, x + i]
            xAll += i * gray[y + j, x + i]
            yAll += j * gray[y + j, x + i]
    u_center = np.round((xAll / all + x), 5)
    v_center = np.round((yAll / all + y), 5)
    return [u_center, v_center, x, y]

# conecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
# Grabing Continusely (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
converter = pylon.ImageFormatConverter()
# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

while camera.IsGrabbing():
    oldtime = datetime.datetime.now()
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data
        image = converter.Convert(grabResult)
        img = image.GetArray()
        opencv_img = copy.deepcopy(grabResult.Array)#记时
        #img process
        source_img = converter.Convert(grabResult).GetArray()
        [u, v, x_left, y_left] = template_matching(template, opencv_img, source_img)
        #装入队列
        data.u.append(u)
        data.v.append(v)
        '''
        if (scrollingplots.q.qsize() >= scrollingplots.qmaxsize):
            scrollingplots.q.get()
        scrollingplots.q.put(u)
        print('队列质心数值：', scrollingplots.q.queue)
        scrollingplots.set_value(scrollingplots.q.queue)
        '''
        #config.update_flag = True
        newtime = datetime.datetime.now()
        intervaltime = (newtime - oldtime).microseconds/1000
        #print('质心数据', data.u)
        #print('间隔时间：', intervaltime, '毫秒', data.u)  # 计时
        cv.putText(img, str(u) + "," + str(v), (x_left, y_left - 50), cv.CHAIN_APPROX_SIMPLE, 1, (255, 255, 0), 1)
        cv.putText(img, str(intervaltime) + "ms", (50, 50), cv.CHAIN_APPROX_SIMPLE, 1, (255, 255, 0), 1)
        cv.putText(img, str(round(1/intervaltime*1000,2)) + "HZ", (1100, 50), cv.CHAIN_APPROX_SIMPLE, 1, (255, 255, 0), 1)
        cv.rectangle(img, (int(u)-50, int(v)-50), (int(u)+50, int(v)+50), (255, 255, 255), 2)
        #cv.namedWindow('double shield test', cv.WINDOW_NORMAL)
        cv.imshow('double shield test', img)        
        k = cv.waitKey(1)
        if k == 27:
            break
    grabResult.Release()

# Releasing the resource    
camera.StopGrabbing()
c2.destroyAllWindows()
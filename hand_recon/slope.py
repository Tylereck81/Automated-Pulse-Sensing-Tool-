import numpy as np
import math
k = 20
infinity = 100000
def getValueWithM(x, y, m, img):
    ori = img[y][x]
    width = 0
    value = 0
    for i in range(1, img.shape[1]):
        if (ori != img[y][x+i]).any():
            break
        width+=1
        ori = img[y][x+i]
    ori = img[y][x]
    for i in range(1, img.shape[1]): #left
        if (ori != img[y][x-i]).any():
            break
        width+=1
        ori = img[y][x-i]
    width-=1 #中間重複
    #print("width: ",width)
    #print("m: ", round(m,2))
    if m == infinity:#直接計算
        value = width
    else:
        value = math.sin(math.atan(m)) * width
    return abs(round(value))
def getValue(x, y, img):
    value = 0
    slope = find_m(x, y, img)#第一個元素是 m, 第二個是值
    if slope[0] == infinity:#直接計算
        value = slope[1]
    else:
        value = math.sin(math.atan(slope[0])) * slope[1]
    return abs(round(value))

def find_m(x, y, img):
    ori = img[y][x]
    solution = [0,0]
    width = 0
    m = 0
    for i in range(1, img.shape[1]): #right
        if (ori != img[y][x+i]).any():
            if (img[y-(round(img.shape[0]/k))][x+i] == img[y][x+i]).all():
                x_shift = __left__(x+i, y-(round(img.shape[0]/k)), img) # k是參數, 是實際拍攝圖片決定
                if x_shift != 0:
                    m = -1 * ((round(img.shape[0]/k))/x_shift)
            else:
                m = Lfind_m(x, y, img)
            break
        width+=1
        ori = img[y][x+i]
    ori = img[y][x]
    for i in range(1, img.shape[1]): #left
        if (ori != img[y][x-i]).any():
            break
        width+=1
        ori = img[y][x-i]
    if m == 0:
        m = infinity #以目前圖片像素來說等於無窮
    solution[0] = m
    solution[1] = width-1
    print("wid:",width)
    return solution
def Lfind_m(x, y, img):
    ori = np.array(img[y][x])
    m = 0
    for i in range(1, img.shape[1]): #left
        if (ori != img[y][x-i]).any():
            if (img[y-(round(img.shape[0]/k))][x-i] == img[y][x-i]).all():
                x_shift = __right__(x-i, y-(round(img.shape[0]/k)), img)
                if x_shift != 0:
                    m = ((round(img.shape[0]/k))/x_shift)
            break
    ori = img[y][x-i]
    return m
def __left__(x, y, img):
    ori = np.array(img[y][x])
    for i in range(1, img.shape[1]): #left
        if (ori != img[y][x-i]).any():
            return i
    return 0
def __right__(x, y, img):
    ori = np.array(img[y][x])
    for i in range(1, img.shape[1]): #right
        if (ori != img[y][x+i]).any():
            return i
    return 0
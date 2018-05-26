import numpy as np
import gdal
import cv2
import matplotlib.pyplot as plt
import mahotas

from os import walk
default_path = "R10_test"

def mean(image):
    N,L = image.shape
    total = 0
    values = 0
    for x in range(N):
        for y in range(L):
            if image[x,y] > 0:
                values += image[x,y]
                total +=1
    return values/total

def adaptative_thresholding(image):
    m = np.array(image).mean()
    th1 = round(m/2)
    th2 = m + round(m/2)
    th3 = 255 - round(m/2)
    mask_a = image <= th1
    mask_b = np.bitwise_and(image<=m, image > th1)
    mask_c = np.bitwise_and(image <= th2, image > m)
    mask_d = image > th2
    mask = np.bitwise_or(mask_c, mask_d)
    road = image * mask
    return np.array(mask,dtype="uint8")

def compare_images(image1, image2):
    f = plt.figure()
    f.add_subplot(1, 2, 1)
    plt.imshow(image1,cmap='gray')
    f.add_subplot(1, 2, 2)
    plt.imshow(image2,cmap='gray')
    plt.show()

#ajuste de iluminação da imagem
def adjust_gamma(image, gamma=0.3):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.5 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
    for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def pre_process(image):
    final = image
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    contrast = clahe.apply(final)
    gamma = adjust_gamma(contrast)
    return gamma

def neighbours_vec(image):
    return image[2:,1:-1], image[2:,2:], image[1:-1,2:], image[:-2,2:], image[:-2,1:-1], image[:-2,:-2], image[1:-1,:-2], image[2:,:-2]

def transitions_vec(P2, P3, P4, P5, P6, P7, P8, P9):
    return ((P3-P2) > 0).astype(int) + ((P4-P3) > 0).astype(int) +\
           ((P5-P4) > 0).astype(int) + ((P6-P5) > 0).astype(int) +\
           ((P7-P6) > 0).astype(int) + ((P8-P7) > 0).astype(int) +\
           ((P9-P8) > 0).astype(int) + ((P2-P9) > 0).astype(int)

def zhangSuen_vec(image, iterations):
    for iter in range (1, iterations):
        print (iter)
        # step 1
        P2,P3,P4,P5,P6,P7,P8,P9 = neighbours_vec(image)
        condition0 = image[1:-1,1:-1]
        condition4 = P4*P6*P8
        condition3 = P2*P4*P6
        condition2 = transitions_vec(P2, P3, P4, P5, P6, P7, P8, P9) == 1
        condition1 = (2 <= P2+P3+P4+P5+P6+P7+P8+P9) * (P2+P3+P4+P5+P6+P7+P8+P9 <= 6)
        cond = (condition0 == 1) * (condition4 == 0) * (condition3 == 0) * (condition2 == 1) * (condition1 == 1)
        changing1 = np.where(cond == 1)
        image[changing1[0]+1,changing1[1]+1] = 0
        # step 2
        P2,P3,P4,P5,P6,P7,P8,P9 = neighbours_vec(image)
        condition0 = image[1:-1,1:-1]
        condition4 = P2*P6*P8
        condition3 = P2*P4*P8
        condition2 = transitions_vec(P2, P3, P4, P5, P6, P7, P8, P9) == 1
        condition1 = (2 <= P2+P3+P4+P5+P6+P7+P8+P9) * (P2+P3+P4+P5+P6+P7+P8+P9 <= 6)
        cond = (condition0 == 1) * (condition4 == 0) * (condition3 == 0) * (condition2 == 1) * (condition1 == 1)
        changing2 = np.where(cond == 1)
        image[changing2[0]+1,changing2[1]+1] = 0
    return image

def skeleton(img):
    size = np.size(img)
    skel = np.zeros(img.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    done = False

    while (not done):
        eroded = cv2.erode(img, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img = eroded.copy()

        zeros = size - cv2.countNonZero(img)
        print(size,zeros)
        if zeros == size:
            done = True
    return skel

def process(image):
    kernel1 = np.ones((8, 8), np.uint8)
    kernel2 = np.ones((2, 2), np.uint8)
    m_opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel1)
    m_opening = m_opening > 0
    opening = np.array(image * (1-m_opening),dtype="uint8")
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel2)
    compare_images(image,closing)
    skel = skeleton(opening)
    return skel

if __name__=="__main__":
    #path = ""
    #path = input("Satellite images folder:")
    #if path == "":
    #    print("Using default path " + default_path)
    #    path = default_path

    #obter images
    #tci = read_image(path)
    kernel1 = np.ones((8, 8), np.uint8)
    kernel2 = np.ones((3, 3), np.uint8)
    kernel3 = cv2.getStructuringElement(cv2.MORPH_CROSS, (8, 8))
    kernel4 = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

    tci = np.array((cv2.imread('wtf.tif'))[:,:,1])
    image = np.array(tci)
    pre = pre_process(image)
    road = adaptative_thresholding(pre)
    skel = process(road)
    #teste = pre_process(road)
    #compare_images(road,closing)
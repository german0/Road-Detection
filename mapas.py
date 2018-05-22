import numpy as np
import gdal
import cv2
import matplotlib.pyplot as plt
import mahotas

from os import walk
default_path = "R10_test"

def adaptative_thresholding(image):
    m = image.mean()
    th1 = round(m/2)
    th2 = m + round(m/2)
    th3 = 255 - round(m/2)
    mask_a = image <= th1
    mask_b = np.bitwise_and(image<=m, image > th1)
    mask_c = np.bitwise_and(image <= th2, image > m)
    mask_d = image > th2
    #mask = np.bitwise_or(mask_c, mask_d)
    road = image * mask_c
    compare_images(image,road)
    image = road
    return image

def compare_images(image1, image2):
    f = plt.figure()
    f.add_subplot(1, 3, 1)
    plt.imshow(image1,cmap='gray')
    f.add_subplot(1, 3, 2)
    plt.imshow(image2,cmap='gray')
    plt.show()

if __name__=="__main__":
    #path = ""
    #path = input("Satellite images folder:")
    #if path == "":
    #    print("Using default path " + default_path)
    #    path = default_path

    #obter images
    #tci = read_image(path)

    tci = np.array((cv2.imread('wtf.tif'))[:,:,1])
    image = np.array(tci)
    road = adaptative_thresholding(image)
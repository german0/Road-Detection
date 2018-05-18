import rasterio
import geopyspark as gps
import numpy as np
import gdal
import cv2
import matplotlib.pyplot as plt

from os import walk
from scipy.misc import imsave

default_path = "R10_test"

def read_image(path):
    bandas = []
    tci = []
    wvp = []
    #obter os ficheiros da pasta dada como input
    for (dirpath, dirnames, filenames) in walk(path):
        jp2s = filenames
        break
    for jp2 in jp2s:
        if 'TCI' in jp2:
            nir_ds = gdal.Open(path + "/" + jp2)
            nir_band = nir_ds.GetRasterBand(1)
            nir = nir_band.ReadAsArray()
            tci = nir
        if 'B03' in jp2:
            nir_ds = gdal.Open(path + "/" + jp2)
            nir_band = nir_ds.GetRasterBand(1)
            nir = nir_band.ReadAsArray()
            wvp = nir
    return np.array(tci),np.array(wvp)

def divide_regions(image):
    region1 = image < 50
    region2 = (image < 125)
    region3 = (image < 185)
    region4 = image - region3
    region3 = region3 - region2
    region2 = region2 - region1
    return region1,region2,region3,region4

#ajuste de iluminação da imagem
def adjust_gamma(image, gamma=0.3):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
    for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def pre_process(tci):
    final = tci
    #subdividir a imagem de forma a que o aumento do contraste tenha melhores resultados
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4,4))
    contrast = clahe.apply(final)
    print_image(contrast)
    gamma = adjust_gamma(contrast)
    print_image(gamma)
    return gamma

def print_image(image):
    plt.imshow(image,cmap='gray')
    plt.show()

def build_filters():
    filters = []
    ksize = 52
    for theta in np.arange(0, np.pi, np.pi / 7):
        kern = cv2.getGaborKernel((ksize, ksize), 1.7, theta, 5.0, 0.5, 0, ktype=cv2.CV_32F)
        kern /= 1.9*kern.sum()
        filters.append(kern)
    return filters

def process_gabor(img, filters):
    accum = np.zeros_like(img)
    gabor = img
    for kern in filters:
        fimg = cv2.filter2D(gabor, cv2.CV_8UC3, kern)
        np.maximum(accum, fimg, accum)
    return accum

def gabor_filtering(image):
    filters = build_filters()
    print_image(image)
    ret1, th1 = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    gabor = process_gabor(image,filters)
    return gabor

def path_opening(image):
    ksize = 4
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(ksize,ksize))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(ksize,ksize))
    kernel3 = cv2.getStructuringElement(cv2.MORPH_CROSS,(ksize,ksize))
    ret1, th1 = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    print_image(th1)
    teste=cv2.dilate(th1,kernel,iterations = 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    print_image(cv2.erode(teste,kernel))
    return 0

if __name__=="__main__":
    #path = ""
    #path = input("Satellite images folder:")
    #if path == "":
    #    print("Using default path " + default_path)
    #    path = default_path

    #obter images
    #tci,wvp = read_image(path)
    tci = (cv2.imread('wtf.tif'))[:,:,1]
    N,L = tci.shape
    pre = pre_process(tci)
    gabor = gabor_filtering(pre)
    #opening = path_opening(gabor)
    #opening = path_opening(gabor)
    #print_image(gabor)
    #print_image(gabor)
    #print_image(pre)
    #print_image(cv2.Canny(pre,100,200))
    #imsave("teste.jpeg", tci)


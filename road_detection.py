import numpy as np
import gdal
import cv2
import matplotlib.pyplot as plt
import mahotas

from os import walk

default_path = "R10_test"
''''
def read_image(path):
    bandas = []
    tci = []
    rgb = []
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
        if 'B02' in jp2:
            nir_ds = gdal.Open(path + "/" + jp2)
            nir_band = nir_ds.GetRasterBand(1)
            nir = nir_band.ReadAsArray()
            rgb.append(np.array(nir))
        if 'B03' in jp2:
            nir_ds = gdal.Open(path + "/" + jp2)
            nir_band = nir_ds.GetRasterBand(1)
            nir = nir_band.ReadAsArray()
            rgb.append(np.array(nir))
        if 'B04' in jp2:
            nir_ds = gdal.Open(path + "/" + jp2)
            nir_band = nir_ds.GetRasterBand(1)
            nir = nir_band.ReadAsArray()
            rgb.append(np.array(nir))
    return  np.array(rgb)

def detect_clouds(image,N,L):
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    mean = np.array(blur).mean()
    st = np.array(blur).std()
    print(mean)
    for i in range(0,N):
        for j in range(0,L):
            if blur[i,j] <= mean - st or blur[i,j] >= mean+st:
                image[i,j] = mean
    return image

#ajuste de iluminação da imagem
def adjust_gamma(image, gamma=0.3):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.5 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
    for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def pre_process(tci):
    final = tci
    #subdividir a imagem de forma a que o aumento do contraste tenha melhores resultados
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    contrast = clahe.apply(final)
    gamma = adjust_gamma(contrast)
    return gamma

def print_image(image):
    plt.imshow(image,cmap='gray')
    plt.show()

def build_filters():
    filters = []
    ksize = 52
    for theta in np.arange(0, np.pi, np.pi / 7):
        #kern = cv2.getGaborKernel((ksize, ksize), 1.0, theta, 5.0, 0.5, 0, ktype=cv2.CV_32F)
        kern = cv2.getGaborKernel((ksize,ksize), 3.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
        kern /= 1.5*kern.sum()
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
    gabor = process_gabor(image,filters)
    #print_image(gabor)
    ret, th1 = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY)
    print_image(th1)
    return gabor

def path_opening(image):
    ksize = 7
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(ksize,ksize))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(ksize,ksize))
    kernel3 = cv2.getStructuringElement(cv2.MORPH_CROSS,(ksize,ksize))
    ret1, th1 = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    erode = cv2.erode(th1,kernel)
    dilation = cv2.dilate(erode,kernel,iterations=1)
    print_image(image)
    return 0'''

def print_image(image):
    plt.imshow(image,cmap='gray')
    plt.show()

def crop(image):
    image = np.array(image)
    N,L = image.shape
    step_x = round(N/2)
    step_y= round(L/2)
    for x in range(0,N-step_x,step_x):
        for y in range(0,L-step_y,step_y):
            cropped = image[x:x+step_x,y:y+step_y]
            print_image(cropped)

def detect_clouds(image):
    N,L = image.shape
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    mean = np.array(blur).mean()
    st = np.array(blur).std()
    for i in range(0,N):
        for j in range(0,L):
            if image[i,j] <= mean - st or image[i,j] >= mean+st:
                image[i,j] = 0
    return image

#ajuste de iluminação da imagem
def adjust_gamma(image, gamma=0.5):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.5 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
    for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def pre_process(tci):
    final = tci
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast = clahe.apply(final)
    gamma = adjust_gamma(contrast)
    return gamma

def process_gabor(img, filters):
    accum = np.zeros_like(img)
    gabor = img
    for kern in filters:
        fimg = cv2.filter2D(gabor, cv2.CV_8UC3, kern)
        np.maximum(accum, fimg, accum)
    return accum

def build_filters():
    filters = []
    ksize = 52
    for theta in np.arange(0, np.pi, np.pi / 7):
        #kern = cv2.getGaborKernel((ksize, ksize), 1.0, theta, 5.0, 0.5, 0, ktype=cv2.CV_32F)
        kern = cv2.getGaborKernel((ksize,ksize), 3.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
        kern /= 1.5*kern.sum()
        filters.append(kern)
    return filters

def divide_regions(image):
    division = 4
    step = round(255/division)
    mean = np.array(image).mean()
    st = np.array(image).std()
    region1 = image<step
    region2 = image<(2*step)-region1
    region3 = image<(3*step)-region2
    region4 = image - region3
    return region1,region2,region3,region4

def gabor_filtering(image):
    #ret, th1 = cv2.threshold(image, 40, 255, cv2.THRESH_BINARY)
    #opening = cv2.morphologyEx(th1, cv2.MORPH_OPEN, kernel)
    #filters = build_filters()
    #gabor = process_gabor(image,filters)
    #print_image(gabor)
    #ret, th1 = cv2.threshold(image.astype(np.uint8), 40, 255, cv2.THRESH_BINARY)
    #print_image(th1)
    print_image(cv2.Canny(image.astype(np.uint8),100,200))
    #return gabor


if __name__=="__main__":
    #path = ""
    #path = input("Satellite images folder:")
    #if path == "":
    #    print("Using default path " + default_path)
    #    path = default_path

    #obter images
    #tci = read_image(path)

    tci = np.array((cv2.imread('wtf.tif'))[:,:,1])
    #print_image(tci)
    pre = pre_process(tci)
    r1,r2,r3,r4 = divide_regions(pre)
    clouds = r3 * pre
    grass = (1-r1) * clouds
    #cv2.Canny(grass.astype(np.uint8),0,255)
    #gabor_filtering(np.array(grass))
    #print_image(pre)
    f = plt.figure()
    f.add_subplot(1, 3, 1)
    plt.imshow(pre)
    f.add_subplot(1, 3, 2)
    plt.imshow(grass)
    f.add_subplot(1, 3, 3)
    plt.imshow(cv2.morphologyEx(grass.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2,2)),iterations=2))
    plt.show()
    #gabor_filtering(new)


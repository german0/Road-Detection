import numpy as np
import gdal
import cv2
import matplotlib.pyplot as plt
import mahotas

from os import walk
default_path = "R10m"

def read_image(path):
    bandas = []
    tci = []
    rgb = []
    jp2s = []
    #obter os ficheiros da pasta dada como input
    print(path)
    for (dirpath, dirnames, filenames) in walk(path):
        jp2s = filenames
        break
    for jp2 in jp2s:
        if 'TCI' in jp2:
            nir_ds = gdal.Open(path + "/" + jp2)
            nir_band = nir_ds.GetRasterBand(1)
            nir = nir_band.ReadAsArray()
            tci = nir
        #if 'B02' in jp2:
        #    nir_ds = gdal.Open(path + "/" + jp2)
        #    nir_band = nir_ds.GetRasterBand(1)
        #    red = nir_band.ReadAsArray()
        #if 'B03' in jp2:
        #    nir_ds = gdal.Open(path + "/" + jp2)
        #    nir_band = nir_ds.GetRasterBand(1)
        #    green = nir_band.ReadAsArray()
        #if 'B04' in jp2:
        #    nir_ds = gdal.Open(path + "/" + jp2)
        #    nir_band = nir_ds.GetRasterBand(1)
        #    blue = nir_band.ReadAsArray()
    #N,L = red.shape
    #rgb = np.zeros((N,L,3), 'uint8')
    #rgb[...,0] = red
    #rgb[...,1] = green
    #rgb[...,2] = blue
    return  tci,np.array(rgb)

def mean(image):
    N,L = image.shape
    total = 0
    values = image.sum()
    total = ((image>0)*1).sum()
    return values/total

def remove_bright(image,mask):
    #160
    image = image*mask
    blur = cv2.GaussianBlur(image,(11,11),0)
    thresh = cv2.threshold(blur, 160, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)
    return thresh

def adaptative_thresholding(image):
    #m = np.array(image).mean()
    #print(m,mean(image))
    m = mean(image)
    th1 = round(m/2)
    th2 = m + round(m/2)
    mask_a = image <= th1
    mask_b = np.bitwise_and(image<=m, image > th1)
    mask_c = np.bitwise_and(image <= th2, image > m)
    print(th2)
    mask_d = image>th2
    mask = np.bitwise_or(mask_c, mask_d)
    return np.array(mask,dtype="uint8")

def compare_images(image1, image2):
    f = plt.figure()
    f.add_subplot(1, 2, 1)
    plt.imshow(image1,cmap='gray')
    f.add_subplot(1, 2, 2)
    plt.imshow(image2,cmap='gray')
    plt.show()

#ajuste de iluminação da imagem
def adjust_gamma(image, gamma=0.5):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.5 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
    for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def pre_process(image):
    final = image
    #clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(final)
    gamma = adjust_gamma(contrast)
    return gamma

def skeleton(img):
    size = np.size(img)
    skel = np.zeros(img.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    kernel_thin = np.array([[1,1,1],[-1,1,1],[0,0,0]])
    kernel_prune = np.array([[0,-1,-1],[0,1,1],[0,0,0]])
    done = False

    while (not done):
        eroded = cv2.erode(img, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img = eroded.copy()

        zeros = size - cv2.countNonZero(img)
        if zeros == size:
            done = True
    return skel

def morphology(image):
    kernel1 = np.ones((20, 20), np.uint8)
    kernel2 = np.ones((2, 2), np.uint8)
    m_opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel1,iterations=4)
    #m_opening = m_opening > 0
    #opening = np.array(image * (1-m_opening),dtype="uint8")
    #compare_images(image,opening)
    closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel2)
    m_opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel2)
    skel = skeleton(m_opening)
    return m_opening

def pruning(skel):
    # make out input nice, possibly necessary
    skel = skel.copy()
    skel[skel != 0] = 1
    skel = np.uint8(skel)

    # apply the convolution
    kernel = np.uint8([[1, 1, 1],
                       [1, 10, 1],
                       [1, 1, 1]])
    src_depth = -1
    filtered = cv2.filter2D(skel, src_depth, kernel)

    # now look through to find the value of 11
    # this returns a mask of the endpoints, but if you just want the coordinates, you could simply return np.where(filtered==11)
    out = np.zeros_like(skel)
    out[np.where(filtered == 11)] = 1
    return out

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
    return gabor

def process(image):
    N,L = image.shape
    stepx = round(N/30)
    stepy = round(N/30)
    kernel1 = np.ones((8, 8), np.uint8)
    kernel2 = np.ones((3, 3), np.uint8)
    kernel3 = cv2.getStructuringElement(cv2.MORPH_CROSS, (8, 8))
    kernel4 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    pre = pre_process(image)
    road = adaptative_thresholding(pre)
    clouds = remove_bright(pre,road)
    for x in range(0,N-stepx,stepx):
        for y in range(0,L-stepy,stepy):
            cropped = road[x:x+stepx,y:y+stepy]
            skel = morphology(cropped)
            compare_images(pre[x:x+stepx,y:y+stepy],clouds[x:x+stepx,y:y+stepy])
            #compare_images(pre[x:x + stepx, y:y + stepy], cropped)
            #prune = pruning(skel)
    # compare_images(skel,cv2.Canny(skel,100,200))
    return skel


if __name__=="__main__":
    path = ""
    path = input("Satellite images folder:")
    if path == "":
        print("Using default path " + default_path)
        path = default_path
    # tci = np.array((cv2.imread('wtf.tif'))[:,:,1])
    tci,rgb = read_image(path)
    tci = np.array(tci,dtype='uint8')
    final = process(tci)
    #edges = cv2.Canny(img,100,200)

    #testar closings e openings
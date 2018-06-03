import numpy as np
import gdal
import cv2
import matplotlib.pyplot as plt
import osgeo

from os import walk
default_path = "R10m"

def read_image(path):
    bandas = []
    tci = []
    rgb = []
    jp2s = []
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

def detect_bright(image):
    #160
    element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11))
    blur = cv2.GaussianBlur(image,(11,11),0)
    thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=5)
    thresh = cv2.dilate(thresh, element, iterations=3)
    return 1*(thresh == 255)

def adaptative_thresholding(image):
    m = np.array(image).mean()
    #print(m,mean(image))
    #m = mean(image)
    th1 = round(m/2)
    th2 = m + round(m/2)
    mask_a = image <= th1
    mask_b = np.bitwise_and(image<=m, image > th1)
    mask_c = np.bitwise_and(image <= th2, image > m)
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

def morphology(original,laplacian,mask):
    kernel1 = np.ones((2, 2), np.uint8)
    kernel2 = np.ones((3, 3), np.uint8)
    kernel3 = np.ones((1,1), np.uint8)
    relev = np.array(1 - (laplacian == 0),dtype = 'uint8')
    closing = cv2.morphologyEx(relev, cv2.MORPH_CLOSE, kernel2, iterations=1)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel2, iterations=1)
    segmented = np.array(laplacian * opening,dtype='uint8')
    road = cv2.adaptiveThreshold(segmented,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
    #inverter a imagem para ficar com as estradas como partes claras
    road = np.array((255 - road) * mask,dtype='uint8')
    road = cv2.erode(road, kernel3, iterations = 1)
    skel = skeleton(road)
    return skel

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
    out = np.zeros_like(skel)
    out[np.where(filtered == 11)] = 1
    return out

def interval(image):
    min = np.array(image).min()
    image += abs(min)
    max = np.array(image).max()
    value = np.divide(image,max)*255
    return value

def process(image):
    N,L = image.shape
    stepx = round(N/30)
    stepy = round(N/30)
    final = np.zeros_like(image)
    print("Adjusting gamma values ...")
    pre = pre_process(image)
    print("Done.\n")
    print("Dividing in regions by frequency ...")
    road_mask = adaptative_thresholding(pre)
    print("Done.\n")
    print("Processing image ...")
    road = pre * road_mask
    clouds_mask = detect_bright(road)
    laplacian = cv2.Laplacian(road, cv2.CV_64F)
    laplacian =  interval(laplacian)
    
    for x in range(0,N-stepx,stepx):
        for y in range(0,L-stepy,stepy):
            cropped_o = road[x:x+stepx,y:y+stepy]
            cropped_l = laplacian[x:x+stepx,y:y+stepy]
            mask = 1 - clouds_mask[x:x+stepx,y:y+stepy]
            edges = morphology(cropped_o,cropped_l,mask)
            final[x:x+stepx,y:y+stepy] = edges
            compare_images(image[x:x+stepx,y:y+stepy],final[x:x+stepx,y:y+stepy])

    for x in range(0,N-stepx,stepx):
        cropped_o = road[x:x+stepx,L-stepy:L]
        cropped_l = laplacian[x:x+stepx,L-stepy:L]
        mask = 1 - clouds_mask[x:x+stepx,L-stepy:L]
        edges = morphology(cropped_o,cropped_l,mask)
        final[x:x+stepx,L-stepy:L] = edges
    
    for y in range(0,L-stepy,stepy):
        cropped_o = road[N-stepx:N,y:y+stepy]
        cropped_l = laplacian[N-stepx:N,y:y+stepy]
        mask = 1 - clouds_mask[N-stepx:N,y:y+stepy]
        edges = morphology(cropped_o,cropped_l,mask)
        final[N-stepx:N,y:y+stepy] = edges

    print("Processing complete ...")
    
    return final


if __name__=="__main__":
    path = ""
    path = input("Satellite images folder:")
    if path == "":
        print("Using default path " + default_path)
        path = default_path

    print("\nReading image ...")
    tci,rgb = read_image(path)
    print("Done.\n")
    tci = np.array(tci,dtype='uint8')
    final = process(tci)
    #cv2.imwrite('final.jp2',final)
    print("Saving image \"final.jpg\" to path ...")
    print("Script complete.")
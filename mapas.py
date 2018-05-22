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
    mask = np.bitwise_or(mask_c, mask_d)
    road = image * mask
    image = road
    return image

def compare_images(image1, image2):
    f = plt.figure()
    f.add_subplot(1, 3, 1)
    plt.imshow(image1,cmap='gray')
    f.add_subplot(1, 3, 2)
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

def pre_process(tci):
    final = tci
    #subdividir a imagem de forma a que o aumento do contraste tenha melhores resultados
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    contrast = clahe.apply(final)
    compare_images(final,contrast)
    gamma = adjust_gamma(contrast)
    return gamma

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
    pre = pre_process(image)
    road = adaptative_thresholding(pre)
    compare_images(image,road)
    #teste = pre_process(road)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
    closing = cv2.morphologyEx(road, cv2.MORPH_CLOSE, kernel2)
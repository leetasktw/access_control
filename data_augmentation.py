import cv2
import os
import time
import argparse
import numpy as np
from imutils import paths
from datetime import datetime
from keras.preprocessing.image import ImageDataGenerator

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset", required=True,
    help="path to input directory of faces + images")
args = vars(ap.parse_args())

imagePaths = list(paths.list_images(args["dataset"]))
datagen = ImageDataGenerator(rotation_range=20, width_shift_range=0.2, height_shift_range=0.2, zoom_range=0.2, horizontal_flip=True)
for (i, imagePath) in enumerate(imagePaths):    
    img = cv2.imread(imagePath)   
    img = img.reshape((1,) + img.shape)
   
    count = 1
    for batch in datagen.flow(img, batch_size=10, save_format='jpeg'):
        img = batch[0]
        filename = datetime.now().strftime('%Y_%m_%d %H_%M_%S')
        cv2.imwrite(filename + '.jpg', img)
        count += 1
        time.sleep(1)
        if count > 20:
            break

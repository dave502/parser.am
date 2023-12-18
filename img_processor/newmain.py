import numpy as np
import pandas as pd
import os
import cv2
from mtcnn.mtcnn import MTCNN
detector = MTCNN()
def cropFaces(img):
    
    # detect faces in the image
    faces = detector.detect_faces(img)
    #print(faces)
    if len(faces) == 0:
        return faces
    x, y, width, height = faces[0]['box']
    #img[y:y+height , x:x+width, :]
    return img[y:y+height, x:x+width, :]
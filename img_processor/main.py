
from mtcnn import MTCNN 
import tensorflow as tf 
import cv2

# # For measuring the inference time.
import time

# import pandas as pd
from urllib.parse import urlparse, unquote
from fastapi import FastAPI
import uvicorn
import numpy as np
import os
from pathlib import Path
import requests
import io
from starlette.responses import StreamingResponse
from fastapi.responses import FileResponse, Response


app = FastAPI()

@app.get("/")
def read_root():
    return "Faces detection app"

@app.get("/img_url/{img_url:path}")
def make_pic_with_faces(img_url: str):
    """
     1. gets picture from web with url == img_url
     2. detects faces on the picture 
     3. saves the picture with detected faces on server 
     4. returns the url of picture fith faces 
     
     img_url - url of picture in web
    """
      
    img_url = unquote(img_url)
    TEMP_FOLDER = Path("./images_temp")
    
    url = urlparse(img_url)
    filename = url.path.replace("/", "-").strip('-')
    
    filepath = TEMP_FOLDER / filename

    dl_request = requests.get(img_url)
    dl_request.raise_for_status()
       
    with open(filepath, 'wb') as img_file:
      img_file.write(dl_request.content)

    image = cv2.imread(str(filepath))

    detector = MTCNN() 

    faces = detector.detect_faces(image)
    
    for face in faces:
      x, y, width, height = face['box']
      cv2.rectangle(image, (x, y), (x+width, y+height), (255, 0, 0), 2)
      
    new_file_path = str(Path("./images_new") / filename)

    result = cv2.imwrite(new_file_path, image)
      
    return {'img_url':"http://213.171.14.158/img/" + new_file_path}
    
    
@app.get("/img_get/{img_url:path}")
def get_pic_with_faces(img_url: str):
  
    """
    gets picture with faces from server with url == img_url
     
    img_url - url of picture on server (returned by /img_url/)
    """
    
    FOLDER = Path("./images_new")
    return FileResponse(FOLDER / img_url)
    
    
@app.get("/img/{img_url:path}")
def get_pic_with_faces(img_url: str):
  
    """
     1. gets picture from web with url == img_url
     2. detects faces on the picture 
     3. returns the picture as bytes response
     
     img_url - url of picture in web
    """
    
    img_url = unquote(img_url)
    TEMP_FOLDER = Path("./images_temp")
    
    url = urlparse(img_url)
    filename = url.path.replace("/", "-").strip('-')
    
    filepath = TEMP_FOLDER / filename

    dl_request = requests.get(img_url)
    dl_request.raise_for_status()
     
    with open(filepath, 'wb') as img_file:
      img_file.write(dl_request.content)

    image = cv2.imread(str(filepath))

    detector = MTCNN() 

    faces = detector.detect_faces(image)
    
    for face in faces:
      x, y, width, height = face['box']
      cv2.rectangle(image, (x, y), (x+width, y+height), (255, 0, 0), 2)
      
    success, img_numpy = cv2.imencode('.jpg', image)
    img_bytes = img_numpy.tostring()
    return Response(content=img_bytes, media_type="image/png")
      
 
if __name__ == "__main__":
    print("test")
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
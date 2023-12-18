
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

@app.get("/url_with_faces/{img_url:path}")
def detect_faces(img_url: str):
    
    img_url = unquote(img_url)
    TEMP_FOLDER = Path("./images_temp")
    
    print(f"{img_url=}")
    
    url = urlparse(img_url)
    filename = url.path.replace("/", "-").strip('-')
    
    print(f"{filename=}")
    
    filepath = TEMP_FOLDER / filename
    
    print(f"{filepath=}")

    dl_request = requests.get(img_url)
    dl_request.raise_for_status()
    
    print(f"{dl_request.status_code=}")
     
    with open(filepath, 'wb') as img_file:
      img_file.write(dl_request.content)
      
    print(f"{filepath=} {filepath.is_file()=}")
    # dl_request.raise_for_status()
    # print(2)
    # img = tf.image.decode_jpeg(dl_request.content, channels=3)
    # print(3)
    # tf.keras.utils.save_img(filename, img)
    # print(4)
    
    print(f"{str(filepath)=}")
    image = cv2.imread(str(filepath))
    print(f"{len(image)=}")
    detector = MTCNN() 
    print(6)
    faces = detector.detect_faces(image)
    print(7)
    
    for face in faces:
      x, y, width, height = face['box']
      cv2.rectangle(image, (x, y), (x+width, y+height), (255, 0, 0), 2)
      
    new_file_path = str(Path("./images_new") / filename)
    print(f"{new_file_path=}")
    result = cv2.imwrite(new_file_path, image)
    print(f"{result=}")
      
    return {'img_url':"http://213.171.14.158/img/" + new_file_path}
    
    
@app.get("/img/{img_url:path}")
def detect_faces(img_url: str):
    
    FOLDER = Path("./images_new")
    return FileResponse(FOLDER / img_url)
    
    
@app.get("/img_with_faces/{img_url:path}")
def detect_faces(img_url: str):
    
    img_url = unquote(img_url)
    TEMP_FOLDER = Path("./images_temp")
    
    print(f"{img_url=}")
    
    url = urlparse(img_url)
    filename = url.path.replace("/", "-").strip('-')
    
    print(f"{filename=}")
    
    filepath = TEMP_FOLDER / filename
    
    print(f"{filepath=}")

    dl_request = requests.get(img_url)
    dl_request.raise_for_status()
    
    print(f"{dl_request.status_code=}")
     
    with open(filepath, 'wb') as img_file:
      img_file.write(dl_request.content)
      
    print(f"{filepath=} {filepath.is_file()=}")

    
    print(f"{str(filepath)=}")
    image = cv2.imread(str(filepath))
    print(f"{len(image)=}")
    detector = MTCNN() 
    print(6)
    faces = detector.detect_faces(image)
    print(7)
    
    for face in faces:
      x, y, width, height = face['box']
      cv2.rectangle(image, (x, y), (x+width, y+height), (255, 0, 0), 2)
      
    return Response(content=image, media_type="image/png")
      
 


if __name__ == "__main__":
    print("test")
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
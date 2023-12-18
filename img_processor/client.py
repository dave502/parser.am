import requests
from urllib.parse import quote, unquote
from urllib.parse import urlparse
from pathlib import Path

SERVER_URL = 'http://213.171.14.158:8080/url_with_faces/' # 'http://localhost:8501/v1/models/resnet:predict'
IMAGE_URL = 'https://www.urlencoder.io/static/79f22f13dec2866b2903a6c89f31a9b4/72e01/how-to-do-url-encoding-in-java.jpg'

def main():

  response = requests.get(SERVER_URL + quote(IMAGE_URL, safe=''), stream=True)
  response.raise_for_status()
  new_img = response.json().get('img_url')
  print()

if __name__ == '__main__':
  main()

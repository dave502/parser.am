import requests
from urllib.parse import quote, unquote
from urllib.parse import urlparse
from pathlib import Path

SERVER_URL = 'http://213.171.14.158:8080/detect_faces/' # 'http://localhost:8501/v1/models/resnet:predict'
IMAGE_URL = 'https://www.urlencoder.io/static/79f22f13dec2866b2903a6c89f31a9b4/72e01/how-to-do-url-encoding-in-java.jpg'

def main():
  # Download the image
  
  img_url = quote(IMAGE_URL, safe='')
  url = urlparse(img_url)
  filename = url.path.replace("/", "-").strip('-')
  filepath = Path("./images_temp") / filename
  
  print(filepath)
  
  img_url = unquote(img_url)
  dl_request = requests.get(img_url)
  dl_request.raise_for_status()
  print(1)
  with open(filepath, 'wb') as img_file:
    img_file.write(dl_request.content)
  
  dl_request = requests.get(SERVER_URL + quote(IMAGE_URL, safe=''), stream=True)
  dl_request.raise_for_status()

  if MODEL_ACCEPT_JPG:
    # Compose a JSON Predict request (send JPEG image in base64).
    jpeg_bytes = base64.b64encode(dl_request.content).decode('utf-8')
    predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes
  else:
    # Compose a JOSN Predict request (send the image tensor).
    jpeg_rgb = Image.open(io.BytesIO(dl_request.content))
    # Normalize and batchify the image
    jpeg_rgb = np.expand_dims(np.array(jpeg_rgb) / 255.0, 0).tolist()
    predict_request = json.dumps({'instances': jpeg_rgb})

  # Send few requests to warm-up the model.
  for _ in range(3):
    response = requests.post(SERVER_URL, data=predict_request)
    response.raise_for_status()

  # Send few actual requests and report average latency.
  total_time = 0
  num_requests = 10
  for _ in range(num_requests):
    response = requests.post(SERVER_URL, data=predict_request)
    response.raise_for_status()
    total_time += response.elapsed.total_seconds()
    prediction = response.json()['predictions'][0]

  print('Prediction class: {}, avg latency: {} ms'.format(
      np.argmax(prediction), (total_time * 1000) / num_requests))


if __name__ == '__main__':
  main()

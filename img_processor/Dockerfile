FROM tensorflow/serving
EXPOSE 8501
RUN tensorflow_model_server --rest_api_port=8501 --model_name=resnet --model_base_path=/model/resnet
FROM tensorflow/serving

ENV MODEL_PATH=/models/resnet
ENV MODEL_NAME=resnet
ENV SAVED_MODEL_PATH="https://storage.googleapis.com/download.tensorflow.org/models/official/20181001_resnet/savedmodels/resnet_v2_fp32_savedmodel_NHWC_jpg.tar.gz"

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl  

RUN echo ${MODEL_PATH}/1/ && mkdir -p ${MODEL_PATH}/1/ \
    && curl -s $SAVED_MODEL_PATH | tar --strip-components=2 -C ${MODEL_PATH}/1/ -xvz

EXPOSE 8501

# RUN tensorflow_model_server --rest_api_port=8501 --model_name=$MODEL_NAME --model_base_path=$MODEL_PATH
FROM tensorflow/serving

ENV MODEL_PATH=/models/resnet
# ENV MODEL_NAME=resnet
# SAVED_MODEL_PATH

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl  

RUN echo $MODEL_PATH && mkdir -p $MODEL_PATH \
    && curl -s $SAVED_MODEL_PATH | tar --strip-components=2 -C $MODEL_PATH -xvz

EXPOSE 8501

# RUN tensorflow_model_server --rest_api_port=8501 --model_name=$MODEL_NAME --model_base_path=$MODEL_PATH
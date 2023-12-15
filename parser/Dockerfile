FROM python:3.11.2-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRON_MODE "Development"
ENV AppDir=/app
#ENV PYTHONPATH $AppDir

WORKDIR $AppDir

COPY . $AppDir

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y cron
RUN touch $AppDir/logs/cron.log
RUN chmod -R +x ./cron
# https://docs.docker.com/config/containers/multi-service_container/
RUN chmod +x ./run.sh

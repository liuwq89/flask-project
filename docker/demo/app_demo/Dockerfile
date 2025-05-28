FROM python3.9:ubuntu22.04

ENV RUN_ENV=prod

WORKDIR /apps/app_server_name

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# start up supervisor, run server and celery.
COPY supervisor.conf /etc/supervisor/supervisord.conf
COPY app_server_name.ini /etc/supervisor/conf.d/app_server_name.ini
COPY celery_service.ini /etc/supervisor/conf.d/celery_service.ini

COPY target /apps/app_server_name

CMD ["supervisord","-c","/etc/supervisor/supervisord.conf"]


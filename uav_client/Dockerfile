FROM python:3

ADD uav_client.py /

RUN pip install numpy
RUN pip install pika

CMD [ "python", "uav_client.py" ]

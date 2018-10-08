FROM python:3

RUN pip install numpy
RUN pip install pika

ADD uav_client.py /
CMD [ "python", "uav_client.py" ]

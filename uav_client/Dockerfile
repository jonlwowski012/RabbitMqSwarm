FROM python:3

RUN pip install numpy
RUN pip install pika
RUN pip install pyyaml

ADD config.yaml /
ADD uav_client.py /
CMD [ "python", "uav_client.py" ]

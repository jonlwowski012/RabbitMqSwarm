FROM python:3

RUN pip install numpy
RUN pip install pika

ADD asv_client.py /
CMD [ "python", "asv_client.py" ]

FROM python:3

ADD asv_client.py /

RUN pip install numpy
RUN pip install pika

CMD [ "python", "asv_client.py" ]

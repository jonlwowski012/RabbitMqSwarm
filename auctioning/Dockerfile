FROM python:3

ADD auctioning.py /

RUN pip install numpy
RUN pip install pika

CMD [ "python", "auctioning.py" ]

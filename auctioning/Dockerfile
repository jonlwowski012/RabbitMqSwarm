FROM python:3

RUN pip install numpy
RUN pip install pika

ADD auctioning.py /
CMD [ "python", "auctioning.py" ]

FROM python:3

RUN pip install numpy
RUN pip install pika
RUN pip install pyyaml
RUN pip install mysql-connector

ADD config.yaml /
ADD save_auctioning.py /
CMD [ "python", "save_auctioning.py" ]

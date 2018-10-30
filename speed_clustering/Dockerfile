FROM python:3

RUN pip install numpy
RUN pip install pika
RUN pip install scikit-learn
RUN pip install scipy
RUN pip install pyyaml
RUN pip install mysql-connector
RUN apt-get update

ADD config.yaml /
ADD speed_clustering.py /
CMD [ "python3",  "speed_clustering.py" ]

FROM python:3

RUN pip install numpy
RUN pip install pika
RUN pip install scikit-learn
RUN pip install scipy
RUN apt-get update

ADD speed_clustering.py /
CMD [ "python3",  "speed_clustering.py" ]

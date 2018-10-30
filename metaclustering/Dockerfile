FROM python:3

RUN pip install numpy
RUN pip install pika
RUN pip install scipy
RUN pip install scikit-fuzzy
RUN pip install scikit-learn
RUN pip install pyyaml
RUN pip install mysql-connector

ADD config.yaml /
ADD metaclustering.py /
CMD [ "python", "metaclustering.py" ]

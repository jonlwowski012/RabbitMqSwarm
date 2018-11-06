FROM python:3

RUN pip install numpy
RUN pip install pika
RUN pip install scikit-learn
RUN pip install scipy
RUN pip install matplotlib
RUN pip install pyyaml
RUN pip install mysql-connector

ADD config.yaml /
ADD clustering.py /
CMD [ "python3",  "clustering.py" ]

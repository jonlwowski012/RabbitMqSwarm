FROM python:3

ADD metaclustering.py /

RUN pip install numpy
RUN pip install pika
RUN pip install scikit-fuzzy
RUN pip install scikit-learn

CMD [ "python", "metaclustering.py" ]

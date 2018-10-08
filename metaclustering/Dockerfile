FROM python:3

RUN pip install numpy
RUN pip install pika
RUN pip install scikit-fuzzy
RUN pip install scikit-learn

ADD metaclustering.py /
CMD [ "python", "metaclustering.py" ]

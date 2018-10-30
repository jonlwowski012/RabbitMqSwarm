FROM python:3

RUN pip install numpy
RUN pip install pika
RUN pip install pyyaml
RUN pip install mysql-connector
RUN git clone https://github.com/dmishin/tsp-solver.git && cd tsp-solver && python setup.py install

ADD config.yaml /
ADD tsp.py /
CMD [ "python", "tsp.py" ]

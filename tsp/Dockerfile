FROM python:3

RUN pip install numpy
RUN pip install pika
RUN git clone https://github.com/dmishin/tsp-solver.git && cd tsp-solver && python setup.py install

ADD tsp.py /
CMD [ "python", "tsp.py" ]

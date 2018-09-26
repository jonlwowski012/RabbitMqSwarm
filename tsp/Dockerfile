FROM python:3

ADD tsp.py /

RUN pip install numpy
RUN pip install pika
RUN git clone https://github.com/dmishin/tsp-solver.git && cd tsp-solver && python setup.py install

CMD [ "python", "tsp.py" ]

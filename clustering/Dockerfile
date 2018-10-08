FROM python:3

RUN pip install numpy
RUN pip install pika
RUN pip install scikit-learn
RUN pip install scipy
RUN apt-get update
RUN apt-get install python3-mpi4py -y
RUN apt install libopenmpi-dev -y
RUN pip install mpi4py

ADD clustering.py /
#CMD [ "mpiexec", "--allow-run-as-root", "-n", "4", "python3", "-m", "mpi4py", "clustering.py" ]
CMD [ "python3",  "clustering.py" ]

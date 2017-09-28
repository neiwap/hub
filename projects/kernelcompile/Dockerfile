FROM gcc as kernelcompile
RUN apt-get update \
&&  apt-get install -y \
    bc \
    time \
    python \
    python-pip
WORKDIR kernelcompile
RUN git clone https://github.com/torvalds/linux
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY benchmark.py ./benchmark.py
ENTRYPOINT [ "python", "benchmark.py" ]

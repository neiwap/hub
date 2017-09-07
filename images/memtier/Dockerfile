FROM memtier_benchmark
RUN apt-get update \
&&  apt-get install -y \
    python \
    python-pip
WORKDIR memtier
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY memtier.py ./memtier.py
ENTRYPOINT [ "python", "memtier.py" ]

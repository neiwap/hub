FROM python
WORKDIR collector
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY collector.py ./collector.py
ENTRYPOINT [ "python", "collector.py" ]
CMD [ "--print" ]

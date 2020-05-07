FROM python:3.7

ADD filler/req.txt /app/filler/req.txt

RUN pip install --trusted-host pypi.python.org -r /app/filler/req.txt

WORKDIR /app

ADD filler/filler.py /app/filler/

ENV PYTHONPATH /app

CMD [ "python", "filler/filler.py" ]
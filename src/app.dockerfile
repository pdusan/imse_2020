FROM python:3.7

ADD app/req.txt /app/main/req.txt

RUN pip install --trusted-host pypi.python.org -r /app/main/req.txt

WORKDIR /app

ADD app/app.py /app/main/

ENV PYTHONPATH /app

CMD [ "python", "main/app.py" ]
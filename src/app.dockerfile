FROM python:3.7

ADD app/req.txt /app/main/req.txt

RUN pip install --trusted-host pypi.python.org -r /app/main/req.txt

WORKDIR /app

ADD app/app.py /app/

ADD app/templates /app/templates/

ADD app/static /app/static/

ENV PYTHONPATH /app

CMD [ "python", "app.py" ]
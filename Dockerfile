FROM python:3.7
WORKDIR /project/flaskai
COPY requirements.txt /project/flaskai
RUN pip install -r requirements.txt
RUN pip install gunicorn gevent
COPY . /project/flaskai

ENTRYPOINT ["gunicorn", "run:app", "-c", "gunicorn.conf.py"]
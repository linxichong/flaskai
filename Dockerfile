FROM python:3.7
WORKDIR /project/flaskai-img
COPY requirements.txt /project/flaskai-img
RUN pip install -r requirements.txt
RUN pip install gunicorn gevent
COPY . /project/flaskai-img

ENTRYPOINT ["gunicorn", "run:app", "-c", "gunicorn.conf.py"]
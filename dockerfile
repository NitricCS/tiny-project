FROM python:3.11
ADD tiny.py .

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app

RUN pip install -r requirements.txt
COPY . /opt/app

ENTRYPOINT [ "python", "./tiny.py" ]
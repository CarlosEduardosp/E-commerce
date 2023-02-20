FROM python:3

COPY . /delivery

RUN pip install flask && pip install flask_sqlalchemy && pip install requests

WORKDIR  /delivery

CMD ["python", "main.py"]

EXPOSE 5000
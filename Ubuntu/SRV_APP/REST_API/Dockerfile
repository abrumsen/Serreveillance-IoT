FROM python:3.11-slim-bullseye

WORKDIR /restapi-docker
COPY requirements.txt app.py ./

RUN pip3 install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

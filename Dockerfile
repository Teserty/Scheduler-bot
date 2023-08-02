FROM python:3.8-slim-buster

ADD . .

RUN pip3 install -r requirements.txt
CMD [ "python", "./Scheduler-bot.py" ]

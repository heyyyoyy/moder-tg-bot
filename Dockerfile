FROM python:3.7

RUN pip install pipenv

COPY Pipfile Pipfile.lock /opt/bot/
WORKDIR /opt/bot/

RUN pipenv install --system --deploy

COPY .env handlers.py models.py polling.py settings.py views.py /opt/bot/
WORKDIR /opt/bot/

CMD ["python", "polling.py"]

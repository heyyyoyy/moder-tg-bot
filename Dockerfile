FROM python:3.7

RUN pip install pipenv

COPY Pipfile Pipfile.lock /opt/bot/
WORKDIR /opt/bot/

RUN pipenv install --system --deploy

COPY .env bot/ conf.d/webhook_cert.pem /opt/bot/
WORKDIR /opt

EXPOSE 8888
CMD ["python", "-m", "bot.server"]

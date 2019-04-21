from kennethreitz/pipenv

ENV PYTHONDONTWRITEBYTECODE 1

COPY . /app

CMD python3 setup.py test

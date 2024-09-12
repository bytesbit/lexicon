FROM python:3.8.10-buster


RUN apt-get update \
    && apt-get install -y --no-install-recommends tini ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

WORKDIR /lexicon

COPY . /lexicon/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r requirements.txt


CMD ["python", "manage.py", "runserver"]

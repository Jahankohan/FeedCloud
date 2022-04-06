FROM python:3.9-slim-buster as base
RUN apt-get update && \
    apt-get install --no-install-recommends --yes curl netcat
RUN pip install --upgrade pip pip-tools
RUN mkdir /app

FROM base as builder
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    build-essential autoconf automake libtool pkg-config libc++-dev git libffi-dev
COPY requirements /app/requirements
RUN pip install -r /app/requirements/requirements.txt

FROM base
COPY --from=builder /usr/local /usr/local
COPY . /app
WORKDIR /app
EXPOSE 8000
ARG SECRET_KEY
ENV SECRET_KEY $SECRET_KEY
CMD ["/app/dockerfiles/feedcloud/run.sh"]

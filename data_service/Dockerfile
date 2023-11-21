FROM python:3.9.16

LABEL maintainer="ReAPI" version="1.0.0"

ADD . /code

WORKDIR /code

VOLUME ["/opt/project", "/data"]

RUN pip install --no-index --find-links=./py_pkgs -r requirements.txt

RUN rm -r ./py_pkgs

ENTRYPOINT ["python", "reapi_data_service.py"]
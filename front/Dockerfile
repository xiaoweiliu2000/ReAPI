FROM node:18

LABEL maintainer="ReAPI" version="1.0.0"

ADD . /code

WORKDIR /code

VOLUME ["/data"]

ENTRYPOINT ["npm", "run", "serve"]

FROM node:latest as builder
WORKDIR /app

# Install dependencies
COPY client/package.json client/yarn.lock /app/
RUN yarn --frozen-lockfile

# Build
COPY .git/ /app/.git/
COPY client/ /app/
RUN yarn build


FROM girder/girder as runtime

# ENV GIRDER_MONGO_URI mongodb://mongo:27017/girder
# ENV GIRDER_ADMIN_USER admin
# ENV GIRDER_ADMIN_PASSWORD letmein
# ENV CELERY_BROKER_URL amqp://guest:guest@rabbit/
# ENV BROKER_CONNECTION_TIMEOUT 2

# Initialize python virtual environment
RUN apt-get update && apt-get install -y python3.7-venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3.7 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=builder /app/dist/ $VIRTUAL_ENV/share/girder/static/core3d/

# install tini init system
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

WORKDIR /home/core3d

COPY server/setup.py /home/core3d/
RUN pip install --no-cache-dir .

COPY server/ /home/core3d/
RUN pip install --no-deps .

RUN girder build

CMD [ "/tini", "-v". "--", "girder", "serve", "--host", "0.0.0.0" ]

FROM node:latest as builder
WORKDIR /app

# Install dependencies
COPY client/package.json client/yarn.lock /app/client/
COPY client/resonantgeoview /app/client/resonantgeoview
RUN yarn --cwd /app/client --frozen-lockfile

# Copy client and git files
COPY client/ /app/client/
COPY .git/ /app/.git/
COPY .gitmodules /app/.gitmodules

# Install resonantgeoview
RUN git submodule update --init --recursive

# Build
RUN yarn --cwd /app/client build

########Girder########
FROM girder/girder as runtime

ENV GIRDER_MONGO_URI mongodb://mongo:27017/girder
ENV GIRDER_ADMIN_USER admin
ENV GIRDER_ADMIN_PASSWORD letmein

# Initialize python virtual environment
RUN apt-get update && apt-get install -y python3.7-venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3.7 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=builder /app/client/dist/ $VIRTUAL_ENV/share/girder/static/core3d/

# install tini init system
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

WORKDIR /home/core3d

# Install GDAL deps
RUN apt-get update \
 && apt-get install -y binutils libproj-dev gdal-bin libgdal-dev

# Install GDAL
RUN pip install "gdal==$(gdal-config --version)"

# Pin this dep so that install below succeeds
RUN pip install "pyproj==2.6.1"

COPY server/setup.py /home/core3d/
RUN pip install --no-cache-dir .

COPY server/ /home/core3d/
RUN pip install --no-deps .

RUN girder build

COPY docker/provision/ /home/provision
ENTRYPOINT [ "/home/provision/girder_entrypoint.sh" ]

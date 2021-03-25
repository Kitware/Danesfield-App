FROM node:latest as builder
WORKDIR /app

# Install resonantgeoview
COPY .git/ /app/.git/
COPY .gitmodules /app/.gitmodules
COPY client /app/client
RUN git submodule update --init --recursive

# Install dependencies
RUN yarn --cwd /app/client --frozen-lockfile

# Copy client and git files
COPY client/ /app/client/

# Build
RUN yarn --cwd /app/client build

########Girder########
FROM girder/girder as runtime

ENV GIRDER_MONGO_URI mongodb://mongo:27017/girder
ENV GIRDER_ADMIN_USER admin
ENV GIRDER_ADMIN_PASSWORD letmein

ENV CELERY_BROKER_URL amqp://guest:guest@rabbit/
ENV BROKER_CONNECTION_TIMEOUT 2

# Initialize python virtual environment
RUN apt-get update && apt-get install -y python3.7-venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3.7 -m venv $VIRTUAL_ENV

# Activate the environment
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Cryptography requires latest pip, setuptools.
# https://cryptography.io/en/latest/faq.html#installing-cryptography-fails-with-error-can-not-find-rust-compiler
RUN pip install -U pip setuptools

# Copy built frontend to be served by Girder
COPY --from=builder /app/client/dist/ $VIRTUAL_ENV/share/girder/static/core3d/

# install tini init system
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

WORKDIR /home/core3d

# Install numpy before installing GDAL
# https://gis.stackexchange.com/questions/153199/import-error-no-module-named-gdal-array
RUN pip install "numpy>=1.20.1"

# Install GDAL deps
RUN apt-get update \
 && apt-get install -y binutils libproj-dev gdal-bin libgdal-dev libtiff-dev

# Install GDAL
RUN pip install gdal==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"

# Install packages that can't be listed properly in setup.py
COPY server/extra-requirements.txt /home/core3d/
RUN pip install -r extra-requirements.txt

# Copy this header file so it can be found by venv
# https://stackoverflow.com/a/65776297
RUN cp /usr/include/x86_64-linux-gnu/tiff.h $VIRTUAL_ENV/include/tiff.h

COPY server/setup.py /home/core3d/
RUN pip install --no-cache-dir .

COPY server/ /home/core3d/
RUN pip install --no-deps .

RUN girder build

COPY docker/provision/ /home/provision
ENTRYPOINT [ "/home/provision/girder_entrypoint.sh" ]

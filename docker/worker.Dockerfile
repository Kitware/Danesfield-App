FROM gitlab.kitware.com:4567/core3d/danesfield-app/danesfield-app-girder:latest as runtime

WORKDIR /home/danesfield

ENV CELERY_BROKER_URL amqp://guest:guest@rabbit/
ENV BROKER_CONNECTION_TIMEOUT 2

RUN apt-get update && \
	export DEBIAN_FRONTEND=noninteractive && \
  apt-get install -qy software-properties-common python3-software-properties && \
  apt-get update && apt-get install -qy \
    build-essential \
    wget \
    libvips \
    libvips-dev \
    python3.7 \
    libpython3.7-dev && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

# Activate the venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Needed for large image
RUN pip install pyvips

# Switch over to user "worker"
RUN useradd -D --shell=/bin/bash && useradd -m worker
RUN chown -R worker:worker /usr/local/lib/python*
USER worker

ENTRYPOINT ["/tini", "--"]
CMD ["/home/provision/girder_worker_entrypoint.sh"]

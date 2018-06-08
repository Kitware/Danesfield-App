# Dockerfile extension for p3d to support running from Girder Worker.

FROM p3d

COPY ./docker-entrypoint.sh docker-entrypoint.sh

ENTRYPOINT ["/bin/bash", "./docker-entrypoint.sh"]

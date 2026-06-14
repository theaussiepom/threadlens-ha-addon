# Thin wrapper around the published ThreadLens Core image.
# Supervisor builds this add-on locally; Core application code is not duplicated.
ARG BUILD_VERSION=0.1.2
FROM ghcr.io/theaussiepom/threadlens:${BUILD_VERSION}

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash \
    && rm -rf /var/lib/apt/lists/*

COPY config_generator.py /config_generator.py
COPY run.sh /run.sh
RUN chmod a+x /run.sh

LABEL \
  io.hass.version="0.1.0" \
  io.hass.type="addon" \
  io.hass.arch="aarch64|amd64"

USER threadlens

CMD ["/bin/bash", "/run.sh"]

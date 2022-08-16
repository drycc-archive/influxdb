FROM registry.drycc.cc/drycc/base:bullseye

ENV DRYCC_UID=1001 \
  DRYCC_GID=1001 \
  DRYCC_HOME_DIR=/data \
  PYTHON_VERSION="3.10.4" \
  INFLUXDB_VERSION="2.2.0"

COPY . /

RUN groupadd drycc --gid ${DRYCC_GID} \
  && useradd drycc -u ${DRYCC_UID} -g ${DRYCC_GID} -s /bin/bash -m -d ${DRYCC_HOME_DIR} \
  && install-stack python $PYTHON_VERSION \
  && . init-stack \
  && set -eux; pip3 install --disable-pip-version-check sanic aiohttp 2>/dev/null; set +eux \
  && install-stack influxdb $INFLUXDB_VERSION \
  && chmod +x /usr/local/bin/start-proxy.py /usr/local/bin/start-backend.sh \
  && rm -rf \
      /usr/share/doc \
      /usr/share/man \
      /usr/share/info \
      /usr/share/locale \
      /var/lib/apt/lists/* \
      /var/log/* \
      /var/cache/debconf/* \
      /etc/systemd \
      /lib/lsb \
      /lib/udev \
      /usr/lib/`echo $(uname -m)`-linux-gnu/gconv/IBM* \
      /usr/lib/`echo $(uname -m)`-linux-gnu/gconv/EBC* \
      /var/cache/apk/* /root/.gem/ruby/*/cache/*.gem \
  && bash -c "mkdir -p /usr/share/man/man{1..8}"

VOLUME ${DRYCC_HOME_DIR}

USER ${DRYCC_UID}
CMD ["start-backend.sh"]

# Expose the proxy port
EXPOSE 8000
# Expose the backend port
EXPOSE 8086

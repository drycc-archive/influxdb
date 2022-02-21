FROM docker.io/drycc/base:bullseye

RUN adduser --system \
	--shell /bin/bash \
	--disabled-password \
	--home /data \
	--group \
	drycc

COPY . /
ENV INFLUXDB_VERSION="2.1.1"

RUN install-stack influxdb $INFLUXDB_VERSION \
  && mkdir -p /data \
  && chmod +x /usr/local/bin/start-influxdb \
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

VOLUME /data

USER drycc
CMD ["start-influxdb"]

# Expose the ssl http api port
EXPOSE 8084
# Expose the http api port
EXPOSE 8086

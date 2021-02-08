FROM docker.io/library/debian:stable
ARG INFLUXDB_VERSION=2.0.3
COPY . /

RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && apt-get install -y --no-install-recommends \
    bash \
    curl \
    ca-certificates \
  && INFLUXDB_PATH=/tmp/influxdb2_${INFLUXDB_VERSION}_$(dpkg --print-architecture).deb \
  && curl -o $INFLUXDB_PATH https://dl.influxdata.com/influxdb/releases/influxdb2_${INFLUXDB_VERSION}_$(dpkg --print-architecture).deb \
  && dpkg -i $INFLUXDB_PATH \
  && mkdir -p /data \
  && chmod +x /usr/local/bin/start-influxdb \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man /usr/share/doc

VOLUME /data

CMD ["start-influxdb"]

# Expose the ssl http api port
EXPOSE 8084
# Expose the http api port
EXPOSE 8086

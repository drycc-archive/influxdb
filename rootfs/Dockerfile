FROM quay.io/influxdb/influxdb:v2.0.3
COPY . /
RUN mkdir -p /data \
	&& chmod +x /home/influxdb/start-influxdb

VOLUME /data

WORKDIR /home/influxdb
CMD ["./start-influxdb"]

# Expose the ssl http api port
EXPOSE 8084
# Expose the http api port
EXPOSE 8086

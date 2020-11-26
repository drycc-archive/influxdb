FROM influxdb:1.8.3

COPY . /

RUN curl -SL -o /home/influxdb/envtpl https://github.com/arschles/envtpl/releases/download/0.2.3/envtpl_linux_amd64 \
	&& chmod +x /home/influxdb/envtpl \
	&& mkdir -p /data \
	&& chmod +x /home/influxdb/start-influxdb

VOLUME /data

WORKDIR /home/influxdb
CMD ["./start-influxdb"]

# Expose the ssl http api port
EXPOSE 8084
# Expose the http api port
EXPOSE 8086

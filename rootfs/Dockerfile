FROM drycc/go-dev:latest AS go-dev


FROM influxdb:1.8.3

COPY . /
COPY --from=go-dev /bin/envtpl /home/influxdb/envtpl

RUN mkdir -p /data \
	&& chmod +x /home/influxdb/start-influxdb

VOLUME /data

WORKDIR /home/influxdb
CMD ["./start-influxdb"]

# Expose the ssl http api port
EXPOSE 8084
# Expose the http api port
EXPOSE 8086

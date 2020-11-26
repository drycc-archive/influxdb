install:
	helm upgrade influxdb charts/influxdb --install --namespace drycc --set influxdb.org=${IMAGE_PREFIX},influxdb.docker_tag=${VERSION}

upgrade: 
	helm upgrade influxdb charts/influxdb --namespace drycc --set influxdb.org=${IMAGE_PREFIX},influxdb.docker_tag=${VERSION}

uninstall:
	helm delete influxdb
#!/bin/bash

export INFLUXD_ENGINE_PATH="/data"
export INFLUXD_BOLT_PATH="/data/influxd.bolt"
export INFLUXD_CONFIG_PATH="/data/influxdb.conf"
export INFLUX_CONFIGS_PATH="/data/configs"
export INFLUXD_HTTP_BIND_ADDRESS=":8086"

function check_env(){
  if [ -z "${INFLUXDB_ORG}" ]; then
    echo "Please set INFLUXDB_ORG environment"
    exit 1
  fi
  if [ -z "${INFLUXDB_BUCKET}" ]; then
    echo "Please set INFLUXDB_BUCKET environment"
    exit 1
  fi  
  if [ -z "${INFLUXDB_USER}" ]; then
    echo "Please set INFLUXDB_USER environment"
    exit 1
  fi
  if [ -z "${INFLUXDB_PASSWORD}" ]; then
    echo "Please set INFLUXDB_PASSWORD environment"
    exit 1
  fi
  if [ -z "${INFLUXDB_TOKEN}" ]; then
    echo "Please set INFLUXDB_TOKEN environment"
    exit 1
  fi
  if [ -z "${INFLUXDB_RETENTION}" ]; then
    echo "Please set INFLUXDB_RETENTION environment"
    exit 1
  fi
}

function init_influxdb(){
  INFLUXDB_HTTP_BIND_ADDRESS="127.0.0.1:8086" influxd run --store=disk &
  pid=$!
  echo "Waiting to run influxdb bg no auth..."
  while [[ $(curl -s -o /dev/null -w "%{http_code}" localhost:8086/ping) != "204" ]]; do 
    sleep 5;
  done

  while true
  do
    has_bucket=$(influx bucket ls -o "${INFLUXDB_ORG}" -n "$INFLUXDB_BUCKET" 2>/dev/null | awk '$2==ENVIRON["INFLUXDB_BUCKET"] {print $2}')
    if [ "$has_bucket" ]; then
      break
    else
      influx setup -f \
	      -o "${INFLUXDB_ORG}" \
        -b "${INFLUXDB_BUCKET}" \
        -u "${INFLUXDB_USER}" \
        -p "${INFLUXDB_PASSWORD}" \
        -t "${INFLUXDB_TOKEN}" \
        -r "${INFLUXDB_RETENTION}"
    fi
    echo "Waiting to initialize influxdb..."
    sleep 2s
  done
  kill -s TERM $pid && wait $pid
}

check_env
if [[ ! -f "${INFLUX_CONFIGS_PATH}" ]]; then
  init_influxdb
  echo "Initialization of database completed."
fi
exec influxd run --store disk

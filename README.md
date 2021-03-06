# SimpleMetric
Latency benchmark for time series database

## Setup benchmark tool
1. Install python version 3.6
2. Install requirements `pip install -r requirements.txt`

## Run benchmark tool
1. Run `python data_generator.py` to generate data for benchmark
```
usage: data_generator.py [-h] --out_file OUT_FILE [--frequency FREQUENCY]
                         [--start_time START_TIME] [--end_time END_TIME]
                         [--sensor_number SENSOR_NUMBER] [--format FORMAT]

Generate values

optional arguments:
  -h, --help            show this help message and exit
  --out_file OUT_FILE   Output file
  --frequency FREQUENCY
                        Frequency in seconds (default: 1 sec)
  --start_time START_TIME
                        Beginning timestamp (RFC3339). (default
                        "2019-01-01T00:00:00Z")
  --end_time END_TIME   Ending timestamp (RFC3339). (default
                        "2019-01-02T00:00:00Z")
  --sensor_number SENSOR_NUMBER
                        Number of sensors (default: 10)
  --format FORMAT       Please select output format ["influx", "csv", "json"]
                        (default: "influx")
```

Here is snippet of Python code to simplify running of data_generator
```python
from datetime import datetime, timedelta
import os

start = datetime(2019, 1, 1)

if not os.path.exists('../data/csv/'):
	os.makedirs('../data/csv/')

for i in range(1, 101):
    delta = timedelta(days=1)
    stop = start + delta
    start_date = start.strftime('%Y-%m-%dT%H:%M:%SZ')
    stop_date = stop.strftime('%Y-%m-%dT%H:%M:%SZ')
    cmd = 'python data_generator.py --start_time "{start}" --end_time "{stop}" --format "csv" --sensor_number 10 --out_file ../data/csv/csv_1sec_{day}d.dat'.format(start=start_date, stop=stop_date, day=i)
    start = stop
    os.system(cmd)
```

2. Run `python runner.py` to process benchmark
```
usage: runner.py [-h] [--thread THREAD] [--aggregate AGGREGATE]
                 [--latency LATENCY] [--packetloss PACKETLOSS] --database
                 
DATABASE
Load data test

optional arguments:
  -h, --help            show this help message and exit
  --thread THREAD       number of connections. default is 1
  --aggregate AGGREGATE
                        type of aggregate function [max, count, avg, sum].
                        default is "sum"
  --latency LATENCY     latency in ms.
  --packetloss PACKETLOSS
                        packet loss type in percentage
  --database DATABASE   database type [cratedb, graphite, influxdb, kairosdb,
                        kdb, timescaledb]
```

## Setup database within Docker container

### [InfluxDB](https://www.influxdata.com/)
1. Pull Docker image `docker pull influxdb:latest`
2. Run Docker container `docker run -p 8086:8086 -p 8083:8083 -p 8090:8090 -e INFLUXDB_REPORTING_DISABLED=true -e INFLUXDB_DATA_QUERY_LOG_ENABLED=false -e INFLUXDB_HTTP_LOG_ENABLED=false -e INFLUXDB_CONTINUOUS_QUERIES_LOG_ENABLED=false influxdb:latest`

### [KDB+](https://kx.com/)
1. Download 'q.zip' from https://kx.com/connect-with-us/download/
2. Copy 'q.zip' to the docker/kdb/ folder
3. Build KDB+ docker with `docker build -t kdb -f kdb/Dockerfile .`
4. Run Docker container `docker run -p 5000:5000 kdb q -p 5000`
5. To run benchmark for KDB+ it is necessary to install `java`. For Ubuntu you can use this command: `sudo apt install openjdk-8-jdk`.

### [Graphite](https://graphiteapp.org/)
1. Got to the docker directory `cd docker`
2. Build Graphite docker with `docker build -t graphite -f graphite/Dockerfile .`
3. Run Docker container `docker run -p 2003:2003 -p 8000:8000 graphite`

### [TimescaleDB](https://www.timescale.com/)
1. Got to the docker directory `cd docker`
2. Pull Docker image `docker pull timescale/timescaledb`
3. Run Docker container `docker run -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=benchmarkdb timescale/timescaledb`

### [KairosDB](https://kairosdb.github.io/)
1. Got to the docker directory `cd docker`
2. Build KairosDB docker with `docker build -t kairosdb -f kairosdb/Dockerfile .`
3. Run Docker container `docker run -p 4242:4242 -p 8080:8080 kairosdb`

### [CrateDB](https://crate.io/)
1. Pull Docker image `docker pull crate:latest`
2. Run Docker container `docker run -p 4200:4200 -p 4300:4300 -p 5432:5432 crate:latest -Ccluster.name=democluster -Chttp.cors.enabled=true -Chttp.cors.allow-origin="*"`
* In case of _"ERROR: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]"_ please run this command before starting docker:
```
sudo sysctl -w vm.max_map_count=262144
```
## Simulate network latency and packet loss

Network simulation was done by `tc` and `netem`

### Setup network simualtion
1. Install `tc` and `netem` linux tools
2. Run `docker network create slownet` to create a slow network
3. Run `docker network inspect slownet` to get the id of the slow network
4. Run `ifconfig` and pick right network id based on `docker network inspect` and `ifconfig`. Let's assume it will be called NETWORKID

### Run network simulation
1. Here is an example how to setup network latency 10ms and packet loss 5%:
```
tc qdisc add dev NETWORKID root netem delay 10ms loss 5%
```
2. Remove any latency and packet loss from network
```
tc qdisc del dev NETWORKID root
```
3. To apply latency and packet loss it is necessary to provide NETWORKID to container
```
docker run --net=slownet ... 
```

## Benchmark result

### Control loop computational overhead, 1 connection
![alt text](https://raw.githubusercontent.com/comnetstud/SimpleMetric/master/images/average_latency_one_thread.png "Control loop computational overhead, 1 connection")
***
### Control loop computational overhead, 5 concurrent connections
![alt text](https://raw.githubusercontent.com/comnetstud/SimpleMetric/master/images/average_latency_five_thread.png "Control loop computational overhead, 5 concurrent connections")
***
### ECDF of INSERT successful completion w.r.t. time. InluxDB and Graphite comparison. 1, 5, and 10 concurrent connections.
![alt text](https://raw.githubusercontent.com/comnetstud/SimpleMetric/master/images/influxdb_graphite_comparison_insert.png "ECDF of INSERT successful completion w.r.t. time. InluxDB and Graphite comparison. 1, 5, and 10 concurrent connections.")
***
### ECDF of INSERT and aggregate successful completion w.r.t. time. InluxDB and Graphite comparison. 1, 5, and 10 concurrent connections.
![alt text](https://raw.githubusercontent.com/comnetstud/SimpleMetric/master/images/influxdb_graphite_comparison.png "ECDF of INSERT and aggregate successful completion w.r.t. time. InluxDB and Graphite comparison. 1, 5, and 10 concurrent connections.")
***
### ECDF of INSERT successful completion w.r.t. time and varying network conditions. InluxDB (format: number of concurrent connections j network latency j packet loss rate)
![alt text](https://raw.githubusercontent.com/comnetstud/SimpleMetric/master/images/network_influxdb_comparison.png "ECDF of INSERT successful completion w.r.t. time and varying network conditions. InluxDB (format: number of concurrent connections j network latency j packet loss rate)")
***
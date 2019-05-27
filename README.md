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
3. Build KairosDB docker with `docker build -t kairosdb -f docker/kairosdb/Dockerfile`
4. Run Docker container `docker run -p 5000:5000 kdb q -p 5000`

### [Graphite](https://graphiteapp.org/)
1. Build Graphite docker with `docker build -t graphite -f docker/graphite/Dockerfile`
2. Run Docker container `docker run -p 2003:2003 -p 8000:8000 graphite`

### [TimescaleDB](https://www.timescale.com/)
1. Pull Docker image `docker pull timescale/timescaledb`
2. Run Docker container `docker run -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=benchmarkdb timescale/timescaledb`

### [KairosDB](https://kairosdb.github.io/)
1. Build KairosDB docker with `docker build -t kairosdb -f docker/kairosdb/Dockerfile`
2. Run Docker container `docker run -p 4242:4242 -p 8080:8080 kairosdb`

### [CrateDB](https://crate.io/)
1. Pull Docker image `docker pull crate:latest`
2. Run Docker container `docker run -p 4200:4200 -p 4300:4300 -p 5432:5432 crate:latest -Ccluster.name=democluster -Chttp.cors.enabled=true -Chttp.cors.allow-origin="*"`

## Benchmark result

### Control loop computational overhead, 1 connection
![alt text](https://raw.githubusercontent.com/comnetstud/SimpleMetric/master/images/average_latency_one_thread.png "Control loop computational overhead, 1 connection")
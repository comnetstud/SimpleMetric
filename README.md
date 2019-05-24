# SimpleMetric
Latency benchmark for time series database

## Setup benchmark tool
1. Install python version 3.6
2. Install requirements `pip install -r requirements.txt`
3. Run `data_generator.py` to generate data for benchmark
4. Run `runner.py` to process benchmark

## Setup database 

### InfluxDB
1. Run Docker container `docker run -p 8086:8086 -p 8083:8083 -p 8090:8090 -e INFLUXDB_REPORTING_DISABLED=true -e INFLUXDB_DATA_QUERY_LOG_ENABLED=false -e INFLUXDB_HTTP_LOG_ENABLED=false -e INFLUXDB_CONTINUOUS_QUERIES_LOG_ENABLED=false influxdb:latest`

### CrateDB
1. Run Docker container `docker run -p 4200:4200 -p 4300:4300 -p 5432:5432 crate:latest -Ccluster.name=democluster -Chttp.cors.enabled=true -Chttp.cors.allow-origin="*"`

### Graphite
1. Build Graphite docker with `docker build -t graphite -f docker/graphite/Dockerfile`
2. Run Docker container `docker run -p 2003:2003 -p 8000:8000 graphite`

### KairosDB
1. Build KairosDB docker with `docker build -t kairosdb -f docker/kairosdb/Dockerfile`
2. Run Docker container `docker run -p 4242:4242 -p 8080:8080 kairosdb`

### KDB+
1. Download 'q.zip' from https://kx.com/connect-with-us/download/
2. Copy 'q.zip' to the docker/kdb/ folder
3. Build KairosDB docker with `docker build -t kairosdb -f docker/kairosdb/Dockerfile`
4. Run Docker container `docker run -p 5000:5000 kdb q -p 5000`

### TimescaleDB
Run Docker container `docker run -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=benchmarkdb timescale/timescaledb`


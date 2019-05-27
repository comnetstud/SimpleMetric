import argparse
import asyncio
import os
import sys
import time

import influxdb
from aioinflux import InfluxDBClient
import datetime

ANALYSIS_DIRECTORY = "../analysis/influxdb"
BENCHMARK_TEST = "latency_meter"
QUERY_TYPE_LIST = {
    'count': 'select count(sensor001) from ssdata where time >= START_TIME AND time <= END_TIME',
    'max': 'select max(sensor001) from ssdata where time >= START_TIME AND time <= END_TIME',
    'sum': 'select sum(sensor001) from ssdata where time >= START_TIME AND time <= END_TIME',
    'mean': 'select mean(sensor001) from ssdata where time >= START_TIME AND time <= END_TIME',
    'raw': 'select sensor001 from ssdata where time >= START_TIME AND time <= END_TIME',
}
LATENCY_TYPE = None
PACKETLOSS_TYPE = None


def cleanup_db():
    try:
        client = influxdb.InfluxDBClient('localhost', 8086, 'root', 'root')
        client.drop_database('benchmarkdb')
        client.create_database('benchmarkdb')
    except Exception as e:
        print('Error: {}'.format(e))


def setup_report():
    if not os.path.exists('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST)):
        os.makedirs('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST))


async def run_test(number_of_day, total_number, type_request):
    try:
        end_time = datetime.datetime(2019, 1, 1, 0, 0, 0) + datetime.timedelta(days=number_of_day)
        start_time = end_time - datetime.timedelta(days=1)
        query = QUERY_TYPE_LIST[type_request].replace('START_TIME',
                                                      '{}000000000'.format(int(time.mktime(start_time.timetuple())))).replace(
            'END_TIME', '{}000000000'.format(int(time.mktime(end_time.timetuple()))))
        async with InfluxDBClient(db='benchmarkdb') as client:
            try:
                with open('../data/influx/influx_1sec_{}d.dat'.format(number_of_day), 'rt') as f:
                    network_setup = ''
                    if LATENCY_TYPE or PACKETLOSS_TYPE:
                        network_setup = '_{}_{}'.format(LATENCY_TYPE, PACKETLOSS_TYPE)
                    with open('{}/{}/{}_{}_{}_{}{}.txt'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST, BENCHMARK_TEST, type_request,
                                                               total_number, number_of_day, network_setup),
                              'w') as fw:
                        i = 0
                        for i in range(864):
                            bulk_data = []
                            for j in range(100):
                                l = f.readline()
                                bulk_data.append(l)

                            prev_time = time.time()
                            await client.write(bulk_data)
                            bulk_time = time.time()
                            await client.query(query, db='benchmarkdb')
                            curr_time = time.time()

                            fw.write('{}\t{}\t{}\t{}\n'.format(i, curr_time - prev_time, bulk_time - prev_time,
                                                               bulk_time - curr_time))

            except FileNotFoundError:
                print('You need to generate data first. Please use "data_generator.py" with influx data format.')
    except Exception as e:
        print('Error: {}'.format(e))


def main(argv):
    parser = argparse.ArgumentParser(description='Load data test')
    parser.add_argument('--thread', type=int, help='number of threads. default is 1')
    parser.add_argument('--aggregate', type=str, help='type of aggregate function [max, count, avg, sum]. default is "sum"')
    parser.add_argument('--latency_type', type=str, help='latency type')
    parser.add_argument('--packetloss_type', type=str, help='packet loss type')

    TOTAL_NUMBER = 1
    TYPE_REQUEST = 'sum'

    if len(argv) > 1:
        args = parser.parse_args(argv[1:])

        if args.thread:
            TOTAL_NUMBER = args.thread
        if args.aggregate:
            TYPE_REQUEST = args.aggregate
        if args.latency_type:
            LATENCY_TYPE = args.latency_type
        if args.packetloss_type:
            PACKETLOSS_TYPE = args.packetloss_type

    cleanup_db()
    setup_report()
    several_futures = asyncio.gather(*[run_test(i, TOTAL_NUMBER, TYPE_REQUEST) for i in range(1, TOTAL_NUMBER + 1)])
    asyncio.get_event_loop().run_until_complete(several_futures)


if __name__ == '__main__':
    sys.exit(main(argv=sys.argv))

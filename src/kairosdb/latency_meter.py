import argparse
import asyncio
import datetime
import gzip
import json
import sys
import zlib

import aiohttp
import influxdb
import os

import time

ANALYSIS_DIRECTORY = "../analysis/kairosdb"
BENCHMARK_TEST = "latency_meter"
QUERY_TYPE_LIST = {
    'count': json.dumps({
        "start_absolute": 1546300800000,
        "end_relative": {
            "value": "1",
            "unit": "days"
        },
        "metrics": [
            {
                "name": "sensor001",
                "aggregators": [
                    {
                        "name": "count",
                        "sampling": {
                            "value": 10000,
                            "unit": "minutes"
                        }
                    }
                ]
            }
        ]
    }),
    'max': json.dumps({
        "start_absolute": 1546300800000,
        "end_relative": {
            "value": "1",
            "unit": "days"
        },
        "metrics": [
            {
                "name": "sensor001",
                "aggregators": [
                    {
                        "name": "max",
                        "sampling": {
                            "value": 10000,
                            "unit": "minutes"
                        }
                    }
                ]
            }
        ]
    }),
    'sum': json.dumps({
        "start_absolute": 1546300800000,
        "end_relative": {
            "value": "1",
            "unit": "days"
        },
        "metrics": [
            {
                "name": "sensor001",
                "aggregators": [
                    {
                        "name": "sum",
                        "sampling": {
                            "value": 10000,
                            "unit": "minutes"
                        }
                    }
                ]
            }
        ]
    }),
    'avg': json.dumps({
        "start_absolute": 1546300800000,
        "end_relative": {
            "value": "1",
            "unit": "days"
        },
        "metrics": [
            {
                "name": "sensor001",
                "aggregators": [
                    {
                        "name": "avg",
                        "sampling": {
                            "value": 10000,
                            "unit": "minutes"
                        }
                    }
                ]
            }
        ]
    })
}

LATENCY_TYPE = None
PACKETLOSS_TYPE = None


def setup_report():
    if not os.path.exists('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST)):
        os.makedirs('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST))


async def run_test(number_of_day, total_number, type_request):
    start_time = datetime.datetime(2019, 1, 1, 0, 0, 0) - datetime.timedelta(days=number_of_day - 1)
    query = QUERY_TYPE_LIST[type_request].replace('1546300800000',
                                                  '{}000'.format(
                                                      int(time.mktime(start_time.timetuple()))))
    sensor_list = ['sensor{:03d}'.format(i) for i in range(1, 11)]

    async with aiohttp.ClientSession() as session:
        try:
            with open('../data/csv/csv_1sec_{}d.dat'.format(number_of_day), 'rt') as f:
                f.readline()
                network_setup = ''
                if LATENCY_TYPE or PACKETLOSS_TYPE:
                    network_setup = '_{}_{}'.format(LATENCY_TYPE, PACKETLOSS_TYPE)
                with open('{}/{}/{}_{}_{}_{}{}.txt'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST, BENCHMARK_TEST, type_request,
                                                           total_number, number_of_day, network_setup),
                          'w') as fw:
                    i = 0
                    for i in range(864):
                        bulk_data = {}
                        for sensor in sensor_list:
                            bulk_data[sensor] = []
                        for j in range(100):
                            l = f.readline()
                            d = l.strip().split(';')
                            cnt = 0
                            for sensor in sensor_list:
                                cnt += 1
                                bulk_data[sensor].append([int(d[0]) * 1000, float(d[cnt])])
                        data = []
                        for sensor in sensor_list:
                            data.append(
                                {
                                    "name": sensor,
                                    "datapoints": bulk_data[sensor],
                                    "tags": {
                                        "project": "benchmarkdb"
                                    }
                                }
                            )
                        gzipped = gzip.compress(bytes(json.dumps(data), 'UTF-8'))
                        headers = {'content-type': 'application/gzip'}

                        prev_time = time.time()

                        b = await session.post('http://localhost:8080/api/v1/datapoints', data=gzipped, headers=headers)

                        bulk_time = time.time()

                        a = await session.post('http://localhost:8080/api/v1/datapoints/query', data=query)

                        curr_time = time.time()

                        fw.write('{}\t{}\t{}\t{}\n'.format(i, curr_time - prev_time, bulk_time - prev_time,
                                                           bulk_time - curr_time))
        except FileNotFoundError:
            print('You need to generate data first. Please use "data_generator.py" with csv data format.')


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

    setup_report()
    several_futures = asyncio.gather(*[run_test(i, TOTAL_NUMBER, TYPE_REQUEST) for i in range(1, TOTAL_NUMBER + 1)])
    asyncio.get_event_loop().run_until_complete(several_futures)


if __name__ == '__main__':
    sys.exit(main(argv=sys.argv))

import argparse
import asyncio
import datetime
from datetime import timedelta
import os
import sys
import time

import aiohttp
import graphitesend

ANALYSIS_DIRECTORY = "../analysis/graphite"
BENCHMARK_TEST = "latency_meter"
QUERY_TYPE_LIST = {
    'max': "http://localhost:8000/render?target=summarize(systems.il-test.sensor001,'1year','max')&from=START_DATE&until=END_DATE&format=json",
    'sum': "http://localhost:8000/render?target=summarize(systems.il-test.sensor001,'1year','sum')&from=START_DATE&until=END_DATE&format=json",
    'avg': "http://localhost:8000/render?target=summarize(systems.il-test.sensor001,'1year','avg')&from=START_DATE&until=END_DATE&format=json",
}
LATENCY_TYPE = None
PACKETLOSS_TYPE = None
START_DATE = datetime.datetime(2019, 1, 1, 0, 0, 0)


def setup_report():
    if not os.path.exists('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST)):
        os.makedirs('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST))


async def run_test(number_of_day, total_number, type_request):
    try:
        end_date = START_DATE + timedelta(days=number_of_day)
        start_date = end_date - timedelta(days=1)
        request_query = QUERY_TYPE_LIST[type_request].replace('START_DATE', start_date.strftime('%Y%m%d')).replace(
            'END_DATE', end_date.strftime('%Y%m%d'))
        graphitesend.init(graphite_server='localhost')
        async with aiohttp.ClientSession() as session:
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
                        bulk_data = []
                        for j in range(100):
                            l = f.readline()
                            d = list(map(float, l.strip().split(';')))
                            for ii in range(1, 11):
                                bulk_data.append(('sensor{:03d}'.format(ii), float(d[ii]), int(d[0]),))

                        prev_time = time.time()
                        graphitesend.send_list(bulk_data)
                        bulk_time = time.time()
                        resp = await session.get(request_query)
                        curr_time = time.time()

                        fw.write('{}\t{}\t{}\t{}\n'.format(i, curr_time - prev_time, bulk_time - prev_time,
                                                           bulk_time - curr_time))
    except Exception as e:
        print('Error: {}'.format(e))


def main(argv):
    parser = argparse.ArgumentParser(description='Load data test')
    parser.add_argument('--thread', type=int, help='number of threads. default is 1')
    parser.add_argument('--aggregate', type=str, help='type of aggregate function [max, avg, sum]. default is "sum"')
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
            if args.aggregate == 'count':
                print('Graphite benchmark does not support "count" aggregate function.')
                sys.exit(0)
        if args.latency_type:
            LATENCY_TYPE = args.latency_type
        if args.packetloss_type:
            PACKETLOSS_TYPE = args.packetloss_type

    setup_report()
    several_futures = asyncio.gather(*[run_test(i, TOTAL_NUMBER, TYPE_REQUEST) for i in range(1, TOTAL_NUMBER + 1)])
    asyncio.get_event_loop().run_until_complete(several_futures)


if __name__ == '__main__':
    sys.exit(main(argv=sys.argv))

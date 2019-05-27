import argparse
import asyncio
import os
import sys
import traceback
import time
from datetime import datetime

from crate import client

ANALYSIS_DIRECTORY = "../analysis/cratedb"
BENCHMARK_TEST = "latency_meter"
QUERY_TYPE_LIST = {
    'count': 'select count(*) from benchmarkdb.ssdata',
    'max': 'select max(sensor001) from benchmarkdb.ssdata',
    'sum': 'select sum(sensor001) from benchmarkdb.ssdata',
    'avg': 'select avg(sensor001) from benchmarkdb.ssdata',
}
LATENCY_TYPE = None
PACKETLOSS_TYPE = None


def cleanup_db():
    try:
        connection = client.connect('http://localhost:4200/', username='crate')
        cursor = connection.cursor()
        s = ['sensor{:03d} DOUBLE '.format(i) for i in range(1, 11)]
        cursor.execute('CREATE TABLE IF NOT EXISTS benchmarkdb.ssdata (time timestamp, {});'.format(','.join(s)))
    except Exception as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()

def setup_report():
    if not os.path.exists('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST)):
        os.makedirs('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST))


async def run_test(number_of_day, total_number, type_request):
    try:
        conn = client.connect('http://localhost:4200/', username='crate')
        cursor = conn.cursor()
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
                        bulk_data = []
                        for j in range(100):
                            l = f.readline()
                            d = list(map(float, l.strip().split(';')))
                            d[0] = datetime.fromtimestamp(d[0])
                            bulk_data.append(d)

                        prev_time = time.time()

                        cursor.executemany('''INSERT INTO benchmarkdb.ssdata VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);''',
                                               bulk_data)
                        bulk_time = time.time()
                        cursor.execute(QUERY_TYPE_LIST[type_request])
                        cursor.fetchall()
                        curr_time = time.time()

                        fw.write('{}\t{}\t{}\t{}\n'.format(i, curr_time - prev_time, bulk_time - prev_time,
                                                           bulk_time - curr_time))
        except FileNotFoundError:
            print('You need to generate data first. Please use "data_generator.py" with csv data format.')
        conn.close()
    except Exception as ex:
        print('Error: {}'.format(ex))
        traceback.print_exc(limit=1, file=sys.stdout)

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

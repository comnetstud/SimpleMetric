import argparse
import asyncio
import os
import sys
import time
from datetime import datetime, timedelta

import asyncpg
import psycopg2

ANALYSIS_DIRECTORY = "../analysis/timescaledb"
BENCHMARK_TEST = "bulk_load_and_retrieve"
QUERY_TYPE_LIST = {
    'count': 'select count(*) from ssdata WHERE time > \'START_DATE\' AND time < \'END_DATE\'',
    'max': 'select max(sensor001) from ssdata WHERE time > \'START_DATE\' AND time < \'END_DATE\'',
    'sum': 'select sum(sensor001) from ssdata WHERE time > \'START_DATE\' AND time < \'END_DATE\'',
    'avg': 'select AVG(sensor001) from ssdata WHERE time > \'START_DATE\' AND time < \'END_DATE\'',
}
LATENCY_TYPE = None
PACKETLOSS_TYPE = None


def cleanup_db():
    connection = None
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="postgres",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="benchmarkdb")
        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS ssdata')

        s = ['sensor{:03d} DOUBLE PRECISION NULL'.format(i) for i in range(1, 11)]
        # print('CREATE TABLE IF NOT EXISTS ssdata (time TIMESTAMPTZ NOT NULL, {});'.format(','.join(s)))
        cursor.execute('CREATE TABLE IF NOT EXISTS ssdata (time TIMESTAMPTZ NOT NULL, {});'.format(','.join(s)))
        cursor.execute("SELECT create_hypertable('ssdata', 'time');")
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    # client = influxdb.InfluxDBClient('localhost', 8086, 'root', 'root')
    # client.drop_database('benchmarkdb')
    # client.create_database('benchmarkdb')
    # print('DROP TABLE IF EXISTS ssdata')
    # print('CREATE TABLE IF NOT EXISTS ssdata (time TIMESTAMPTZ NOT NULL, {});'.format(','.join(s)))


def setup_report():
    if not os.path.exists('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST)):
        os.makedirs('{}/{}'.format(ANALYSIS_DIRECTORY, BENCHMARK_TEST))


async def run_test(number_of_day, total_number, type_request):
    try:
        conn = await asyncpg.connect(user='postgres', password='postgres', database='benchmarkdb', host='127.0.0.1',
                                     port='5432')

        # await conn.execute('DROP TABLE IF EXISTS ssdata')
        #
        # s = ['sensor{:03d} DOUBLE PRECISION NULL'.format(i) for i in range(1, 11)]
        # await conn.execute('CREATE TABLE IF NOT EXISTS ssdata (time TIMESTAMPTZ NOT NULL, {});'.format(','.join(s)))
        end_date = datetime(2019, 1, 1, 0, 0, 0, 0) + timedelta(days=number_of_day)
        start_date = end_date - timedelta(days=1)

        query = QUERY_TYPE_LIST[type_request].replace('START_DATE', start_date.strftime('%Y-%m-%d')).replace(
            'END_DATE', end_date.strftime('%Y-%m-%d'))
        try:
            with open('../../data/csv/csv_1sec_{}d.dat'.format(number_of_day), 'rt') as f:
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
                            # print(d)
                            bulk_data.append(d)
                            # bulk_data.append('{}{}'.format(l[0:3], l[l.index(' '):]))

                        prev_time = time.time()

                        await conn.executemany('''INSERT INTO ssdata VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);''',
                                               bulk_data)
                        bulk_time = time.time()
                        await conn.fetch(query)
                        curr_time = time.time()

                        fw.write('{}\t{}\t{}\t{}\n'.format(i, curr_time - prev_time, bulk_time - prev_time,
                                                           bulk_time - curr_time))
        except FileNotFoundError:
            print('You need to generate data first. Please use "data_generator.py" with csv data format.')

        await conn.close()
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

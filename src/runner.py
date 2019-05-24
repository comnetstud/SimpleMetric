import argparse
import asyncio
import os
import sys
import time
from datetime import datetime

ANALYSIS_DIRECTORY = '../analysis'
BENCHMARK_TEST = 'latency_meter'

def setup_analysis(database):
    if not os.path.exists('{}/{}/{}'.format(ANALYSIS_DIRECTORY, database, BENCHMARK_TEST)):
        os.makedirs('{}/{}/{}'.format(ANALYSIS_DIRECTORY, database, BENCHMARK_TEST))



def main(argv):
    parser = argparse.ArgumentParser(description='Load data test')
    parser.add_argument('--thread', type=int, help='number of connections. default is 1')
    parser.add_argument('--aggregate', type=str, help='type of aggregate function [max, count, avg, sum]. default is "sum"')
    parser.add_argument('--latency', type=float, help='latency in ms.')
    parser.add_argument('--packetloss', type=float, help='packet loss type in percentage')
    parser.add_argument('--database', type=str, help='database type [cratedb, graphite, influxdb, kairosdb, kdb, timescaledb]', required=True)

    THREADS = 1
    AGGREGATE = 'sum'
    PACKETLOSS = None
    LATENCY = None
    DATABASE = None

    if len(argv)  == 1:
        parser.print_help()
        sys.exit(0)

    if len(argv) > 1:
        args = parser.parse_args(argv[1:])

        if not args.database:
            parser.print_help()
            sys.exit(1)

        if args.database:
            DATABASE = args.database
        if args.thread:
            THREADS = args.thread
        if args.aggregate:
            AGGREGATE = args.aggregate
        if args.latency:
            LATENCY = args.latency
        if args.packetloss:
            packetloss = args.packetloss
    
    os.system('python {database}/latency_meter.py --thread {thread} --aggregate "{aggregate}" --latency {latency} --packetloss {packetloss}'.format(database=DATABASE, thread=THREADS, aggregate=AGGREGATE, latency=LATENCY, packetloss=PACKETLOSS))
if __name__ == '__main__':
    sys.exit(main(argv=sys.argv))

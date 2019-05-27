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
    parser.add_argument('--latency', type=str, help='latency in ms.')
    parser.add_argument('--packetloss', type=str, help='packet loss type in percentage')
    parser.add_argument('--database', type=str, help='database type')

    THREAD = 1
    AGGREGATE = 'sum'
    PACKETLOSS = None
    LATENCY = None

    if len(argv) > 1:
        args = parser.parse_args(argv[1:])

        if args.thread:
            THREAD = args.thread
        if args.aggregate:
            aggregate = args.aggregate
        if args.latency:
            LATENCY = args.latency
        if args.packetloss:
            PACKETLOSS = args.packetloss
    
    setup_analysis('kdb')
    if not LATENCY:
	    os.system('java -jar kdb/kdb.jar -t {thread} -r "{aggregate}" -l "{latency}" -p "{packetloss}"'.format(
	                    thread=THREAD, aggregate=AGGREGATE,packetloss=PACKETLOSS,
	                    latency=LATENCY))
    else:
	    os.system('java -jar kdb/kdb.jar -t {thread} -r "{aggregate}"'.format(
	                    thread=THREAD, aggregate=AGGREGATE))
if __name__ == '__main__':
    sys.exit(main(argv=sys.argv))

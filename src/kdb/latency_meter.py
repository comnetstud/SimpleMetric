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
    parser.add_argument('--database', type=str, help='database type')

    TOTAL_NUMBER = 1
    TYPE_REQUEST = 'sum'

    if len(argv) > 1:
        args = parser.parse_args(argv[1:])

        if args.thread:
            TOTAL_NUMBER = args.thread
        if args.type_request:
            TYPE_REQUEST = args.type_request
        if args.latency_type:
            LATENCY_TYPE = args.latency_type
        if args.packetloss_type:
            PACKETLOSS_TYPE = args.packetloss_type
    
    os.system('java -jar kdb_network.jar -t {thread} -r "{aggregate}" -l "{latency}" -p "{packetloss}"'.format(
                    thread=thread, aggregate=aggregate,packetloss=packetloss,
                    latency=latency))

if __name__ == '__main__':
    sys.exit(main(argv=sys.argv))

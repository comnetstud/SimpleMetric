import argparse
import sys
from datetime import datetime, timedelta
import time
import numpy as np

SENSOR_TEMPLATE = 'sensor'
TABLE = 'ssdata'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
KDB_DATETIME_FORMAT = '%Y.%m.%dD%H:%M:%SZ'


def generate_data(out_file, frequency, start_time, end_time, sensor_number, format):
    sensor_names = ['{}{:03d}'.format(SENSOR_TEMPLATE, i + 1) for i in range(sensor_number)]

    with open(out_file, 'wt') as f:
        cur_time = start_time
        while True:
            if end_time <= cur_time:
                break
            measure_time = int(time.mktime(cur_time.timetuple()))
            sensor_values = np.round(np.random.uniform(low=-100.0, high=100.0, size=sensor_number), 2)
            d = ''
            if format == 'influx':
                values = ['{}={}'.format(s, v) for s, v in zip(sensor_names, sensor_values)]
                d = '{} {} {}\n'.format(TABLE, ','.join(values), measure_time * 1000000000)
            elif format == 'csv':
                if cur_time == start_time:
                    f.write(';'.join(sensor_names))
                    f.write('\n')
                sensor_values = ['{}'.format(v) for v in sensor_values]
                d = '{};{}\n'.format(measure_time, ';'.join(sensor_values))
            elif format == 'kdb':
                sensor_values = ['{}'.format(v) for v in sensor_values]
                d = '`ssdata insert(`{};{})\n'.format(cur_time.strftime(KDB_DATETIME_FORMAT), ';'.join(sensor_values))
            f.write(d)
            cur_time = cur_time + timedelta(seconds=frequency)


def main(argv):
    parser = argparse.ArgumentParser(description='Generate values')
    parser.add_argument('--out_file', type=str, help='Output file', required=True)
    parser.add_argument('--frequency', type=float, help='Frequency in seconds (default: 1 sec)')
    parser.add_argument('--start_time', type=str,
                        help='Beginning timestamp (RFC3339). (default "2019-01-01T00:00:00Z")')
    parser.add_argument('--end_time', type=str, help='Ending timestamp (RFC3339). (default "2019-01-02T00:00:00Z")')
    parser.add_argument('--sensor_number', type=int, help='Number of sensors (default: 10)')
    parser.add_argument('--format', type=str,
                        help='Please select output format ["influx", "csv", "json"] (default: "influx")')

    out_file = 'output.out'
    frequency = 1
    start_time = '2019-01-01T00:00:00Z'
    end_time = '2019-01-01T10:00:00Z'
    sensor_number = 10
    format = 'influx'

    if len(argv) <= 1:
        parser.print_help()
        return 0

    if len(argv) > 1:
        args = parser.parse_args(argv[1:])

        if args.out_file:
            out_file = args.out_file

        if args.frequency:
            frequency = args.frequency

        if args.start_time:
            start_time = args.start_time

        if args.end_time:
            end_time = args.end_time

        if args.sensor_number:
            sensor_number = args.sensor_number

        if args.sensor_number:
            sensor_number = args.sensor_number

        if args.format:
            format = args.format

    try:
        start_time = datetime.strptime(start_time, DATETIME_FORMAT)
        end_time = datetime.strptime(end_time, DATETIME_FORMAT)
        generate_data(out_file=out_file, frequency=frequency, start_time=start_time, end_time=end_time,
                      sensor_number=sensor_number, format=format)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    sys.exit(main(argv=sys.argv))

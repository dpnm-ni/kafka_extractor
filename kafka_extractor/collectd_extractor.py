# -*- coding: utf-8 -*-
import argparse
import sys
import json
import pdb
import traceback, logging

import collectd_metrics

from config import cfg
from confluent_kafka import Producer, Consumer, KafkaError, TopicPartition
from influxdb import InfluxDBClient

format_str = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=format_str)
logger = logging.getLogger(__name__)

collectd_cfg = cfg['collectd']
influxdb_cfg = cfg['influxdb']

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logger.error('Message delivery failed: {}'.format(err))

def extract(message):
    data = message.value().decode('utf-8')
    data = json.loads(message.value())
    data = data[0]
    return collectd_metrics.get_measurements(data)

def main():
    # kafka
    consumer = Consumer(collectd_cfg['consumer'])
    consumer.subscribe([collectd_cfg['raw_data_topic']])
    producer = Producer(collectd_cfg['producer'])
    # Trigger any available delivery report callbacks from previous produce() calls
    # see: https://github.com/confluentinc/confluent-kafka-python/issues/16
    producer.poll(0)

    # influxdb
    influxdb_client = InfluxDBClient(host=influxdb_cfg['server'],
                                    database=influxdb_cfg['database'])
    influxdb_client.create_database(influxdb_cfg['database'])
    influxdb_client.create_retention_policy(name="infinite",
            duration='INF',
            replication=1,
            database=influxdb_cfg['database'],
            default=True
        )

    logger.info("Start processing collectd data ...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error("Consumer error: {}".format(msg.error()))
                continue

            measurements = extract(msg)

            # Send extracted data to kafka topics
            # Asynchronously produce a message, the delivery report callback
            # will be triggered from poll() above, or flush() below, when the message has
            # been successfully delivered or failed permanently.
            for item in measurements:
                producer.produce(topic='collectd',
                        value=str({item[0]: item[1]}),
                        timestamp=item[2],
                        callback=delivery_report)
                producer.poll(0)

            # Send extracted data to influxdb
            data_points = []
            for item in measurements:
                data_points.append({"measurement": item[0],
                                    # timestamp from ms in collectd to ns in influxdb
                                    "time": int(item[2]) * 10**6,
                                    "fields": {
                                        "value": item[1],
                                    }
                                })
            influxdb_client.write_points(data_points)


    except KeyboardInterrupt:
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        producer.flush()
        consumer.close()

if __name__ == '__main__':
    main()

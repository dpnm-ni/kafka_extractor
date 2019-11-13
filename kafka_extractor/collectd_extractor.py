# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import sys
import json
import pdb

import collectd_metrics

from config import cfg
from confluent_kafka import Producer, Consumer, KafkaError, TopicPartition

collectd_cfg = cfg['collectd']

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))

def extract(message):
    data = message.value().decode('utf-8')
    data = json.loads(message.value())
    data = data[0]
    return collectd_metrics.data_to_toppic(data)

def main():
    consumer = Consumer(collectd_cfg['consumer'])
    consumer.subscribe(['collectd'])

    producer = Producer(collectd_cfg['producer'])
    # Trigger any available delivery report callbacks from previous produce() calls
    # see: https://github.com/confluentinc/confluent-kafka-python/issues/16
    producer.poll(0)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue

            topic_value_list = extract(msg)
            # Asynchronously produce a message, the delivery report callback
            # will be triggered from poll() above, or flush() below, when the message has
            # been successfully delivered or failed permanently.
            for item in topic_value_list:
                producer.produce(topic=item[0],
                        value=str(item[1]),
                        timestamp=item[2],
                        callback=delivery_report)
                producer.poll(0)

    except KeyboardInterrupt:
        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.
        producer.flush()
        consumer.close()

if __name__ == '__main__':
    main()

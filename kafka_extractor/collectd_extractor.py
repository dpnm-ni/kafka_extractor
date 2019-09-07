# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import sys
import json
import pdb

from config import cfg
from confluent_kafka import Producer, Consumer, KafkaError, TopicPartition

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))

def is_active_mesurement(data):
    if (cfg['collectd']['mesurement_filters_enable'] == False):
        return True
    s = "%s___%s___%s" %(
        data['plugin'],
        data['type'],
        data['type_instance'],
        )
    if (s in cfg['collectd']['mesurement_filters']):
        return True
    return False

def extract(message):
    data = message.value().decode('utf-8')
    data = json.loads(message.value())
    data = data[0]
    result = []

    if not is_active_mesurement(data):
        return result

    for i in range(0, len(data['values'])):
        topic = "%s___%s___%s___%s___%s___%s___%s" %(
            data['host'],
            data['plugin'],
            data['plugin_instance'],
            data['type'],
            data['type_instance'],
            data['dsnames'][i],
            data['dstypes'][i],
            )
        result.append((topic, data['values'][i], data['time']))
    return result

def main():
    consumer = Consumer(cfg['collectd']['consumer'])
    consumer.subscribe(['collectd'])

    producer = Producer(cfg['collectd']['producer'])
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

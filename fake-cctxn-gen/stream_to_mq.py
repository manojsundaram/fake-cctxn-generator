#!/usr/bin/env python3
import random
import sys
import pika

def publish_mq(msg):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='prod')
    channel.basic_publish(exchange='',
                      routing_key='prod',
                      body=msg)
    connection.close()

if __name__ == '__main__':
    filename = sys.argv[1]
    f = open(filename,'r')
    lines = f.read().splitlines()
    while len(lines) > 0 :
        random_item_from_list = random.choice(lines)
        publish_mq(random_item_from_list)
        lines.remove(random_item_from_list)

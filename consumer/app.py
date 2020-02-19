'''Program to consume messages from kafka and send that to elasticsearch.'''
import json

from confluent_kafka import Consumer, KafkaError
from elasticsearch import Elasticsearch

c = Consumer({
    'bootstrap.servers': '192.168.56.107:9092',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['user_log'])


def main():

    while True:
        msg = c.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        value = msg.value().decode('utf-8')
        print('Received message: {}'.format(value))

        data = json.loads(value)
        # print(data['user_id'])

        es = Elasticsearch()

        res = es.index(index="user_log", body=data)

        # print(res['result'])

        # break

    c.close()


if __name__ == "__main__":
    main()

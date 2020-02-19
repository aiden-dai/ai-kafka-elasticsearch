'''Use Pandas to process the csv file and send the records to a kafka topic.'''
import time
import json
import pandas as pd

from confluent_kafka import Producer


def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    # else:
    #     print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def main():
    data = pd.read_csv('data/sample.csv', sep=',')
    #data = pd.read_csv('data/tianchi_mobile_recommend_train_user.csv', sep=',')

    #data = data.sort_values(by='time', ascending=True)
    print(data.head(5))

    print(data.shape)
    print(data.columns)

    p = Producer({'bootstrap.servers': '192.168.56.107:9092'})

    for i, row in data.iterrows():
        data = {
            'user_id': row.user_id,
            'item_id': row.item_id,
            'behavior_type': row.behavior_type,
            'item_category': row.item_category,
            'date': '2019-{}'.format(row.time[5:10]),
            'hour': int(row.time[-2:])
        }

        p.poll(0)

        # Asynchronously produce a message, the delivery report callback
        p.produce('user_log', json.dumps(data).encode(
            'utf-8'), callback=delivery_report)

        # time.sleep(0.1)

        if (i + 1) % 100 == 0:
            print('Totally {} records has been sent'.format(i + 1))

    p.flush()


if __name__ == "__main__":
    main()

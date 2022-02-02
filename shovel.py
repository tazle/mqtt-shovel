import asyncio
from amqtt.client import MQTTClient, QOS_0
import time
import sys

MQTT_RECEIVE_TIMEOUT = 30

async def connect(url):
    client = MQTTClient()
    try:
        await client.connect(url)
        print("Connected", url)
    except Exception as e:
        print("Connection failed for %s: %s" % (url, e))
        asyncio.get_running_loop().stop()
    return client

last_receive_timestamp = time.time()
async def main(from_url, from_topic, to_url, to_topic):
    global last_receive_timestamp

    print("Connecting source", from_url)
    from_client = await connect(from_url)
    print("Connecting destination", to_url)
    to_client = await connect(to_url)

    await from_client.subscribe([
        (from_topic, QOS_0),
        ])
    print("Subscribed source")

    counter = 0
    while True:
        message = await from_client.deliver_message()
        await to_client.publish(to_topic, message.data)
        counter += 1
        if counter and counter % 100 == 0:
            print("Delivered", counter, "messages")
        last_receive_timestamp = time.time()

async def watchdog():
    print("Starting watchdog")
    while True:
        now = time.time()
        since_last_receive = (now - last_receive_timestamp)

        if since_last_receive > MQTT_RECEIVE_TIMEOUT:
            print("No new BLE data received in %d seconds, exiting" %MQTT_RECEIVE_TIMEOUT)
            sys.exit(1)

        await asyncio.sleep(1)

def init():
    from_url, from_topic, to_url, to_topic = sys.argv[1:]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.ensure_future(watchdog(), loop=loop)
    asyncio.ensure_future(main(from_url, from_topic, to_url, to_topic), loop=loop)
    loop.run_forever()

if __name__ == '__main__':
    init()


# Shovel messages from one MQTT topic to another

```
docker build . -t mqtt-shovel && docker run --rm -it mqtt-shovel mqtt://localhost /example/source mqtt://anotherhost /example/target 
```

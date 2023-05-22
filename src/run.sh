#!/bin/bash

MQTT_CONFIG="${MQTT_PASS}@${MQTT_HOST}"

echo "Starting with options: COMMANDS="$COMMANDS" DEVICE_PATH=$DEVICE_PATH POLLING_INTERVAL=$POLLING_INTERVAL MQTT_CLIENT_ID=$MQTT_CLIENT_ID MQTT_TOPIC=$MQTT_TOPIC MQTT_TOPIC_SUB=$MQTT_TOPIC_SUB VERBOSE=$VERBOSE"

python3 -u \
	/app/main.py \
	"$COMMANDS" \
	-d "$DEVICE_PATH" \
	-p "$POLLING_INTERVAL" \
	-m "$MQTT_CONFIG" \
	-c "$MQTT_CLIENT_ID" \
	-t "$MQTT_TOPIC" \
	-s "$MQTT_TOPIC_SUB" \
	-v "$VERBOSE"

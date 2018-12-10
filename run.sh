#!/bin/bash

[ ! -z "$SLEEP" ] || SLEEP=600

while :
do
	echo "Running AudioSync..."
	python main.py
	echo "Sleeping for $SLEEP seconds..."
	sleep $SLEEP
done
#!/bin/bash
sudo rm -rf /opt/ustreamer-launcher/launch
sudo cp ./launch  /opt/ustreamer-launcher/

sudo rm -rf /opt/tinypilot/app/
sudo cp -r ./app /opt/tinypilot/app
sudo chown -R tinypilot:tinypilot /opt/tinypilot/app

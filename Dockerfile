FROM python:3.10-slim
# FROM python:3.10-alpine

########################################
# add a user so we're not running as root
########################################
# ubuntu mode
RUN useradd mqtt
RUN apt-get update && apt-get -y install dumb-init && apt-get clean

# alpine mode
# RUN apk add --no-cache curl
# RUN addgroup -S appgroup && adduser -S mqtt -G appgroup

RUN mkdir -p /home/mqtt/.config/
RUN chown mqtt /home/mqtt -R

# RUN mkdir -p build/mqtt

WORKDIR /app

COPY mqtt_monitor mqtt_monitor
COPY pyproject.toml .

# RUN python -m pip install poetry

RUN chown mqtt /app -R
WORKDIR /app/
USER mqtt

RUN python -m pip install --upgrade --no-warn-script-location pip
RUN python -m pip install --no-warn-script-location /app

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD python -m mqtt_monitor --config-file /app/mqtt-monitor.json

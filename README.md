# Telegram business bot
 Bot for tracking actual currencies rates.

 Allow subscribable notifications with current currency <b>rate</b> at time <i>you</i> set.
 
## Install

Clone from github:

```sh
git clone https://github.com/sh-ram/bizbot.git && cd bizbot
```

## Build


To build project, you need to install 
<b>[docker](https://docs.docker.com/engine/install/)</b> and 
<b>[docker-compose](https://docs.docker.com/compose/install/)</b> api.

If you already have, use to build:

```sh
docker-compose up -d
```

### Using docker containers

To connect working docker container with <b>telegram bot</b> use:

```sh
docker exec -it bizbot bash
```
And to <b>selenium</b> docker container:

```sh
docker exec -it selenium bash
```

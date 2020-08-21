# Telegram business bot
 Bot for tracking actual currencies rates.

 Allow subscribable notifications with current currency <b>rate</b> at time <i>you</i> set.
 
## Install

Clone from github:

```sh
git clone https://github.com/sh-ram/bizbot && cd bizbot
```

## Build


To build project, you need to install <b>docker</b> and <b>docker-compose</b> api, [here](https://docs.docker.com/engine/install/) official samples.

If you already have use to build:

```sh
docker-compose up -d
```

### Using docker containers

To connect working docker container with <b>telegram bot</b> use:

```sh
docker exec -it bizbot bash
```
And to connect <b>selenium</b> docker container:

```sh
docker exec -it selenium bash
```

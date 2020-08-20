FROM python:3.8

ENV TELEGRAM_BOT_TOKEN=''
ENV HOST=''
ENV CHROME_COMMAND_EXECUTOR='http://'${HOST}':4444/wd/hub'

RUN pip install -U pip selenium python-telegram-bot && \
    apt-get update && apt-get install sqlite3 

RUN groupadd automation \
        --gid 1301 \
    && useradd automation \
        --create-home \
        --gid 1301 \
        --shell /bin/bash \
        --uid 1300 \
    && usermod -a -G sudo automation \
    && echo  'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers \
    && echo 'automation:secret' | chpasswd

ENV HOME=/home/automation

WORKDIR ${HOME}
COPY *.py ./
COPY createdb.sql ./
RUN sqlite3 currency.db < createdb.sql && \
    chown -R automation:automation ${HOME}

USER 1300

ENTRYPOINT [ "python3", "server.py" ]

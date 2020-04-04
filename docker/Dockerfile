
FROM python:3.6
USER root

ENV TZ=Asia/Taipei
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=zh_TW.UTF-8

RUN apt-get update \
    && apt-get install -y --fix-missing python3-dev python3-setuptools \
    python3-pip cron sudo locales tzdata \
    && locale-gen zh_TW.UTF-8 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && echo "zh_TW BIG5" > /etc/locale.gen \
    && echo "zh_TW.UTF-8 UTF-8" > /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/*

RUN groupadd notify -g 1000 ;\
    useradd notify -m --uid 1000 --gid 1000 -d /home/notify -s /bin/bash

COPY entrypoint.sh /entrypoint.sh
COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt ;\
    pip3 install --no-cache-dir yfinance==0.1.44 ;\
    rm -rfv /root/.cache /tmp/requirements.txt ;\
    chmod a+x /entrypoint.sh

RUN rm -rfv /root/.cache /home/stock/.cache /tmp/docker > /dev/null 2>&1




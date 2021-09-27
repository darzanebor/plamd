FROM alphaceti/default-python:0.1.3 as base
ENV PROMETHEUS_MULTIPROC_DIR="/usr/src/app/prometheus" \
    PATH="${PATH}:/home/plamd/.local/bin"
ADD app /usr/src/app
RUN addgroup -S plamd && \
    adduser -h /home/plamd -S plamd -G plamd && \
    chmod +x /usr/src/app/* && \
    chown -R plamd:plamd /usr/src/app && \
    apk add --update --no-cache
EXPOSE 5000/tcp
USER plamd
WORKDIR /usr/src/app
RUN pip3 install -r ./requirements.txt
ENTRYPOINT [ "./entry.sh" ]

FROM java:8-alpine

RUN apk upgrade libssl1.0 --update-cache && \
    apk add wget ca-certificates bash
RUN wget -O /tmp/kairosdb-1.2.2-1.tar.gz \
    https://github.com/kairosdb/kairosdb/releases/download/v1.2.2/kairosdb-1.2.2-1.tar.gz

RUN mkdir -p /opt/ && \
    cd /opt/ && \
    tar -xvf /tmp/kairosdb*

#COPY conf/kairosdb.properties /opt/kairosdb/conf/kairosdb.properties

EXPOSE 4242 8080 2003 2004
ENTRYPOINT [ "/opt/kairosdb/bin/kairosdb.sh"]
CMD [ "run" ]
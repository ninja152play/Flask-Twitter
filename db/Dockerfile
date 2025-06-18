FROM postgres:13

COPY postgresql.conf /etc/postgresql/postgresql.conf

RUN chown postgres:postgres /etc/postgresql/postgresql.conf && \
    chmod 644 /etc/postgresql/postgresql.conf

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
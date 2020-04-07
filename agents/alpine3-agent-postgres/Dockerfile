FROM postgres:12-alpine AS agent-postgres

RUN mkdir -p \
    /var/lib/postgresql; \
  chown -R \
    postgres:postgres \
    /var/lib/postgresql

VOLUME /var/lib/postgresql

#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER bus WITH PASSWORD 'map' ;
    CREATE DATABASE busmap TEMPLATE=template_postgis;
    GRANT ALL PRIVILEGES ON DATABASE busmap TO bus;
EOSQL
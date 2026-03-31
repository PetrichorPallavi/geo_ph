#!/bin/sh

echo "🚀 Starting OSM update..."

osm2pgsql-replication update \
  -d tokyo_osm \
  -H postgis \
  -U postgres

echo "📊 Refreshing business table..."

docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < /sql/refresh_business_table.sql

echo "✅ Done."
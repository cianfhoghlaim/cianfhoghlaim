curl -u cairo_user:cairo_secure_123  -X POST "http://34.59.164.124:9200/historical-documents/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {"match_all": {}},
    "size": 1,
    "_source": true
  }'
#!/bin/bash
# scripts/elasticsearch-startup.sh
# Terraform template file for Elasticsearch installation

set -e

# Logging
exec > >(tee /var/log/elasticsearch-setup.log) 2>&1
echo "Starting Elasticsearch installation at $(date)"

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y openjdk-11-jdk curl wget gnupg2

# Add Elasticsearch repository
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" > /etc/apt/sources.list.d/elastic-8.x.list

# Install Elasticsearch and Kibana
apt update
apt install -y elasticsearch kibana

# Configure Elasticsearch
cat > /etc/elasticsearch/elasticsearch.yml <<EOF
# Basic configuration
cluster.name: ${project_name}-${environment}
node.name: \$${HOSTNAME}
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch

# Network settings
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node

# Security settings (disabled for development)
xpack.security.enabled: false
xpack.security.enrollment.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false

# Memory settings
bootstrap.memory_lock: true

# CORS settings for development
http.cors.enabled: true
http.cors.allow-origin: "*"
http.cors.allow-methods: OPTIONS, HEAD, GET, POST, PUT, DELETE
http.cors.allow-headers: X-Requested-With,X-Auth-Token,Content-Type,Content-Length,Authorization
EOF

# Set JVM heap size
cat > /etc/elasticsearch/jvm.options.d/heap.options <<EOF
-Xms${heap_size}
-Xmx${heap_size}
EOF

# Configure memory limits
echo "elasticsearch soft memlock unlimited" >> /etc/security/limits.conf
echo "elasticsearch hard memlock unlimited" >> /etc/security/limits.conf

# Configure systemd override
mkdir -p /etc/systemd/system/elasticsearch.service.d/
cat > /etc/systemd/system/elasticsearch.service.d/override.conf <<EOF
[Service]
LimitMEMLOCK=infinity
EOF

# Configure Kibana
cat > /etc/kibana/kibana.yml <<EOF
server.host: "0.0.0.0"
server.port: 5601
elasticsearch.hosts: ["http://localhost:9200"]
server.name: "${project_name}-kibana-${environment}"
EOF

# Reload systemd and start services
systemctl daemon-reload

# Enable and start Elasticsearch
systemctl enable elasticsearch
systemctl start elasticsearch

# Enable and start Kibana
systemctl enable kibana
systemctl start kibana

# Wait for Elasticsearch to be ready
echo "Waiting for Elasticsearch to start..."
for i in {1..30}; do
    if curl -s http://localhost:9200/_cluster/health > /dev/null; then
        echo "✅ Elasticsearch is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 10
done

# Create the cairo-genizah index with proper mapping
echo "Creating cairo-genizah index..."
curl -X PUT "localhost:9200/cairo-genizah" \
  -H 'Content-Type: application/json' \
  -d '{
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "index.max_result_window": 50000
    },
    "mappings": {
      "properties": {
        "doc_id": {"type": "keyword"},
        "text": {"type": "text", "analyzer": "standard"},
        "embedding": {
          "type": "dense_vector",
          "dims": 128,
          "index": true,
          "similarity": "cosine"
        },
        "language": {"type": "keyword"},
        "content_type": {"type": "keyword"},
        "document_type": {"type": "keyword"},
        "institution": {"type": "keyword"},
        "library": {"type": "keyword"},
        "collection": {"type": "keyword"},
        "collection_type": {"type": "keyword"},
        "has_images": {"type": "boolean"},
        "has_description": {"type": "boolean"},
        "has_transcriptions": {"type": "boolean"},
        "has_translations": {"type": "boolean"},
        "has_date": {"type": "boolean"},
        "transcription_completeness": {"type": "keyword"},
        "donation_year": {"type": "keyword"},
        "donor_surname": {"type": "keyword"},
        "source_institution": {"type": "keyword"},
        "crowding_tag": {"type": "keyword"},
        "created_at": {"type": "date"},
        "processed_at": {"type": "date"}
      }
    }
  }'

echo ""
echo "✅ Elasticsearch setup complete at $(date)"
echo "🔍 Elasticsearch: http://$(curl -s ifconfig.me):9200"
echo "📊 Kibana: http://$(curl -s ifconfig.me):5601"
echo "📋 Logs: /var/log/elasticsearch-setup.log"
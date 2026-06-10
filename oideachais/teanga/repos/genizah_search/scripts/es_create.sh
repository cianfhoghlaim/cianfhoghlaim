#!/bin/bash
# Create a GCP VM for Elasticsearch
gcloud compute instances create cairo-elasticsearch \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-standard \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=elasticsearch-server \
  --metadata=startup-script='#!/bin/bash
    # Update system
    apt update && apt upgrade -y

    # Install Java
    apt install -y openjdk-11-jdk

    # Add Elasticsearch repository
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
    echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" > /etc/apt/sources.list.d/elastic-8.x.list

    # Install Elasticsearch
    apt update
    apt install -y elasticsearch

    # Configure Elasticsearch
    cat > /etc/elasticsearch/elasticsearch.yml <<EOF
cluster.name: cairo-genizah-cluster
node.name: cairo-node-1
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node

# Security disabled for simplicity
xpack.security.enabled: false
xpack.security.enrollment.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false

# Memory settings
bootstrap.memory_lock: true
EOF

    # Set JVM heap (use half of available RAM)
    cat > /etc/elasticsearch/jvm.options.d/heap.options <<EOF
-Xms2g
-Xmx2g
EOF

    # Set memory limits
    echo "elasticsearch soft memlock unlimited" >> /etc/security/limits.conf
    echo "elasticsearch hard memlock unlimited" >> /etc/security/limits.conf

    # Enable and start
    systemctl enable elasticsearch
    systemctl start elasticsearch

    # Install nginx for basic auth (optional)
    apt install -y nginx apache2-utils
    '

# Create firewall rule for Elasticsearch
gcloud compute firewall-rules create allow-elasticsearch \
  --allow tcp:9200 \
  --source-ranges 0.0.0.0/0 \
  --target-tags elasticsearch-server \
  --description "Allow Elasticsearch access"

# Optional: Create firewall rule for Kibana
gcloud compute firewall-rules create allow-kibana \
  --allow tcp:5601 \
  --source-ranges 0.0.0.0/0 \
  --target-tags elasticsearch-server \
  --description "Allow Kibana access"

echo "Elasticsearch VM is being created..."
echo "It will be ready in about 5 minutes."
echo "Get the external IP with: gcloud compute instances describe cairo-elasticsearch --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)'"
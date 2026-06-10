#!/bin/bash

# Create cairo_user using existing elastic password
VM_NAME="cairo-elasticsearch"
ZONE="us-central1-a"

# Prompt for the elastic password
echo "Enter the elastic user password:"
read -s ELASTIC_PASSWORD

echo ""
echo "Creating cairo_user with elastic password..."

gcloud compute ssh $VM_NAME --zone=$ZONE --command="
echo 'Testing elastic user authentication...'
curl -u elastic:$ELASTIC_PASSWORD 'http://localhost:9200/_cluster/health'

echo ''
echo 'Creating cairo_user...'
curl -X POST 'localhost:9200/_security/user/cairo_user' \\
  -u 'elastic:$ELASTIC_PASSWORD' \\
  -H 'Content-Type: application/json' \\
  -d '{
    \"password\": \"cairo_secure_123\",
    \"roles\": [\"superuser\"],
    \"full_name\": \"Cairo Application User\",
    \"email\": \"cairo@example.com\"
  }'

echo ''
echo 'Testing cairo_user...'
curl -u cairo_user:cairo_secure_123 'http://localhost:9200/_cluster/health'

echo ''
echo 'SUCCESS! Cairo user created.'
echo ''
echo 'APPLICATION CREDENTIALS:'
echo 'Username: cairo_user'
echo 'Password: cairo_secure_123'
"

echo ""
EXTERNAL_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "External IP: $EXTERNAL_IP"
echo ""
echo "✅ CAIRO USER CREATED"
echo ""
echo "Update your .env file:"
echo "ELASTICSEARCH_HOST=http://$EXTERNAL_IP:9200"
echo "ELASTICSEARCH_USERNAME=cairo_user"
echo "ELASTICSEARCH_PASSWORD=cairo_secure_123"
echo ""
echo "Test from your machine:"
echo "curl -u cairo_user:cairo_secure_123 http://$EXTERNAL_IP:9200/_cluster/health"
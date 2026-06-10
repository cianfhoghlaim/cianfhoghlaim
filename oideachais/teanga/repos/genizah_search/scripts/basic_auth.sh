#!/bin/bash

# Reset Elasticsearch security to clean state
VM_NAME="cairo-elasticsearch"
ZONE="us-central1-a"

echo "Resetting Elasticsearch security to clean state..."

gcloud compute ssh $VM_NAME --zone=$ZONE --command="
echo 'Step 1: Disable security temporarily...'
sudo sed -i 's/xpack.security.enabled: true/xpack.security.enabled: false/' /etc/elasticsearch/elasticsearch.yml

echo 'Step 2: Restart Elasticsearch without security...'
sudo systemctl restart elasticsearch

echo 'Waiting for Elasticsearch to start...'
sleep 10

echo 'Step 3: Test that ES is working without security...'
curl -s http://localhost:9200/_cluster/health

echo ''
echo 'Step 4: Clear any existing security configuration...'
# Remove any existing users/roles data
sudo rm -rf /var/lib/elasticsearch/nodes/*/indices/.security-*

echo 'Step 5: Re-enable security...'
sudo sed -i 's/xpack.security.enabled: false/xpack.security.enabled: true/' /etc/elasticsearch/elasticsearch.yml

echo 'Step 6: Restart with security enabled...'
sudo systemctl restart elasticsearch

echo 'Waiting for Elasticsearch to start with fresh security...'
sleep 15

echo 'Step 7: Set up passwords for built-in users (fresh start)...'
sudo /usr/share/elasticsearch/bin/elasticsearch-setup-passwords auto -b > /tmp/es_passwords_new.txt

echo 'Generated fresh passwords:'
cat /tmp/es_passwords_new.txt

# Extract the elastic user password
ELASTIC_PASSWORD=\$(grep 'PASSWORD elastic' /tmp/es_passwords_new.txt | awk '{print \$4}')
echo \"Extracted elastic password: \$ELASTIC_PASSWORD\"

echo ''
echo 'Step 8: Create your application user...'
curl -X POST \"localhost:9200/_security/user/cairo_user\" \\
  -u \"elastic:\$ELASTIC_PASSWORD\" \\
  -H 'Content-Type: application/json' \\
  -d '{
    \"password\": \"cairo_secure_123\",
    \"roles\": [\"superuser\"]
  }'

echo ''
echo 'Step 9: Test the new setup...'
curl -u cairo_user:cairo_secure_123 \"http://localhost:9200/_cluster/health\"

echo ''
echo 'RESET COMPLETE!'
echo ''
echo 'ADMIN CREDENTIALS:'
echo \"Username: elastic\"
echo \"Password: \$ELASTIC_PASSWORD\"
echo ''
echo 'APPLICATION CREDENTIALS:'
echo 'Username: cairo_user'
echo 'Password: cairo_secure_123'
"

echo ""
EXTERNAL_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "External IP: $EXTERNAL_IP"
echo ""
echo "Test from your machine:"
echo "curl -u cairo_user:cairo_secure_123 http://$EXTERNAL_IP:9200/_cluster/health"
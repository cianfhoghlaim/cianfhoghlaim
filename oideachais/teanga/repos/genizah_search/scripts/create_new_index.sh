VM_NAME="cairo-app-vm"
ZONE="us-central1-a"

echo "Fixing Elasticsearch connection issues..."
echo "========================================"

gcloud compute ssh $VM_NAME --zone=$ZONE --command="
echo '=== Checking Environment Variables ==='
cat /app/.env
echo ''
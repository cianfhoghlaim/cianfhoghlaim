# Get detailed error information from the failed operation
echo "=== Getting detailed operation information ==="

# Use the operation ID from your error message
OPERATION_ID="5581651914908499968"
PROJECT_ID="133237556095"  # From your error
LOCATION="us-central1"

echo "Fetching operation details..."
gcloud ai operations describe projects/${PROJECT_ID}/locations/${LOCATION}/operations/${OPERATION_ID} \
  --format="json" > operation_details.json

echo "=== Operation Details ==="
cat operation_details.json | jq '.'

echo -e "\n=== Checking for specific error details ==="
cat operation_details.json | jq '.error'

echo -e "\n=== Checking metadata for more info ==="
cat operation_details.json | jq '.metadata'

echo -e "\n=== Alternative: Try with gcloud directly ==="
echo "If above doesn't work, try:"
echo "gcloud ai operations describe ${OPERATION_ID} --region=${LOCATION}"

echo -e "\n=== Let's also check a few problematic files manually ==="

# Check some of the files mentioned in the error
PROBLEM_FILES=(
  "gs://cairo-genizah-vector-index-dev/index/batch_64_20250606_020746.json"
  "gs://cairo-genizah-vector-index-dev/index/batch_29_20250606_020735.json"
  "gs://cairo-genizah-vector-index-dev/index/batch_5_20250606_020717.json"
)

for file in "${PROBLEM_FILES[@]}"; do
  echo -e "\n--- Checking $file ---"

  # Quick validation
  first_line=$(gsutil cat "$file" | head -1)
  echo "First record preview:"
  echo "$first_line" | head -c 150
  echo "..."

  # Check if it's valid JSON
  echo "$first_line" | python3 -c "
import json, sys
try:
    data = json.loads(sys.stdin.read())
    print('✓ Valid JSON')

    # Check datapoint_id for issues
    if 'datapoint_id' in data:
        dp_id = str(data['datapoint_id'])
        print(f'ID: {dp_id}')
        if '/' in dp_id:
            print('⚠ Contains forward slash')
        if len(dp_id) > 128:
            print('⚠ ID too long')

    # Check vector
    if 'feature_vector' in data:
        vec = data['feature_vector']
        print(f'Vector length: {len(vec)}')
        if len(vec) != 128:
            print(f'⚠ Wrong dimensions! Expected 128, got {len(vec)}')

except Exception as e:
    print(f'✗ Error: {e}')
"
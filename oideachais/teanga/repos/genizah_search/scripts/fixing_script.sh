# Script to fix duplicate namespace issues in restricts

echo "=== Fixing duplicate namespace issues ==="

# Create backup first
echo "Creating backup..."
gsutil -m cp -r gs://cairo-genizah-vector-index-dev/index gs://cairo-genizah-vector-index-dev/backup_before_namespace_fix_$(date +%Y%m%d_%H%M%S)

# Create Python script to fix namespaces
cat > fix_namespaces.py << 'EOF'
import json
import sys
from collections import defaultdict

def fix_restricts(restricts):
    """Merge duplicate namespaces in restricts array"""
    namespace_values = defaultdict(set)

    # Collect all values for each namespace
    for restrict in restricts:
        namespace = restrict.get('namespace')
        allow_values = restrict.get('allow', [])

        if namespace:
            # Add all values to the set for this namespace
            namespace_values[namespace].update(allow_values)

    # Create new restricts array with merged namespaces
    fixed_restricts = []
    for namespace, values in namespace_values.items():
        fixed_restricts.append({
            "namespace": namespace,
            "allow": sorted(list(values))  # Convert set back to sorted list
        })

    return fixed_restricts

def fix_jsonl_file(input_file, output_file):
    """Fix JSONL file by merging duplicate namespaces in restricts"""
    fixed_count = 0
    total_count = 0

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                total_count += 1

                # Fix restricts if present
                if 'restricts' in data and data['restricts']:
                    original_restricts = data['restricts']
                    fixed_restricts = fix_restricts(original_restricts)

                    # Check if we actually fixed something
                    if len(fixed_restricts) != len(original_restricts):
                        fixed_count += 1
                        print(f"  Fixed line {line_num}: {len(original_restricts)} -> {len(fixed_restricts)} restricts")

                    data['restricts'] = fixed_restricts

                # Write fixed JSON
                json.dump(data, outfile, separators=(',', ':'))
                outfile.write('\n')

            except json.JSONDecodeError as e:
                print(f"ERROR: JSON decode error on line {line_num}: {e}")
                continue
            except Exception as e:
                print(f"ERROR: Unexpected error on line {line_num}: {e}")
                continue

    print(f"  Total records: {total_count}, Fixed records: {fixed_count}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_namespaces.py input.json output.json")
        sys.exit(1)

    fix_jsonl_file(sys.argv[1], sys.argv[2])
EOF

echo "=== Processing files to fix duplicate namespaces ==="

# Get list of files
gsutil ls "gs://cairo-genizah-vector-index-dev/index/*.json" > files_to_fix.txt

total_files=$(wc -l < files_to_fix.txt)
current_file=0

while read -r file_url; do
    current_file=$((current_file + 1))
    filename=$(basename "$file_url")
    echo "[$current_file/$total_files] Processing $filename..."

    # Download
    gsutil cp "$file_url" "$filename"

    # Fix with Python
    python3 fix_namespaces.py "$filename" "fixed_$filename"

    # Upload fixed version
    gsutil cp "fixed_$filename" "$file_url"

    # Clean up local files
    rm "$filename" "fixed_$filename"

done < files_to_fix.txt

echo "=== Cleanup ==="
rm files_to_fix.txt fix_namespaces.py

echo "=== Final verification ==="
echo "Checking a sample file for duplicate namespaces:"
sample_file=$(gsutil ls gs://cairo-genizah-vector-index-dev/index/*.json | head -1)
gsutil cat "$sample_file" | head -1 | python3 -c "
import json, sys
from collections import Counter

try:
    data = json.loads(sys.stdin.read())
    if 'restricts' in data:
        namespaces = [r['namespace'] for r in data['restricts']]
        duplicates = [ns for ns, count in Counter(namespaces).items() if count > 1]
        if duplicates:
            print(f'✗ Still has duplicate namespaces: {duplicates}')
        else:
            print('✓ No duplicate namespaces found')
        print(f'Total restricts: {len(data[\"restricts\"])}')
    else:
        print('No restricts field found')
except Exception as e:
    print(f'Error: {e}')
"

echo -e "\n=== Ready for terraform apply ==="
echo "All files should now have unique namespaces in restricts."
echo "Run 'terraform apply' again."
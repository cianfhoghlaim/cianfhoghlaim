import re

files_to_process = ["README.md", "oideachais/README.md", "oideachais/README_eile.md"]

for filepath in files_to_process:
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Dagster
        content = re.sub(r'dagster\s*\(\>=1\.9\.0\)', 'dagster (>=1.13.0)', content)
        content = re.sub(r'Dagster\s+v1\.9\.0', 'Dagster v1.13.0', content)
        content = re.sub(r'\|\s*\*\*dagster\*\*\s*\|\s*>=1\.9\.0\s*\|', '| **dagster** | >=1.13.0 |', content)
        content = re.sub(r'asset-based pipelines \(v1\.9\+\)', 'asset-based pipelines (v1.13+)', content)
        
        # dlt
        content = re.sub(r'dlt\s*\(\>=1\.4\.0\)', 'dlt (>=1.5.0)', content)
        content = re.sub(r'DLT\s+v1\.4\.0', 'DLT v1.5.0', content)
        content = re.sub(r'\|\s*\*\*dlt\*\*\s*\|\s*>=1\.4\.0\s*\|', '| **dlt** | >=1.5.0 |', content)
        content = re.sub(r'streaming support \(v1\.4\+\)', 'streaming support (v1.5+)', content)
        
        # ADK
        content = re.sub(r'google-adk\s*\(\>=0\.1\.0\)', 'google-adk (>=2.1.0)', content)
        content = re.sub(r'Google-ADK\s*\(\>=0\.1\.0\)', 'Google-ADK (>=2.1.0)', content)
        content = re.sub(r'\|\s*\*\*google-adk\*\*\s*\|\s*>=0\.1\.0\s*\|', '| **google-adk** | >=2.1.0 |', content)
        
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Processed {filepath}")
    except Exception as e:
        print(f"Error on {filepath}: {e}")

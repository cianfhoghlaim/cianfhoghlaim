#!/usr/bin/env python3
"""
Agentic 1Password Vault Synchronization Tool (op_sync.py).

This script uses the official `onepassword-sdk-python` to:
1. Parse the `.op.env` template.
2. Ensure all referenced `op://vault/item/field` paths exist in 1Password.
3. Automatically generate a clean, shell-agnostic `.env` file.

REQUIREMENTS:
- pip install onepassword-sdk
- OP_SERVICE_ACCOUNT_TOKEN environment variable set.
"""

import logging
import os
import re
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OnePasswordSync")

try:
    import onepassword
    from onepassword import Client
except ImportError:
    logger.error("onepassword-sdk not found. Please run: pip install onepassword-sdk")
    sys.exit(1)


class VaultSyncAgent:
    def __init__(self, template_path: str = ".op.env", output_path: str = ".env"):
        self.template_path = Path(template_path)
        self.output_path = Path(output_path)

        # Initialize 1Password Client
        token = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
        if not token:
            logger.warning("OP_SERVICE_ACCOUNT_TOKEN not found in environment.")
            logger.info("Falling back to local 1Password CLI integration if possible, but SDK requires a Service Account Token.")
            # We will still parse to show which items are required
            self.client = None
        else:
            try:
                self.client = Client.authenticate(auth=token)
                logger.info("Successfully authenticated with 1Password SDK.")
            except Exception as e:
                logger.error(f"Failed to authenticate with 1Password: {e}")
                self.client = None

    def sync_and_generate(self):
        """Parses the template, validates secrets, and writes the output."""
        if not self.template_path.exists():
            logger.error(f"Template {self.template_path} not found.")
            return

        with open(self.template_path) as f:
            lines = f.readlines()

        missing_secrets = []
        output_lines = []

        # Regex to match op://vault/item/field
        op_regex = re.compile(r'op://([^/]+)/([^/]+)/([^/\s]+)')

        logger.info(f"Scanning {self.template_path} for 1Password references...")

        for _line_num, line in enumerate(lines, 1):
            original_line = line.strip()

            # Skip comments or empty lines
            if not original_line or original_line.startswith('#'):
                output_lines.append(line)
                continue

            # Check if line contains an op:// reference
            match = op_regex.search(original_line)
            if match:
                op_reference = match.group(0)
                vault, item, field = match.groups()

                if self.client:
                    try:
                        logger.debug(f"Resolving {op_reference}...")
                        # Resolve the secret using the SDK
                        resolved_value = self.client.secrets.resolve(op_reference)
                        # Replace the reference with the actual secret
                        new_line = original_line.replace(op_reference, resolved_value)
                        output_lines.append(new_line + "\n")
                        logger.info(f"✅ Successfully loaded: {item}/{field}")
                    except Exception as e:
                        logger.error(f"❌ Failed to resolve {op_reference} in vault '{vault}': {e}")
                        missing_secrets.append(op_reference)
                        output_lines.append(line) # Keep original if failed
                else:
                    # Just simulate the check if SDK client isn't available
                    logger.info(f"🔍 Found requirement for vault='{vault}', item='{item}', field='{field}'")
                    output_lines.append(line)
            else:
                # Regular env var
                output_lines.append(line)

        # Write output file
        if self.client and not missing_secrets:
            with open(self.output_path, 'w') as f:
                f.writelines(output_lines)

            # Secure file permissions
            os.chmod(self.output_path, 0o600)
            logger.info(f"🎉 Successfully generated secure {self.output_path} file!")
        elif missing_secrets:
            logger.warning(f"⚠️ Missing {len(missing_secrets)} secrets in 1Password. {self.output_path} generation aborted to prevent partial state.")
            logger.info("Please ensure the following secrets are created in your 1Password vault:")
            for s in missing_secrets:
                logger.info(f"  -> {s}")
        elif not self.client:
            logger.info(f"Skipped writing {self.output_path} because 1Password Client was not authenticated.")


if __name__ == "__main__":
    agent = VaultSyncAgent()
    agent.sync_and_generate()

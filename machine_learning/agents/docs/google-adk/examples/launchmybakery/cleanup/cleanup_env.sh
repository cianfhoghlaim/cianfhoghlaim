#!/bin/bash

# ==========================================
# MCP Bakery Demo - Complete Cleanup Script
# ==========================================

# 1. Configuration & Project Detection
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
DATASET_NAME="mcp_bakery"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_FILE="$SCRIPT_DIR/../adk_agent/mcp_bakery_app/.env"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: Could not determine Google Cloud Project ID."
    exit 1
fi

# Determine bucket name (Default or Argument)
if [ -z "$1" ]; then
    BUCKET_NAME="gs://mcp-bakery-data-$PROJECT_ID"
else
    BUCKET_NAME=$1
fi

echo "----------------------------------------------------------------"
echo "CLEANUP TARGETS"
echo "----------------------------------------------------------------"
echo "Project:   $PROJECT_ID"
echo "Dataset:   $DATASET_NAME"
echo "Bucket:    $BUCKET_NAME"
echo "Local Env: $ENV_FILE"
echo "API Keys:  Keys named 'bakery-demo-key-*'"
echo "----------------------------------------------------------------"
echo "WARNING: This will permanently delete the dataset, bucket, and API keys."
read -p "Are you sure you want to proceed? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 1
fi
echo "----------------------------------------------------------------"

# ------------------------------------------
# Phase 1: BigQuery & Storage
# ------------------------------------------
echo "[1/5] Removing BigQuery Dataset..."
if bq show "$PROJECT_ID:$DATASET_NAME" >/dev/null 2>&1; then
    # -r = Recursive, -f = Force
    bq rm -r -f --dataset "$PROJECT_ID:$DATASET_NAME"
    echo "      Dataset '$DATASET_NAME' removed."
else
    echo "      Dataset not found. Skipping."
fi

echo "[2/5] Removing Storage Bucket..."
if gcloud storage buckets describe "$BUCKET_NAME" >/dev/null 2>&1; then
    gcloud storage rm --recursive "$BUCKET_NAME"
    echo "      Bucket '$BUCKET_NAME' deleted."
else
    echo "      Bucket not found. Skipping."
fi

# ------------------------------------------
# Phase 2: API Keys
# ------------------------------------------
echo "[3/5] Cleaning up API Keys..."
# Find keys matching the demo pattern
KEYS_TO_DELETE=$(gcloud alpha services api-keys list \
    --filter="displayName:bakery-demo-key-*" \
    --format="value(name)" 2>/dev/null)

if [ -z "$KEYS_TO_DELETE" ]; then
    echo "      No matching API keys found."
else
    for KEY_NAME in $KEYS_TO_DELETE; do
        echo "      Deleting API Key: $KEY_NAME"
        gcloud alpha services api-keys delete "$KEY_NAME" --quiet
    done
    echo "      Keys deleted."
fi

# ------------------------------------------
# Phase 3: Local Config
# ------------------------------------------
echo "[4/5] Removing local configuration..."
if [ -f "$ENV_FILE" ]; then
    rm "$ENV_FILE"
    echo "      Deleted $ENV_FILE"
else
    echo "      .env file not found. Skipping."
fi

# ------------------------------------------
# Phase 4: Disable APIs (Optional)
# ------------------------------------------
echo "[5/5] Checking Enabled APIs..."
echo "----------------------------------------------------------------"
echo "The setup enabled: mapstools, apikeys, bigquery."
echo "NOTE: Only disable these if no other apps in this project use them."
echo ""
read -p "Do you want to disable these APIs? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Disabling APIs (this may take a moment)..."
    gcloud services disable mapstools.googleapis.com --project=$PROJECT_ID --force
    gcloud services disable bigquery.googleapis.com --project=$PROJECT_ID --force
    gcloud services disable apikeys.googleapis.com --project=$PROJECT_ID --force
    echo "APIs disabled."
else
    echo "Skipping API disablement."
fi

echo "----------------------------------------------------------------"
echo "Cleanup Complete!"
echo "----------------------------------------------------------------"
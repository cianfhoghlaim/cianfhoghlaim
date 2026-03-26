#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Get all commits in chronological order from root to HEAD
commits=$(git log --reverse --format="%H" main)

echo "Starting incremental push for $(echo "$commits" | wc -l) commits..."

counter=1
total=$(echo "$commits" | wc -l | tr -d ' ')

for commit in $commits; do
  echo "Pushing commit $counter of $total: $commit"
  
  # Push the specific commit to the main branch on origin
  git push origin "$commit":refs/heads/main --force
  
  echo "Successfully pushed $commit"
  ((counter++))
done

echo "Incremental push completed successfully!"

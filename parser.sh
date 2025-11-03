#!/bin/bash

GREEN='\e[32m'
BLUE='\e[34m'
YELLOW='\e[33m'
CYAN='\e[36m'
NC='\e[0m'

# --- 1. Setup for tracking duplicates ---
# Create a temporary file to store unique hashes.
# We use mktemp for a secure, unique file name.
UNIQUE_TRACKER=$(mktemp)
# Ensure the temporary file is deleted upon script exit
trap 'rm -f "$UNIQUE_TRACKER"' EXIT

# Read from a file or stdin. Here, assuming input.txt contains your JSON list
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines
    [[ -z "$line" ]] && continue

    # Extract fields from JSON
    operationName=$(echo "$line" | jq -r '.operationName')
    variables=$(echo "$line" | jq -c '.variables')
    query=$(echo "$line" | jq -r '.query')

    # --- 2. Create a Unique Identifier (Hash) ---
    # Combine key fields and hash them to create a unique fingerprint.
    # This is more efficient to search than the whole query string.
    # We combine operationName and the full query for a solid unique key.
    UNIQUE_KEY_DATA="${operationName}${query}"
    UNIQUE_HASH=$(echo -n "$UNIQUE_KEY_DATA" | sha256sum | awk '{print $1}')

    # --- 3. Check for Duplicates ---
    # Check if the hash is already in the tracker file
    if grep -q "$UNIQUE_HASH" "$UNIQUE_TRACKER"; then
        echo -e "${YELLOW}Skipping duplicate: ${CYAN}$operationName${NC}"
        continue # Skip the rest of the loop for this line
    fi

    # Record the hash to the tracker file since it's a new, unique entry
    echo "$UNIQUE_HASH" >> "$UNIQUE_TRACKER"

    # --- 4. Processing the Unique Entry (Original Logic) ---
    # Extract operation type and name from the first line of the query
    first_line=$(echo "$query" | head -n1)
    operation_type=$(echo "$first_line" | awk '{print $1}')
    query_name=$(echo "$first_line" | awk '{print $2}')

    # Extract fields for the main GraphQL response
    # This assumes the first field inside the outer braces is the main object
    fields=$(echo "$query" | sed -n '/{/,/}/p' | sed '1d;$d' | sed 's/^[[:space:]]*//')

    # Print results
    echo -e "${YELLOW}----------------------------------------${NC}"
    echo -e "${BLUE}Operation Name:${NC} ${GREEN}$operationName${NC}"
    echo -e "${CYAN}Query Name:${NC} ${GREEN}$query_name${NC}"
    echo -e "${CYAN}Operation Type:${NC} ${GREEN}$operation_type${NC}"
    echo -e "${CYAN}Variables:${NC} ${GREEN}$variables${NC}"
    echo -e "${CYAN}Fields:${NC}"
    echo -e "${GREEN}$fields${NC}"
done < queries.json

#!/bin/bash
# Script to import GoDaddy domains into Cloudflare after they're added via web console

source ../env.sh

cd terraform

echo "=================================================="
echo "Importing GoDaddy domains into Cloudflare"
echo "=================================================="

# Array of domain keys and names
declare -A domains=(
    ["cocoonspamini"]="cocoonspamini.com"
    ["glassbubble"]="glassbubble.net"
    ["iheartdinos"]="iheartdinos.com"
    ["jughunt"]="jughunt.com"
    ["lipbalmjunkie"]="lipbalmjunkie.com"
    ["ohsorad"]="ohsorad.com"
    ["rosamimosa"]="rosamimosa.com"
    ["taicho"]="taicho.com"
    ["tokyo3"]="tokyo3.com"
)

# Import each domain
for key in "${!domains[@]}"; do
    domain="${domains[$key]}"
    echo ""
    echo "Importing $domain as godaddy_domains[\"$key\"]..."
    
    docker run --rm -v $(pwd):/app -w /app \
      -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
      -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
      -e CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN" \
      -e CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID" \
      callableapis:infra terraform import \
        cloudflare_zone.godaddy_domains[\"$key\"] $domain
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully imported $domain"
    else
        echo "❌ Failed to import $domain"
    fi
    
    sleep 1
done

echo ""
echo "=================================================="
echo "Import complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Run: terraform apply"
echo "2. Update nameservers in GoDaddy"
echo "3. Add DNS records to Cloudflare"
echo ""


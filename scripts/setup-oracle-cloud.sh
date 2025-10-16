#!/bin/bash

# Oracle Cloud Infrastructure Setup Helper
# This script helps you gather the required OCI credentials

echo "🔧 Oracle Cloud Infrastructure Setup Helper"
echo "=========================================="
echo ""

echo "📋 Please gather the following information from your OCI console:"
echo ""

echo "1️⃣  USER OCID:"
echo "   • Go to Profile (top-right) → User Settings"
echo "   • Copy the OCID (starts with ocid1.user.oc1..)"
echo ""

echo "2️⃣  TENANCY OCID:"
echo "   • Go to Profile → Tenancy"
echo "   • Copy the OCID (starts with ocid1.tenancy.oc1..)"
echo ""

echo "3️⃣  COMPARTMENT OCID:"
echo "   • Go to Identity & Security → Compartments"
echo "   • Create a compartment named 'callableapis' if needed"
echo "   • Copy the OCID (starts with ocid1.compartment.oc1..)"
echo ""

echo "4️⃣  API KEY FINGERPRINT:"
echo "   • Go to Profile → User Settings → API Keys"
echo "   • Click 'Add API Key' → 'Generate API Key Pair'"
echo "   • Download the private key and save it"
echo "   • Copy the fingerprint (format: xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx)"
echo ""

echo "5️⃣  REGION:"
echo "   • Look at the top-right corner of OCI console"
echo "   • Common regions: us-ashburn-1, us-phoenix-1, us-sanjose-1"
echo ""

echo "📁 PRIVATE KEY LOCATION:"
echo "   • Save the private key as: terraform/oracle/oci-private-key.pem"
echo "   • Make sure it's readable: chmod 600 terraform/oracle/oci-private-key.pem"
echo ""

echo "✅ Once you have all the information, update your env.sh file with:"
echo ""
echo "export OCI_TENANCY_OCID=\"your-tenancy-ocid-here\""
echo "export OCI_USER_OCID=\"your-user-ocid-here\""
echo "export OCI_FINGERPRINT=\"your-fingerprint-here\""
echo "export OCI_PRIVATE_KEY_PATH=\"/Users/rlee/dev/infra/terraform/oracle/oci-private-key.pem\""
echo "export OCI_COMPARTMENT_ID=\"your-compartment-ocid-here\""
echo "export OCI_REGION=\"your-region-here\""
echo ""

echo "🧪 Test your setup with:"
echo "   source env.sh && cd terraform/oracle && terraform plan"
echo ""

echo "❓ Need help? Check the Oracle Cloud documentation:"
echo "   https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm"

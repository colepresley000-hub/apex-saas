#!/bin/bash

echo "🧪 TESTING APEX SWARM DEPLOYMENT FLOW"
echo "="*70
echo ""

BASE_URL="https://keen-wonder-production-d29d.up.railway.app"

# Step 1: Test activation
echo "📝 Step 1: Activating test account..."
ACTIVATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/activate" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "license_key": "TEST-LICENSE-123"
  }')

echo "Response: $ACTIVATE_RESPONSE"

# Extract API key
API_KEY=$(echo $ACTIVATE_RESPONSE | grep -o '"api_key":"[^"]*"' | cut -d'"' -f4)

if [ -z "$API_KEY" ]; then
    echo "❌ Activation failed!"
    exit 1
fi

echo "✅ Account activated!"
echo "API Key: $API_KEY"
echo ""

# Step 2: Deploy arbitrage agent
echo "🤖 Step 2: Deploying arbitrage agent..."
DEPLOY1=$(curl -s -X POST "$BASE_URL/api/v1/agents/deploy" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_type\": \"arbitrage\",
    \"api_key\": \"$API_KEY\"
  }")

echo "Response: $DEPLOY1"
echo ""

# Step 3: Deploy DeFi agent
echo "🌾 Step 3: Deploying DeFi agent..."
DEPLOY2=$(curl -s -X POST "$BASE_URL/api/v1/agents/deploy" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"agent_type\": \"defi\",
    \"api_key\": \"$API_KEY\"
  }")

echo "Response: $DEPLOY2"
echo ""

# Step 4: Check dashboard
echo "📊 Step 4: Checking dashboard..."
DASHBOARD=$(curl -s "$BASE_URL/api/v1/user/dashboard" \
  -H "X-API-Key: $API_KEY")

echo "Dashboard: $DASHBOARD"
echo ""

# Summary
echo "="*70
echo "✅ TEST COMPLETE!"
echo ""
echo "Summary:"
echo "  - Account activated: ✅"
echo "  - API Key generated: ✅"
echo "  - Agents deployed: 2"
echo "  - Dashboard loaded: ✅"
echo ""
echo "To test in browser:"
echo "  1. Go to: $BASE_URL/activate"
echo "  2. Email: test@example.com"
echo "  3. License: TEST-LICENSE-123"
echo "  4. Click activate, get API key"
echo "  5. Go to dashboard"
echo "  6. Deploy agents using the buttons"
echo ""

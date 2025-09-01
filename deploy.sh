#!/bin/bash

echo "🚀 Deploying EvolvingTrader Dashboard to Vercel..."

# Remove any existing vercel.json that might cause issues
rm -f vercel.json

# Create the static vercel.json
cat > vercel.json << EOF
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "index.html"
    }
  ]
}
EOF

echo "✅ Created vercel.json for static deployment"

# Deploy to Vercel
echo "📤 Deploying to Vercel..."
vercel --prod

echo "🎉 Deployment complete!"
echo "Your dashboard should be available at the URL shown above."
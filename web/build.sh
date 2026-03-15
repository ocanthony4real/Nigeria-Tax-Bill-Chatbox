#!/bin/bash
# Build script for local development

echo "Building frontend..."
cd frontend
npm install
npm run build

echo "Copying static files..."
mkdir -p ../static
cp -r out/* ../static/

echo "Done! Run with: uvicorn main:app --reload"

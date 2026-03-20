#!/bin/bash
sed -i 's/\r$//' deploy.sh
chmod +x deploy.sh
echo "fixed"

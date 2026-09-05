#!/bin/bash
# Script to create channel artifacts for FraudMesh Fabric network

set -e

echo "Creating channel artifacts..."

export FABRIC_CFG_PATH=${PWD}
CHANNEL_NAME="fraudmesh-channel"

# Check if configtxgen is available
if ! command -v configtxgen &> /dev/null; then
    echo "configtxgen not found. Please install Hyperledger Fabric binaries."
    echo "For demo purposes, we'll create placeholder files."
    
    # Create placeholder genesis block info
    mkdir -p ./channel-artifacts
    echo "PLACEHOLDER_GENESIS_BLOCK" > ./channel-artifacts/genesis.block
    echo "PLACEHOLDER_CHANNEL_TX" > ./channel-artifacts/${CHANNEL_NAME}.tx
    echo "Placeholder artifacts created for demo."
    exit 0
fi

# Generate genesis block for orderer
echo "Generating genesis block..."
configtxgen -profile FraudMeshOrdererGenesis -channelID fraudmesh-sys-channel -outputBlock ./channel-artifacts/genesis.block

# Generate channel transaction
echo "Generating channel transaction..."
configtxgen -profile FraudMeshChannel -outputCreateChannelTx ./channel-artifacts/${CHANNEL_NAME}.tx -channelID ${CHANNEL_NAME}

# Generate anchor peer updates for Org1
echo "Generating anchor peer update for Org1..."
configtxgen -profile FraudMeshChannel -outputAnchorPeersUpdate ./channel-artifacts/Org1MSPanchors.tx -channelID ${CHANNEL_NAME} -asOrg Org1MSP

# Generate anchor peer updates for Org2
echo "Generating anchor peer update for Org2..."
configtxgen -profile FraudMeshChannel -outputAnchorPeersUpdate ./channel-artifacts/Org2MSPanchors.tx -channelID ${CHANNEL_NAME} -asOrg Org2MSP

# Generate anchor peer updates for Org3
echo "Generating anchor peer update for Org3..."
configtxgen -profile FraudMeshChannel -outputAnchorPeersUpdate ./channel-artifacts/Org3MSPanchors.tx -channelID ${CHANNEL_NAME} -asOrg Org3MSP

echo "Channel artifacts created successfully!"
ls -la ./channel-artifacts/

#!/bin/bash
# Script to generate crypto material for Fabric network
# This creates a simplified crypto setup for the demo

set -e

echo "Generating crypto material for FraudMesh Fabric network..."

CRYPTO_CONFIG_DIR="./crypto-config"
CHANNEL_ARTIFACTS_DIR="./channel-artifacts"

# Create directories
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/{ca,msp,peers,users}
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/{ca,msp,peers,users}
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/{ca,msp,peers,users}
mkdir -p $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/{orderers,msp}

# Generate placeholder certificates (in production, use cryptogen or fabric-ca)
# For demo purposes, we create self-signed certs

echo "Creating organization MSP structures..."

# Org1 MSP
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/msp/{admincerts,cacerts,keystore,signcerts,tlscacerts}
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/peers/peer0.org1.fraudmesh/{msp,tlscacerts}
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/users/Admin@org1.fraudmesh/msp

# Org2 MSP
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/msp/{admincerts,cacerts,keystore,signcerts,tlscacerts}
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/peers/peer0.org2.fraudmesh/{msp,tlscacerts}
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/users/Admin@org2.fraudmesh/msp

# Org3 MSP
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/msp/{admincerts,cacerts,keystore,signcerts,tlscacerts}
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/peers/peer0.org3.fraudmesh/{msp,tlscacerts}
mkdir -p $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/users/Admin@org3.fraudmesh/msp

# Orderer MSP
mkdir -p $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/msp/{admincerts,cacerts,keystore,signcerts,tlscacerts}
mkdir -p $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/orderers/orderer.fraudmesh/{msp,tlscacerts}

# Generate self-signed CA certificates for demo
echo "Generating demo certificates..."

# Org1 CA
openssl genrsa -out $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/ca/ca.org1.fraudmesh-key.pem 2048 2>/dev/null
openssl req -new -x509 -key $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/ca/ca.org1.fraudmesh-key.pem \
  -out $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/ca/ca.org1.fraudmesh-cert.pem \
  -days 365 -subj "/C=US/ST=California/L=San Francisco/O=Org1/OU=CA/CN=ca.org1.fraudmesh" 2>/dev/null

# Org2 CA
openssl genrsa -out $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/ca/ca.org2.fraudmesh-key.pem 2048 2>/dev/null
openssl req -new -x509 -key $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/ca/ca.org2.fraudmesh-key.pem \
  -out $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/ca/ca.org2.fraudmesh-cert.pem \
  -days 365 -subj "/C=US/ST=California/L=San Francisco/O=Org2/OU=CA/CN=ca.org2.fraudmesh" 2>/dev/null

# Org3 CA
openssl genrsa -out $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/ca/ca.org3.fraudmesh-key.pem 2048 2>/dev/null
openssl req -new -x509 -key $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/ca/ca.org3.fraudmesh-key.pem \
  -out $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/ca/ca.org3.fraudmesh-cert.pem \
  -days 365 -subj "/C=US/ST=California/L=San Francisco/O=Org3/OU=CA/CN=ca.org3.fraudmesh" 2>/dev/null

# Copy CA certs to MSP directories
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/ca/ca.org1.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/msp/cacerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/ca/ca.org1.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/msp/admincerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/ca/ca.org1.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/peers/peer0.org1.fraudmesh/msp/cacerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/ca/ca.org1.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/peers/peer0.org1.fraudmesh/msp/admincerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/ca/ca.org1.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/users/Admin@org1.fraudmesh/msp/cacerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/ca/ca.org1.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/users/Admin@org1.fraudmesh/msp/admincerts/

# Generate peer0.org1 keys
openssl genrsa -out $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/peers/peer0.org1.fraudmesh/msp/keystore/priv_sk.pem 2048 2>/dev/null
openssl req -new -key $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/peers/peer0.org1.fraudmesh/msp/keystore/priv_sk.pem \
  -out $CRYPTO_CONFIG_DIR/peerOrganizations/org1.fraudmesh/peers/peer0.org1.fraudmesh/msp/signcerts/cert.pem \
  -subj "/C=US/ST=California/L=San Francisco/O=Org1/OU=Peer/CN=peer0.org1.fraudmesh" 2>/dev/null

# Similar for Org2
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/ca/ca.org2.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/msp/cacerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/ca/ca.org2.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/msp/admincerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/ca/ca.org2.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/peers/peer0.org2.fraudmesh/msp/cacerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/ca/ca.org2.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/peers/peer0.org2.fraudmesh/msp/admincerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/ca/ca.org2.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/users/Admin@org2.fraudmesh/msp/cacerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/ca/ca.org2.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/users/Admin@org2.fraudmesh/msp/admincerts/

openssl genrsa -out $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/peers/peer0.org2.fraudmesh/msp/keystore/priv_sk.pem 2048 2>/dev/null
openssl req -new -key $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/peers/peer0.org2.fraudmesh/msp/keystore/priv_sk.pem \
  -out $CRYPTO_CONFIG_DIR/peerOrganizations/org2.fraudmesh/peers/peer0.org2.fraudmesh/msp/signcerts/cert.pem \
  -subj "/C=US/ST=California/L=San Francisco/O=Org2/OU=Peer/CN=peer0.org2.fraudmesh" 2>/dev/null

# Similar for Org3
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/ca/ca.org3.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/msp/cacerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/ca/ca.org3.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/msp/admincerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/ca/ca.org3.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/peers/peer0.org3.fraudmesh/msp/cacerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/ca/ca.org3.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/peers/peer0.org3.fraudmesh/msp/admincerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/ca/ca.org3.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/users/Admin@org3.fraudmesh/msp/cacerts/
cp $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/ca/ca.org3.fraudmesh-cert.pem \
   $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/users/Admin@org3.fraudmesh/msp/admincerts/

openssl genrsa -out $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/peers/peer0.org3.fraudmesh/msp/keystore/priv_sk.pem 2048 2>/dev/null
openssl req -new -key $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/peers/peer0.org3.fraudmesh/msp/keystore/priv_sk.pem \
  -out $CRYPTO_CONFIG_DIR/peerOrganizations/org3.fraudmesh/peers/peer0.org3.fraudmesh/msp/signcerts/cert.pem \
  -subj "/C=US/ST=California/L=San Francisco/O=Org3/OU=Peer/CN=peer0.org3.fraudmesh" 2>/dev/null

# Orderer setup
ORDERER_CA_KEY=$CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/ca/ca.fraudmesh-key.pem
ORDERER_CA_CERT=$CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/ca/ca.fraudmesh-cert.pem
openssl genrsa -out $ORDERER_CA_KEY 2048 2>/dev/null
openssl req -new -x509 -key $ORDERER_CA_KEY \
  -out $ORDERER_CA_CERT \
  -days 365 -subj "/C=US/ST=California/L=San Francisco/O=OrdererOrg/OU=CA/CN=ca.fraudmesh" 2>/dev/null

cp $ORDERER_CA_CERT $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/msp/cacerts/
cp $ORDERER_CA_CERT $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/msp/admincerts/
cp $ORDERER_CA_CERT $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/orderers/orderer.fraudmesh/msp/cacerts/
cp $ORDERER_CA_CERT $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/orderers/orderer.fraudmesh/msp/admincerts/

openssl genrsa -out $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/orderers/orderer.fraudmesh/msp/keystore/priv_sk.pem 2048 2>/dev/null
openssl req -new -key $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/orderers/orderer.fraudmesh/msp/keystore/priv_sk.pem \
  -out $CRYPTO_CONFIG_DIR/ordererOrganizations/fraudmesh/orderers/orderer.fraudmesh/msp/signcerts/cert.pem \
  -subj "/C=US/ST=California/L=San Francisco/O=OrdererOrg/OU=Orderer/CN=orderer.fraudmesh" 2>/dev/null

echo "Crypto material generated successfully!"
echo ""
echo "Next steps:"
echo "1. Generate genesis block using configtxgen"
echo "2. Create channel transaction using configtxgen"
echo "3. Start the Fabric network"

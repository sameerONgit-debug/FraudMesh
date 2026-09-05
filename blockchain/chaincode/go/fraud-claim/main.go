// SPDX-License-Identifier: Apache-2.0
/*
 * FraudMesh Fraud Claim Chaincode
 * 
 * This chaincode manages fraud claims and case events on the Hyperledger Fabric ledger.
 * It stores minimal metadata and cryptographic commitments - NO raw PII or sensitive data.
 */

package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-chaincode-go/pkg/cid"
	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// FraudClaim represents a minimal fraud signal stored on the ledger
// IMPORTANT: No raw PII, account numbers, or sensitive customer data
type FraudClaim struct {
	ClaimID           string  `json:"claimId"`
	EntityToken       string  `json:"entityToken"`       // Tokenized identifier (HMAC)
	SignalType        string  `json:"signalType"`        // e.g., CONFIRMED_MULE_ASSOCIATION
	Confidence        float64 `json:"confidence"`        // 0.0 to 1.0
	SourceInstitution string  `json:"sourceInstitution"` // e.g., BANK_B
	EvidenceHash      string  `json:"evidenceHash"`      // SHA-256 of off-chain evidence
	ModelVersion      string  `json:"modelVersion"`      // e.g., fraud-v1.3
	Status            string  `json:"status"`            // ACTIVE, DISPUTED, CLEARED, EXPIRED
	CreatedAt         int64   `json:"createdAt"`         // Unix timestamp
	UpdatedAt         int64   `json:"updatedAt"`         // Unix timestamp
	ExpiresAt         int64   `json:"expiresAt"`         // Unix timestamp
	Version           int     `json:"version"`           // Version number for auditing
}

// CaseEvent represents an auditable event in a fraud investigation
type CaseEvent struct {
	EventID       string `json:"eventId"`
	CaseID        string `json:"caseId"`
	EventType     string `json:"eventType"` // CASE_CREATED, RISK_COMPUTED, etc.
	Institution   string `json:"institution"`
	Actor         string `json:"actor"`
	Timestamp     int64  `json:"timestamp"`
	Reason        string `json:"reason,omitempty"`
	EvidenceHash  string `json:"evidenceHash,omitempty"`
	PreviousState string `json:"previousState,omitempty"`
	NewState      string `json:"newState,omitempty"`
}

// FraudClaimContract implements the smart contract
type FraudClaimContract struct {
	contractapi.Contract
}

// CreateClaim creates a new fraud claim on the ledger
func (cc *FraudClaimContract) CreateClaim(
	ctx contractapi.TransactionContextInterface,
	claimID string,
	entityToken string,
	signalType string,
	confidence float64,
	sourceInstitution string,
	evidenceHash string,
	modelVersion string,
	expiresAt int64,
) error {
	// Check if claim already exists (idempotency)
	exists, err := cc.ClaimExists(ctx, claimID)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("claim %s already exists", claimID)
	}

	// Validate confidence range
	if confidence < 0.0 || confidence > 1.0 {
		return fmt.Errorf("confidence must be between 0.0 and 1.0")
	}

	// Get creator identity for audit
	callerID, err := cid.GetID(ctx.GetStub())
	if err != nil {
		return fmt.Errorf("failed to get caller ID: %v", err)
	}

	now := time.Now().Unix()

	claim := &FraudClaim{
		ClaimID:           claimID,
		EntityToken:       entityToken,
		SignalType:        signalType,
		Confidence:        confidence,
		SourceInstitution: sourceInstitution,
		EvidenceHash:      evidenceHash,
		ModelVersion:      modelVersion,
		Status:            "ACTIVE",
		CreatedAt:         now,
		UpdatedAt:         now,
		ExpiresAt:         expiresAt,
		Version:           1,
	}

	claimJSON, err := json.Marshal(claim)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(claimID, claimJSON)
	if err != nil {
		return fmt.Errorf("failed to put state: %v", err)
	}

	// Create initial case event
	eventID := fmt.Sprintf("EVT-%s-001", claimID)
	caseEvent := &CaseEvent{
		EventID:     eventID,
		CaseID:      claimID,
		EventType:   "CLAIM_CREATED",
		Institution: sourceInstitution,
		Actor:       callerID,
		Timestamp:   now,
		NewState:    "ACTIVE",
	}

	eventJSON, err := json.Marshal(caseEvent)
	if err != nil {
		return err
	}

	eventKey := fmt.Sprintf("event:%s:%s", claimID, eventID)
	err = ctx.GetStub().PutState(eventKey, eventJSON)
	if err != nil {
		return fmt.Errorf("failed to store event: %v", err)
	}

	fmt.Printf("Claim %s created successfully by %s\n", claimID, callerID)
	return nil
}

// GetClaim retrieves a fraud claim by ID
func (cc *FraudClaimContract) GetClaim(
	ctx contractapi.TransactionContextInterface,
	claimID string,
) (*FraudClaim, error) {
	claimJSON, err := ctx.GetStub().GetState(claimID)
	if err != nil {
		return nil, fmt.Errorf("failed to read claim: %v", err)
	}
	if claimJSON == nil {
		return nil, fmt.Errorf("claim %s does not exist", claimID)
	}

	var claim FraudClaim
	err = json.Unmarshal(claimJSON, &claim)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal claim: %v", err)
	}

	return &claim, nil
}

// ClaimExists checks if a claim exists
func (cc *FraudClaimContract) ClaimExists(
	ctx contractapi.TransactionContextInterface,
	claimID string,
) (bool, error) {
	claimJSON, err := ctx.GetStub().GetState(claimID)
	if err != nil {
		return false, fmt.Errorf("failed to read claim: %v", err)
	}
	return claimJSON != nil && len(claimJSON) > 0, nil
}

// UpdateClaimState updates the status of an existing claim
func (cc *FraudClaimContract) UpdateClaimState(
	ctx contractapi.TransactionContextInterface,
	claimID string,
	newStatus string,
	reason string,
) error {
	claim, err := cc.GetClaim(ctx, claimID)
	if err != nil {
		return err
	}

	// Validate status transition
	validStatuses := map[string]bool{
		"ACTIVE": true, "SUSPECTED": true, "UNDER_REVIEW": true,
		"CONFIRMED": true, "DISPUTED": true, "CLEARED": true, "EXPIRED": true,
	}
	if !validStatuses[newStatus] {
		return fmt.Errorf("invalid status: %s", newStatus)
	}

	oldStatus := claim.Status
	claim.Status = newStatus
	claim.UpdatedAt = time.Now().Unix()
	claim.Version++

	// Get caller identity
	callerID, err := cid.GetID(ctx.GetStub())
	if err != nil {
		return fmt.Errorf("failed to get caller ID: %v", err)
	}

	claimJSON, err := json.Marshal(claim)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(claimID, claimJSON)
	if err != nil {
		return fmt.Errorf("failed to update claim: %v", err)
	}

	// Record event
	eventID := fmt.Sprintf("EVT-%s-%03d", claimID, claim.Version)
	caseEvent := &CaseEvent{
		EventID:       eventID,
		CaseID:        claimID,
		EventType:     "CLAIM_STATUS_UPDATED",
		Institution:   claim.SourceInstitution,
		Actor:         callerID,
		Timestamp:     claim.UpdatedAt,
		Reason:        reason,
		PreviousState: oldStatus,
		NewState:      newStatus,
	}

	eventJSON, err := json.Marshal(caseEvent)
	if err != nil {
		return err
	}

	eventKey := fmt.Sprintf("event:%s:%s", claimID, eventID)
	err = ctx.GetStub().PutState(eventKey, eventJSON)
	if err != nil {
		return fmt.Errorf("failed to store event: %v", err)
	}

	fmt.Printf("Claim %s updated from %s to %s by %s\n", claimID, oldStatus, newStatus, callerID)
	return nil
}

// DisputeClaim marks a claim as disputed
func (cc *FraudClaimContract) DisputeClaim(
	ctx contractapi.TransactionContextInterface,
	claimID string,
	reason string,
) error {
	callerID, err := cid.GetID(ctx.GetStub())
	if err != nil {
		return err
	}

	claim, err := cc.GetClaim(ctx, claimID)
	if err != nil {
		return err
	}

	if claim.Status == "DISPUTED" {
		return fmt.Errorf("claim %s is already disputed", claimID)
	}

	oldStatus := claim.Status
	claim.Status = "DISPUTED"
	claim.UpdatedAt = time.Now().Unix()
	claim.Version++

	claimJSON, err := json.Marshal(claim)
	if err != nil {
		return err
	}

	err = ctx.GetStub().PutState(claimID, claimJSON)
	if err != nil {
		return err
	}

	// Record dispute event
	eventID := fmt.Sprintf("EVT-%s-%03d", claimID, claim.Version)
	caseEvent := &CaseEvent{
		EventID:       eventID,
		CaseID:        claimID,
		EventType:     "CLAIM_DISPUTED",
		Institution:   claim.SourceInstitution,
		Actor:         callerID,
		Timestamp:     claim.UpdatedAt,
		Reason:        reason,
		PreviousState: oldStatus,
		NewState:      "DISPUTED",
	}

	eventJSON, err := json.Marshal(caseEvent)
	if err != nil {
		return err
	}

	eventKey := fmt.Sprintf("event:%s:%s", claimID, eventID)
	return ctx.GetStub().PutState(eventKey, eventJSON)
}

// ConfirmClaim marks a claim as confirmed
func (cc *FraudClaimContract) ConfirmClaim(
	ctx contractapi.TransactionContextInterface,
	claimID string,
	reason string,
) error {
	return cc.UpdateClaimState(ctx, claimID, "CONFIRMED", reason)
}

// ClearClaim marks a claim as cleared
func (cc *FraudClaimContract) ClearClaim(
	ctx contractapi.TransactionContextInterface,
	claimID string,
	reason string,
) error {
	return cc.UpdateClaimState(ctx, claimID, "CLEARED", reason)
}

// ExpireClaim marks a claim as expired
func (cc *FraudClaimContract) ExpireClaim(
	ctx contractapi.TransactionContextInterface,
	claimID string,
) error {
	claim, err := cc.GetClaim(ctx, claimID)
	if err != nil {
		return err
	}

	now := time.Now().Unix()
	if now < claim.ExpiresAt {
		return fmt.Errorf("claim %s has not yet expired", claimID)
	}

	return cc.UpdateClaimState(ctx, claimID, "EXPIRED", "Automatic expiry")
}

// AddCaseEvent adds a new event to a case history
func (cc *FraudClaimContract) AddCaseEvent(
	ctx contractapi.TransactionContextInterface,
	caseID string,
	eventType string,
	institution string,
	actor string,
	reason string,
	evidenceHash string,
) error {
	claim, err := cc.GetClaim(ctx, caseID)
	if err != nil {
		// If claim doesn't exist, we can still add events for related cases
		// This allows tracking investigation steps before claim creation
	}

	now := time.Now().Unix()
	eventID := fmt.Sprintf("EVT-%s-%d", caseID, now)

	caseEvent := &CaseEvent{
		EventID:      eventID,
		CaseID:       caseID,
		EventType:    eventType,
		Institution:  institution,
		Actor:        actor,
		Timestamp:    now,
		Reason:       reason,
		EvidenceHash: evidenceHash,
	}

	eventJSON, err := json.Marshal(caseEvent)
	if err != nil {
		return err
	}

	eventKey := fmt.Sprintf("event:%s:%s", caseID, eventID)
	return ctx.GetStub().PutState(eventKey, eventJSON)
}

// GetCaseHistory retrieves all events for a case
func (cc *FraudClaimContract) GetCaseHistory(
	ctx contractapi.TransactionContextInterface,
	caseID string,
) ([]*CaseEvent, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange(
		fmt.Sprintf("event:%s:", caseID),
		fmt.Sprintf("event:%s:\uffff", caseID),
	)
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var events []*CaseEvent
	for resultsIterator.HasNext() {
		response, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var event CaseEvent
		err = json.Unmarshal(response.Value, &event)
		if err != nil {
			return nil, fmt.Errorf("failed to unmarshal event: %v", err)
		}
		events = append(events, &event)
	}

	return events, nil
}

// QueryClaimsByEntityToken finds all claims for a given entity token
func (cc *FraudClaimContract) QueryClaimsByEntityToken(
	ctx contractapi.TransactionContextInterface,
	entityToken string,
) ([]*FraudClaim, error) {
	// Note: In production, use CouchDB indexes for efficient queries
	// For demo, we iterate through all claims
	
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "\uffff")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var matchingClaims []*FraudClaim
	for resultsIterator.HasNext() {
		response, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		// Skip events
		if len(response.Key) > 6 && response.Key[:6] == "event:" {
			continue
		}

		var claim FraudClaim
		err = json.Unmarshal(response.Value, &claim)
		if err != nil {
			continue
		}

		if claim.EntityToken == entityToken && claim.Status == "ACTIVE" {
			matchingClaims = append(matchingClaims, &claim)
		}
	}

	return matchingClaims, nil
}

// VerifyClaim verifies a claim's integrity and status
func (cc *FraudClaimContract) VerifyClaim(
	ctx contractapi.TransactionContextInterface,
	claimID string,
) (map[string]interface{}, error) {
	claim, err := cc.GetClaim(ctx, claimID)
	if err != nil {
		return nil, err
	}

	now := time.Now().Unix()

	result := map[string]interface{}{
		"claimId":        claim.ClaimID,
		"exists":         true,
		"status":         claim.Status,
		"notExpired":     now < claim.ExpiresAt,
		"evidenceHash":   claim.EvidenceHash,
		"sourceOrg":      claim.SourceInstitution,
		"version":        claim.Version,
		"createdAt":      claim.CreatedAt,
		"updatedAt":      claim.UpdatedAt,
		"verificationTs": now,
	}

	return result, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&FraudClaimContract{})
	if err != nil {
		panic(fmt.Sprintf("Error creating fraud-claim chaincode: %s", err))
	}

	if err := chaincode.Start(); err != nil {
		panic(fmt.Sprintf("Error starting fraud-claim chaincode: %s", err))
	}
}

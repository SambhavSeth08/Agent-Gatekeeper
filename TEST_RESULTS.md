# Agent Gatekeeper – Test Results

**Student Enrolment Number:** PGD202568904  
**Organization:** JPMorgan Chase Bank  
**Project:** Agent Gatekeeper  
**Testing Date:** 21 November 2026

## 1. Testing Objective

The objective of testing is to verify whether the Agent Gatekeeper prototype correctly evaluates banking requests submitted by AI agents and generates appropriate authorization decisions.

## 2. Test Cases

| Test ID | Test Scenario | Expected Decision | Actual Decision | Status |
|---|---|---|---|---|
| TC01 | Known active agent – View Balance | ALLOW | Enter actual result | Enter PASS/FAIL |
| TC02 | Unknown agent – View Balance | BLOCK | Enter actual result | Enter PASS/FAIL |
| TC03 | Payment above spending limit | ASK CUSTOMER | Enter actual result | Enter PASS/FAIL |
| TC04 | Payment below spending limit | ALLOW | Enter actual result | Enter PASS/FAIL |
| TC05 | Revoked agent makes a request | BLOCK | Enter actual result | Enter PASS/FAIL |
| TC06 | Active agent – Money Transfer | Verify configured rule | Enter actual result | Enter PASS/FAIL |

## 3. Testing Observations

The application was tested using the Request Simulator and Test Cases & Verification module.

The testing process focused on:

- Agent authorization and registration.
- Unknown and revoked agent handling.
- Banking request authorization.
- Transaction spending limits.
- Compliance audit logging.

## 4. Conclusion

The testing exercise demonstrates how an Agent Gatekeeper can help a bank control access by external AI agents. It provides an authorization layer that evaluates requests before allowing banking actions.

The prototype is developed for academic demonstration and is not connected to actual JPMorgan Chase banking systems.

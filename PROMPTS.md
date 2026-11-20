# PROMPTS.md
## Agent Gatekeeper – AI Agent Authorization and Risk Management System

**Student Enrolment Number:** PGD202568904  
**Organization:** JPMorgan Chase Bank  
**Project:** Agent Gatekeeper  
**Development Tool:** Antigravity AI Coding Assistant

---

## 1. Primary Master Prompt

**Date:** 14 November 2026

The following is a structured record of the master prompt provided through ChatGPT and pasted into Antigravity to develop the Agent Gatekeeper application.

### Prompt Objective

Develop a functional Python-based Agent Gatekeeper prototype for JPMorgan Chase Bank using Streamlit and SQLite.

The application should act as an authorization gateway between external AI agents and banking services. It should evaluate customer requests and return one of three decisions:

- ALLOW
- ASK CUSTOMER
- BLOCK

### Functional Requirements

1. Display the project name and student enrolment number PGD202568904 on the application dashboard.
2. Provide an interface to register AI agents.
3. Allow users to view registered agents and revoke their authorization.
4. Accept customer name, agent name, banking action and transaction amount.
5. Implement authorization rules R1–R7.
6. Generate decisions with the corresponding rule number.
7. Maintain a compliance audit log containing timestamps, requests, decisions and rule references.
8. Provide six test cases to demonstrate the authorization logic.
9. Use SQLite for database operations.
10. Create a professional and user-friendly Streamlit dashboard.

### Authorization Rules

| Rule | Condition | Decision |
|---|---|---|
| R1 | Unknown agent | BLOCK |
| R2 | Revoked agent | BLOCK |
| R3 | Active agent requesting balance information | ALLOW |
| R4 | Bill payment up to ₹5,000 | ALLOW |
| R5 | Bill payment above ₹5,000 | ASK CUSTOMER |
| R6 | Money transfer request | ASK CUSTOMER |
| R7 | Invalid request | BLOCK |

### Expected Technology

- Python
- Streamlit
- SQLite

### Expected Project Files

- app.py
- database.py
- engine.py
- tests.py
- requirements.txt
- README.md

---

## 2. Additional Development Instructions

The development process also involved checking the application's functionality, running the test suite, resolving implementation issues where necessary, and preparing the application for deployment.

The final application was deployed using Streamlit Community Cloud and connected to the GitHub repository.

**Live Application:** https://agent-gatekeeper-ai.streamlit.app

---

## 3. Personal Verification and Changes

The following activities were personally reviewed or completed during the project:

1. Checked the deployed Streamlit application and its dashboard.
2. Reviewed the available application modules, including agent registration, agent management, request simulation and compliance audit log.
3. Updated the GitHub README to include the live application link.
4. Added an academic disclaimer clarifying that the prototype does not connect to actual JPMorgan Chase banking systems or process real financial transactions.

---

## 4. Academic Integrity Statement

This document records the main development prompt and requirements used for the project. The primary prompt was originally provided through ChatGPT and pasted into Antigravity.

The prompt description above is a structured summary, not a verbatim reproduction of the original conversation.

The application is an academic prototype developed for educational and demonstration purposes.

"""
Agent Gatekeeper - Decision Engine
JPMorgan Chase Bank | AI & Digital Transformation MBA Project
Student Enrolment Number: PGD202568904

Implements predefined authorization rules and strict priority evaluation:
Priority 1: RULE R7 - Invalid Request
Priority 2: RULE R1 - Unknown Agent
Priority 3: RULE R2 - Revoked Agent
Priority 4: RULE R3 - Read-Only Access
Priority 5: RULE R4 - Small Bill Payment
Priority 6: RULE R5 - Large Bill Payment
Priority 7: RULE R6 - Money Transfer
"""

from datetime import datetime
from database import get_agent

VALID_ACTIONS = [
    "View Account Balance",
    "Pay a Bill",
    "Transfer Money"
]

BILL_PAYMENT_AUTONOMOUS_LIMIT = 5000.0  # ₹5,000 threshold


def evaluate_request(customer_id, customer_name, agent_id, agent_name, banking_action, transaction_amount):
    """
    Evaluates an external AI agent's banking request against predefined authorization rules
    in strict priority order.

    Returns:
        dict: {
            "decision": "ALLOW" | "ASK CUSTOMER" | "BLOCK",
            "rule_number": "R1".."R7",
            "rule_title": str,
            "explanation": str,
            "agent_status": "ACTIVE" | "REVOKED" | "UNKNOWN",
            "timestamp": str,
            "action": str,
            "amount": float,
            "customer_id": str,
            "customer_name": str,
            "agent_id": str,
            "agent_name": str
        }
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Clean string inputs
    c_id = str(customer_id).strip() if customer_id is not None else ""
    c_name = str(customer_name).strip() if customer_name is not None else ""
    a_id = str(agent_id).strip() if agent_id is not None else ""
    a_name = str(agent_name).strip() if agent_name is not None else ""
    action = str(banking_action).strip() if banking_action is not None else ""

    # Parse and validate transaction amount
    try:
        amount = float(transaction_amount) if transaction_amount is not None and str(transaction_amount).strip() != "" else 0.0
    except (ValueError, TypeError):
        amount = None

    # =========================================================================
    # PRIORITY 1: RULE R7 - INVALID REQUEST
    # If the request contains missing information, a negative amount or an
    # unsupported banking action, BLOCK the request.
    # =========================================================================
    if not c_id or not c_name or not a_id or not a_name:
        return {
            "decision": "BLOCK",
            "rule_number": "R7",
            "rule_title": "INVALID REQUEST",
            "explanation": "Request rejected due to missing mandatory fields (Customer ID, Customer Name, Agent ID, or Agent Name).",
            "agent_status": "UNKNOWN",
            "timestamp": timestamp,
            "action": action,
            "amount": amount if amount is not None else 0.0,
            "customer_id": c_id,
            "customer_name": c_name,
            "agent_id": a_id,
            "agent_name": a_name
        }

    if amount is None or amount < 0:
        return {
            "decision": "BLOCK",
            "rule_number": "R7",
            "rule_title": "INVALID REQUEST",
            "explanation": f"Request rejected due to invalid transaction amount ({amount}). Negative or non-numeric amounts are strictly prohibited.",
            "agent_status": "UNKNOWN",
            "timestamp": timestamp,
            "action": action,
            "amount": -1.0 if amount is None else amount,
            "customer_id": c_id,
            "customer_name": c_name,
            "agent_id": a_id,
            "agent_name": a_name
        }

    if action not in VALID_ACTIONS:
        return {
            "decision": "BLOCK",
            "rule_number": "R7",
            "rule_title": "INVALID REQUEST",
            "explanation": f"Request rejected due to unsupported banking action '{action}'. Supported actions: {', '.join(VALID_ACTIONS)}.",
            "agent_status": "UNKNOWN",
            "timestamp": timestamp,
            "action": action,
            "amount": amount,
            "customer_id": c_id,
            "customer_name": c_name,
            "agent_id": a_id,
            "agent_name": a_name
        }

    # =========================================================================
    # Check agent registration in persistent database
    # =========================================================================
    agent_record = get_agent(a_id)

    # =========================================================================
    # PRIORITY 2: RULE R1 - UNKNOWN AGENT
    # If an agent is not registered in the system, BLOCK the request.
    # =========================================================================
    if agent_record is None:
        return {
            "decision": "BLOCK",
            "rule_number": "R1",
            "rule_title": "UNKNOWN AGENT",
            "explanation": f"Agent ID '{a_id}' is not registered in the JPMorgan Chase Gatekeeper repository. Unrecognized external agents are untrusted and strictly BLOCKED.",
            "agent_status": "UNKNOWN",
            "timestamp": timestamp,
            "action": action,
            "amount": amount,
            "customer_id": c_id,
            "customer_name": c_name,
            "agent_id": a_id,
            "agent_name": a_name
        }

    agent_status = agent_record.get("status", "UNKNOWN")

    # =========================================================================
    # PRIORITY 3: RULE R2 - REVOKED AGENT
    # If an agent has been revoked, BLOCK every request regardless of action or amount.
    # =========================================================================
    if agent_status == "REVOKED":
        rev_time = agent_record.get("revocation_timestamp", "Unknown date")
        rev_reason = agent_record.get("revocation_reason", "Customer or Administrative revocation")
        return {
            "decision": "BLOCK",
            "rule_number": "R2",
            "rule_title": "REVOKED AGENT",
            "explanation": f"Agent '{agent_record.get('agent_name', a_name)}' ({a_id}) was REVOKED on {rev_time} (Reason: {rev_reason}). Revoked agents are permanently prohibited from executing any banking activities.",
            "agent_status": "REVOKED",
            "timestamp": timestamp,
            "action": action,
            "amount": amount,
            "customer_id": c_id,
            "customer_name": c_name,
            "agent_id": a_id,
            "agent_name": a_name
        }

    # Agent is confirmed ACTIVE
    # =========================================================================
    # PRIORITY 4: RULE R3 - READ-ONLY ACCESS
    # If an active registered agent requests to view an account balance, ALLOW.
    # =========================================================================
    if action == "View Account Balance":
        return {
            "decision": "ALLOW",
            "rule_number": "R3",
            "rule_title": "READ-ONLY ACCESS",
            "explanation": f"Active registered agent '{a_name}' ({a_id}) granted read-only access to view customer account balance.",
            "agent_status": "ACTIVE",
            "timestamp": timestamp,
            "action": action,
            "amount": 0.0,
            "customer_id": c_id,
            "customer_name": c_name,
            "agent_id": a_id,
            "agent_name": a_name
        }

    # =========================================================================
    # PRIORITY 5: RULE R4 - SMALL BILL PAYMENT
    # If an active registered agent requests to pay a bill of ₹5,000 or less, ALLOW.
    # =========================================================================
    if action == "Pay a Bill" and amount <= BILL_PAYMENT_AUTONOMOUS_LIMIT:
        return {
            "decision": "ALLOW",
            "rule_number": "R4",
            "rule_title": "SMALL BILL PAYMENT",
            "explanation": f"Bill payment of ₹{amount:,.2f} is within the pre-authorized autonomous threshold of ₹{BILL_PAYMENT_AUTONOMOUS_LIMIT:,.2f}. Request automatically ALLOWED.",
            "agent_status": "ACTIVE",
            "timestamp": timestamp,
            "action": action,
            "amount": amount,
            "customer_id": c_id,
            "customer_name": c_name,
            "agent_id": a_id,
            "agent_name": a_name
        }

    # =========================================================================
    # PRIORITY 6: RULE R5 - LARGE BILL PAYMENT
    # If an active registered agent requests to pay a bill above ₹5,000, ASK CUSTOMER.
    # =========================================================================
    if action == "Pay a Bill" and amount > BILL_PAYMENT_AUTONOMOUS_LIMIT:
        return {
            "decision": "ASK CUSTOMER",
            "rule_number": "R5",
            "rule_title": "LARGE BILL PAYMENT",
            "explanation": f"Bill payment of ₹{amount:,.2f} exceeds the autonomous threshold of ₹{BILL_PAYMENT_AUTONOMOUS_LIMIT:,.2f}. Explicit customer confirmation is REQUIRED before proceeding.",
            "agent_status": "ACTIVE",
            "timestamp": timestamp,
            "action": action,
            "amount": amount,
            "customer_id": c_id,
            "customer_name": c_name,
            "agent_id": a_id,
            "agent_name": a_name
        }

    # =========================================================================
    # PRIORITY 7: RULE R6 - MONEY TRANSFER
    # If an active registered agent requests a money transfer, ASK CUSTOMER regardless of amount.
    # =========================================================================
    if action == "Transfer Money":
        return {
            "decision": "ASK CUSTOMER",
            "rule_number": "R6",
            "rule_title": "MONEY TRANSFER",
            "explanation": f"Money transfer request of ₹{amount:,.2f} carries elevated risk of irrevocable fund outflow. Explicit customer confirmation is REQUIRED regardless of amount.",
            "agent_status": "ACTIVE",
            "timestamp": timestamp,
            "action": action,
            "amount": amount,
            "customer_id": c_id,
            "customer_name": c_name,
            "agent_id": a_id,
            "agent_name": a_name
        }

    # Fallback safety block (fail-safe by design)
    return {
        "decision": "BLOCK",
        "rule_number": "R7",
        "rule_title": "INVALID REQUEST",
        "explanation": "Unrecognized request structure fell through gatekeeper safety filters. BLOCKED by default.",
        "agent_status": agent_status,
        "timestamp": timestamp,
        "action": action,
        "amount": amount,
        "customer_id": c_id,
        "customer_name": c_name,
        "agent_id": a_id,
        "agent_name": a_name
    }

"""
Agent Gatekeeper - Testing Suite
JPMorgan Chase Bank | AI & Digital Transformation MBA Project
Student Enrolment Number: PGD202568904

Predefined Academic Test Cases:
TEST 1: Active registered agent requests account balance. Expected: ALLOW (R3)
TEST 2: Unknown agent requests account balance. Expected: BLOCK (R1)
TEST 3: Active registered agent requests bill payment of ₹10,000. Expected: ASK CUSTOMER (R5)
TEST 4: Active registered agent requests bill payment of ₹2,000. Expected: ALLOW (R4)
TEST 5: Previously registered but revoked agent requests money transfer. Expected: BLOCK (R2)
TEST 6: Active registered agent requests money transfer of ₹1,000. Expected: ASK CUSTOMER (R6)
"""

from datetime import datetime
from database import get_connection, init_db
from engine import evaluate_request

# Standard Test Fixture IDs
TEST_ACTIVE_AGENT_ID = "AGT-TEST-ACTIVE"
TEST_REVOKED_AGENT_ID = "AGT-TEST-REVOKED"
TEST_UNKNOWN_AGENT_ID = "AGT-TEST-UNKNOWN"


def ensure_test_fixtures():
    """
    Ensures that test fixtures (active agent and revoked agent) exist in the SQLite database
    so the 6 predefined academic test cases can execute reliably.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Active Test Agent
    cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (TEST_ACTIVE_AGENT_ID,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO agents (agent_id, agent_name, customer_id, customer_name, registration_date, status, revocation_timestamp, revocation_reason, created_at)
            VALUES (?, ?, ?, ?, ?, 'ACTIVE', NULL, NULL, ?)
        """, (TEST_ACTIVE_AGENT_ID, "Verified Financial Agent", "CUST-MBA-101", "Aarav Gupta", "2026-11-01", now_str))

    # 2. Revoked Test Agent
    cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (TEST_REVOKED_AGENT_ID,))
    existing_revoked = cursor.fetchone()
    if not existing_revoked:
        cursor.execute("""
            INSERT INTO agents (agent_id, agent_name, customer_id, customer_name, registration_date, status, revocation_timestamp, revocation_reason, created_at)
            VALUES (?, ?, ?, ?, ?, 'REVOKED', ?, ?, ?)
        """, (TEST_REVOKED_AGENT_ID, "Compromised Legacy Agent", "CUST-MBA-102", "Kavita Rao", "2026-10-15", "2026-11-08 11:45:00", "Security audit revocation: unauthorized policy deviation", now_str))
    elif existing_revoked["status"] != "REVOKED":
        cursor.execute("""
            UPDATE agents SET status = 'REVOKED', revocation_timestamp = ?, revocation_reason = ? WHERE agent_id = ?
        """, ("2026-11-08 11:45:00", "Security audit revocation: unauthorized policy deviation", TEST_REVOKED_AGENT_ID))

    # Ensure Unknown Agent is NOT in database
    cursor.execute("DELETE FROM agents WHERE agent_id = ?", (TEST_UNKNOWN_AGENT_ID,))

    conn.commit()
    conn.close()


# Predefined 6 Academic Test Cases Specification
PREDEFINED_TEST_CASES = [
    {
        "test_id": "TEST 1",
        "title": "Read-Only Balance Inquiry by Active Agent",
        "description": "Active registered agent requests account balance.",
        "expected_decision": "ALLOW",
        "expected_rule": "R3",
        "rule_title": "READ-ONLY ACCESS",
        "input": {
            "customer_id": "CUST-MBA-101",
            "customer_name": "Aarav Gupta",
            "agent_id": TEST_ACTIVE_AGENT_ID,
            "agent_name": "Verified Financial Agent",
            "banking_action": "View Account Balance",
            "transaction_amount": 0.0
        },
        "objective": "Verify autonomous read-only permission for active registered agents under Rule R3."
    },
    {
        "test_id": "TEST 2",
        "title": "Unregistered / Unknown Agent Request",
        "description": "Unknown agent requests account balance.",
        "expected_decision": "BLOCK",
        "expected_rule": "R1",
        "rule_title": "UNKNOWN AGENT",
        "input": {
            "customer_id": "CUST-MBA-999",
            "customer_name": "Unknown Customer",
            "agent_id": TEST_UNKNOWN_AGENT_ID,
            "agent_name": "Unregistered External Bot",
            "banking_action": "View Account Balance",
            "transaction_amount": 0.0
        },
        "objective": "Verify zero-trust security perimeter: external unregistered agents must be immediately blocked under Rule R1."
    },
    {
        "test_id": "TEST 3",
        "title": "High-Value Bill Payment Threshold Exceeded",
        "description": "Active registered agent requests a bill payment of ₹10,000.",
        "expected_decision": "ASK CUSTOMER",
        "expected_rule": "R5",
        "rule_title": "LARGE BILL PAYMENT",
        "input": {
            "customer_id": "CUST-MBA-101",
            "customer_name": "Aarav Gupta",
            "agent_id": TEST_ACTIVE_AGENT_ID,
            "agent_name": "Verified Financial Agent",
            "banking_action": "Pay a Bill",
            "transaction_amount": 10000.0
        },
        "objective": "Verify human-in-the-loop escalation: bill payments strictly above ₹5,000 require explicit customer consent under Rule R5."
    },
    {
        "test_id": "TEST 4",
        "title": "Autonomous Small Bill Payment Within Limit",
        "description": "Active registered agent requests a bill payment of ₹2,000.",
        "expected_decision": "ALLOW",
        "expected_rule": "R4",
        "rule_title": "SMALL BILL PAYMENT",
        "input": {
            "customer_id": "CUST-MBA-101",
            "customer_name": "Aarav Gupta",
            "agent_id": TEST_ACTIVE_AGENT_ID,
            "agent_name": "Verified Financial Agent",
            "banking_action": "Pay a Bill",
            "transaction_amount": 2000.0
        },
        "objective": "Verify frictionless automation: bill payments of ₹5,000 or less are autonomously authorized under Rule R4."
    },
    {
        "test_id": "TEST 5",
        "title": "Money Transfer by Revoked Agent",
        "description": "Previously registered but revoked agent requests a money transfer.",
        "expected_decision": "BLOCK",
        "expected_rule": "R2",
        "rule_title": "REVOKED AGENT",
        "input": {
            "customer_id": "CUST-MBA-102",
            "customer_name": "Kavita Rao",
            "agent_id": TEST_REVOKED_AGENT_ID,
            "agent_name": "Compromised Legacy Agent",
            "banking_action": "Transfer Money",
            "transaction_amount": 5000.0
        },
        "objective": "Verify permanent revocation enforcement: revoked agents are unconditionally blocked from any banking activity under Rule R2."
    },
    {
        "test_id": "TEST 6",
        "title": "Money Transfer Request Requiring Customer Confirmation",
        "description": "Active registered agent requests a money transfer of ₹1,000.",
        "expected_decision": "ASK CUSTOMER",
        "expected_rule": "R6",
        "rule_title": "MONEY TRANSFER",
        "input": {
            "customer_id": "CUST-MBA-101",
            "customer_name": "Aarav Gupta",
            "agent_id": TEST_ACTIVE_AGENT_ID,
            "agent_name": "Verified Financial Agent",
            "banking_action": "Transfer Money",
            "transaction_amount": 1000.0
        },
        "objective": "Verify mandatory human confirmation for high-risk outbound fund transfers regardless of amount under Rule R6."
    }
]


def run_test(test_case):
    """Executes a single test case against the Decision Engine and verifies result."""
    ensure_test_fixtures()
    inp = test_case["input"]
    result = evaluate_request(
        customer_id=inp["customer_id"],
        customer_name=inp["customer_name"],
        agent_id=inp["agent_id"],
        agent_name=inp["agent_name"],
        banking_action=inp["banking_action"],
        transaction_amount=inp["transaction_amount"]
    )

    decision_match = (result["decision"] == test_case["expected_decision"])
    rule_match = (result["rule_number"] == test_case["expected_rule"])
    passed = decision_match and rule_match

    return {
        "test_id": test_case["test_id"],
        "title": test_case["title"],
        "description": test_case["description"],
        "expected_decision": test_case["expected_decision"],
        "expected_rule": test_case["expected_rule"],
        "actual_decision": result["decision"],
        "actual_rule": result["rule_number"],
        "explanation": result["explanation"],
        "decision_match": decision_match,
        "rule_match": rule_match,
        "passed": passed,
        "timestamp": result["timestamp"]
    }


def run_all_tests():
    """Executes all 6 test cases sequentially and returns aggregate results."""
    ensure_test_fixtures()
    results = [run_test(tc) for tc in PREDEFINED_TEST_CASES]
    total_passed = sum(1 for r in results if r["passed"])
    return {
        "total": len(results),
        "passed": total_passed,
        "failed": len(results) - total_passed,
        "pass_rate": (total_passed / len(results)) * 100.0,
        "results": results
    }


if __name__ == "__main__":
    summary = run_all_tests()
    print(f"Executed {summary['total']} tests: {summary['passed']} PASSED, {summary['failed']} FAILED.")
    for r in summary["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['test_id']}: Expected {r['expected_decision']} ({r['expected_rule']}) -> Got {r['actual_decision']} ({r['actual_rule']})")

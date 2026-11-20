"""
Agent Gatekeeper - Database Management Module
JPMorgan Chase Bank | AI & Digital Transformation MBA Project
Student Enrolment Number: PGD202568904
"""

import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_gatekeeper.db")


def get_connection():
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite database schemas for agents, audit logs, and revocation logs."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Agents Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'REVOKED')),
            revocation_timestamp TEXT,
            revocation_reason TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # 2. Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            request_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            customer_id TEXT,
            customer_name TEXT,
            agent_id TEXT,
            agent_name TEXT,
            banking_action TEXT,
            transaction_amount REAL,
            decision TEXT NOT NULL CHECK(decision IN ('ALLOW', 'ASK CUSTOMER', 'BLOCK')),
            rule_number TEXT NOT NULL,
            explanation TEXT NOT NULL,
            customer_confirmation_status TEXT CHECK(customer_confirmation_status IN ('APPROVED', 'REJECTED', 'PENDING', 'N/A')),
            confirmation_timestamp TEXT
        )
    """)

    # 3. Revocation Events Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revocation_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            revocation_timestamp TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    """)

    conn.commit()

    # Seed sample baseline agents if table is empty
    cursor.execute("SELECT COUNT(*) FROM agents")
    if cursor.fetchone()[0] == 0:
        seed_sample_data(conn)

    conn.close()


def seed_sample_data(conn):
    """Populates initial sample banking agents and audit entries for realistic demonstration."""
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sample agents
    sample_agents = [
        ("AGT-101", "Chase AutoPay Agent", "CUST-9001", "Vikram Malhotra", "2026-10-15", "ACTIVE", None, None, now_str),
        ("AGT-102", "WealthFront Balance Watcher", "CUST-9002", "Priya Sharma", "2026-10-20", "ACTIVE", None, None, now_str),
        ("AGT-103", "Legacy Crypto Bot", "CUST-9003", "Rohan Mehta", "2026-09-01", "REVOKED", "2026-11-01 14:30:15", "Security policy violation - unapproved algorithm", now_str),
        ("AGT-104", "Utility Bill Scheduler", "CUST-9004", "Ananya Roy", "2026-11-05", "ACTIVE", None, None, now_str)
    ]

    cursor.executemany("""
        INSERT INTO agents (agent_id, agent_name, customer_id, customer_name, registration_date, status, revocation_timestamp, revocation_reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_agents)

    # Sample revocation entry for AGT-103
    cursor.execute("""
        INSERT INTO revocation_logs (agent_id, agent_name, customer_id, customer_name, revocation_timestamp, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("AGT-103", "Legacy Crypto Bot", "CUST-9003", "Rohan Mehta", "2026-11-01 14:30:15", "Security policy violation - unapproved algorithm"))

    # Initial historical audit log entries
    sample_logs = [
        ("REQ-20261110-001", "2026-11-10 10:15:30", "CUST-9001", "Vikram Malhotra", "AGT-101", "Chase AutoPay Agent", "View Account Balance", 0.0, "ALLOW", "R3", "Read-only access granted for balance inquiry.", "N/A", None),
        ("REQ-20261111-002", "2026-11-11 11:20:45", "CUST-9004", "Ananya Roy", "AGT-104", "Utility Bill Scheduler", "Pay a Bill", 2450.0, "ALLOW", "R4", "Bill payment of ₹2,450.00 is within autonomous threshold of ₹5,000.", "N/A", None),
        ("REQ-20261112-003", "2026-11-12 15:40:10", "CUST-9001", "Vikram Malhotra", "AGT-101", "Chase AutoPay Agent", "Pay a Bill", 12500.0, "ASK CUSTOMER", "R5", "Bill payment of ₹12,500.00 exceeds ₹5,000 threshold. Customer approval required.", "APPROVED", "2026-11-12 15:42:01"),
        ("REQ-20261113-004", "2026-11-13 09:05:22", "CUST-9999", "Unknown", "AGT-999", "Rogue Bot", "Transfer Money", 50000.0, "BLOCK", "R1", "Agent ID AGT-999 is not registered in the system.", "N/A", None),
        ("REQ-20261113-005", "2026-11-13 16:12:00", "CUST-9003", "Rohan Mehta", "AGT-103", "Legacy Crypto Bot", "Transfer Money", 5000.0, "BLOCK", "R2", "Agent AGT-103 is REVOKED. All banking transactions are permanently prohibited.", "N/A", None)
    ]

    cursor.executemany("""
        INSERT INTO audit_logs (request_id, timestamp, customer_id, customer_name, agent_id, agent_name, banking_action, transaction_amount, decision, rule_number, explanation, customer_confirmation_status, confirmation_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_logs)

    conn.commit()


def register_agent(customer_id, customer_name, agent_name, agent_id, registration_date):
    """
    Registers a new agent in SQLite.
    Prevents duplicate Agent IDs.
    Returns (success: bool, message: str)
    """
    agent_id = str(agent_id).strip()
    customer_id = str(customer_id).strip()
    customer_name = str(customer_name).strip()
    agent_name = str(agent_name).strip()
    registration_date = str(registration_date).strip()

    if not agent_id or not customer_id or not customer_name or not agent_name:
        return False, "All fields (Customer ID, Customer Name, Agent Name, Agent ID) are mandatory."

    conn = get_connection()
    cursor = conn.cursor()

    # Check for duplicate Agent ID
    cursor.execute("SELECT agent_id FROM agents WHERE agent_id = ?", (agent_id,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return False, f"Agent ID '{agent_id}' already exists in the system. Duplicate Agent IDs are strictly prohibited."

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO agents (agent_id, agent_name, customer_id, customer_name, registration_date, status, revocation_timestamp, revocation_reason, created_at)
        VALUES (?, ?, ?, ?, ?, 'ACTIVE', NULL, NULL, ?)
    """, (agent_id, agent_name, customer_id, customer_name, registration_date, now_str))

    conn.commit()
    conn.close()
    return True, f"Agent '{agent_name}' ({agent_id}) successfully registered for customer {customer_name} ({customer_id})."


def revoke_agent(agent_id, reason="Customer or Administrator Revocation"):
    """
    Revokes an agent permanently:
    - Changes status to REVOKED.
    - Saves exact revocation timestamp.
    - Stores revocation record permanently in revocation_logs.
    - Revoked agents can never perform transactions.
    Returns (success: bool, message: str)
    """
    agent_id = str(agent_id).strip()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
    agent = cursor.fetchone()
    if not agent:
        conn.close()
        return False, f"Agent ID '{agent_id}' not found."

    if agent["status"] == "REVOKED":
        conn.close()
        return False, f"Agent '{agent_id}' is already REVOKED on {agent['revocation_timestamp']}."

    exact_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update agent record
    cursor.execute("""
        UPDATE agents
        SET status = 'REVOKED', revocation_timestamp = ?, revocation_reason = ?
        WHERE agent_id = ?
    """, (exact_time, reason, agent_id))

    # Insert into revocation_logs
    cursor.execute("""
        INSERT INTO revocation_logs (agent_id, agent_name, customer_id, customer_name, revocation_timestamp, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (agent["agent_id"], agent["agent_name"], agent["customer_id"], agent["customer_name"], exact_time, reason))

    conn.commit()
    conn.close()
    return True, f"Agent '{agent['agent_name']}' ({agent_id}) successfully REVOKED at {exact_time}. All future transaction requests will be BLOCKED."


def get_agent(agent_id):
    """Retrieves an agent by ID as a dictionary, or None if not found."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (str(agent_id).strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_agents():
    """Returns all agents as a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM agents ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_revocation_logs():
    """Returns revocation audit logs as a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM revocation_logs ORDER BY revocation_timestamp DESC", conn)
    conn.close()
    return df


def log_request(request_id, timestamp, customer_id, customer_name, agent_id, agent_name,
                banking_action, transaction_amount, decision, rule_number, explanation,
                customer_confirmation_status="N/A", confirmation_timestamp=None):
    """Writes an audit log entry for every incoming agent evaluation request."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO audit_logs 
        (request_id, timestamp, customer_id, customer_name, agent_id, agent_name, banking_action, 
         transaction_amount, decision, rule_number, explanation, customer_confirmation_status, confirmation_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (request_id, timestamp, customer_id, customer_name, agent_id, agent_name,
          banking_action, transaction_amount, decision, rule_number, explanation,
          customer_confirmation_status, confirmation_timestamp))

    conn.commit()
    conn.close()


def update_customer_confirmation(request_id, confirmation_status):
    """
    Updates the customer confirmation status (APPROVED / REJECTED) 
    and sets the response timestamp.
    """
    exact_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE audit_logs
        SET customer_confirmation_status = ?, confirmation_timestamp = ?
        WHERE request_id = ?
    """, (confirmation_status, exact_time, request_id))

    conn.commit()
    conn.close()
    return exact_time


def get_audit_logs(decision_filter="ALL", agent_filter="ALL", search_term=""):
    """Fetches audit logs with multi-parameter filtering."""
    conn = get_connection()
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = []

    if decision_filter and decision_filter != "ALL":
        query += " AND decision = ?"
        params.append(decision_filter)

    if agent_filter and agent_filter != "ALL":
        query += " AND agent_id = ?"
        params.append(agent_filter)

    if search_term:
        term = f"%{search_term.strip()}%"
        query += " AND (request_id LIKE ? OR customer_id LIKE ? OR customer_name LIKE ? OR agent_name LIKE ? OR explanation LIKE ?)"
        params.extend([term, term, term, term, term])

    query += " ORDER BY timestamp DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_dashboard_metrics():
    """Computes real-time key metrics for the executive dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM audit_logs")
    total_requests = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE decision = 'ALLOW'")
    allowed_requests = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE decision = 'ASK CUSTOMER'")
    ask_customer_requests = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE decision = 'BLOCK'")
    blocked_requests = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM agents")
    registered_agents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'REVOKED'")
    revoked_agents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'ACTIVE'")
    active_agents = cursor.fetchone()[0]

    conn.close()

    return {
        "total_requests": total_requests,
        "allowed_requests": allowed_requests,
        "ask_customer_requests": ask_customer_requests,
        "blocked_requests": blocked_requests,
        "registered_agents": registered_agents,
        "active_agents": active_agents,
        "revoked_agents": revoked_agents
    }

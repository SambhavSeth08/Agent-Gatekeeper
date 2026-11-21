# Agent Gatekeeper: AI Agent Authorization and Risk Management System

**Academic Project for MBA in AI & Digital Transformation**  
- **Student Enrolment Number:** PGD202568904  
- **Target Organization:** JPMorgan Chase Bank  
- **Project Name:** Agent Gatekeeper  

---

## 1. Executive Summary & Objective

In modern digital banking ecosystems, customers increasingly leverage external autonomous AI agents (e.g., personal finance assistants, utility bill schedulers, budget optimizers) to interact with core banking services. 

Allowing unconstrained, autonomous agent execution introduces severe financial, operational, and regulatory risks (e.g., rogue bot executions, accidental large transfers, prompt injections, or unauthorized transactions).

**Agent Gatekeeper** is an enterprise-grade AI agent authorization firewall and risk management gateway engineered for **JPMorgan Chase Bank**. It intercepts inbound requests from external agents and determines whether the activity is:
1. **ALLOW**: Fully automated execution for low-risk, pre-authorized scenarios.
2. **ASK CUSTOMER**: Human-in-the-loop escalation requiring explicit customer consent before execution.
3. **BLOCK**: Unconditional rejection for unauthorized, revoked, or high-risk anomalous activities.

---

## 2. Technology Stack

- **Application Logic:** Python 3.11+
- **Web Interface:** Streamlit
- **Persistent Data Store:** SQLite (Zero external database overhead)
- **Data & Audit Processing:** Pandas
- **Visualization:** Plotly Express & Streamlit Native Telemetry
- **Timestamps & Audit:** Python `datetime`
- **Cost & Dependencies:** 100% free, locally executable, requiring zero external API keys or paid services.

---

## 3. Decision Engine & Rule Hierarchy

The Decision Engine enforces seven predefined authorization rules evaluated in a **strict priority sequence** to guarantee zero-trust deterministic safety:

```
+-----------------------------------------------------------------------+
|                       INBOUND AGENT REQUEST                           |
|       (Customer ID, Customer Name, Agent ID, Action, Amount)          |
+-----------------------------------------------------------------------+
                                   |
                                   v
             [ Priority 1: RULE R7 - Invalid Request? ]
             (Missing fields, negative amount, unsupported action)
                       /                        \
                    YES                          NO
                    /                              \
        ==> BLOCK (R7)                              v
                                [ Priority 2: RULE R1 - Unknown Agent? ]
                                (Agent not in database registry)
                                          /               \
                                       YES                 NO
                                       /                     \
                           ==> BLOCK (R1)                     v
                                         [ Priority 3: RULE R2 - Revoked Agent? ]
                                         (Agent status is REVOKED)
                                                   /              \
                                                YES                NO
                                                /                    \
                                    ==> BLOCK (R2)                    v
                                                   [ Priority 4: RULE R3 - Read-Only Access? ]
                                                   (Action == "View Account Balance")
                                                             /              \
                                                          YES                NO
                                                          /                    \
                                              ==> ALLOW (R3)                    v
                                                            [ Priority 5: RULE R4 - Small Bill Payment? ]
                                                            (Action == "Pay a Bill" and Amount <= 5,000)
                                                                      /              \
                                                                   YES                NO
                                                                   /                    \
                                                       ==> ALLOW (R4)                    v
                                                                     [ Priority 6: RULE R5 - Large Bill Payment? ]
                                                                     (Action == "Pay a Bill" and Amount > 5,000)
                                                                               /              \
                                                                            YES                NO
                                                                            /                    \
                                                                ==> ASK CUSTOMER (R5)             v
                                                                              [ Priority 7: RULE R6 - Money Transfer? ]
                                                                              (Action == "Transfer Money")
                                                                                        /
                                                                                     YES
                                                                                     /
                                                                         ==> ASK CUSTOMER (R6)
```

### Authorization Rules Summary Table

| Rule | Name | Condition | Decision | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **R7** | **Invalid Request** | Missing fields, negative amount, or unsupported action | **BLOCK** | Input hygiene and validation failure. |
| **R1** | **Unknown Agent** | Agent ID not registered in SQLite repository | **BLOCK** | Zero-trust: unregistered agents are untrusted. |
| **R2** | **Revoked Agent** | Agent previously revoked by customer/bank | **BLOCK** | Permanent exclusion: revoked agents cannot transact. |
| **R3** | **Read-Only Access** | Active agent requests "View Account Balance" | **ALLOW** | Zero financial outflow; non-destructive read. |
| **R4** | **Small Bill Payment**| Active agent requests bill payment $\le$ ₹5,000 | **ALLOW** | Low-risk automated routine utility bill settlement. |
| **R5** | **Large Bill Payment**| Active agent requests bill payment $>$ ₹5,000 | **ASK CUSTOMER**| Escalation: anomalous or high-value utility outflow. |
| **R6** | **Money Transfer** | Active agent requests "Transfer Money" | **ASK CUSTOMER**| Highest risk: irreversible third-party fund transfer. |

---

## 4. Key Application Modules

1. **Executive Banking Dashboard:**
   - Real-time KPI summary cards displaying Total Requests, Allowed Requests, Customer Confirmation Requests, Blocked Requests, Registered Agents, and Revoked Agents.
   - Interactive Plotly visualizations for Decision distribution (donut chart) and Banking Actions distribution (bar chart).
   - Recent transaction telemetry stream.

2. **Agent Registration:**
   - Form capturing Customer ID, Customer Name, Agent Name, Agent ID, and Registration Date.
   - Permanent storage in SQLite `agents` table.
   - Duplicate Agent ID prevention with instantaneous validation.

3. **Agent Management & Revocation:**
   - Real-time status display of all agents (ACTIVE vs. REVOKED).
   - 1-Click Revocation mechanism with mandatory reason recording.
   - Permanent audit recording in `revocation_logs` with exact revocation timestamp.
   - Irrevocable policy: revoked agents are permanently blocked.

4. **Request Simulator & Customer Confirmation:**
   - Interactive transaction dispatch form supporting quick-selection of active/revoked agents or manual testing of unknown agents.
   - Real-time decision display with color-coded badge, rule number, explanation, and timestamp.
   - Interactive **APPROVE** and **REJECT** buttons when decision is `ASK CUSTOMER`.
   - Records customer response and response timestamp in the audit log.

5. **Compliance Audit Log:**
   - Permanent SQLite log of all inbound requests.
   - Multi-parameter filtering: Full-text search, Filter by Decision, Filter by Agent ID.
   - 1-Click export to standard CSV format.

6. **Academic Testing Suite (6 Predefined Test Cases):**
   - Automated runner for all 6 predefined MBA evaluation test cases.
   - Visual test scorecard with Pass/Fail badges, rule verification, and detailed execution traces.

---

## 5. Predefined Test Cases & Results

| Test ID | Test Scenario | Expected Decision | Expected Rule | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TEST 1** | Active registered agent requests account balance | **ALLOW** | **R3** | ALLOW (R3) | **PASS** |
| **TEST 2** | Unknown agent requests account balance | **BLOCK** | **R1** | BLOCK (R1) | **PASS** |
| **TEST 3** | Active registered agent requests bill payment of ₹10,000 | **ASK CUSTOMER** | **R5** | ASK CUSTOMER (R5) | **PASS** |
| **TEST 4** | Active registered agent requests bill payment of ₹2,000 | **ALLOW** | **R4** | ALLOW (R4) | **PASS** |
| **TEST 5** | Previously registered but revoked agent requests money transfer | **BLOCK** | **R2** | BLOCK (R2) | **PASS** |
| **TEST 6** | Active registered agent requests money transfer of ₹1,000 | **ASK CUSTOMER** | **R6** | ASK CUSTOMER (R6) | **PASS** |

**Test Execution Summary: 6 / 6 Test Cases PASSED (100% Pass Rate).**

---

## 6. How to Run Locally

### Prerequisites
- Python 3.10 or 3.11 installed.

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Automated Test Suite (CLI)
```bash
python tests.py
```

### Step 3: Launch the Streamlit Web Application
```bash
streamlit run app.py
```

The web dashboard will launch at `http://localhost:8501`.
---

## 7. Live Demo

The Agent Gatekeeper prototype is deployed using Streamlit Community Cloud.

**Live Application:** https://agent-gatekeeper-ai.streamlit.app

Users can explore the dashboard, register AI agents, manage agent authorization, simulate banking requests, and review compliance audit logs.

**Note:** This is an academic prototype developed for demonstration purposes. It does not connect to actual JPMorgan Chase banking systems or process real financial transactions.

---

## 8. Testing and Verification

The Agent Gatekeeper prototype includes six test scenarios designed to evaluate AI agent authorization and banking request handling.

The testing covers:

1. Known active agent requesting balance information.
2. Unknown agent requesting banking information.
3. Payment exceeding the configured spending limit.
4. Payment within the configured spending limit.
5. Revoked agent attempting a banking request.
6. Money transfer authorization.

Test outcomes are documented in [TEST_RESULTS.md](TEST_RESULTS.md).

## 9. Project Limitations

- This is an academic prototype.
- It does not connect to actual JPMorgan Chase banking infrastructure.
- No real banking transactions or customer funds are processed.
- The authorization decisions demonstrate a proposed approach to AI agent governance and risk management.

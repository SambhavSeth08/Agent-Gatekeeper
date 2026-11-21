Agent Gatekeeper — Test Results
AI Agent Authorization and Risk Management System
	
Organization	JPMorgan Chase Bank
Programme	MBA in AI & Digital Transformation
Student Enrolment Number	PGD202568904
Technology Stack	Python, Streamlit, SQLite
GitHub Repository	https://github.com/SambhavSeth08/Agent-Gatekeeper

Live Application	https://agent-gatekeeper-ai.streamlit.app

Test Execution Date	22 November 2026
Overall Result	6 of 6 tests passed
Contents
1.	Testing Objective
2.	Testing Methodology
3.	Test Results Summary
4.	Detailed Test Cases
5.	Testing Observations
6.	Conclusion

1. Testing Objective
The objective is to verify that the Decision Engine (engine.py) returns the correct decision (ALLOW, ASK CUSTOMER or BLOCK) and cites the correct rule number for six representative requests made by external AI agents.
The tests cover the following behaviours:
•	Autonomous read-only access for an active, registered agent (R3)
•	Zero-trust blocking of an unregistered agent (R1)
•	Customer confirmation for bill payments above the spending limit (R5)
•	Autonomous approval of bill payments within the spending limit (R4)
•	Permanent blocking of a revoked agent (R2)
•	Customer confirmation for money transfers (R6)
1.1 Authorization Rules Implemented in the Source Code
Only the rules below exist in engine.py. They are evaluated in strict priority order, and the first matching rule determines the outcome.
Priority	Rule	Title	Condition	Decision
1	R7	Invalid Request	Missing mandatory field, negative or non-numeric amount, or unsupported banking action	BLOCK
2	R1	Unknown Agent	Agent ID is not registered in the agents table	BLOCK
3	R2	Revoked Agent	Agent status is REVOKED (any action, any amount)	BLOCK
4	R3	Read-Only Access	Active agent requests View Account Balance	ALLOW
5	R4	Small Bill Payment	Active agent requests Pay a Bill of ₹5,000 or less	ALLOW
6	R5	Large Bill Payment	Active agent requests Pay a Bill above ₹5,000	ASK CUSTOMER
7	R6	Money Transfer	Active agent requests Transfer Money (any amount)	ASK CUSTOMER
Supported banking actions (VALID_ACTIONS): View Account Balance, Pay a Bill, Transfer Money.
1.2 Configured Spending Limit
The limit is defined in engine.py:
python
BILL_PAYMENT_AUTONOMOUS_LIMIT = 5000.0  # ₹5,000 threshold
•	Bill payments of ₹5,000.00 or less are allowed autonomously (R4).
•	Bill payments above ₹5,000.00 require customer confirmation (R5).
•	The limit applies only to Pay a Bill. Money transfers (R6) require confirmation regardless of amount.
________________________________________
2. Testing Methodology
Approach: Black-box, rule-based functional testing of the Decision Engine using the six predefined test cases in tests.py (PREDEFINED_TEST_CASES).
2.1 Procedure
1.	ensure_test_fixtures() prepares three agent fixtures: 
o	AGT-TEST-ACTIVE: registered, status ACTIVE
o	AGT-TEST-REVOKED: registered, status REVOKED
o	AGT-TEST-UNKNOWN: guaranteed absent from the agents table
2.	Each test calls evaluate_request(...) with the inputs listed in Section 4.
3.	The returned decision and rule_number are compared with the expected values.
4.	A test is marked PASS only if both the decision and the rule number match.
5.	The suite was run with python tests.py and by calling run_all_tests().
2.2 Execution Environment
Item	Detail
Python version	3.12.3
Files tested	engine.py, database.py, tests.py (unmodified)
Database	Freshly created local SQLite database
Scope	Python modules executed directly
Not covered	The deployed Streamlit interface was not exercised in this run
2.3 Status Definitions
Status	Meaning
PASS	Executed; actual decision and rule matched the expected values
FAIL	Executed; actual decision or rule differed from the expected values
NOT VERIFIED	Not executed
3. Test Results Summary
Test ID	Scenario	Input Summary	Expected	Actual	Rule	Status
TEST 1	Active agent requests View Balance	View Account Balance, ₹0	ALLOW	ALLOW	R3	✅ PASS
TEST 2	Unknown agent requests View Balance	View Account Balance, ₹0	BLOCK	BLOCK	R1	✅ PASS
TEST 3	Payment above spending limit	Pay a Bill, ₹10,000	ASK CUSTOMER	ASK CUSTOMER	R5	✅ PASS
TEST 4	Payment below spending limit	Pay a Bill, ₹2,000	ALLOW	ALLOW	R4	✅ PASS
TEST 5	Revoked agent attempts a request	Transfer Money, ₹5,000	BLOCK	BLOCK	R2	✅ PASS
TEST 6	Additional request: Money Transfer	Transfer Money, ₹1,000	ASK CUSTOMER	ASK CUSTOMER	R6	✅ PASS
Metric	Value
Total tests executed	6
Passed	6
Failed	0
Not verified	0
Pass rate	100.0%
4. Detailed Test Cases
TEST 1: Known Active Agent Requests View Balance
Scenario: A registered agent with status ACTIVE requests to view an account balance.
Input
Parameter	Value
Customer ID	CUST-MBA-101
Customer Name	Aarav Gupta
Agent ID	AGT-TEST-ACTIVE
Agent Name	Verified Financial Agent
Banking Action	View Account Balance
Amount	₹0.00
Expected vs Actual
	Decision	Rule
Expected	ALLOW	R3 (Read-Only Access)
Actual	ALLOW	R3 (Read-Only Access)
Status: ✅ PASS (executed and verified)
Engine output: Active registered agent 'Verified Financial Agent' (AGT-TEST-ACTIVE) granted read-only access to view customer account balance.
Explanation: The request passes R7 validation, the agent exists (R1 not triggered) and is not revoked (R2 not triggered). R3 then allows read-only balance access.
________________________________________
TEST 2: Unknown Agent Requests View Balance
Scenario: An agent that is not registered in the system requests to view an account balance.
Input
Parameter	Value
Customer ID	CUST-MBA-999
Customer Name	Unknown Customer
Agent ID	AGT-TEST-UNKNOWN
Agent Name	Unregistered External Bot
Banking Action	View Account Balance
Amount	₹0.00
Expected vs Actual
	Decision	Rule
Expected	BLOCK	R1 (Unknown Agent)
Actual	BLOCK	R1 (Unknown Agent)
Status: ✅ PASS (executed and verified)
Engine output: Agent ID 'AGT-TEST-UNKNOWN' is not registered in the JPMorgan Chase Gatekeeper repository. Unrecognized external agents are untrusted and strictly BLOCKED.
Explanation: The input is valid (R7 not triggered), but the database lookup finds no record, so R1 blocks the request even though the action is read-only.
________________________________________
TEST 3: Payment Above the Spending Limit
Scenario: An active agent requests a bill payment of ₹10,000, which is above the ₹5,000 autonomous limit.
Input
Parameter	Value
Customer ID	CUST-MBA-101
Customer Name	Aarav Gupta
Agent ID	AGT-TEST-ACTIVE
Agent Name	Verified Financial Agent
Banking Action	Pay a Bill
Amount	₹10,000.00
Expected vs Actual
	Decision	Rule
Expected	ASK CUSTOMER	R5 (Large Bill Payment)
Actual	ASK CUSTOMER	R5 (Large Bill Payment)
Status: ✅ PASS (executed and verified)
Engine output: Bill payment of ₹10,000.00 exceeds the autonomous threshold of ₹5,000.00. Explicit customer confirmation is REQUIRED before proceeding.
Explanation: ₹10,000 is greater than BILL_PAYMENT_AUTONOMOUS_LIMIT (₹5,000), so R4 does not apply and R5 requires explicit customer confirmation.
________________________________________
TEST 4: Payment Below the Spending Limit
Scenario: An active agent requests a bill payment of ₹2,000, which is below the ₹5,000 autonomous limit.
Input
Parameter	Value
Customer ID	CUST-MBA-101
Customer Name	Aarav Gupta
Agent ID	AGT-TEST-ACTIVE
Agent Name	Verified Financial Agent
Banking Action	Pay a Bill
Amount	₹2,000.00
Expected vs Actual
	Decision	Rule
Expected	ALLOW	R4 (Small Bill Payment)
Actual	ALLOW	R4 (Small Bill Payment)
Status: ✅ PASS (executed and verified)
Engine output: Bill payment of ₹2,000.00 is within the pre-authorized autonomous threshold of ₹5,000.00. Request automatically ALLOWED.
Explanation: ₹2,000 is at or below the ₹5,000 limit, so R4 allows the payment without customer involvement.
________________________________________
TEST 5: Revoked Agent Attempts a Banking Request
Scenario: A previously registered agent that has since been revoked attempts a money transfer.
Input
Parameter	Value
Customer ID	CUST-MBA-102
Customer Name	Kavita Rao
Agent ID	AGT-TEST-REVOKED
Agent Name	Compromised Legacy Agent
Banking Action	Transfer Money
Amount	₹5,000.00
Expected vs Actual
	Decision	Rule
Expected	BLOCK	R2 (Revoked Agent)
Actual	BLOCK	R2 (Revoked Agent)
Status: ✅ PASS (executed and verified)
Engine output: Agent 'Compromised Legacy Agent' (AGT-TEST-REVOKED) was REVOKED on 2026-11-08 11:45:00 (Reason: Security audit revocation: unauthorized policy deviation). Revoked agents are permanently prohibited from executing any banking activities.
Explanation: The agent exists, so R1 is not triggered, but its status is REVOKED. R2 is evaluated before R6, so the transfer is blocked instead of being escalated to the customer.
________________________________________
TEST 6: Additional Request — Money Transfer
Scenario: An active agent requests a money transfer of ₹1,000.
Input
Parameter	Value
Customer ID	CUST-MBA-101
Customer Name	Aarav Gupta
Agent ID	AGT-TEST-ACTIVE
Agent Name	Verified Financial Agent
Banking Action	Transfer Money
Amount	₹1,000.00
Expected vs Actual
	Decision	Rule
Expected	ASK CUSTOMER	R6 (Money Transfer)
Actual	ASK CUSTOMER	R6 (Money Transfer)
Status: ✅ PASS (executed and verified)
Engine output: Money transfer request of ₹1,000.00 carries elevated risk of irrevocable fund outflow. Explicit customer confirmation is REQUIRED regardless of amount.
Explanation: Transfers are never autonomous. Although ₹1,000 is below ₹5,000, the bill-payment limit does not apply to transfers, so R6 requires customer confirmation.
________________________________________
5. Testing Observations
5.1 Verified by Execution
1.	All six predefined tests passed. The decision and rule number matched the expected values in every case.
2.	Rule priority behaved as specified. In TEST 5, a revoked agent requesting a money transfer was blocked under R2 and was not escalated under R6.
3.	The spending-limit boundary is inclusive. A direct check returned ALLOW (R4) for ₹5,000.00 and ASK CUSTOMER (R5) for ₹5,000.01.
4.	Explanations are rule-specific. They include the relevant amount, limit, revocation time and reason, which supports auditability.
5.2 Identified by Code Inspection (Not Tested)
5.	R7 is implemented but not exercised. Missing fields, negative amounts and unsupported actions are not covered by the six tests, so R7 is NOT VERIFIED in this cycle.
6.	No customer-to-agent ownership check. evaluate_request looks up the agent by Agent ID only and does not compare the request's Customer ID with the customer the agent is registered to. This is a potential enhancement.
7.	Test runs are not audit-logged. run_test() calls evaluate_request() directly and does not call log_request(). Requests submitted through the Streamlit simulator are logged.
8.	The system is a simulation. ASK CUSTOMER outcomes are recorded as PENDING, APPROVED or REJECTED, but no real banking transaction is executed.
9.	Fixtures write to the database. ensure_test_fixtures() inserts AGT-TEST-ACTIVE and AGT-TEST-REVOKED into the agents table, so they appear in the application's agent registry.
5.3 Limitations
•	Tests were run against the Python modules, not through the Streamlit interface or the live deployment.
•	The suite has one test per rule path for R1–R6 and none for R7 or the fail-safe fallback block in engine.py.
________________________________________
6. Conclusion
Executing the six predefined test cases against the Decision Engine produced 6 PASS, 0 FAIL and 0 NOT VERIFIED. The actual decisions and rule numbers matched the expected outcomes in every scenario.
For the scenarios tested, the results confirm that:
•	Active registered agents may view balances autonomously (R3).
•	Unregistered agents are blocked (R1), and revoked agents are blocked for any action (R2).
•	Bill payments of up to ₹5,000 are allowed autonomously (R4), while payments above ₹5,000 require customer confirmation (R5).
•	Money transfers require customer confirmation regardless of amount (R6).
Rule R7 and the customer-to-agent ownership check are not covered by this cycle. Adding test cases for them is the recommended next step to extend coverage.
________________________________________
Results reflect a test run on 22 November 2026 using Python 3.12.3 on the unmodified engine.py, database.py and tests.py.


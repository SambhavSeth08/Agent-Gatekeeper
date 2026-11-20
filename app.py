"""
Agent Gatekeeper - Main Streamlit Web Application
JPMorgan Chase Bank | AI & Digital Transformation MBA Project
Student Details:
- Enrolment Number: PGD202568904
- Company: JPMorgan Chase Bank
- Project Name: Agent Gatekeeper
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import uuid

# Internal modules
from database import (
    init_db,
    register_agent,
    revoke_agent,
    get_all_agents,
    get_agent,
    log_request,
    update_customer_confirmation,
    get_audit_logs,
    get_dashboard_metrics,
    get_revocation_logs
)
from engine import evaluate_request, VALID_ACTIONS
from tests import PREDEFINED_TEST_CASES, run_test, run_all_tests, ensure_test_fixtures

# Page Configuration
st.set_page_config(
    page_title="Agent Gatekeeper | JPMorgan Chase Bank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schemas and test fixtures
init_db()
ensure_test_fixtures()

# -----------------------------------------------------------------------------
# Custom Styling - JPMorgan Chase Corporate Aesthetic
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Fonts & Theme */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Header Banner */
    .jpm-header-banner {
        background: linear-gradient(135deg, #0A2540 0%, #002D62 50%, #004B87 100%);
        color: #FFFFFF;
        padding: 24px 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(10, 37, 64, 0.15);
        border-left: 6px solid #FFB81C;
    }
    .jpm-header-banner h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #FFFFFF;
    }
    .jpm-header-banner p {
        margin: 6px 0 0 0;
        font-size: 14px;
        color: #D1E3F8;
    }
    .student-badge-container {
        margin-top: 12px;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .student-badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
        color: #FFFFFF;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
    .gold-badge {
        background: #FFB81C;
        color: #0A2540 !important;
        font-weight: 700;
    }

    /* KPI Metric Cards */
    .metric-card {
        background: #FFFFFF;
        padding: 18px 20px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    }
    .metric-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #0A2540;
        margin-bottom: 2px;
    }
    .metric-sub {
        font-size: 11px;
        color: #94A3B8;
    }

    /* Decision Badges */
    .decision-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 0.4px;
    }
    .pill-allow {
        background-color: #E6F4EA;
        color: #137333;
        border: 1px solid #A8DAB5;
    }
    .pill-ask {
        background-color: #FEF7E0;
        color: #B06000;
        border: 1px solid #FDD663;
    }
    .pill-block {
        background-color: #FCE8E6;
        color: #C5221F;
        border: 1px solid #F5A39D;
    }
    
    /* Status Badges */
    .status-active {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid #C8E6C9;
    }
    .status-revoked {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid #FFCDD2;
    }

    /* Decision Box in Simulator */
    .decision-box {
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .box-allow {
        background-color: #F0FDF4;
        border-left: 6px solid #16A34A;
        border: 1px solid #BBF7D0;
        border-left-width: 6px;
    }
    .box-ask {
        background-color: #FFFBEB;
        border-left: 6px solid #D97706;
        border: 1px solid #FDE68A;
        border-left-width: 6px;
    }
    .box-block {
        background-color: #FEF2F2;
        border-left: 6px solid #DC2626;
        border: 1px solid #FECACA;
        border-left-width: 6px;
    }

    /* Section Subtitle */
    .section-desc {
        color: #475569;
        font-size: 14px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Corporate Header Banner
# -----------------------------------------------------------------------------
st.markdown("""
<div class="jpm-header-banner">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
            <h1>JPMorgan Chase Bank &bull; Agent Gatekeeper</h1>
            <p>AI Agent Authorization and Risk Management System | Autonomous Financial Guardrails</p>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 12px; opacity: 0.85;">Security Level: TIER-1 BANKING ENGINE</span><br>
            <span style="font-size: 11px; color: #93C5FD;">Evaluation Mode: Strict Priority Deterministic</span>
        </div>
    </div>
    <div class="student-badge-container">
        <span class="student-badge gold-badge">MBA PROJECT: AI & DIGITAL TRANSFORMATION</span>
        <span class="student-badge">COMPANY: JPMorgan Chase Bank</span>
        <span class="student-badge">PROJECT: Agent Gatekeeper</span>
        <span class="student-badge">ENROLMENT NO: PGD202568904</span>
        <span class="student-badge">STORAGE: Persistent SQLite</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Navigation Tabs
# -----------------------------------------------------------------------------
tab_dashboard, tab_registration, tab_management, tab_simulator, tab_audit, tab_testing = st.tabs([
    "📊 Application Dashboard",
    "📝 Agent Registration",
    "🛡️ Agent Management & Revocation",
    "⚡ Request Simulator",
    "📋 Compliance Audit Log",
    "🧪 Test Cases & Verification"
])

# =============================================================================
# TAB 1: APPLICATION DASHBOARD (Section 3)
# =============================================================================
with tab_dashboard:
    st.subheader("Executive Banking Overview")
    st.markdown('<p class="section-desc">Real-time telemetry and risk distribution of external AI agent transactions.</p>', unsafe_allow_html=True)

    metrics = get_dashboard_metrics()

    # Metric Row 1: Request Decisions
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #0A2540;">
            <div class="metric-title">Total Requests Received</div>
            <div class="metric-value">{metrics['total_requests']}</div>
            <div class="metric-sub">Processed through Gatekeeper</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #16A34A;">
            <div class="metric-title">Allowed Requests</div>
            <div class="metric-value" style="color: #16A34A;">{metrics['allowed_requests']}</div>
            <div class="metric-sub">Autonomously approved (R3, R4)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #D97706;">
            <div class="metric-title">Customer Confirmation</div>
            <div class="metric-value" style="color: #D97706;">{metrics['ask_customer_requests']}</div>
            <div class="metric-sub">Human-in-the-loop (R5, R6)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #DC2626;">
            <div class="metric-title">Blocked Requests</div>
            <div class="metric-value" style="color: #DC2626;">{metrics['blocked_requests']}</div>
            <div class="metric-sub">Policy violations (R1, R2, R7)</div>
        </div>
        """, unsafe_allow_html=True)

    # Metric Row 2: Agent Registry
    col_ag1, col_ag2, col_ag3 = st.columns(3)
    with col_ag1:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #0284C7;">
            <div class="metric-title">Total Registered Agents</div>
            <div class="metric-value">{metrics['registered_agents']}</div>
            <div class="metric-sub">In permanent SQLite registry</div>
        </div>
        """, unsafe_allow_html=True)
    with col_ag2:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #059669;">
            <div class="metric-title">Active Authorized Agents</div>
            <div class="metric-value" style="color: #059669;">{metrics['active_agents']}</div>
            <div class="metric-sub">Currently permitted to transact</div>
        </div>
        """, unsafe_allow_html=True)
    with col_ag3:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #E11D48;">
            <div class="metric-title">Revoked Agents</div>
            <div class="metric-value" style="color: #E11D48;">{metrics['revoked_agents']}</div>
            <div class="metric-sub">Permanently prohibited</div>
        </div>
        """, unsafe_allow_html=True)

    # Visual Analytics: Charts
    st.markdown("### Decision & Action Distribution")
    chart_col1, chart_col2 = st.columns(2)

    df_logs = get_audit_logs()

    with chart_col1:
        if not df_logs.empty and metrics['total_requests'] > 0:
            decision_counts = df_logs['decision'].value_counts().reset_index()
            decision_counts.columns = ['Decision', 'Count']
            color_map = {
                'ALLOW': '#16A34A',
                'ASK CUSTOMER': '#D97706',
                'BLOCK': '#DC2626'
            }
            fig_pie = px.pie(
                decision_counts,
                names='Decision',
                values='Count',
                title="Requests by Authorization Decision",
                color='Decision',
                color_discrete_map=color_map,
                hole=0.45
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=320)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No audit logs available to display decision chart.")

    with chart_col2:
        if not df_logs.empty and metrics['total_requests'] > 0:
            action_counts = df_logs['banking_action'].value_counts().reset_index()
            action_counts.columns = ['Action', 'Count']
            fig_bar = px.bar(
                action_counts,
                x='Action',
                y='Count',
                title="Requests by Banking Action",
                color='Action',
                color_discrete_sequence=['#0A2540', '#004B87', '#0284C7']
            )
            fig_bar.update_layout(margin=dict(t=40, b=20, l=20, r=20), height=320, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No audit logs available to display action chart.")

    # Recent Activity Feed
    st.markdown("### Recent Evaluation Telemetry")
    if not df_logs.empty:
        display_cols = ['request_id', 'timestamp', 'customer_name', 'agent_name', 'banking_action', 'transaction_amount', 'decision', 'rule_number']
        recent_df = df_logs[display_cols].head(5).copy()
        recent_df['transaction_amount'] = recent_df['transaction_amount'].apply(lambda x: f"₹{x:,.2f}" if pd.notnull(x) else "₹0.00")
        recent_df.rename(columns={
            'request_id': 'Request ID',
            'timestamp': 'Timestamp',
            'customer_name': 'Customer',
            'agent_name': 'Agent',
            'banking_action': 'Action',
            'transaction_amount': 'Amount',
            'decision': 'Decision',
            'rule_number': 'Rule'
        }, inplace=True)
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.write("No requests logged yet.")

# =============================================================================
# TAB 2: AGENT REGISTRATION (Section 4)
# =============================================================================
with tab_registration:
    st.subheader("Register New Customer AI Agent")
    st.markdown('<p class="section-desc">Enroll authorized external AI agents into the JPMorgan Chase Gatekeeper repository. Each Agent ID must be globally unique.</p>', unsafe_allow_html=True)

    with st.form("agent_registration_form", clear_on_submit=True):
        col_reg1, col_reg2 = st.columns(2)
        with col_reg1:
            reg_customer_id = st.text_input("Customer ID *", placeholder="e.g., CUST-1008", help="Unique identifier for the bank customer.")
            reg_customer_name = st.text_input("Customer Name *", placeholder="e.g., Neha Kapur", help="Full legal name of the account holder.")
            reg_date = st.date_input("Registration Date *", value=date.today())

        with col_reg2:
            reg_agent_id = st.text_input("Agent ID *", placeholder="e.g., AGT-301", help="Unique alphanumeric identifier for the external AI agent. Duplicate IDs are rejected.")
            reg_agent_name = st.text_input("Agent Name *", placeholder="e.g., Mint Portfolio Optimizer", help="Descriptive name of the third-party AI assistant.")

        st.markdown("<small style='color: #64748B;'>* All fields are required. Registered agents will immediately have ACTIVE status.</small>", unsafe_allow_html=True)
        submit_reg = st.form_submit_button("Register Agent", use_container_width=True)

        if submit_reg:
            success, message = register_agent(
                customer_id=reg_customer_id,
                customer_name=reg_customer_name,
                agent_name=reg_agent_name,
                agent_id=reg_agent_id,
                registration_date=reg_date.strftime("%Y-%m-%d")
            )
            if success:
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ Registration Failed: {message}")

    # Display Current Agents Reference Table
    st.markdown("### Currently Registered Agents")
    df_all_agents = get_all_agents()
    if not df_all_agents.empty:
        summary_view = df_all_agents[['agent_id', 'agent_name', 'customer_id', 'customer_name', 'registration_date', 'status']].copy()
        summary_view.rename(columns={
            'agent_id': 'Agent ID',
            'agent_name': 'Agent Name',
            'customer_id': 'Customer ID',
            'customer_name': 'Customer Name',
            'registration_date': 'Registered On',
            'status': 'Status'
        }, inplace=True)
        st.dataframe(summary_view, use_container_width=True, hide_index=True)
    else:
        st.info("No agents currently registered.")

# =============================================================================
# TAB 3: AGENT MANAGEMENT AND REVOCATION (Section 5)
# =============================================================================
with tab_management:
    st.subheader("Agent Management & Security Revocation")
    st.markdown('<p class="section-desc">Manage existing agents and execute immediate security revocations. Revocation is permanent: once revoked, all future transactions by that agent are strictly BLOCKED.</p>', unsafe_allow_html=True)

    df_agents = get_all_agents()

    # Active Agent Revocation Section
    st.markdown("#### Revoke an Agent")
    active_agents_df = df_agents[df_agents['status'] == 'ACTIVE']

    if not active_agents_df.empty:
        agent_options = {
            f"{row['agent_name']} ({row['agent_id']}) - Customer: {row['customer_name']}": row['agent_id']
            for _, row in active_agents_df.iterrows()
        }
        
        with st.container():
            col_rev1, col_rev2 = st.columns([3, 2])
            with col_rev1:
                selected_label = st.selectbox("Select Active Agent to Revoke", list(agent_options.keys()))
                rev_reason = st.text_input("Revocation Reason", value="Customer authorization withdrawal / Security policy update")
            with col_rev2:
                st.write("")
                st.write("")
                if st.button("🚨 REVOKE AGENT", type="primary", use_container_width=True):
                    agent_id_to_revoke = agent_options[selected_label]
                    success, msg = revoke_agent(agent_id_to_revoke, reason=rev_reason)
                    if success:
                        st.success(f"🔒 {msg}")
                        st.rerun()
                    else:
                        st.error(f"Error: {msg}")
    else:
        st.info("No active agents available to revoke. All registered agents are currently revoked or no agents exist.")

    st.divider()

    # Agent Management Table
    st.markdown("#### Agent Status & Audit Records")
    if not df_agents.empty:
        table_view = df_agents[['customer_name', 'agent_name', 'agent_id', 'registration_date', 'status', 'revocation_timestamp', 'revocation_reason']].copy()
        table_view['revocation_timestamp'] = table_view['revocation_timestamp'].fillna("N/A (Active)")
        table_view['revocation_reason'] = table_view['revocation_reason'].fillna("N/A")
        table_view.rename(columns={
            'customer_name': 'Customer Name',
            'agent_name': 'Agent Name',
            'agent_id': 'Agent ID',
            'registration_date': 'Registration Date',
            'status': 'Current Status',
            'revocation_timestamp': 'Revocation Timestamp',
            'revocation_reason': 'Reason'
        }, inplace=True)
        st.dataframe(table_view, use_container_width=True, hide_index=True)
    else:
        st.write("No agents registered.")

    # Permanent Revocation Audit Log
    with st.expander("📜 Permanent Revocation Audit Trail (Historical Log)"):
        df_rev_logs = get_revocation_logs()
        if not df_rev_logs.empty:
            df_rev_display = df_rev_logs.copy()
            df_rev_display.rename(columns={
                'log_id': 'Log ID',
                'agent_id': 'Agent ID',
                'agent_name': 'Agent Name',
                'customer_id': 'Customer ID',
                'customer_name': 'Customer Name',
                'revocation_timestamp': 'Revocation Timestamp',
                'reason': 'Reason'
            }, inplace=True)
            st.dataframe(df_rev_display, use_container_width=True, hide_index=True)
        else:
            st.write("No revocation events logged yet.")

# =============================================================================
# TAB 4: REQUEST SIMULATOR & CUSTOMER CONFIRMATION (Sections 6, 7 & 8)
# =============================================================================
with tab_simulator:
    st.subheader("External AI Agent Request Simulator")
    st.markdown('<p class="section-desc">Simulate inbound transaction requests from customer AI agents and trigger the Gatekeeper Rule Engine in real time.</p>', unsafe_allow_html=True)

    # Session state for simulator results and pending customer confirmations
    if "latest_eval" not in st.session_state:
        st.session_state.latest_eval = None
    if "confirmation_status" not in st.session_state:
        st.session_state.confirmation_status = None

    # Option to autofill from registered agents or test arbitrary agent
    df_agents = get_all_agents()
    fill_mode = st.radio("Agent Selection Mode", ["Select Existing Agent (Active or Revoked)", "Manual Input (Test Unknown or Custom Agent)"], horizontal=True)

    default_cust_id = ""
    default_cust_name = ""
    default_agent_id = ""
    default_agent_name = ""

    if fill_mode == "Select Existing Agent (Active or Revoked)" and not df_agents.empty:
        agent_dict = {
            f"[{row['status']}] {row['agent_name']} ({row['agent_id']}) - Customer: {row['customer_name']}": row
            for _, row in df_agents.iterrows()
        }
        chosen_agent_label = st.selectbox("Choose Registered Agent", list(agent_dict.keys()))
        chosen_row = agent_dict[chosen_agent_label]
        default_cust_id = chosen_row['customer_id']
        default_cust_name = chosen_row['customer_name']
        default_agent_id = chosen_row['agent_id']
        default_agent_name = chosen_row['agent_name']

    # Simulator Form
    with st.form("request_simulator_form"):
        col_sim1, col_sim2 = st.columns(2)
        with col_sim1:
            sim_cust_id = st.text_input("Customer ID *", value=default_cust_id, placeholder="e.g., CUST-9001")
            sim_cust_name = st.text_input("Customer Name *", value=default_cust_name, placeholder="e.g., Vikram Malhotra")
            sim_action = st.selectbox("Banking Action *", VALID_ACTIONS, help="Available actions: View Account Balance, Pay a Bill, Transfer Money.")

        with col_sim2:
            sim_agent_id = st.text_input("Agent ID *", value=default_agent_id, placeholder="e.g., AGT-101")
            sim_agent_name = st.text_input("Agent Name *", value=default_agent_name, placeholder="e.g., Chase AutoPay Agent")
            sim_amount = st.number_input("Transaction Amount (INR) *", min_value=0.0, value=0.0 if sim_action == "View Account Balance" else 2500.0, step=100.0, format="%.2f")

        submit_sim = st.form_submit_button("SUBMIT REQUEST", type="primary", use_container_width=True)

        if submit_sim:
            # Generate Unique Request ID
            req_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
            
            # Evaluate through Gatekeeper Decision Engine
            eval_result = evaluate_request(
                customer_id=sim_cust_id,
                customer_name=sim_cust_name,
                agent_id=sim_agent_id,
                agent_name=sim_agent_name,
                banking_action=sim_action,
                transaction_amount=sim_amount
            )
            eval_result["request_id"] = req_id

            # Initial confirmation status
            init_conf_status = "PENDING" if eval_result["decision"] == "ASK CUSTOMER" else "N/A"

            # Log to permanent SQLite audit trail
            log_request(
                request_id=req_id,
                timestamp=eval_result["timestamp"],
                customer_id=sim_cust_id,
                customer_name=sim_cust_name,
                agent_id=sim_agent_id,
                agent_name=sim_agent_name,
                banking_action=sim_action,
                transaction_amount=sim_amount,
                decision=eval_result["decision"],
                rule_number=eval_result["rule_number"],
                explanation=eval_result["explanation"],
                customer_confirmation_status=init_conf_status,
                confirmation_timestamp=None
            )

            st.session_state.latest_eval = eval_result
            st.session_state.confirmation_status = init_conf_status

    # =========================================================================
    # DISPLAY DECISION ENGINE RESULT (Section 7)
    # =========================================================================
    if st.session_state.latest_eval:
        res = st.session_state.latest_eval
        dec = res["decision"]
        box_class = "box-allow" if dec == "ALLOW" else ("box-ask" if dec == "ASK CUSTOMER" else "box-block")
        pill_class = "pill-allow" if dec == "ALLOW" else ("pill-ask" if dec == "ASK CUSTOMER" else "pill-block")

        st.markdown(f"""
        <div class="decision-box {box_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div>
                    <span class="decision-pill {pill_class}">DECISION: {dec}</span>
                    <span style="margin-left: 10px; font-weight: 700; color: #0A2540;">RULE {res['rule_number']}: {res['rule_title']}</span>
                </div>
                <div style="font-size: 12px; color: #64748B;">
                    <strong>Timestamp:</strong> {res['timestamp']} | <strong>Request ID:</strong> {res['request_id']}
                </div>
            </div>
            <p style="margin: 8px 0; font-size: 15px; color: #1E293B;"><strong>Explanation:</strong> {res['explanation']}</p>
            <div style="font-size: 12px; color: #64748B; margin-top: 8px;">
                Customer: <strong>{res['customer_name']}</strong> ({res['customer_id']}) &bull; 
                Agent: <strong>{res['agent_name']}</strong> ({res['agent_id']}) &bull; 
                Action: <strong>{res['action']}</strong> &bull; 
                Amount: <strong>₹{res['amount']:,.2f}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # =====================================================================
        # CUSTOMER CONFIRMATION SECTION (Section 8)
        # =====================================================================
        if dec == "ASK CUSTOMER":
            st.markdown("### 🔔 Customer Confirmation Required")
            st.info(f"**Action Required**: Agent **{res['agent_name']}** requests permission to execute **{res['action']}** for amount **₹{res['amount']:,.2f}** on behalf of **{res['customer_name']}**.")

            if st.session_state.confirmation_status == "PENDING":
                col_btn1, col_btn2, col_space = st.columns([1.5, 1.5, 3])
                with col_btn1:
                    if st.button("✅ APPROVE", type="primary", use_container_width=True):
                        conf_time = update_customer_confirmation(res["request_id"], "APPROVED")
                        st.session_state.confirmation_status = "APPROVED"
                        st.session_state.confirmation_time = conf_time
                        st.rerun()
                with col_btn2:
                    if st.button("❌ REJECT", use_container_width=True):
                        conf_time = update_customer_confirmation(res["request_id"], "REJECTED")
                        st.session_state.confirmation_status = "REJECTED"
                        st.session_state.confirmation_time = conf_time
                        st.rerun()
            else:
                conf_color = "#16A34A" if st.session_state.confirmation_status == "APPROVED" else "#DC2626"
                st.markdown(f"""
                <div style="padding: 12px 16px; background-color: #F8FAFC; border-radius: 8px; border: 1px solid #CBD5E1; margin-top: 10px;">
                    <strong>Customer Response Recorded:</strong> 
                    <span style="color: {conf_color}; font-weight: 700;">{st.session_state.confirmation_status}</span>
                    <span style="color: #64748B; font-size: 12px; margin-left: 10px;">(Logged at {st.session_state.get('confirmation_time', 'Recently')})</span>
                    <br><small style="color: #94A3B8;">Notice: Authorization simulation only. No actual banking transactions or fund transfers were executed.</small>
                </div>
                """, unsafe_allow_html=True)

# =============================================================================
# TAB 5: AUDIT LOG (Section 9)
# =============================================================================
with tab_audit:
    st.subheader("Permanent Regulatory Audit Log")
    st.markdown('<p class="section-desc">Search, filter and export the permanent compliance audit repository stored in SQLite.</p>', unsafe_allow_html=True)

    # Filter Toolbar
    f_col1, f_col2, f_col3 = st.columns([2, 1.5, 1.5])
    with f_col1:
        search_kw = st.text_input("🔍 Search Logs", placeholder="Search Request ID, Customer, Agent, or Rule explanation...")
    with f_col2:
        decision_filter = st.selectbox("Filter by Decision", ["ALL", "ALLOW", "ASK CUSTOMER", "BLOCK"])
    with f_col3:
        all_agents_list = get_all_agents()
        agent_opts = ["ALL"] + (all_agents_list['agent_id'].tolist() if not all_agents_list.empty else [])
        agent_filter = st.selectbox("Filter by Agent ID", agent_opts)

    # Fetch Filtered Logs
    df_filtered_logs = get_audit_logs(
        decision_filter=decision_filter,
        agent_filter=agent_filter,
        search_term=search_kw
    )

    # Export to CSV Button
    if not df_filtered_logs.empty:
        csv_data = df_filtered_logs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Audit Records as CSV",
            data=csv_data,
            file_name=f"JPMorgan_Agent_Gatekeeper_Audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=False
        )

        # Prettify table for presentation
        df_display = df_filtered_logs.copy()
        df_display['transaction_amount'] = df_display['transaction_amount'].apply(lambda x: f"₹{x:,.2f}" if pd.notnull(x) else "₹0.00")
        df_display['confirmation_timestamp'] = df_display['confirmation_timestamp'].fillna("N/A")
        df_display.rename(columns={
            'request_id': 'Request ID',
            'timestamp': 'Date & Time',
            'customer_id': 'Customer ID',
            'customer_name': 'Customer Name',
            'agent_id': 'Agent ID',
            'agent_name': 'Agent Name',
            'banking_action': 'Banking Action',
            'transaction_amount': 'Amount',
            'decision': 'Decision',
            'rule_number': 'Rule',
            'explanation': 'Explanation',
            'customer_confirmation_status': 'Customer Confirmation',
            'confirmation_timestamp': 'Confirmation Timestamp'
        }, inplace=True)

        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(df_display)} audit log entries.")
    else:
        st.info("No matching audit records found.")

# =============================================================================
# TAB 6: TESTING SECTION (Section 10)
# =============================================================================
with tab_testing:
    st.subheader("Academic Predefined Test Suite (6 Predefined Test Cases)")
    st.markdown("""
    <p class="section-desc">
    Automated regression and rule verification suite for the 6 MBA evaluation test cases.
    Click <strong>Run All Tests</strong> to verify the Decision Engine against all expected outcomes and rule numbers.
    </p>
    """, unsafe_allow_html=True)

    test_col1, test_col2 = st.columns([2, 4])
    with test_col1:
        run_all_clicked = st.button("▶️ RUN ALL PREDEFINED TESTS", type="primary", use_container_width=True)

    if "test_results" not in st.session_state:
        st.session_state.test_results = None

    if run_all_clicked:
        st.session_state.test_results = run_all_tests()

    if st.session_state.test_results:
        res_summary = st.session_state.test_results
        
        # Summary Scorecard
        score_c1, score_c2, score_c3, score_c4 = st.columns(4)
        with score_c1:
            st.metric("Total Tests", res_summary["total"])
        with score_c2:
            st.metric("Passed", res_summary["passed"], delta="100%" if res_summary["failed"] == 0 else None)
        with score_c3:
            st.metric("Failed", res_summary["failed"])
        with score_c4:
            st.metric("Pass Rate", f"{res_summary['pass_rate']:.1f}%")

        st.divider()

    # Detailed Test Cases Display
    st.markdown("### Predefined Test Case Specifications & Results")

    for tc in PREDEFINED_TEST_CASES:
        t_id = tc["test_id"]
        inp = tc["input"]

        # Run individual test if requested
        with st.container():
            st.markdown(f"#### {t_id}: {tc['title']}")
            st.markdown(f"**Scenario:** {tc['description']}")
            st.markdown(f"<small style='color: #64748B;'><strong>Academic Objective:</strong> {tc['objective']}</small>", unsafe_allow_html=True)

            c_spec1, c_spec2 = st.columns([3, 2])
            with c_spec1:
                st.write(f"- **Customer:** {inp['customer_name']} (`{inp['customer_id']}`)")
                st.write(f"- **Agent:** {inp['agent_name']} (`{inp['agent_id']}`)")
                st.write(f"- **Banking Action:** `{inp['banking_action']}` &bull; **Amount:** ₹{inp['transaction_amount']:,.2f}")
            with c_spec2:
                st.write(f"- **Expected Decision:** `{tc['expected_decision']}`")
                st.write(f"- **Expected Rule:** `{tc['expected_rule']}` ({tc['rule_title']})")

            # Execute single test button
            if st.button(f"Run {t_id}", key=f"btn_{t_id}"):
                single_res = run_test(tc)
                if "individual_runs" not in st.session_state:
                    st.session_state.individual_runs = {}
                st.session_state.individual_runs[t_id] = single_res

            # Display result if available in batch or individual run
            display_res = None
            if st.session_state.test_results:
                for r in st.session_state.test_results["results"]:
                    if r["test_id"] == t_id:
                        display_res = r
                        break
            elif "individual_runs" in st.session_state and t_id in st.session_state.individual_runs:
                display_res = st.session_state.individual_runs[t_id]

            if display_res:
                if display_res["passed"]:
                    st.success(f"✅ **PASS** | Got: **{display_res['actual_decision']}** under Rule **{display_res['actual_rule']}** | *Explanation:* {display_res['explanation']}")
                else:
                    st.error(f"❌ **FAIL** | Expected {tc['expected_decision']} ({tc['expected_rule']}) but got {display_res['actual_decision']} ({display_res['actual_rule']}) | *Explanation:* {display_res['explanation']}")

            st.markdown("<hr style='margin: 15px 0; border: 0.5px solid #E2E8F0;'>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Corporate Footer
# -----------------------------------------------------------------------------
st.markdown("""
<div style="margin-top: 40px; padding: 20px; text-align: center; border-top: 1px solid #E2E8F0; color: #64748B; font-size: 12px;">
    <strong>JPMorgan Chase Bank &bull; Agent Gatekeeper System</strong><br>
    MBA in AI & Digital Transformation | Student Enrolment Number: <strong>PGD202568904</strong><br>
    Deterministic Risk Management & Human-In-The-Loop AI Authorization Simulator &bull; Local SQLite Implementation
</div>
""", unsafe_allow_html=True)

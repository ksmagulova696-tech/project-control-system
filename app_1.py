import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib

st.set_page_config(
    page_title="Blockchain Project Control",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL CSS — LIGHT THEME
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

.stApp { background: #f6f8fa; color: #1c2128; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 1400px; }

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #d0d7de !important;
}
[data-testid="stSidebar"] * { color: #1c2128 !important; }

input[type="text"], .stTextInput input, .stSelectbox select {
    background: #ffffff !important;
    border: 1px solid #d0d7de !important;
    border-radius: 6px !important;
    color: #1c2128 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 13px !important;
}
input[type="text"]:focus, .stTextInput input:focus {
    border-color: #0969da !important;
    box-shadow: 0 0 0 2px rgba(9,105,218,0.12) !important;
}

.stButton > button {
    background: #ffffff !important;
    color: #1c2128 !important;
    border: 1px solid #d0d7de !important;
    border-radius: 6px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 6px 14px !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    border-color: #0969da !important;
    color: #0969da !important;
    background: rgba(9,105,218,0.05) !important;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #1a7f37, #0969da) !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background: #e6edf3 !important;
    border-radius: 4px !important;
    height: 8px !important;
}

[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1px solid #d0d7de !important;
    border-radius: 6px !important;
    color: #1c2128 !important;
}

[data-testid="stDataFrame"] { border-radius: 8px !important; overflow: hidden; }

.stSuccess { background: rgba(26,127,55,0.08)  !important; border: 1px solid rgba(26,127,55,0.3)  !important; border-radius: 8px !important; color: #1a7f37 !important; }
.stError   { background: rgba(207,34,46,0.08)  !important; border: 1px solid rgba(207,34,46,0.3)  !important; border-radius: 8px !important; color: #cf222e !important; }
.stWarning { background: rgba(154,103,0,0.08)  !important; border: 1px solid rgba(154,103,0,0.3)  !important; border-radius: 8px !important; color: #9a6700 !important; }
.stInfo    { background: rgba(9,105,218,0.06)  !important; border: 1px solid rgba(9,105,218,0.2)  !important; border-radius: 8px !important; color: #0550ae !important; }

hr { border-color: #d0d7de !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER COMPONENTS
# ─────────────────────────────────────────────

def kpi(label, value, color="#1c2128", sub=""):
    sub_html = f'<div style="font-size:11px;color:#656d76;margin-top:3px;">{sub}</div>' if sub else ""
    return f"""
    <div style="background:#ffffff;border:1px solid #d0d7de;border-radius:8px;padding:14px 16px;">
        <div style="font-size:10px;color:#656d76;font-weight:600;letter-spacing:.5px;
                    text-transform:uppercase;margin-bottom:5px;">{label}</div>
        <div style="font-size:24px;font-weight:700;color:{color};line-height:1;">{value}</div>
        {sub_html}
    </div>"""


def status_icon(status):
    return {"Done": "🟢", "In Progress": "🟡"}.get(status, "⚪")


def status_color_light(status):
    return {"Done": "#1a7f37", "In Progress": "#0969da", "Pending": "#656d76"}.get(status, "#656d76")


# ─────────────────────────────────────────────
# CORE LOGIC
# ─────────────────────────────────────────────

def create_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def create_plan_hash(stages: list) -> str:
    return create_hash("".join(stages))


def add_log(action: str, project: str, user: str, log_type: str = "TRANSACTION"):
    prev_hash = st.session_state.logs[-1]["hash"] if st.session_state.logs else "0"
    time_str  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_string = f"{time_str}_{user}_{action}_{project}_{prev_hash}"
    current_hash = create_hash(log_string)
    st.session_state.logs.append({
        "time":      time_str,
        "user":      user,
        "action":    action,
        "project":   project,
        "type":      log_type,
        "prev_hash": prev_hash,
        "hash":      current_hash,
    })


def validate_chain(logs: list) -> bool:
    for i in range(1, len(logs)):
        prev = logs[i - 1]
        cur  = logs[i]
        recalculated = create_hash(
            f"{cur['time']}_{cur['user']}_{cur['action']}_{cur['project']}_{cur['prev_hash']}"
        )
        if cur["prev_hash"] != prev["hash"] or cur["hash"] != recalculated:
            return False
    return True


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

for key, val in [("projects", {}), ("logs", [])]:
    if key not in st.session_state:
        st.session_state[key] = val


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#0969da,#54aeff);
                        border-radius:8px;display:flex;align-items:center;justify-content:center;
                        font-size:16px;">⛓</div>
            <div>
                <div style="font-size:15px;font-weight:700;color:#1c2128;"></div>
                <div style="font-size:10px;color:#656d76;letter-spacing:.4px;">BLOCKCHAIN PROJECT CONTROL</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**👤 User**")
    user = st.text_input("", placeholder="Enter your name…", label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.session_state.logs:
        intact = validate_chain(st.session_state.logs)
        color  = "#1a7f37" if intact else "#cf222e"
        icon   = "✓" if intact else "✗"
        label  = "CHAIN INTACT" if intact else "CHAIN BROKEN"

        # Count violations
        violations = sum(1 for l in st.session_state.logs if l.get("type") == "ATTEMPT")
        viol_html  = ""
        if violations:
            viol_html = f'<div style="font-size:10px;color:#cf222e;margin-top:4px;">⚠ {violations} violation attempt(s) recorded</div>'

        st.markdown(f"""
        <div style="padding:10px 12px;background:{color}10;border:1px solid {color}33;
                    border-radius:8px;margin-bottom:12px;">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:16px;">{icon}</span>
                <div>
                    <div style="font-size:10px;font-weight:700;color:{color};letter-spacing:.5px;">{label}</div>
                    <div style="font-size:10px;color:#656d76;">{len(st.session_state.logs)} blocks recorded</div>
                </div>
            </div>
            {viol_html}
        </div>""", unsafe_allow_html=True)

    st.markdown("**📂 Projects**")
    for pname in st.session_state.projects:
        p     = st.session_state.projects[pname]
        total = len(p["stages"])
        done  = sum(1 for s in p["stages"] if s["status"] == "Done")
        pct   = int(done / total * 100) if total else 0
        st.markdown(f"""
        <div style="padding:8px 10px;background:#f6f8fa;border-radius:6px;margin-bottom:4px;
                    border-left:3px solid {'#1a7f37' if pct==100 else '#0969da' if pct>0 else '#d0d7de'};">
            <div style="font-size:12px;font-weight:600;color:#1c2128;">{pname}</div>
            <div style="font-size:10px;color:#656d76;">{done}/{total} stages · {pct}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:10px;color:#656d76;line-height:1.7;">
        <div style="font-weight:600;color:#57606a;margin-bottom:4px;">HOW IT WORKS</div>
        Each action is hash-chained using SHA-256.<br>
        Violation <em>attempts</em> are blocked but recorded.<br>
        Any tamper breaks the chain instantly.<br><br>
        <span style="color:#0969da;">Real implementation:</span><br>
        Hyperledger Fabric / distributed ledger
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown("""
<div style="padding:28px 0 20px;">
    <h1 style="font-size:34px;font-weight:700;color:#1c2128;margin:0 0 6px;">
        Project Planning with Immutable Execution Control
    </h1>
    
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────

total_projects = len(st.session_state.projects)
total_stages   = sum(len(p["stages"]) for p in st.session_state.projects.values())
total_done     = sum(sum(1 for s in p["stages"] if s["status"] == "Done")
                     for p in st.session_state.projects.values())
total_blocks   = len(st.session_state.logs)
overall_pct    = int(total_done / total_stages * 100) if total_stages else 0
total_attempts = sum(1 for l in st.session_state.logs if l.get("type") == "ATTEMPT")
chain_ok       = validate_chain(st.session_state.logs) if st.session_state.logs else True

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(kpi("Projects", str(total_projects), "#0969da", f"{total_stages} total stages"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi("Stages Completed", f"{total_done}/{total_stages}", "#1a7f37", f"{overall_pct}% overall"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi("Chain Blocks", str(total_blocks), "#8250df", "SHA-256 hash-chained"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi("Blocked Attempts", str(total_attempts), "#cf222e" if total_attempts else "#656d76",
                    "recorded on chain"), unsafe_allow_html=True)
with k5:
    status_val = "INTACT ✓" if chain_ok else "BROKEN ✗"
    status_col = "#1a7f37" if chain_ok else "#cf222e"
    st.markdown(kpi("Chain Integrity", status_val, status_col, "verify below"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN COLUMNS
# ─────────────────────────────────────────────

left, right = st.columns([1, 1], gap="large")


# ══════════════════════════════════════════════
# LEFT — PROJECT MANAGEMENT
# ══════════════════════════════════════════════

with left:

    st.markdown("""
    <div style="font-size:20px;font-weight:700;color:#1c2128;margin-bottom:10px;">
        📁 Create New Project
    </div>""", unsafe_allow_html=True)

    project_name = st.text_input("Project name", placeholder="e.g. KazFinTech API Migration")
    stages_input = st.text_input("Stages (comma-separated)",
                                 placeholder="e.g. Analysis, Design, Development, Testing, Deployment")

    if st.button("Create Project", use_container_width=True):
        if not user:
            st.error("Please enter your name in the sidebar first.")
        elif not project_name:
            st.error("Project name is required.")
        elif not stages_input:
            st.error("Define at least one stage.")
        elif project_name in st.session_state.projects:
            st.error("A project with this name already exists.")
        else:
            stages    = [s.strip() for s in stages_input.split(",") if s.strip()]
            plan_hash = create_plan_hash(stages)
            st.session_state.projects[project_name] = {
                "stages":    [{"name": s, "status": "Pending"} for s in stages],
                "plan_hash": plan_hash,
            }
            add_log("Project created", project_name, user, log_type="GENESIS")
            st.success(f"✓ Project '{project_name}' created. Genesis block committed.")
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:20px;font-weight:700;color:#1c2128;margin-bottom:10px;">
        ⚙️ Execute Project Plan
    </div>""", unsafe_allow_html=True)

    if not st.session_state.projects:
        st.markdown("""
        <div style="background:#ffffff;border:1px dashed #d0d7de;border-radius:8px;
                    padding:24px;text-align:center;color:#656d76;font-size:13px;">
            No projects yet — create one above.
        </div>""", unsafe_allow_html=True)
    else:
        selected_project = st.selectbox("Select project", list(st.session_state.projects.keys()))
        project = st.session_state.projects[selected_project]

        total = len(project["stages"])
        done  = sum(1 for s in project["stages"] if s["status"] == "Done")
        pct   = done / total if total else 0

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;font-size:11px;
                    color:#656d76;margin-bottom:4px;">
            <span>Execution Progress</span>
            <span style="color:{'#1a7f37' if pct==1 else '#0969da'};font-weight:600;">
                {done}/{total} stages
            </span>
        </div>""", unsafe_allow_html=True)
        st.progress(pct)

        st.markdown(f"""
        <div style="font-size:11px;color:#656d76;margin-bottom:14px;">
            Plan hash:
            <code style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                         background:#f6f8fa;color:#0969da;padding:2px 7px;
                         border-radius:4px;border:1px solid #d0d7de;">
                {project['plan_hash'][:20]}…
            </code>
        </div>""", unsafe_allow_html=True)

        for i, stage in enumerate(project["stages"]):
            s_color  = status_color_light(stage["status"])
            is_done  = stage["status"] == "Done"
            prev_done = i == 0 or project["stages"][i - 1]["status"] == "Done"
            can_exec = prev_done and not is_done
            is_locked = not prev_done and not is_done  # previous stage not done yet

            border = "#1a7f3740" if is_done else ("#0969da40" if can_exec else "#cf222e30")
            bg     = "#1a7f3706" if is_done else ("#0969da06" if can_exec else "#fff0f0")

            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-radius:8px;
                        padding:12px 14px;margin-bottom:6px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:{'6px' if not is_done else '0'};">
                    <span>{'🔒' if is_locked else status_icon(stage['status'])}</span>
                    <span style="font-size:13px;font-weight:600;color:#1c2128;flex:1;">
                        {stage['name']}
                    </span>
                    <span style="font-size:10px;font-weight:600;padding:2px 8px;border-radius:12px;
                                background:{s_color}15;color:{s_color};border:1px solid {s_color}40;">
                        {stage['status'].upper()}
                    </span>
                    {'<span style="font-size:10px;color:#cf222e;font-weight:600;">SEQUENCE LOCK</span>' if is_locked else ''}
                </div>
                {'<div style="font-size:11px;color:#9a6700;background:#fff8c5;border:1px solid #d4a72c;border-radius:6px;padding:6px 10px;margin-bottom:6px;">⚠ Previous stage must be completed first. Attempts to skip are recorded on the blockchain.</div>' if is_locked else ''}
            """, unsafe_allow_html=True)

            # Show button for both executable AND locked stages
            if not is_done:
                btn_label = f"✓ Complete: {stage['name']}" if can_exec else f"⚠ Attempt to skip: {stage['name']}"
                btn_key   = f"btn_{selected_project}_{i}"

                if st.button(btn_label, key=btn_key, use_container_width=True):
                    if not user:
                        st.error("Enter your name in the sidebar first.")
                    elif is_locked:
                        # BLOCKED — but record the attempt on chain
                        add_log(
                            f"⚠ ATTEMPT: skip to '{stage['name']}' (previous stage incomplete)",
                            selected_project,
                            user,
                            log_type="ATTEMPT"
                        )
                        st.error(
                            f"⛔ Action blocked. '{stage['name']}' cannot be completed before "
                            f"'{project['stages'][i-1]['name']}'. "
                            f"This attempt has been permanently recorded on the blockchain."
                        )
                        st.rerun()
                    else:
                        stage["status"] = "Done"
                        add_log(f"Stage completed: {stage['name']}", selected_project, user, log_type="TRANSACTION")
                        st.success(f"✓ '{stage['name']}' marked done. Block committed.")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# RIGHT — BLOCKCHAIN AUDIT
# ══════════════════════════════════════════════

with right:

    st.markdown("""
    <div style="font-size:20px;font-weight:700;color:#1c2128;margin-bottom:10px;">
        Blockchain Ledger
    </div>""", unsafe_allow_html=True)

    if not st.session_state.logs:
        st.markdown("""
        <div style="background:#ffffff;border:1px dashed #d0d7de;border-radius:8px;
                    padding:24px;text-align:center;color:#656d76;font-size:13px;">
            No blocks yet — create a project to commit the genesis block.
        </div>""", unsafe_allow_html=True)
    else:
        recent = st.session_state.logs[-6:]
        for idx, log in enumerate(reversed(recent)):
            abs_idx    = len(st.session_state.logs) - 1 - idx
            log_type   = log.get("type", "TRANSACTION")

            type_color = {
                "GENESIS":     "#9a6700",
                "TRANSACTION": "#0969da",
                "ATTEMPT":     "#cf222e",
                "TAMPER":      "#cf222e",
            }.get(log_type, "#0969da")

            type_bg = {
                "GENESIS":     "#fff8c5",
                "TRANSACTION": "#ddf4ff",
                "ATTEMPT":     "#ffebe9",
                "TAMPER":      "#ffebe9",
            }.get(log_type, "#ddf4ff")

            type_icon = {
                "GENESIS":     "🟡",
                "TRANSACTION": "🔵",
                "ATTEMPT":     "🔴",
                "TAMPER":      "🔴",
            }.get(log_type, "🔵")

            border_col = "#d4a72c" if log_type == "GENESIS" else ("#cf222e40" if log_type == "ATTEMPT" else "#d0d7de")

            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid {border_col};
                        border-radius:8px;padding:14px 16px;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                                color:#656d76;background:#f6f8fa;padding:2px 7px;
                                border-radius:4px;border:1px solid #d0d7de;">#{abs_idx}</span>
                    <span style="font-size:10px;font-weight:600;padding:2px 8px;border-radius:12px;
                                background:{type_bg};color:{type_color};">
                        {type_icon} {log_type}
                    </span>
                    <span style="font-size:12px;font-weight:600;color:#1c2128;flex:1;">{log['action']}</span>
                    <span style="font-size:10px;color:#656d76;">{log['user']}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11px;">
                    <div>
                        <div style="color:#656d76;margin-bottom:2px;font-size:10px;
                                    text-transform:uppercase;letter-spacing:.4px;">Project</div>
                        <div style="color:#1c2128;">{log['project']}</div>
                    </div>
                    <div>
                        <div style="color:#656d76;margin-bottom:2px;font-size:10px;
                                    text-transform:uppercase;letter-spacing:.4px;">Timestamp</div>
                        <div style="color:#1c2128;">{log['time']}</div>
                    </div>
                    <div>
                        <div style="color:#656d76;margin-bottom:2px;font-size:10px;
                                    text-transform:uppercase;letter-spacing:.4px;">Prev Hash</div>
                        <div style="font-family:'IBM Plex Mono',monospace;color:#9a6700;font-size:10px;">
                            {log['prev_hash'][:20]}…</div>
                    </div>
                    <div>
                        <div style="color:#656d76;margin-bottom:2px;font-size:10px;
                                    text-transform:uppercase;letter-spacing:.4px;">This Hash</div>
                        <div style="font-family:'IBM Plex Mono',monospace;color:#0969da;font-size:10px;">
                            {log['hash'][:20]}…</div>
                    </div>
                </div>
            </div>
            {'<div style="width:1px;height:10px;background:#d0d7de;margin-left:18px;"></div>' if idx < len(recent)-1 else ''}
            """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Audit Log Table ──
    st.markdown("""
    <div style="font-size:20px;font-weight:700;color:#1c2128;margin-bottom:10px;">
        Full Audit Log
    </div>""", unsafe_allow_html=True)

    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        df["hash"]      = df["hash"].str[:16] + "…"
        df["prev_hash"] = df["prev_hash"].str[:16] + "…"
        df = df[["time", "type", "user", "action", "project", "prev_hash", "hash"]]
        df.columns = ["Time", "Type", "User", "Action", "Project", "Prev Hash", "Hash"]
        st.dataframe(df, use_container_width=True, height=220)
    else:
        st.markdown('<div style="color:#656d76;font-size:13px;">No entries yet.</div>',
                    unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Validation & Tamper Demo ──
    st.markdown("""
    <div style="font-size:20px;font-weight:700;color:#1c2128;margin-bottom:10px;">
        Chain Validation
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✓ Verify Integrity", use_container_width=True):
            if not st.session_state.logs:
                st.warning("No blocks to verify.")
            elif validate_chain(st.session_state.logs):
                st.success("✓ Chain is intact — all hashes match.")
            else:
                st.error("❌ Chain broken — data was tampered!")

    with c2:
        if st.button("⚠ Simulate Tamper Attack", use_container_width=True):
            if st.session_state.logs:
                st.session_state.logs[0]["action"] = "⚠ TAMPERED RECORD"
                st.warning("Block #0 modified. Run 'Verify Integrity' to see the breach.")
                st.rerun()
            else:
                st.warning("No blocks exist to tamper with.")

        st.markdown("<br>", unsafe_allow_html=True)
    


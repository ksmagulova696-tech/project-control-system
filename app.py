import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib

st.set_page_config(page_title="Project Control System", layout="wide")

# -----------------------------
# ФУНКЦИИ
# -----------------------------

def create_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()


def create_plan_hash(stages):
    return create_hash("".join(stages))


def add_log(action, project, user):
    prev_hash = st.session_state.logs[-1]["hash"] if st.session_state.logs else "0"

    log_string = f"{datetime.now()}_{user}_{action}_{project}_{prev_hash}"
    current_hash = create_hash(log_string)

    st.session_state.logs.append({
        "time": datetime.now(),
        "user": user,
        "action": action,
        "project": project,
        "prev_hash": prev_hash,
        "hash": current_hash
    })


def validate_chain(logs):
    for i in range(1, len(logs)):
        prev = logs[i-1]
        current = logs[i]

        recalculated = create_hash(
            f"{current['time']}_{current['user']}_{current['action']}_{current['project']}_{current['prev_hash']}"
        )

        if current["prev_hash"] != prev["hash"] or current["hash"] != recalculated:
            return False

    return True


def status_color(status):
    if status == "Done":
        return "🟢"
    elif status == "In Progress":
        return "🟡"
    else:
        return "⚪"

# -----------------------------
# ИНИЦИАЛИЗАЦИЯ
# -----------------------------

if "projects" not in st.session_state:
    st.session_state.projects = {}

if "logs" not in st.session_state:
    st.session_state.logs = []

# -----------------------------
# UI — ВСТУПЛЕНИЕ
# -----------------------------

st.markdown("""
# Project Planning with Immutable Execution Control

**Problem:** project stages can be completed retroactively, and execution logs can be modified

**Solution:** sequential workflow control combined with a hash chain mechanism (blockchain-like approach)

Try to break the order of execution
""")

user = st.text_input("User")

col1, col2 = st.columns(2)

# -----------------------------
# ЛЕВАЯ ЧАСТЬ — УПРАВЛЕНИЕ
# -----------------------------

with col1:
    st.header("📁 Project Creation")

    project_name = st.text_input("Project Name")
    stages_input = st.text_input("Stages (comma-separated)")

    if st.button("Create project"):
        if project_name and stages_input:
            stages = [s.strip() for s in stages_input.split(",")]
            plan_hash = create_plan_hash(stages)

            st.session_state.projects[project_name] = {
                "stages": [{"name": s, "status": "Pending"} for s in stages],
                "plan_hash": plan_hash
            }

            add_log("Project created", project_name, user)
            st.success("Project created")

    st.header("⚙️ Project Management")

    if st.session_state.projects:
        selected_project = st.selectbox(
            "Select a project", list(st.session_state.projects.keys())
        )

        project = st.session_state.projects[selected_project]

        st.subheader("Stages")

        total = len(project["stages"])
        done = sum(1 for s in project["stages"] if s["status"] == "Done")

        progress = done / total if total > 0 else 0
        st.progress(progress)
        st.write(f"Progress: {done}/{total}")

        for i, stage in enumerate(project["stages"]):
            st.write(f"{status_color(stage['status'])} {stage['name']} — {stage['status']}")

            if st.button(f"Complete {stage['name']}", key=f"{selected_project}_{i}"):

                if not user:
                    st.error("Enter user")
                    break

                if i > 0 and project["stages"][i-1]["status"] != "Done":
                    st.error("Process flow violation")
                    add_log("🚫 Process violation", selected_project, user)
                else:
                    stage["status"] = "Done"
                    add_log(f"The stage is completed: {stage['name']}", selected_project, user)
                    st.success("Stage completed")

# -----------------------------
# ПРАВАЯ ЧАСТЬ — ЛОГИКА И ДОКАЗАТЕЛЬСТВО
# -----------------------------

with col2:
    st.header("🔍 Audit Log")

    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No entries")

    st.subheader("⛓️ Chain (Blockchain Logic)")

    for log in st.session_state.logs[-5:]:
        st.write(f"""
        🔗 {log['action']}  
        hash: {log['hash'][:12]}...  
        prev: {log['prev_hash'][:12]}...
        """)

    if st.button("Check integrity"):
        if validate_chain(st.session_state.logs):
            st.success("The chain is intact")
        else:
            st.error("❌ The data has been changed!")

    # демонстрация атаки
    if st.button("⚠️ Try changing the data"):
        if st.session_state.logs:
            st.session_state.logs[0]["action"] = "CHANGED"
            st.warning("Data changed manually!")

# -----------------------------
# HASH ПЛАНА
# -----------------------------

st.header("📌 Plan Hash")

if st.session_state.projects:
    st.write(project["plan_hash"])

# -----------------------------
# КОНЦЕПЦИЯ
# -----------------------------

st.info("""
Each action is recorded as a transaction

Each record contains the hash of the previous one

Any modification breaks the chain

In a real-world implementation:
Hyperledger Fabric can be used
""")

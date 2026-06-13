import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

# Database Configuration
DB_NAME = "football_manager.db"

def init_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS players 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS matches 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, date_time DATETIME NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS attendance 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, match_id INTEGER, player_id INTEGER, 
                      paid_stadium INTEGER DEFAULT 0, paid_delivery INTEGER DEFAULT 0,
                      FOREIGN KEY (match_id) REFERENCES matches (id),
                      FOREIGN KEY (player_id) REFERENCES players (id))''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")

def get_next_saturday_2030():
    now = datetime.now()
    days_ahead = 5 - now.weekday()
    if days_ahead <= 0: days_ahead += 7
    next_sat = now + timedelta(days=days_ahead)
    return next_sat.replace(hour=20, minute=30, second=0, microsecond=0)

# DB Operations
def add_player(name, phone):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO players (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    conn.close()

def get_players():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM players", conn)
    conn.close()
    return df

def delete_player(p_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM players WHERE id = ?", (p_id,))
    conn.commit()
    conn.close()
    st.rerun()

def create_match(dt):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO matches (date_time) VALUES (?)", (dt,))
    m_id = c.lastrowid
    conn.commit()
    conn.close()
    return m_id

def get_latest_match():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM matches ORDER BY id DESC LIMIT 1")
    match = c.fetchone()
    conn.close()
    return match

def save_attendance(match_id, attendance_data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM attendance WHERE match_id = ?", (match_id,))
    for p_id, data in attendance_data.items():
        if data['attending']:
            c.execute("INSERT INTO attendance (match_id, player_id, paid_stadium, paid_delivery) VALUES (?, ?, ?, ?)",
                      (match_id, p_id, int(data['stadium']), int(data['delivery'])))
    conn.commit()
    conn.close()
    st.success("Data saved successfully!")

def main():
    st.set_page_config(page_title="Football Match Manager", layout="wide", page_icon="⚽")
    st.title("⚽ Football Match Manager")
    init_db()

    # Initialize session state for teams
    if 'team_a' not in st.session_state: st.session_state.team_a = []
    if 'team_b' not in st.session_state: st.session_state.team_b = []

    tab1, tab2 = st.tabs(["👥 Player Roster", "🏟️ Match & Pitch"])

    with tab1:
        st.header("Player Management")
        with st.form("new_player"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Player Name")
            phone = c2.text_input("Phone Number")
            if st.form_submit_button("Add to Squad"):
                if name and phone: 
                    add_player(name, phone)
                    st.rerun()
        
        st.subheader("Current Squad")
        players_df = get_players()
        for _, row in players_df.iterrows():
            cols = st.columns([3, 3, 1])
            cols[0].write(f"**{row['name']}**")
            cols[1].write(row['phone'])
            if cols[2].button("🗑️", key=f"del_{row['id']}"): delete_player(row['id'])

    with tab2:
        # Match Setup
        with st.expander("⚙️ Match Configuration"):
            match_dt = st.datetime_input("Schedule Match", value=get_next_saturday_2030())
            if st.button("Create New Match"):
                create_match(match_dt)
                st.session_state.team_a, st.session_state.team_b = [], [] # Clear old teams
                st.rerun()

        current_match = get_latest_match()
        if not current_match:
            st.info("Please create a match to start tracking attendance.")
            return

        m_id, m_dt = current_match
        st.subheader(f"📍 Active Match: {m_dt}")
        
        # Attendance & Payment Table
        players = get_players()
        attendance_state = {}
        
        st.write("### Attendance & Payments")
        cols_head = st.columns([2, 1, 1, 1])
        cols_head[0].write("**Player**")
        cols_head[1].write("**Attending**")
        cols_head[2].write("**Paid Stadium**")
        cols_head[3].write("**Paid Delivery**")

        for _, p in players.iterrows():
            p_id, p_name = p['id'], p['name']
            r_cols = st.columns([2, 1, 1, 1])
            r_cols[0].write(p_name)
            is_attending = r_cols[1].checkbox("Present", key=f"att_{p_id}")
            
            p_s, p_d = False, False
            if is_attending:
                p_s = r_cols[2].checkbox("Paid", key=f"ps_{p_id}")
                p_d = r_cols[3].checkbox("Paid", key=f"pd_{p_id}")
            
            attendance_state[p_id] = {'name': p_name, 'attending': is_attending, 'stadium': p_s, 'delivery': p_d}

        # Calculations
        attending_names = [v['name'] for v in attendance_state.values() if v['attending']]
        num_attending = len(attending_names)
        cost_s = 42 / num_attending if num_attending > 0 else 0
        cost_d = 30 / num_attending if num_attending > 0 else 0
        
        # Dashboard
        st.divider()
        st.header("📊 Pitch Dashboard")
        d1, d2 = st.columns(2)
        d1.metric("Stadium / Person", f"{cost_s:.2f} DT")
        d2.metric("Delivery / Person", f"{cost_d:.2f} DT")

        if num_attending > 0:
            total_s_col = sum(cost_s for v in attendance_state.values() if v['stadium'])
            total_d_col = sum(cost_d for v in attendance_state.values() if v['delivery'])
            
            c1, c2 = st.columns(2)
            c1.progress(min(total_s_col/42, 1.0), text=f"Stadium: {total_s_col:.2f} / 42 DT")
            c2.progress(min(total_d_col/30, 1.0), text=f"Delivery: {total_d_col:.2f} / 30 DT")

        # Team Balancer
        st.divider()
        st.header("🏃 Team Balancer")
        if st.button("🔀 Randomly Split Teams", type="secondary"):
            if num_attending >= 2:
                shuffled = attending_names.copy()
                random.shuffle(shuffled)
                mid = len(shuffled) // 2
                st.session_state.team_a = shuffled[:mid]
                st.session_state.team_b = shuffled[mid:]
            else:
                st.warning("Need at least 2 players to split teams.")

        if st.session_state.team_a:
            t1, t2 = st.columns(2)
            t1.success(f"**Team A**\n\n" + "\n".join([f"- {n}" for n in st.session_state.team_a]))
            t2.info(f"**Team B**\n\n" + "\n".join([f"- {n}" for n in st.session_state.team_b]))

        # WhatsApp Summary
        st.divider()
        st.header("📱 Group Summary")
        summary_text = f"""⚽ *Match Summary: {m_dt}*
---
✅ *Confirmed Players:* {num_attending}
💰 *Stadium:* {cost_s:.2f} DT / person
🍕 *Delivery:* {cost_d:.2f} DT / person
💵 *Total to pay:* {cost_s + cost_d:.2f} DT

🏃 *Teams:*
*Team A:* {', '.join(st.session_state.team_a) if st.session_state.team_a else 'Not set'}
*Team B:* {', '.join(st.session_state.team_b) if st.session_state.team_b else 'Not set'}"""
        
        st.text_area("Copy for WhatsApp:", value=summary_text, height=250)
        
        if st.button("💾 Finalize & Save All Data", type="primary"):
            save_attendance(m_id, attendance_state)

if __name__ == "__main__":
    main()

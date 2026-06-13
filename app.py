import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Database Configuration
DB_NAME = "football_manager.db"

def init_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # Players Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        # Matches Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_time DATETIME NOT NULL
            )
        ''')
        # Attendance & Payment Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                player_id INTEGER,
                paid_stadium INTEGER DEFAULT 0,
                paid_delivery INTEGER DEFAULT 0,
                FOREIGN KEY (match_id) REFERENCES matches (id),
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")

def get_next_saturday_2030():
    """Calculate the next Saturday at 20:30."""
    now = datetime.now()
    days_ahead = 5 - now.weekday() # Saturday is 5
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    next_sat = now + timedelta(days=days_ahead)
    return next_sat.replace(hour=20, minute=30, second=0, microsecond=0)

# DB Operations
def add_player(name, phone):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO players (name, phone) VALUES (?, ?)", (name, phone))
        conn.commit()
        conn.close()
        st.success(f"Player {name} added!")
    except sqlite3.Error as e:
        st.error(f"Error: {e}")

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

def save_attendance(match_id, attendance_data):
    """Save or update attendance for a match."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Clear existing for this match to overwrite
    c.execute("DELETE FROM attendance WHERE match_id = ?", (match_id,))
    for p_id, data in attendance_data.items():
        if data['attending']:
            c.execute('''
                INSERT INTO attendance (match_id, player_id, paid_stadium, paid_delivery)
                VALUES (?, ?, ?, ?)
            ''', (match_id, p_id, int(data['stadium']), int(data['delivery'])))
    conn.commit()
    conn.close()
    st.success("Attendance and payments saved!")

def get_latest_match():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM matches ORDER BY id DESC LIMIT 1")
    match = c.fetchone()
    conn.close()
    return match

def main():
    st.set_page_config(page_title="Football Match Manager", layout="wide")
    st.title("⚽ Football Match Manager")
    init_db()

    tab1, tab2 = st.tabs(["Player Management", "Match & Attendance"])

    with tab1:
        st.header("👤 Player Roster")
        with st.form("new_player"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Name")
            phone = c2.text_input("Phone")
            if st.form_submit_button("Add Player"):
                if name and phone: add_player(name, phone)
        
        players_df = get_players()
        for _, row in players_df.iterrows():
            cols = st.columns([3, 3, 1])
            cols[0].write(row['name'])
            cols[1].write(row['phone'])
            if cols[2].button("Delete", key=f"del_{row['id']}"):
                delete_player(row['id'])

    with tab2:
        st.header("📅 Match Management")
        
        # Match Creation
        with st.expander("Create New Match"):
            default_dt = get_next_saturday_2030()
            match_dt = st.datetime_input("Match Date & Time", value=default_dt)
            if st.button("Initialize Match"):
                create_match(match_dt)
                st.rerun()

        current_match = get_latest_match()
        if not current_match:
            st.info("No matches created yet.")
        else:
            m_id, m_dt = current_match
            st.subheader(f"Current Match: {m_dt}")
            
            players = get_players()
            attendance_state = {}
            
            # Attendance List
            st.write("---")
            cols_head = st.columns([2, 1, 1, 1])
            cols_head[0].write("**Player**")
            cols_head[1].write("**Attending**")
            cols_head[2].write("**Paid Stadium**")
            cols_head[3].write("**Paid Delivery**")

            for _, p in players.iterrows():
                p_id = p['id']
                row_cols = st.columns([2, 1, 1, 1])
                row_cols[0].write(p['name'])
                
                is_attending = row_cols[1].checkbox("Present", key=f"att_{p_id}")
                
                paid_s = False
                paid_d = False
                if is_attending:
                    paid_s = row_cols[2].checkbox("Paid", key=f"ps_{p_id}")
                    paid_d = row_cols[3].checkbox("Paid", key=f"pd_{p_id}")
                
                attendance_state[p_id] = {
                    'attending': is_attending,
                    'stadium': paid_s,
                    'delivery': paid_d
                }

            # Dynamic Math
            num_attendees = sum(1 for v in attendance_state.values() if v['attending'])
            
            st.divider()
            st.header("📊 Real-time Dashboard")
            
            if num_attendees > 0:
                cost_s = 42 / num_attendees
                cost_d = 30 / num_attendees
                
                # Financial Summary Logic
                total_s_collected = sum(cost_s for v in attendance_state.values() if v['stadium'])
                total_d_collected = sum(cost_d for v in attendance_state.values() if v['delivery'])

                m1, m2 = st.columns(2)
                m1.metric("Stadium Cost / Person", f"{cost_s:.2f} DT")
                m2.metric("Delivery Cost / Person", f"{cost_d:.2f} DT")

                c1, c2 = st.columns(2)
                c1.progress(min(total_s_collected / 42, 1.0), text=f"Stadium: {total_s_collected:.2f} / 42 DT")
                c2.progress(min(total_d_collected / 30, 1.0), text=f"Delivery: {total_d_collected:.2f} / 30 DT")
            else:
                st.warning("Check players above to calculate costs.")

            if st.button("💾 Save Match Data", type="primary"):
                save_attendance(m_id, attendance_state)

if __name__ == "__main__":
    main()

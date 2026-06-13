import streamlit as st
import sqlite3
import pandas as pd

# Database Configuration
DB_NAME = "football_manager.db"

def init_db():
    """Initialize the database and create the players table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")

def add_player(name, phone):
    """Add a new player to the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO players (name, phone) VALUES (?, ?)", (name, phone))
        conn.commit()
        conn.close()
        st.success(f"Player {name} added successfully!")
    except sqlite3.Error as e:
        st.error(f"Error adding player: {e}")

def get_all_players():
    """Retrieve all players from the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM players", conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        st.error(f"Error fetching players: {e}")
        return pd.DataFrame()

def delete_player(player_id):
    """Delete a player by ID."""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM players WHERE id = ?", (player_id,))
        conn.commit()
        conn.close()
        st.rerun()
    except sqlite3.Error as e:
        st.error(f"Error deleting player: {e}")

# Streamlit UI
def main():
    st.set_page_config(page_title="Football Match Manager", layout="centered")
    st.title("⚽ Football Match Manager")
    
    init_db()

    # Section: Add New Player
    st.header("👤 Add New Player")
    with st.form("add_player_form", clear_on_submit=True):
        name = st.text_input("Name")
        phone = st.text_input("Phone Number")
        submit = st.form_submit_button("Add Player")
        
        if submit:
            if name and phone:
                add_player(name, phone)
            else:
                st.warning("Please fill in both name and phone number.")

    st.divider()

    # Section: Squad Roster
    st.header("📋 Squad Roster")
    players_df = get_all_players()

    if players_df.empty:
        st.info("No players found in the roster.")
    else:
        # We use a custom display to include delete buttons
        for index, row in players_df.iterrows():
            cols = st.columns([3, 3, 1])
            cols[0].write(f"**{row['name']}**")
            cols[1].write(row['phone'])
            if cols[2].button("Delete", key=f"del_{row['id']}"):
                delete_player(row['id'])

if __name__ == "__main__":
    main()

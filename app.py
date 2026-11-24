import os
import sqlite3
import hashlib
import secrets
import json
import random
from datetime import datetime, date, time
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "app.db"
UPLOAD_DIR = APP_DIR / "uploads"
DATA_DIR = APP_DIR / "data"
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Memory & Moments", page_icon="❤️", layout="wide")

TEXT = {
    "English": {
        "welcome": "Welcome", "what": "What would you like to do today?",
        "games": "Play Games", "memories": "My Memories", "today": "Today's Activities",
        "relax": "Music & Relax", "start": "Start today's activity",
        "caregiver": "Caregiver Dashboard", "logout": "Log out",
        "home": "Home", "profile": "My Settings", "history": "Activity History",
        "language": "Language", "save": "Save", "name": "Your name",
        "good": "Lovely effort! Let's enjoy another activity when you're ready.",
        "instruction": "Take your time. There is no hurry."
    },
    "Hindi": {
        "welcome": "स्वागत है", "what": "आज आप क्या करना चाहेंगे?",
        "games": "खेल खेलें", "memories": "मेरी यादें", "today": "आज की गतिविधियाँ",
        "relax": "संगीत और आराम", "start": "आज की गतिविधि शुरू करें",
        "caregiver": "देखभालकर्ता डैशबोर्ड", "logout": "लॉग आउट",
        "home": "होम", "profile": "मेरी सेटिंग्स", "history": "गतिविधि इतिहास",
        "language": "भाषा", "save": "सहेजें", "name": "आपका नाम",
        "good": "बहुत अच्छा प्रयास! जब आप तैयार हों, हम एक और गतिविधि करेंगे।",
        "instruction": "आराम से करें। कोई जल्दी नहीं है।"
    },
    "Kannada": {
        "welcome": "ಸ್ವಾಗತ", "what": "ಇಂದು ನೀವು ಏನು ಮಾಡಲು ಇಷ್ಟಪಡುತ್ತೀರಿ?",
        "games": "ಆಟಗಳನ್ನು ಆಡಿ", "memories": "ನನ್ನ ನೆನಪುಗಳು", "today": "ಇಂದಿನ ಚಟುವಟಿಕೆಗಳು",
        "relax": "ಸಂಗೀತ ಮತ್ತು ವಿಶ್ರಾಂತಿ", "start": "ಇಂದಿನ ಚಟುವಟಿಕೆಯನ್ನು ಪ್ರಾರಂಭಿಸಿ",
        "caregiver": "ಪಾಲಕರ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್", "logout": "ಲಾಗ್ ಔಟ್",
        "home": "ಮುಖಪುಟ", "profile": "ನನ್ನ ಸೆಟ್ಟಿಂಗ್‌ಗಳು", "history": "ಚಟುವಟಿಕೆ ಇತಿಹಾಸ",
        "language": "ಭಾಷೆ", "save": "ಉಳಿಸಿ", "name": "ನಿಮ್ಮ ಹೆಸರು",
        "good": "ಚೆನ್ನಾಗಿ ಪ್ರಯತ್ನಿಸಿದ್ದೀರಿ! ಸಿದ್ಧರಾದಾಗ ಮತ್ತೊಂದು ಚಟುವಟಿಕೆ ಮಾಡೋಣ.",
        "instruction": "ನಿಮ್ಮ ಸಮಯ ತೆಗೆದುಕೊಳ್ಳಿ. ಆತುರ ಬೇಡ."
    }
}

def db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, salt TEXT NOT NULL,
            role TEXT NOT NULL, language TEXT DEFAULT 'English',
            pairing_code TEXT UNIQUE, large_text INTEGER DEFAULT 0,
            high_contrast INTEGER DEFAULT 0, voice_on INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS links(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caregiver_id INTEGER NOT NULL, patient_id INTEGER NOT NULL,
            can_memories INTEGER DEFAULT 1, can_history INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            UNIQUE(caregiver_id, patient_id)
        );
        CREATE TABLE IF NOT EXISTS memories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL, title TEXT NOT NULL,
            relation TEXT DEFAULT '', category TEXT DEFAULT 'People',
            note TEXT DEFAULT '', image_path TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS activities(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL, game TEXT NOT NULL,
            level INTEGER NOT NULL, score INTEGER NOT NULL,
            duration_seconds INTEGER DEFAULT 0, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reminders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL, title TEXT NOT NULL,
            reminder_time TEXT NOT NULL, active INTEGER DEFAULT 1
        );
        """)
init_db()

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180000).hex()
    return digest, salt

def verify_password(password, digest, salt):
    return hash_password(password, salt)[0] == digest

def query_one(sql, params=()):
    with db() as con:
        return con.execute(sql, params).fetchone()

def query_all(sql, params=()):
    with db() as con:
        return con.execute(sql, params).fetchall()

def execute(sql, params=()):
    with db() as con:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid

def speak(text):
    safe = json.dumps(str(text))
    components.html(f"""
    <div style="padding:4px 0">
      <button onclick='const u=new SpeechSynthesisUtterance({safe}); speechSynthesis.cancel(); speechSynthesis.speak(u);'
      style="font-size:18px;padding:10px 16px;border-radius:12px;border:1px solid #888;background:#f3f4f6;cursor:pointer">
      🔊 Listen
      </button>
    </div>
    """, height=58)

def user_by_id(uid):
    return query_one("SELECT * FROM users WHERE id=?", (uid,))

def login_screen():
    st.title("❤️ Memory & Moments")
    st.subheader("Play. Remember. Connect.")
    tab1, tab2 = st.tabs(["Login", "Create account"])
    with tab1:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            ok = st.form_submit_button("Login", use_container_width=True)
        if ok:
            u = query_one("SELECT * FROM users WHERE username=?", (username.strip().lower(),))
            if u and verify_password(password, u["password_hash"], u["salt"]):
                st.session_state.user_id = u["id"]
                st.rerun()
            else:
                st.error("Login details not recognised. Please try again.")
    with tab2:
        with st.form("signup"):
            name = st.text_input("Full name")
            username = st.text_input("Choose a username")
            password = st.text_input("Create password (at least 8 characters)", type="password")
            role = st.selectbox("Account type", ["Patient", "Caregiver"])
            language = st.selectbox("Preferred language", list(TEXT.keys()))
            ok = st.form_submit_button("Create account", use_container_width=True)
        if ok:
            if not name.strip() or not username.strip() or len(password) < 8:
                st.error("Enter your name, username and a password of at least 8 characters.")
            else:
                digest, salt = hash_password(password)
                code = secrets.token_hex(3).upper() if role == "Patient" else None
                try:
                    execute("""INSERT INTO users(name,username,password_hash,salt,role,language,pairing_code,created_at)
                               VALUES(?,?,?,?,?,?,?,?)""",
                            (name.strip(), username.strip().lower(), digest, salt, role, language, code, datetime.now().isoformat()))
                    st.success("Account created. Please log in using the Login tab.")
                except sqlite3.IntegrityError:
                    st.error("That username is already taken. Please choose another.")

def add_activity(patient_id, game, level, score, duration=0):
    execute("INSERT INTO activities(patient_id,game,level,score,duration_seconds,created_at) VALUES(?,?,?,?,?,?)",
            (patient_id, game, level, score, duration, datetime.now().isoformat()))

def game_area(patient, lang):
    st.header("🧠 " + TEXT[lang]["games"])
    game = st.selectbox("Choose an activity", [
        "Picture Memory", "Matching Pairs", "Remember the Sequence",
        "Name the Object", "Numbers & Counting", "Everyday Activities"
    ])
    level = st.select_slider("Difficulty level", options=[1,2,3,4], value=1,
                             format_func=lambda x: ["Very Easy","Easy","Moderate","Advanced"][x-1])
    st.info("There is no pass or fail. Take your time and enjoy the activity.")
    speak("Take your time. Look carefully and enjoy the activity.")
    if game == "Picture Memory":
        items = ["🍎 Apple", "🏠 House", "🐈 Cat", "🌸 Flower", "🚗 Car", "☀️ Sun"]
        count = min(2 + level, 6)
        chosen = random.sample(items, count)
        if "picture_set" not in st.session_state or st.session_state.get("picture_game") != (game, level):
            st.session_state.picture_set = chosen
            st.session_state.picture_game = (game, level)
            st.session_state.picture_show = True
        if st.session_state.picture_show:
            st.write("Look at these pictures and remember them:")
            st.title("   ".join(st.session_state.picture_set))
            if st.button("I am ready"):
                st.session_state.picture_show = False
                st.rerun()
        else:
            st.write("Which pictures did you see?")
            answers = st.multiselect("Choose the pictures", items)
            if st.button("Finish activity"):
                score = sum(x in st.session_state.picture_set for x in answers)
                add_activity(patient["id"], game, level, score)
                st.success(TEXT[lang]["good"])
                st.session_state.pop("picture_set", None)
                st.session_state.pop("picture_game", None)
                st.session_state.pop("picture_show", None)
    elif game == "Matching Pairs":
        symbols = ["🍎","🌼","🐟","🚲"][:2 + (level//2)]
        deck = symbols + symbols
        random.shuffle(deck)
        cols = st.columns(4)
        if "match_revealed" not in st.session_state or st.session_state.get("match_game") != (game, level):
            st.session_state.match_revealed = []
            st.session_state.match_game = (game, level)
        for i, symbol in enumerate(deck):
            with cols[i % 4]:
                if st.button(symbol if i in st.session_state.match_revealed else "❔", key=f"match_{level}_{i}"):
                    if i not in st.session_state.match_revealed:
                        st.session_state.match_revealed.append(i)
                    st.rerun()
        if len(st.session_state.match_revealed) >= len(deck):
            st.success("You explored all the cards!")
            if st.button("Record activity"):
                add_activity(patient["id"], game, level, len(symbols))
                st.session_state.pop("match_revealed", None)
                st.rerun()
        st.caption("Tap the cards to reveal them. Explore at your own pace.")
    elif game == "Remember the Sequence":
        seqs = {
            1:["🍎","🌼"], 2:["🍎","🌼","🐟"],
            3:["🍎","🌼","🐟","🚗"], 4:["🍎","🌼","🐟","🚗","🏠"]
        }
        sequence = seqs[level]
        if "sequence_visible" not in st.session_state or st.session_state.get("seq_game") != (game,level):
            st.session_state.sequence_visible = True
            st.session_state.seq_game = (game,level)
        if st.session_state.sequence_visible:
            st.title("   ".join(sequence))
            if st.button("Hide sequence"):
                st.session_state.sequence_visible = False
                st.rerun()
        else:
            answer = st.text_input("Type the symbols in the same order (copy/paste is okay)", key="sequence_answer")
            if st.button("Check sequence"):
                score = int(answer.replace(" ","") == "".join(sequence))
                add_activity(patient["id"], game, level, score)
                st.success(TEXT[lang]["good"])
                st.session_state.pop("sequence_visible", None)
    elif game == "Name the Object":
        objects = [("🍌","Banana",["Banana","Apple","Car"]),("🔑","Key",["Key","Spoon","Book"]),
                   ("☕","Cup",["Cup","Shoe","Tree"]),("🚲","Bicycle",["Bicycle","House","Fish"])]
        obj = objects[(level-1) % len(objects)]
        st.title(obj[0])
        ans = st.radio("What is this?", obj[2], horizontal=True)
        if st.button("Submit answer"):
            add_activity(patient["id"], game, level, int(ans == obj[1]))
            st.success(TEXT[lang]["good"])
    elif game == "Numbers & Counting":
        target = [2,3,4,5][level-1]
        st.title("⭐ " * target)
        ans = st.radio("How many stars can you see?", [str(x) for x in range(1,7)], horizontal=True)
        if st.button("Check answer"):
            add_activity(patient["id"], game, level, int(ans == str(target)))
            st.success(TEXT[lang]["good"])
    else:
        st.write("Put these everyday activities in a helpful order.")
        options = ["Eat breakfast", "Wake up", "Brush teeth"]
        ans = st.selectbox("First step", options)
        ans2 = st.selectbox("Next step", [x for x in options if x != ans])
        ans3 = st.selectbox("Last step", [x for x in options if x not in [ans,ans2]])
        if st.button("Finish"):
            correct = ["Wake up","Brush teeth","Eat breakfast"]
            score = int([ans,ans2,ans3] == correct)
            add_activity(patient["id"], game, level, score)
            st.success(TEXT[lang]["good"])

def memories_page(patient_id, can_edit=True):
    st.header("❤️ Personal Memories")
    if can_edit:
        with st.expander("＋ Add a memory", expanded=False):
            with st.form("add_memory", clear_on_submit=True):
                title = st.text_input("Name / memory title")
                relation = st.text_input("Relationship or details (optional)")
                category = st.selectbox("Category", ["People","Places","Things","Events"])
                note = st.text_area("A little note (optional)")
                photo = st.file_uploader("Add a photograph (optional)", type=["png","jpg","jpeg"])
                save = st.form_submit_button("Save memory")
            if save and title.strip():
                image_path = ""
                if photo:
                    ext = Path(photo.name).suffix.lower()
                    fname = f"memory_{patient_id}_{secrets.token_hex(6)}{ext}"
                    image_path = str(UPLOAD_DIR / fname)
                    with open(image_path, "wb") as f:
                        f.write(photo.getbuffer())
                execute("""INSERT INTO memories(patient_id,title,relation,category,note,image_path,created_at)
                            VALUES(?,?,?,?,?,?,?)""",
                         (patient_id,title.strip(),relation,category,note,image_path,datetime.now().isoformat()))
                st.success("Memory saved.")
                st.rerun()
    rows = query_all("SELECT * FROM memories WHERE patient_id=? ORDER BY id DESC", (patient_id,))
    if not rows:
        st.info("No memories have been added yet. A caregiver can add familiar people, places and things.")
    for r in rows:
        with st.container(border=True):
            c1,c2 = st.columns([1,3])
            with c1:
                if r["image_path"] and os.path.exists(r["image_path"]):
                    st.image(r["image_path"], use_container_width=True)
                else:
                    st.title("❤️")
            with c2:
                st.subheader(r["title"])
                if r["relation"]: st.write(r["relation"])
                st.caption(r["category"])
                if r["note"]: st.write(r["note"])
                if can_edit and st.button("Delete memory", key=f"delmem_{r['id']}"):
                    if r["image_path"] and os.path.exists(r["image_path"]):
                        os.remove(r["image_path"])
                    execute("DELETE FROM memories WHERE id=?", (r["id"],))
                    st.rerun()

def caregiver_dashboard(caregiver):
    st.header("👨‍👩‍👧 Caregiver Dashboard")
    links = query_all("""SELECT l.*,u.name,u.id AS pid FROM links l JOIN users u ON l.patient_id=u.id
                         WHERE l.caregiver_id=?""", (caregiver["id"],))
    with st.expander("Connect to a patient"):
        st.write("Ask the patient to share their six-character connection code from their account settings.")
        code = st.text_input("Patient connection code", key="connect_code")
        if st.button("Request connection"):
            patient = query_one("SELECT * FROM users WHERE pairing_code=? AND role='Patient'", (code.strip().upper(),))
            if not patient:
                st.error("Code not found. Check the code with the patient.")
            elif patient["id"] == caregiver["id"]:
                st.error("This code cannot be used for this account.")
            else:
                try:
                    execute("INSERT INTO links(caregiver_id,patient_id,created_at) VALUES(?,?,?)",
                            (caregiver["id"],patient["id"],datetime.now().isoformat()))
                    st.success("Connection created.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.info("You are already connected to this patient.")
    if not links:
        st.info("No patient accounts are connected yet.")
        return
    names = {f"{x['name']} (ID {x['pid']})": x for x in links}
    selected = st.selectbox("Connected patient", list(names.keys()))
    link = names[selected]
    patient = user_by_id(link["pid"])
    st.subheader(f"Overview for {patient['name']}")
    acts = query_all("SELECT * FROM activities WHERE patient_id=? ORDER BY created_at DESC LIMIT 30", (patient["id"],))
    today = date.today().isoformat()
    todays = [a for a in acts if a["created_at"].startswith(today)]
    c1,c2,c3 = st.columns(3)
    c1.metric("Activities today", len(todays))
    c2.metric("Activities recorded", len(acts))
    c3.metric("Different games today", len(set(a["game"] for a in todays)))
    st.caption("These are engagement records, not clinical or diagnostic measurements.")
    if link["can_memories"]:
        memories_page(patient["id"], can_edit=True)
    else:
        st.info("Memory access has not been granted.")
    if link["can_history"]:
        st.subheader("Recent activity")
        if acts:
            df = pd.DataFrame([dict(a) for a in acts])
            st.dataframe(df[["game","level","score","created_at"]], use_container_width=True, hide_index=True)
        else:
            st.info("No activities recorded yet.")
    st.subheader("Access permissions")
    m = st.checkbox("Allow access to personal memories", value=bool(link["can_memories"]), key=f"memperm_{link['id']}")
    h = st.checkbox("Allow access to activity history", value=bool(link["can_history"]), key=f"histperm_{link['id']}")
    if st.button("Save permissions"):
        execute("UPDATE links SET can_memories=?,can_history=? WHERE id=?", (int(m),int(h),link["id"]))
        st.success("Permissions updated.")
        st.rerun()
    if st.button("Disconnect this patient"):
        execute("DELETE FROM links WHERE id=?", (link["id"],))
        st.success("Connection removed.")
        st.rerun()

def patient_settings(patient):
    st.header("⚙️ My Settings & Permissions")
    st.write(f"Your caregiver connection code: **{patient['pairing_code']}**")
    st.caption("Share this code only with a caregiver you trust.")
    lang = st.selectbox("Language", list(TEXT.keys()), index=list(TEXT.keys()).index(patient["language"] or "English"))
    large = st.checkbox("Large text", value=bool(patient["large_text"]))
    contrast = st.checkbox("High contrast", value=bool(patient["high_contrast"]))
    voice = st.checkbox("Voice instructions enabled", value=bool(patient["voice_on"]))
    if st.button("Save settings"):
        execute("UPDATE users SET language=?,large_text=?,high_contrast=?,voice_on=? WHERE id=?",
                (lang,int(large),int(contrast),int(voice),patient["id"]))
        st.success("Settings saved.")
        st.rerun()
    st.subheader("Connected caregivers")
    links = query_all("SELECT l.id,u.name,u.username FROM links l JOIN users u ON u.id=l.caregiver_id WHERE l.patient_id=?",
                      (patient["id"],))
    if not links:
        st.info("No caregivers are connected.")
    for l in links:
        c1,c2 = st.columns([3,1])
        c1.write(f"{l['name']} ({l['username']})")
        if c2.button("Revoke access", key=f"revoke_{l['id']}"):
            execute("DELETE FROM links WHERE id=?", (l["id"],))
            st.success("Caregiver access revoked.")
            st.rerun()

def history_page(patient_id):
    st.header("📅 Activity History")
    rows = query_all("SELECT game,level,score,duration_seconds,created_at FROM activities WHERE patient_id=? ORDER BY created_at DESC LIMIT 100",
                     (patient_id,))
    if rows:
        df = pd.DataFrame([dict(r) for r in rows])
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d %b %Y, %I:%M %p")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(pd.DataFrame([dict(r) for r in rows]).groupby("game").size().rename("Activities"))
    else:
        st.info("Your completed activities will appear here.")

def today_page(patient):
    st.header("📅 Today's Activities")
    st.write("A gentle routine for today. You can do these in any order.")
    for label,desc in [("🧠 Memory game","A few minutes of picture or matching games"),
                       ("❤️ Personal memory","Look through familiar people and places"),
                       ("🌼 Relax","Take a comfortable break")]:
        with st.container(border=True):
            st.subheader(label)
            st.write(desc)
    st.subheader("Reminders")
    with st.form("reminder_form"):
        title = st.text_input("Reminder message", "Time for a little activity")
        when = st.time_input("Reminder time", value=time(9,0))
        submit = st.form_submit_button("Add reminder")
    if submit:
        execute("INSERT INTO reminders(patient_id,title,reminder_time) VALUES(?,?,?)",
                (patient["id"],title,when.strftime("%H:%M")))
        st.success("Reminder saved.")
    reminders = query_all("SELECT * FROM reminders WHERE patient_id=? AND active=1", (patient["id"],))
    for r in reminders:
        st.write(f"⏰ {r['reminder_time']} — {r['title']}")
    st.caption("In this MVP, reminders are displayed in the app; background push notifications are not enabled.")

def dataset_page():
    st.header("📊 Included Dataset Overview")
    st.info("The supplied datasets are included for academic exploration only. They are not used to diagnose users or determine game difficulty.")
    for filename in ["OPTIMAL_combined_3studies_6feb2020.csv", "dementia_patients_health_data.csv"]:
        path = DATA_DIR / filename
        if path.exists():
            st.subheader(filename)
            try:
                df = pd.read_csv(path)
                st.write(f"Rows: {len(df):,} · Columns: {len(df.columns)}")
                st.write("Column names:", ", ".join(df.columns.astype(str)))
                st.dataframe(df.head(8), use_container_width=True, hide_index=True)
            except Exception as e:
                st.warning(f"Could not read this dataset: {e}")

def main():
    if "user_id" not in st.session_state:
        login_screen()
        return
    user = user_by_id(st.session_state.user_id)
    if not user:
        st.session_state.pop("user_id", None)
        st.rerun()
    if st.sidebar.button("Log out"):
        st.session_state.clear()
        st.rerun()
    if user["role"] == "Caregiver":
        caregiver_dashboard(user)
        with st.sidebar:
            st.title("❤️ Memory & Moments")
            st.caption(f"Signed in as {user['name']}")
            if st.button("Dataset overview"):
                st.session_state.show_dataset = True
        if st.session_state.get("show_dataset"):
            dataset_page()
        return

    lang = user["language"] if user["language"] in TEXT else "English"
    t = TEXT[lang]
    if user["large_text"]:
        st.markdown("<style>html,body,[class*='st-']{font-size:1.15rem!important} button{min-height:3.2rem!important}</style>", unsafe_allow_html=True)
    if user["high_contrast"]:
        st.markdown("<style>.stApp{background:#000!important;color:#fff!important} [data-testid='stSidebar']{background:#111!important}</style>", unsafe_allow_html=True)
    st.sidebar.title("❤️ Memory & Moments")
    st.sidebar.caption(f"{t['welcome']}, {user['name']}")
    page = st.sidebar.radio("Menu", [t["home"],t["games"],t["memories"],t["today"],t["history"],t["profile"],"Dataset overview"])
    st.title(f"{t['welcome']}, {user['name']}! ❤️")
    if page == t["home"]:
        st.subheader(t["what"])
        speak(t["instruction"])
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🧠  " + t["start"], use_container_width=True):
                st.session_state.go_games = True
                st.rerun()
            if st.button("❤️  " + t["memories"], use_container_width=True):
                st.session_state.go_memories = True
                st.rerun()
        with c2:
            if st.button("🎮  " + t["games"], use_container_width=True):
                st.session_state.go_games = True
                st.rerun()
            if st.button("📅  " + t["today"], use_container_width=True):
                st.session_state.go_today = True
                st.rerun()
        if st.session_state.pop("go_games", False): game_area(user,lang)
        if st.session_state.pop("go_memories", False): memories_page(user["id"])
        if st.session_state.pop("go_today", False): today_page(user)
        st.success(t["good"])
    elif page == t["games"]:
        game_area(user,lang)
    elif page == t["memories"]:
        memories_page(user["id"], can_edit=False)
    elif page == t["today"]:
        today_page(user)
    elif page == t["history"]:
        history_page(user["id"])
    elif page == t["profile"]:
        patient_settings(user)
    else:
        dataset_page()

if __name__ == "__main__":
    main()

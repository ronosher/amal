import json
import os
import streamlit as st

# הגדרת עיצוב עמוד רחב ומותאם למובייל
st.set_page_config(
    page_title="ניהול הימורי כדורגל", page_icon="⚽", layout="wide"
)

# קובצי הנתונים
DATA_FILE = "bets_data.json"
SCHEDULE_FILE = "schedule.json"

# הגדרות כספיות ראשוניות
INITIAL_BANKROLL = 990.0
MY_TEAMS = ["נתניה", "קרית ים", "פולאהם", "בטיס"]

DEFAULT_SCHEDULE = {
    "1": [
        {
            "home": "נתניה",
            "away": "הפועל תל אביב",
            "my_team": "נתניה",
        },
        {"home": "הפועל חיפה", "away": "מכבי חיפה", "my_team": "בטיס"},
        {"home": "בילבאו", "away": "ריאל מדריד", "my_team": "פולאהם"},
        {"home": "ווסטהאם", "away": "ארסנל", "my_team": "קרית ים"},
    ],
    "2": [
        {
            "home": "הפועל תל אביב",
            "away": "נתניה",
            "my_team": "נתניה",
        },
        {"home": "הפועל חיפה", "away": "מכבי תל אביב", "my_team": "בטיס"},
        {"home": "ריאל מדריד", "away": "ברצלונה", "my_team": "קרית ים"},
        {"home": "ארסנל", "away": "צ'לסי", "my_team": "פולאהם"},
    ],
    "3": [
        {
            "home": "נתניה",
            "away": "מכבי פתח תקווה",
            "my_team": "נתניה",
        },
        {"home": "סכנין", "away": "הפועל חיפה", "my_team": "קרית ים"},
        {"home": "סביליה", "away": "ריאל מדריד", "my_team": "פולאהם"},
        {"home": "ליברפול", "away": "ארסנל", "my_team": "בטיס"},
    ],
}


def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_SCHEDULE


def load_data():
    schedule = load_schedule()
    saved_data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                saved_raw = json.load(f)
                saved_data = {int(k): v for k, v in saved_raw.items()}
        except Exception:
            pass

    rounds_data = {}
    for r_str, matches in schedule.items():
        r = int(r_str)
        rounds_data[r] = []
        saved_matches = saved_data.get(r, [])

        for idx, m in enumerate(matches):
            saved_m = saved_matches[idx] if idx < len(saved_matches) else {}
            rounds_data[r].append(
                {
                    "home": m.get("home", ""),
                    "away": m.get("away", ""),
                    "my_team": m.get("my_team", ""),
                    "odds": saved_m.get("odds", "1.0"),
                    "stake": 50,
                    "result": saved_m.get("result", "טרם שוחק"),
                }
            )
    return rounds_data


def save_data(rounds_data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(rounds_data, f, ensure_ascii=False, indent=4)


def calculate_stakes_and_stats(rounds_data):
    total_invested = 0.0
    total_returned = 0.0
    team_stats = {
        team: {
            "played": 0,
            "wins": 0,
            "losses": 0,
            "invested": 0.0,
            "returned": 0.0,
            "profit": 0.0,
        }
        for team in MY_TEAMS
    }
    team_current_stake = {team: 50 for team in MY_TEAMS}
    max_round = max(rounds_data.keys()) if rounds_data else 1

    for r in range(1, max_round + 1):
        if r not in rounds_data:
            continue
        for match in rounds_data[r]:
            team = match["my_team"]
            if team not in team_stats:
                team_stats[team] = {
                    "played": 0,
                    "wins": 0,
                    "losses": 0,
                    "invested": 0.0,
                    "returned": 0.0,
                    "profit": 0.0,
                }
                team_current_stake[team] = 50

            match["stake"] = team_current_stake[team]

            if match["result"] != "טרם שוחק":
                try:
                    odds = float(match["odds"])
                except ValueError:
                    odds = 1.0

                stake = match["stake"]
                total_invested += stake
                team_stats[team]["played"] += 1
                team_stats[team]["invested"] += stake

                if match["result"] == "ניצחון":
                    ret = stake * odds
                    total_returned += ret
                    team_stats[team]["wins"] += 1
                    team_stats[team]["returned"] += ret
                    team_current_stake[team] = 50
                elif match["result"] == "הפסד/תיקו":
                    team_stats[team]["losses"] += 1
                    team_current_stake[team] += 50

    for team, s in team_stats.items():
        s["profit"] = s["returned"] - s["invested"]

    net_profit = total_returned - total_invested
    current_bankroll = INITIAL_BANKROLL + net_profit
    return (
        total_invested,
        total_returned,
        net_profit,
        current_bankroll,
        team_stats,
    )


# טעינת הנתונים
if "rounds_data" not in st.session_state:
    st.session_state.rounds_data = load_data()

rounds_data = st.session_state.rounds_data
(
    total_invested,
    total_returned,
    net_profit,
    current_bankroll,
    team_stats,
) = calculate_stakes_and_stats(rounds_data)

# כותרת ראשית
st.markdown(
    "<h1 style='text-align: center;'>⚽ אפליקציית ניהול הימורי כדורגל 🏆</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# סרגל קופה ומאזן (Metric Cards)
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 קופה התחלתית", f"{INITIAL_BANKROLL:.0f} ₪")
col2.metric("💸 סך השקעה", f"{total_invested:.1f} ₪")
col3.metric(
    "📈 רווח/הפסד נטו",
    f"{net_profit:+.1f} ₪",
    delta_color="normal" if net_profit >= 0 else "inverse",
)
col4.metric("🏦 קופה עדכנית", f"{current_bankroll:.1f} ₪")

st.markdown("---")

# חלוקת המסך: משחקים (שמאל במובייל/רחב) וסטטיסטיקה (ימין)
col_games, col_stats = st.columns([2, 1])

with col_games:
    st.subheader("🎮 משחקי המחזור")

    # בחירת מחזור
    max_r = max(rounds_data.keys()) if rounds_data else 1
    selected_round = st.selectbox(
        "בחר מחזור:",
        list(range(1, max_r + 1)),
        index=0,
        format_func=lambda x: f"מחזור {x}",
    )

    matches = rounds_data.get(selected_round, [])

    # טופס עדכון משחקים
    with st.form(f"form_round_{selected_round}"):
        for idx, m in enumerate(matches):
            st.markdown(f"**{m['home']} - {m['away']}** | הקבוצה שלי: ⚽ **{m['my_team']}**")
            c_odds, c_stake, c_res = st.columns([1, 1, 1.5])

            odds_input = c_odds.text_input(
                "יחס זכייה", value=str(m["odds"]), key=f"odds_{selected_round}_{idx}"
            )
            c_stake.markdown(f"<br><b>הימור: {m['stake']} ₪</b>", unsafe_allow_html=True)

            res_options = ["טרם שוחק", "ניצחון", "הפסד/תיקו"]
            res_idx = (
                res_options.index(m["result"]) if m["result"] in res_options else 0
            )
            result_input = c_res.selectbox(
                "תוצאה",
                res_options,
                index=res_idx,
                key=f"res_{selected_round}_{idx}",
            )

            # עדכון במבנה
            m["odds"] = odds_input
            m["result"] = result_input
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

        submitted = st.form_submit_button("💾 שמור שינויים במחזור זה", use_container_width=True)
        if submitted:
            save_data(rounds_data)
            st.success("הנתונים עודכנו ונשמרו בהצלחה!")
            st.rerun()

with col_stats:
    st.subheader("📊 סטטיסטיקת 4 הקבוצות")
    stats_list = []
    for team, s in team_stats.items():
        stats_list.append(
            {
                "קבוצה": team,
                "משחקים": s["played"],
                "נצ'": s["wins"],
                "הפס'/תיקו": s["losses"],
                "רווח/הפסד": f"{s['profit']:+.1f} ₪",
            }
        )
    st.dataframe(stats_list, use_container_width=True, hide_index=True)

# תחתית המסך
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; background-color: #1e293b; padding: 15px; border-radius: 10px; color: white;'>
        <h3 style='color: #facc15; margin:0;'>✨ "בשם השם נעשה ונצליח" ✨</h3>
        <p style='margin: 5px 0 0 0;'>צוות השחקנים: רון  |  אלי  |  רונן</p>
    </div>
    """,
    unsafe_allow_html=True,
)
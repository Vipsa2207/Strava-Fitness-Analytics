import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# ============================================================
# CONFIG — every color defined once, used everywhere below
# ============================================================
COLORS = {
    "orange": "#FC5200",
    "dark_card": "#1E1E1E",
    "text_dark": "#1A1A1A",
    "text_light": "#FFFFFF",
    "light_bg": "#FAFAFA",
    "chart_grid": "#333333",
    "chart_spine": "#444444",
}

st.set_page_config(
    page_title="Strava Insights Hub",
    page_icon="🟠",
    layout="wide"
)

# ============================================================
# CUSTOM CSS — injected once, styles every tab consistently
# ============================================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    * {{
        font-family: 'Poppins', sans-serif !important;
    }}
    .stApp {{
        background-color: {COLORS['light_bg']} !important;
    }}
    h1, h2, h3, p, span, label, div {{
        color: {COLORS['text_dark']} !important;
    }}
    .kpi-card {{
        background: linear-gradient(135deg, #1E1E1E 0%, #2A1400 100%);
        color: {COLORS['text_light']} !important;
        border: 2px solid {COLORS['orange']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(252, 82, 0, 0.25);
    }}
    .kpi-card * {{
        color: {COLORS['text_light']} !important;
    }}
    .kpi-icon {{
        font-size: 24px;
        margin-bottom: 4px;
    }}
    .kpi-value {{
        font-size: 32px;
        font-weight: 700;
        color: {COLORS['orange']} !important;
    }}
    .kpi-label {{
        font-size: 14px;
        margin-top: 4px;
    }}
    .section-header {{
        font-size: 26px;
        font-weight: 600;
        color: {COLORS['text_dark']};
        margin-top: 10px;
        margin-bottom: 10px;
    }}
    .insight-box {{
        background-color: #FFF4EC;
        border-left: 4px solid {COLORS['orange']};
        border-radius: 6px;
        padding: 14px 18px;
        margin-top: 10px;
        margin-bottom: 20px;
    }}
    .note-box {{
        background-color: #F0F0F0;
        border-left: 4px solid #999999;
        border-radius: 6px;
        padding: 12px 16px;
        margin-top: 10px;
        margin-bottom: 10px;
        font-size: 14px;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 16px;
        font-weight: 600;
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
    }}
    .stTabs [data-baseweb="tab"] p {{
        color: {COLORS['text_dark']} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['dark_card']} !important;
        border-bottom-color: {COLORS['orange']} !important;
    }}
    .stTabs [aria-selected="true"] p {{
        color: {COLORS['orange']} !important;
        font-weight: 700;
    }}
    .leaderboard-row {{
        display: flex;
        align-items: center;
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 14px 20px;
        margin-bottom: 8px;
    }}
    .leaderboard-rank {{
        font-size: 22px;
        font-weight: 700;
        width: 60px;
    }}
    .leaderboard-name {{
        font-size: 16px;
        font-weight: 600;
        flex-grow: 1;
    }}
    .leaderboard-value {{
        font-size: 18px;
        font-weight: 700;
        color: {COLORS['orange']} !important;
    }}
    .badge-card {{
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        margin-bottom: 10px;
    }}
    .badge-earned {{
        background-color: {COLORS['dark_card']};
        border: 2px solid {COLORS['orange']};
        box-shadow: 0 4px 12px rgba(252, 82, 0, 0.25);
    }}
    .badge-earned * {{
        color: {COLORS['text_light']} !important;
    }}
    .badge-locked {{
        background-color: #EFEFEF;
        border: 2px dashed #CCCCCC;
        opacity: 0.6;
    }}
    .badge-emoji {{
        font-size: 34px;
    }}
    .badge-title {{
        font-size: 14px;
        font-weight: 700;
        margin-top: 6px;
    }}
    .badge-desc {{
        font-size: 12px;
        margin-top: 2px;
    }}
    </style>
""", unsafe_allow_html=True)

# ============================================================
# REUSABLE COMPONENTS
# ============================================================
def kpi_card(icon, label, value):
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

def section_header(icon, text):
    st.markdown(f'<div class="section-header">{icon} {text}</div>', unsafe_allow_html=True)

def insight_box(text):
    st.markdown(f'<div class="insight-box">💡 <b>Insight:</b> {text}</div>', unsafe_allow_html=True)

def note_box(text):
    st.markdown(f'<div class="note-box">ℹ️ {text}</div>', unsafe_allow_html=True)

def leaderboard_row(rank, name, value_str):
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    rank_display = medals.get(rank, f"#{rank}")
    st.markdown(f"""
        <div class="leaderboard-row">
            <div class="leaderboard-rank">{rank_display}</div>
            <div class="leaderboard-name">{name}</div>
            <div class="leaderboard-value">{value_str}</div>
        </div>
    """, unsafe_allow_html=True)

def badge_card(emoji, title, desc, earned):
    css_class = "badge-earned" if earned else "badge-locked"
    st.markdown(f"""
        <div class="badge-card {css_class}">
            <div class="badge-emoji">{emoji}</div>
            <div class="badge-title">{title}</div>
            <div class="badge-desc">{desc}</div>
        </div>
    """, unsafe_allow_html=True)

def run_query_safely(query, conn):
    """Only allows SELECT queries. Returns (dataframe, error_message)."""
    cleaned = query.strip().rstrip(';').strip()
    if not cleaned.upper().startswith('SELECT'):
        return None, "Only SELECT queries are allowed in this playground. Queries that modify data (DROP, DELETE, UPDATE, INSERT, etc.) are blocked to keep the database intact for everyone using this session."
    try:
        result_df = pd.read_sql_query(cleaned, conn)
        return result_df, None
    except Exception as e:
        return None, f"SQL Error: {e}"

def quick_stats_summary(result_df):
    """Auto-generates a basic stats summary for any query result's numeric columns.
    Excludes Id-like columns, since averaging an ID number is meaningless."""
    numeric_cols = result_df.select_dtypes(include='number').columns
    numeric_cols = [c for c in numeric_cols if c.lower() != 'id']
    if len(numeric_cols) == 0:
        return None
    lines = []
    for col in numeric_cols[:4]:
        lines.append(f"**{col}** — avg: {result_df[col].mean():,.1f}, min: {result_df[col].min():,.1f}, max: {result_df[col].max():,.1f}")
    return lines

def style_dark_chart(fig, ax):
    """Applies a dark theme to a matplotlib chart, matching the app's black/orange/white palette."""
    fig.patch.set_facecolor(COLORS['dark_card'])
    ax.set_facecolor(COLORS['dark_card'])
    ax.tick_params(colors='white', labelsize=9)
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_color(COLORS['chart_spine'])
    ax.grid(color=COLORS['chart_grid'], alpha=0.4, linewidth=0.5)

# ============================================================
# HEADER
# ============================================================
header_col1, header_col2 = st.columns([1, 8])
with header_col1:
    st.image("strava_logo.png", width=70)
with header_col2:
    st.markdown(f"<h1 style='margin-bottom:0; color:{COLORS['text_dark']} !important;'>Strava Insights Hub</h1>", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# DATA LOADING
# ============================================================
master = pd.read_csv('master_clean.csv')
master['Date'] = pd.to_datetime(master['Date'])

unique_ids = sorted(master['Id'].unique())
id_to_label = {uid: f"User {i+1}" for i, uid in enumerate(unique_ids)}
label_to_id = {v: k for k, v in id_to_label.items()}

# ============================================================
# SQLITE DATABASE SETUP
# ============================================================
@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    daily = pd.read_csv('daily_clean.csv')
    sleep = pd.read_csv('sleep_clean.csv')
    weight = pd.read_csv('weight_clean.csv')
    daily.to_sql('daily_activity', conn, index=False, if_exists='replace')
    sleep.to_sql('sleep', conn, index=False, if_exists='replace')
    weight.to_sql('weight', conn, index=False, if_exists='replace')
    return conn

conn = get_db_connection()

# ============================================================
# EXAMPLE QUERIES
# ============================================================
EXAMPLE_QUERIES = {
    "Join: Activity + Sleep + Weight": {
        "sql": """SELECT d.Id, d.Date, d.TotalSteps, s.TotalMinutesAsleep, w.BMI
FROM daily_activity d
LEFT JOIN sleep s ON d.Id = s.Id AND d.Date = s.Date
LEFT JOIN weight w ON d.Id = w.Id AND d.Date = w.Date
LIMIT 20;""",
        "insight": "This LEFT JOIN keeps all 940 activity days as the base, attaching sleep and weight data only where it exists. Across the full result, sleep data is present for 410 of 940 days (44%) and weight data for only 67 (7%) — the join correctly preserves every activity day rather than dropping rows without a full match, which matters since an INNER JOIN here would have discarded 96%+ of the data."
    },
    "BMI Categorization (WHO Bands)": {
        "sql": """SELECT
  CASE
    WHEN BMI < 18.5 THEN 'Underweight'
    WHEN BMI < 25 THEN 'Normal'
    WHEN BMI < 30 THEN 'Overweight'
    ELSE 'Obese'
  END AS bmi_category,
  COUNT(*) AS record_count,
  COUNT(DISTINCT Id) AS user_count
FROM weight
GROUP BY bmi_category
ORDER BY record_count DESC;""",
        "insight": "Using WHO's standard BMI bands, 34 of 67 weight records (3 users) fall in the 'Normal' range, 32 records (4 users) in 'Overweight', and 1 record (1 user) in 'Obese'. With only 8 total users in the weight dataset, these category counts describe individual people's logging patterns, not a statistically meaningful population split — no single category should be generalized beyond these specific users."
    },
    "Activity-Level Segmentation": {
        "sql": """SELECT
  CASE
    WHEN TotalSteps < 5000 THEN 'Sedentary'
    WHEN TotalSteps < 7500 THEN 'Low Active'
    WHEN TotalSteps < 10000 THEN 'Somewhat Active'
    WHEN TotalSteps < 12500 THEN 'Active'
    ELSE 'Highly Active'
  END AS activity_level,
  COUNT(*) AS day_count,
  ROUND(AVG(Calories), 0) AS avg_calories
FROM daily_activity
GROUP BY activity_level
ORDER BY day_count DESC;""",
        "insight": "Segmenting days by step count shows a clear calorie gradient: 'Sedentary' days (under 5,000 steps, 303 days) average 1,807 calories, rising steadily to 'Highly Active' days (12,500+ steps, 144 days) averaging 2,960 calories — a 64% increase in average calories burned between the least and most active segments. 'Sedentary' is also the single largest segment (303 of 940 days, 32%), reinforcing the Dashboard's earlier finding that sedentary time dominates this dataset."
    },
    "Weekday vs. Weekend Patterns": {
        "sql": """SELECT
  CASE WHEN strftime('%w', Date) IN ('0','6') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
  ROUND(AVG(TotalSteps), 0) AS avg_steps,
  ROUND(AVG(Calories), 0) AS avg_calories
FROM daily_activity
GROUP BY day_type;""",
        "insight": "Average steps are nearly identical between weekdays (7,669) and weekends (7,551) — only a 1.5% difference, and average calories are also nearly flat (2,302 vs. 2,310). This dataset does not show a strong weekday/weekend activity pattern, which is a notable finding in itself: it suggests activity habits in this group are driven by routine rather than the work-week structure."
    },
    "Non-Wear Days vs. Logged Days": {
        "sql": """SELECT
  CASE WHEN is_zero_activity = 1 THEN 'Non-Wear Day (0 steps)' ELSE 'Logged Activity Day' END AS day_status,
  COUNT(*) AS day_count,
  ROUND(AVG(Calories), 0) AS avg_calories
FROM daily_activity
GROUP BY day_status;""",
        "insight": "The 77 flagged non-wear days still average 1,657 calories (baseline/resting burn with no steps recorded), compared to 2,361 calories on the 863 days with logged activity — a 30% gap. This confirms the cleaning-stage decision to keep these rows rather than delete them: they carry real information (baseline calorie burn) even without step data."
    },
}

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊  Dashboard", "🗄️  SQL Analytics Playground", "🏃  User Explorer", "🏆  Leaderboard & Badges"])

with tab1:
    section_header("📊", "Dashboard")

    total_users = master['Id'].nunique()
    avg_steps = master['TotalSteps'].mean()
    avg_sleep_hours = master['TotalMinutesAsleep'].mean() / 60
    avg_sedentary_hours = master['SedentaryMinutes'].mean() / 60

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        kpi_card("", "Total Users Tracked", f"{total_users}")
    with kpi_col2:
        kpi_card("", "Avg Daily Steps", f"{avg_steps:,.0f}")
    with kpi_col3:
        kpi_card("", "Avg Sleep (hrs)", f"{avg_sleep_hours:.1f}")
    with kpi_col4:
        kpi_card("", "Avg Sedentary (hrs)", f"{avg_sedentary_hours:.1f}")

    st.markdown("")
    section_header("📈", "Key Visualizations")

    CHART_FIGSIZE = (6, 4)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Distribution of Total Daily Steps**")
            fig1, ax1 = plt.subplots(figsize=CHART_FIGSIZE)
            sns.histplot(master['TotalSteps'], bins=30, kde=True, ax=ax1,
                         color=COLORS['orange'], edgecolor='white', linewidth=0.3)
            ax1.lines[0].set_color('white')
            ax1.set_xlabel('Total Steps')
            ax1.set_ylabel('Number of Days')
            style_dark_chart(fig1, ax1)
            fig1.tight_layout()
            st.pyplot(fig1)

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Distribution of Total Minutes Asleep**")
            fig2, ax2 = plt.subplots(figsize=CHART_FIGSIZE)
            sns.histplot(master['TotalMinutesAsleep'].dropna(), bins=30, kde=True, ax=ax2,
                         color='#4FC3F7', edgecolor='white', linewidth=0.3)
            ax2.lines[0].set_color('white')
            ax2.set_xlabel('Minutes Asleep')
            ax2.set_ylabel('Number of Nights')
            style_dark_chart(fig2, ax2)
            fig2.tight_layout()
            st.pyplot(fig2)

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        with st.container(border=True):
            st.markdown("**Average Daily Minutes by Activity Intensity**")
            activity_cols = ['VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes', 'SedentaryMinutes']
            short_labels = ['Very Active', 'Fairly Active', 'Lightly Active', 'Sedentary']
            avg_values = master[activity_cols].mean()
            fig3, ax3 = plt.subplots(figsize=CHART_FIGSIZE)
            ax3.bar(short_labels, avg_values.values, color=['#FF6B6B', '#FFA94D', '#69DB7C', COLORS['orange']])
            ax3.set_ylabel('Average Minutes per Day')
            style_dark_chart(fig3, ax3)
            fig3.tight_layout()
            st.pyplot(fig3)

    with chart_col4:
        with st.container(border=True):
            st.markdown("**Steps vs. Calories Burned**")
            fig4, ax4 = plt.subplots(figsize=CHART_FIGSIZE)
            sns.regplot(x='TotalSteps', y='Calories', data=master, ax=ax4,
                        scatter_kws={'alpha': 0.5, 'color': '#CCCCCC', 's': 20},
                        line_kws={'color': COLORS['orange']})
            ax4.set_xlabel('Total Steps')
            ax4.set_ylabel('Calories')
            style_dark_chart(fig4, ax4)
            fig4.tight_layout()
            st.pyplot(fig4)

    st.markdown("")
    section_header("🔥", "Correlation Heatmap")

    with st.container(border=True):
        st.markdown("**How Key Metrics Relate to Each Other**")
        corr_cols = ['TotalSteps', 'Calories', 'VeryActiveMinutes', 'SedentaryMinutes', 'TotalMinutesAsleep', 'BMI']
        corr_matrix = master[corr_cols].corr().round(2)

        fig5, ax5 = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm',
                    center=0, vmin=-1, vmax=1, square=True, ax=ax5,
                    cbar_kws={'label': 'Correlation Strength'},
                    annot_kws={'color': 'black'})
        style_dark_chart(fig5, ax5)
        cbar = ax5.collections[0].colorbar
        cbar.ax.yaxis.set_tick_params(color='white', labelcolor='white')
        cbar.ax.yaxis.label.set_color('white')
        fig5.tight_layout()
        st.pyplot(fig5)

    insight_box("Sedentary minutes and sleep duration show a moderate negative correlation (r = -0.60) — notably stronger than the near-zero relationship found earlier between total active minutes and sleep (r = -0.069). This suggests it isn't activity itself that relates to sleep, but specifically how much sedentary time someone accumulates: more sedentary time associates with less sleep. Steps and Very Active Minutes remain the strongest positive pair with Calories (r = 0.59 and r = 0.62), consistent with earlier findings.")

with tab2:
    section_header("🗄️", "SQL Analytics Playground")

    st.write("Query the `daily_activity`, `sleep`, and `weight` tables directly. Only `SELECT` queries are allowed.")

    st.markdown("#### 📌 Example Queries")
    selected_example = st.selectbox("Pick an example to load:", ["-- None --"] + list(EXAMPLE_QUERIES.keys()))

    if selected_example != "-- None --":
        default_query = EXAMPLE_QUERIES[selected_example]["sql"]
    else:
        default_query = "SELECT * FROM daily_activity LIMIT 10;"

    st.markdown("#### ✍️ Your Query")
    user_query = st.text_area("SQL query:", value=default_query, height=140, key=f"query_{selected_example}")

    if st.button("▶ Run Query"):
        result_df, error = run_query_safely(user_query, conn)

        if error:
            st.error(error)
        else:
            st.success(f"Query returned {len(result_df)} rows.")
            st.dataframe(result_df, use_container_width=True)

            if selected_example != "-- None --":
                insight_box(EXAMPLE_QUERIES[selected_example]["insight"])
            else:
                stats = quick_stats_summary(result_df)
                if stats:
                    with st.container(border=True):
                        st.markdown("**📊 Quick Stats (auto-generated)**")
                        for line in stats:
                            st.markdown(f"- {line}")

with tab3:
    section_header("🏃", "User Explorer")
    st.write("Select a user to see their individual activity, sleep, and calorie trends.")

    selected_label = st.selectbox("Select a user:", list(label_to_id.keys()), key="explorer_user_select")
    selected_id = label_to_id[selected_label]

    user_data = master[master['Id'] == selected_id].sort_values('Date')

    days_tracked = len(user_data)
    user_avg_steps = user_data['TotalSteps'].mean()
    user_avg_sleep = user_data['TotalMinutesAsleep'].mean()
    user_avg_calories = user_data['Calories'].mean()

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        kpi_card("", "Days Tracked", f"{days_tracked}")
    with kpi_col2:
        kpi_card("", "Avg Steps", f"{user_avg_steps:,.0f}")
    with kpi_col3:
        sleep_display = f"{user_avg_sleep:.0f} min" if pd.notna(user_avg_sleep) else "No data"
        kpi_card("", "Avg Sleep", sleep_display)
    with kpi_col4:
        kpi_card("", "Avg Calories", f"{user_avg_calories:,.0f}")

    sleep_days = user_data['TotalMinutesAsleep'].notna().sum()
    weight_days = user_data['BMI'].notna().sum()
    note_box(f"{selected_label} has {days_tracked} activity days logged, {sleep_days} with sleep data, and {weight_days} with weight data.")

    st.markdown("")
    section_header("📈", f"{selected_label}'s Trends Over Time")

    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:
        with st.container(border=True):
            st.markdown("**Steps Over Time**")
            fig6, ax6 = plt.subplots(figsize=(6, 4))
            ax6.plot(user_data['Date'], user_data['TotalSteps'], color=COLORS['orange'], marker='o', markersize=3)
            ax6.set_xlabel('Date')
            ax6.set_ylabel('Total Steps')
            plt.setp(ax6.get_xticklabels(), rotation=30, ha='right')
            style_dark_chart(fig6, ax6)
            fig6.tight_layout()
            st.pyplot(fig6)

    with trend_col2:
        with st.container(border=True):
            st.markdown("**Calories Over Time**")
            fig7, ax7 = plt.subplots(figsize=(6, 4))
            ax7.plot(user_data['Date'], user_data['Calories'], color='#F5F5F5', marker='o', markersize=3)
            ax7.set_xlabel('Date')
            ax7.set_ylabel('Calories')
            plt.setp(ax7.get_xticklabels(), rotation=30, ha='right')
            style_dark_chart(fig7, ax7)
            fig7.tight_layout()
            st.pyplot(fig7)

    if sleep_days > 0:
        with st.container(border=True):
            st.markdown("**Sleep Over Time**")
            sleep_data = user_data.dropna(subset=['TotalMinutesAsleep'])
            fig8, ax8 = plt.subplots(figsize=(12, 4))
            ax8.plot(sleep_data['Date'], sleep_data['TotalMinutesAsleep'], color='#B39DDB', marker='o', markersize=4)
            ax8.set_xlabel('Date')
            ax8.set_ylabel('Minutes Asleep')
            plt.setp(ax8.get_xticklabels(), rotation=30, ha='right')
            style_dark_chart(fig8, ax8)
            fig8.tight_layout()
            st.pyplot(fig8)
    else:
        note_box(f"{selected_label} has no sleep data logged, so no sleep trend is shown.")

with tab4:
    section_header("🏆", "Leaderboard & Achievement Badges")
    st.write("See how users compare across key metrics, and which achievements each user has unlocked.")

    user_stats = master.groupby('Id').agg(
        days_tracked=('TotalSteps', 'count'),
        avg_steps=('TotalSteps', 'mean'),
        total_distance=('TotalDistance', 'sum'),
        avg_calories=('Calories', 'mean'),
        std_steps=('TotalSteps', 'std'),
        zero_days=('is_zero_activity', 'sum'),
    ).reset_index()

    sleep_only = master.dropna(subset=['TotalMinutesAsleep', 'TotalTimeInBed']).copy()
    sleep_only['efficiency'] = sleep_only['TotalMinutesAsleep'] / sleep_only['TotalTimeInBed'] * 100
    sleep_eff = sleep_only.groupby('Id')['efficiency'].mean().reset_index()
    sleep_eff.columns = ['Id', 'avg_sleep_efficiency']

    user_stats = user_stats.merge(sleep_eff, on='Id', how='left')
    user_stats['label'] = user_stats['Id'].map(id_to_label)

    st.markdown("#### 🏁 Leaderboard")

    category = st.selectbox(
        "Choose a category:",
        ["👟 Step Champion (avg daily steps)",
         "🔥 Calorie Burn Leader (avg daily calories)",
         "📏 Total Distance Covered",
         "🎯 Most Consistent Athlete (lowest step variability)",
         "😴 Best Sleep Efficiency"]
    )

    with st.container(border=True):
        if category.startswith("👟"):
            top5 = user_stats.sort_values('avg_steps', ascending=False).head(5)
            for rank, (_, row) in enumerate(top5.iterrows(), start=1):
                leaderboard_row(rank, row['label'], f"{row['avg_steps']:,.0f} steps/day")

        elif category.startswith("🔥"):
            top5 = user_stats.sort_values('avg_calories', ascending=False).head(5)
            for rank, (_, row) in enumerate(top5.iterrows(), start=1):
                leaderboard_row(rank, row['label'], f"{row['avg_calories']:,.0f} cal/day")

        elif category.startswith("📏"):
            top5 = user_stats.sort_values('total_distance', ascending=False).head(5)
            for rank, (_, row) in enumerate(top5.iterrows(), start=1):
                leaderboard_row(rank, row['label'], f"{row['total_distance']:,.1f} mi total")

        elif category.startswith("🎯"):
            eligible = user_stats[user_stats['days_tracked'] >= 20]
            top5 = eligible.sort_values('std_steps', ascending=True).head(5)
            for rank, (_, row) in enumerate(top5.iterrows(), start=1):
                leaderboard_row(rank, row['label'], f"±{row['std_steps']:,.0f} steps std dev")
            note_box("Ranked by lowest day-to-day step variability, among users with 20+ tracked days (for a fair comparison).")

        elif category.startswith("😴"):
            eligible = user_stats.dropna(subset=['avg_sleep_efficiency'])
            top5 = eligible.sort_values('avg_sleep_efficiency', ascending=False).head(5)
            for rank, (_, row) in enumerate(top5.iterrows(), start=1):
                leaderboard_row(rank, row['label'], f"{row['avg_sleep_efficiency']:.1f}% efficiency")
            note_box(f"Only {len(eligible)} of 33 users logged sleep data and are eligible for this leaderboard.")

    st.markdown("")
    st.markdown("#### 🎖️ Achievement Badges")

    badge_user_label = st.selectbox("Select a user to view their badges:", list(label_to_id.keys()), key="badge_user_select")
    badge_user_id = label_to_id[badge_user_label]
    urow = user_stats[user_stats['Id'] == badge_user_id].iloc[0]

    badges = [
        {"emoji": "🎯", "title": "10K Club", "desc": "Avg 10,000+ steps/day",
         "earned": urow['avg_steps'] >= 10000},
        {"emoji": "😴", "title": "Sleep Champion", "desc": "90%+ avg sleep efficiency",
         "earned": pd.notna(urow['avg_sleep_efficiency']) and urow['avg_sleep_efficiency'] >= 90},
        {"emoji": "🏃", "title": "Marathon Mover", "desc": "150+ total miles logged",
         "earned": urow['total_distance'] >= 150},
        {"emoji": "🎖️", "title": "Consistency Award", "desc": "Below-median step variability",
         "earned": urow['std_steps'] <= user_stats['std_steps'].median()},
        {"emoji": "✅", "title": "Perfect Logger", "desc": "Zero non-wear days",
         "earned": urow['zero_days'] == 0},
    ]

    earned_count = sum(b['earned'] for b in badges)
    st.markdown(f"**{badge_user_label}** has earned **{earned_count} of {len(badges)}** badges.")

    badge_cols = st.columns(5)
    for col, badge in zip(badge_cols, badges):
        with col:
            badge_card(badge['emoji'], badge['title'], badge['desc'], badge['earned'])
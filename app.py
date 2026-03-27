import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st 
import warnings
warnings.filterwarnings('ignore')

# --- Page config ---
st.set_page_config(
    page_title="F1 Pit Strategy Simulator",
    page_icon="🏎️",
    layout="wide"
)

# --- Driver roster ---
driver_roster = {
    "Verstappen":  {"team": "Red Bull",     "color": "#3671C6"},
    "Leclerc":     {"team": "Ferrari",      "color": "#E8003D"},
    "Norris":      {"team": "McLaren",      "color": "#FF8000"},
    "Piastri":     {"team": "McLaren",      "color": "#FF8000"},
    "Hamilton":    {"team": "Ferrari",      "color": "#E8003D"},
    "Russell":     {"team": "Mercedes",     "color": "#27F4D2"},
    "Sainz":       {"team": "Williams",     "color": "#64C4FF"},
    "Alonso":      {"team": "Aston Martin", "color": "#229971"},
    "Perez":       {"team": "Red Bull",     "color": "#3671C6"},
    "Gasly":       {"team": "Alpine",       "color": "#FF87BC"},
}

driver_names = list(driver_roster.keys())

# --- Tyre models ---
degradation_models = {
    'SOFT': {
        'base_time': 96.5,
        'deg_per_lap': 0.250
    },
    'MEDIUM': {
        'base_time': 97.4,
        'deg_per_lap': 0.145
    },
    'HARD': {
        'base_time': 98.2,
        'deg_per_lap': 0.075
    }
}

# --- Simulator function ---
def simulate_strategy(
    driver_a_compound, driver_a_tyre_age,
    driver_b_compound, driver_b_tyre_age,
    gap_ab, pit_lap, total_laps,
    new_compound, pit_loss=24.0
):
    model_a   = degradation_models[driver_a_compound]
    model_b   = degradation_models[driver_b_compound]
    model_new = degradation_models[new_compound]

    results = []
    current_gap        = gap_ab
    a_tyre_age         = driver_a_tyre_age
    b_tyre_age         = driver_b_tyre_age
    pitted             = False
    compound_a_current = driver_a_compound

    for lap in range(1, total_laps + 1):
        if lap == pit_lap and not pitted:
            lap_time_a = model_a['base_time'] + model_a['deg_per_lap'] * a_tyre_age + pit_loss
            a_tyre_age = 1
            pitted = True
            compound_a_current = new_compound
        elif pitted:
            lap_time_a = model_new['base_time'] + model_new['deg_per_lap'] * a_tyre_age
            a_tyre_age += 1
        else:
            lap_time_a = model_a['base_time'] + model_a['deg_per_lap'] * a_tyre_age
            a_tyre_age += 1

        lap_time_b = model_b['base_time'] + model_b['deg_per_lap'] * b_tyre_age
        b_tyre_age += 1

        current_gap += (lap_time_b - lap_time_a)

        results.append({
            'Lap': lap,
            'GapAheadOfB': round(current_gap, 3),
            'LapTimeA': round(lap_time_a, 3),
            'LapTimeB': round(lap_time_b, 3),
            'CompoundA': compound_a_current,
            'Pitted': lap == pit_lap
        })

    return pd.DataFrame(results)


# --- Plot function ---
def plot_strategy(result_undercut, result_overcut, driver_a, driver_b,
                  undercut_lap, overcut_lap,
                  color_a='#E8003D', color_b='#0067FF'):

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle(
        f'Pit Stop Strategy Simulator — Bahrain 2024\n{driver_a} vs {driver_b}',
        fontsize=13, fontweight='bold'
    )

    # --- Plot 1: Gap ---
    ax1 = axes[0]
    ax1.plot(result_undercut['Lap'], result_undercut['GapAheadOfB'],
             color=color_a, linewidth=2.5, label=f'Undercut (pit lap {undercut_lap})')
    ax1.plot(result_overcut['Lap'], result_overcut['GapAheadOfB'],
             color=color_b, linewidth=2.5, linestyle='--',
             label=f'Overcut (pit lap {overcut_lap})')
    ax1.axhline(0, color='gray', linestyle=':', linewidth=1)
    ax1.axvline(undercut_lap, color=color_a, linestyle=':', linewidth=1.2, alpha=0.6)
    ax1.axvline(overcut_lap,  color=color_b, linestyle=':', linewidth=1.2, alpha=0.6)

    ax1.fill_between(result_undercut['Lap'], result_undercut['GapAheadOfB'], 0,
                     where=result_undercut['GapAheadOfB'] > 0, alpha=0.08, color=color_a)
    ax1.fill_between(result_undercut['Lap'], result_undercut['GapAheadOfB'], 0,
                     where=result_undercut['GapAheadOfB'] < 0, alpha=0.08, color=color_a)

    final_u = result_undercut['GapAheadOfB'].iloc[-1]
    final_o = result_overcut['GapAheadOfB'].iloc[-1]
    ax1.annotate(f"Final: {final_u:+.1f}s",
                 xy=(result_undercut['Lap'].iloc[-1], final_u),
                 xytext=(-8, 6), textcoords='offset points', fontsize=8, color=color_a)
    ax1.annotate(f"Final: {final_o:+.1f}s",
                 xy=(result_overcut['Lap'].iloc[-1], final_o),
                 xytext=(-8, -14), textcoords='offset points', fontsize=8, color=color_b)

    ax1.set_xlabel('Laps remaining', fontsize=10)
    ax1.set_ylabel(f'Gap — {driver_a} ahead of {driver_b} (s)', fontsize=10)
    ax1.set_title('Position gap over time', fontsize=11)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.2)
    ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0fs'))

    # --- Plot 2: Lap times ---
    ax2 = axes[1]
    ax2.plot(result_undercut['Lap'], result_undercut['LapTimeA'],
             color=color_a, linewidth=2, label=f'{driver_a} (undercut)')
    ax2.plot(result_undercut['Lap'], result_undercut['LapTimeB'],
             color='gray', linewidth=2, linestyle='--', label=f'{driver_b} (stays out)')
    ax2.plot(result_overcut['Lap'], result_overcut['LapTimeA'],
             color=color_b, linewidth=2, label=f'{driver_a} (overcut)')
    ax2.axvline(undercut_lap, color=color_a, linestyle=':', linewidth=1.2, alpha=0.6)
    ax2.axvline(overcut_lap,  color=color_b, linestyle=':', linewidth=1.2, alpha=0.6)

    ax2.set_xlabel('Laps remaining', fontsize=10)
    ax2.set_ylabel('Lap time (seconds)', fontsize=10)
    ax2.set_title('Lap time comparison', fontsize=11)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.2)
    ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1fs'))

    plt.tight_layout()
    return fig


# ============================================================
# STREAMLIT UI
# ============================================================

st.title("🏎️ F1 Pit Stop Strategy Simulator")
st.markdown("**Bahrain 2024** · Simulate undercut vs overcut scenarios in real time")
st.divider()

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Scenario Settings")

    st.subheader("Drivers")
    driver_a = st.selectbox("Driver A (attacker)", driver_names, index=0)
    driver_b = st.selectbox("Driver B (defender)", driver_names, index=1)

    color_a = driver_roster[driver_a]["color"]
    color_b = driver_roster[driver_b]["color"]

    st.markdown(
        f"<span style='color:{color_a}'>■</span> {driver_a} · {driver_roster[driver_a]['team']} &nbsp;&nbsp;"
        f"<span style='color:{color_b}'>■</span> {driver_b} · {driver_roster[driver_b]['team']}",
        unsafe_allow_html=True
    )

    st.subheader("Starting conditions")
    gap_ab     = st.slider("Driver A gap ahead of B (s)", -5.0, 10.0, 3.0, 0.5)
    total_laps = st.slider("Laps remaining", 10, 50, 30)

    st.subheader("Tyre settings")
    compounds    = ['SOFT', 'MEDIUM', 'HARD']
    a_compound   = st.selectbox("Driver A current compound", compounds, index=1)
    a_tyre_age   = st.slider("Driver A tyre age (laps)", 1, 40, 18)
    b_compound   = st.selectbox("Driver B current compound", compounds, index=1)
    b_tyre_age   = st.slider("Driver B tyre age (laps)", 1, 40, 15)
    new_compound = st.selectbox("Driver A new compound (after pit)", compounds, index=2)

    st.subheader("Pit stop settings")
    pit_loss     = st.slider("Pit loss time (s)", 18.0, 30.0, 24.0, 0.5)
    undercut_lap = st.slider("Undercut pit lap", 1, total_laps - 5, 3)
    overcut_lap  = st.slider("Overcut pit lap", undercut_lap + 1, total_laps - 2, 8)

# --- Run simulations ---
result_undercut = simulate_strategy(
    a_compound, a_tyre_age, b_compound, b_tyre_age,
    gap_ab, undercut_lap, total_laps, new_compound, pit_loss
)
result_overcut = simulate_strategy(
    a_compound, a_tyre_age, b_compound, b_tyre_age,
    gap_ab, overcut_lap, total_laps, new_compound, pit_loss
)

final_u = result_undercut['GapAheadOfB'].iloc[-1]
final_o = result_overcut['GapAheadOfB'].iloc[-1]

# --- Verdict banner ---
st.subheader("📊 Strategy Verdict")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f"Undercut (pit lap {undercut_lap})",
        value=f"{final_u:+.2f}s",
        delta="Works ✓" if final_u > 0 else "Fails ✗"
    )
with col2:
    st.metric(
        label=f"Overcut (pit lap {overcut_lap})",
        value=f"{final_o:+.2f}s",
        delta="Works ✓" if final_o > 0 else "Fails ✗"
    )
with col3:
    if final_u > 0 and final_o > 0:
        better = "Undercut" if final_u > final_o else "Overcut"
        margin = abs(final_u - final_o)
        st.metric(label="Recommended", value=better, delta=f"by {margin:.2f}s")
    elif final_u > 0:
        st.metric(label="Recommended", value="Undercut", delta="Only viable option")
    elif final_o > 0:
        st.metric(label="Recommended", value="Overcut", delta="Only viable option")
    else:
        st.metric(label="Recommended", value="Stay out", delta="Both strategies fail")

st.divider()

# --- Charts ---
st.subheader("📈 Strategy Simulation")
fig = plot_strategy(result_undercut, result_overcut,
                    driver_a, driver_b, undercut_lap, overcut_lap,
                    color_a, color_b)
st.pyplot(fig)
plt.close()

st.divider()

# --- Raw data ---
with st.expander("🔍 View raw simulation data"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Undercut — pit lap {undercut_lap}**")
        st.dataframe(result_undercut, use_container_width=True)
    with col2:
        st.markdown(f"**Overcut — pit lap {overcut_lap}**")
        st.dataframe(result_overcut, use_container_width=True)

# --- Footer ---
st.divider()
st.caption("Built with FastF1 · Bahrain 2024 tyre data · Pirelli compound estimates")
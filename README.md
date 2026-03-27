# 🏎️ F1 Pit Stop Strategy Simulator — Bahrain 2024

An interactive race strategy simulator built with Python and Streamlit that models undercut and overcut scenarios using real F1 tyre degradation data.

🔗 **Live App** → [f1-pit-strategy-simulator.streamlit.app](https://f1-pit-strategy-simulator.streamlit.app/)

---

## 📸 App Preview

![F1 Pit Strategy Simulator](screenshot.png)

---

## 🎯 Project Overview

In Formula 1, the difference between winning and losing often comes down to a single pit stop decision made in under 10 seconds. This project simulates two of the most critical strategic calls a race engineer can make:

- **Undercut** — pit early for fresh tyres, use the pace advantage to jump your rival when they pit later
- **Overcut** — stay out longer, build a gap on track, pit after your rival and emerge ahead

The simulator lets you configure any two drivers, tyre compounds, tyre ages, gap, and pit lap — and instantly shows you which strategy wins and by how much.

---

## 🧠 What I Learned

### 1. F1 data is messier than it looks
I started by pulling race data from the FastF1 API across multiple circuits — Monza, Silverstone, Las Vegas, and Bahrain. The plan was to fit a linear regression model per tyre compound to learn degradation rates directly from lap time data.

The regression consistently returned **negative degradation coefficients** — meaning tyres appeared to get faster with age, which is physically impossible. After investigating, I found several confounding factors:

- **Fuel load effect** — cars are significantly heavier at the start of a race, making early laps slower regardless of tyre age. This creates a downward trend in lap times over a stint that masks tyre degradation
- **Traffic and track position** — drivers in traffic post slower laps unrelated to tyre condition
- **Safety car periods** — artificially slow laps that skew the regression
- **Mixed conditions** — Silverstone 2024 had an intermediate tyre phase that contaminated the data entirely

### 2. Knowing when to switch approaches
After testing four different circuits and getting unreliable regression outputs each time, I made the engineering decision to **abandon the regression model** and switch to a physics-based lookup table approach using Pirelli's published compound data.

This was the right call for two reasons:

- Pirelli publishes detailed pre-event tyre notes for every race including estimated pace deltas and expected degradation windows — this is primary source data, not a proxy
- Real F1 teams don't derive tyre models purely from timing data either. They combine telemetry, tyre temperature sensors, compound construction data, and simulation tools — a simple linear regression on lap times is too blunt an instrument

The one reliable number I extracted from the regression was **Medium tyre degradation at Bahrain (+0.158s/lap)**, which I used to anchor the relative estimates for Soft and Hard compounds.

### 3. Simulation modelling
The core simulator models lap-by-lap gap evolution between two drivers. Key inputs:

- Base lap time per compound (from Pirelli data)
- Degradation rate per compound (seconds lost per lap)
- Current tyre age for both drivers
- Pit loss time (~24s at Bahrain)
- Pit lap choice for undercut and overcut scenarios

The gap update rule is simple but powerful:
```python
gap += (driver_b_lap_time - driver_a_lap_time)
```

A positive gap means Driver A is ahead. On the pit lap, Driver A loses the pit loss time but gains fresh tyre pace from the next lap onward. The crossover point — where fresh tyre pace recovers the pit deficit — is what determines whether the strategy works.

### 4. Building an interactive tool
Converting the Jupyter notebook analysis into a Streamlit app taught me how to structure code for interactivity — separating the simulation logic from the UI layer, and designing controls that make strategic trade-offs immediately visible.

---

## 🔍 Key Insight — Why the Undercut Wins at Bahrain

At Bahrain, the Hard tyre has a degradation rate of just **+0.075s/lap** vs **+0.145s/lap** for the Medium. This means a driver on fresh Hards gains roughly **~1.7s per lap** over a driver on worn Mediums. With a pit loss of 24s, the undercut recovers the deficit in approximately **14 laps** — well within a typical stint length.

The overcut works too, but by a smaller margin — staying out longer burns more tyre life on the Medium before switching, meaning the Hard stint starts from a shallower pace advantage.

**Undercut wins at Bahrain by ~3.3s over the overcut** in a standard scenario.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| FastF1 | F1 timing and lap data API |
| Pandas | Data cleaning and manipulation |
| Matplotlib | Visualisation |
| Scikit-learn | Linear regression (tyre degradation modelling) |
| Streamlit | Interactive web app |

---

## 📊 Tyre Model — Bahrain 2024

| Compound | Base lap time | Degradation |
|---|---|---|
| Soft | 96.5s | +0.250s/lap |
| Medium | 97.4s | +0.145s/lap |
| Hard | 98.2s | +0.075s/lap |

Soft and Hard values estimated from Pirelli's 2024 Bahrain pre-event notes. Medium degradation rate validated against FastF1 regression (+0.158s/lap from race data).

---

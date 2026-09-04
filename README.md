# ✨ Navtara Pulse

A precision Vedic astrology transit application built with Python and Streamlit. **Navtara Pulse** computes daily lunar transits using the Swiss Ephemeris (`pyswisseph`) C-engine and maps them against your Janma Nakshatra across the 27-Nakshatra, 3-cycle Navtara system.

---

## 🚀 Features

- **Sub-Arcsecond Astronomical Precision:** Powered by Swiss Ephemeris (`Moshier` model + true Chitrapaksha Lahiri Ayanamsa subtraction).
- **Automated 7-Day Matrix:** Real-time calculation of exact Nakshatra ingress and egress timings down to 1-minute precision.
- **Risk & Opportunity Color Coding:** Instant status alerts for high-yield windows (🟢🟢 Ati-Mitra, Sampat) and high-risk periods (🔴 Vipat, Pratyari, Vadha).
- **Persistent User Profile:** Automatically stores your birth details and Janma Nakshatra locally (`user_profile.json`) so you don't have to re-enter them on reload.

---

## 📖 How to Use

### 1. First-Time Setup (Sidebar)
1. Open the left sidebar (`>`).
2. Enter your **Name**, **Date of Birth**, **Time of Birth**, and **Birth Place**.
3. Select your **Janma Nakshatra** (e.g., *Bharani*).
4. Click **💾 Save Profile**.
   > *Your details are now saved. Every time you open or refresh the app, your saved settings will load automatically.*

---

### 2. Reading the 7-Day Transit Table
The main dashboard displays the next 7 days of continuous Moon transits divided into specific time windows:

| Column | What It Means |
| :--- | :--- |
| **Status** | The active Navtara energy indicator (e.g., 🔴 Vipat, 🟢🟢 Ati-Mitra, Sampat, Sadhana). |
| **Day, Date & Time Range** | The exact start and end timestamps (IST) for that specific lunar transit. |
| **Nakshatra Name** | The constellation the Moon is actively transiting through. |
| **Navtara Series** | The category description and cycle (Series 1: Nakshatras 1–9, Series 2: 10–18, Series 3: 19–27). |

---

### 3. Operational Rules (How to Act on the Data)

- **🟢🟢 Ati-Mitra (Great Friend) & Sampat (Wealth):**
  - **Best for:** Important meetings, major financial allocation, entering contracts, launching projects, and critical personal milestones.
- **🔴 Vipat (Danger), Pratyari (Conflict), Vadha (Destruction):**
  - **Precaution:** Exercise restraint. Avoid high-risk financial decisions, initiating heated discussions, or beginning complex structural tasks during these windows.
- **Kshema (Well-being) & Sadhana (Achievement):**
  - **Best for:** Health maintenance, rest, research, focused learning, and completing pending operational work.

---


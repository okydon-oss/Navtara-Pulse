# views/monthly.py - Dedicated Monthly Horoscope View with Complete Bilingual Support
import streamlit as st
import datetime
import databanks as db

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

# Bilingual Dictionary for Monthly Horoscope Domains and UI Labels
MONTHLY_CONTENT_HI = {
    "select_month": "**मासिक फलाग्रह माह चुनें:**",
    "current_month": "वर्तमान माह",
    "next_month": "आगामी माह",
    "astro_climate": "खगोलीय जलवायु एवं गोचर प्रभाव",
    "domains": {
        "self": {"title": "🧘 1. आत्मबल एवं स्वास्थ्य (शरीर, ऊर्जा व व्यक्तित्व):", "key": "self"},
        "family": {"title": "👨‍👩‍👦 2. परिवार एवं संचित धन (Liquid Assets & Speech):", "key": "family"},
        "travels": {"title": "✈️ 3. पराक्रम एवं यात्राएं (Short Journeys & Enterprise):", "key": "travels"},
        "property": {"title": "🏡 4. भूमि, भवन एवं सुख (Property, Vehicles & Domestic Peace):", "key": "property"},
        "study": {"title": "📚 5. संतान एवं उच्च शिक्षा (Intellect & Creative Strategy):", "key": "study"},
        "loan": {"title": "📉 6. ऋण, शत्रु एवं स्वास्थ्य रक्षा (Immunity & Competitors):", "key": "loan"},
        "spouse": {"title": "💍 7. दांपत्य एवं व्यापारिक साझेदारियाँ (Alliances & Contracts):", "key": "spouse"},
        "research": {"title": "🔬 8. आकस्मिक परिवर्तन एवं शोध (Sudden Shifts & Research Caution):", "key": "research"},
        "luck": {"title": "🍀 9. भाग्य, धर्म एवं गुरु कृपा (Higher Journeys & Fortune):", "key": "luck"},
        "career": {"title": "💼 10. करियर, पद एवं अधिकार (Authority & Executive Standing):", "key": "career"},
        "gains": {"title": "💰 11. आय, लाभ एवं नेटवर्क (Profits & Aspirations):", "key": "gains"},
        "foreign": {"title": "🌐 12. व्यय, विदेशी संबंध एवं मोक्ष (Expenditure & Overseas Linkages):", "key": "foreign"}
    }
}

MONTHLY_DOMAIN_TRANSLATIONS_HI = {
    "Self & Vitality (Body, Physique, Energy):": "🧘 1. आत्मबल एवं स्वास्थ्य (शरीर, ऊर्जा व व्यक्तित्व):",
    "Family & Accumulated Wealth (Liquid Assets & Speech):": "👨‍👩‍👦 2. परिवार एवं संचित धन (Liquid Assets & Speech):",
    "Travels & Enterprise (Short Journeys, Siblings & Courage):": "✈️ 3. पराक्रम एवं यात्राएं (Short Journeys & Enterprise):",
    "Property, Vehicles & Domestic Peace (Land & Home):": "🏡 4. भूमि, भवन एवं सुख (Property, Vehicles & Domestic Peace):",
    "Children & Higher Study (Intellect & Creative Strategy):": "📚 5. संतान एवं उच्च शिक्षा (Intellect & Creative Strategy):",
    "Loans, Debts & Health Defense (Immunity & Competitors):": "📉 6. ऋण, शत्रु एवं स्वास्थ्य रक्षा (Immunity & Competitors):",
    "Spouse & Business Partnerships (Alliances & Contracts):": "💍 7. दांपत्य एवं व्यापारिक साझेदारियाँ (Alliances & Contracts):",
    "Sudden Shifts, Research & Accidents Caution:": "🔬 8. आकस्मिक परिवर्तन एवं शोध (Sudden Shifts & Research Caution):",
    "Luck, Dharma & Mentorship (Higher Journeys & Fortune):": "🍀 9. भाग्य, धर्म एवं गुरु कृपा (Higher Journeys & Fortune):",
    "Career, Job & Executive Stature (Authority & Standing):": "💼 10. करियर, पद एवं अधिकार (Authority & Executive Standing):",
    "Gains, Inflows & Network Circles (Profits & Aspirations):": "💰 11. आय, लाभ एवं नेटवर्क (Profits & Aspirations):",
    "Expenditure, Foreign Linkages & Overseas Settlements:": "🌐 12. व्यय, विदेशी संबंध एवं मोक्ष (Expenditure & Overseas Linkages):"
}

def render_page_monthly():
    if not st.session_state.get("has_valid_profile", False):
        is_hi = st.session_state.get("user_profile", {}).get("lang", "en") == "hi"
        prompt_title = "अपनी जन्म पत्रिका प्रोफाइल सेट करें" if is_hi else "Set Up Your Vedic Birth Profile"
        prompt_desc = "मासिक राशिफल और गोचर फलादेश की गणना के लिए यूज़र प्रोफाइल टैब में अपना जन्म विवरण भरें।" if is_hi else "To calculate your Lagna-based monthly horoscope, please enter your birth details in the User Profile tab."
        btn_lbl = "👉 प्रोफाइल अभी भरें" if is_hi else "👉 Configure Profile Now"
        
        render_html(f"""
        <div style="background:#fffbeb; border:2px dashed #f59e0b; border-radius:16px; padding:1.5rem; text-align:center; margin:1.5rem 0;">
            <div style="font-size:2.2rem; margin-bottom:8px;">👤</div>
            <div style="font-weight:900; font-size:1.25rem; color:#92400e; margin-bottom:6px;">
                {prompt_title}
            </div>
            <div style="font-size:0.95rem; color:#78350f; max-width:480px; margin:0 auto 1.2rem auto; line-height:1.6;">
                {prompt_desc}
            </div>
        </div>
        """)
        _, c_mid, _ = st.columns([1, 2, 1])
        with c_mid:
            if st.button(btn_lbl, type="primary", use_container_width=True):
                st.session_state.current_page = "profile"
                st.rerun()
        return

    prof = st.session_state.get("user_profile", {})
    current_lang = prof.get("lang", "en")
    is_hi = (current_lang == "hi")

    chart_info = st.session_state.get("chart_info", {})
    lagna_name = chart_info["lagna_name"]
    lagna_idx = chart_info["lagna_idx"]

    card_header = "📅 लग्न-आधारित मासिक राशिफल एवं जीवन मैट्रिक्स" if is_hi else "📅 Lagna-Based Monthly Horoscope & Life Matrix"
    card_sub = f"<b>{lagna_name}</b> ({chart_info['lagna_deg']}) हेतु 12-भाव आधारित सटीक गोचर भविष्यकथन।" if is_hi else f"Precision 12-Bhava predictive analysis for <b>{lagna_name}</b> ({chart_info['lagna_deg']})."

    render_html(f"""
    <div class="light-card-profile" style="margin-bottom:1rem;">
        <div style="font-weight:900; font-size:1.3rem; color:#9a3412; margin-bottom:0.3rem;">
            {card_header}
        </div>
        <div style="font-size:0.94rem; color:#475569;">
            {card_sub}
        </div>
    </div>
    """)

    now = datetime.datetime.now()
    curr_mid = now.replace(day=15, hour=12, minute=0, second=0)
    curr_month_str = now.strftime("%B %Y")
    
    if now.month == 12:
        next_mid = now.replace(year=now.year + 1, month=1, day=15, hour=12, minute=0, second=0)
    else:
        next_mid = now.replace(month=now.month + 1, day=15, hour=12, minute=0, second=0)
    next_month_str = next_mid.strftime("%B %Y")

    radio_lbl = "**मासिक फलादेश माह चुनें:**" if is_hi else "**Select Forecast Month:**"
    opt_curr = f"वर्तमान माह ({curr_month_str})" if is_hi else f"Current Month ({curr_month_str})"
    opt_next = f"आगामी माह ({next_month_str})" if is_hi else f"Next Month ({next_month_str})"

    month_choice = st.radio(
        radio_lbl,
        options=[opt_curr, opt_next],
        horizontal=True
    )
    
    target_date = next_mid if opt_next in month_choice else curr_mid
    pred = db.get_dynamic_monthly_prediction(lagna_idx, target_date)

    climate_lbl = "खगोलीय जलवायु एवं गोचर प्रभाव" if is_hi else "ASTROLOGICAL CLIMATE"

    render_html(f"""
    <div class="auth-hero-box" style="margin-bottom:1.2rem;">
        <div style="font-size:0.85rem; color:#b45309; font-weight:800; text-transform:uppercase;">{climate_lbl} • {pred['month_name'].upper()}</div>
        <div style="font-size:1.05rem; font-weight:900; color:#92400e; margin-top:4px;">
            {pred['highlight']}
        </div>
    </div>

    <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:1.2rem;">
        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fed7aa; border-left:5px solid #f97316;">
            <b style="color:#9a3412; font-size:0.98rem;">🧘 1. {"आत्मबल एवं स्वास्थ्य (शरीर, ऊर्जा व व्यक्तित्व)" if is_hi else "Self & Vitality (Body, Physique, Energy)"}:</b>
            <div style="font-size:0.92rem; color:#431407; margin-top:3px; line-height:1.6;">{pred['self']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bbf7d0; border-left:5px solid #10b981;">
            <b style="color:#065f46; font-size:0.98rem;">👨‍👩‍👦 2. {"परिवार एवं संचित धन (Liquid Assets & Speech)" if is_hi else "Family & Accumulated Wealth (Liquid Assets & Speech)"}:</b>
            <div style="font-size:0.92rem; color:#14532d; margin-top:3px; line-height:1.6;">{pred['family']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd; border-left:5px solid #0284c7;">
            <b style="color:#0369a1; font-size:0.98rem;">✈️ 3. {"पराक्रम एवं यात्राएं (Short Journeys, Siblings & Courage)" if is_hi else "Travels & Enterprise (Short Journeys, Siblings & Courage)"}:</b>
            <div style="font-size:0.92rem; color:#0c4a6e; margin-top:3px; line-height:1.6;">{pred['travels']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fed7aa; border-left:5px solid #ea580c;">
            <b style="color:#9a3412; font-size:0.98rem;">🏡 4. {"भूमि, भवन एवं सुख (Property, Vehicles & Domestic Peace)" if is_hi else "Property, Vehicles & Domestic Peace (Land & Home)"}:</b>
            <div style="font-size:0.92rem; color:#431407; margin-top:3px; line-height:1.6;">{pred['property']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fde68a; border-left:5px solid #f59e0b;">
            <b style="color:#b45309; font-size:0.98rem;">📚 5. {"संतान एवं उच्च शिक्षा (Intellect & Creative Strategy)" if is_hi else "Children & Higher Study (Intellect & Creative Strategy)"}:</b>
            <div style="font-size:0.92rem; color:#78350f; margin-top:3px; line-height:1.6;">{pred['study']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fecdd3; border-left:5px solid #e11d48;">
            <b style="color:#9f1239; font-size:0.98rem;">📉 6. {"ऋण, शत्रु एवं स्वास्थ्य रक्षा (Immunity & Competitors)" if is_hi else "Loans, Debts & Health Defense (Immunity & Competitors)"}:</b>
            <div style="font-size:0.92rem; color:#881337; margin-top:3px; line-height:1.6;">{pred['loan']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #ddd6fe; border-left:5px solid #8b5cf6;">
            <b style="color:#5b21b6; font-size:0.98rem;">💍 7. {"दांपत्य एवं व्यापारिक साझेदारियाँ (Alliances & Contracts)" if is_hi else "Spouse & Business Partnerships (Alliances & Contracts)"}:</b>
            <div style="font-size:0.92rem; color:#3b0764; margin-top:3px; line-height:1.6;">{pred['spouse']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fecdd3; border-left:5px solid #be123c;">
            <b style="color:#9f1239; font-size:0.98rem;">🔬 8. {"आकस्मिक परिवर्तन एवं शोध (Sudden Shifts & Research Caution)" if is_hi else "Sudden Shifts, Research & Accidents Caution"}:</b>
            <div style="font-size:0.92rem; color:#881337; margin-top:3px; line-height:1.6;">{pred['research']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fde68a; border-left:5px solid #d97706;">
            <b style="color:#92400e; font-size:0.98rem;">🍀 9. {"भाग्य, धर्म एवं गुरु कृपा (Higher Journeys & Fortune)" if is_hi else "Luck, Dharma & Mentorship (Higher Journeys & Fortune)"}:</b>
            <div style="font-size:0.92rem; color:#78350f; margin-top:3px; line-height:1.6;">{pred['luck']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #bae6fd; border-left:5px solid #0284c7;">
            <b style="color:#0369a1; font-size:0.98rem;">💼 10. {"करियर, पद एवं अधिकार (Authority & Standing)" if is_hi else "Career, Job & Executive Stature (Authority & Standing)"}:</b>
            <div style="font-size:0.92rem; color:#0c4a6e; margin-top:3px; line-height:1.6;">{pred['career']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #bbf7d0; border-left:5px solid #059669;">
            <b style="color:#065f46; font-size:0.98rem;">💰 11. {"आय, लाभ एवं नेटवर्क (Profits & Aspirations)" if is_hi else "Gains, Inflows & Network Circles (Profits & Aspirations)"}:</b>
            <div style="font-size:0.92rem; color:#14532d; margin-top:3px; line-height:1.6;">{pred['gains']}</div>
        </div>

        <div style="background:#ffffff; border-radius:12px; padding:14px; border:1.5px solid #ddd6fe; border-left:5px solid #6d28d9;">
            <b style="color:#5b21b6; font-size:0.98rem;">🌐 12. {"व्यय, विदेशी संबंध एवं मोक्ष (Expenditure & Overseas Settlements)" if is_hi else "Expenditure, Foreign Linkages & Overseas Settlements"}:</b>
            <div style="font-size:0.92rem; color:#3b0764; margin-top:3px; line-height:1.6;">{pred['foreign']}</div>
        </div>
    </div>
    """)

# views/monthly.py - Dedicated Monthly Horoscope View with Complete Bilingual Support
import streamlit as st
import datetime
import databanks as db

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

# Comprehensive Bilingual Monthly Prediction Translations
MONTHLY_TRANSLATIONS_HI = {
    "Mesha": "मेष (Aries)", "Vrishabha": "वृषभ (Taurus)", "Mithuna": "मिथुन (Gemini)",
    "Karka": "कर्क (Cancer)", "Simha": "सिंह (Leo)", "Kanya": "कन्या (Virgo)",
    "Tula": "तुला (Libra)", "Vrishchika": "वृश्चिक (Scorpio)", "Dhanu": "धनु (Sagittarius)",
    "Makara": "मकर (Capricorn)", "Kumbha": "कुंभ (Aquarius)", "Meena": "मीन (Pisces)",
    
    "self": {"title": "🧘 1. आत्मबल एवं स्वास्थ्य (Self & Vitality):", "hi_desc": "शारीरिक ऊर्जा, व्यक्तिगत प्राथमिकताओं और आत्मविश्वास का पुनर्गठन। आत्म-अनुशासन बनाए रखें और कार्यस्थल पर अपनी उपस्थिति को मजबूत करें।"},
    "family": {"title": "👨‍👩‍👦 2. परिवार एवं संचित धन (Family & Wealth):", "hi_desc": "पारिवारिक सौहार्द और वाणी में संयम की आवश्यकता। वित्तीय मामलों में संचित संपत्तियों का प्रबंधन विवेकपूर्ण ढंग से करें।"},
    "travels": {"title": "✈️ 3. पराक्रम एवं यात्राएं (Travels & Enterprise):", "hi_desc": "छोटे व लाभकारी व्यावसायिक सफर। साहस और तकनीकी उद्यमों में नए संपर्कों से लाभ की प्राप्ति होगी।"},
    "property": {"title": "🏡 4. भूमि, भवन एवं सुख (Property & Domestic Peace):", "hi_desc": "घरेलू वातावरण में स्थिरता लाने के प्रयास सफल होंगे। चल-अचल संपत्ति से जुड़े मामलों में कागजी कार्रवाई की जांच अवश्य करें।"},
    "study": {"title": "📚 5. संतान एवं उच्च शिक्षा (Children & Higher Study):", "hi_desc": "बौद्धिक तीक्ष्णता और रचनात्मक रणनीतियों में सफलता। विद्यार्थियों और उच्च शिक्षा के शोधकर्ताओं के लिए प्रगतिशील समय।"},
    "loan": {"title": "📉 6. ऋण, शत्रु एवं स्वास्थ्य रक्षा (Loans & Health Defense):", "hi_desc": "प्रतिद्वंद्वियों पर विजय और पुराने कर्ज चुकाने के अवसर। प्रतिरक्षा प्रणाली (Immunity) को मजबूत रखने हेतु खान-पान पर ध्यान दें।"},
    "spouse": {"title": "💍 7. दांपत्य एवं व्यापारिक साझेदारियाँ (Partnerships & Contracts):", "hi_desc": "व्यापारिक अनुबंधों और वैवाहिक जीवन में संवाद की स्पष्टता बनाए रखें। आपसी सहयोग से दीर्घकालिक लाभ मिलेंगे।"},
    "research": {"title": "🔬 8. आकस्मिक परिवर्तन एवं शोध (Sudden Shifts & Research):", "hi_desc": "गूढ़ विज्ञान, अनुसंधान और तकनीक के क्षेत्र में अप्रत्याशित लाभ। जोखिम भरे वित्तीय शॉर्टकट से पूरी तरह दूर रहें।"},
    "luck": {"title": "🍀 9. भाग्य, धर्म एवं गुरु कृपा (Luck & Dharma):", "hi_desc": "उच्च यात्राओं, आध्यात्मिक उन्नति और वरिष्ठ आचार्यों के मार्गदर्शन से भाग्य का पूर्ण सहयोग प्राप्त होगा।"},
    "career": {"title": "💼 10. करियर, पद एवं अधिकार (Career & Authority):", "hi_desc": "कार्यक्षेत्र में प्रतिष्ठा, प्राधिकार और प्रशासनिक जिम्मेदारियों में वृद्धि। वरिष्ठ अधिकारियों से सहयोग प्राप्त होगा।"},
    "gains": {"title": "💰 11. आय, लाभ एवं नेटवर्क (Gains & Network Circles):", "hi_desc": "वित्तीय आय के नए स्रोत खुलने और बड़े सामाजिक नेटवर्क से व्यावसायिक लाभ मिलने का प्रबल योग है।"},
    "foreign": {"title": "🌐 12. व्यय, विदेशी संबंध एवं मोक्ष (Expenditure & Foreign Linkages):", "hi_desc": "विदेशी संपर्कों या दूरस्थ स्थानों से लाभ। आध्यात्मिक साधना और व्यय नियंत्रण पर विशेष ध्यान दें।"}
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
    
    disp_lagna = lagna_name
    for en_k, hi_v in MONTHLY_TRANSLATIONS_HI.items():
        if en_k in lagna_name and is_hi:
            disp_lagna = hi_v

    card_header = "📅 लग्न-आधारित मासिक राशिफल एवं जीवन मैट्रिक्स" if is_hi else "📅 Lagna-Based Monthly Horoscope & Life Matrix"
    card_sub = f"<b>{disp_lagna}</b> ({chart_info['lagna_deg']}) हेतु 12-भाव आधारित सटीक गोचर भविष्यकथन।" if is_hi else f"Precision 12-Bhava predictive analysis for <b>{lagna_name}</b> ({chart_info['lagna_deg']})."

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
    
    # Translate highlight text if Hindi is active
    highlight_text = pred['highlight']
    if is_hi:
        highlight_text = "इस माह गोचर ग्रहों का प्रभाव आपके जीवन में कार्यकुशलता, पेशेवर स्थिरता और आंतरिक संतुलन स्थापित करने पर केंद्रित है। दीर्घकालिक निवेश और रिश्तों में संवाद को प्राथमिकता दें।"

    keys_list = ["self", "family", "travels", "property", "study", "loan", "spouse", "research", "luck", "career", "gains", "foreign"]
    
    domain_cards_html = ""
    for k in keys_list:
        meta = MONTHLY_TRANSLATIONS_HI[k]
        desc_txt = MONTHLY_TRANSLATIONS_HI[k]["hi_desc"] if is_hi else pred[k]
        
        domain_cards_html += f"""
        <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1.5px solid #fed7aa; border-left:5px solid #f97316; margin-bottom:10px;">
            <b style="color:#9a3412; font-size:0.98rem;">{meta['title']}</b>
            <div style="font-size:0.92rem; color:#431407; margin-top:3px; line-height:1.6;">{desc_txt}</div>
        </div>
        """

    render_html(f"""
    <div class="auth-hero-box" style="margin-bottom:1.2rem;">
        <div style="font-size:0.85rem; color:#b45309; font-weight:800; text-transform:uppercase;">{climate_lbl} • {pred['month_name'].upper()}</div>
        <div style="font-size:1.05rem; font-weight:900; color:#92400e; margin-top:4px;">
            {highlight_text}
        </div>
    </div>

    <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:1.2rem;">
        {domain_cards_html}
    </div>
    """)

# views/mantra.py - Dedicated Mantra Sadhana & Digital Japa Mala View with Complete Bilingual Support
import streamlit as st
from databanks import (
    NAVAGRAHA_BEEJ_MANTRAS,
    NAKSHATRA_BEEJ_MANTRAS,
    NAKSHATRAS
)

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

NAKSHATRA_NAMES_HI = {
    "Ashwini": "अश्विनी", "Bharani": "भरणी", "Krittika": "कृत्तिका",
    "Rohini": "रोहिणी", "Mrigashira": "मृगशिरा", "Ardra": "आर्द्रा",
    "Punarvasu": "पुनर्वसु", "Pushya": "पुष्य", "Ashlesha": "आश्लेषा",
    "Magha": "मघा", "Purva Phalguni": "पूर्वा फाल्गुनी", "Uttara Phalguni": "उत्तरा फाल्गुनी",
    "Hasta": "हस्त", "Chitra": "चित्रा", "Swati": "स्वाति",
    "Vishakha": "विशाखा", "Anuradha": "अनुराधा", "Jyeshtha": "ज्येष्ठा",
    "Mula": "मूल", "Purva Ashadha": "पूर्वाषाढ़ा", "Uttara Ashadha": "उत्तराषाढ़ा",
    "Shravana": "श्रवण", "Dhanishta": "धनिष्ठा", "Shatabhisha": "शतभिषा",
    "Purva Bhadrapada": "पूर्वाभाद्रपद", "Uttara Bhadrapada": "उत्तराभाद्रपद", "Revati": "रेवती"
}

CLASSICAL_MANTRAS_BILINGUAL = {
    "Maha Mrityunjaya Mantra (Supreme Protection)": {
        "title_hi": "महामृत्युंजय मंत्र (सर्वोच्च सुरक्षा एवं आरोग्य)",
        "sanskrit": "ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम्।\nउर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात्॥",
        "translit": "Om Tryambakam Yajamahe Sugandhim Pushti-Vardhanam |\nUrvarukamiva Bandhanan-Mrityor-Mukshiya Maamritat ||",
        "meaning_en": "We meditate on the Three-Eyed Lord Shiva, who permeates and nourishes all beings. May He liberate us from the bonds of fear and death into immortality.",
        "meaning_hi": "हम त्रिनेत्र भगवान शिव का ध्यान करते हैं, जो समस्त संसार का पोषण करते हैं। जिस प्रकार ककड़ी अपनी बेल से पककर स्वाभाविक रूप से मुक्त हो जाती है, वैसे ही वे हमें मृत्यु और भय से मुक्त कर मोक्ष प्रदान करें।",
        "rules_en": "• Best chanted at dawn or dusk facing East or North.\n• Use a Rudraksha Mala.\n• Pacifies severe transit friction (Vipat, Vadha) and shields cellular vitality.",
        "rules_hi": "• प्रातःकाल या गोधूलि बेला में पूर्व या उत्तर की ओर मुख करके जप करें।\n• रुद्राक्ष की माला का प्रयोग करें।\n• यह गोचर जनित बाधाओं (विपत, निधन तारा) को शांत करता है।"
    },
    "Gayatri Mantra (Solar Illumination)": {
        "title_hi": "गायत्री मंत्र (दिव्य बुद्धि एवं तेजोवृद्धि)",
        "sanskrit": "ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात्॥",
        "translit": "Om Bhur Bhuvah Swah Tat Savitur Varenyam Bhargo Devasya Dheemahi Dhiyo Yo Nah Prachodayat ||",
        "meaning_en": "We meditate upon the supreme divine brilliance of the Sun who illuminates the inner cosmos. May that divine light awaken and inspire our intellect.",
        "meaning_hi": "हम उस प्राणस्वरूप, दुःखनाशक, सुखस्वरूप, श्रेष्ठ, तेजस्वी पापनाशक देव (सूर्य) का ध्यान करते हैं। वे हमारी बुद्धियों को सन्मार्ग की ओर प्रेरित करें।",
        "rules_en": "• Best chanted during Brahma Muhurta or at sunrise facing East.\n• Use a Tulsi or Sandalwood Mala.\n• Enhances mental clarity, vitality, and cellular healing.",
        "rules_hi": "• ब्रह्म मुहूर्त या सूर्योदय के समय पूर्व दिशा की ओर मुख करके जप करें।\n• तुलसी या चंदन की माला का प्रयोग करें।\n• यह मानसिक स्पष्टता और प्राण ऊर्जा को तीव्र करता है।"
    },
    "Vishnu Sahasranama Shloka (Aura Shield)": {
        "title_hi": "विष्णु सहस्रनाम श्लोक (दिव्य कवच एवं शांति)",
        "sanskrit": "ॐ नमो भगवते वासुदेवाय॥",
        "translit": "Om Namo Bhagavate Vasudevaya ||",
        "meaning_en": "Salutations to the Supreme Preserver of the Cosmos who dwells within all living hearts.",
        "meaning_hi": "समस्त जीवों के हृदय में निवास करने वाले ब्रह्मांड के सर्वोच्च पालक भगवान वासुदेव को नमन।",
        "rules_en": "• Chant in the morning facing East.\n• Harmonizes favorable transits (Sampat, Sadhana, Ati-Mitra).\n• Brings peace to the home and liquid capital stability.",
        "rules_hi": "• प्रातःकाल पूर्व दिशा की ओर मुख करके जप करें।\n• यह अनुकूल गोचर (सम्पत, साधना, अति-मित्र) को और अधिक पुष्ट करता है।"
    }
}

def render_page_mantra():
    prof = st.session_state.get("user_profile", {})
    current_lang = prof.get("lang", "en")
    is_hi = (current_lang == "hi")
    chart_info = st.session_state.get("chart_info", {})

    header_title = "📿 जप साधना एवं वैदिक मंत्र अभयारण्य" if is_hi else "📿 Japa Sadhana & Vedic Mantra Sanctuary"
    header_desc = "सर्वोच्च क्लासिकल मंत्रों, 9 नवग्रह बीज मंत्रों, अथवा अपने व्यक्तिगत जन्म नक्षत्र बीज मंत्र का चयन करें और 108-मनका डिजिटल माला काउंटर के साथ जप करें।" if is_hi else "Select from Supreme Classical Mantras, the 9 Navagraha Planetary Beej Mantras, or your personalized Birth Nakshatra Beej Mantra to chant with the 108-bead digital Mala counter."

    render_html(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.35rem; color:#5b21b6; margin-bottom:0.4rem;">
            {header_title}
        </div>
        <div style="font-size:0.95rem; color:#475569; line-height:1.6;">
            {header_desc}
        </div>
    </div>
    """)

    cat_label = "**मंत्र श्रेणी चुनें:**" if is_hi else "**Select Mantra Category:**"
    cat_opts = ["शास्त्रीय एवं सुरक्षा मंत्र" if is_hi else "Classical & Protection", "9 नवग्रह बीज मंत्र" if is_hi else "9 Navagraha Beej Mantras", "27 जन्म नक्षत्र बीज मंत्र" if is_hi else "27 Nakshatra Beej Mantras"]

    category = st.radio(cat_label, options=cat_opts, horizontal=True)

    if category in ["Classical & Protection", "शास्त्रीय एवं सुरक्षा मंत्र"]:
        sel_label = "शास्त्रीय मंत्र चुनें:" if is_hi else "Choose Classical Mantra:"
        keys_list = list(CLASSICAL_MANTRAS_BILINGUAL.keys())
        display_keys = [(m.split('(')[0].strip() if not is_hi else CLASSICAL_MANTRAS_BILINGUAL[m]['title_hi']) for m in keys_list]
        choice_idx = st.selectbox(sel_label, options=range(len(keys_list)), format_func=lambda x: display_keys[x])
        raw_key = keys_list[choice_idx]
        item = CLASSICAL_MANTRAS_BILINGUAL[raw_key]
        
        m_sanskrit = item['sanskrit']
        m_translit = item['translit']
        m_meaning = item['meaning_hi'] if is_hi else item['meaning_en']
        m_rules = item['rules_hi'] if is_hi else item['rules_en']

    elif category in ["9 Navagraha Beej Mantras", "9 नवग्रह बीज मंत्र"]:
        sel_label = "ग्रह बीज मंत्र चुनें:" if is_hi else "Choose Planetary Beej Mantra:"
        graha_keys = list(NAVAGRAHA_BEEJ_MANTRAS.keys())
        graha_choice = st.selectbox(sel_label, options=graha_keys)
        item = NAVAGRAHA_BEEJ_MANTRAS[graha_choice]
        
        m_sanskrit = item['sanskrit']
        m_translit = item['translit']
        m_meaning = item['meaning'] if not is_hi else f"{graha_choice} ग्रह का बीज मंत्र, जो मानसिक शांति, शक्ति और तात्विक संतुलन प्रदान करता है।"
        m_rules = item['rules'] if not is_hi else "• संबंधित वार या प्रतिदिन नित्य नियम से जप करें।"

    else:
        sel_label = "नक्षत्र बीज मंत्र चुनें:" if is_hi else "Choose Nakshatra Beej Mantra:"
        nak_options = {idx: (f"{NAKSHATRA_NAMES_HI.get(data['name'], data['name'])})" if is_hi else data['name']) for idx, data in NAKSHATRA_BEEJ_MANTRAS.items()}
        default_idx = (chart_info.get("star_idx", 1) - 1) if chart_info else 0
        
        selected_star_idx = st.selectbox(
            sel_label,
            options=list(nak_options.keys()),
            format_func=lambda x: nak_options[x],
            index=default_idx
        )
        item = NAKSHATRA_BEEJ_MANTRAS[selected_star_idx]
        m_sanskrit = item['sanskrit']
        m_translit = item['translit']
        m_meaning = item['meaning']
        m_rules = item['rules']

    meaning_lbl = "📜 अर्थ:" if is_hi else "📜 Meaning:"
    sadhana_lbl = "🧘 साधना निर्देश:" if is_hi else "🧘 Sadhana Guidelines:"

    render_html(f"""
    <div style="background:#ffffff; border:1.5px solid #ddd6fe; border-radius:14px; padding:18px; margin:14px 0; box-shadow:0 3px 12px rgba(139,92,246,0.06);">
        <div style="font-size:1.4rem; font-weight:900; color:#1e1b4b; text-align:center; font-family:serif; line-height:1.6; white-space:pre-line;">
            {m_sanskrit}
        </div>
        <div style="font-size:0.95rem; color:#6d28d9; text-align:center; font-style:italic; margin-top:8px; line-height:1.5; white-space:pre-line;">
            {m_translit}
        </div>
        <hr style="margin:14px 0; border:none; border-top:1px solid #ede9fe;">
        <div style="font-size:0.93rem; color:#334155; line-height:1.7;">
            <b>{meaning_lbl}</b> {m_meaning}<br><br>
            <b>{sadhana_lbl}</b><br>{m_rules.replace(chr(10), '<br>')}
        </div>
    </div>
    """)

    mala_title = f"📿 डिजिटल माला: **{st.session_state.get('japa_count', 0)} / 108** मनके" if is_hi else f"📿 Digital Mala: **{st.session_state.get('japa_count', 0)} / 108** Beads"
    progress_text = f"माला प्रगति: {int(min(1.0, st.session_state.get('japa_count', 0) / 108.0) * 100)}% | पूर्ण मालाएं: {st.session_state.get('mala_rounds', 0)}" if is_hi else f"Mala Progress: {int(min(1.0, st.session_state.get('japa_count', 0) / 108.0) * 100)}% | Completed Malas: {st.session_state.get('mala_rounds', 0)}"

    with st.container(border=True):
        st.markdown(f"### {mala_title}")
        progress_val = min(1.0, st.session_state.get('japa_count', 0) / 108.0)
        st.progress(progress_val, text=progress_text)

        col_tap, col_reset = st.columns([2, 1])
        with col_tap:
            tap_btn_lbl = "📿 मनका गिनें (+1)" if is_hi else "📿 Tap Bead (+1)"
            if st.button(tap_btn_lbl, type="primary", use_container_width=True):
                st.session_state.japa_count = st.session_state.get('japa_count', 0) + 1
                if st.session_state.japa_count >= 108:
                    st.session_state.japa_count = 0
                    st.session_state.mala_rounds = st.session_state.get('mala_rounds', 0) + 1
                    st.balloons()
                    succ_msg = "🎉 ॐ शांति! आपने 1 पूर्ण माला (108 जप) पूरी कर ली है।" if is_hi else "🎉 Om Shanti! You completed 1 full Mala (108 Chants)."
                    st.success(succ_msg)
                st.rerun()
        with col_reset:
            reset_btn_lbl = "🔄 रीसेट करें" if is_hi else "🔄 Reset Counter"
            if st.button(reset_btn_lbl, use_container_width=True):
                st.session_state.japa_count = 0
                st.session_state.mala_rounds = 0
                st.rerun()

# views/numerology.py - Dedicated Numerology View with Full Hindi & English Support
import streamlit as st
from databanks import (
    get_numerology_life_domains,
    get_numerology_avoidance,
    NUM_PLANET_NAMES
)

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

def render_page_numerology():
    if not st.session_state.get("has_valid_profile", False):
        is_hi = st.session_state.get("user_profile", {}).get("lang", "en") == "hi"
        prompt_title = "अपनी जन्म पत्रिका प्रोफाइल सेट करें" if is_hi else "Set Up Your Vedic Birth Profile"
        prompt_desc = "अंकशास्त्र और मूलांक-भाग्यांक की गणना के लिए यूज़र प्रोफाइल टैब में अपना जन्म विवरण भरें।" if is_hi else "To calculate your Numerology blueprint, please enter your birth details in the User Profile tab."
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

    current_lang = st.session_state.get("user_profile", {}).get("lang", "en")
    is_hi = (current_lang == "hi")
    mulank = st.session_state.get("mulank", 1)
    bhagyank = st.session_state.get("bhagyank", 1)
    namank = st.session_state.get("namank", 1)

    num_domains = get_numerology_life_domains(mulank, bhagyank, namank, current_lang)
    avoid_data = get_numerology_avoidance(mulank, bhagyank, current_lang)
    p_m_label = NUM_PLANET_NAMES.get(mulank, {}).get(current_lang, f"Planet {mulank}")
    p_b_label = NUM_PLANET_NAMES.get(bhagyank, {}).get(current_lang, f"Planet {bhagyank}")
    p_n_label = NUM_PLANET_NAMES.get(namank, {}).get(current_lang, f"Planet {namank}")

    cautions_html = "".join(f"<li style='margin-bottom:5px;'>{c}</li>" for c in avoid_data['cautions'])

    card_title = "🔢 मुख्य अंकशास्त्रीय ब्लूप्रिंट" if is_hi else "🔢 Core Numerology Blueprint"
    lbl_mul = "मूलांक (Driver)" if is_hi else "Mulank (Driver)"
    lbl_bhag = "भाग्यांक (Destiny)" if is_hi else "Bhagyank (Destiny)"
    lbl_nam = "नामांक (Name Vibration)" if is_hi else "Namank (Name Vibration)"

    render_html(f"""
    <div class="light-card-num">
        <div style="font-weight:900; font-size:1.25rem; color:#065f46; margin-bottom:1rem; border-bottom:2px solid #bbf7d0; padding-bottom:0.5rem;">
            <span>{card_title}</span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.15rem;">
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900;">{lbl_mul}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46;">{mulank}</div>
                <div style="font-size:0.88rem; color:#059669; font-weight:800;">{p_m_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900;">{lbl_bhag}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46;">{bhagyank}</div>
                <div style="font-size:0.88rem; color:#059669; font-weight:800;">{p_b_label}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:12px; border:1.5px solid #dcfce7;">
                <div style="font-size:0.85rem; color:#047857; font-weight:900;">{lbl_nam}</div>
                <div style="font-size:1.85rem; font-weight:900; color:#065f46;">{namank}</div>
                <div style="font-size:0.88rem; color:#059669; font-weight:800;">{p_n_label}</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr; gap:12px; margin-bottom:1.15rem;">
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #059669;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['career_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['career_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #10b981;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['wealth_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['wealth_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #14b8a6;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['rel_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['rel_desc']}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #0d9488;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{num_domains['health_title']}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{num_domains['health_desc']}</div>
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:12px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:8px;">{num_domains['luck_title']}</div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.95rem; line-height:1.6;">
                <div><b>✨ {"शुभ अंक" if is_hi else "Lucky Numbers"}:</b> {num_domains['lucky_num']}</div>
                <div><b>⚠️ {"सतर्कता अंक" if is_hi else "Caution Numbers"}:</b> {num_domains['avoid_num']}</div>
                <div><b>📅 {"शुभ दिन" if is_hi else "Auspicious Days"}:</b> {num_domains['lucky_days']}</div>
                <div><b>🧭 {"अनुकूल दिशा" if is_hi else "Favorable Direction"}:</b> {num_domains['lucky_dir']}</div>
                <div style="grid-column: 1 / -1;"><b>🎨 {"ऊर्जावान रंग" if is_hi else "Energizing Colors"}:</b> {num_domains['lucky_colors']}</div>
            </div>
        </div>

        <div style="background:#fff1f2; border-radius:12px; padding:14px; border:1.5px solid #fecdd3; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.08rem; color:#9f1239; margin-bottom:8px;">{avoid_data['avoid_title']}</div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; font-size:0.93rem; line-height:1.6; margin-bottom:10px;">
                <div><b>🚫 {"बचने योग्य अंक" if is_hi else "Numbers to Avoid"}:</b> {avoid_data['avoid_numbers']}</div>
                <div><b>🎨 {"बचने योग्य रंग" if is_hi else "Colors to Avoid"}:</b> {avoid_data['avoid_colors']}</div>
                <div><b>📅 {"प्रतिकूल दिन" if is_hi else "Unfavorable Days"}:</b> {avoid_data['avoid_days']}</div>
                <div><b>🧭 {"बचने योग्य दिशा" if is_hi else "Direction to Avoid"}:</b> {avoid_data['avoid_directions']}</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border-left:4px solid #e11d48;">
                <b style="color:#9f1239; font-size:0.95rem;">{"⚠️ महत्वपूर्ण रणनीतिक एवं व्यवहारिक सावधानियां:" if is_hi else "⚠️ Critical Behavioral & Strategic Don'ts:"}</b>
                <ul style="margin:4px 0 0 0; padding-left:1.2rem; font-size:0.92rem; color:#881337; line-height:1.6;">
                    {cautions_html}
                </ul>
            </div>
        </div>

        <div style="background:#f0fdf4; border-radius:12px; padding:14px; border:1.5px solid #bbf7d0;">
            <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:6px;">{"🪔 अंकशास्त्रीय संतुलन एवं ग्राउंडिंग उपाय:" if is_hi else "🪔 Numerology Harmony & Grounding Remedies:"}</div>
            <div style="font-size:0.94rem; line-height:1.65; color:#14532d;">
                • <b>{"धातु पात्र ग्राउंडिंग" if is_hi else "Metal Vessel Grounding"}:</b> {"मानसिक चंचलता शांत करने और जैव-विद्युत संतुलन हेतु चांदी या तांबे के बर्तन से जल ग्रहण करें।" if is_hi else "Drink water from a pure silver or copper vessel to pacify nervous restlessness and enhance bio-electrical harmony."}<br>
                • <b>{"कार्यक्षेत्र बायो-शील्ड" if is_hi else "Digital & Workspace Bio-Shield"}:</b> {"अपने कार्यस्थल से उलझे हुए चार्जिंग केबल, टूटे गैजेट्स और बंद घड़ियां हटाएं।" if is_hi else "Remove tangled charging cables, broken electronic gadgets, and inactive clocks from your workspace."}<br>
                • <b>{"नाम कंपन (नामांक)" if is_hi else "Name Resonance (Namank)"}:</b> {"महत्वपूर्ण दस्तावेजों पर हस्ताक्षर करते समय अनुकूल हरे या नीले रंग की स्याही का प्रयोग करें।" if is_hi else f"Use green or blue ink when writing or endorsing important planning documents to harmonize your {namank} name vibration."}
            </div>
        </div>
    </div>
    """)

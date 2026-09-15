# views/shani.py - Dedicated Shani, Paya & Sade Sati View with Complete Bilingual Support
import streamlit as st

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

def render_page_shani():
    if not st.session_state.get("has_valid_profile", False):
        is_hi = st.session_state.get("user_profile", {}).get("lang", "en") == "hi"
        prompt_title = "अपनी जन्म पत्रिका प्रोफाइल सेट करें" if is_hi else "Set Up Your Vedic Birth Profile"
        prompt_desc = "शनि पाया और साढ़े साती की सटीक गणना के लिए यूज़र प्रोफाइल टैब में अपना जन्म विवरण भरें।" if is_hi else "To calculate your Shani Paya and Sade Sati status, please enter your birth details in the User Profile tab."
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

    chart_info = st.session_state.get("chart_info", {})
    shani_paya_data = st.session_state.get("shani_paya_data", {})
    shani_sadesati_data = st.session_state.get("shani_sadesati_data", {})

    m_name = chart_info.get('moon_rashi_name', 'Mesha').split()[0]
    
    # Active badges
    p1_active_tag = '<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">सक्रिय (ACTIVE)</span>' if is_hi and shani_sadesati_data.get('phase_1_active') else ('<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW</span>' if shani_sadesati_data.get('phase_1_active') else '')
    p2_active_tag = '<span style="font-size:0.82rem; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:12px; font-weight:800;">सक्रिय - शिखर (PEAK)</span>' if is_hi and shani_sadesati_data.get('phase_2_active') else ('<span style="font-size:0.82rem; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW (PEAK)</span>' if shani_sadesati_data.get('phase_2_active') else '')
    p3_active_tag = '<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">सक्रिय (ACTIVE)</span>' if is_hi and shani_sadesati_data.get('phase_3_active') else ('<span style="font-size:0.82rem; background:#ede9fe; color:#6d28d9; padding:2px 8px; border-radius:12px; font-weight:800;">ACTIVE NOW</span>' if shani_sadesati_data.get('phase_3_active') else '')

    raw_paya = shani_paya_data.get('paya', '')
    if is_hi:
        if "Swarna" in raw_paya or "Gold" in raw_paya:
            paya_display = "स्वर्ण पाया (Gold Paya — अत्यधिक परिश्रम व मानसिक संघर्ष)"
        elif "Roupya" in raw_paya or "Silver" in raw_paya:
            paya_display = "रौप्य पाया (Silver Paya — मध्यम फलदायक, सुख व सफलता)"
        elif "Tamra" in raw_paya or "Copper" in raw_paya:
            paya_display = "ताम्र पाया (Copper Paya — प्रगति, आय वृद्धि एवं विजय)"
        else:
            paya_display = "लोह पाया (Iron Paya — कड़ा संघर्ष, अनुशासन व परीक्षा)"
    else:
        paya_display = raw_paya

    main_title = "🪐 शनि पाया एवं साढ़े साती संपूर्ण जीवन-क्षेत्र मैट्रिक्स" if is_hi else "🪐 Shani Paya & Sade Sati Exhaustive Life-Domain Matrix"
    saturn_transit = "मीन राशि में शनि गोचर" if is_hi else "Saturn in Pisces (Meena)"
    active_paya_lbl = f"आपकी {m_name.upper()} चन्द्र राशि हेतु वर्तमान गोचर पाया:" if is_hi else f"ACTIVE TRANSIT PAYA FOR YOUR {m_name.upper()} MOON"
    
    raw_status = shani_paya_data.get('status', '')
    if is_hi:
        status_grade = "संघर्षपूर्ण एवं संवेदनशील" if "Challenging" in raw_status else "संतुलित एवं रणनीतिक"
    else:
        status_grade = raw_status

    tone_disp = shani_paya_data.get('tone', '')
    timeline_disp = shani_paya_data.get('timeline', '')
    
    houses_raw = shani_paya_data.get('houses', '2nd')
    if is_hi:
        h_map = {"12th": "द्वादश (12वें)", "1st": "प्रथम (पहले)", "2nd": "द्वितीय (दूसरे)"}
        h_trans = h_map.get(houses_raw, houses_raw)
        desc_disp = f"वर्तमान में शनि आपकी जन्मकालीन चन्द्र राशि से {h_trans} भाव में गोचर कर रहे हैं। यह स्थिति आपके जीवन में दीर्घकालिक अनुशासन, पेशेवर पुनर्गठन और कर्मिक संतुलन की मांग करती है।"
    else:
        desc_disp = shani_paya_data.get('desc', f"Saturn is currently transiting the {houses_raw} house relative to your {m_name} Moon, bringing structural discipline, operational audits, and karmic recalibration.")

    sadesati_title = f"⚖️ {m_name} चन्द्र राशि हेतु सक्रिय साढ़े साती / ढैय्या जीवन-क्षेत्र विश्लेषण" if is_hi else f"⚖️ Active Sade Sati / Dhaiya Life-Domain Breakdown for {m_name} Moon"

    # Localized Paya domain impacts
    if is_hi:
        paya_health = "शारीरिक थकान, जोड़ों में दर्द और अत्यधिक कार्यभार के कारण ऊर्जा स्तर में उतार-चढ़ाव संभव है।"
        paya_wealth = "वित्तीय मामलों में अत्यधिक सावधानी बरतें; सट्टेबाजी, जोखिम भरे निवेश या उधार देने से बचें।"
        paya_family = "घरेलू जिम्मेदारियां बढ़ेंगी; परिजनों के साथ धैर्य और सौम्य संवाद बनाए रखना श्रेष्ठ रहेगा।"
        paya_loan = "नए कर्ज लेने से बचें और पूर्व के ऋणों को समय पर चुकाने की व्यावहारिक योजना बनाएं।"
        paya_partner = "व्यापारिक साझेदारियों में पारदर्शिता रखें और किसी पर भी आँख मूंदकर भरोसा न करें।"
        paya_luck = "भाग्य के भरोसे न बैठकर अपने पुरुषार्थ और निरंतर अनुशासन पर पूर्ण विश्वास रखें।"
        paya_career = "कार्यालय में उच्चाधिकारियों से सामंजस्य रखें; वरिष्ठों व अनुभवी सलाहकारों का मार्गदर्शन आपके हित में रहेगा।"
        paya_protocol = "नियमित शनि बीज मंत्र का जप करें और शनिवार को काले तिल, सरसों का तेल अथवा वस्त्र का दान करें।"
    else:
        paya_health = shani_paya_data.get('health', '')
        paya_wealth = shani_paya_data.get('wealth', '')
        paya_family = shani_paya_data.get('family', '')
        paya_loan = shani_paya_data.get('loan', '')
        paya_partner = shani_paya_data.get('partner', '')
        paya_luck = shani_paya_data.get('luck', '')
        paya_career = shani_paya_data.get('career', '')
        paya_protocol = shani_paya_data.get('protocol', '')

    # Localized Sade Sati domain impacts
    if is_hi:
        ss_health = "मानसिक तनाव व थकान से बचने के लिए योग, ध्यान और पर्याप्त विश्राम को अपनी दिनचर्या में शामिल करें।"
        ss_wealth = "वित्तीय अनुशासन अपनाएं, अनावश्यक खर्चों पर लगाम लगाएं और दीर्घकालिक संपत्तियों में सुरक्षित निवेश करें।"
        ss_family = "परिवार के साथ गुणवत्तापूर्ण समय बिताएं; घरेलू मामलों में अहंकार के टकराव से बचें।"
        ss_loan = "क्रेडिट कार्ड या भारी ब्याज वाले ऋणों के जाल में फंसने से पूरी तरह सतर्क रहें।"
        ss_partner = "व्यापारिक साझेदारियों में सभी कानूनी शर्तों और समझौतों को लिखित रूप में स्पष्ट रखें।"
        ss_luck = "प्रगति की धीमी गति से निराश न हों; यह काल आपके व्यक्तित्व को दीर्घकालिक सफलता के लिए परिपक्व कर रहा है।"
        ss_career = "धैर्य बनाए रखें, शॉर्टकट से बचें और अपने कार्य में उच्च कोटि की गुणवत्ता व ईमानदारी बरतें।"
        ss_remedy = "शनिवार की संध्या को पीपल के वृक्ष के नीचे सरसों के तेल का दीपक प्रज्वलित करें और हनुमान चालीसा का पाठ करें।"
    else:
        ss_health = shani_sadesati_data.get('health', '')
        ss_wealth = shani_sadesati_data.get('wealth', '')
        ss_family = shani_sadesati_data.get('family', '')
        ss_loan = shani_sadesati_data.get('loan', '')
        ss_partner = shani_sadesati_data.get('partner', '')
        ss_luck = shani_sadesati_data.get('luck', '')
        ss_career = shani_sadesati_data.get('career', '')
        ss_remedy = shani_sadesati_data.get('remedy', '')

    r12 = shani_sadesati_data.get('rashi_12th', '12th')
    r1st = shani_sadesati_data.get('rashi_1st', '1st')
    r2nd = shani_sadesati_data.get('rashi_2nd', '2nd')

    # Phase 1, 2, 3 dynamic localized subtitles and bullet points
    if is_hi:
        p1_title = f"प्रथम चरण: उदय काल (शनि {r12} राशि / चन्द्र से 12वें भाव में)"
        p2_title = f"द्वितीय चरण: शिखर काल (शनि {r1st} राशि / जन्म चन्द्र के ऊपर)"
        p3_title = f"तृतीय चरण: अस्त काल (शनि {r2nd} राशि / चन्द्र से दूसरे भाव में)"
        
        p1_dyn = "मानसिक पुनर्गठन, अंतर्मुखता, और व्यय नियंत्रण का काल।"
        p1_fin = "यात्राओं, निवेश या स्वास्थ्य संबंधी खर्चों में वृद्धि; कार्य पर्दे के पीछे से होते हैं।"
        p1_kar = "पुरानी मानसिक बाधाओं को छोड़कर भविष्य के लिए मानसिक रूप से तैयार होना।"
        
        p2_dyn = "चरित्र एवं सहनशक्ति की कड़ी परीक्षा। अहंकार का शमन एवं आत्म-सत्य की खोज।"
        p2_fin = "कार्यभार की अधिकता, महत्वपूर्ण निर्णयों का दबाव और नेतृत्व संबंधी एकाग्रता।"
        p2_kar = "भावनात्मक दृढ़ता, शारीरिक अनुशासन और परिपक्वता का विकास।"

        p3_dyn = "मानसिक दबाव में कमी, अर्जित ज्ञान का स्थिरीकरण और पारिवारिक सौहार्द की बहाली।"
        p3_fin = "धन लाभ, संपत्ति की प्राप्ति, वाणी में संयम और विलंबित मान्यता (delayed recognition) की प्राप्ति।"
        p3_kar = "पूर्व संघर्षों के अनुभवों को ठोस सफलता और दीर्घकालिक सुरक्षा में बदलना।"

        ss_status_title = shani_sadesati_data.get('status_title', '')
        if "Sade Sati" in ss_status_title:
            ss_status_display = ss_status_title.replace("Active Sade Sati", "सक्रिय शनि साढ़े साती").replace("Phase", "चरण").replace("Peak", "शिखर")
        else:
            ss_status_display = ss_status_title.replace("Active Saturn Dhaiya", "सक्रिय शनि ढैय्या")
        
        ss_dates = shani_sadesati_data.get('dates', '')
        ss_focus = "अवचेतन शोधन, एकांत, खर्चों में वृद्धि और अलगाव" if "Subconscious" in shani_sadesati_data.get('focus', '') else shani_sadesati_data.get('focus', '')
        ss_impact_text = "शनि वर्तमान में आपकी चन्द्र राशि से मीन राशि में 12वें भाव में गोचर कर रहे हैं। यह व्यक्तिगत प्राथमिकताओं के गहरे पुनर्गठन, व्यर्थ वित्तीय आदतों के त्याग और मानसिक शुद्धि को प्रेरित करता है।" if "transits your 12th house" in shani_sadesati_data.get('impact', '') else shani_sadesati_data.get('impact', '')
    else:
        p1_title = f"Phase 1: Rising Phase (Saturn in {r12} / 12th from Moon)"
        p2_title = f"Phase 2: Peak Janma Shani (Saturn in {r1st} / Over Natal Moon)"
        p3_title = f"Phase 3: Setting Phase (Saturn in {r2nd} / 2nd from Moon)"
        
        p1_dyn = "Subconscious restructuring, elimination of toxic habits, and mental detachment."
        p1_fin = "Spikes in expenses related to travel, relocation, or healthcare; work happens behind the scenes."
        p1_kar = "Shedding psychological baggage and preparing for the core transit."

        p2_dyn = "Crucible of character and endurance. Dissolves false pride and tests emotional truth."
        p2_fin = "Maximum administrative burden, heavy decision-making stress, and executive solitude."
        p2_kar = "Cultivating emotional resilience, physical discipline, and enduring maturity."

        p3_dyn = "Lifting of psychological pressure, consolidation of hard-won wisdom, and stabilizing family harmony."
        p3_fin = "Wealth recovery, acquisition of durable assets, disciplined speech, and delayed recognition."
        p3_kar = "Transforming lessons into lasting institutional stability and financial security."

        ss_status_display = shani_sadesati_data.get('status_title', '')
        ss_dates = shani_sadesati_data.get('dates', '')
        ss_focus = shani_sadesati_data.get('focus', '')
        ss_impact_text = shani_sadesati_data.get('impact', '')

    render_html(f"""
    <div class="light-card-shani">
        <div style="font-weight:900; font-size:1.35rem; color:#5b21b6; margin-bottom:1rem; border-bottom:2px solid #ddd6fe; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{main_title}</span>
            <span style="font-size:0.85rem; background:#ede9fe; color:#5b21b6; padding:4px 10px; border-radius:20px; font-weight:800;">{saturn_transit}</span>
        </div>
        
        <!-- SHANI PAYA IN-DEPTH MATRIX -->
        <div style="background:#f5f3ff; border-radius:14px; padding:16px; border:1.5px solid #e9d5ff; margin-bottom:1.25rem;">
            <div style="font-size:0.85rem; color:#6d28d9; font-weight:800; text-transform:uppercase;">{active_paya_lbl}</div>
            <div style="font-size:1.45rem; font-weight:900; color:#5b21b6; margin:4px 0;">{paya_display}</div>
            <div style="font-size:0.98rem; color:#7c3aed; font-weight:800;">{"स्तर" if is_hi else "Grade"}: {status_grade} | {"ऊर्जा" if is_hi else "Dynamic"}: {tone_disp}</div>
            <div style="font-size:0.92rem; color:#475569; margin-top:3px;"><b>{"सक्रिय समयावधि" if is_hi else "Active Timeline"}:</b> {timeline_disp}</div>
            
            <div style="background:#ffffff; border-radius:12px; padding:12px 14px; border:1px solid #ddd6fe; margin-top:12px; font-size:0.93rem; color:#3b0764; line-height:1.7;">
                <b>🏛️ {"शास्त्रीय आधार" if is_hi else "Classical Foundation"}:</b> {desc_disp}
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-top:12px;">
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #f97316; font-size:0.91rem; color:#7c2d12; line-height:1.6;">
                    <b>🌿 1. {"स्वास्थ्य एवं प्राण ऊर्जा प्रभाव" if is_hi else "Health & Vitality Impact"}:</b><br>{paya_health}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d; line-height:1.6;">
                    <b>💰 2. {"धन संचय एवं नकदी प्रवाह" if is_hi else "Wealth & Cash Flow Dynamics"}:</b><br>{paya_wealth}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764; line-height:1.6;">
                    <b>👨‍👩‍👧‍👦 3. {"पारिवारिक एवं घरेलू सामंजस्य" if is_hi else "Family & Domestic Harmony"}:</b><br>{paya_family}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #e11d48; font-size:0.91rem; color:#881337; line-height:1.6;">
                    <b>📉 4. {"ऋण एवं देनदारियों का प्रबंधन" if is_hi else "Loans & Liabilities Management"}:</b><br>{paya_loan}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #065f46; font-size:0.91rem; color:#065f46; line-height:1.6;">
                    <b>🤝 5. {"व्यापारिक साझेदारियाँ व अनुबंध" if is_hi else "Partnerships & Business Alliances"}:</b><br>{paya_partner}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #d97706; font-size:0.91rem; color:#78350f; line-height:1.6;">
                    <b>🍀 6. {"भाग्य एवं अवसर संरेखण" if is_hi else "Luck & Destiny Alignment"}:</b><br>{paya_luck}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #0284c7; font-size:0.91rem; color:#0369a1; line-height:1.6;">
                    <b>💼 7. {"कर्मक्षेत्र, अधिकार एवं प्रतिष्ठा" if is_hi else "Career, Authority & Executive Standing"}:</b><br>{paya_career}
                </div>
                <div style="background:#ffffff; border-radius:10px; padding:12px; border-left:4px solid #475569; font-size:0.91rem; color:#0f172a; line-height:1.6;">
                    <b>🪔 8. {"लक्षित तत्वीय उपाय एवं सावधानियाँ" if is_hi else "Targeted Elemental Countermeasures"}:</b><br>{paya_protocol}
                </div>
            </div>
        </div>

        <!-- SADE SATI / DHAIYA EXHAUSTIVE MATRIX -->
        <div style="background:#ffffff; border-radius:14px; padding:16px; border:1.5px solid #ddd6fe; margin-bottom:1.25rem;">
            <div style="font-weight:900; font-size:1.2rem; color:#5b21b6; margin-bottom:10px; border-bottom:1px solid #e9d5ff; padding-bottom:5px; display:flex; justify-content:space-between; align-items:center;">
                <span>{sadesati_title}</span>
                <span style="font-size:0.82rem; background:#ede9fe; color:#5b21b6; padding:3px 8px; border-radius:10px; font-weight:800;">{shani_sadesati_data.get('status_title', '').split(':')[0]}</span>
            </div>
            
            <div style="background:{'#fef2f2' if shani_sadesati_data.get('phase_2_active') else '#f5f3ff'}; border-radius:12px; padding:14px; border-left:5px solid {'#ef4444' if shani_sadesati_data.get('phase_2_active') else '#9333ea'}; margin-bottom:14px;">
                <b style="color:{'#991b1b' if shani_sadesati_data.get('phase_2_active') else '#5b21b6'}; font-size:1.1rem;">{ss_status_display}</b>
                <div style="font-size:0.92rem; color:#64748b; margin:3px 0 8px 0;"><b>{"सक्रिय समयावधि" if is_hi else "Active Window"}:</b> {ss_dates} | <b>{"मुख्य फोकस" if is_hi else "Core Focus"}:</b> {ss_focus}</div>
                <div style="font-size:0.95rem; line-height:1.7; color:#334155;">{ss_impact_text}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr; gap:10px; margin-bottom:14px;">
                <div style="background:#fff7ed; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#7c2d12; border-left:4px solid #f97316;">
                    <b>🌿 1. {"स्वास्थ्य प्रभाव" if is_hi else "Health & Vitality Impact"}:</b><br>{ss_health}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#14532d; border-left:4px solid #10b981;">
                    <b>💰 2. {"धन एवं नकदी प्रवाह" if is_hi else "Wealth Dynamics"}:</b><br>{ss_wealth}
                </div>
                <div style="background:#faf5ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#3b0764; border-left:4px solid #8b5cf6;">
                    <b>👨‍👩‍👧‍👦 3. {"परिवार व गृहस्थी" if is_hi else "Family Harmony"}:</b><br>{ss_family}
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#881337; border-left:4px solid #e11d48;">
                    <b>📉 4. {"ऋण व देयताएं" if is_hi else "Loans & Liabilities"}:</b><br>{ss_loan}
                </div>
                <div style="background:#f0fdf4; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#065f46;">
                    <b>🤝 5. {"साझेदारियाँ" if is_hi else "Partnerships"}:</b><br>{ss_partner}
                </div>
                <div style="background:#fffbeb; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#78350f;">
                    <b>🍀 6. {"भाग्य संरेखण" if is_hi else "Destiny Alignment"}:</b><br>{ss_luck}
                </div>
                <div style="background:#f0f9ff; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0369a1;">
                    <b>💼 7. {"करियर व प्रतिष्ठा" if is_hi else "Career Standing"}:</b><br>{ss_career}
                </div>
                <div style="background:#f8fafc; border-radius:10px; padding:10px 12px; font-size:0.91rem; color:#0f172a;">
                    <b>🪔 8. {"उपाय प्रोटोकॉल" if is_hi else "Remedial Protocol"}:</b><br>{ss_remedy}
                </div>
            </div>

            <div style="font-weight:900; font-size:1.05rem; color:#475569; margin:16px 0 8px 0; border-top:1px solid #e9d5ff; padding-top:10px;">
                {"चन्द्र राशि हेतु 7.5-वर्षीय शनि साढ़े साती के तीनों चरण:" if is_hi else f"Complete 7.5-Year Sade Sati Evolutionary Blueprint for {m_name} Moon:"}
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #a855f7; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#5b21b6; font-size:0.96rem;">{p1_title}</b>
                    {p1_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>{"मूल प्रभाव" if is_hi else "Core Dynamic"}:</b> {p1_dyn}<br>
                    • <b>{"आर्थिक एवं करियर" if is_hi else "Financial & Career"}:</b> {p1_fin}<br>
                    • <b>{"कर्मिक सीख" if is_hi else "Karmic Mastery"}:</b> {p1_kar}
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #ef4444; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#991b1b; font-size:0.96rem;">{p2_title}</b>
                    {p2_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>{"मूल प्रभाव" if is_hi else "Core Dynamic"}:</b> {p2_dyn}<br>
                    • <b>{"आर्थिक एवं करियर" if is_hi else "Financial & Career"}:</b> {p2_fin}<br>
                    • <b>{"कर्मिक सीख" if is_hi else "Karmic Mastery"}:</b> {p2_kar}
                </div>
            </div>

            <div style="background:#faf5ff; border-radius:10px; padding:12px; border-left:4px solid #10b981; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#065f46; font-size:0.96rem;">{p3_title}</b>
                    {p3_active_tag}
                </div>
                <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.6;">
                    • <b>{"मूल प्रभाव" if is_hi else "Core Dynamic"}:</b> {p3_dyn}<br>
                    • <b>{"आर्थिक एवं करियर" if is_hi else "Financial & Career"}:</b> {p3_fin}<br>
                    • <b>{"कर्मिक सीख" if is_hi else "Karmic Mastery"}:</b> {p3_kar}
                </div>
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe;">
            <div style="font-weight:900; font-size:1.05rem; color:#5b21b6; margin-bottom:6px;">{"🪔 शनि ग्रह शांति एवं शमन हेतु वैदिक उपाय:" if is_hi else "🪔 Prescribed Remedies for Planetary Neutralization:"}</div>
            <div style="font-size:0.93rem; line-height:1.7; color:#3b0764;">
                • <b>{"मंत्र जप" if is_hi else "Mantra Japa"}:</b> {"शनिवार की संध्या को पश्चिम दिशा की ओर मुख करके 'ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः' मंत्र का 108 बार जप करें।" if is_hi else "Recite the Shani Beej Mantra (ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः) 108 times at twilight on Saturdays facing West."}<br>
                • <b>{"हनुमान साधना" if is_hi else "Vitality Shield"}:</b> {"मानसिक शांति और प्राण ऊर्जा बढ़ाने के लिए प्रतिदिन हनुमान चालीसा का पाठ करें।" if is_hi else "Recite the Hanuman Chalisa daily to boost pranic fire, disperse lethargy, and protect mental peace."}<br>
                • <b>{"दान एवं सेवा" if is_hi else "Charity & Service"}:</b> {"शनिवार के दिन सरसों का तेल, काले तिल अथवा काले वस्त्र असहाय श्रमिकों को दान करें।" if is_hi else "Donate mustard oil, black sesame seeds, or dark blankets to laborers, sweepers, or elderly persons on Saturdays."}<br>
                • <b>{"व्यवहारिक अनुशासन" if is_hi else "Behavioral Grounding"}:</b> {"समय की पाबंदी रखें, विनम्र रहें और अनुबंधों में शॉर्टकट से बचें।" if is_hi else "Practice absolute punctuality, avoid harsh speech, and avoid shortcuts in contractual agreements."}
            </div>
        </div>
    </div>
    """)

    st.write("")
    if st.button("📿 डिजिटल जप माला काउंटर खोलें" if is_hi else "📿 Open Dedicated Digital Japa Counter", type="primary", use_container_width=True):
        st.session_state.current_page = "mantra"
        st.rerun()

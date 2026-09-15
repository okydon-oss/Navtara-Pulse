# views/numerology.py - Dedicated Numerology View with Full Hindi & English Support
import streamlit as st

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

# Complete Bilingual Numerology Blueprint Dictionary (1 to 9)
NUMEROLOGY_CONTENT = {
    1: {
        "planet_en": "Sun (Surya)", "planet_hi": "सूर्य (Surya)",
        "career_en": "Executive Leadership, Government Administration, Corporate Directorship, Entrepreneurship, Public Relations.",
        "career_hi": "कार्यकारी नेतृत्व, सरकारी प्रशासन, कॉर्पोरेट निदेशक पद, उद्यमिता और जनसंपर्क।",
        "wealth_en": "Strong capacity for asset accumulation through independent ventures, real estate, and strategic investments. Avoid speculative gambling.",
        "wealth_hi": "स्वतंत्र उद्यमों, रियल एस्टेट और रणनीतिक निवेश के माध्यम से धन संचय की मजबूत क्षमता। सट्टेबाजी से दूर रहें।",
        "rel_en": "Commands natural respect but requires conscious effort to balance authority with collaborative listening at home.",
        "rel_hi": "प्राकृतिक सम्मान प्राप्त होता है, किंतु घर पर अधिकार और सहयोगात्मक संवाद के बीच संतुलन बनाए रखने के लिए सचेत प्रयास की आवश्यकता है।",
        "health_en": "Vitality is robust, but watch out for inflammatory conditions, high blood pressure, and eye strain.",
        "health_hi": "शारीरिक ऊर्जा मजबूत होती है, किंतु पित्त विकार, उच्च रक्तचाप और नेत्र तनाव से सावधान रहें।"
    },
    2: {
        "planet_en": "Moon (Chandra)", "planet_hi": "चन्द्रमा (Chandra)",
        "career_en": "Diplomacy, Counseling, Hospitality, Fine Arts, Liquid Trading, Healthcare, Human Resources.",
        "career_hi": "कूटनीति, परामर्श, आतिथ्य सत्कार, ललित कला, तरल पदार्थों का व्यापार, स्वास्थ्य सेवाएं और मानव संसाधन।",
        "wealth_en": "Fluctuating cash flows requiring disciplined budgeting; gains through partnerships, advisory roles, and public sectors.",
        "wealth_hi": "अनुशासित बजट की मांग करने वाला उतार-चढ़ाव वाला धन प्रवाह; साझेदारियों, सलाहकार भूमिकाओं और सार्वजनिक क्षेत्रों से लाभ।",
        "rel_en": "Deeply empathetic and nurturing; highly sensitive to emotional friction from close companions.",
        "rel_hi": "अत्यंत सहानुभूतिपूर्ण और देखभाल करने वाले; करीबी साथियों के भावनात्मक व्यवहार के प्रति अत्यधिक संवेदनशील।",
        "health_en": "Prone to mental fatigue, sleep disruption, water-retention, and respiratory sensitivities.",
        "health_hi": "मानसिक थकान, अनिद्रा, जल संचय (कफ) और श्वास संबंधी संवेदनशीलता की प्रवृत्ति।"
    },
    3: {
        "planet_en": "Jupiter (Guru)", "planet_hi": "बृहस्पति (Guru)",
        "career_en": "Teaching, Law, Philosophy, Publishing, Financial Consulting, Management, Mentorship.",
        "career_hi": "अध्यापन, कानून, दर्शनशास्त्र, प्रकाशन, वित्तीय परामर्श, प्रबंधन और मेंटरशिप।",
        "wealth_en": "Expansive financial luck; steady compound wealth accumulation through education, advisory, and ethical investments.",
        "wealth_hi": "विस्तृत वित्तीय भाग्य; शिक्षा, परामर्श और नैतिक निवेश के माध्यम से स्थिर चक्रवृद्धि धन संचय।",
        "rel_en": "Generous and inspiring partner; values intellectual freedom and philosophical alignment in relationships.",
        "rel_hi": "उदार और प्रेरित करने वाले जीवनसाथी; रिश्तों में बौद्धिक स्वतंत्रता और दार्शनिक मेल को महत्व देते हैं।",
        "health_en": "Generally robust constitution; prone to over-indulgence leading to metabolic lethargy or liver sluggishness.",
        "health_hi": "सामान्यतः मजबूत स्वास्थ्य; अत्यधिक खान-पान के कारण चयापचय में सुस्ती या यकृत (लिवर) संबंधी विकार की संभावना।"
    },
    4: {
        "planet_en": "Rahu / Uranus", "planet_hi": "राहु / यूरेनस",
        "career_en": "Engineering, Software Architecture, Research & Development, Logistics, Strategic Planning, Data Science.",
        "career_hi": "इंजीनियरिंग, सॉफ्टवेयर वास्तुकला, अनुसंधान एवं विकास, लॉजिस्टिक्स, रणनीतिक योजना और डेटा विज्ञान।",
        "wealth_en": "Unconventional wealth spikes; requires meticulous legal paperwork and avoidance of unverified shortcuts.",
        "wealth_hi": "अपरंपरागत धन लाभ; इसके लिए सूक्ष्म कानूनी कागजी कार्रवाई और असत्यापित शॉर्टकट से बचना आवश्यक है।",
        "rel_en": "Fiercely loyal but unconventional; needs mental stimulation and trust to prevent suspicion.",
        "rel_hi": "दृढ़ता से वफादार किंतु अपरंपरागत; संदेह से बचने के लिए मानसिक उत्तेजना और आपसी विश्वास की आवश्यकता होती है।",
        "health_en": "Nervous tension, sleep irregularities, and stress-induced fatigue requiring grounding routines.",
        "health_hi": "नसों में तनाव, अनिद्रा और तनाव जनित थकान, जिसके लिए नियमित योग व विश्राम आवश्यक है।"
    },
    5: {
        "planet_en": "Mercury (Budha)", "planet_hi": "बुध (Budha)",
        "career_en": "Media, Commerce, Journalism, Technology, Marketing, Sales, Public Speaking, Translation.",
        "career_hi": "मीडिया, वाणिज्य, पत्रकारिता, प्रौद्योगिकी, विपणन (मार्केटिंग), बिक्री, सार्वजनिक भाषण और अनुवाद।",
        "wealth_en": "Agile cash generation across multiple diverse income streams; rewards multi-channel diversification.",
        "wealth_hi": "कई विविध आय स्रोतों से तेजी से धन अर्जित करना; बहु-चैनल विविधीकरण फायदेमंद रहता है।",
        "rel_en": "Charming, witty, and adaptable; values lively conversation and freedom over rigid domestic bounds.",
        "rel_hi": "आकर्षक, विनोदी और अनुकूलनीय; कठोर घरेलू बंधनों के मुकाबले जीवंत संवाद और स्वतंत्रता को प्राथमिकता देते हैं।",
        "health_en": "High nervous energy; prone to over-exertion, mental burnout, and anxiety.",
        "health_hi": "उच्च स्नायु ऊर्जा; अति-श्रम, मानसिक थकान और चिंता की प्रवृत्ति।"
    },
    6: {
        "planet_en": "Venus (Shukra)", "planet_hi": "शुक्र (Shukra)",
        "career_en": "Luxury Goods, Architecture, Fashion Design, Entertainment, Hospitality, Interior Decor, Finance.",
        "career_hi": "विलासिता की वस्तुएं, वास्तुकला, फैशन डिजाइन, मनोरंजन, आतिथ्य, इंटीरियर डिजाइन और वित्त।",
        "wealth_en": "Attracts high-value assets, luxury vehicles, and real estate; prone to generous spending on comfort.",
        "wealth_hi": "उच्च मूल्य की संपत्ति, लग्जरी वाहन और रियल एस्टेट आकर्षित करते हैं; सुख-सुविधाओं पर खुलकर खर्च करने की प्रवृत्ति होती है।",
        "rel_en": "Deeply affectionate, romantic, and harmony-seeking; highly devoted to family and partnerships.",
        "rel_hi": "अत्यंत स्नेही, रोमांटिक और सामंजस्य चाहने वाले; परिवार और साझेदारियों के प्रति पूर्ण समर्पित।"
    },
    7: {
        "planet_en": "Ketu / Neptune", "planet_hi": "केतु / नेपच्यून",
        "career_en": "Occult Research, Data Analysis, Writing, Psychology, Scientific Investigation, Auditing, Spirituality.",
        "career_hi": "गूढ़ अनुसंधान, डेटा विश्लेषण, लेखन, मनोविज्ञान, वैज्ञानिक जांच, ऑडिटिंग और आध्यात्मिकता।",
        "wealth_en": "Intuitive financial instincts; gains through specialized research, writing, or hidden assets rather than speculation.",
        "wealth_hi": "सहज वित्तीय अंतर्दृष्टि; सट्टेबाजी के बजाय विशेष अनुसंधान, लेखन या गुप्त संपत्तियों के माध्यम से लाभ।",
        "rel_en": "Independent and introspective; requires personal space and deep emotional resonance to feel secure.",
        "rel_hi": "स्वतंत्र और आत्म-विश्लेषी; सुरक्षित महसूस करने के लिए व्यक्तिगत स्थान और गहरी भावनात्मक समझ की आवश्यकता होती है।",
        "health_en": "Vulnerable to psychosomatic fatigue, joint stiffness, and erratic sleep cycles.",
        "health_hi": "मनोदैहिक थकान, जोड़ों में अकड़न और अनियमित निद्रा चक्र के प्रति संवेदनशील।"
    },
    8: {
        "planet_en": "Saturn (Shani)", "planet_hi": "शनि (Shani)",
        "career_en": "Corporate Governance, Heavy Industry, Real Estate, Infrastructure, Judiciary, Banking, Auditing.",
        "career_hi": "कॉर्पोरेट प्रशासन, भारी उद्योग, रियल एस्टेट, बुनियादी ढांचा, न्यायपालिका, बैंकिंग और ऑडिटिंग।",
        "wealth_en": "Slow, methodical capital compounding; builds immovable wealth and enduring financial security over time.",
        "wealth_hi": "धीमी, व्यवस्थित पूंजी वृद्धि; समय के साथ अचल संपत्ति और स्थाई वित्तीय सुरक्षा का निर्माण करते हैं।",
        "rel_en": "Deeply committed and protective; expresses care through duty and reliability rather than emotional displays.",
        "rel_hi": "गहन रूप से प्रतिबद्ध और सुरक्षात्मक; भावनात्मक प्रदर्शन के बजाय कर्तव्य और विश्वसनीयता के माध्यम से स्नेह व्यक्त करते हैं।",
        "health_en": "Prone to bone stiffness, joint discomfort, dental sensitivity, and fatigue from overworking.",
        "health_hi": "हड्डियों की अकड़न, जोड़ों की तकलीफ, दांतों की संवेदनशीलता और अति-श्रम से थकान की प्रवृत्ति।"
    },
    9: {
        "planet_en": "Mars (Mangal)", "planet_hi": "मंगल (Mangal)",
        "career_en": "Defense Services, Surgery, Engineering, Real Estate Development, Sports, Emergency Operations.",
        "career_hi": "रक्षा सेवाएं, शल्य चिकित्सा (सर्जरी), इंजीनियरिंग, रियल एस्टेट विकास, खेल और आपातकालीन संचालन।",
        "wealth_en": "Brave financial risk-taking; gains through land, property, and industrial assets with assertive management.",
        "wealth_hi": "साहसी वित्तीय जोखिम लेना; दृढ़ प्रबंधन के साथ भूमि, संपत्ति और औद्योगिक संपत्तियों से लाभ।",
        "rel_en": "Protective, passionate, and fiercely loyal; requires mutual respect and emotional directness.",
        "rel_hi": "सुरक्षात्मक, उत्साही और अत्यंत निष्ठावान; आपसी सम्मान और भावनात्मक स्पष्टता की आवश्यकता होती है।",
        "health_en": "High physical stamina; susceptible to accidental cuts, inflammation, and high blood pressure.",
        "health_hi": "उच्च शारीरिक सहनशक्ति; दुर्घटनात्मक चोट, सूजन और उच्च रक्तचाप के प्रति संवेदनशील।"
    }
}

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

    m_data = NUMEROLOGY_CONTENT.get(mulank, NUMEROLOGY_CONTENT[1])
    b_data = NUMEROLOGY_CONTENT.get(bhagyank, NUMEROLOGY_CONTENT[1])
    n_data = NUMEROLOGY_CONTENT.get(namank, NUMEROLOGY_CONTENT[1])

    p_m_label = m_data["planet_hi"] if is_hi else m_data["planet_en"]
    p_b_label = b_data["planet_hi"] if is_hi else b_data["planet_en"]
    p_n_label = n_data["planet_hi"] if is_hi else n_data["planet_en"]

    card_title = "🔢 मुख्य अंकशास्त्रीय ब्लूप्रिंट" if is_hi else "🔢 Core Numerology Blueprint"
    lbl_mul = "मूलांक (Driver)" if is_hi else "Mulank (Driver)"
    lbl_bhag = "भाग्यांक (Destiny)" if is_hi else "Bhagyank (Destiny)"
    lbl_nam = "नामांक (Name Vibration)" if is_hi else "Namank (Name Vibration)"

    c_title = "💼 अनुकूल आजीविका एवं कार्यक्षेत्र" if is_hi else "💼 Optimal Career & Vocation"
    w_title = "💰 धन संचय एवं वित्तीय प्रबंधन" if is_hi else "💰 Wealth Accumulation & Financial Management"
    r_title = "❤️ पारस्परिक संबंध एवं साझेदारी" if is_hi else "❤️ Interpersonal Relations & Partnerships"
    h_title = "🌿 स्वास्थ्य एवं प्राण ऊर्जा संतुलन" if is_hi else "🌿 Health & Vitality Balance"

    c_desc = m_data["career_hi"] if is_hi else m_data["career_en"]
    w_desc = b_data["wealth_hi"] if is_hi else b_data["wealth_en"]
    r_desc = m_data["rel_hi"] if is_hi else m_data["rel_en"]
    h_desc = m_data["health_hi"] if is_hi else m_data["health_en"]

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
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{c_title}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{c_desc}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #10b981;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{w_title}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{w_desc}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #14b8a6;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{r_title}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{r_desc}</div>
            </div>
            <div style="background:#ffffff; border-radius:12px; padding:14px; border:1px solid #d1fae5; border-left:5px solid #0d9488;">
                <div style="font-weight:900; font-size:1.05rem; color:#065f46; margin-bottom:5px;">{h_title}</div>
                <div style="font-size:0.95rem; line-height:1.65; color:#1e293b;">{h_desc}</div>
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

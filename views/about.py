# views/about.py - Dedicated About App Screen with Full Hindi & English Content
import streamlit as st
import urllib.parse

def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

ABOUT_CONTENT = {
    "en": {
        "lang_selector_label": "**🌐 Select Language / भाषा चुनें:**",
        "hero_title": "🧬 Navtara Pulse: Precision Chronobiology & Vedic Timing Engine",
        "hero_desc": (
            "<b>Navtara Pulse</b> bridges ancient Sidereal Jyotish with modern chronobiology. "
            "It is an algorithmic decision-support compass designed to answer one crucial question: "
            "<b>\"Is today mathematically aligned for aggressive action, or does it demand strategic defense?\"</b><br><br>"
            "By mapping the Moon's real-time transit through the 27 lunar mansions (Nakshatras) against your natal birth frequency, "
            "the app calculates your personalized 9-fold bio-rhythm, pinpointing exact windows of peak influence, effortless execution, and friction avoidance."
        ),
        "science_heading": "🔬 The Scientific Logic: Gravitational Hydrodynamics & Bio-Rhythms",
        "point_1_title": "1. Lunar Tidal Hydrodynamics & Neuro-Endocrine Flow:",
        "point_1_desc": (
            "The adult human brain and body are composed of approximately <b>70% water and electrolytic fluids</b>. "
            "Chronobiology confirms that lunar periodicity modulates circadian gene expression, sleep architecture (REM cycles), "
            "cerebrospinal fluid pressure, and neuro-transmitter output. In classical Vedic science, the Moon governs the mind "
            "(<i>\"Chandro Manaso Jatah\"</i>). When the celestial Moon aligns harmoniously with your natal Moon's electromagnetic horizon, "
            "neural processing operates at peak cognitive clarity."
        ),
        "point_2_title": "2. The 9-Fold Mathematical Resonance Grid (27 = 9 × 3):",
        "point_2_intro": (
            "The zodiac is divided into 27 Nakshatras of 13° 20' each. The Vedic <b>Navtara Chakra</b> is an infradian mathematical model "
            "that groups these 27 stars into 3 repeating cycles of 9 qualitative energetic frequencies (Taras). "
            "Every single day, the Moon activates one of these 9 energetic chambers for your unique neural wiring:"
        ),
        "bullet_1": "<b>Expansion Windows (Sampat, Sadhana, Mitra, Ati-Mitra):</b> Characterized by high environmental receptivity and synaptic coherence. Ideal for high-stakes business negotiations, signing contracts, strategic investing, and key launches.",
        "bullet_2": "<b>Friction Shields (Vipat, Pratyari, Vadha):</b> Characterized by elevated resistance, biochemical fatigue, and communication misfires. On these days, defensive prudence and patient review prevent costly missteps.",
        "bullet_3": "<b>Foundational & Consolidation Days (Janma, Kshema):</b> Optimal for internal diagnostics, physical recuperation, and team alignment.",
        "point_3_title": "3. Sub-Arcsecond Planetary Ephemeris (Swiss Ephemeris):",
        "point_3_desc": (
            "Unlike conventional astrology apps that rely on generic sun signs or flat 24-hour sunrise assumptions, "
            "<b>Navtara Pulse</b> incorporates the <b>Moshier Swiss Ephemeris</b> (pyswisseph) with true topocentric Chitrapaksha Lahiri Ayanamsa. "
            "Ingress and egress timestamps are calculated down to the exact second for your geographical horizon."
        ),
        "share_title": "📲 Share Navtara Pulse With Friends & Family",
        "share_desc": "Share this authentic Vedic chronobiology tool with your family, friends, and colleagues:",
        "share_msg": "Track your real-time Vedic Moon transit rhythm, Shani Paya, and personalized timing blueprint with Navtara Pulse!"
    },
    "hi": {
        "lang_selector_label": "**🌐 भाषा चुनें / Select Language:**",
        "hero_title": "🧬 नवतारा पल्स: सूक्ष्म क्रोनोबायोलॉजी एवं वैदिक काल-गणना इंजन",
        "hero_desc": (
            "<b>नवतारा पल्स (Navtara Pulse)</b> प्राचीन निरयण वैदिक ज्योतिष और आधुनिक क्रोनोबायोलॉजी (जैविक समय-विज्ञान) का एक वैज्ञानिक समन्वय है। "
            "यह एक ऐसा गणितीय निर्णय-समर्थन तंत्र है जो इस महत्वपूर्ण प्रश्न का सटीक समाधान देता है: "
            "<b>\"क्या आज का दिन महत्वपूर्ण निर्णय व साहसिक कदमों के अनुकूल है, अथवा यह रणनीतिक धैर्य की मांग करता है?\"</b><br><br>"
            "आकाश में 27 नक्षत्रों से होकर गुजरने वाले चन्द्रमा के तात्कालिक गोचर की तुलना आपकी जन्मकालीन नक्षत्र-तरंग से करके, "
            "यह ऐप आपके व्यक्तिगत 9-स्तरीय जैविक-ऊर्जा चक्र (नव-तारा) का विश्लेषण करता है ताकि आप अनुकूल अवसरों का अधिकतम लाभ उठा सकें और संभावित अवरोधों से सुरक्षित रह सकें।"
        ),
        "science_heading": "🔬 वैज्ञानिक आधार: गुरुत्वाकर्षण, जलगतिकी एवं जैव-चक्रीय लय",
        "point_1_title": "1. चन्द्र ज्वारीय प्रभाव एवं तंत्रिका-हार्मोनल संतुलन:",
        "point_1_desc": (
            "मानव मस्तिष्क और शरीर लगभग <b>70% जल और इलेक्ट्रोलाइट द्रवों</b> से निर्मित है। "
            "आधुनिक विज्ञान प्रमाणित करता है कि चन्द्रमा की गति हमारी सर्केडियन लय, निद्रा चक्र (REM स्लीप), सेरेब्रोस्पाइनल द्रव के दबाव और न्यूरोट्रांसमीटर के स्राव को प्रत्यक्ष रूप से प्रभावित करती है। "
            "वैदिक दर्शन में चन्द्रमा को मन का कारक माना गया है (<i>\"चन्द्रमा मनसो जातः\"</i>)। जब गोचरीय चन्द्रमा आपके जन्म नक्षत्र के साथ अनुकूल कोण बनाता है, "
            "तो आपकी मानसिक एकाग्रता, निर्णय लेने की क्षमता और कार्यक्षमता अपने उच्चतम स्तर पर होती है।"
        ),
        "point_2_title": "2. नौ-स्तरीय गणितीय ऊर्जा ग्रिड (27 = 9 × 3):",
        "point_2_intro": (
            "सम्पूर्ण भचक्र 13° 20' के 27 नक्षत्रों में विभाजित है। वैदिक <b>नवतारा चक्र</b> एक विशिष्ट गणितीय मॉडल है जो इन 27 तारों को 9 ऊर्जा श्रेणियों के 3 चक्रों में वर्गीकृत करता है। "
            "प्रतिदिन चन्द्रमा आपकी जन्म कुंडली के अनुसार इन 9 में से किसी एक ऊर्जा क्षेत्र को सक्रिय करता है:"
        ),
        "bullet_1": "<b>सकारात्मक विस्तार काल (सम्पत, साधना, मित्र, अति-मित्र):</b> उच्च मानसिक तालमेल और वातावरण की अनुकूलता। व्यापारिक सौदे, नवीन अनुबंध, पूंजी निवेश और शुभ कार्यों के शुभारंभ के लिए सर्वोत्तम।",
        "bullet_2": "<b>सुरक्षात्मक व सतर्कता काल (विपत, प्रत्यरि, वध):</b> स्वाभाविक प्रतिरोध, मानसिक तनाव और गलतफहमी की संभावना। इन दिनों में जोखिम भरे निर्णयों को टालना और धैर्यपूर्वक आत्म-निरीक्षण करना श्रेष्ठ होता है।",
        "bullet_3": "<b>आधारभूत एवं संतुलन काल (जन्म, क्षेम):</b> शारीरिक स्वास्थ्य लाभ, कार्य योजना की समीक्षा और आन्तरिक संतुलन के लिए अनुकूल।",
        "point_3_title": "3. उच्च परिशुद्धता खगोलीय गणना (स्विस एफिमेरिस):",
        "point_3_desc": (
            "पारंपरिक पंचांगों के सामान्य अनुमानों के विपरीत, <b>नवतारा पल्स</b> उच्च-सटीक <b>स्विस एफिमेरिस (Swiss Ephemeris)</b> और शुद्ध चित्रापक्षीय लाहिड़ी अयनांश का उपयोग करता है। "
            "आपके जन्म स्थान के सटीक अक्षांश व देशांतर के अनुसार नक्षत्र प्रवेश और समाप्ति का समय सेकंड की सूक्ष्मता तक परिकलित किया जाता है।"
        ),
        "share_title": "📲 नवतारा पल्स को परिवार व मित्रों के साथ साझा करें",
        "share_desc": "इस प्रामाणिक वैदिक काल-गणना प्रणाली को अपने परिवार, मित्रों और सहयोगियों के साथ साझा करें:",
        "share_msg": "नवतारा पल्स के साथ अपने वास्तविक समय के चन्द्र नक्षत्र गोचर, शनि पाया और दैनिक ऊर्जा तालमेल को समझें!"
    }
}

def render_page_about():
    # Read user profile and current language from session state
    prof = st.session_state.get("user_profile", {})
    current_lang = prof.get("lang", "en")
    is_hi = (current_lang == "hi")
    c = ABOUT_CONTENT["hi"] if is_hi else ABOUT_CONTENT["en"]

    # Language Switcher Card
    with st.container(border=True):
        st.markdown(c["lang_selector_label"])
        lang_col1, _ = st.columns([2, 1])
        with lang_col1:
            lang_options = {"en": "English", "hi": "हिन्दी (Hindi)"}
            selected_lang_code = st.selectbox(
                "App Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=list(lang_options.keys()).index(current_lang if current_lang in lang_options else "en"),
                label_visibility="collapsed"
            )
            if selected_lang_code != current_lang:
                st.session_state.user_profile["lang"] = selected_lang_code
                st.query_params["lang"] = selected_lang_code
                st.rerun()

    # Hero Banner
    render_html(f"""
    <div class="auth-hero-box">
        <div style="font-weight:900; font-size:1.35rem; color:#92400e; margin-bottom:0.75rem; border-bottom:1.5px solid #fde68a; padding-bottom:0.4rem;">
            {c['hero_title']}
        </div>
        <div style="font-size:0.98rem; line-height:1.8; color:#451a03; margin-bottom:0.8rem;">
            {c['hero_desc']}
        </div>
    </div>

    <!-- Scientific & Vedic Logic Card -->
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            {c['science_heading']}
        </div>
        
        <div style="font-size:0.96rem; line-height:1.75; color:#334155; margin-bottom:1rem;">
            <b>{c['point_1_title']}</b><br>
            {c['point_1_desc']}
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#334155; margin-bottom:1rem;">
            <b>{c['point_2_title']}</b><br>
            {c['point_2_intro']}
            <ul style="margin-top:6px; padding-left:1.3rem;">
                <li>{c['bullet_1']}</li>
                <li>{c['bullet_2']}</li>
                <li>{c['bullet_3']}</li>
            </ul>
        </div>

        <div style="font-size:0.96rem; line-height:1.75; color:#334155;">
            <b>{c['point_3_title']}</b><br>
            {c['point_3_desc']}
        </div>
    </div>
    """)

    # Social Sharing Widget
    app_url = "https://navtara-pulse.streamlit.app"
    encoded_url = urllib.parse.quote(app_url)
    encoded_msg = urllib.parse.quote(f"{c['share_msg']}\n\n{app_url}")

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.25rem; color:#9a3412; margin-bottom:0.75rem; border-bottom:2px solid #fed7aa; padding-bottom:0.4rem;">
            {c['share_title']}
        </div>
        <div style="font-size:0.95rem; color:#475569; margin-bottom:0.85rem;">
            {c['share_desc']}
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:1rem;">
            <a href="https://api.whatsapp.com/send?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#25D366; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(37,211,102,0.2);">
                    🟢 WhatsApp
                </div>
            </a>
            <a href="https://t.me/share/url?url={encoded_url}&text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0088cc; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(0,136,204,0.2);">
                    ✈️ Telegram
                </div>
            </a>
            <a href="mailto:?subject=Navtara Pulse&body={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#ea4335; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(234,67,53,0.2);">
                    ✉️ Email
                </div>
            </a>
            <a href="https://twitter.com/intent/tweet?text={encoded_msg}" target="_blank" style="text-decoration:none;">
                <div style="background:#0f172a; color:#ffffff; padding:12px; border-radius:12px; text-align:center; font-weight:900; font-size:1rem; box-shadow:0 2px 8px rgba(15,23,42,0.2);">
                    🐦 X (Twitter)
                </div>
            </a>
        </div>
    </div>
    """)

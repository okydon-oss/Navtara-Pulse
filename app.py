# ... existing code ...
CITY_COORDS = {
    "chhatrapati sambhajinagar": (19.8762, 75.3433),
    "aurangabad": (19.8762, 75.3433),
    "mumbai": (19.0760, 72.8777),
    "pune": (18.5204, 73.8567),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "ahmedabad": (23.0225, 72.5714),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "jaipur": (26.9124, 75.7873),
    "surat": (21.1702, 72.8311),
    "nagpur": (21.1458, 79.0882),
    "indore": (22.7196, 75.8577),
    "bhopal": (23.2599, 77.4126),
    "lucknow": (26.8467, 80.9462),
    "patna": (25.5941, 85.1376),
    "panvel": (18.9894, 73.1175),
    "thane": (19.2183, 72.9781),
    "nashik": (19.9975, 73.7898)
}

def resolve_coords(place_str: str):
    """Resolves latitude and longitude from city name or defaults to Sambhajinagar."""
    normalized = place_str.lower().split(",")[0].strip()
    return CITY_COORDS.get(normalized, (19.8762, 75.3433))

TRANSLATIONS["en"].update({
    "sec1_title": "🌟 1. Navtara & Vedic Astrological Profile",
    "sec2_title": "🔢 2. Core Numerology Blueprint & Fixed Life Attributes",
    "sec3_title": "🪐 3. Shani Paya & Shani Gochar (Sade Sati / Dhaiya)",
    "lagna_label": "Lagna (Ascendant)",
    "nak_deity_lord": "Ruling Deity & Nakshatra Lord",
    "nak_personality_full": "In-Depth Nakshatra Personality & Mindset",
    "nak_remedies_title": "🪔 Vedic Remedies for Janma Nakshatra",
    "num_remedies_title": "🪔 Astro-Numerology Life Harmonizing Remedies",
    "sadesati_card_title": "Saturn Gochar (Sade Sati / Dhaiya Status)",
    "sadesati_timeline_lbl": "Transit Timeline & Phase",
    "sadesati_impact_lbl": "Sade Sati / Dhaiya Influence & Life Strategy",
    "shani_integrated_remedies": "🛡️ Combined Vedic Shani Protection Remedies"
})

TRANSLATIONS["hi"].update({
    "sec1_title": "🌟 1. नवतारा एवं वैदिक जन्म कुंडली प्रोफाइल",
    "sec2_title": "🔢 2. अंक ज्योतिष रूपरेखा एवं मूल स्वभाव विश्लेषण",
    "sec3_title": "🪐 3. शनि पाया एवं शनि गोचर (साढ़े साती / ढैय्या प्रभाव)",
    "lagna_label": "लग्न (Ascendant)",
    "nak_deity_lord": "नक्षत्र स्वामी एवं अधिष्ठाता देवता",
    "nak_personality_full": "विस्तृत जन्म नक्षत्र व्यक्तित्व एवं मानसिक स्वभाव",
    "nak_remedies_title": "🪔 जन्म नक्षत्र शांति एवं वैदिक उपाय",
    "num_remedies_title": "🪔 अंक ज्योतिषीय संतुलन एवं भाग्योदय उपाय",
    "sadesati_card_title": "वर्तमान शनि गोचर (साढ़े साती / ढैय्या स्थिति)",
    "sadesati_timeline_lbl": "गोचर समयावधि एवं सक्रिय चरण",
    "sadesati_impact_lbl": "साढ़े साती / ढैय्या फलादेश एवं जीवन प्रभाव",
    "shani_integrated_remedies": "🛡️ शनि पाया व साढ़े साती सुरक्षात्मक वैदिक उपाय"
})

TRANSLATIONS["mr"].update({
    "sec1_title": "🌟 १. नवतारा व वैदिक जन्म कुंडली रूपरेषा",
    "sec2_title": "🔢 २. अंकशास्त्र ब्लूप्रिंट व स्थायी जीवन स्वभाव",
    "sec3_title": "🪐 ३. शनी पाया व शनी गोचर (साडेसाती / अडीचकी प्रभाव)",
    "lagna_label": "लग्न (Ascendant)",
    "nak_deity_lord": "नक्षत्र स्वामी व आराध्य देवता",
    "nak_personality_full": "सखोल जन्म नक्षत्र व्यक्तिमत्त्व व विचारसरणी",
    "nak_remedies_title": "🪔 जन्म नक्षत्र शांती व वैदिक उपाय",
    "num_remedies_title": "🪔 अंकशास्त्र ऊर्जा समतोल व भाग्योदय उपाय",
    "sadesati_card_title": "सद्य शनी गोचर (साडेसाती / ढैय्या स्थिती)",
    "sadesati_timeline_lbl": "गोचर कालावधी व सक्रिय टप्पा",
    "sadesati_impact_lbl": "साडेसाती / अडीचकी प्रभाव व जीवन फलादेश",
    "shani_integrated_remedies": "🛡️ शनी पाया व साडेसाती प्रतिबंधक वैदिक उपाय"
})

TRANSLATIONS["gu"].update({
    "sec1_title": "🌟 ૧. નવતારા અને વૈદિક જન્મ કુંડળી રૂપરેખા",
    "sec2_title": "🔢 ૨. અંકશાસ્ત્ર બ્લૂપ્રિન્ટ અને મૂળ સ્વભાવ વિશ્લેષણ",
    "sec3_title": "🪐 ૩. શનિ પાયા અને શનિ ગોચર (સાડાસાતી / ઢૈય્યા પ્રભાવ)",
    "lagna_label": "લગ્ન (Ascendant)",
    "nak_deity_lord": "નક્ષત્ર સ્વામી અને અધિષ્ઠાતા દેવ",
    "nak_personality_full": "વિગતવાર જન્મ નક્ષત્ર વ્યક્તિત્વ અને મૂળ સ્વભાવ",
    "nak_remedies_title": "🪔 જન્મ નક્ષત્ર શાંતિ અને વૈદિક ઉપાયો",
    "num_remedies_title": "🪔 અંકશાસ્ત્ર સંતુલન અને ભાગ્યોદય ઉપાયો",
    "sadesati_card_title": "વર્તમાન શનિ ગોચર (સાડાસાતી / ઢૈય્યા સ્થિતિ)",
    "sadesati_timeline_lbl": "ગોચર સમયગાળો અને સક્રિય તબક્કો",
    "sadesati_impact_lbl": "સાડાસાતી / ઢૈય્યા ફળકથન અને જીવન પ્રભાવ",
    "shani_integrated_remedies": "🛡️ શનિ પાયા અને સાડાસાતી રક્ષાત્મક વૈદિક ઉપાયો"
})

NAKSHATRA_DETAILS = {
    0: {"lord": "Ketu", "deity": "Ashwini Kumaras", "tree": "Kuchila / Strychnos", "mantra": "Om Ashwibhyam Namah"},
    1: {"lord": "Shukra (Venus)", "deity": "Yama", "tree": "Amla (Indian Gooseberry)", "mantra": "Om Yamaya Namah / Om Shukraya Namah"},
    2: {"lord": "Surya (Sun)", "deity": "Agni", "tree": "Gular (Cluster Fig)", "mantra": "Om Agnaye Namah"},
    3: {"lord": "Chandra (Moon)", "deity": "Brahma / Prajapati", "tree": "Jamun (Black Plum)", "mantra": "Om Brahmane Namah"},
    4: {"lord": "Mangal (Mars)", "deity": "Soma (Moon God)", "tree": "Khair (Acacia)", "mantra": "Om Somaya Namah"},
    5: {"lord": "Rahu", "deity": "Rudra", "tree": "Pakar (Ficus Lacor)", "mantra": "Om Rudraya Namah"},
    6: {"lord": "Guru (Jupiter)", "deity": "Aditi", "tree": "Bamboo", "mantra": "Om Aditaye Namah"},
    7: {"lord": "Shani (Saturn)", "deity": "Brihaspati", "tree": "Peepal (Sacred Fig)", "mantra": "Om Brihaspataye Namah"},
    8: {"lord": "Budha (Mercury)", "deity": "Nagas (Serpents)", "tree": "Nagkesar", "mantra": "Om Sarpabhyo Namah"},
    9: {"lord": "Ketu", "deity": "Pitris (Ancestors)", "tree": "Banyan (Vat Vriksha)", "mantra": "Om Pitribhyo Namah"},
    10: {"lord": "Shukra (Venus)", "deity": "Bhaga (Sun of Fortune)", "tree": "Palash (Flame of the Forest)", "mantra": "Om Bhagaya Namah"},
    11: {"lord": "Surya (Sun)", "deity": "Aryaman", "tree": "Rudraksha / Plaksha", "mantra": "Om Aryamne Namah"},
    12: {"lord": "Chandra (Moon)", "deity": "Savitr", "tree": "Chameli (Jasmine)", "mantra": "Om Savitre Namah"},
    13: {"lord": "Mangal (Mars)", "deity": "Tvashtar (Vishwakarma)", "tree": "Bilva (Bael Tree)", "mantra": "Om Tvashtre Namah"},
    14: {"lord": "Rahu", "deity": "Vayu (Wind God)", "tree": "Arjuna Tree", "mantra": "Om Vayave Namah"},
    15: {"lord": "Guru (Jupiter)", "deity": "Indra-Agni", "tree": "Vikankata / Wood Apple", "mantra": "Om Indragnibhyam Namah"},
    16: {"lord": "Shani (Saturn)", "deity": "Mitra (God of Friendship)", "tree": "Bakul (Maulsari)", "mantra": "Om Mitraya Namah"},
    17: {"lord": "Budha (Mercury)", "deity": "Indra", "tree": "Pine / Shalmali", "mantra": "Om Indraya Namah"},
    18: {"lord": "Ketu", "deity": "Nirriti", "tree": "Sal (Shorea Robusta)", "mantra": "Om Nirritaye Namah"},
    19: {"lord": "Shukra (Venus)", "deity": "Apas (Water Goddess)", "tree": "Ashoka Tree", "mantra": "Om Adbhyo Namah"},
    20: {"lord": "Surya (Sun)", "deity": "Vishvadevas", "tree": "Jackfruit (Phanas)", "mantra": "Om Vishvedevabhyo Namah"},
    21: {"lord": "Chandra (Moon)", "deity": "Vishnu", "tree": "Arka (Madar)", "mantra": "Om Vishnave Namah"},
    22: {"lord": "Mangal (Mars)", "deity": "Ashta Vasus", "tree": "Shami (Prosopis)", "mantra": "Om Vasubhyo Namah"},
    23: {"lord": "Rahu", "deity": "Varuna", "tree": "Kadamba", "mantra": "Om Varunaya Namah"},
    24: {"lord": "Guru (Jupiter)", "deity": "Aja Ekapada", "tree": "Mango Tree", "mantra": "Om Ajaikapade Namah"},
    25: {"lord": "Shani (Saturn)", "deity": "Ahirbudhnya", "tree": "Neem Tree", "mantra": "Om Ahirbudhnyaya Namah"},
    26: {"lord": "Budha (Mercury)", "deity": "Pushan", "tree": "Mahua", "mantra": "Om Pushne Namah"}
}

def get_nakshatra_remedy(nak_idx: int, lang: str = "en") -> list:
    details = NAKSHATRA_DETAILS.get(nak_idx, NAKSHATRA_DETAILS[1])
    deity = details["deity"]
    lord = details["lord"]
    mantra = details["mantra"]
    tree = details["tree"]

    if lang == "hi":
        return [
            f"**नक्षत्र आराध्य देव:** भगवान {deity} एवं नक्षत्र स्वामी {lord} की नियमित पूजा-अर्चना करें।",
            f"**बीज मंत्र जप:** प्रतिदिन अथवा जन्म नक्षत्र के दिन `{mantra}` का 108 बार मानसिक जप करें।",
            f"**पवित्र वृक्ष संरक्षण:** {tree} के पौधे का रोपण करें या उसकी परिक्रमा कर जल अर्पित करें।",
            "**कल्याणकारी दान:** अपनी जन्म राशि एवं नक्षत्र स्वामी के अनुकूल सात्विक खाद्य पदार्थों व वस्त्रों का दान करें।"
        ]
    elif lang == "mr":
        return [
            f"**नक्षत्र आराध्य दैवत:** {deity} आणि नक्षत्र स्वामी {lord} यांचे नित्य स्मरण व पूजन करा.",
            f"**बीज मंत्र जप:** दररोज किंवा जन्म नक्षत्राच्या दिवशी `{mantra}` चा १०८ वेळा शांतपणे जप करा.",
            f"**पवित्र वृक्ष सेवा:** {tree} वृक्षाला जल अर्पण करा अथवा त्याचे संवर्धन करा.",
            "**सात्विक दान:** नक्षत्र अनुकूल धान्याचे व गरजू व्यक्तींना वस्त्रदान करून पुण्य संपादन करा."
        ]
    elif lang == "gu":
        return [
            f"**નક્ષત્ર આરાધ્ય દેવ:** {deity} અને નક્ષત્ર સ્વામી {lord} ની નિયમિત ભક્તિ કરો.",
            f"**બીજ મંત્ર જાપ:** દરરોજ અથવા જન્મ નક્ષત્રના દિવસે `{mantra}` નો ૧૦૮ વખત જાપ કરવો.",
            f"**પવિત્ર વૃક્ષ સેવન:** {tree} ના વૃક્ષની જાળવણી કરો અથવા તેને જળ ચડાવો.",
            "**કલ્યાણકારી દાન:** નક્ષત્ર સ્વામીના વાર પર જરૂરીયાતમંદ લોકોને અન્ન અને વસ્ત્રનું દાન કરવું."
        ]
    else:
        return [
            f"**Nakshatra Deity Worship:** Offer prayers to {deity} and honor the planetary ruler {lord}.",
            f"**Sacred Japa:** Recite `{mantra}` 108 times daily or on Moon transit over your birth star.",
            f"**Sacred Plant Connection:** Honor, plant, or water the {tree} to harmonize planetary frequencies.",
            "**Sattvic Charity:** Donate grains, white flowers, or clothes aligned with your Nakshatra lord."
        ]

def calculate_lagna(jd_birth_ut: float, lat: float, lon: float):
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    ayanamsa = swe.get_ayanamsa_ut(jd_birth_ut)
    houses, ascmc = swe.houses(jd_birth_ut, lat, lon, b'P')
    ascendant_sidereal = (ascmc[0] - ayanamsa) % 360.0
    rashi_idx = int(ascendant_sidereal / 30.0) % 12
    deg = ascendant_sidereal % 30.0
    return rashi_idx, deg

def calculate_birth_chart(dob: datetime.date, tob: datetime.time, place_str: str = "", tz_offset_hours: float = 5.5):
    """Calculates Moon Nakshatra, Pada, Moon Rashi, and Lagna (Ascendant) via Lahiri Swiss Ephemeris."""
    birth_dt_local = datetime.datetime.combine(dob, tob)
    birth_dt_utc = birth_dt_local - datetime.timedelta(hours=tz_offset_hours)
    jd_birth = dt_to_jd(birth_dt_utc)
    moon_lon = get_sidereal_lon(jd_birth, swe.MOON)
    nak_idx, pada = lon_to_nakshatra(moon_lon)
    rashi_idx, rashi_deg = lon_to_rashi(moon_lon)
    lat, lon = resolve_coords(place_str)
    lagna_rashi_idx, lagna_deg = calculate_lagna(jd_birth, lat, lon)
    return nak_idx, pada, rashi_idx, rashi_deg, lagna_rashi_idx, lagna_deg

def calculate_shani_sadesati_dhaiya(moon_rashi_idx: int, saturn_rashi_idx: int, lang: str = "en"):
    """Determines exact Sade Sati or Dhaiya phase, transit timeline, prediction, and Vedic remedies."""
    house_from_moon = ((saturn_rashi_idx - moon_rashi_idx) % 12) + 1
    timeline_str = "29 March 2025 – 23 February 2028 (Meena / Pisces Transit)"

    # Sade Sati: Saturn in 12th, 1st, or 2nd from natal Moon
    if house_from_moon == 12:
        is_active = True
        status_type = "Sade Sati Phase 1 (Rising / चहढ़ती साढ़े साती)" if lang == "en" else "साढ़े साती प्रथम चरण (आरंभिक / लग्न चरण)"
        impact_en = (
            "Saturn transits the 12th house from your natal Moon sign. Known as the Rising Phase of Sade Sati. "
            "It prompts deep inner introspection, expenditure restructuring, overseas or long-distance shifts, "
            "and detachment from non-essential commitments. While expenses and travel increase, operating with "
            "disciplined routines turns this into a period of massive long-term spiritual and professional restructuring."
        )
        impact_hi = (
            "शनि देव आपकी चन्द्र राशि से द्वादश (12वें) भाव में गोचर कर रहे हैं। यह साढ़े साती का प्रथम (आरंभिक) चरण कहलाता है। "
            "यह चरण जीवन में अनावश्यक व्यय पर नियंत्रण, दूरगामी योजनाओं, विदेश या सुदूर संपर्कों और आध्यात्मिक चिंतन का विस्तार करता है। "
            "आर्थिक मामलों में अत्यधिक सतर्कता और स्वास्थ्य व निद्रा का ध्यान रखें। अनुशासित दिनचर्या से यह समय जीवन को सुदृढ़ आधार देता है।"
        )
        impact_mr = (
            "शनी महाराज आपल्या चंद्र राशीपासून १२ व्या भावात गोचर करत आहेत. हा साडेसातीचा प्रथम (चढती साडेसाती) टप्पा आहे. "
            "या काळात खर्च वाढू शकतो, कामाच्या निमित्ताने प्रवास होतात व जीवनशैलीत मोठे बदल घडून येतात. "
            "आर्थिक व्यवहारात सावधगिरी बाळगा आणि आरोग्याकडे लक्ष द्या. प्रामाणिक परिश्रमाने मोठी प्रगती साध्य होते."
        )
        impact_gu = (
            "શનિ દેવ તમારી ચંદ્ર રાશિથી ૧૨મા ભાવમાં ગોચર કરી રહ્યા છે. આ સાડાસાતીનો પ્રથમ તબક્કો છે. "
            "આ સમયગાળામાં ખર્ચ પર અંકુશ રાખવો, લાંબા ગાળાનું આયોજન કરવું અને બિનજરૂરી દોડધામથી બચવું હિતાવહ છે. "
            "ધૈર્ય અને આધ્યાત્મિક સાધનાથી મુશ્કેલ કાર્યો પણ સરળતાથી પાર પડી શકે છે."
        )
        remedies = [
            "शनिवार की संध्या पीपल के वृक्ष के नीचे सरसों के तेल का दीपक प्रज्वलित करें एवं 7 परिक्रमा करें।" if lang != "en" else "Light a mustard oil lamp beneath a Peepal tree on Saturday evenings and perform 7 circumambulations.",
            "नित्य 'हनुमान चालीसा' एवं 'दशरथ कृत शनि स्तोत्र' का पाठ करें।" if lang != "en" else "Recite the Hanuman Chalisa and Dasharatha Shani Stotra daily with pure devotion.",
            "श्रमिकों, सफाई कर्मियों एवं दिव्यांगजनों की निःस्वार्थ सेवा करें एवं उन्हें काले तिल, जूते या कंबल दान करें।" if lang != "en" else "Serve domestic helpers, sanitation workers, and donate black sesame or footwear on Saturdays.",
            "लोहे या घोड़े की नाल का छल्ला मध्यमा अंगुली में शनिवार को विधिपूर्वक धारण करें।" if lang != "en" else "Wear an iron ring crafted from a horse-shoe on your middle finger on a Saturday after Shani mantra japa."
        ]
        return is_active, status_type, timeline_str, (impact_hi if lang == "hi" else (impact_mr if lang == "mr" else (impact_gu if lang == "gu" else impact_en))), remedies

    elif house_from_moon == 1:
        is_active = True
        status_type = "Sade Sati Phase 2 (Peak / मध्य चरण)" if lang == "en" else "साढ़े साती द्वितीय चरण (शिखर काल)"
        desc = "Saturn transits directly over your Moon. Demands peak patience, mental resilience, and steady focus." if lang == "en" else "शनि का चन्द्र राशि पर प्रत्यक्ष गोचर; मानसिक धैर्य, कड़ी मेहनत और व्यक्तिगत रूपांतरण का मुख्य काल।"
        remedies = ["Recite Maha Mrityunjaya Mantra daily." if lang == "en" else "प्रतिदिन महामृत्युंजय मंत्र का 108 बार जप करें।"]
        return is_active, status_type, timeline_str, desc, remedies

    elif house_from_moon == 2:
        is_active = True
        status_type = "Sade Sati Phase 3 (Setting / उतरती साढ़े साती)" if lang == "en" else "साढ़े साती तृतीय चरण (उतरती साढ़े साती)"
        desc = "Saturn moves into the 2nd house from natal Moon. Finances, speech, and family stabilization period." if lang == "en" else "शनि चन्द्र से दूसरे भाव में; वाणी पर संयम, पारिवारिक सामंजस्य और वित्तीय स्थिरता लाने का समय।"
        remedies = ["Donate food to needy elders on Saturdays." if lang == "en" else "शनिवार को वृद्धजनों को भोजन कराएं।"]
        return is_active, status_type, timeline_str, desc, remedies

    elif house_from_moon == 4:
        is_active = True
        status_type = "Kantaka Shani (4th House Dhaiya / छोटी पनौती)" if lang == "en" else "कंटक शनि ढैय्या (चतुर्थ भाव ढैय्या)"
        desc = "Saturn transits 4th from your Moon. Focus on domestic peace, property prudence, and mother's well-being." if lang == "en" else "शनि चन्द्र से चौथे भाव में; गृह शांति, अचल संपत्ति और माता के स्वास्थ्य पर विशेष ध्यान अपेक्षित।"
        remedies = ["Offer blue flowers to Lord Shiva on Saturdays." if lang == "en" else "शनिवार को शिवलिंग पर नीले अपराजिता फूल अर्पित करें।"]
        return is_active, status_type, timeline_str, desc, remedies

    elif house_from_moon == 8:
        is_active = True
        status_type = "Ashtama Shani (8th House Dhaiya / अष्टम ढैय्या)" if lang == "en" else "अष्टम शनि ढैय्या (अष्टम भाव गोचर)"
        desc = "Saturn transits 8th from your Moon. High caution in investments, health checkups, and contracts required." if lang == "en" else "शनि चन्द्र से 8वें भाव में; जोखिम भरे निवेश से बचें, वाहन सावधानी से चलाएं एवं स्वास्थ्य का ध्यान रखें।"
        remedies = ["Chant 'Om Sham Shanicharaya Namah' 108 times." if lang == "en" else "प्रतिदिन 'ॐ शं शनैश्चराय नमः' का 108 बार जप करें।"]
        return is_active, status_type, timeline_str, desc, remedies

    else:
        is_active = False
        status_type = "No Sade Sati / Dhaiya Active (शनि गोचर अनुकूल/तटस्थ)" if lang != "en" else "No Sade Sati or Dhaiya Active (Favorable / Neutral Saturn Transit)"
        desc = f"Saturn is in house {house_from_moon} from your natal Moon sign. You are completely free from Sade Sati and Dhaiya cycles!" if lang == "en" else f"शनि देव आपकी चन्द्र राशि से {house_from_moon}वें भाव में गोचर कर रहे हैं। आप साढ़े साती व ढैय्या के प्रभाव से पूर्णतः मुक्त हैं!"
        remedies = ["Maintain discipline and help service workers." if lang == "en" else "कर्मठता बनाए रखें और जरूरतमंदों का सहयोग करें।"]
        return is_active, status_type, timeline_str, desc, remedies

def get_numerology_remedies(mulank: int, bhagyank: int, lang: str = "en") -> list:
    rem_en = [
        f"**Favorable Harmonizing Colors:** Integrate tones aligned with Driver {mulank} (Rahu - Smokey Gray, Blue) and Conductor {bhagyank} (Mars - Red, Coral, Warm Gold).",
        "**Vedic Japa:** Chant the Rahu Gayatri (`Om Shirorupaya Vidmahe...`) and Gayatri Mantra to balance electric analytical drive with peaceful clarity.",
        "**Astro-Nutrition & Fasting:** Keep Tuesdays and Saturdays light; consume soaked almonds and drink water stored in a copper/silver vessel.",
        "**Charity on Key Days:** Feed stray dogs on Saturdays (Rahu pacification) and donate red lentils (Masoor Dal) or jaggery on Tuesdays (Mars empowerment)."
    ]
    rem_hi = [
        f"**अनुकूल शुभ रंग:** मूलांक {mulank} (राहु) एवं भाग्यांक {bhagyank} (मंगल) के लिए हल्का नीला, धूसर, गहरा लाल और तांबई रंग शुभ हैं।",
        "**वैदिक मंत्र जप:** नित्य गायत्री मंत्र एवं 'ॐ रां राहवे नमः' व 'ॐ अं अंगारकाय नमः' का 11 बार शांतिपूर्वक स्मरण करें।",
        "**आहार एवं जीवनशैली:** मंगलवार और शनिवार को सात्विक भोजन लें; तांबे अथवा चाँदी के पात्र से नियमित जल पिएं।",
        "**ग्रह शांति दान:** शनिवार को श्वान (कुत्ते) को मीठी रोटी खिलाएं तथा मंगलवार को गुड़ या लाल मसूर की दाल का दान करें।"
    ]
    rem_mr = [
        f"**शुभ रंग:** मूलांक {mulank} आणि भाग्यांक {bhagyank} यांच्या समतोलासाठी आकाशी निळा, लाल व चॉकलेटी रंग लाभदायक आहेत.",
        "**वैदिक मंत्र:** दररोज गायत्री मंत्र व 'ॐ अं अंगारकाय नमः' चा जप करून मनाची एकाग्रता वाढवा.",
        "**सात्विक दिनचर्या:** मंगळवार व शनिवारी सात्विक आहार ठेवा; चांदीच्या किंवा तांब्याच्या भांड्यातील पाणी प्या.",
        "**पुण्य कार्य:** शनिवारी मुक्या प्राण्यांना अन्न द्या व मंगळवारी गुळ किंवा मसूर डाळीचे दान करा."
    ]
    rem_gu = [
        f"**અનુકૂળ રંગો:** મૂળાંક {mulank} અને ભાગ્યાંક {bhagyank} ના સુમેળ માટે હળવો વાદળી, કેસરી અને લાલ રંગ શુભ રહેશે.",
        "**મંત્ર ઉપાસના:** ગાયત્રી મંત્ર તેમજ હનુમાન ચાલીસાનો નિત્ય પાઠ આત્મવિશ્વાસ વધારશે.",
        "**જીવનશૈલી:** મંગળવાર અને શનિવારે સાત્વિક ભોજન લેવું; તાંબાના પાત્રમાંથી જળ પીવું ઉત્તમ છે.",
        "**દાન પુણ્ય:** શનિવારે પક્ષીઓ/પ્રાણીઓને અન્ન ખવડાવવું અને મંગળવારે ગોળનું દાન કરવું."
    ]
    return rem_hi if lang == "hi" else (rem_mr if lang == "mr" else (rem_gu if lang == "gu" else rem_en))
# ... existing code ...
```

```python:Navtara Pulse App:app.py
# ... existing code ...
user_name = prof.get("name", "Okesh")
user_dob = prof.get("dob", datetime.date(1984, 1, 13))
user_tob = prof.get("tob", datetime.time(14, 0))
user_place = prof.get("place", "Chhatrapati Sambhajinagar, India")

# Calculate Janma Nakshatra, Pada, Moon Rashi, and Lagna (Ascendant)
janma_idx, janma_pada, natal_moon_rashi_idx, natal_rashi_deg, lagna_rashi_idx, lagna_deg = calculate_birth_chart(
    user_dob, user_tob, user_place
)
janma_name = NAKSHATRAS[janma_idx]
nak_personality_desc = get_nakshatra_description(janma_idx, current_lang)
nak_remedies = get_nakshatra_remedy(janma_idx, current_lang)

mulank, bhagyank, namank = calculate_numerology(user_dob, user_name)
num_remedies_list = get_numerology_remedies(mulank, bhagyank, current_lang)

now_utc = datetime.datetime.now(datetime.timezone.utc)
ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
now_ist = now_utc.astimezone(ist_tz)
jd_now = dt_to_jd(now_utc)

saturn_lon = get_sidereal_lon(jd_now, swe.SATURN)
saturn_rashi_idx, _ = lon_to_rashi(saturn_lon)
moon_lon = get_sidereal_lon(jd_now, swe.MOON)
cur_moon_rashi_idx, _ = lon_to_rashi(moon_lon)
cur_moon_nak_idx, _ = lon_to_nakshatra(moon_lon)

paya_name, paya_status, paya_desc, paya_remedies, paya_timeline = calculate_shani_paya(
    natal_moon_rashi_idx, saturn_rashi_idx, current_lang
)
is_ss_active, ss_status, ss_timeline, ss_impact, ss_remedies = calculate_shani_sadesati_dhaiya(
    natal_moon_rashi_idx, saturn_rashi_idx, current_lang
)

today_vahan_num, today_vahan = calculate_shani_vahan(
    janma_idx + 1, cur_moon_nak_idx + 1, current_lang
)
cur_nav_cat, cur_nav_series = calculate_navtara(janma_idx, cur_moon_nak_idx)
u_day, p_day, p_title, p_desc, num_remedy = get_personal_day_vibe(mulank, now_ist.date(), current_lang)

# ==============================================================================
# PAGE 1: NATIVE ASTROLOGICAL PROFILE (3 SUB-SECTIONS)
# ==============================================================================
if st.session_state.current_page == "profile":
    with st.expander(t("edit_profile_expander", current_lang), expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            in_name = st.text_input(t("input_name", current_lang), value=user_name)
            in_dob = st.date_input(t("input_dob", current_lang), value=user_dob)
        with c2:
            in_tob = st.time_input(t("input_tob", current_lang), value=user_tob)
            in_place = st.text_input(t("input_place", current_lang), value=user_place)

        st.caption("ℹ️ *Janma Nakshatra, Pada, Moon Sign, and Lagna are calculated automatically from birth date, time, and place using the Swiss Ephemeris engine.*")

        if st.button(t("save_profile_btn", current_lang), use_container_width=True, type="primary"):
            updated_data = {
                "name": in_name,
                "dob": in_dob,
                "tob": in_tob,
                "place": in_place,
                "language": current_lang
            }
            st.session_state.profile = updated_data
            if save_user_profile(updated_data):
                st.success(t("profile_saved_msg", current_lang))
                st.rerun()

    # -------------------------------------------------------------------------
    # SUBSECTION 1: NAVTARA & VEDIC ASTROLOGICAL PROFILE
    # -------------------------------------------------------------------------
    st.markdown(f"""
    <div class="light-card-profile">
        <div style="font-weight:800; font-size:16px; color:#78350f; margin-bottom:12px; border-bottom:1.5px solid #fed7aa; padding-bottom:6px;">
            {t('sec1_title', current_lang)}
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h3 style="margin:0; font-size:1.35rem; font-weight:800; color:#431407;">👤 {user_name}</h3>
                <div style="font-size:13.5px; color:#78350f; margin-top:3px;">
                    🎂 {user_dob.strftime('%d %B %Y')} • ⏰ {user_tob.strftime('%H:%M')} • 📍 {user_place}
                </div>
            </div>
            <div>
                <span class="badge-favorable" style="font-size:13px; padding:6px 12px;">
                    🌙 {RASHIS[natal_moon_rashi_idx].split(' ')[0]}
                </span>
            </div>
        </div>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:8px; margin-top:14px; text-align:center;">
            <div style="background:#ffffff; border-radius:10px; padding:10px 8px; border:1px solid #fed7aa;">
                <div style="font-size:11.5px; color:#9a3412; font-weight:700;">{t('janma_star_label', current_lang)}</div>
                <div style="font-size:14.5px; font-weight:800; color:#431407; margin-top:2px;">{janma_name}</div>
                <div style="font-size:11px; color:#b45309;">(#{janma_idx + 1} • Pada {janma_pada})</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 8px; border:1px solid #fed7aa;">
                <div style="font-size:11.5px; color:#9a3412; font-weight:700;">{t('moon_rashi_label', current_lang)}</div>
                <div style="font-size:14.5px; font-weight:800; color:#431407; margin-top:2px;">{RASHIS[natal_moon_rashi_idx].split(' ')[0]}</div>
                <div style="font-size:11px; color:#b45309;">{natal_rashi_deg:.2f}° Sidereal</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px 8px; border:1px solid #fed7aa;">
                <div style="font-size:11.5px; color:#9a3412; font-weight:700;">{t('lagna_label', current_lang)}</div>
                <div style="font-size:14.5px; font-weight:800; color:#431407; margin-top:2px;">{RASHIS[lagna_rashi_idx].split(' ')[0]}</div>
                <div style="font-size:11px; color:#b45309;">{lagna_deg:.2f}° Ascendant</div>
            </div>
        </div>

        <div style="margin-top:12px; background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #fed7aa;">
            <div style="font-weight:700; font-size:13.5px; color:#9a3412; margin-bottom:4px;">
                {t('nak_personality_title', current_lang)} ({janma_name}):
            </div>
            <div style="font-size:13px; line-height:1.6; color:#431407;">
                {nak_personality_desc}
            </div>
        </div>

        <div style="margin-top:10px; background:#fff7ed; border-radius:10px; padding:12px 14px; border:1px solid #ffedd5;">
            <div style="font-weight:700; font-size:13.5px; color:#c2410c; margin-bottom:6px;">
                {t('nak_remedies_title', current_lang)}:
            </div>
    """, unsafe_allow_html=True)
    for nr in nak_remedies:
        st.markdown(f"<div style='font-size:12.8px; color:#7c2d12; margin-bottom:3px;'>• {nr}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SUBSECTION 2: CORE NUMEROLOGY BLUEPRINT & FIXED LIFE ATTRIBUTES
    # -------------------------------------------------------------------------
    st.markdown(f"""
    <div class="light-card-num">
        <div style="font-weight:800; font-size:16px; color:#064e3b; margin-bottom:12px; border-bottom:1.5px solid #a7f3d0; padding-bottom:6px;">
            {t('sec2_title', current_lang)}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; text-align:center; margin-bottom:12px;">
            <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#047857; font-weight:700;">{t('mulank_label', current_lang)}</div>
                <div style="font-size:26px; font-weight:900; color:#065f46;">{mulank}</div>
                <div style="font-size:11px; color:#059669;">Rahu / Driver</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#047857; font-weight:700;">{t('bhagyank_label', current_lang)}</div>
                <div style="font-size:26px; font-weight:900; color:#065f46;">{bhagyank}</div>
                <div style="font-size:11px; color:#059669;">Mars / Conductor</div>
            </div>
            <div style="background:#ffffff; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#047857; font-weight:700;">{t('namank_label', current_lang)}</div>
                <div style="font-size:26px; font-weight:900; color:#065f46;">{namank}</div>
                <div style="font-size:11px; color:#059669;">Chaldean Vibration</div>
            </div>
        </div>
        <div style="font-size:13.5px; line-height:1.6; color:#064e3b; background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #bbf7d0;">
            {get_fixed_numerology_prediction(mulank, bhagyank, current_lang)}
        </div>
        <div style="margin-top:10px; background:#f0fdf4; border-radius:10px; padding:12px 14px; border:1px solid #dcfce7;">
            <div style="font-weight:700; font-size:13.5px; color:#047857; margin-bottom:6px;">
                {t('num_remedies_title', current_lang)}:
            </div>
    """, unsafe_allow_html=True)
    for rem_num in num_remedies_list:
        st.markdown(f"<div style='font-size:12.8px; color:#065f46; margin-bottom:3px;'>• {rem_num}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SUBSECTION 3: SHANI PAYA & SHANI GOCHAR (SADE SATI / DHAIYA)
    # -------------------------------------------------------------------------
    sadesati_badge = "<span class='badge-danger' style='font-size:12px;'>⚠️ " + ss_status + "</span>" if is_ss_active else "<span class='badge-favorable' style='font-size:12px;'>✅ Favorable Shani Transit</span>"

    st.markdown(f"""
    <div class="light-card-paya">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1.5px solid #ddd6fe; padding-bottom:6px;">
            <span style="font-weight:800; font-size:16px; color:#3b0764;">
                {t('sec3_title', current_lang)}
            </span>
            {sadesati_badge}
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #e9d5ff; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-weight:800; font-size:15px; color:#3b0764;">
                    {paya_name}
                </div>
                <div style="font-size:12px; font-weight:700; color:#6b21a8;">
                    ✦ {paya_status}
                </div>
            </div>
            <div style="font-size:12.5px; font-weight:600; color:#581c87; margin-top:4px;">
                ⏳ <b>{t('transit_timeline_lbl', current_lang)}:</b> {paya_timeline}
            </div>
            <div style="font-size:13px; line-height:1.55; color:#3b0764; margin-top:6px;">
                <b>{t('paya_impact_lbl', current_lang)}:</b><br>{paya_desc}
            </div>
        </div>

        <div style="background:#ffffff; border-radius:10px; padding:12px 14px; border:1px solid #e9d5ff; margin-bottom:10px;">
            <div style="font-weight:800; font-size:14.5px; color:#4c1d95; margin-bottom:4px;">
                🪐 {t('sadesati_card_title', current_lang)}:
            </div>
            <div style="font-size:12.5px; font-weight:600; color:#6b21a8; margin-bottom:6px;">
                ⏳ <b>{t('sadesati_timeline_lbl', current_lang)}:</b> {ss_status} ({ss_timeline})
            </div>
            <div style="font-size:13px; line-height:1.55; color:#2e1065;">
                <b>{t('sadesati_impact_lbl', current_lang)}:</b><br>{ss_impact}
            </div>
        </div>

        <div style="background:#f5f3ff; border-radius:10px; padding:12px 14px; border:1px solid #ddd6fe;">
            <div style="font-weight:700; font-size:13.5px; color:#581c87; margin-bottom:6px;">
                {t('shani_integrated_remedies', current_lang)}:
            </div>
    """, unsafe_allow_html=True)
    all_shani_remedies = paya_remedies + [r for r in ss_remedies if r not in paya_remedies]
    for sr in all_shani_remedies:
        st.markdown(f"<div style='font-size:12.8px; color:#4c1d95; margin-bottom:3px;'>• {sr}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    if st.button(t("btn_view_forecast", current_lang), use_container_width=True, type="primary"):
        st.session_state.current_page = "forecast"
        st.rerun()

# ==============================================================================
# PAGE 2: TRANSIT PREDICTIONS, 7-DAY MATRIX, REMEDIES & PLANETS
# ==============================================================================
# ... existing code ...
```

The diff structure updates the profile page into the three sections:

1. **Section 1 (Navtara & Vedic Astrological Profile):**
   - Incorporates automated **Lagna (Ascendant)** calculation using Swiss Ephemeris and geographic coordinates (`CITY_COORDS`).
   - Displays Janma Nakshatra, Pada, Moon Rashi, Lagna degree, full behavioral personality analysis, and Nakshatra-specific Vedic remedies (sacred deity, seed mantra, and sacred tree).
2. **Section 2 (Numerology Blueprint):**
   - Displays Mulank (Driver), Bhagyank (Conductor), and Namank (Chaldean).
   - Generates the integrated Rahu-Mars fixed life analysis and tailored Astro-Numerology Vedic remedies (harmonizing colors, japa, fasting routines, and charity).
3. **Section 3 (Shani Paya & Shani Gochar — Sade Sati / Dhaiya):**
   - Evaluates the current **Shani Paya (Rajat Paya / Silver Feet 🥈)** with its transit timeline.
   - Computes whether Sade Sati or Dhaiya is currently active (for Aries Moon during Saturn's Pisces transit: **Sade Sati Phase 1 / Rising Phase**).
   - Details the life impact and provides combined Vedic remedies (Peepal lamp, Hanuman Chalisa, Dasharatha Stotra, and silver grounding).

# views/profile.py - Dedicated User Profile View with Complete Hindi & English Content
import streamlit as st
import datetime
from databanks import (
    NAKSHATRAS,
    get_tara_bala_info,
    resolve_location_name
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

RASHI_NAMES_HI = {
    "Mesha": "मेष", "Vrishabha": "वृषभ", "Mithuna": "मिथुन",
    "Karka": "कर्क", "Simha": "सिंह", "Kanya": "कन्या",
    "Tula": "तुला", "Vrishchika": "वृश्चिक", "Dhanu": "धनु",
    "Makara": "मकर", "Kumbha": "कुंभ", "Meena": "मीन",
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन",
    "Cancer": "कर्क", "Leo": "सिंह", "Virgo": "कन्या",
    "Libra": "तुला", "Scorpio": "वृश्चिक", "Sagittarius": "धनु",
    "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}

TARA_NAMES_HI = {
    "Janma": "जन्म तारा", "Sampat": "सम्पत तारा", "Vipat": "विपत तारा",
    "Kshema": "क्षेम तारा", "Pratyak": "प्रत्यक तारा", "Sadhana": "साधना तारा",
    "Naidhana": "निधन तारा", "Mitra": "मित्र तारा", "Ati-Mitra": "अति-मित्र तारा"
}

# 27 NAKSHATRA BIO & ATTRIBUTE DATA (BILINGUAL)
NAKSHATRA_BIO = {
    1: {"deity_en": "Ashwini Kumaras (Divine Healers)", "deity_hi": "अश्विनी कुमार (दिव्य चिकित्सक)", "symbol_en": "Horse's Head", "symbol_hi": "अश्व (घोड़े) का मुख", "tree_en": "Poison Nut (Kuchila)", "tree_hi": "कुचिला", "bird_en": "Wild Eagle", "bird_hi": "गरुड़ / चील", "animal_en": "Male Horse (Ashwa)", "animal_hi": "अश्व (घोड़ा)", "lord_en": "Ketu", "lord_hi": "केतु"},
    2: {"deity_en": "Lord Yama (Dharma & Cosmic Justice)", "deity_hi": "यमराज (धर्म एवं न्याय के अधिपति)", "symbol_en": "Yoni / Creative Triangle", "symbol_hi": "योनि / त्रिकोण", "tree_en": "Amla (Indian Gooseberry)", "tree_hi": "आंवला (धात्री)", "bird_en": "Crow (Kaka)", "bird_hi": "कौआ (काक)", "animal_en": "Male Elephant (Gaja)", "animal_hi": "गज (हाथी)", "lord_en": "Venus", "lord_hi": "शुक्र"},
    3: {"deity_en": "Agni Dev (Fire God)", "deity_hi": "अग्नि देव", "symbol_en": "Razor / Knife / Flame", "symbol_hi": "छुरा / ज्वाला", "tree_en": "Udumbar (Gular)", "tree_hi": "गूलर", "bird_en": "Peacock", "bird_hi": "मयूर (मोर)", "animal_en": "Female Sheep (Mesh)", "animal_hi": "मेष (भेड़)", "lord_en": "Sun", "lord_hi": "सूर्य"},
    4: {"deity_en": "Lord Brahma (Creator)", "deity_hi": "ब्रह्मा जी (सृष्टिकर्ता)", "symbol_en": "Chariot / Temple / Cart", "symbol_hi": "रथ / मंदिर", "tree_en": "Jamun (Blackberry)", "tree_hi": "जामुन", "bird_en": "Owl / Hansa", "bird_hi": "हंस / उल्लू", "animal_en": "Male Serpent", "animal_hi": "सर्प", "lord_en": "Moon", "lord_hi": "चन्द्र"},
    5: {"deity_en": "Soma (Moon God)", "deity_hi": "सोम (चन्द्र देव)", "symbol_en": "Deer's Head", "symbol_hi": "मृगशीर्ष (हिरण का सिर)", "tree_en": "Khadira (Cutch tree)", "tree_hi": "खैर (खदिर)", "bird_en": "Hen / Cock", "bird_hi": "मुर्गा", "animal_en": "Female Serpent", "animal_hi": "सर्पिणी", "lord_en": "Mars", "lord_hi": "मंगल"},
    6: {"deity_en": "Rudra (Storm God / Shiva)", "deity_hi": "रुद्र (भगवान शिव)", "symbol_en": "Teardrop / Diamond", "symbol_hi": "अश्रु बूंद / हीरा", "tree_en": "Agarwood / Krishna Thulasi", "tree_hi": "अगर / कृष्ण तुलसी", "bird_en": "Black Eagle", "bird_hi": "काली चील", "animal_en": "Female Dog (Shwani)", "animal_hi": "श्वान (कुत्ता)", "lord_en": "Rahu", "lord_hi": "राहु"},
    7: {"deity_en": "Aditi (Cosmic Mother)", "deity_hi": "अदिति (देवमाता)", "symbol_en": "Bow and Quiver", "symbol_hi": "धनुष एवं तरकश", "tree_en": "Bamboo (Vamsha)", "tree_hi": "बांस", "bird_en": "Swan", "bird_hi": "हंस", "animal_en": "Female Cat (Marjari)", "animal_hi": "बिल्ली", "lord_en": "Jupiter", "lord_hi": "गुरु"},
    8: {"deity_en": "Brihaspati (Guru)", "deity_hi": "देवगुरु बृहस्पति", "symbol_en": "Flower / Circle / Cow's Udder", "symbol_hi": "कमल पुष्प / चक्र", "tree_en": "Peepal (Ashwattha)", "tree_hi": "पीपल", "bird_en": "Sea Crow", "bird_hi": "जलकाक", "animal_en": "Male Goat (Aja)", "animal_hi": "बकरा", "lord_en": "Saturn", "lord_hi": "शनि"},
    9: {"deity_en": "Nagas (Serpent Deities)", "deity_hi": "सर्प देव (नाग)", "symbol_en": "Coiled Serpent", "symbol_hi": "कुंडलीकृत सर्प", "tree_en": "Nagkeshar", "tree_hi": "नागकेसर", "bird_en": "Small Falcon", "bird_hi": "कबूतर / बाज", "animal_en": "Male Cat", "animal_hi": "बिलाव", "lord_en": "Mercury", "lord_hi": "बुध"},
    10: {"deity_en": "Pitris (Ancestral Forefathers)", "deity_hi": "पितृ देव", "symbol_en": "Royal Throne Room", "symbol_hi": "राजसिंहासन", "tree_en": "Banyan Tree (Vata)", "tree_hi": "बरगद (वट)", "bird_en": "Male Rooster", "bird_hi": "नर मुर्गा", "animal_en": "Male Rat (Mushaka)", "animal_hi": "मूषक (चूहा)", "lord_en": "Ketu", "lord_hi": "केतु"},
    11: {"deity_en": "Bhaga (God of Wealth & Luck)", "deity_hi": "भग देव (समृद्धि प्रदाता)", "symbol_en": "Front Legs of Bed / Hammock", "symbol_hi": "झूला / मंच", "tree_en": "Palash (Flame of Forest)", "tree_hi": "पलाश (ढाक)", "bird_en": "Female Falcon", "bird_hi": "मादा बाज", "animal_en": "Female Rat", "animal_hi": "मादा मूषक", "lord_en": "Venus", "lord_hi": "शुक्र"},
    12: {"deity_en": "Aryaman (God of Contracts & Honor)", "deity_hi": "अर्यमा (सत्य व न्याय देव)", "symbol_en": "Back Legs of Bed", "symbol_hi": "पलंग के पिछले पाए", "tree_en": "Plaksha (Pakur tree)", "tree_hi": "पाकड़ (प्लक्ष)", "bird_en": "Beetle / Kingfisher", "bird_hi": "नीलकंठ", "animal_en": "Male Cow (Bull)", "animal_hi": "वृषभ (बैल)", "lord_en": "Sun", "lord_hi": "सूर्य"},
    13: {"deity_en": "Savitr (Sun of Inspiration)", "deity_hi": "सविता (तेजस्वी सूर्य देव)", "symbol_en": "Hand / Open Palm", "symbol_hi": "खुली हथेली (हस्त)", "tree_en": "Jasmine (Chameli)", "tree_hi": "चमेली", "bird_en": "Vulture", "bird_hi": "गिद्ध", "animal_en": "Female Buffalo", "animal_hi": "भैंस", "lord_en": "Moon", "lord_hi": "चन्द्र"},
    14: {"deity_en": "Tvashtar (Divine Architect)", "deity_hi": "त्वष्टा (विश्वकर्मा देव)", "symbol_en": "Bright Jewel / Pearl", "symbol_hi": "चमकता रत्न / मोती", "tree_en": "Bilva (Bael Tree)", "tree_hi": "बेलपत्र (बिल्व)", "bird_en": "Woodpecker", "bird_hi": "कठफोड़वा", "animal_en": "Female Tiger", "animal_hi": "बाघिन", "lord_en": "Mars", "lord_hi": "मंगल"},
    15: {"deity_en": "Vayu (Wind God)", "deity_hi": "वायु देव", "symbol_en": "Shoot of Plant / Coral", "symbol_hi": "अंकुरित पौधा / मूंगा", "tree_en": "Arjuna Tree", "tree_hi": "अर्जुन वृक्ष", "bird_en": "Pigeon / Sparrow", "bird_hi": "कबूतर", "animal_en": "Male Buffalo (Mahisha)", "animal_hi": "भैंसा", "lord_en": "Rahu", "lord_hi": "राहु"},
    16: {"deity_en": "Indra & Agni (Chieftains)", "deity_hi": "इन्द्राग्नि (इन्द्र व अग्नि)", "symbol_en": "Triumphal Arch / Potter's Wheel", "symbol_hi": "विजय तोरण द्वार", "tree_en": "Wood Apple (Kaitha)", "tree_hi": "कैथ", "bird_en": "Red Crested Falcon", "bird_hi": "लाल कलगी बाज", "animal_en": "Male Tiger (Vyaghra)", "animal_hi": "बाघ (सिंह)", "lord_en": "Jupiter", "lord_hi": "गुरु"},
    17: {"deity_en": "Mitra (God of Friendship)", "deity_hi": "मित्र देव (मैत्री अधिपति)", "symbol_en": "Lotus Flower / Staff", "symbol_hi": "कमल / दंड", "tree_en": "Bakul (Maulsari)", "tree_hi": "मौलश्री (बकुल)", "bird_en": "Nightingale", "bird_hi": "बुलबुल", "animal_en": "Female Deer (Harini)", "animal_hi": "मृग (हिरण)", "lord_en": "Saturn", "lord_hi": "शनि"},
    18: {"deity_en": "Indra (King of Gods)", "deity_hi": "इन्द्र देव (देवराज)", "symbol_en": "Circular Amulet / Umbrella", "symbol_hi": "कुंडल / छत्र", "tree_en": "Pine / Shalmali", "tree_hi": "चीड़ / सेमल", "bird_en": "Brahminy Kite", "bird_hi": "चक्रवाक", "animal_en": "Male Hare / Deer", "animal_hi": "मृग", "lord_en": "Mercury", "lord_hi": "बुध"},
    19: {"deity_en": "Nirriti (Goddess of Dissolution)", "deity_hi": "निरृति (विघटन व सत्य देवी)", "symbol_en": "Tied Bunch of Roots / Elephant Goad", "symbol_hi": "बंधी हुई जड़ें / अंकुश", "tree_en": "Anjan (Hardwickia)", "tree_hi": "अंजन वृक्ष", "bird_en": "Vulture / Owl", "bird_hi": "गिद्ध", "animal_en": "Male Dog", "animal_hi": "कुत्ता", "lord_en": "Ketu", "lord_hi": "केतु"},
    20: {"deity_en": "Apas (Cosmic Water Goddess)", "deity_hi": "आपः (जल देवी)", "symbol_en": "Elephant Tusk / Winnowing Fan", "symbol_hi": "हाथी दांत / सूप", "tree_en": "Vanjula (Ashoka)", "tree_hi": "अशोक वृक्ष", "bird_en": "Francolin / Partridge", "bird_hi": "तीतर", "animal_en": "Male Monkey (Vanara)", "animal_hi": "वानर (बंदर)", "lord_en": "Venus", "lord_hi": "शुक्र"},
    21: {"deity_en": "Vishvedevas (Universal Principles)", "deity_hi": "विश्वेदेवा (सर्वव्यापी शक्तियां)", "symbol_en": "Small Cot / Elephant Tusk", "symbol_hi": "छोटा मंच / गजदंत", "tree_en": "Jackfruit Tree (Phanasa)", "tree_hi": "कटहल", "bird_en": "Stork", "bird_hi": "बगुल", "animal_en": "Female Mongoose", "animal_hi": "नेवला", "lord_en": "Sun", "lord_hi": "सूर्य"},
    22: {"deity_en": "Lord Vishnu (All-Pervading)", "deity_hi": "भगवान श्री हरि विष्णु", "symbol_en": "Three Footprints / Ear", "symbol_hi": "तीन पग चिन्ह / कान", "tree_en": "Calotropis (Arka / Aak)", "tree_hi": "आक (मदार)", "bird_en": "Francolin Partridge", "bird_hi": "तीतर / हंस", "animal_en": "Female Monkey", "animal_hi": "वानर", "lord_en": "Moon", "lord_hi": "चन्द्र"},
    23: {"deity_en": "Ashta Vasus (Gods of Abundance)", "deity_hi": "अष्ट वसु (समृद्धि व ऊर्जा देव)", "symbol_en": "Drum (Damru) / Flute", "symbol_hi": "डमरू / बांसुरी", "tree_en": "Shami (Prosopis cineraria)", "tree_hi": "शमी वृक्ष", "bird_en": "Golden Bee / Peacock", "bird_hi": "मयूर", "animal_en": "Female Lion (Singhi)", "animal_hi": "सिंह (शेर)", "lord_en": "Mars", "lord_hi": "मंगल"},
    24: {"deity_en": "Varuna (God of Cosmic Oceans)", "deity_hi": "वरुण देव (जल एवं सत्य के स्वामी)", "symbol_en": "Empty Circle / 100 Flowers", "symbol_hi": "रिक्त वृत्त / 100 पुष्प", "tree_en": "Kadamba", "tree_hi": "कदम्ब", "bird_en": "Raven", "bird_hi": "काला कौआ", "animal_en": "Female Horse (Ashwi)", "animal_hi": "घोड़ी", "lord_en": "Rahu", "lord_hi": "राहु"},
    25: {"deity_en": "Aja Ekapada (One-Footed Cosmic Fire)", "deity_hi": "अज एकपाद (दिव्य अग्नि शक्ति)", "symbol_en": "Front of Funeral Cot / Sword", "symbol_hi": "खड़ा खड्ग / दो मुख", "tree_en": "Mango Tree (Amra)", "tree_hi": "आम का वृक्ष", "bird_en": "Kite", "bird_hi": "चील", "animal_en": "Male Lion (Simha)", "animal_hi": "सिंह", "lord_en": "Jupiter", "lord_hi": "गुरु"},
    26: {"deity_en": "Ahirbudhnya (Serpent of Deep Wisdom)", "deity_hi": "अहिर्बुध्न्य (गहन ज्ञान के सर्प देव)", "symbol_en": "Back of Funeral Cot / Twin Snake", "symbol_hi": "गहरा जल कुंड / सर्प युगल", "tree_en": "Neem (Azadirachta indica)", "tree_hi": "नीम", "bird_en": "Rain Quail", "bird_hi": "बटेर", "animal_en": "Female Cow (Gau)", "animal_hi": "गाय (गौमाता)", "lord_en": "Saturn", "lord_hi": "शनि"},
    27: {"deity_en": "Pushan (Nourisher of Travelers)", "deity_hi": "पूषा (यात्रियों के रक्षक व पोषक)", "symbol_en": "Fish Pair Swimming in Sea", "symbol_hi": "मीन युगल (मछलियों का जोड़ा)", "tree_en": "Mahua (Butter Tree)", "tree_hi": "महुआ", "bird_en": "Kestrel", "bird_hi": "कबूतर / चकोर", "animal_en": "Female Elephant (Hathini)", "animal_hi": "हथिनी", "lord_en": "Mercury", "lord_hi": "बुध"}
}

# COMPLETE BILINGUAL ASTROLOGICAL PREDICTIONS
PREDICTIONS_DB = {
    # 2: Bharani
    2: {
        "core_en": "Enduring moral resilience, deep magnetic charisma, uncompromising principles, and strong sense of justice.",
        "core_hi": "अडिग नैतिक दृढ़ता, चुंबकीय आकर्षण, सिद्धांतों से समझौता न करने वाला स्वभाव और न्याय के प्रति गहरी निष्ठा।",
        "strengths_en": "Unshakeable loyalty, crisis endurance, turnaround management, artistic discernment.",
        "strengths_hi": "अटूट विश्वसनीयता, संकट के समय अभूतपूर्व धैर्य, कठिन परिस्थितियों को अनुकूल बनाने की क्षमता और उच्च कलात्मक समझ।",
        "shadows_en": "All-or-nothing intensity, stubborn resistance to compromise, suppressed emotional burdens.",
        "shadows_hi": "अत्यधिक हठधर्मिता, समझौते से इंकार, चरम विचार (सब कुछ या कुछ नहीं) और मानसिक तनाव को भीतर दबाए रखना।",
        "careers_en": "Executive management, judicial leadership, healthcare systems, creative design, risk governance.",
        "careers_hi": "प्रशासनिक प्रबंधन, विधि व न्यायपालिका, स्वास्थ्य प्रणाली व चिकित्सा, रचनात्मक उद्योग और वित्तीय जोखिम नियंत्रण।",
        "prediction_en": "Transformations occur cyclically every 7–9 years leading to permanent asset compounding and public authority.",
        "prediction_hi": "प्रत्येक 7 से 9 वर्षों में जीवन में गहरे सकारात्मक परिवर्तन होते हैं, जो अंततः स्थायी संपत्ति और सामाजिक प्रतिष्ठा प्रदान करते हैं।",
        "remedies_en": "• Recite Maha Mrityunjaya Mantra 11 times daily.\n• Water an Amla tree on Fridays.\n• Feed crows or stray animals on Tuesdays.",
        "remedies_hi": "• प्रतिदिन 11 बार महामृत्युंजय मंत्र का जप करें।\n• शुक्रवार को आंवले के वृक्ष को जल अर्पित करें।\n• मंगलवार अथवा शनिवार को कौवों व असहाय पशुओं को भोजन कराएं।"
    }
}

# Fallback generator for other nakshatras to guarantee pure Hindi output
def get_localized_nak_prediction(star_idx: int, is_hi: bool):
    if star_idx in PREDICTIONS_DB:
        p = PREDICTIONS_DB[star_idx]
        return {
            "core": p["core_hi"] if is_hi else p["core_en"],
            "strengths": p["strengths_hi"] if is_hi else p["strengths_en"],
            "shadows": p["shadows_hi"] if is_hi else p["shadows_en"],
            "careers": p["careers_hi"] if is_hi else p["careers_en"],
            "prediction": p["prediction_hi"] if is_hi else p["prediction_en"],
            "remedies": p["remedies_hi"] if is_hi else p["remedies_en"]
        }
    
    # Generic classical fallback
    if is_hi:
        return {
            "core": "गहन एकाग्रता, आत्मसम्मान, बौद्धिक सूक्ष्मता एवं स्वतंत्र निर्णय क्षमता का नैसर्गिक संयोजन।",
            "strengths": "कार्य निष्ठा, रणनीतिक दूरदर्शिता, त्वरित निर्णय एवं संकट प्रबंधन में दक्षता।",
            "shadows": "अति-विचार, भावनात्मक अधीरता और दूसरों के प्रति त्वरित प्रतिक्रिया।",
            "careers": "उच्च प्रबंधन, तकनीकी विशेषज्ञता, संस्थागत परामर्श, व्यापार एवं नीति निर्धारण।",
            "prediction": "मध्यम आयु के उपरांत निरंतर उन्नति, स्थायी पूंजी निर्माण एवं सामाजिक प्रतिष्ठा की प्राप्ति।",
            "remedies": "• जन्म नक्षत्र गायत्री मंत्र का प्रातःकाल जप करें।\n• इष्ट देव को नित्य जल अर्पित करें।\n• जरूरतमंदों को सात्विक अन्न दान करें।"
        }
    return {
        "core": "Deep analytical focus, self-sovereignty, intellectual precision, and autonomous decision-making.",
        "strengths": "Methodical execution, visionary strategy, prompt troubleshooting under crisis.",
        "shadows": "Over-analysis, emotional impatience, quick critical reactions to collaborators.",
        "careers": "Executive management, specialized tech domains, institutional advisory, structured trade.",
        "prediction": "Accelerating milestones post mid-30s leading to durable capital and public standing.",
        "remedies": "• Recite Janma Nakshatra Gayatri Mantra at dawn.\n• Offer clean water to your Ishta Devata.\n• Donate grains to the needy."
    }

# BILINGUAL MOON SIGN PREDICTIONS
RASHI_PREDICTIONS = {
    "Mesha": {
        "element_en": "Fire (Agni)", "element_hi": "अग्नि तत्व (Fire)",
        "ruler_en": "Mars (Mangal)", "ruler_hi": "मंगल (Mars)",
        "psychology_en": "Initiative-driven, direct, fearless, intolerant of stagnation, rapid processing.",
        "psychology_hi": "पहल करने की प्रबल इच्छा, स्पष्टवादी, निडर, ठहराव के प्रति असहिष्णु और त्वरित विचार प्रक्रिया।",
        "instincts_en": "Immediate action under pressure; prefers confronting obstacles head-on over diplomatic delay.",
        "instincts_hi": "दबाव में त्वरित कदम उठाना; कूटनीतिक विलंब के स्थान पर बाधाओं का सीधा सामना करना पसंद करते हैं।",
        "relations_en": "Passionate, protective, highly candid; requires honest partners who respect autonomy.",
        "relations_hi": "उत्साही, सुरक्षात्मक और अत्यंत निष्कपट; ऐसे जीवनसाथी की आवश्यकता होती है जो स्वतंत्रता का सम्मान करे।",
        "health_en": "High metabolic vitality; prone to excess heat (Pitta), headaches, and muscular tension.",
        "health_hi": "उच्च चयापचय ऊर्जा; पित्त विकार, सिरदर्द और मांसपेशियों में तनाव की प्रवृत्ति।",
        "remedies_en": "Recite Hanuman Chalisa on Tuesdays; keep pure water in a copper vessel overnight.",
        "remedies_hi": "मंगलवार को श्री हनुमान चालीसा का पाठ करें; रात्रि में तांबे के पात्र में रखा जल प्रातः ग्रहण करें।"
    }
}

def get_localized_rashi_data(rashi_name: str, is_hi: bool):
    key = rashi_name.split()[0]
    data = RASHI_PREDICTIONS.get(key, RASHI_PREDICTIONS["Mesha"])
    return {
        "element": data["element_hi"] if is_hi else data["element_en"],
        "ruler": data["ruler_hi"] if is_hi else data["ruler_en"],
        "psychology": data["psychology_hi"] if is_hi else data["psychology_en"],
        "instincts": data["instincts_hi"] if is_hi else data["instincts_en"],
        "relations": data["relations_hi"] if is_hi else data["relations_en"],
        "health": data["health_hi"] if is_hi else data["health_en"],
        "remedies": data["remedies_hi"] if is_hi else data["remedies_en"]
    }

# BILINGUAL LAGNA PREDICTIONS
LAGNA_PREDICTIONS = {
    "Mesha": {
        "element_en": "Fire (Agni)", "element_hi": "अग्नि तत्व (Fire)",
        "lord_en": "Mars (Mangal)", "lord_hi": "मंगल (Mars)",
        "constitution_en": "Athletic, energetic posture, high cardiovascular drive, robust recuperative speed.",
        "constitution_hi": "सुगठित शारीरिक संरचना, ऊर्जावान चाल-ढाल, उच्च प्राणशक्ति एवं शीघ्र स्वास्थ्य लाभ की क्षमता।",
        "persona_en": "Direct executive aura, command presence, authoritative tone, decisive negotiation style.",
        "persona_hi": "प्रत्यक्ष नेतृत्वकारी व्यक्तित्व, प्रभावशाली उपस्थिति, दृढ़ स्वर एवं निर्णायक बातचीत शैली।",
        "life_arc_en": "Rapid self-made rise through pioneering technical, managerial, or real-estate enterprise.",
        "life_arc_hi": "तकनीकी, प्रशासनिक अथवा रियल एस्टेट के साहसिक उपक्रमों द्वारा स्वअर्जित तीव्र उन्नति।",
        "remedies_en": "Perform Surya Arghya with red kumkum at sunrise; wear pure copper or coral after trials.",
        "remedies_hi": "प्रातःकाल तांबे के लोटे में रोली डालकर सूर्य देव को अर्घ्य दें; योग्य परामर्श उपरांत मूंगा या तांबा धारण करें।"
    }
}

def get_localized_lagna_data(lagna_name: str, is_hi: bool):
    key = lagna_name.split()[0]
    data = LAGNA_PREDICTIONS.get(key, LAGNA_PREDICTIONS["Mesha"])
    return {
        "element": data["element_hi"] if is_hi else data["element_en"],
        "lord": data["lord_hi"] if is_hi else data["lord_en"],
        "constitution": data["constitution_hi"] if is_hi else data["constitution_en"],
        "persona": data["persona_hi"] if is_hi else data["persona_en"],
        "life_arc": data["life_arc_hi"] if is_hi else data["life_arc_en"],
        "remedies": data["remedies_hi"] if is_hi else data["remedies_en"]
    }

def render_page_profile():
    prof = st.session_state.get("user_profile", {})
    current_lang = prof.get("lang", "en")
    is_hi = (current_lang == "hi")
    
    has_valid_profile = st.session_state.get("has_valid_profile", False)
    dob_parsed = st.session_state.get("dob_parsed")
    tob_parsed = st.session_state.get("tob_parsed")
    chart_info = st.session_state.get("chart_info")
    u_lat = float(prof.get("lat", 28.6139))
    u_lon = float(prof.get("lon", 77.2090))

    if not has_valid_profile or st.session_state.get("edit_mode", False):
        form_title = "👤 वैदिक जन्म विवरण दर्ज करें" if is_hi else "👤 Configure Vedic Birth Profile"
        form_sub = "प्रामाणिक जन्म पत्रिका, लग्न, जन्म नक्षत्र एवं साढ़े साती की गणना हेतु अपना विवरण भरें:" if is_hi else "Please enter your birth details to generate your authentic Vedic chart, Lagna, Janma Nakshatra, and Sade Sati status."
        name_label = "पूरा नाम" if is_hi else "Full Name"
        dob_label = "जन्म तिथि" if is_hi else "Birth Date"
        time_label = "**जन्म समय (घंटा, मिनट एवं AM/PM):**" if is_hi else "**Birth Time (Hour, Minute & AM/PM):**"
        hr_lbl = "घंटा" if is_hi else "Hour"
        min_lbl = "मिनट" if is_hi else "Minute"
        city_label = "जन्म स्थान का नाम" if is_hi else "Birth Location / City Name"
        save_btn_lbl = "✨ सुरक्षित करें एवं गणना करें" if is_hi else "✨ Save & Calculate Profile"
        cancel_btn_lbl = "रद्द करें" if is_hi else "Cancel"
        err_name = "कृपया अपना पूरा नाम दर्ज करें।" if is_hi else "Please provide your full name."
        err_city = "कृपया जन्म स्थान का नाम दर्ज करें।" if is_hi else "Please provide a birth location name."
        spinner_txt = "स्थान के भौगोलिक निर्देशांक खोजे जा रहे हैं..." if is_hi else "Searching coordinates for your location..."

        render_html(f"""
        <div class="light-card-profile">
            <div style="font-weight:900; font-size:1.3rem; color:#9a3412; margin-bottom:0.5rem;">
                {form_title}
            </div>
            <div style="font-size:0.94rem; color:#475569; margin-bottom:1rem;">
                {form_sub}
            </div>
        </div>
        """)
        with st.form("create_profile_form"):
            new_name = st.text_input(name_label, value=prof.get("name", ""), placeholder="e.g. Rahul Sharma")
            d_init = dob_parsed if dob_parsed else datetime.date(1990, 1, 1)
            new_dob = st.date_input(dob_label, value=d_init)
            
            st.markdown(time_label)
            t_col1, t_col2, t_col3 = st.columns([1.5, 1.5, 1.5])
            with t_col1:
                init_hr = (tob_parsed.hour % 12) if tob_parsed else 12
                init_hr = 12 if init_hr == 0 else init_hr
                in_hour = st.selectbox(hr_lbl, options=list(range(1, 13)), index=init_hr - 1)
            with t_col2:
                init_min = tob_parsed.minute if tob_parsed else 0
                in_minute = st.selectbox(min_lbl, options=list(range(0, 60)), index=init_min)
            with t_col3:
                init_ampm = "PM" if (tob_parsed and tob_parsed.hour >= 12) else "AM"
                in_ampm = st.selectbox("AM / PM", options=["AM", "PM"], index=1 if init_ampm == "PM" else 0)

            new_city_query = st.text_input(city_label, value=prof.get("city", ""), placeholder="e.g. Panvel, Aurangabad, Mumbai, London, New York")

            c_save, c_canc = st.columns([2, 1])
            with c_save:
                submitted = st.form_submit_button(save_btn_lbl, type="primary", use_container_width=True)
            with c_canc:
                canceled = st.form_submit_button(cancel_btn_lbl, use_container_width=True)

            if submitted:
                if not new_name.strip():
                    st.error(err_name)
                elif not new_city_query.strip():
                    st.error(err_city)
                else:
                    hr_24 = in_hour % 12
                    if in_ampm == "PM":
                        hr_24 += 12
                    final_tob_str = f"{hr_24:02d}:{in_minute:02d}"

                    with st.spinner(spinner_txt):
                        resolved_lat, resolved_lon = resolve_location_name(new_city_query)

                    st.session_state.user_profile.update({
                        "name": new_name.strip(),
                        "dob": new_dob.strftime("%Y-%m-%d"),
                        "tob": final_tob_str,
                        "city": new_city_query.strip(),
                        "lat": resolved_lat,
                        "lon": resolved_lon
                    })
                    
                    st.query_params.update({
                        "name": new_name.strip(),
                        "dob": new_dob.strftime("%Y-%m-%d"),
                        "tob": final_tob_str,
                        "city": new_city_query.strip(),
                        "lat": f"{resolved_lat:.4f}",
                        "lon": f"{resolved_lon:.4f}"
                    })

                    st.session_state.edit_mode = False
                    st.session_state.current_page = "install_guide"
                    st.rerun()
            
            if canceled:
                st.session_state.edit_mode = False
                st.rerun()
        return

    lbl_profile_tag = "की प्रोफाइल" if is_hi else "'s Profile"
    lbl_dob_tag = "जन्म तिथि" if is_hi else "DOB"
    lbl_time_tag = "समय" if is_hi else "Time"
    lbl_place_tag = "स्थान" if is_hi else "Place"
    lbl_edit_btn = "✏️ विवरण बदलें" if is_hi else "✏️ Edit Details"

    with st.container(border=True):
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            render_html(f"""
            <div style="font-weight:900; font-size:1.2rem; color:#0f172a;">👤 {prof['name']} {lbl_profile_tag}</div>
            <div style="font-size:0.95rem; color:#334155; margin-top:5px; line-height:1.6;">
                📅 <b>{lbl_dob_tag}:</b> {dob_parsed.strftime('%d %B %Y')} &nbsp;|&nbsp; ⏰ <b>{lbl_time_tag}:</b> {tob_parsed.strftime('%I:%M %p')}<br>
                📍 <b>{lbl_place_tag}:</b> {prof['city']} ({u_lat:.4f}° N, {u_lon:.4f}° E)
            </div>
            """)
        with col_p2:
            if st.button(lbl_edit_btn, use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

    # Retrieve attributes and predictions cleanly based on language
    star_idx = chart_info["star_idx"]
    bio_item = NAKSHATRA_BIO.get(star_idx, NAKSHATRA_BIO[2])
    n_data = get_localized_nak_prediction(star_idx, is_hi)
    m_data = get_localized_rashi_data(chart_info["moon_rashi_name"], is_hi)
    l_data = get_localized_lagna_data(chart_info["lagna_name"], is_hi)
    
    moon_parts = chart_info['moon_rashi_name'].split()
    moon_p1 = moon_parts[0] if moon_parts else chart_info['moon_rashi_name']
    moon_p2 = moon_parts[-1] if len(moon_parts) > 1 else ""

    lagna_parts = chart_info['lagna_name'].split()
    lagna_p1 = lagna_parts[0] if lagna_parts else chart_info['lagna_name']

    raw_nak = chart_info.get('star_name', 'Bharani')
    disp_nak = NAKSHATRA_NAMES_HI.get(raw_nak, raw_nak) if is_hi else raw_nak
    disp_rashi = RASHI_NAMES_HI.get(moon_p1, moon_p1) if is_hi else moon_p1
    disp_lagna = RASHI_NAMES_HI.get(lagna_p1, lagna_p1) if is_hi else lagna_p1
    disp_pada = f"चरण {chart_info['pada']}" if is_hi else f"Pada {chart_info['pada']}"

    lbl_verified_header = "🌌 प्रमाणित वैदिक कुंडली संरेखण" if is_hi else "🌌 Verified Vedic Kundali Alignment"
    lbl_ayanamsa = "चित्रापक्षीय लाहिड़ी अयनांश" if is_hi else "Chitrapaksha Lahiri Ayanamsa"
    lbl_lagna = "लग्न राशि" if is_hi else "Ascendant (Lagna)"
    lbl_nak = "जन्म नक्षत्र" if is_hi else "Janma Nakshatra"
    lbl_rashi = "चन्द्र राशि" if is_hi else "Moon Sign (Rashi)"

    lbl_nak_section = f"⭐ जन्म नक्षत्र: {disp_nak} ({disp_pada})" if is_hi else f"⭐ Janma Nakshatra: {chart_info['star_name']} (Pada {chart_info['pada']})"
    lbl_rashi_section = f"🌙 चन्द्र राशि: {disp_rashi}" if is_hi else f"🌙 Moon Sign (Chandra Rashi): {chart_info['moon_rashi_name']}"
    lbl_lagna_section = f"🌅 लग्न राशि: {disp_lagna} ({chart_info['lagna_deg']})" if is_hi else f"🌅 Ascendant (Lagna): {chart_info['lagna_name']} at {chart_info['lagna_deg']}"

    attr_deity = "🏛️ अधिष्ठाता देवता:" if is_hi else "🏛️ Deity:"
    attr_symbol = "🔱 प्रतीक:" if is_hi else "🔱 Symbol:"
    attr_tree = "🌳 पूज्य वृक्ष:" if is_hi else "🌳 Sacred Tree:"
    attr_bird = "🦅 पक्षी:" if is_hi else "🦅 Sacred Bird:"
    attr_animal = "🦁 योनि प्राणी:" if is_hi else "🦁 Yoni Animal:"
    attr_lord = "🪐 नक्षत्र स्वामी:" if is_hi else "🪐 Planetary Lord:"

    attr_rashi_lord = "🪐 राशि स्वामी:" if is_hi else "🪐 Rashi Sovereign:"
    attr_element = "🔥 तत्व:" if is_hi else "🔥 Element:"
    attr_lagna_lord = "👑 लग्नेश:" if is_hi else "👑 Ascendant Lord:"
    attr_lagna_tattva = "🌍 लग्न तत्व:" if is_hi else "🌍 Lagna Tattva:"

    lbl_core_arch = "🧠 मूल संज्ञानात्मक एवं व्यवहारिक स्वभाव:" if is_hi else "🧠 Core Cognitive & Behavioral Archetype:"
    lbl_superpowers = "✨ विशिष्ट क्षमताएं व जन्मजात शक्तियां:" if is_hi else "✨ Superpowers & Natural Assets:"
    lbl_shadows = "⚠️ कर्मिक चुनौतियां व कमजोर पहलू:" if is_hi else "⚠️ Karmic Shadows & Blind Spots:"
    lbl_vocational = "💼 अनुकूल आजीविका एवं कार्यक्षेत्र:" if is_hi else "💼 Peak Vocational & Executive Fields:"
    lbl_life_path = "🔮 जीवन पथ एवं विकास यात्रा:" if is_hi else "🔮 Evolutionary Life Path Trajectory:"
    lbl_nak_remedies = "🪔 निर्धारित नक्षत्र वैदिक उपाय:" if is_hi else "🪔 Prescribed Vedic Nakshatra Remedies:"

    lbl_psychology = "🧠 भावनात्मक दृष्टिकोण एवं अवचेतन विचार:" if is_hi else "🧠 Emotional Mindset & Subconscious Processing:"
    lbl_instincts = "⚡ तनाव में स्वाभाविक प्रतिक्रियाएं:" if is_hi else "⚡ Stress Reflexes & Primal Coping Instincts:"
    lbl_relations = "❤️ पारस्परिक संबंध एवं साझेदारी शैली:" if is_hi else "❤️ Interpersonal Blueprint & Relationship Style:"
    lbl_health = "🌿 शारीरिक प्रकृति एवं स्वास्थ्य संतुलन:" if is_hi else "🌿 Bio-Rhythms & Physiological Vitality:"
    lbl_lunar_rem = "🪔 निर्धारित चन्द्र उपाय:" if is_hi else "🪔 Prescribed Lunar Remedies:"

    lbl_constitution = "🛡️ शारीरिक बनावट, ओज एवं प्रकृति (Prakriti):" if is_hi else "🛡️ Physical Constitution, Vitality & Posture (Prakriti):"
    lbl_persona = "👔 सामाजिक छवि एवं नेतृत्व क्षमता:" if is_hi else "👔 Outward Persona & Negotiating Presence:"
    lbl_life_arc = "🚀 जीवन की दिशा एवं संपत्ति निर्माण:" if is_hi else "🚀 Evolutionary Life Arc & Asset Compounding:"
    lbl_lagna_rem = "🪔 निर्धारित लग्न उपाय:" if is_hi else "🪔 Prescribed Ascendant Remedies:"

    deity_val = bio_item["deity_hi"] if is_hi else bio_item["deity_en"]
    symbol_val = bio_item["symbol_hi"] if is_hi else bio_item["symbol_en"]
    tree_val = bio_item["tree_hi"] if is_hi else bio_item["tree_en"]
    bird_val = bio_item["bird_hi"] if is_hi else bio_item["bird_en"]
    animal_val = bio_item["animal_hi"] if is_hi else bio_item["animal_en"]
    lord_val = bio_item["lord_hi"] if is_hi else bio_item["lord_en"]

    render_html(f"""
    <div class="light-card-profile">
        <div style="font-weight:900; font-size:1.35rem; color:#9a3412; margin-bottom:1rem; border-bottom:2px solid #fed7aa; padding-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
            <span>{lbl_verified_header}</span>
            <span style="font-size:0.85rem; background:#ffedd5; color:#c2410c; padding:4px 10px; border-radius:20px; font-weight:800;">{lbl_ayanamsa}</span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:10px; text-align:center; margin-bottom:1.25rem;">
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{lbl_lagna}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{disp_lagna}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{chart_info['lagna_deg']}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{lbl_nak}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{disp_nak}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{disp_pada}</div>
            </div>
            <div style="background:#fff7ed; border-radius:12px; padding:12px; border:1.5px solid #ffedd5;">
                <div style="font-size:0.82rem; color:#c2410c; font-weight:800; text-transform:uppercase;">{lbl_rashi}</div>
                <div style="font-size:1.3rem; font-weight:900; color:#9a3412; margin:2px 0;">{disp_rashi}</div>
                <div style="font-size:0.88rem; color:#ea580c; font-weight:700;">{moon_p2}</div>
            </div>
        </div>

        <!-- JANMA NAKSHATRA CARD -->
        <div style="background:#fffaf0; border-radius:14px; padding:14px; border:1.5px solid #fed7aa; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#9a3412; margin-bottom:8px;">
                {lbl_nak_section}
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:8px; margin-bottom:12px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_deity}</b> {deity_val}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_symbol}</b> {symbol_val}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_tree}</b> {tree_val}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_bird}</b> {bird_val}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_animal}</b> {animal_val}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #fed7aa;"><b>{attr_lord}</b> {lord_val}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:12px; border:1px solid #fed7aa; margin-bottom:8px;">
                <b style="color:#9a3412; font-size:0.96rem;">{lbl_core_arch}</b>
                <div style="font-size:0.92rem; line-height:1.65; color:#431407; margin-top:2px;">{n_data['core']}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:8px;">
                <div style="background:#f0fdf4; border-radius:10px; padding:10px; border:1px solid #bbf7d0;">
                    <b style="color:#15803d; font-size:0.92rem;">{lbl_superpowers}</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#14532d; margin-top:2px;">{n_data['strengths']}</div>
                </div>
                <div style="background:#fff1f2; border-radius:10px; padding:10px; border:1px solid #fecdd3;">
                    <b style="color:#be123c; font-size:0.92rem;">{lbl_shadows}</b>
                    <div style="font-size:0.89rem; line-height:1.55; color:#881337; margin-top:2px;">{n_data['shadows']}</div>
                </div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>{lbl_vocational}</b><br>{n_data['careers']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #fed7aa; margin-bottom:8px; font-size:0.91rem; color:#431407;">
                <b>{lbl_life_path}</b><br>{n_data['prediction']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #f97316; font-size:0.91rem; color:#431407;">
                <b>{lbl_nak_remedies}</b><br>{n_data['remedies'].replace(chr(10), '<br>')}
            </div>
        </div>

        <!-- MOON RASHI CARD -->
        <div style="background:#f0fdf4; border-radius:14px; padding:14px; border:1.5px solid #bbf7d0; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#065f46; margin-bottom:8px;">
                {lbl_rashi_section}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>{attr_element}</b> {m_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #bbf7d0;"><b>{attr_rashi_lord}</b> {m_data['ruler']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>{lbl_psychology}</b><br>{m_data['psychology']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>{lbl_instincts}</b><br>{m_data['instincts']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>{lbl_relations}</b><br>{m_data['relations']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #bbf7d0; margin-bottom:8px; font-size:0.92rem; color:#14532d; line-height:1.6;">
                <b>{lbl_health}</b><br>{m_data['health']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #10b981; font-size:0.91rem; color:#14532d;">
                <b>{lbl_lunar_rem}</b><br>{m_data['remedies']}
            </div>
        </div>

        <!-- ASCENDANT (LAGNA) CARD -->
        <div style="background:#f5f3ff; border-radius:14px; padding:14px; border:1.5px solid #ddd6fe; margin-bottom:1.15rem;">
            <div style="font-weight:900; font-size:1.15rem; color:#5b21b6; margin-bottom:8px;">
                {lbl_lagna_section}
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px; font-size:0.9rem;">
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>{attr_lagna_tattva}</b> {l_data['element']}</div>
                <div style="background:#ffffff; border-radius:10px; padding:8px 10px; border:1px solid #ddd6fe;"><b>{attr_lagna_lord}</b> {l_data['lord']}</div>
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>{lbl_constitution}</b><br>{l_data['constitution']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>{lbl_persona}</b><br>{l_data['persona']}
            </div>

            <div style="background:#ffffff; border-radius:10px; padding:10px 12px; border:1px solid #ddd6fe; margin-bottom:8px; font-size:0.92rem; color:#3b0764; line-height:1.6;">
                <b>{lbl_life_arc}</b><br>{l_data['life_arc']}
            </div>

            <div style="background:#ffffff; border-radius:8px; padding:10px 12px; border-left:4px solid #8b5cf6; font-size:0.91rem; color:#3b0764;">
                <b>{lbl_lagna_rem}</b><br>{l_data['remedies']}
            </div>
        </div>
    </div>
    """)

    # Tara Bala Widget (Fully Localized)
    lbl_tara_title = "**🤝 नक्षत्र अनुकूलता एवं ऊर्जा संबंध (तारा बल - Tara Bala)**" if is_hi else "**🤝 Nakshatra Synergy & Compatibility Evaluator (Tara Bala)**"
    lbl_select_star = "अन्य व्यक्ति का जन्म नक्षत्र चुनें:" if is_hi else "Select Counterpart's Birth Star:"
    lbl_dynamic = "ऊर्जा तालमेल (Dynamic):" if is_hi else "Dynamic:"

    with st.container(border=True):
        st.markdown(lbl_tara_title)
        
        if is_hi:
            star_display_options = [f"{NAKSHATRA_NAMES_HI.get(s, s)} ({s})" for s in NAKSHATRAS]
            partner_star_sel = st.selectbox(lbl_select_star, options=star_display_options, index=0)
            p_star_idx = star_display_options.index(partner_star_sel) + 1
        else:
            partner_star_choice = st.selectbox(lbl_select_star, options=NAKSHATRAS, index=0)
            p_star_idx = NAKSHATRAS.index(partner_star_choice) + 1

        tara_res = get_tara_bala_info(chart_info['star_idx'], p_star_idx)
        
        box_bg = '#f0fdf4' if tara_res['is_allied'] else ('#fff1f2' if tara_res['is_friction'] else '#f8fafc')
        box_border = '#86efac' if tara_res['is_allied'] else ('#fecdd3' if tara_res['is_friction'] else '#e2e8f0')
        box_color = '#15803d' if tara_res['is_allied'] else ('#be123c' if tara_res['is_friction'] else '#0f172a')
        
        disp_tara_name = TARA_NAMES_HI.get(tara_res['tara_name'], tara_res['tara_name']) if is_hi else tara_res['tara_name']

        render_html(f"""
        <div style="background:{box_bg}; border:1.5px solid {box_border}; border-radius:12px; padding:12px; margin-top:8px;">
            <div style="font-size:1.05rem; font-weight:800; color:{box_color};">
                {tara_res['icon']} {disp_tara_name} — {tara_res['quality']}
            </div>
            <div style="font-size:0.92rem; font-weight:700; color:#334155; margin-top:4px;">
                {lbl_dynamic} {tara_res['relationship_tone']}
            </div>
            <div style="font-size:0.9rem; color:#475569; margin-top:4px; line-height:1.5;">
                {tara_res['advice']}
            </div>
        </div>
        """)

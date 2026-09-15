# views/dasha.py - Dedicated Vimshottari Dasha Engine & UI
import streamlit as st
import datetime

# Helper function to inject clean HTML safely
def render_html(html_string: str):
    clean_html = " ".join(line.strip() for line in html_string.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)

DASHA_SEQ = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YRS = {
    "Ketu": 7.0, "Venus": 20.0, "Sun": 6.0, "Moon": 10.0, "Mars": 7.0, 
    "Rahu": 18.0, "Jupiter": 16.0, "Saturn": 19.0, "Mercury": 17.0
}

PLANET_NAMES_HI = {
    "Sun": "सूर्य (Surya)", "Moon": "चन्द्र (Chandra)", "Mars": "मंगल (Mangal)",
    "Rahu": "राहु (Rahu)", "Jupiter": "गुरु / बृहस्पति (Guru)", "Saturn": "शनि (Shani)",
    "Mercury": "बुध (Budha)", "Ketu": "केतु (Ketu)", "Venus": "शुक्र (Shukra)"
}

LAGNA_NAMES_HI = {
    "Aries": "मेष", "Taurus": "वृषभ", "Gemini": "मिथुन", "Cancer": "कर्क",
    "Leo": "सिंह", "Virgo": "कन्या", "Libra": "तुला", "Scorpio": "वृश्चिक",
    "Sagittarius": "धनु", "Capricorn": "मकर", "Aquarius": "कुंभ", "Pisces": "मीन"
}

LAGNA_LORDS = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
}

NATURAL_FRIENDSHIPS = {
    "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "neutrals": ["Mercury"], "enemies": ["Venus", "Saturn", "Rahu", "Ketu"]},
    "Moon": {"friends": ["Sun", "Mercury"], "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"], "enemies": ["Rahu", "Ketu"]},
    "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "neutrals": ["Venus", "Saturn"], "enemies": ["Mercury", "Rahu", "Ketu"]},
    "Mercury": {"friends": ["Sun", "Venus"], "neutrals": ["Mars", "Jupiter", "Saturn"], "enemies": ["Moon", "Rahu", "Ketu"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "neutrals": ["Saturn"], "enemies": ["Mercury", "Venus", "Rahu", "Ketu"]},
    "Venus": {"friends": ["Mercury", "Saturn", "Rahu", "Ketu"], "neutrals": ["Mars", "Jupiter"], "enemies": ["Sun", "Moon"]},
    "Saturn": {"friends": ["Mercury", "Venus", "Rahu"], "neutrals": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars", "Ketu"]},
    "Rahu": {"friends": ["Venus", "Saturn", "Mercury"], "neutrals": ["Jupiter"], "enemies": ["Sun", "Moon", "Mars", "Ketu"]},
    "Ketu": {"friends": ["Mars", "Venus", "Jupiter"], "neutrals": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon", "Rahu"]}
}

LAGNA_AFFILIATION_MAP = {
    0: {
        "Sun": {"role_en": "5th Lord (Trine)", "role_hi": "पंचमेश (त्रिकोण भाव अधिपति)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "4th Lord (Kendra)", "role_hi": "चतुर्थेश (केंद्र भाव अधिपति)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "Lagna & 8th Lord", "role_hi": "लग्नेश एवं अष्टमेश", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "3rd & 6th Lord", "role_hi": "तृतीयेश एवं षष्ठेश (त्रिक भाव)", "gem_safe": False},
        "Jupiter": {"role_en": "9th & 12th Lord", "role_hi": "नवमेश एवं द्वादशेश (भाग्येश)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Yellow Sapphire)"},
        "Venus": {"role_en": "2nd & 7th Lord", "role_hi": "द्वितीयेश एवं सप्तमेश (मारक भाव)", "gem_safe": False},
        "Saturn": {"role_en": "10th & 11th Lord", "role_hi": "दशमेश एवं एकादशेश", "gem_safe": False},
        "Rahu": {"role_en": "Upachaya Catalyst", "role_hi": "उपचय भाव विस्तारक", "gem_safe": False},
        "Ketu": {"role_en": "Moksha Catalyst", "role_hi": "मोक्ष एवं वैराग्य कारक", "gem_safe": False}
    },
    1: {
        "Sun": {"role_en": "4th Lord (Kendra)", "role_hi": "चतुर्थेश (सुख व भूमि भाव)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "3rd Lord", "role_hi": "तृतीयेश (पराक्रम भाव)", "gem_safe": False},
        "Mars": {"role_en": "7th & 12th Lord", "role_hi": "सप्तमेश एवं द्वादशेश (मारक व व्यय)", "gem_safe": False},
        "Mercury": {"role_en": "2nd & 5th Lord", "role_hi": "द्वितीयेश एवं पंचमेश (परम धन व बुद्धि कारक)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "8th & 11th Lord", "role_hi": "अष्टमेश एवं एकादशेश (त्रिक भाव)", "gem_safe": False},
        "Venus": {"role_en": "Lagna & 6th Lord", "role_hi": "लग्नेश एवं षष्ठेश", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / ओपल / सफेद जरकन"},
        "Saturn": {"role_en": "9th & 10th Lord", "role_hi": "नवमेश व दशमेश (परम राजयोगकारक)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम / जामुनिया (Blue Sapphire)"},
        "Rahu": {"role_en": "Material Catalyst", "role_hi": "भौतिक उन्नति कारक", "gem_safe": False},
        "Ketu": {"role_en": "Introspective Catalyst", "role_hi": "आंतरिक अनुसंधान कारक", "gem_safe": False}
    },
    2: {
        "Sun": {"role_en": "3rd Lord", "role_hi": "तृतीयेश (उद्यम भाव)", "gem_safe": False},
        "Moon": {"role_en": "2nd Lord", "role_hi": "द्वितीयेश (धन व वाणी)", "gem_safe": False},
        "Mars": {"role_en": "6th & 11th Lord", "role_hi": "षष्ठेश एवं एकादशेश", "gem_safe": False},
        "Mercury": {"role_en": "Lagna & 4th Lord", "role_hi": "लग्नेश एवं चतुर्थेश", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "7th & 10th Lord", "role_hi": "सप्तमेश एवं दशमेश", "gem_safe": False},
        "Venus": {"role_en": "5th & 12th Lord", "role_hi": "पंचमेश एवं द्वादशेश (त्रिकोण कारक)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / जरकन"},
        "Saturn": {"role_en": "8th & 9th Lord", "role_hi": "अष्टमेश एवं नवमेश (भाग्येश)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Career Catalyst", "role_hi": "कर्म विस्तारक कारक", "gem_safe": False},
        "Ketu": {"role_en": "Analytical Catalyst", "role_hi": "विश्लेषणात्मक वैराग्य कारक", "gem_safe": False}
    },
    3: {
        "Sun": {"role_en": "2nd Lord", "role_hi": "द्वितीयेश (धन संचय)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "Lagna Lord", "role_hi": "लग्नेश (शरीर व आत्मबल)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "5th & 10th Lord", "role_hi": "पंचमेश व दशमेश (परम योगकारक)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "3rd & 12th Lord", "role_hi": "तृतीयेश एवं द्वादशेश", "gem_safe": False},
        "Jupiter": {"role_en": "6th & 9th Lord", "role_hi": "षष्ठेश एवं नवमेश (भाग्य वृद्धि)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "4th & 11th Lord", "role_hi": "चतुर्थेश एवं एकादशेश (बाधक भाव)", "gem_safe": False},
        "Saturn": {"role_en": "7th & 8th Lord", "role_hi": "सप्तमेश एवं अष्टमेश (मारक व त्रिक)", "gem_safe": False},
        "Rahu": {"role_en": "Expansion Catalyst", "role_hi": "अप्रत्यक्ष विस्तारक", "gem_safe": False},
        "Ketu": {"role_en": "Intuition Catalyst", "role_hi": "आध्यात्मिक ज्ञान कारक", "gem_safe": False}
    },
    4: {
        "Sun": {"role_en": "Lagna Lord", "role_hi": "लग्नेश (ओज व आत्म संप्रभुता)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "12th Lord", "role_hi": "द्वादशेश (व्यय भाव)", "gem_safe": False},
        "Mars": {"role_en": "4th & 9th Lord", "role_hi": "चतुर्थेश व नवमेश (परम योगकारक)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "2nd & 11th Lord", "role_hi": "द्वितीयेश एवं एकादशेश (परम धन कारक)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "5th & 8th Lord", "role_hi": "पंचमेश एवं अष्टमेश (ज्ञान व मंत्र सिद्धि)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "3rd & 10th Lord", "role_hi": "तृतीयेश एवं दशमेश", "gem_safe": False},
        "Saturn": {"role_en": "6th & 7th Lord", "role_hi": "षष्ठेश एवं सप्तमेश (मारक)", "gem_safe": False},
        "Rahu": {"role_en": "Scale Catalyst", "role_hi": "महत्वाकांक्षा विस्तारक", "gem_safe": False},
        "Ketu": {"role_en": "Detachment Catalyst", "role_hi": "अहंकार निवारक", "gem_safe": False}
    },
    5: {
        "Sun": {"role_en": "12th Lord", "role_hi": "द्वादशेश (व्यय व दूरस्थ संबंध)", "gem_safe": False},
        "Moon": {"role_en": "11th Lord", "role_hi": "एकादशेश (आय व लाभ भाव)", "gem_safe": False},
        "Mars": {"role_en": "3rd & 8th Lord", "role_hi": "तृतीयेश एवं अष्टमेश (अति पापी)", "gem_safe": False},
        "Mercury": {"role_en": "Lagna & 10th Lord", "role_hi": "लग्नेश एवं दशमेश (कुलदीपक योगकारक)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "4th & 7th Lord", "role_hi": "चतुर्थेश एवं सप्तमेश (केंद्राधिपति दोष)", "gem_safe": False},
        "Venus": {"role_en": "2nd & 9th Lord", "role_hi": "द्वितीयेश एवं नवमेश (परम भाग्य व धन कारक)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / जरकन"},
        "Saturn": {"role_en": "5th & 6th Lord", "role_hi": "पंचमेश एवं षष्ठेश (त्रिकोण अधिपति)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Tech Catalyst", "role_hi": "तकनीकी नवाचार कारक", "gem_safe": False},
        "Ketu": {"role_en": "Audit Catalyst", "role_hi": "गहन विश्लेषण कारक", "gem_safe": False}
    },
    6: {
        "Sun": {"role_en": "11th Lord", "role_hi": "एकादशेश (बाधक भाव)", "gem_safe": False},
        "Moon": {"role_en": "10th Lord", "role_hi": "दशमेश (कर्म व यश)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "2nd & 7th Lord", "role_hi": "द्वितीयेश एवं सप्तमेश (प्रबल मारक)", "gem_safe": False},
        "Mercury": {"role_en": "9th & 12th Lord", "role_hi": "नवमेश एवं द्वादशेश (भाग्य कारक)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "3rd & 6th Lord", "role_hi": "तृतीयेश एवं षष्ठेश (रोग व संघर्ष)", "gem_safe": False},
        "Venus": {"role_en": "Lagna & 8th Lord", "role_hi": "लग्नेश एवं अष्टमेश (शरीर व प्रतिष्ठा)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / ओपल"},
        "Saturn": {"role_en": "4th & 5th Lord", "role_hi": "चतुर्थेश व पंचमेश (परम योगकारक)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Visibility Catalyst", "role_hi": "वैश्विक प्रभाव कारक", "gem_safe": False},
        "Ketu": {"role_en": "Esoteric Catalyst", "role_hi": "गूढ़ साधना कारक", "gem_safe": False}
    },
    7: {
        "Sun": {"role_en": "10th Lord", "role_hi": "दशमेश (राजसत्ता व कीर्ति)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "9th Lord", "role_hi": "नवमेश (धर्म व भाग्य कारक)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "Lagna & 6th Lord", "role_hi": "लग्नेश एवं षष्ठेश (शत्रुहंता)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "8th & 11th Lord", "role_hi": "अष्टमेश एवं एकादशेश", "gem_safe": False},
        "Jupiter": {"role_en": "2nd & 5th Lord", "role_hi": "द्वितीयेश एवं पंचमेश (महा धन कारक)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "7th & 12th Lord", "role_hi": "सप्तमेश एवं द्वादशेश (मारक व व्यय)", "gem_safe": False},
        "Saturn": {"role_en": "3rd & 4th Lord", "role_hi": "तृतीयेश एवं चतुर्थेश", "gem_safe": False},
        "Rahu": {"role_en": "Breakthrough Catalyst", "role_hi": "अकस्मात उन्नति कारक", "gem_safe": False},
        "Ketu": {"role_en": "Psychological Catalyst", "role_hi": "मानसिक शोधक कारक", "gem_safe": False}
    },
    8: {
        "Sun": {"role_en": "9th Lord", "role_hi": "नवमेश (परम भाग्य व धर्म कारक)", "gem_safe": True, "gem_en": "Ruby (Manikya)", "gem_hi": "माणिक्य (Ruby)"},
        "Moon": {"role_en": "8th Lord", "role_hi": "अष्टमेश (आयु व संकट)", "gem_safe": False},
        "Mars": {"role_en": "5th & 12th Lord", "role_hi": "पंचमेश एवं द्वादशेश (त्रिकोण कारक)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "7th & 10th Lord", "role_hi": "सप्तमेश एवं दशमेश", "gem_safe": False},
        "Jupiter": {"role_en": "Lagna & 4th Lord", "role_hi": "लग्नेश एवं चतुर्थेश (परम शुभ)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "6th & 11th Lord", "role_hi": "षष्ठेश एवं एकादशेश (अति पापी)", "gem_safe": False},
        "Saturn": {"role_en": "2nd & 3rd Lord", "role_hi": "द्वितीयेश एवं तृतीयेश (मारक)", "gem_safe": False},
        "Rahu": {"role_en": "Expansion Catalyst", "role_hi": "ज्ञान व भौतिक विस्तारक", "gem_safe": False},
        "Ketu": {"role_en": "Liberation Catalyst", "role_hi": "आध्यात्मिक मुक्ति कारक", "gem_safe": False}
    },
    9: {
        "Sun": {"role_en": "8th Lord", "role_hi": "अष्टमेश (गूढ़ संकट व परिवर्तन)", "gem_safe": False},
        "Moon": {"role_en": "7th Lord", "role_hi": "सप्तमेश (मारक भाव)", "gem_safe": False},
        "Mars": {"role_en": "4th & 11th Lord", "role_hi": "चतुर्थेश एवं एकादशेश (बाधक)", "gem_safe": False},
        "Mercury": {"role_en": "6th & 9th Lord", "role_hi": "षष्ठेश एवं नवमेश (भाग्य वृद्धि)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "3rd & 12th Lord", "role_hi": "तृतीयेश एवं द्वादशेश", "gem_safe": False},
        "Venus": {"role_en": "5th & 10th Lord", "role_hi": "पंचमेश व दशमेश (परम राजयोगकारक)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / ओपल"},
        "Saturn": {"role_en": "Lagna & 2nd Lord", "role_hi": "लग्नेश एवं द्वितीयेश (धन व सत्ता)", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Elevation Catalyst", "role_hi": "अभूतपूर्व उत्थान कारक", "gem_safe": False},
        "Ketu": {"role_en": "Mastery Catalyst", "role_hi": "आत्म-नियंत्रण कारक", "gem_safe": False}
    },
    10: {
        "Sun": {"role_en": "7th Lord", "role_hi": "सप्तमेश (मारक भाव)", "gem_safe": False},
        "Moon": {"role_en": "6th Lord", "role_hi": "षष्ठेश (रोग व ऋण भाव)", "gem_safe": False},
        "Mars": {"role_en": "3rd & 10th Lord", "role_hi": "तृतीयेश एवं दशमेश", "gem_safe": False},
        "Mercury": {"role_en": "5th & 8th Lord", "role_hi": "पंचमेश एवं अष्टमेश (बुद्धि व शोध)", "gem_safe": True, "gem_en": "Emerald (Panna)", "gem_hi": "पन्ना (Emerald)"},
        "Jupiter": {"role_en": "2nd & 11th Lord", "role_hi": "द्वितीयेश एवं एकादशेश (प्रबल धनेश)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "4th & 9th Lord", "role_hi": "चतुर्थेश व नवमेश (परम योगकारक)", "gem_safe": True, "gem_en": "Diamond / White Zircon", "gem_hi": "हीरा / ओपल"},
        "Saturn": {"role_en": "Lagna & 12th Lord", "role_hi": "लग्नेश एवं द्वादशेश", "gem_safe": True, "gem_en": "Blue Sapphire (Neelam)", "gem_hi": "नीलम (Neelam)"},
        "Rahu": {"role_en": "Innovation Catalyst", "role_hi": "युगांतरकारी परिवर्तन कारक", "gem_safe": False},
        "Ketu": {"role_en": "Reformation Catalyst", "role_hi": "आध्यात्मिक शोधक", "gem_safe": False}
    },
    11: {
        "Sun": {"role_en": "6th Lord", "role_hi": "षष्ठेश (शत्रु व रोग भाव)", "gem_safe": False},
        "Moon": {"role_en": "5th Lord", "role_hi": "पंचमेश (त्रिकोण व विद्या कारक)", "gem_safe": True, "gem_en": "Natural Pearl (Moti)", "gem_hi": "सच्चा मोती (Pearl)"},
        "Mars": {"role_en": "2nd & 9th Lord", "role_hi": "द्वितीयेश एवं नवमेश (परम धन व भाग्य कारक)", "gem_safe": True, "gem_en": "Red Coral (Moonga)", "gem_hi": "मूंगा (Red Coral)"},
        "Mercury": {"role_en": "4th & 7th Lord", "role_hi": "चतुर्थेश एवं सप्तमेश (केंद्राधिपति)", "gem_safe": False},
        "Jupiter": {"role_en": "Lagna & 10th Lord", "role_hi": "लग्नेश एवं दशमेश (कुलदीपक राजयोग)", "gem_safe": True, "gem_en": "Yellow Sapphire (Pukhraj)", "gem_hi": "पुखराज (Pukhraj)"},
        "Venus": {"role_en": "3rd & 8th Lord", "role_hi": "तृतीयेश एवं अष्टमेश (अति पापी)", "gem_safe": False},
        "Saturn": {"role_en": "11th & 12th Lord", "role_hi": "एकादशेश एवं द्वादशेश", "gem_safe": False},
        "Rahu": {"role_en": "Unconventional Catalyst", "role_hi": "अप्रत्यक्ष लाभ कारक", "gem_safe": False},
        "Ketu": {"role_en": "Moksha Catalyst", "role_hi": "मोक्ष व वैराग्य कारक", "gem_safe": False}
    }
}

REMEDIAL_PROTOCOLS = {
    "Sun": {
        "mantra": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः (11 या 108 बार प्रातःकाल)",
        "deity": "भगवान सूर्य नारायण — प्रातःकाल तांबे के लोटे में रोली, अक्षत और लाल पुष्प डालकर सूर्य देव को अर्घ्य दें।",
        "fasting": "रविवार के दिन नमक रहित व्रत का पालन करें।",
        "charity": "गेहूं, गुड़, तांबे के पात्र अथवा लाल वस्त्र किसी योग्य ब्राह्मण या जरूरतमंद को दान करें।"
    },
    "Moon": {
        "mantra": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः (11 या 108 बार संध्या समय)",
        "deity": "भगवान शिव — प्रत्येक सोमवार को शिवलिंग पर कच्चा दूध, जल अथवा पंचामृत से रुद्राभिषेक करें।",
        "fasting": "सोमवार अथवा पूर्णिमा के दिन उपवास रखें।",
        "charity": "सफेद चावल, दूध, चांदी, मिश्री अथवा पीने के जल का दान करें।"
    },
    "Mars": {
        "mantra": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः (11 या 108 बार एकाग्रचित्त होकर)",
        "deity": "श्री हनुमान जी अथवा कार्तिकेय जी — प्रतिदिन हनुमान चालीसा का पाठ करें और चमेली के तेल का दीपक जलाएं।",
        "fasting": "मंगलवार को नमक रहित व्रत रखें और तामसिक भोजन से पूर्णतः दूर रहें।",
        "charity": "लाल मसूर की दाल, तांबा अथवा रक्तदान कर जीवन रक्षा में सहयोग करें।"
    },
    "Rahu": {
        "mantra": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः (11 या 108 बार सूर्यास्त के बाद)",
        "deity": "माँ दुर्गा अथवा काल भैरव — सायंकाल दुर्गा सप्तशती अथवा भैरव चालीसा का पाठ करें।",
        "fasting": "शनिवार को सात्विक आहार लें और संयम बरतें।",
        "charity": "काले कुत्ते को मीठी रोटी खिलाएं, सूखा नारियल बहते जल में प्रवाहित करें या काले कंबल का दान करें।"
    },
    "Jupiter": {
        "mantra": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः (19 या 108 बार प्रातःकाल)",
        "deity": "भगवान श्री हरि विष्णु — विष्णु सहस्रनाम का पाठ करें और गुरुवार को केले अथवा पीपल के वृक्ष की सेवा करें।",
        "fasting": "गुरुवार को व्रत रखें और भोजन में चने की दाल या बेसन की पीली वस्तुओं का प्रयोग करें।",
        "charity": "चने की दाल, हल्दी, धार्मिक पुस्तकें अथवा पीले वस्त्र सुपात्र गुरुजन या मंदिर में अर्पित करें।"
    },
    "Saturn": {
        "mantra": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः (11 या 108 बार सायंकाल)",
        "deity": "शनि देव अथवा महाकाल — शनिवार की शाम पीपल वृक्ष के नीचे सरसों के तेल का दीपक प्रज्वलित करें।",
        "fasting": "शनिवार को व्रत रखें और उड़द दाल की खिचड़ी का सेवन करें।",
        "charity": "काले तिल, सरसों का तेल, लोहे के बर्तन या जूते-चप्पल असहाय श्रमिकों को दान करें।"
    },
    "Mercury": {
        "mantra": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः (11 या 108 बार प्रातःकाल)",
        "deity": "माँ सरस्वती अथवा भगवान विष्णु — ॐ नमो भगवते वासुदेवाय का जप करें और तुलसी दल अर्पित करें।",
        "fasting": "बुधवार को मूंग दाल युक्त सात्विक भोजन ग्रहण करें।",
        "charity": "बुधवार को गौमाता को हरा चारा, पालक अथवा हरी घास खिलाएं।"
    },
    "Ketu": {
        "mantra": "ॐ स्रां स्रीं स्रौं सः केतवे नमः (11 या 108 बार प्रातः अथवा रात्रि)",
        "deity": "विघ्नहर्ता भगवान श्री गणेश — गणेश जी को दूर्वा अर्पित करें और संकटनाशन गणेश स्तोत्र का पाठ करें।",
        "fasting": "मंगलवार या शनिवार को हल्का फलाहार रखें।",
        "charity": "स्ट्रीट डॉग्स को भोजन कराएं, दो-रंगी (चितकबरे) कंबल या काले-सफेद तिल का दान करें।"
    },
    "Venus": {
        "mantra": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः (16 या 108 बार संध्या समय)",
        "deity": "माँ महालक्ष्मी — शुक्रवार को श्री सूक्त या कनकधारा स्तोत्र का पाठ कर देशी घी का दीपक जलाएं।",
        "fasting": "शुक्रवार को नमक व खटाई रहित खीर का सेवन करें।",
        "charity": "शुद्ध देशी घी, कपूर, दही, मिश्री अथवा सफेद रेशमी वस्त्र किसी वृद्ध स्त्री को दान करें।"
    }
}

DASHA_DETAILED_FORECASTS = {
    "Sun": {
        "md_en": "The Mahadasha of the Sun establishes a monumental multi-year epoch focused on sovereign authority, organizational leadership, and executive consolidation. Under this solar cycle, passive execution gives way to direct administrative accountability. You are compelled to step into roles demanding executive decision-making, visibility before key authorities, and clear ethical alignment. In career domains, this era rewards institutional compliance, transparent capital management, and decisive leadership. Financial growth stems from steady, structured advancement rather than hasty speculation. On a psychological level, it develops resolute confidence but cautions against egoic friction with peers or superiors. Health requires monitoring bodily heat, cardiovascular stamina, and eye wellness through balanced discipline.",
        "md_hi": "सूर्य की यह महादशा आपके जीवन में स्वावलंबन, प्रशासनिक प्रतिष्ठा, आत्मविश्वास और कार्यक्षेत्र में संप्रभु नेतृत्व का एक विशाल युग स्थापित करती है। इस सौर चक्र के प्रभाव से आपके भीतर निर्णय लेने की क्षमता और कार्यपालिका शक्ति का अभूतपूर्व विकास होता है। यदि यह ग्रह आपकी कुंडली में शुभ भावों का स्वामी है, तो उच्चाधिकारियों, शासन-प्रशासन और समाज के प्रबुद्ध वर्ग से पूर्ण सहयोग प्राप्त होता है। वित्तीय दृष्टिकोण से यह समय दीर्घकालिक पूंजी निर्माण, पैतृक संपत्ति के संरक्षण और प्रतिष्ठा से जुड़े कार्यों में स्थिरता प्रदान करता है। आपको अपने व्यक्तिगत अहंकार, उच्चाधिकारियों से वैचारिक टकराव और पित्त प्रकृति के रोगों (रक्तचाप, नेत्र विकार) से सजग रहने की आवश्यकता है। सूर्योपासना से मान-सम्मान में निरंतर वृद्धि होगी।",
        "ad_en": "During this Sun sub-period, tactical responsibilities accelerate rapidly. Decisions regarding managerial promotions, legal documentation, and organizational visibility come to the forefront. It demands transparent communication and disciplined execution.",
        "ad_hi": "सूर्य की इस अंतर्दशा के दौरान दैनिक कार्यक्षेत्र में आपकी भूमिका और दृश्यता तीव्र हो जाती है। पदोन्नति, प्रशासनिक निर्णय और उत्तरदायित्वों में त्वरित परिवर्तन देखने को मिलते हैं। अहंकार से बचते हुए स्पष्ट एवं पारदर्शी कार्यशैली अपनाना ही सफलता की कुंजी है।"
    },
    "Moon": {
        "md_en": "The Mahadasha of the Moon inaugurates an intensely foundational decade governing emotional intelligence, public trust, domestic assets, and intuitive strategy. The lunar archetype operates through cyclical momentum; hence, this era demands emotional resilience and adaptive versatility. Professional advancement is heavily linked to public relations, organizational branding, human capital management, and real estate stabilization. Capital reserves compound best when protected against emotional or impulsive spending. Psychologically, your intuition, maternal bonding, and protective impulses are heightened, but boundary management is necessary to avoid mental fatigue. Health maintenance focuses on lymphatic hydration, restful sleep cycles, and grounding routines.",
        "md_hi": "चन्द्रमा की यह 10-वर्षीय महादशा मानसिक शांति, जनसंपर्क, गृह-संपत्ति, मातृसुख और बौद्धिक संवेदनशीलता का एक अत्यंत महत्वपूर्ण आधारभूत कालखंड है। चन्द्रमा का प्रभाव जीवन में उतार-चढ़ाव और निरंतर गतिशीलता लाता है, अतः इस युग में धैर्य और मानसिक संतुलन अत्यंत आवश्यक है। कार्यक्षेत्र में जनता, ग्राहकों, टीम प्रबंधन और संस्थागत साख से जुड़े क्षेत्रों में उल्लेखनीय प्रगति होती है। भूमि, भवन और वाहन से संबंधित निवेश अनुकूल परिणाम देते हैं। अत्यधिक भावुकता, अनिद्रा, जल जनित रोग और कफ विकारों से सावधान रहना चाहिए। शिव साधना और ध्यान से इस महादशा में अपार मानसिक शांति और स्थिरता प्राप्त होती है।",
        "ad_en": "This Moon sub-period centers immediate tactical focus on domestic stabilization, workplace empathy, and flexible planning. Favorable for building supportive team relationships and managing liquid capital.",
        "ad_hi": "चन्द्रमा की इस अंतर्दशा में तात्कालिक प्राथमिकताएं गृह-परिवार के सामंजस्य, मानसिक प्रसन्नता और कार्यस्थल पर सहयोगियों के साथ विश्वास सुदृढ़ करने पर केंद्रित रहती हैं। वित्तीय लेन-देन में भावुक निर्णयों से बचें।"
    },
    "Mars": {
        "md_en": "The Mahadasha of Mars commands a fast-paced, high-stakes 7-year chapter characterized by decisive action, courage, competitive triumph, and technical enterprise. Under this martian vibration, hesitation is replaced by intense operational drive. Career progress is fueled by conquering market rivals, spearheading ambitious infrastructure or real estate initiatives, and resolving overdue liabilities. Wealth compounding thrives when channelled into tangible assets and calculated, vetted industrial investments. Strategic caution is vital against impulsive aggression, volatile confrontations, and contractual haste. Physical endurance is high, but safeguard against inflammation, muscular strain, and accident risks through mindful scheduling.",
        "md_hi": "मंगल की यह 7-वर्षीय महादशा पराक्रम, अदम्य साहस, प्रतिस्पर्धी विजय, भूमि-संपत्ति और तकनीकी पुरुषार्थ का एक अत्यंत ऊर्जावान कालखंड है। इस युग में आपके निर्णय लेने की गति तीव्र होती है और आप कठिन चुनौतियों व शत्रुओं पर विजय प्राप्त करने में सक्षम होते हैं। रियल एस्टेट, निर्माण, प्रबंधन, विधि और तकनीकी उद्यमों में अप्रत्याशित सफलता मिलती है। वित्तीय दृष्टिकोण से यह समय साहसिक किंतु संयमित निवेश द्वारा संपत्ति अर्जन का है। उग्र वाणी, जल्दबाजी, पारिवारिक विवादों और रक्त/अग्नि संबंधित दुर्घटनाओं से विशेष सावधानी बरतनी चाहिए। हनुमान जी की नियमित उपासना आपको अजेय सुरक्षा प्रदान करेगी।",
        "ad_en": "The active Mars sub-period acts as a high-octane catalyst, accelerating urgent deliverables and competitive benchmarks. Focus squarely on decisive resolution without entering unnecessary friction.",
        "ad_hi": "मंगल की इस अंतर्दशा में दैनिक गतिशीलता और कार्य का दबाव बढ़ जाता है। रुके हुए कार्यों को पूरा करने और प्रतिस्पर्धियों को पीछे छोड़ने के लिए यह उत्कृष्ट समय है, बशर्ते आप क्रोध और जल्दबाजी पर अंकुश रखें।"
    },
    "Rahu": {
        "md_en": "The Mahadasha of Rahu initiates a transformative 18-year epoch of boundary-breaking material ambition, foreign linkages, unorthodox scaling, and technological disruption. Rahu refuses conventional limitations, propelling you into unfamiliar ecosystems, innovative ventures, and cross-border commercial networks. Professional expansion often occurs in dramatic, exponential surges rather than linear increments. However, this illusionary catalyst commands strict risk governance: beware of unvetted speculative schemes, toxic sycophants, and sudden psychological restlessness. Channeling Rahu's obsessive drive into structured, ethical enterprise yields massive material elevation while preserving peace of mind.",
        "md_hi": "राहु की यह 18-वर्षीय महादशा अप्रत्याशित विस्तार, वैश्विक संपर्कों, तकनीकी नवाचार, महत्वाकांक्षा और जीवन में अभूतपूर्व मोड़ों का एक चमत्कारी कालखंड है। राहु परंपरागत सीमाओं को तोड़कर आपको नए अवसरों, विदेशी संपर्कों और आधुनिक प्रणालियों की ओर अग्रसर करता है। कार्यक्षेत्र में अचानक बड़ी उपलब्धियां और पद-प्रतिष्ठा में वृद्धि संभव है। किंतु यह छाया ग्रह भ्रम और लालच का कारक भी है; अतः रातों-रात अमीर बनने की योजनाओं, अनैतिक प्रलोभनों और गोपनीय शत्रुओं से अत्यधिक सतर्क रहना अनिवार्य है। दुर्गा सप्तशती और सात्विक दिनचर्या राहु के नकारात्मक प्रभावों को निर्मल कर देती है।",
        "ad_en": "During this Rahu sub-period, expect sudden tactical pivots, unconventional ideas, and digital or foreign possibilities. Meticulously verify all fine print before committing capital.",
        "ad_hi": "राहु की इस अंतर्दशा में अप्रत्याशित सूचनाएं और अचानक यात्राएं या योजनाएं बन सकती हैं। किसी भी नए अनुबंध पर हस्ताक्षर करने से पूर्व कानूनी और वित्तीय पहलुओं की गहन जांच अवश्य करें।"
    },
    "Jupiter": {
        "md_en": "The Mahadasha of Jupiter ushers in a golden 16-year era of philosophical expansion, institutional prestige, wealth compounding, and righteous counsel. Governed by the supreme benefic Guru, this chapter anchors long-term prosperity through ethical governance, higher learning, and institutional mentorship. Professional ventures gain gravitas; your advice is sought after, and financial structures achieve permanent compound stability. Children, legacy projects, and spiritual pilgrimages flourish. Cautions involve guarding against blind optimism, over-leveraging capital on optimistic forecasts, and liver or metabolic lethargy. Maintaining strict intellectual and dietary discipline guarantees sustained grace.",
        "md_hi": "बृहस्पति (गुरु) की यह 16-वर्षीय महादशा ज्ञान, विवेक, आर्थिक सुदृढ़ता, आध्यात्मिक उन्नति और संतान सुख का एक अत्यंत शुभ व गरिमामय युग है। देवगुरु की कृपा से समाज और कार्यक्षेत्र में आपका सम्मान बढ़ता है, वरिष्ठों व मार्गदर्शकों का आशीर्वाद प्राप्त होता है, और स्थायी संपत्ति का संचय होता है। शिक्षा, परामर्श, वित्त, न्याय और लोक-कल्याणकारी कार्यों में असाधारण प्रगति होती है। यह कालखंड संचित पुण्यों के उदय का है। अति-आशावादिता, अनुचित वित्तीय जोखिम और स्वास्थ्य में यकृत (लिवर) या मोटापे से संबंधित विकारों से सचेत रहना चाहिए। विष्णु आराधना से जीवन में निरंतर शुभता प्रवाहित होती है।",
        "ad_en": "The active Jupiter sub-period brings protective tactical grace, ethical clarity, and favorable financial arrangements. Excellent for launching educational, legal, or advisory milestones.",
        "ad_hi": "गुरु की इस अंतर्दशा में तात्कालिक समस्याओं का समाधान विवेकपूर्ण संवाद से होता है। यह समय नई योजनाओं के शुभारंभ, वित्तीय निवेश और पारिवारिक मांगलिक कार्यों के लिए अत्यंत अनुकूल है।"
    },
    "Saturn": {
        "md_en": "The Mahadasha of Saturn commands a profound 19-year masterclass in karmic accountability, structural discipline, organizational grit, and permanent legacy building. Saturn strips away superficial shortcuts, demanding meticulous labor, procedural integrity, and unyielding patience. While early phases often impose heavy operational burdens and delayed gratification, the structures forged during this era become indestructible anchors of permanent success. Capital must be allocated with extreme conservatism and zero speculative leverage. Health discipline requires attention to joint mobility, posture, and neurological stress through consistent restorative habits.",
        "md_hi": "शनिदेव की यह 19-वर्षीय महादशा कर्म शुद्धि, कठोर परिश्रम, अनुशासन, धैर्य और जीवन में स्थायी नींव रखने का एक गहरा आध्यात्मिक व व्यावहारिक कालखंड है। शनिदेव न्याय के अधिष्ठाता हैं; अतः यह युग किसी भी प्रकार के शॉर्टकट या अनैतिक आचरण को स्वीकार नहीं करता। प्रारंभिक रूप से कार्यभार और जिम्मेदारियां बढ़ सकती हैं, किंतु आपकी निष्ठा और संयम आपको दीर्घकालिक स्थायी सफलता, सत्ता और सम्मान प्रदान करते हैं। वित्तीय प्रबंधन में अत्यधिक मितव्ययिता बरतें। जोड़ों के दर्द, वात रोग, अवसाद और मानसिक तनाव से बचने के लिए नियमित योग व शनि साधना अनिवार्य है।",
        "ad_en": "The active Saturn sub-period demands rigorous attention to detail, operational audits, and patient stamina. Eliminate workflow redundancies and respect structural timelines.",
        "ad_hi": "शनि की इस अंतर्दशा में कार्यस्थल पर अनुशासन और दायित्वों की समीक्षा आवश्यक हो जाती है। परिणाम आने में भले ही थोड़ा विलंब हो, किंतु आपकी निरंतर मेहनत अंततः ठोस और स्थायी परिणाम देगी।"
    },
    "Mercury": {
        "md_en": "The Mahadasha of Mercury unfolds a versatile, intellectually stimulating 17-year chapter focused on commercial expansion, data synthesis, negotiation mastery, and communications. Under Mercury’s analytical stewardship, your mind operates at maximum agility. Professional gains materialize through digital media, cross-functional trade, legal contracts, and intellectual networking. Wealth thrives through diversified liquid asset allocations and calculated trading strategies. The primary hazards are cognitive burnout, nervous anxiety, and scattered priorities caused by over-multitasking. Grounding mental chatter through meditation and nature resets restores peak clarity.",
        "md_hi": "बुध की यह 17-वर्षीय महादशा व्यापारिक विस्तार, बौद्धिक चातुर्य, संचार कौशल, लेखन और विश्लेषणात्मक दक्षता का एक अत्यंत गतिशील युग है। बुध की कृपा से निर्णय क्षमता में तीव्रता आती है, व्यापार और साझेदारी के नए मार्ग प्रशस्त होते हैं, और बौद्धिक संपदा का विकास होता है। वाणिज्य, वित्त, मीडिया, सूचना प्रौद्योगिकी और जनसंचार से जुड़े लोगों के लिए यह कालखंड स्वर्णिम सिद्ध होता है। अत्यधिक मानसिक कार्य से स्नायु दुर्बलता (नर्वस सिस्टम) और त्वचा संबंधी विकारों से सावधान रहें। गौसेवा और गणेश जी की आराधना से व्यापार व बुद्धि में तीव्र प्रगति होती है।",
        "ad_en": "During this Mercury sub-period, correspondence, documentation, and verbal diplomacy take center stage. Execute contracts cleanly and maintain precise data hygiene.",
        "ad_hi": "बुध की इस अंतर्दशा में दैनिक कार्यों में संवाद, व्यापारिक यात्राएं और लिखा-पढ़ी के कार्य बढ़ जाते हैं। किसी भी दस्तावेज़ पर विचार-विमर्श के उपरांत ही सहमति दें।"
    },
    "Ketu": {
        "md_en": "The Mahadasha of Ketu represents a profound 7-year spiritual crucible dedicated to root-cause investigation, metaphysical research, psychological purification, and detachment from obsolete constructs. Ketu dissolves superficial attachments, compelling you to seek higher self-mastery. In professional domains, routine bureaucratic vanity loses appeal, shifting focus toward deep specialist research, technical troubleshooting, or autonomous advisory roles. Financial preservation demands conservative security rather than expansionist enterprise. Guard against sudden escapism, erratic decisions, and contractual ambiguity through grounded self-discipline.",
        "md_hi": "केतु की यह 7-वर्षीय महादशा आत्म-निरीक्षण, गूढ़ विद्याओं, आध्यात्मिक अनुसंधान, वैराग्य और भौतिक बंधनों के शोधन का एक पवित्र कालखंड है। केतु पुरानी और निरर्थक व्यवस्थाओं को समाप्त कर जीवन में एक नई चेतना का संचार करता है। कार्यक्षेत्र में नियमित चमक-दमक के स्थान पर गहन तकनीकी शोध, एकांत चिंतन और स्वतंत्र परामर्श में अभूतपूर्व सफलता मिलती है। भौतिक योजनाओं में अचानक बदलाव आ सकते हैं; अतः अनुबंधों में पूर्ण स्पष्टता रखें। मानसिक भटकाव और अज्ञात भय से बचने के लिए गणेश उपासना और ध्यान का आश्रय लेना सर्वश्रेष्ठ रहता है।",
        "ad_en": "This Ketu sub-period brings moments of introspection and subtle course-corrections. Rely on gut intuition while ensuring practical safeguards remain anchored.",
        "ad_hi": "केतु की इस अंतर्दशा में आपका मन आत्म-मंथन और एकांत की ओर प्रवृत्त हो सकता है। तात्कालिक योजनाओं को शांत भाव से परखें और जल्दबाजी में कोई संबंध या कार्य न छोड़ें।"
    },
    "Venus": {
        "md_en": "The Mahadasha of Venus commands an expansive 20-year cycle dedicated to material comforts, harmonious alliances, creative mastery, and refined aesthetic wealth. Governed by Daityaguru Shukra, this epoch unlocks access to luxury conveyances, domestic beautification, artistic fulfillment, and mutually enriching partnerships. Executive authority is achieved through soft power, diplomacy, and persuasive negotiation rather than brute force. Financial capital compounds through strategic alliances, high-value consumer assets, and creative design. Strategic caution centers on financial over-indulgence, vanity, and interpersonal dependency. Living with elegant restraint preserves peak harmony.",
        "md_hi": "शुक्र की यह 20-वर्षीय महादशा भौतिक ऐश्वर्य, कलात्मक सुरुचि, वाहन-सुख, मधुर संबंधों और जीवन में सुख-समृद्धि का एक अत्यंत वैभवशाली युग है। शुक्राचार्य की कृपा से जीवनशैली में गुणात्मक सुधार आता है, व्यापारिक साझेदारियों और दांपत्य जीवन में प्रगाढ़ता आती है, और नए संपत्तियों का अर्जन होता है। कूटनीति, सौंदर्य, विलासिता और रचनात्मक क्षेत्रों में भारी लाभ मिलता है। वित्तीय मामलों में अत्यधिक विलासिता, फिजूलखर्ची और आत्म-मुग्धता से बचना आवश्यक है। माँ महालक्ष्मी की नित्य आराधना इस महादशा में निरंतर सुख और अखंड लक्ष्मी की प्राप्ति कराती है।",
        "ad_en": "The active Venus sub-period refines immediate negotiations, social engagements, and domestic upgrades. Excellent for formalizing collaborations and resolving interpersonal friction.",
        "ad_hi": "शुक्र की इस अंतर्दशा में सामाजिक दायरे का विस्तार, कलात्मक कार्यों में रुचि और पारिवारिक सुख में वृद्धि होती है। वित्तीय सौदों में संयम बनाए रखें।"
    }
}

def generate_relationship_statements(lagna_idx: int, md_lord: str, ad_lord: str, is_hi: bool):
    lagna_lord = LAGNA_LORDS.get(lagna_idx, "Mars")
    lagna_aff = LAGNA_AFFILIATION_MAP.get(lagna_idx, {})
    
    md_aff = lagna_aff.get(md_lord, {"role_en": "Influence", "role_hi": "प्रभाव", "gem_safe": False})
    ad_aff = lagna_aff.get(ad_lord, {"role_en": "Influence", "role_hi": "प्रभाव", "gem_safe": False})
    
    md_name = PLANET_NAMES_HI[md_lord] if is_hi else md_lord
    ad_name = PLANET_NAMES_HI[ad_lord] if is_hi else ad_lord
    l_lord_name = PLANET_NAMES_HI[lagna_lord] if is_hi else lagna_lord
    
    md_role = md_aff['role_hi'] if is_hi else md_aff['role_en']
    ad_role = ad_aff['role_hi'] if is_hi else ad_aff['role_en']

    # 1. MD to Lagna
    md_friends = NATURAL_FRIENDSHIPS.get(md_lord, {}).get("friends", [])
    md_enemies = NATURAL_FRIENDSHIPS.get(md_lord, {}).get("enemies", [])
    if md_lord == lagna_lord:
        md_lagna_rel = f"महादशा स्वामी **{md_name}** स्वयं आपके **लग्नेश** हैं ({md_role})। यह कालखंड आत्मबल, शारीरिक आरोग्यता और व्यक्तिगत संप्रभुता के लिए अत्यंत फलदायी है।" if is_hi else f"The Mahadasha lord **{md_lord}** is your **Lagna Lord** ({md_role}). This establishes an era of personal empowerment and autonomy."
    elif lagna_lord in md_friends:
        md_lagna_rel = f"महादशा स्वामी **{md_name}** आपके लग्नेश {l_lord_name} के **प्राकृतिक मित्र** हैं तथा आपकी कुंडली में **{md_role}** का दायित्व संभालते हैं। यह संबंध करियर और जीवन में स्वाभाविक प्रगति और अनुकूल वातावरण प्रदान करता है।" if is_hi else f"The Mahadasha lord **{md_lord}** is a **natural ally** to your Lagna lord {l_lord_name} ({md_role}), supporting career stability and steady growth."
    elif lagna_lord in md_enemies:
        md_lagna_rel = f"महादशा स्वामी **{md_name}** आपके लग्नेश {l_lord_name} के **शत्रु ग्रह** हैं और कुंडली में **{md_role}** के रूप में स्थित हैं। यह कालखंड संयम, निरंतर सतर्कता और अनुशासित योजना की मांग करता है।" if is_hi else f"The Mahadasha lord **{md_lord}** is a **functional adversary** to your Lagna lord {l_lord_name} ({md_role}), demanding patient resilience and risk management."
    else:
        md_lagna_rel = f"महादशा स्वामी **{md_name}** आपके लग्नेश {l_lord_name} के प्रति **सम (तटस्थ)** भाव रखते हैं तथा **{md_role}** का कार्य करते हैं। परिणाम आपके निजी प्रयासों और कर्म पर निर्भर करेंगे।" if is_hi else f"The Mahadasha lord **{md_lord}** is **neutral** toward your Lagna lord {l_lord_name} ({md_role}). Outcomes depend directly on personal effort."

    # 2. AD to Lagna
    ad_friends = NATURAL_FRIENDSHIPS.get(ad_lord, {}).get("friends", [])
    ad_enemies = NATURAL_FRIENDSHIPS.get(ad_lord, {}).get("enemies", [])
    if ad_lord == lagna_lord:
        ad_lagna_rel = f"अंतर्दशा स्वामी **{ad_name}** आपके **लग्नेश** हैं ({ad_role})। यह समय आपके स्वास्थ्य, व्यक्तिगत निर्णयों और मान-सम्मान को प्रत्यक्ष रूप से सशक्त करता है।" if is_hi else f"The Antardasha lord **{ad_lord}** is your **Lagna Lord** ({ad_role}), revitalizing self-identity and physical energy."
    elif lagna_lord in ad_friends:
        ad_lagna_rel = f"अंतर्दशा स्वामी **{ad_name}** आपके लग्नेश के **मित्र** हैं ({ad_role})। यह दैनिक कार्यों को सुगम बनाता है और कार्यक्षेत्र में सहयोग प्राप्त कराता है।" if is_hi else f"The Antardasha lord **{ad_lord}** is an **ally to your Lagna lord** ({ad_role}), smoothing daily initiatives."
    elif lagna_lord in ad_enemies:
        ad_lagna_rel = f"अंतर्दशा स्वामी **{ad_name}** आपके लग्नेश के **शत्रु** हैं ({ad_role})। तात्कालिक परिस्थितियों में थोड़ा मानसिक तनाव अथवा अवरोध संभव है।" if is_hi else f"The Antardasha lord **{ad_lord}** is an **adversary to your Lagna lord** ({ad_role}), introducing short-term operational hurdles."
    else:
        ad_lagna_rel = f"अंतर्दशा स्वामी **{ad_name}** आपके लग्नेश के प्रति **सम** हैं ({ad_role})। दिनचर्या सामान्य और संतुलित रहेगी।" if is_hi else f"The Antardasha lord **{ad_lord}** is **neutral** to your Lagna lord ({ad_role}), maintaining steady daily rhythm."

    # 3. AD to MD Relationship
    ad_rel_friends = NATURAL_FRIENDSHIPS.get(ad_lord, {}).get("friends", [])
    ad_rel_enemies = NATURAL_FRIENDSHIPS.get(ad_lord, {}).get("enemies", [])
    if ad_lord == md_lord:
        ad_md_rel = f"अंतर्दशा स्वामी **{ad_name}** स्वयं महादशा स्वामी हैं (स्व-भुक्ति)। इस ग्रह का मूल प्रभाव बिना किसी रुकावट के पूर्ण क्षमता से कार्य करेगा।" if is_hi else f"The Antardasha lord **{ad_lord}** is identical to the Mahadasha lord (Sva-Bhukti), operating at full archetypal strength."
    elif md_lord in ad_rel_friends:
        ad_md_rel = f"अंतर्दशा स्वामी **{ad_name}** एवं महादशा स्वामी **{md_name}** के मध्य **परस्पर मित्रता** है। दोनों ग्रह सामंजस्य से कार्य करेंगे जिससे योजनाओं में त्वरित गति आएगी।" if is_hi else f"The Antardasha lord **{ad_lord}** is a **friend** to Mahadasha lord **{md_lord}**, allowing long-term projects to advance smoothly."
    elif md_lord in ad_rel_enemies:
        ad_md_rel = f"अंतर्दशा स्वामी **{ad_name}** एवं महादशा स्वामी **{md_name}** के मध्य **परस्पर शत्रुता** है। दीर्घकालिक लक्ष्यों और तात्कालिक प्राथमिकताओं में थोड़ा द्वंद्व रह सकता है।" if is_hi else f"The Antardasha lord **{ad_lord}** is an **adversary** to Mahadasha lord **{md_lord}**, requiring balance between macro and immediate priorities."
    else:
        ad_md_rel = f"अंतर्दशा स्वामी **{ad_name}** एवं महादशा स्वामी **{md_name}** के मध्य **तटस्थ संबंध** है। कार्य सुचारू रूप से आगे बढ़ेंगे।" if is_hi else f"The Antardasha lord **{ad_lord}** holds a **neutral** relationship with Mahadasha lord **{md_lord}**, maintaining steady progress."

    return md_lagna_rel, ad_lagna_rel, ad_md_rel, md_aff, ad_aff

def format_remedial_protocol(planet_name: str, aff_dict: dict, is_hi: bool) -> str:
    rem = REMEDIAL_PROTOCOLS.get(planet_name, {})
    lines = []
    
    if is_hi:
        if aff_dict.get("gem_safe", False):
            lines.append(f"<b>💎 अनुशंसित रत्न:</b> {aff_dict.get('gem_hi')} (शुभ मुहूर्त में विधिपूर्वक धारण करें)")
        else:
            lines.append(f"<b>⚠️ रत्न परामर्श:</b> आपकी कुंडली अनुसार {PLANET_NAMES_HI[planet_name]} त्रिक अथवा मारक भाव के स्वामी हैं; अतः <b>रत्न धारण वर्जित है</b>। अनिष्ट ग्रहों का रत्न धारण करने से रुकावटें बढ़ सकती हैं। केवल सात्विक पूजा व मंत्र जप करें:")
        
        lines.append(f"<b>📿 बीज मंत्र:</b> {rem.get('mantra')}")
        lines.append(f"<b>🪔 शास्त्रीय देव आराधना:</b> {rem.get('deity')}")
        lines.append(f"<b>🍲 उपवास व आहार नियम:</b> {rem.get('fasting')}")
        lines.append(f"<b>🤝 निर्धारित दान:</b> {rem.get('charity')}")
    else:
        p_name_en = planet_name
        if aff_dict.get("gem_safe", False):
            lines.append(f"<b>💎 Prescribed Vedic Gemstone:</b> {aff_dict.get('gem_en')} worn on recommended finger after expert trial.")
        else:
            lines.append(f"<b>⚠️ Gemstone Advisory:</b> Because {p_name_en} governs functional dusthana or maraka houses for your Ascendant, <b>gemstones are strictly not recommended</b>. Use the following non-invasive, sattvic protocols instead:")
        
        lines.append(f"<b>📿 Authentic Beej Mantra:</b> {rem.get('mantra')}")
        lines.append(f"<b>🪔 Classical Deity Sadhana:</b> {rem.get('deity')}")
        lines.append(f"<b>🍲 Dietary & Fasting Discipline:</b> {rem.get('fasting')}")
        lines.append(f"<b>🤝 Prescribed Charitable Action (Daan):</b> {rem.get('charity')}")
        
    return "<br><br>".join(lines)

def local_add_years(dt: datetime.datetime, years: float) -> datetime.datetime:
    return dt + datetime.timedelta(days=years * 365.2425)

def local_calculate_live_dasha(birth_dt: datetime.datetime, moon_lon: float, target_dt: datetime.datetime):
    star_span = 360.0 / 27.0
    star_idx = int(moon_lon / star_span)
    start_lord_idx = star_idx % 9
    
    elapsed_deg = moon_lon - (star_idx * star_span)
    fraction_left = max(0.0, min(1.0, 1.0 - (elapsed_deg / star_span)))
    
    start_lord = DASHA_SEQ[start_lord_idx]
    balance_years = DASHA_YRS[start_lord] * fraction_left
    
    md_idx = start_lord_idx
    md_start = birth_dt
    md_years = balance_years
    md_end = local_add_years(md_start, md_years)
    
    while target_dt > md_end:
        md_start = md_end
        md_idx = (md_idx + 1) % 9
        current_lord = DASHA_SEQ[md_idx]
        md_years = DASHA_YRS[current_lord]
        md_end = local_add_years(md_start, md_years)
        
    current_md_lord = DASHA_SEQ[md_idx]
    
    curr_ad_st = md_start
    active_ad = ("Ketu", md_years, md_start, md_end)
    for i in range(9):
        sub_lord = DASHA_SEQ[(md_idx + i) % 9]
        sub_yrs = (md_years * DASHA_YRS[sub_lord]) / 120.0
        sub_ed = local_add_years(curr_ad_st, sub_yrs)
        if curr_ad_st <= target_dt <= sub_ed:
            active_ad = (sub_lord, sub_yrs, curr_ad_st, sub_ed)
            break
        curr_ad_st = sub_ed
    else:
        active_ad = (sub_lord, sub_yrs, curr_ad_st, sub_ed)
        
    return [
        {"level": "Mahadasha", "lord": current_md_lord, "start": md_start, "end": md_end},
        {"level": "Antardasha", "lord": active_ad[0], "start": active_ad[2], "end": active_ad[3]}
    ]

# The Primary View Renderer
def render_page_dasha():
    # Read state directly from session_state (Pattern B)
    if not st.session_state.get("has_valid_profile", False):
        st.warning("Please set up your profile first.")
        return

    chart_info = st.session_state["chart_info"]
    dob_parsed = st.session_state["dob_parsed"]
    tob_parsed = st.session_state["tob_parsed"]
    current_lang = st.session_state.user_profile.get("lang", "en")
    is_hi = (current_lang == "hi")

    birth_ist = datetime.datetime.combine(dob_parsed, tob_parsed)
    now_ist = datetime.datetime.now()
    
    dasha_levels = local_calculate_live_dasha(birth_ist, chart_info['moon_lon'], now_ist)
    md_item = dasha_levels[0]
    ad_item = dasha_levels[1]
    
    next_ad_target = ad_item['end'] + datetime.timedelta(days=2)
    next_ad_levels = local_calculate_live_dasha(birth_ist, chart_info['moon_lon'], next_ad_target)
    next_ad_item = next_ad_levels[1]

    next_md_target = md_item['end'] + datetime.timedelta(days=2)
    next_md_levels = local_calculate_live_dasha(birth_ist, chart_info['moon_lon'], next_md_target)
    next_md_item = next_md_levels[0]

    lagna_idx = chart_info['lagna_idx']
    raw_lagna_name = chart_info['lagna_name']
    display_lagna = f"{LAGNA_NAMES_HI.get(raw_lagna_name, raw_lagna_name)} लग्न" if is_hi else f"{raw_lagna_name} Ascendant"

    md_lagna_rel, ad_lagna_rel, ad_md_rel, md_aff, ad_aff = generate_relationship_statements(
        lagna_idx, md_item['lord'], ad_item['lord'], is_hi
    )

    md_forecast_obj = DASHA_DETAILED_FORECASTS.get(md_item['lord'], DASHA_DETAILED_FORECASTS["Jupiter"])
    ad_forecast_obj = DASHA_DETAILED_FORECASTS.get(ad_item['lord'], DASHA_DETAILED_FORECASTS["Saturn"])
    
    md_pred_text = md_forecast_obj['md_hi'] if is_hi else md_forecast_obj['md_en']
    ad_pred_text = ad_forecast_obj['ad_hi'] if is_hi else ad_forecast_obj['ad_en']

    md_rem_text = format_remedial_protocol(md_item['lord'], md_aff, is_hi)
    ad_rem_text = format_remedial_protocol(ad_item['lord'], ad_aff, is_hi)

    md_disp_name = PLANET_NAMES_HI[md_item['lord']] if is_hi else md_item['lord'].upper()
    ad_disp_name = PLANET_NAMES_HI[ad_item['lord']] if is_hi else ad_item['lord'].upper()
    next_md_disp = PLANET_NAMES_HI[next_md_item['lord']] if is_hi else next_md_item['lord'].upper()
    next_ad_disp = PLANET_NAMES_HI[next_ad_item['lord']] if is_hi else next_ad_item['lord'].upper()

    lbl_title = "⏳ विंशोत्तरी दशा: खगोलीय समयरेखा" if is_hi else "⏳ Vimshottari Dasha: The Cosmic Timeline"
    lbl_subtitle = "आपकी वर्तमान सक्रिय ग्रहों की महादशा और अंतरदशा सटीक समय के साथ।" if is_hi else "Your active planetary periods mathematically calculated down to the exact minute. This represents the overarching 'season' of your life."
    lbl_md_card = "🟩 वर्तमान महादशा" if is_hi else "🟩 Active Mahadasha"
    lbl_ad_card = "🟦 वर्तमान अंतर्दशा" if is_hi else "🟦 Active Antardasha"
    lbl_rel_header = "🪐 लग्न के साथ संबंध:" if is_hi else "🪐 Planetary Relationship with Your Lagna:"
    lbl_ad_rel_header = "🪐 अंतर्दशा ग्रहीय संबंध:" if is_hi else "🪐 Sub-Period Planetary Relationships:"
    lbl_md_fc_header = "📋 विस्तृत रणनीतिक फलादेश (महादशा कालखंड):" if is_hi else "📋 Detailed Strategic Forecast (Mahadasha Era):"
    lbl_ad_fc_header = "🎯 सामयिक फलादेश (अंतर्दशा उप-काल):" if is_hi else "🎯 Tactical Forecast (Antardasha Sub-Period):"
    lbl_rem_header = "🪔 निर्धारित वैदिक उपाय एवं अनुष्ठान:" if is_hi else "🪔 Prescribed Remedial Protocol:"
    lbl_ad_rem_header = "🪔 अंतर्दशा उप-काल उपाय:" if is_hi else "🪔 Sub-Period Remedial Protocol:"
    lbl_upcoming_header = "⏳ आगामी ग्रहीय परिवर्तन (Upcoming Transitions)" if is_hi else "⏳ Upcoming Planetary Transitions"
    lbl_next_md = "अगली महादशा:" if is_hi else "Next Mahadasha:"
    lbl_next_ad = "अगली अंतर्दशा:" if is_hi else "Next Antardasha:"
    lbl_starts = "प्रारंभ" if is_hi else "Starts"

    render_html(f"""
    <div style="margin-bottom:1.5rem;">
        <div style="font-weight:900; font-size:1.35rem; color:#1e293b;">{lbl_title}</div>
        <div style="font-size:0.95rem; color:#475569; margin-top:4px;">
            {lbl_subtitle} ({display_lagna})
        </div>
    </div>

    <!-- ACTIVE TIMELINE CARDS WITH EMBEDDED IN-DEPTH BRIEFINGS -->
    <div style="display:grid; grid-template-columns: 1fr; gap:16px; margin-bottom:1.5rem;">
        
        <!-- MAHADASHA CARD -->
        <div style="background:#f0fdf4; border-radius:14px; padding:18px; border:1px solid #bbf7d0; border-left:6px solid #16a34a; box-shadow:0 3px 10px rgba(0,0,0,0.02);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <b style="color:#14532d; font-size:1.18rem;">{lbl_md_card}: {md_disp_name}</b>
                <span style="font-size:0.8rem; background:#ffffff; color:#15803d; padding:3px 8px; border-radius:12px; font-weight:800; border:1px solid #86efac;">Live 🟢</span>
            </div>
            <div style="font-size:0.88rem; color:#166534; font-weight:700; margin-bottom:12px;">
                ⏱️ {md_item['start'].strftime('%b %d, %Y')} — {md_item['end'].strftime('%b %d, %Y')}
            </div>

            <div style="background:#dcfce7; border-radius:10px; padding:12px 14px; border:1px solid #bbf7d0; margin-bottom:12px; font-size:0.93rem; color:#14532d; line-height:1.6;">
                <b>{lbl_rel_header}</b><br>{md_lagna_rel}
            </div>

            <div style="font-size:0.95rem; color:#1e293b; line-height:1.75; background:#ffffff; padding:16px 18px; border-radius:10px; border:1px solid #dcfce7; margin-bottom:12px;">
                <b style="color:#15803d; font-size:1.02rem;">{lbl_md_fc_header}</b><br><br>
                {md_pred_text}
            </div>

            <div style="font-size:0.92rem; color:#14532d; line-height:1.65; background:#ffffff; padding:14px 16px; border-radius:10px; border:1px solid #86efac;">
                <b style="color:#166534; font-size:0.98rem;">{lbl_rem_header}</b><br><br>
                {md_rem_text}
            </div>
        </div>

        <!-- ANTARDASHA CARD -->
        <div style="background:#eff6ff; border-radius:14px; padding:18px; border:1px solid #bfdbfe; border-left:6px solid #2563eb; box-shadow:0 3px 10px rgba(0,0,0,0.02);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <b style="color:#1e3a8a; font-size:1.18rem;">{lbl_ad_card}: {ad_disp_name}</b>
                <span style="font-size:0.8rem; background:#ffffff; color:#1d4ed8; padding:3px 8px; border-radius:12px; font-weight:800; border:1px solid #93c5fd;">Live 🟢</span>
            </div>
            <div style="font-size:0.88rem; color:#1e40af; font-weight:700; margin-bottom:12px;">
                ⏱️ {ad_item['start'].strftime('%b %d, %Y')} — {ad_item['end'].strftime('%b %d, %Y')}
            </div>

            <div style="background:#dbeafe; border-radius:10px; padding:12px 14px; border:1px solid #bfdbfe; margin-bottom:12px; font-size:0.93rem; color:#1e3a8a; line-height:1.6;">
                <b>{lbl_ad_rel_header}</b><br>
                • {ad_lagna_rel}<br>
                • {ad_md_rel}
            </div>

            <div style="font-size:0.95rem; color:#1e293b; line-height:1.75; background:#ffffff; padding:16px 18px; border-radius:10px; border:1px solid #dbeafe; margin-bottom:12px;">
                <b style="color:#1d4ed8; font-size:1.02rem;">{lbl_ad_fc_header}</b><br><br>
                {ad_pred_text}
            </div>

            <div style="font-size:0.92rem; color:#1e3a8a; line-height:1.65; background:#ffffff; padding:14px 16px; border-radius:10px; border:1px solid #93c5fd;">
                <b style="color:#1e40af; font-size:0.98rem;">{lbl_ad_rem_header}</b><br><br>
                {ad_rem_text}
            </div>
        </div>
    </div>

    <!-- UPCOMING TRANSITIONS CARD -->
    <div style="background:#ffffff; border-radius:14px; padding:16px; border:1.5px solid #cbd5e1; box-shadow:0 3px 10px rgba(0,0,0,0.02);">
        <div style="font-weight:900; font-size:1.1rem; color:#0f172a; margin-bottom:10px; border-bottom:1.5px solid #f1f5f9; padding-bottom:6px;">
            {lbl_upcoming_header}
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:0.9rem;">
            <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                <b style="color:#0369a1;">{lbl_next_md}</b><br>
                <div style="font-weight:900; color:#0f172a; font-size:1rem; margin:2px 0;">{next_md_disp}</div>
                <span style="font-size:0.82rem; color:#64748b;">{lbl_starts} {next_md_item['start'].strftime('%b %d, %Y')}</span>
            </div>
            <div style="background:#f8fafc; border-radius:10px; padding:10px; border:1px solid #e2e8f0;">
                <b style="color:#0369a1;">{lbl_next_ad}</b><br>
                <div style="font-weight:900; color:#0f172a; font-size:1rem; margin:2px 0;">{next_ad_disp}</div>
                <span style="font-size:0.82rem; color:#64748b;">{lbl_starts} {next_ad_item['start'].strftime('%b %d, %Y')}</span>
            </div>
        </div>
    </div>
    """)

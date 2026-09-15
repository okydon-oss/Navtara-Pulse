import streamlit as st
# databanks.py - Exhaustive Dictionaries & Encyclopedias

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

RASHIS = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAVTARA_NAMES = [
    ("Janma (Birth/Identity)", "🌱", "Sensitive & Foundational"),
    ("Sampat (Wealth/Gain)", "🟢", "Highly Auspicious & Material Abundance"),
    ("Vipat (Adversity/Friction)", "🔴", "Caution & Resistance"),
    ("Kshema (Well-being/Comfort)", "🟢", "Peace, Protection & Sustenance"),
    ("Pratyari (Obstacles/Delays)", "🔴", "High Resistance & Delays"),
    ("Sadhana (Accomplishment)", "🟢", "Success, Discipline & Mastery"),
    ("Vadha (Destruction/Loss)", "🔴", "Heavy Friction & Caution"),
    ("Mitra (Friendship/Allies)", "🟢", "Cordiality & Cooperative Harmony"),
    ("Ati-Mitra (Supreme Alliance)", "🟢🟢", "Supreme Synergy & Deep Expansion")
]

SHANI_VAHANS = {
    1: {"name": "Gaja (Elephant / हस्ती)", "type": "Highly Auspicious (अति शुभ)", "speed": "Dignified & Steady", "desc": "Guaranteed wealth expansion, societal respect, sound health, and enduring peace."},
    2: {"name": "Ashwa (Horse / अश्व)", "type": "Progressive & Dynamic (शुभ)", "speed": "Rapid & Victorious", "desc": "Brisk progress, victory in competitive undertakings, and sudden career momentum."},
    3: {"name": "Simha (Lion / सिंह)", "type": "Victorious & Authoritative (शुभ)", "speed": "Commanding & Decisive", "desc": "Dominance over competitors, professional promotion, and clear leadership recognition."},
    4: {"name": "Gardabha (Donkey / गर्दभ)", "type": "Demanding & Heavy (कठिन)", "speed": "Slow & Laborious", "desc": "Heavy labor, delayed recognition, and testing of patient endurance."},
    5: {"name": "Kukkuta (Rooster / कुक्कुट)", "type": "Restless & Mixed (मिश्रित)", "speed": "Impulsive & Alert", "desc": "Sudden squabbles, mental restlessness, and unnecessary emotional volatility."},
    6: {"name": "Shvana (Dog / श्वान)", "type": "Vigilant & Challenging (संघर्षमय)", "speed": "Guarded & Suspicious", "desc": "Heightened anxiety, false accusations, and risk of misunderstandings."},
    7: {"name": "Jambuka (Jackal / जम्बुक)", "type": "Difficult & Testing (कठिन)", "speed": "Hesitant & Cautious", "desc": "Unexpected financial leaks, health dips, and domestic disharmony."},
    8: {"name": "Kaka (Crow / काक)", "type": "High Friction (अशुभ)", "speed": "Disruptive & Harsh", "desc": "Mental distress, family strife, and high risk of wasted expenditure."},
    9: {"name": "Mayura (Peacock / मयूर)", "type": "Auspicious & Graceful (शुभ)", "speed": "Harmonious & Joyful", "desc": "Artistic success, mental serenity, sudden fortune, and creative joy."}
}

CHALDEAN_MAP = {
    'A': 1, 'I': 1, 'J': 1, 'Q': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}

NUM_PLANET_NAMES = {
    1: {"en": "Sun (Surya / सूर्य)", "hi": "सूर्य (Sun)"},
    2: {"en": "Moon (Chandra / चन्द्र)", "hi": "चन्द्र (Moon)"},
    3: {"en": "Jupiter (Brihaspati / गुरु)", "hi": "गुरु (Jupiter)"},
    4: {"en": "Rahu (North Node / राहु)", "hi": "राहु (Rahu)"},
    5: {"en": "Mercury (Budha / बुध)", "hi": "बुध (Mercury)"},
    6: {"en": "Venus (Shukra / शुक्र)", "hi": "शुक्र (Venus)"},
    7: {"en": "Ketu (South Node / केतु)", "hi": "केतु (Ketu)"},
    8: {"en": "Saturn (Shani / शनि)", "hi": "शनि (Saturn)"},
    9: {"en": "Mars (Mangal / मंगल)", "hi": "मंगल (Mars)"}
}

CITY_COORDINATES = {
    "Delhi / New Delhi, India": (28.6139, 77.2090),
    "Mumbai, Maharashtra, India": (19.0760, 72.8777),
    "Chhatrapati Sambhajinagar (Aurangabad), Maharashtra, India": (19.8762, 75.3433),
    "Pune, Maharashtra, India": (18.5204, 73.8567),
    "Nagpur, Maharashtra, India": (21.1458, 79.0882),
    "Bengaluru, Karnataka, India": (12.9716, 77.5946),
    "Hyderabad, Telangana, India": (17.3850, 78.4867),
    "Chennai, Tamil Nadu, India": (13.0827, 80.2707),
    "Kolkata, West Bengal, India": (22.5726, 88.3639),
    "Ahmedabad, Gujarat, India": (23.0225, 72.5714),
    "Surat, Gujarat, India": (21.1702, 72.8311),
    "Jaipur, Rajasthan, India": (26.9124, 75.7873),
    "Lucknow, Uttar Pradesh, India": (26.8467, 80.9462),
    "Varanasi, Uttar Pradesh, India": (25.3176, 82.9739),
    "Patna, Bihar, India": (25.5941, 85.1376),
    "Bhopal, Madhya Pradesh, India": (23.2599, 77.4126),
    "Indore, Madhya Pradesh, India": (22.7196, 75.8577),
    "Chandigarh, India": (30.7333, 76.7794),
    "Dubai, UAE": (25.2048, 55.2708),
    "London, UK": (51.5074, -0.1278),
    "New York, USA": (40.7128, -74.0060),
    "San Francisco, USA": (37.7749, -122.4194),
    "Singapore": (1.3521, 103.8198),
    "Toronto, Canada": (43.6532, -79.3832)
}

NAKSHATRA_BIO_DATA = {
    1: {"deity": "Ashwini Kumaras (Celestial Healers)", "symbol": "Horse's Head", "tree": "Kuchila / Strychnine (विषमुष्टी)", "bird": "Shikra / Wild Hawk", "animal": "Horse (Ashwa / अश्व)", "lord": "Ketu"},
    2: {"deity": "Lord Yama (Dharma & Cosmic Justice)", "symbol": "Yoni / Creative Triangle", "tree": "Amla / Indian Gooseberry (धात्री)", "bird": "Crow (काक)", "animal": "Elephant (Gaja / गज)", "lord": "Venus (Shukra)"},
    3: {"deity": "Agni (God of Fire & Transformation)", "symbol": "Razor / Flame / Knife", "tree": "Gular / Cluster Fig (उदुम्बर)", "bird": "Peacock (मयूर)", "animal": "Sheep / Ram (मेष)", "lord": "Sun (Surya)"},
    4: {"deity": "Prajapati / Lord Brahma (Creator)", "symbol": "Chariot / Cart / Temple", "tree": "Jamun / Black Plum (जम्बू)", "bird": "Owl (उलूक)", "animal": "Serpent (Sarpa / सर्प)", "lord": "Moon (Chandra)"},
    5: {"deity": "Soma (God of Nectar & Vitality)", "symbol": "Deer's Head", "tree": "Khair / Acacia Catechu (खदिर)", "bird": "Batar / Francolin", "animal": "Serpent (Sarpa / सर्प)", "lord": "Mars (Mangal)"},
    6: {"deity": "Rudra (Storm & Destructive Transformation)", "symbol": "Teardrop / Diamond / Jewel", "tree": "Agarwood / Krishna Agaru (अगरु)", "bird": "Andal / Red-wattled Lapwing", "animal": "Dog (Shwana / श्वान)", "lord": "Rahu"},
    7: {"deity": "Aditi (Cosmic Mother of Gods)", "symbol": "Bow and Quiver of Arrows", "tree": "Vamsha / Sacred Bamboo (वंश)", "bird": "Swan (Hamsa / हंस)", "animal": "Cat (Marjara / मार्जार)", "lord": "Jupiter (Guru)"},
    8: {"deity": "Brihaspati (Guru of the Devatas)", "symbol": "Cow's Udder / Lotus / Wheel", "tree": "Peepal / Sacred Fig (अश्वत्थ)", "bird": "Sea Crow / जलकाक", "animal": "Goat / Sheep (Aja / अज)", "lord": "Saturn (Shani)"},
    9: {"deity": "Nagas (Divine Serpent Guardians)", "symbol": "Coiled Serpent", "tree": "Nagkeshar / Ashoka (नागकेशर)", "bird": "Small Owl (उलूक)", "animal": "Cat (Marjara / मार्जार)", "lord": "Mercury (Budha)"},
    10: {"deity": "Pitris (Sacred Ancestors & Lineage)", "symbol": "Royal Throne / Palanquin", "tree": "Banyan / Bargad (वटवृक्ष)", "bird": "Male Eagle (चील)", "animal": "Rat (Mushaka / मूषक)", "lord": "Ketu"},
    11: {"deity": "Bhaga (God of Fortune & Prosperity)", "symbol": "Front Legs of Couch / Hammock", "tree": "Palasa / Flame of Forest (पलाश)", "bird": "Falcon (शिशुक)", "animal": "Female Rat (मूषक)", "lord": "Venus (Shukra)"},
    12: {"deity": "Aryaman (God of Honor, Vows & Truth)", "symbol": "Back Legs of Couch / Bed", "tree": "Plaksha / Rudraksha (प्लक्ष)", "bird": "Beetle / Crow", "animal": "Bull / Cow (वृषभ)", "lord": "Sun (Surya)"},
    13: {"deity": "Savitur (Solar Awakening & Energy)", "symbol": "Open Hand / Palm Blessing", "tree": "Chameli / Wild Jasmine (चमेली)", "bird": "Vulture / Hawk", "animal": "Female Buffalo (महिषी)", "lord": "Moon (Chandra)"},
    14: {"deity": "Vishwakarma (Divine Cosmic Architect)", "symbol": "Bright Pearl / Polished Gem", "tree": "Bilva / Bael Patra (बिल्व)", "bird": "Woodpecker (काष्ठकूट)", "animal": "Female Tiger (व्याघ्र)", "lord": "Mars (Mangal)"},
    15: {"deity": "Vayu (God of Cosmic Wind & Breath)", "symbol": "Young Sprout swaying in Wind / Coral", "tree": "Arjuna (अर्जुन वृक्ष)", "bird": "Pigeon / Sparrow (कपोत)", "animal": "Male Buffalo (महिष)", "lord": "Rahu"},
    16: {"deity": "Indragni (Alliance of Power & Fire)", "symbol": "Triumphal Arch / Potter's Wheel", "tree": "Wood Apple / Kaith (कपित्थ)", "bird": "Red Falcon (श्येन)", "animal": "Male Tiger (व्याघ्र)", "lord": "Jupiter (Guru)"},
    17: {"deity": "Mitra (God of Friendship & Devotion)", "symbol": "Staff / Lotus / Arc of Victory", "tree": "Bakula / Maulsari (बकुल)", "bird": "Nightingale / Peacock", "animal": "Female Deer (मृग)", "lord": "Saturn (Shani)"},
    18: {"deity": "Indra (Supreme King of Heaven)", "symbol": "Round Talisman / Royal Umbrella", "tree": "Semal / Silk Cotton (शाल्मली)", "bird": "Brahminy Kite (गरुड)", "animal": "Male Deer (मृग)", "lord": "Mercury (Budha)"},
    19: {"deity": "Nirriti (Goddess of Root Realities)", "symbol": "Tied Bundle of Roots / Elephant Goad", "tree": "Sal / Sarjaka (शाल वृक्ष)", "bird": "Red Vulture (गीध)", "animal": "Male Dog (श्वान)", "lord": "Ketu"},
    20: {"deity": "Apah (Divine Waters of Invincibility)", "symbol": "Winnowing Basket / Fan", "tree": "Ashoka / Rattan (अशोक)", "bird": "Francolin / Hawk", "animal": "Male Monkey (वानर)", "lord": "Venus (Shukra)"},
    21: {"deity": "Vishwadevas (Universal Cosmic Laws)", "symbol": "Elephant's Tusk / Small Cot", "tree": "Jackfruit / Phanas (पनस)", "bird": "Stork / सारस", "animal": "Male Mongoose (नकुल)", "lord": "Sun (Surya)"},
    22: {"deity": "Lord Vishnu (Cosmic Preserver)", "symbol": "Three Footprints / Ear of Listening", "tree": "Aak / Rui / Calotropis (मदार)", "bird": "Francolin / Kapinjala", "animal": "Female Monkey (वानर)", "lord": "Moon (Chandra)"},
    23: {"deity": "Eight Vasus (Elemental Energy Lords)", "symbol": "Mridangam / Drum / Flute", "tree": "Shami / Khejri (शमी वृक्ष)", "bird": "Golden Bee / Peacock", "animal": "Female Lion (सिंह)", "lord": "Mars (Mangal)"},
    24: {"deity": "Varuna (God of Cosmic Oceans & Truth)", "symbol": "Hundred Healers / Empty Circle", "tree": "Kadamba (कदम्ब)", "bird": "Raven / Koel (काक)", "animal": "Female Horse (अश्व)", "lord": "Rahu"},
    25: {"deity": "Aja Ekapada (One-Footed Cosmic Fire)", "symbol": "Two Front Legs of Bed / Crossed Swords", "tree": "Mango / Neem (आम्र/निम्ब)", "bird": "Avocet / Peacock", "animal": "Male Lion (सिंह)", "lord": "Jupiter (Guru)"},
    26: {"deity": "Ahirbudhnya (Serpent of Deep Depths)", "symbol": "Two Back Legs of Bed / Serpent in Water", "tree": "Neem / Pithari (निम्ब)", "bird": "Kotwal / Rainbird", "animal": "Female Cow (गौ)", "lord": "Saturn (Shani)"},
    27: {"deity": "Pushan (Nourisher of Safe Journeys)", "symbol": "Pair of Fish / Small Drum", "tree": "Mahua (मधूक)", "bird": "Demoiselle Crane / Sparrow", "animal": "Female Elephant (हस्तिनी)", "lord": "Mercury (Budha)"}
}

NAKSHATRA_RICH_PROFILES = {
    1: {"core": "Pioneering initiator, rapid problem solver, intuitive healer, and swift executive.", "strengths": "Instant crisis responsiveness, fearless courage to break new ground.", "shadows": "Restlessness, impulsiveness, impatience.", "careers": "Emergency response, tech startups, aviation.", "prediction": "Dynamic early rise, with structural tests leading to institutional authority.", "remedies": "• Chant Om Ashwibhyam Namah 11 times daily."},
    2: {"core": "Enduring moral resilience, deep magnetic charisma, uncompromising principles.", "strengths": "Unshakeable loyalty, turnaround management.", "shadows": "All-or-nothing intensity, stubbornness.", "careers": "Executive management, judicial leadership.", "prediction": "Transformations every 7-9 years leading to permanent asset ownership.", "remedies": "• Recite Maha Mrityunjaya Mantra 11 times daily."},
    3: {"core": "Transformative intellect, razor-sharp discernment, and truth-seeking.", "strengths": "Analytical clarity, technical leadership.", "shadows": "Caustic speech, perfectionism.", "careers": "Defense, software engineering, auditing.", "prediction": "Early disciplined labor lays foundation for senior leadership.", "remedies": "• Offer red sandalwood water to Surya Dev."},
    4: {"core": "Creative charm, material refinement, asset compounding taste.", "strengths": "Patience, wealth cultivation.", "shadows": "Possessiveness, comfort indulgence.", "careers": "Luxury, architecture, finance.", "prediction": "Continuous compounding of assets peaking after age 32.", "remedies": "• Offer raw milk on Shiva Lingam."},
    5: {"core": "Perpetual curiosity, versatile intelligence, communicative agility.", "strengths": "Research instincts, networking ease.", "shadows": "Over-thinking, second-guessing.", "careers": "Telecom, research, journalism.", "prediction": "Exploratory youth yields senior advisory roles.", "remedies": "• Chant Om Somaya Namah 11 times."},
    6: {"core": "Storm-like intellectual intensity, deep emotional breakthrough.", "strengths": "Fearlessness during crises, resilience.", "shadows": "Cynicism, emotional outbursts.", "careers": "Advanced tech, cybersecurity, psychotherapy.", "prediction": "Crises forge exceptional wisdom and sovereignty.", "remedies": "• Chant Om Namah Shivaya 108 times."},
    7: {"core": "Benevolent wisdom, restorative resilience, pedagogical balance.", "strengths": "Bouncing back from setbacks, generous mentorship.", "shadows": "Over-idealism, boundary issues.", "careers": "Higher education, counseling, law.", "prediction": "Steady reputation and enduring prestige.", "remedies": "• Chant Om Brihaspataye Namah 19 times."},
    8: {"core": "Nourishing discipline, institutional loyalty, patience.", "strengths": "Organizational stamina, reliability.", "shadows": "Rigidity, resistance to change.", "careers": "Public administration, banking.", "prediction": "Unstoppable ascent after age 36.", "remedies": "• Water sacred Peepal tree on Saturdays."},
    9: {"core": "Hypnotic psychological insight, strategic shrewdness, tactical mastery.", "strengths": "Reading intentions, sharp intellect.", "shadows": "Suspicion, isolation.", "careers": "Diplomacy, intelligence, defense.", "prediction": "Mastery over complex human systems.", "remedies": "• Offer milk and water to Lord Shiva."},
    10: {"core": "Ancestral authority, regal dignity, traditional pride.", "strengths": "Leadership charisma, legacy respect.", "shadows": "Ego sensitivity, high expectations.", "careers": "Corporate governance, politics.", "prediction": "Strong generational blessings and executive honor.", "remedies": "• Perform Pitru Tarpana."},
    11: {"core": "Charismatic magnetism, social elegance, creative prosperity.", "strengths": "Diplomatic warmth, aesthetic eye.", "shadows": "Procrastination, vanity.", "careers": "Creative direction, PR, luxury branding.", "prediction": "Fortunate social alliances and comfort.", "remedies": "• Chant Om Shukraya Namah 16 times."},
    12: {"core": "Nobility of character, contractual fidelity, truth.", "strengths": "Uncompromising integrity, philanthropy.", "shadows": "Rigid protocols, codependency.", "careers": "Judiciary, international contracts.", "prediction": "Ascent into senior governance and trust.", "remedies": "• Offer kumkum water to morning Sun."},
    13: {"core": "Dexterous problem solver, commercial acumen, analytical eye.", "strengths": "Meticulous craftsmanship, commercial wit.", "shadows": "Nervous anxiety, over-criticalness.", "careers": "Accounting, engineering precision.", "prediction": "Rapid career progression and financial independence.", "remedies": "• Chant Gayatri Mantra 24 times."},
    14: {"core": "Architectural genius, vibrant charisma, aesthetic ambition.", "strengths": "Visual imagination, design proportion.", "shadows": "Vanity, extravagance.", "careers": "Architecture, civil engineering, design.", "prediction": "Pioneering creations gain widespread recognition.", "remedies": "• Recite Hanuman Chalisa."},
    15: {"core": "Independent visionary, diplomatic agility, trade adaptability.", "strengths": "Global perspective, quick commercial instinct.", "shadows": "Commitment hesitation.", "careers": "International commerce, aviation.", "prediction": "Major cross-border expansion after age 30.", "remedies": "• Chant Rahu Beej Mantra 18 times."},
    16: {"core": "Unstoppable ambition, competitive tenacity, goal focus.", "strengths": "Relentless perseverance, strategic alliance.", "shadows": "Envy, exhaustion.", "careers": "Executive leadership, litigation.", "prediction": "Late blooming triumph into executive authority.", "remedies": "• Chant Om Indragni Namah 11 times."},
    17: {"core": "Diplomatic loyalty, devotional warmth, endurance.", "strengths": "Unshakeable friendship, organizational diplomacy.", "shadows": "Suppressing emotional hurt.", "careers": "Diplomacy, HR, counseling.", "prediction": "Long-standing loyal partnerships yield rewards.", "remedies": "• Light mustard oil lamp under Peepal."},
    18: {"core": "Commanding sovereignty, protective courage, senior executive stature.", "strengths": "Natural executive poise, team leadership.", "shadows": "Authoritarian temper.", "careers": "Executive management, police/military.", "prediction": "Rapid ascension into high responsibility.", "remedies": "• Recite Vishnu Sahasranama."},
    19: {"core": "Root-seeking truth inquiry, transformative grit, revolutionary insight.", "strengths": "Fearless examination, philosophical depth.", "shadows": "Destructive anger, cynicism.", "careers": "Engineering research, forensic science.", "prediction": "Radical rebirth leading to self-mastery.", "remedies": "• Chant Om Ketave Namah 17 times."},
    20: {"core": "Invincible optimism, emotional purity, unstoppable perseverance.", "strengths": "Refusal to defeat, creative imagination.", "shadows": "Over-promising, extravagance.", "careers": "Maritime, writing, law.", "prediction": "Celebrated public triumphs and liquid wealth.", "remedies": "• Chant Shri Suktam on Fridays."},
    21: {"core": "Universal integrity, quiet dignity, institutional trust.", "strengths": "Universal respect, unassailable ethics.", "shadows": "Excessive seriousness.", "careers": "Judiciary, auditing, regulatory oversight.", "prediction": "Flawless reputation and generational respect.", "remedies": "• Recite Aditya Hridaya Stotra."},
    22: {"core": "Scholarly listening acumen, tradition preservation, learning capacity.", "strengths": "Oral communication, encyclopedic memory.", "shadows": "Gossip susceptibility, fatigue.", "careers": "Education, corporate counsel, media.", "prediction": "High intellectual distinction and advisory roles.", "remedies": "• Chant Om Namo Bhagavate Vasudevaya."},
    23: {"core": "Elemental rhythm, resource mobilization, wealth mastery.", "strengths": "Timing, athletic coordination, capital mobility.", "shadows": "Greed, bluntness.", "careers": "Real estate, trading, mining.", "prediction": "Monumental capital compounding.", "remedies": "• Recite Hanuman or Kartikeya Stotra."},
    24: {"core": "Scientific curiosity, research intuition, healing mastery.", "strengths": "Unconventional intellect, medical foresight.", "shadows": "Emotional alienation, solitude.", "careers": "Advanced medical tech, pharmacology.", "prediction": "Global recognition for scientific contributions.", "remedies": "• Chant Om Varunaya Namah 11 times."},
    25: {"core": "Fiery ascetic determination, visionary reformist drive.", "strengths": "Transformative vision, penetrating eloquence.", "shadows": "Extreme mood swings, intolerance.", "careers": "Revolutionary tech, crisis leadership.", "prediction": "Commanding visionary authority.", "remedies": "• Chant Rudra Gayatri Mantra 11 times."},
    26: {"core": "Serpentine wisdom, calm benevolence, meditative stamina.", "strengths": "Emotional containment, generational foresight.", "shadows": "Inertia, withdrawal.", "careers": "Asset custody, research, philosophy.", "prediction": "Peaceful life yielding permanent wealth.", "remedies": "• Chant Om Namah Shivaya 108 times."},
    27: {"core": "Nourishing grace, safe guidance, artistic completion.", "strengths": "Empathy, aesthetic talent, traveler's luck.", "shadows": "Over-sensitivity, financial naivety.", "careers": "International travel, diplomacy, arts.", "prediction": "Safe navigation and universal fulfillment.", "remedies": "• Chant Budha Beej Mantra 19 times."}
}

def get_nakshatra_rich_data(star_idx: int):
    return NAKSHATRA_PROFILES.get(star_idx, NAKSHATRA_PROFILES[2]) if 'NAKSHATRA_PROFILES' in globals() else NAKSHATRA_RICH_PROFILES.get(star_idx, NAKSHATRA_RICH_PROFILES[1])

RASHI_RICH_PROFILES = {
    0: {"element": "Fire", "ruler": "Mars", "psychology": "Bold, direct, action-oriented.", "instincts": "Fast emotional recovery, instant reflexes.", "relations": "Fiercely protective and open.", "health": "Watch excess Pitta.", "outlook": "Natural pioneer.", "remedies": "• Offer red sandalwood water to Sun."},
    1: {"element": "Earth", "ruler": "Venus", "psychology": "Deliberate, grounded, stable.", "instincts": "Methodical contemplation.", "relations": "Deeply loyal and affectionate.", "health": "Kapha balance.", "outlook": "Master of compound growth.", "remedies": "• Recite Shri Suktam."},
    2: {"element": "Air", "ruler": "Mercury", "psychology": "Versatile agility, intellect.", "instincts": "Intellectual analysis.", "relations": "Engaging and stimulating.", "health": "Nervous system care.", "outlook": "Thrives in media and commerce.", "remedies": "• Chant Vishnu Sahasranama."},
    3: {"element": "Water", "ruler": "Moon", "psychology": "Deep empathy, subconscious intuition.", "instincts": "Intuitive antennae.", "relations": "Fiercely nurturing.", "health": "Fluid balance vital.", "outlook": "Commands public trust.", "remedies": "• Offer raw milk on Shiva Lingam."},
    4: {"element": "Fire", "ruler": "Sun", "psychology": "Regal dignity, executive pride.", "instincts": "Responds with noble authority.", "relations": "Devoted warm leader.", "health": "High vitality, watch BP.", "outlook": "Attains senior governance.", "remedies": "• Recite Aditya Hridaya Stotra."},
    5: {"element": "Earth", "ruler": "Mercury", "psychology": "Analytical precision, optimization.", "instincts": "Practical problem-solving.", "relations": "Thoughtful and dependable.", "health": "Gut health focus.", "outlook": "Mastery over complex systems.", "remedies": "• Chant Budha Beej Mantra."},
    6: {"element": "Air", "ruler": "Venus", "psychology": "Diplomatic equilibrium, justice.", "instincts": "Balances perspectives.", "relations": "Charming and fair-minded.", "health": "Kidney balance.", "outlook": "Success in legal and alliances.", "remedies": "• Worship Goddess Lakshmi."},
    7: {"element": "Water", "ruler": "Mars", "psychology": "Penetrating depth, grit.", "instincts": "Hyper-vigilant radar.", "relations": "Intensely loyal and private.", "health": "Strong recovery power.", "outlook": "Strategy and crisis turnaround.", "remedies": "• Chant Kartikeya mantras."},
    8: {"element": "Fire", "ruler": "Jupiter", "psychology": "Expansive vision, moral integrity.", "instincts": "Interprets setbacks as milestones.", "relations": "Generous and jovial.", "health": "Liver support active metabolism.", "outlook": "High institutional respect.", "remedies": "• Chant Guru Mantra."},
    9: {"element": "Earth", "ruler": "Saturn", "psychology": "Tactical patience, grit.", "instincts": "Duty and legacy driven.", "relations": "Extremely dependable.", "health": "Joint and bone care.", "outlook": "Sovereign executive leadership.", "remedies": "• Light mustard oil lamp under Peepal."},
    10: {"element": "Air", "ruler": "Saturn", "psychology": "Universal ideals, systems reform.", "instincts": "Objective perspective.", "relations": "Broad-minded and friendly.", "health": "Circulatory system care.", "outlook": "Pioneering breakthroughs.", "remedies": "• Chant Shani Gayatri."},
    11: {"element": "Water", "ruler": "Jupiter", "psychology": "Oceanic intuition, deep wisdom.", "instincts": "Exceptional gut instinct.", "relations": "Deeply devoted and romantic.", "health": "Lymphatic balance.", "outlook": "Creative imagination and wisdom.", "remedies": "• Chant Om Namo Bhagavate Vasudevaya."}
}

def get_rashi_rich_data(rashi_idx: int):
    return RASHI_RICH_PROFILES.get(rashi_idx, RASHI_RICH_PROFILES[0])

LAGNA_RICH_PROFILES = {
    0: {"element": "Fire", "lord": "Mars", "constitution": "High Pitta, athletic.", "persona": "Direct, confident, bold.", "life_arc": "Pioneering entrepreneurship.", "remedies": "• Offer sandalwood water to Sun."},
    1: {"element": "Earth", "lord": "Venus", "constitution": "Solid stamina, calm.", "persona": "Composed, patient dignity.", "life_arc": "Compounding permanent wealth.", "remedies": "• Apply white sandalwood."},
    2: {"element": "Air", "lord": "Mercury", "constitution": "Quick reflexes, agile.", "persona": "Articulate, witty.", "life_arc": "Commercial and intellectual distinction.", "remedies": "• Chant Vishnu Sahasranama."},
    3: {"element": "Water", "lord": "Moon", "constitution": "Receptive, sensitive.", "persona": "Empathetic, intuitive.", "life_arc": "Public institutional command.", "remedies": "• Offer clean water to Shiva."},
    4: {"element": "Fire", "lord": "Sun", "constitution": "Regal posture, vital.", "persona": "Sovereign, commanding.", "life_arc": "Administrative authority.", "remedies": "• Perform Surya Namaskar."},
    5: {"element": "Earth", "lord": "Mercury", "constitution": "Structured, precise.", "persona": "Analytical, prepared.", "life_arc": "Operational system mastery.", "remedies": "• Chant Budha Beej Mantra."},
    6: {"element": "Air", "lord": "Venus", "constitution": "Balanced, refined.", "persona": "Diplomatic, calm.", "life_arc": "Institutional and legal balance.", "remedies": "• Worship Lakshmi."},
    7: {"element": "Water", "lord": "Mars", "constitution": "Intense stamina.", "persona": "Authoritative, resilient.", "life_arc": "Transformative executive power.", "remedies": "• Recite Hanuman Chalisa."},
    8: {"element": "Fire", "lord": "Jupiter", "constitution": "Tall, dignified.", "persona": "Inspiring, scholarly.", "life_arc": "Senior institutional leadership.", "remedies": "• Apply yellow sandalwood."},
    9: {"element": "Earth", "lord": "Saturn", "constitution": "Austere, steady.", "persona": "Sober, reliable.", "life_arc": "Permanent institutional foundations.", "remedies": "• Light lamp under Peepal."},
    10: {"element": "Air", "lord": "Saturn", "constitution": "Cerebral, sensitive.", "persona": "Egalitarian, visionary.", "life_arc": "Technological systems reform.", "remedies": "• Chant Shani Gayatri."},
    11: {"element": "Water", "lord": "Jupiter", "constitution": "Gentle, calm.", "persona": "Philosophical, empathetic.", "life_arc": "Spiritual tranquility and peace.", "remedies": "• Chant Vasudevaya mantra."}
}

def get_lagna_rich_data(lagna_idx: int):
    return LAGNA_RICH_PROFILES.get(lagna_idx, LAGNA_RICH_PROFILES[6])

# ==============================================================================
# EXHAUSTIVE SHANI PAYA & SADE SATI ENCYCLOPEDIA
# ==============================================================================
SHANI_PAYA_ENCYCLOPEDIA = {
    "Silver": {
        "title": "🥈 Rajat Paya (Silver Feet / चाँदी का पाया)",
        "grade": "Supreme Auspiciousness (अति शुभ फलदायी)",
        "tone": "Divine Cushion, Financial Liquidity & Reputational Growth",
        "houses": "2nd, 5th, or 9th house from natal Moon",
        "health": "Robust physical vitality, restful sleep patterns, strong immunity, and quick recuperation from minor illnesses.",
        "wealth": "Exceptional capital expansion, stabilization of liquid cash flow, recovery of long-pending debts, and lucrative property compounding.",
        "family": "Harmonious domestic environment, supportive spouse, celebration of auspicious family events, and peace with children.",
        "loan": "Seamless debt clearance, easy approvals for restructuring loans at lower interest rates, and immunity against heavy liabilities.",
        "partner": "Highly cooperative business partners and devoted life partner; commercial agreements flow smoothly with mutual trust.",
        "luck": "Favorable wind in long-term ventures, unexpected windfall gains, and strong alignment of mentors and destiny.",
        "career": "Steady executive advancement, elevation in institutional rank, favorable rapport with senior leadership, and public recognition.",
        "protocol": "Wear a solid pure silver square or ring on the little finger, offer raw cow's milk mixed with water on a Shiva Lingam on Mondays."
    },
    "Copper": {
        "title": "🥉 Tamra Paya (Copper Feet / तांबे का पाया)",
        "grade": "Favorable & Productive (शुभ फलदायी)",
        "tone": "Laborious Progress, Competitive Mastery & Sustained Effort",
        "houses": "3rd, 7th, or 10th house from natal Moon",
        "health": "Good stamina driven by focused effort; watch out for elevated metabolic heat (Pitta) and muscular tension from overwork.",
        "wealth": "Wealth grows steadily through direct exertion, disciplined commercial ventures, and enterprise expansion rather than lottery windfalls.",
        "family": "Supportive domestic sphere where hard work is appreciated; requires conscious time-allocation to prevent work-life imbalance.",
        "loan": "Loans are successfully utilized for productive asset creation (e.g., machinery or real estate) with reliable repayment streams.",
        "partner": "Business partnerships thrive through shared ambition and grit; spouse acts as a strong operational sounding board.",
        "luck": "Luck favors the diligent. Persistence through competitive hurdles unlocks major triumphs.",
        "career": "Dominance over competitors, successful project turnarounds, expansion of client networks, and triumph in challenging negotiations.",
        "protocol": "Drink water stored overnight in a pure copper vessel, donate jaggery and roasted chickpeas on Tuesdays, maintain strict truthfulness."
    },
    "Gold": {
        "title": "🥇 Swarna Paya (Gold Feet / सोने का पाया)",
        "grade": "Testing & Demanding (कठिन एवं संघर्षमय)",
        "tone": "Ego Restructuring, Expense Spikes & Need for Extreme Prudence",
        "houses": "1st, 6th, or 11th house from natal Moon",
        "health": "Nervous exhaustion, occasional sleep disruption, and sensitivity to stress; requires strict adherence to restorative sleep and breathwork.",
        "wealth": "Unforeseen expenses, family commitments consuming cash reserves, and slow returns on speculative ventures. Demands strict budgetary austerity.",
        "family": "Ego clashes or communication friction with relatives; requires active listening and emotional humility to maintain peace.",
        "loan": "Avoid taking new unsecured loans or lending money to peers. Refinance existing liabilities with caution.",
        "partner": "Partnerships undergo stress due to ego friction or misaligned expectations. Keep all agreements transparent and documented.",
        "luck": "Luck requires careful navigation; avoid unhedged shortcuts or speculative gambling.",
        "career": "Ego disputes with seniors or partners, misunderstandings regarding credit, and heightened professional scrutiny.",
        "protocol": "Avoid excessive yellow gold jewelry; wear clean silver; donate yellow lentils or turmeric to temple priests on Thursdays; cultivate humility."
    },
    "Iron": {
        "title": "🪙 Loha Paya (Iron Feet / लोहे का पाया)",
        "grade": "Heavy Crucible & High Friction (अति कठिन / संघर्षमय)",
        "tone": "Karmic Weight, Heavy Responsibilities & Constitutional Testing",
        "houses": "4th, 8th, or 12th house from natal Moon",
        "health": "Prone to joint stiffness, lower back vulnerability, and sluggish digestion. Demands regular walking, clean diet, and early bedtime.",
        "wealth": "Sudden financial leaks, legal or administrative hurdles, and stalled asset liquidity. Strictly avoid leveraged bets or lending money.",
        "family": "Heavy family responsibilities testing your patience; domestic harmony requires conscious emotional restraint and quiet tolerance.",
        "loan": "High risk of debt entanglement if living beyond means. Strict moratorium on new liabilities is mandatory.",
        "partner": "Business and personal partners may face external pressures; maintain clear boundaries and avoid joint financial risks.",
        "luck": "Testing phase where destiny rewards patient endurance rather than aggressive gambles.",
        "career": "Strenuous workloads, organizational restructuring, delays in promotions, and demanding subordinate management.",
        "protocol": "Light a mustard-oil lamp under a sacred Peepal tree every Saturday evening; feed black dogs or crows; donate iron items or black sesame."
    }
}

SADE_SATI_PHASE_ENCYCLOPEDIA = {
    1: {
        "phase_name": "Phase 1: Rising Phase (Aarohi Charana / 12th House Transit)",
        "focus": "Subconscious Cleansing, Isolation, Expense Spikes & Detachment",
        "health": "Sleep fragmentation, eye strain, joint fatigue in feet/ankles, and vulnerability to psychosomatic stress.",
        "wealth": "High unbudgeted expenditures, investments in foreign affairs or healthcare, and necessity to plug financial leaks. Not favorable for speculative risks.",
        "family": "Temporary physical separation from family due to travel or relocation; emotional introspection may cause temporary distance.",
        "loan": "Potential outflow for settling past obligations or medical/travel expenses. Avoid taking fresh unhedged credit.",
        "partner": "Partners may be absorbed in their own challenges; maintain transparent dialogue to prevent miscommunication.",
        "luck": "External luck is muted in favor of inner spiritual and psychological preparation.",
        "career": "Relocation, foreign assignments, working behind the scenes, or navigating corporate restructuring. Recognition may feel delayed despite intense efforts.",
        "remedy": "Recite Maha Mrityunjaya Mantra 108 times at twilight; donate dark blankets to homeless individuals; avoid major financial commitments during late night hours."
    },
    2: {
        "phase_name": "Phase 2: Peak Janma Shani (Core Transit / 1st House Over Natal Moon)",
        "focus": "Identity Rebirth, Character Crucible, Physical Endurance & Leadership",
        "health": "Demands strict physical discipline, spinal and joint care, adequate hydration, and emotional containment to prevent burnout.",
        "wealth": "Cash flow requires meticulous cash-reserve management. Assets are restructured into solid, unshakeable foundations rather than liquid luxuries.",
        "family": "Testing phase for domestic harmony; patience and ego surrender prevent domestic friction from escalating.",
        "loan": "Strictly avoid speculative loans or signing surety for others. Manage existing debt conservatively.",
        "partner": "Intense testing ground for marital and business partnerships. Mutual commitment is forged through shared adversity.",
        "luck": "Destiny places heavy responsibilities on your shoulders; rewards come strictly through unyielding integrity.",
        "career": "Massive increase in executive responsibilities. You become the reliable pillar managing crises, yet must endure high scrutiny and professional solitude.",
        "remedy": "Chant Shani Beej Mantra 108 times on Saturdays; offer water with blue flowers to Lord Shiva; treat factory workers and subordinates with deep respect."
    },
    3: {
        "phase_name": "Phase 3: Setting Phase (Avarohi Charana / 2nd House Transit)",
        "focus": "Asset Consolidation, Speech Discipline, Family Healing & Permanent Rewards",
        "health": "Teeth, throat, vocal cord, and dietary adjustments. Restoring nutritional balance and cellular vitality.",
        "wealth": "Recovery of financial momentum, accumulation of permanent tangible wealth, stabilization of family estates, and steady cash-flow turnaround.",
        "family": "Reconciliation, celebration of family milestones, and peaceful domestic bonding.",
        "loan": "Debts are steadily paid off, leaving you with clean balance sheets and strengthened creditworthiness.",
        "partner": "Business and life partners bring renewed stability, shared financial planning, and mutual growth.",
        "luck": "Cosmic headwinds turn into favorable tailwinds as past efforts begin to bear tangible fruit.",
        "career": "Consolidation of executive authority, reaping the enduring benefits of hard labor endured during Phase 1 & 2, and achieving long-term respect.",
        "remedy": "Practice strict honesty and avoid harsh speech; drink water from a silver cup; donate whole black urad dal and mustard oil on Saturdays."
    }
}

DHAIYA_ENCYCLOPEDIA = {
    4: {
        "name": "Kantaka Shani (4th House Dhaiya / Ardhashtama Shani)",
        "focus": "Domestic Equilibrium, Property Challenges & Work-Life Balance",
        "health": "Chest, respiratory, and heart-rate balance under domestic or work pressure.",
        "wealth": "Focus on property maintenance expenses and consolidating real estate holdings.",
        "family": "Emotional friction at home, restlessness regarding living arrangements, and attention needed toward maternal health.",
        "loan": "Manage property-related mortgages or home loans with prudent budgeting.",
        "partner": "Domestic stress can spill into partnership dynamics; practice conscious patience.",
        "luck": "Shifts focus from external expansion to securing foundational base and home front.",
        "career": "Strenuous workplace politics, change of department or relocation, and balancing heavy domestic needs with professional demands.",
        "remedy": "Serve and respect your mother; light a mustard-oil lamp under a Peepal tree on Saturdays; keep living space clean and clutter-free."
    },
    8: {
        "name": "Ashtama Shani (8th House Dhaiya / High Friction)",
        "focus": "Deep Transformation, Crisis Mitigation, Health Vigilance & Karmic Debts",
        "health": "Avoid fatigue, check chronic symptoms, and maintain daily walking discipline.",
        "wealth": "Avoid unhedged market leverage, speculative schemes, and unsecured loans.",
        "family": "Elevated vulnerability to stress; keep family communications transparent and calm.",
        "loan": "High caution required against sudden financial commitments or guarantor obligations.",
        "partner": "Unforeseen partner issues require calm mediation and legal/financial prudence.",
        "luck": "Testing cycle requiring spiritual introspection and risk minimization.",
        "career": "Unexpected obstacles in career progression, legal or tax audits, and necessity for absolute transparency in business contracts.",
        "remedy": "Recite Hanuman Chalisa twice daily; avoid risky driving late at night; strictly abstain from speculative financial gambling."
    }
}

def calculate_shani_paya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    house_diff = (moon_rashi_idx - saturn_transit_rashi_idx) % 12 + 1
    m_name = RASHIS[moon_rashi_idx].split()[0]
    
    if house_diff in [2, 5, 9]:
        metal = "Silver"
    elif house_diff in [3, 7, 10]:
        metal = "Copper"
    elif house_diff in [1, 6, 11]:
        metal = "Gold"
    else:
        metal = "Iron"

    ency = SHANI_PAYA_ENCYCLOPEDIA[metal]
    
    return {
        "paya": ency["title"],
        "metal": metal,
        "status": ency["grade"],
        "tone": ency["tone"],
        "houses": ency["houses"],
        "psychology": ency["psychology"],
        "health": ency["health"],
        "wealth": ency["wealth"],
        "family": ency["family"],
        "loan": ency["loan"],
        "partner": ency["partner"],
        "luck": ency["luck"],
        "career": ency["career"],
        "protocol": ency["protocol"],
        "desc": f"Saturn is currently transiting the {house_diff}th house relative to your {m_name} Moon, arriving on {metal} Feet ({ency['title'].split('(')[1].split('/')[0].strip()}).",
        "timeline": "29 March 2025 – 23 February 2028 (Saturn in Pisces / Meena Rashi)"
    }

def calculate_shani_sadesati_dhaiya(moon_rashi_idx: int, saturn_transit_rashi_idx: int) -> dict:
    diff = (saturn_transit_rashi_idx - moon_rashi_idx) % 12
    m_name = RASHIS[moon_rashi_idx].split()[0]

    rashi_12th = RASHIS[(moon_rashi_idx - 1) % 12].split()[0]
    rashi_1st = m_name
    rashi_2nd = RASHIS[(moon_rashi_idx + 1) % 12].split()[0]

    if diff == 11:
        p_info = SADE_SATI_PHASE_ENCYCLOPEDIA[1]
        return {
            "active": True,
            "status_title": p_info["phase_name"],
            "phase_num": 1,
            "focus": p_info["focus"],
            "health": p_info["health"],
            "wealth": p_info["wealth"],
            "family": p_info["family"],
            "loan": p_info["loan"],
            "partner": p_info["partner"],
            "luck": p_info["luck"],
            "career": p_info["career"],
            "mental": p_info["mental"],
            "remedy": p_info["remedy"],
            "impact": f"Saturn currently transits your 12th house in {RASHIS[saturn_transit_rashi_idx].split()[0]} relative to your {m_name} Moon. Prompts deep restructuring of personal priorities, elimination of wasteful financial habits, and subconscious purification.",
            "dates": "Active Phase (29 March 2025 – 23 February 2028)",
            "phase_1_active": True, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 0:
        p_info = SADE_SATI_PHASE_ENCYCLOPEDIA[2]
        return {
            "active": True,
            "status_title": p_info["phase_name"],
            "phase_num": 2,
            "focus": p_info["focus"],
            "health": p_info["health"],
            "wealth": p_info["wealth"],
            "family": p_info["family"],
            "loan": p_info["loan"],
            "partner": p_info["partner"],
            "luck": p_info["luck"],
            "career": p_info["career"],
            "mental": p_info["mental"],
            "remedy": p_info["remedy"],
            "impact": f"Saturn transits directly over your natal Moon in {m_name} (Janma Shani). This is the supreme crucible of character, requiring physical stamina, ego dissolution, leadership responsibility, and unwavering moral grounding.",
            "dates": "Active Peak Phase (29 March 2025 – 23 February 2028)",
            "phase_1_active": False, "phase_2_active": True, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 1:
        p_info = SADE_SATI_PHASE_ENCYCLOPEDIA[3]
        return {
            "active": True,
            "status_title": p_info["phase_name"],
            "phase_num": 3,
            "focus": p_info["focus"],
            "health": p_info["health"],
            "wealth": p_info["wealth"],
            "family": p_info["family"],
            "loan": p_info["loan"],
            "partner": p_info["partner"],
            "luck": p_info["luck"],
            "career": p_info["career"],
            "mental": p_info["mental"],
            "remedy": p_info["remedy"],
            "impact": f"Saturn transits the 2nd house from your {m_name} Moon in {RASHIS[saturn_transit_rashi_idx].split()[0]}. As Sade Sati draws toward conclusion, hard lessons solidify into permanent wealth consolidation, stabilized speech, and generational assets.",
            "dates": "Active Concluding Phase (29 March 2025 – 23 February 2028)",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": True,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 3:
        dh_info = DHAIYA_ENCYCLOPEDIA[4]
        return {
            "active": True,
            "status_title": dh_info["name"],
            "phase_num": 4,
            "focus": dh_info["focus"],
            "health": dh_info["health"],
            "wealth": "Focus on property maintenance and real estate asset consolidation.",
            "family": dh_info["family"],
            "loan": "Manage property-related mortgages or home loans with prudent budgeting.",
            "partner": dh_info["partner"],
            "luck": "Shifts focus from external expansion to securing foundational base and home front.",
            "career": dh_info["career"],
            "mental": dh_info["mental"],
            "remedy": dh_info["remedy"],
            "impact": f"Saturn transits your 4th house from {m_name} Moon in {RASHIS[saturn_transit_rashi_idx].split()[0]}. Focus on home stability, vehicle care, maternal health, and inner peace.",
            "dates": "Active 2.5-Year Dhaiya (2025 – 2028)",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    elif diff == 7:
        dh_info = DHAIYA_ENCYCLOPEDIA[8]
        return {
            "active": True,
            "status_title": dh_info["name"],
            "phase_num": 8,
            "focus": dh_info["focus"],
            "health": dh_info["health"],
            "wealth": "Avoid unhedged market leverage, speculative schemes, and unsecured loans.",
            "family": dh_info["family"],
            "loan": "High caution required against sudden financial commitments or guarantor obligations.",
            "partner": dh_info["partner"],
            "luck": "Testing cycle requiring spiritual introspection and risk minimization.",
            "career": dh_info["career"],
            "mental": dh_info["mental"],
            "remedy": dh_info["remedy"],
            "impact": f"Saturn transits your 8th house from {m_name} Moon in {RASHIS[saturn_transit_rashi_idx].split()[0]}. Demands disciplined health habits, careful driving, transparent financial ethics, and spiritual introspection.",
            "dates": "Active 2.5-Year Dhaiya (2025 – 2028)",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }
    else:
        return {
            "active": False,
            "status_title": "No Active Sade Sati or Dhaiya",
            "phase_num": 0,
            "focus": "Unimpeded Progress & Expansion",
            "health": "Standard biological stamina.",
            "wealth": "Standard financial liquidity based on active Dasha periods.",
            "family": "Harmonious domestic relations.",
            "loan": "Normal credit management.",
            "partner": "Stable partnership dynamics.",
            "luck": "Favorable planetary support.",
            "career": "Constructive career growth with minimal Saturnic friction.",
            "mental": "Mental clarity is high; favorable for launching new enterprises.",
            "remedy": "Continue daily prayers and ethical business practices.",
            "impact": f"Saturn is currently in Pisces ({RASHIS[saturn_transit_rashi_idx].split()[0]}), placing it in an auspicious or neutral {((saturn_transit_rashi_idx - moon_rashi_idx) % 12) + 1}th house relative to your {m_name} Moon.",
            "dates": "No Current Friction Cycle",
            "phase_1_active": False, "phase_2_active": False, "phase_3_active": False,
            "rashi_12th": rashi_12th, "rashi_1st": rashi_1st, "rashi_2nd": rashi_2nd
        }

def calculate_shani_vahan(birth_star_idx: int, transit_moon_star_idx: int) -> dict:
    raw_val = (birth_star_idx * 4 + transit_moon_star_idx) % 9
    rem = 9 if raw_val == 0 else raw_val
    return SHANI_VAHANS.get(rem, SHANI_VAHANS[9])

def reduce_to_single_digit(num: int) -> int:
    while num > 9:
        num = sum(int(ch) for ch in str(num))
    return num if num > 0 else 9

def calculate_numerology(dob: datetime.date, name: str):
    mulank = reduce_to_single_digit(dob.day)
    full_date_sum = dob.day + dob.month + dob.year
    bhagyank = reduce_to_single_digit(full_date_sum)
    cleaned_name = "".join(ch for ch in name.upper() if ch.isalpha())
    namank_val = sum(CHALDEAN_MAP.get(ch, 0) for ch in cleaned_name)
    namank = reduce_to_single_digit(namank_val) if namank_val > 0 else 1
    return mulank, bhagyank, namank

def get_personal_day_vibe(dob: datetime.date, target_date: datetime.date, lang: str = "en") -> dict:
    personal_year = reduce_to_single_digit(dob.day + dob.month + target_date.year)
    personal_day = reduce_to_single_digit(personal_year + target_date.month + target_date.day)
    planet_info = NUM_PLANET_NAMES.get(personal_day, {}).get(lang, f"Number {personal_day}")
    return {
        "number": personal_day,
        "planet": planet_info,
        "desc": f"Personal Day {personal_day} resonates with {planet_info} cosmic frequency."
    }

def get_numerology_life_domains(mulank: int, bhagyank: int, namank: int, lang: str = "en") -> dict:
    p_m = NUM_PLANET_NAMES.get(mulank, {}).get(lang, f"Planet {mulank}")
    p_b = NUM_PLANET_NAMES.get(bhagyank, {}).get(lang, f"Planet {bhagyank}")
    return {
        "career_title": "💼 Career Trajectory & Executive Ambition",
        "career_desc": f"The dynamic synthesis of Driver {mulank} ({p_m}) and Conductor {bhagyank} ({p_b}) creates a powerhouse combination of strategic vision and courageous execution.",
        "wealth_title": "💰 Wealth Dynamics & Financial Mastery",
        "wealth_desc": "Your vibrational alignment supports structured compounding and tangible asset security. Avoid volatile speculative gambling.",
        "rel_title": "❤️ Relationships & Interpersonal Dynamics",
        "rel_desc": "You value authentic, pretense-free connections. Practicing active listening during critical discussions will keep family and professional bonds deeply harmonious.",
        "health_title": "🌿 Health, Vitality & Holistic Bio-Rhythms",
        "health_desc": "You possess strong physical endurance. Balance mental momentum with regular hydration, structured rest, and evening breathwork.",
        "luck_title": "🍀 Harmonic Lucky Attributes",
        "lucky_num": f"{mulank}, {bhagyank}, {(mulank + bhagyank) % 9 or 9}",
        "avoid_num": "2, 8 (Exercise tactful patience)",
        "lucky_days": "Tuesday, Thursday, and Sunday",
        "lucky_colors": "Electric Blue, Slate Gray, Rich Amber Gold",
        "lucky_dir": "South and North-East"
    }

def get_numerology_avoidance(mulank: int, bhagyank: int, lang: str = "en") -> dict:
    return {
        "avoid_title": "⚠️ Cosmic Caution & Avoidance Matrix",
        "avoid_numbers": "2, 8 (Challenging karmic tests)",
        "avoid_colors": "Pitch Black, Mud Brown, Dirty Dark Indigo",
        "avoid_days": "Saturday twilight & Monday late nights (for high-stakes launches)",
        "avoid_directions": "South-West during rest",
        "cautions": [
            "Avoid verbal agreements without clearly documented written contracts.",
            "Never commit to capital investments or legal deeds during sudden anger or peak haste.",
            "Strictly avoid speculative options trading and get-rich-quick shortcuts.",
            "Eliminate tangled electronic cables and broken appliances from your primary workspace.",
            "Refrain from purchasing iron hardware or heavy scrap on Saturdays."
        ]
    }

def calculate_sun_times(date_obj: datetime.date, lat: float, lon: float):
    day_of_year = date_obj.timetuple().tm_yday
    decl = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    lat_rad = math.radians(lat)
    decl_rad = math.radians(decl)
    
    cos_ha = -math.tan(lat_rad) * math.tan(decl_rad)
    cos_ha = max(-1.0, min(1.0, cos_ha))
    ha_deg = math.degrees(math.acos(cos_ha))
    
    b = math.radians((360 / 365) * (day_of_year - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    
    time_corr = 4 * (lon - 82.5) + eot
    solar_noon_minutes = 720 - time_corr
    half_day_minutes = (ha_deg / 15.0) * 60.0
    
    sr_minutes = solar_noon_minutes - half_day_minutes
    ss_minutes = solar_noon_minutes + half_day_minutes
    
    base_dt = datetime.datetime.combine(date_obj, datetime.time.min)
    return base_dt + datetime.timedelta(minutes=sr_minutes), base_dt + datetime.timedelta(minutes=ss_minutes)

def calculate_daily_muhurtas(date_obj: datetime.date, lat: float, lon: float):
    sunrise, sunset = calculate_sun_times(date_obj, lat, lon)
    day_duration = (sunset - sunrise).total_seconds()
    
    muhurta_duration = day_duration / 15.0
    abhijit_start = sunrise + datetime.timedelta(seconds=7 * muhurta_duration)
    abhijit_end = sunrise + datetime.timedelta(seconds=8 * muhurta_duration)
    
    eighth_part = day_duration / 8.0
    wday = date_obj.weekday()
    rahu_parts = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
    yamaganda_parts = {0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6, 6: 5}
    
    r_idx = rahu_parts.get(wday, 6)
    rahu_start = sunrise + datetime.timedelta(seconds=(r_idx - 1) * eighth_part)
    rahu_end = sunrise + datetime.timedelta(seconds=r_idx * eighth_part)
    
    y_idx = yamaganda_parts.get(wday, 1)
    yama_start = sunrise + datetime.timedelta(seconds=(y_idx - 1) * eighth_part)
    yama_end = sunrise + datetime.timedelta(seconds=y_idx * eighth_part)
    
    brahma_start = sunrise - datetime.timedelta(minutes=96)
    brahma_end = sunrise - datetime.timedelta(minutes=48)
    
    return {
        "sunrise": sunrise,
        "sunset": sunset,
        "abhijit": (abhijit_start, abhijit_end),
        "rahu": (rahu_start, rahu_end),
        "yamaganda": (yama_start, yama_end),
        "brahma": (brahma_start, brahma_end)
    }

def get_current_nakshatra_window(target_ist_dt: datetime.datetime):
    utc_dt = target_ist_dt - datetime.timedelta(hours=5, minutes=30)
    current_lon = get_sidereal_moon_longitude(utc_dt)
    span = 360.0 / 27.0
    star_idx = max(1, min(27, int(current_lon / span) + 1))
    start_lon = (star_idx - 1) * span

    deg_from_start = (current_lon - start_lon) % span
    deg_to_end = span - deg_from_start

    hours_since_start = max(0.1, deg_from_start / 0.55)
    hours_to_end = max(0.1, deg_to_end / 0.55)

    start_dt = target_ist_dt - datetime.timedelta(hours=hours_since_start)
    end_dt = target_ist_dt + datetime.timedelta(hours=hours_to_end)

    return star_idx, start_dt, end_dt

def get_7_day_moon_transits(start_ist_dt: datetime.datetime, birth_star_idx: int):
    transits = []
    curr_t = start_ist_dt
    for i in range(7):
        target_t = curr_t + datetime.timedelta(days=i)
        star_idx, s_time, e_time = get_current_nakshatra_window(target_t)
        
        offset = (star_idx - birth_star_idx) % 9
        nav_name, icon, quality = NAVTARA_NAMES[offset]
        vahan_rem = (birth_star_idx * 4 + star_idx) % 9
        vahan_rem = 9 if vahan_rem == 0 else vahan_rem
        vahan_info = SHANI_VAHANS.get(vahan_rem, SHANI_VAHANS[9])
        
        transits.append({
            "day_num": i + 1,
            "date": target_t.date(),
            "date_str": target_t.strftime("%a, %d %b"),
            "star_idx": star_idx,
            "star_name": NAKSHATRAS[star_idx - 1],
            "nav_name": nav_name,
            "nav_offset": offset,
            "icon": icon,
            "quality": quality,
            "vahan": vahan_info["name"],
            "vahan_type": vahan_info["type"],
            "start_str": s_time.strftime("%a, %d %b %I:%M %p"),
            "end_str": e_time.strftime("%a, %d %b %I:%M %p IST")
        })
    return transits

def get_detailed_day_insights(offset: int, vahan_dict: dict, current_star_name: str, p_day: dict):
    is_positive = offset in [1, 3, 5, 7, 8]
    is_extreme_friction = offset in [2, 4, 6]

    theme_map = {
        0: ("Identity Renewal & Foundation (Janma)", "Mind feels intensely sensitive, reflective, and connected to root desires. Vital for self-evaluation rather than high-stakes friction.", "Focus on foundational planning, health diagnostics, routine execution, and self-care.", "Avoid impulsive career shifts, major loans, or initiating confrontational meetings."),
        1: ("Accelerated Wealth & Liquidity (Sampat)", "High financial synchronicity. Cosmic doors open for asset acquisition, high-ticket proposals, and capital expansion.", "Sign partnership deeds, initiate investments, submit proposals, and collect receivables.", "Avoid complacency; strike while the cosmic window is open."),
        2: ("Friction Shield & Crisis Deflection (Vipat)", "Elevated environmental resistance. Unforeseen delays, technological glitches, and administrative roadblocks.", "Conduct defensive administrative checks, review error margins, and maintain low profile.", "Strictly avoid speculative bets, aggressive confrontations, or signing irreversible contracts."),
        3: ("Peace, Health & Structural Security (Kshema)", "Sustaining, healing vibrational flow. Excellent for domestic harmony, property matters, and emotional equilibrium.", "Finalize contracts, purchase durable goods, enjoy family gatherings, and resolve old disputes.", "Avoid over-exhaustion; maintain balanced dietary and rest rhythms."),
        4: ("Overcoming Roadblocks & Opposition (Pratyari)", "Testing of diplomatic acumen. Hidden opposition, critical auditors, or challenging counterparties may emerge.", "Gather airtight evidence, exercise extreme tactical patience, and listen twice as much as you speak.", "Avoid losing temper in official communications; do not escalate legal friction."),
        5: ("Strategic Mastery & Manifestation (Sadhana)", "Golden window for high-order accomplishments. Mental faculties are razor sharp for complex engineering, strategy, and execution.", "Launch critical campaigns, undertake complex technical projects, negotiate promotions, and study.", "Do not waste this high-frequency window on superficial trivialities."),
        6: ("High Friction Zone & Defensive Prudence (Vadha)", "Heaviest energetic friction. Physical vitality and mental stamina feel vulnerable to depletion.", "Keep a minimalist agenda, practice quiet perseverance, and double-check all critical data.", "Do not drive long distances late at night; postpone major financial commitments."),
        7: ("Cooperative Harmony & Alliance Building (Mitra)", "Pleasurable, cordial cosmic atmosphere. High responsiveness from peers, mentors, and prospective partners.", "Network with key decision-makers, resolve estrangements, host important discussions, and socialize.", "Avoid being overly accommodating; ensure business boundaries remain firm."),
        8: ("Supreme Synergy & Pinnacle Triumph (Ati-Mitra)", "Peak celestial resonance. The rarest, most fruitful timing window for long-term victories and monumental leaps.", "Pitch high-value clients, launch new business verticals, close major property deals, and celebrate.", "Do not doubt yourself; step forward with unwavering confidence.")
    }

    theme_title, theme_desc, opportunities, hazards = theme_map.get(offset, theme_map[0])

    if is_positive:
        remedy_mantra = "ॐ नमो भगवते वासुदेवाय (Om Namo Bhagavate Vasudevaya) - 11 times in morning facing East."
        remedy_charity = "Offer sweet yellow fruits or milk sweets to elders, mentors, or temples to seal cosmic prosperity."
        remedy_action = "Wear light, vibrant shades (Coral Red, Amber Gold, or Electric White) to broadcast peak resonance."
    elif is_extreme_friction:
        remedy_mantra = "ॐ नमः शिवाय (Om Namah Shivaya) or Maha Mrityunjaya Mantra - 108 times at twilight facing North."
        remedy_charity = "Feed stray dogs, crows, or donate dark grains/black sesame to pacify planetary friction."
        remedy_action = "Apply white sandalwood paste to forehead/wrists; maintain 15 minutes of silent mindfulness (Mauna) before sunset."
    else:
        remedy_mantra = "ॐ सूर्याय नमः (Om Suryaya Namah) - Offer pure water in a copper vessel to morning Sun."
        remedy_charity = "Feed green grass or fresh spinach to cows to enhance cellular vitality and grounding."
        remedy_action = "Drink warm water from a silver cup; strictly abstain from fast food and erratic sleep patterns."

    return {
        "theme_title": theme_title,
        "theme_desc": theme_desc,
        "opportunities": opportunities,
        "hazards": hazards,
        "remedy_mantra": remedy_mantra,
        "remedy_charity": remedy_charity,
        "remedy_action": remedy_action
    }


# ==============================================================================
# 9 NAVAGRAHA BEEJ MANTRAS
# ==============================================================================
NAVAGRAHA_BEEJ_MANTRAS = {
    "Surya (Sun / सूर्य) Beej Mantra": {
        "sanskrit": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः॥",
        "translit": "Om Hraam Hreem Hroum Sah Suryaya Namah ||",
        "count": 7000,
        "deity": "Surya Bhagwan",
        "meaning": "Salutations to the supreme solar intelligence that illuminates consciousness, activates vitality, and dispels darkness.",
        "rules": "• Best chanted at sunrise facing East.\n• Auspicious day: Sunday (रविवार).\n• Mala: Ruby (Manikya) or Red Sandalwood.\n• Bestows: Authority, vitality, heart health, leadership, and soul power."
    },
    "Chandra (Moon / चन्द्र) Beej Mantra": {
        "sanskrit": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः॥",
        "translit": "Om Shraam Shreem Shroum Sah Chandramase Namah ||",
        "count": 11000,
        "deity": "Chandra Deva",
        "meaning": "Salutations to the cooling lunar frequency that governs the mind, emotions, and subtle biological fluids.",
        "rules": "• Best chanted in the evening or twilight facing North-West.\n• Auspicious day: Monday (सोमवार).\n• Mala: White Pearl (Moti) or Sphatik.\n• Bestows: Emotional tranquility, mental composure, hormonal balance, and intuitive clarity."
    },
    "Mangal (Mars / मंगल) Beej Mantra": {
        "sanskrit": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः॥",
        "translit": "Om Kraam Kreem Kroum Sah Bhaumaya Namah ||",
        "count": 10000,
        "deity": "Mangal Deva / Kartikeya",
        "meaning": "Salutations to the fiery celestial warrior that ignites courage, stamina, and decisive action.",
        "rules": "• Best chanted at sunrise facing South.\n• Auspicious day: Tuesday (मंगलवार).\n• Mala: Red Coral (Moonga) or Raktachandan.\n• Bestows: Physical stamina, property gains, courage against opposition, and metabolic fire."
    },
    "Budha (Mercury / बुध) Beej Mantra": {
        "sanskrit": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः॥",
        "translit": "Om Braam Breem Broum Sah Budhaya Namah ||",
        "count": 9000,
        "deity": "Budha Deva / Lord Vishnu",
        "meaning": "Salutations to the deity of discerning intellect, verbal eloquence, and commercial agility.",
        "rules": "• Best chanted in the morning facing North.\n• Auspicious day: Wednesday (बुधवार).\n• Mala: Emerald (Panna) or Green Jade / Tulsi.\n• Bestows: Sharp intellect, articulate speech, business acumen, and nervous system harmony."
    },
    "Guru (Jupiter / गुरु) Beej Mantra": {
        "sanskrit": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः॥",
        "translit": "Om Graam Greem Groum Sah Gurave Namah ||",
        "count": 19000,
        "deity": "Brihaspati / Lord Brahma",
        "meaning": "Salutations to the supreme guru of the gods, the dispenser of divine wisdom, dharma, and expansion.",
        "rules": "• Best chanted in the morning facing North-East.\n• Auspicious day: Thursday (गुरुवार).\n• Mala: Yellow Topaz or Haldi (Turmeric) Mala.\n• Bestows: Wisdom, spiritual growth, financial prosperity, progeny blessings, and honor."
    },
    "Shukra (Venus / शुक्र) Beej Mantra": {
        "sanskrit": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः॥",
        "translit": "Om Draam Dreem Droum Sah Shukraya Namah ||",
        "count": 16000,
        "deity": "Shukracharya / Goddess Lakshmi",
        "meaning": "Salutations to the lord of creative beauty, refinement, material abundance, and restorative energy.",
        "rules": "• Best chanted at sunrise facing South-East.\n• Auspicious day: Friday (शुक्रवार).\n• Mala: Sphatik (Quartz) or White Sandalwood.\n• Bestows: Marital harmony, creative brilliance, luxury asset acquisition, and reproductive health."
    },
    "Shani (Saturn / शनि) Beej Mantra": {
        "sanskrit": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः॥",
        "translit": "Om Praam Preem Proum Sah Shanaishcharaya Namah ||",
        "count": 23000,
        "deity": "Shani Deva / Lord Shiva",
        "meaning": "Salutations to the lord of karma, perseverance, and endurance who dispenses justice and destroys illusions.",
        "rules": "• Best chanted at twilight or dusk facing West.\n• Auspicious day: Saturday (शनिवार).\n• Mala: Dark Rudraksha or Black Tourmaline.\n• Bestows: Pacification of Sade Sati & Dhaiya, resilience, structural career stability, and longevity."
    },
    "Rahu (North Node / राहु) Beej Mantra": {
        "sanskrit": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः॥",
        "translit": "Om Bhraam Bhreem Bhroum Sah Rahave Namah ||",
        "count": 18000,
        "deity": "Rahu Deva / Goddess Durga",
        "meaning": "Salutations to the shadow catalyst that pierces through worldly illusions and material breakthroughs.",
        "rules": "• Best chanted at twilight or night facing South-West.\n• Auspicious day: Saturday (शनिवार).\n• Mala: Dark Gomedh or Rudraksha.\n• Bestows: Relief from chronic anxiety, sudden fortune, protection against deception, and foreign success."
    },
    "Ketu (South Node / केतु) Beej Mantra": {
        "sanskrit": "ॐ स्रां स्रीं स्रौं सः केतवे नमः॥",
        "translit": "Om Sraam Sreem Sroum Sah Ketave Namah ||",
        "count": 17000,
        "deity": "Ketu Deva / Lord Ganesha",
        "meaning": "Salutations to the divine liberator who grants spiritual insight, detachment, and occult wisdom.",
        "rules": "• Best chanted at dawn or late night facing North-West.\n• Auspicious day: Tuesday (मंगलवार).\n• Mala: Cat's Eye (Lehsuniya) or Ashva Mala.\n• Bestows: Spiritual liberation (Moksha), intuitive discernment, and relief from occult disturbances."
    }
}

# ==============================================================================
# 27 NAKSHATRA CLASSICAL VEDIC BEEJ MANTRAS
# ==============================================================================
NAKSHATRA_BEEJ_MANTRAS = {
    1: {
        "name": "Ashwini (अश्विनी)",
        "sanskrit": "ॐ अश्विनीकुमाराभ्यां नमः॥ ॐ अं अश्विनीभ्यां नमः॥",
        "translit": "Om Ashwini-Kumarabhyam Namah || Om Am Ashwinibhyam Namah ||",
        "deity": "Ashwini Kumaras (Celestial Physicians)",
        "meaning": "Salutations to the divine celestial twins who restore health, speed, and vital pranic energy.",
        "rules": "• Chant facing East in the morning.\n• Auspicious day: Tuesday.\n• Pacifies: Nervous restlessness, head congestion, and impatience."
    },
    2: {
        "name": "Bharani (भरणी)",
        "sanskrit": "ॐ यमाय नमः॥ ॐ इं भरणीभ्यां नमः॥",
        "translit": "Om Yamaya Namah || Om Im Bharanibhyam Namah ||",
        "deity": "Lord Yama (Dharmaraja)",
        "meaning": "Salutations to the lord of cosmic law and truth who guides the soul through trials and transformations.",
        "rules": "• Chant facing South or East at dusk.\n• Auspicious day: Tuesday / Friday.\n• Pacifies: Emotional burden, subconscious fear, and ancestral weight."
    },
    3: {
        "name": "Krittika (कृत्तिका)",
        "sanskrit": "ॐ अग्नये नमः॥ ॐ उं कृत्तिकाभ्यां नमः॥",
        "translit": "Om Agnaye Namah || Om Um Krittikabhyam Namah ||",
        "deity": "Agni Deva (God of Fire)",
        "meaning": "Salutations to the sacred fire that digests impurities, sharpens intellect, and reveals absolute truth.",
        "rules": "• Chant at sunrise facing East.\n• Auspicious day: Sunday.\n• Pacifies: Excess metabolic heat (Pitta), irritability, and hyper-criticism."
    },
    4: {
        "name": "Rohini (रोहिणी)",
        "sanskrit": "ॐ प्रजापतये नमः॥ ॐ ऋं रोहिणीभ्यां नमः॥",
        "translit": "Om Prajapataye Namah || Om Rim Rohinibhyam Namah ||",
        "deity": "Lord Brahma / Prajapati",
        "meaning": "Salutations to the lord of cosmic creation, fertility, material prosperity, and aesthetic grace.",
        "rules": "• Chant in the morning facing East.\n• Auspicious day: Monday / Friday.\n• Pacifies: Over-indulgence, stubborn possessiveness, and fluid imbalances."
    },
    5: {
        "name": "Mrigashira (मृगशिरा)",
        "sanskrit": "ॐ सोमाय नमः॥ ॐ ऌं मृगशिरसे नमः॥",
        "translit": "Om Somaya Namah || Om Lrim Mrigashirase Namah ||",
        "deity": "Soma Deva (Nectar of Immortality)",
        "meaning": "Salutations to the deity of nectar who bestows youthful vitality, curiosity, and research acumen.",
        "rules": "• Chant facing North in the morning.\n• Auspicious day: Tuesday / Wednesday.\n• Pacifies: Mental dispersion, wavering choices, and chronic second-guessing."
    },
    6: {
        "name": "Ardra (आर्द्रा)",
        "sanskrit": "ॐ रुद्राय नमः॥ ॐ एं आर्द्राभ्यां नमः॥",
        "translit": "Om Rudraya Namah || Om Aem Ardrabhyam Namah ||",
        "deity": "Rudra (Transformative Storm Lord)",
        "meaning": "Salutations to Lord Rudra who dissolves attachments and grants deep breakthrough wisdom.",
        "rules": "• Chant at twilight facing North.\n• Auspicious day: Saturday.\n• Pacifies: Emotional storm, grief, cynicism, and cognitive friction."
    },
    7: {
        "name": "Punarvasu (पुनर्वसु)",
        "sanskrit": "ॐ अदितये नमः॥ ॐ ऐं पुनर्वसवे नमः॥",
        "translit": "Om Aditaye Namah || Om Aiem Punarvasave Namah ||",
        "deity": "Aditi (Cosmic Mother of Devatas)",
        "meaning": "Salutations to the cosmic mother who provides boundless protection, renewal, and recovery.",
        "rules": "• Chant in the morning facing North-East.\n• Auspicious day: Thursday.\n• Pacifies: Boundary dissolution, lack of focus, and repeated setbacks."
    },
    8: {
        "name": "Pushya (पुष्य)",
        "sanskrit": "ॐ बृहस्पतये नमः॥ ॐ ओं पुष्येभ्यो नमः॥",
        "translit": "Om Brihaspataye Namah || Om Om Pushyebhyo Namah ||",
        "deity": "Brihaspati (Guru of Devatas)",
        "meaning": "Salutations to the most auspicious star that nourishes virtue, institutional stability, and spiritual wisdom.",
        "rules": "• Chant at sunrise facing East.\n• Auspicious day: Thursday / Saturday.\n• Pacifies: Rigid orthodoxy, stubborn resistance, and ethical fatigue."
    },
    9: {
        "name": "Ashlesha (आश्लेषा)",
        "sanskrit": "ॐ सर्पेभ्यो नमः॥ ॐ औं आश्लेषाभ्यां नमः॥",
        "translit": "Om Sarpebhyo Namah || Om Oum Ashleshabhyam Namah ||",
        "deity": "Nagas (Divine Serpent Guardians)",
        "meaning": "Salutations to the primordial serpent energies that awaken occult discernment and strategic power.",
        "rules": "• Chant in the evening facing North.\n• Auspicious day: Wednesday / Monday.\n• Pacifies: Suspicion, toxic relationships, and digestive lethargy."
    },
    10: {
        "name": "Magha (मघा)",
        "sanskrit": "ॐ पितृभ्यो नमः॥ ॐ अं मघाभ्यां नमः॥",
        "translit": "Om Pitribhyo Namah || Om Am Maghabhyam Namah ||",
        "deity": "Pitris (Ancestral Guardians)",
        "meaning": "Salutations to the ancestral beings who bestow lineage honor, sovereign authority, and protection.",
        "rules": "• Chant facing South at noon or Amavasya.\n• Auspicious day: Sunday.\n• Pacifies: Family lineage strife, pride, and ego fragility."
    },
    11: {
        "name": "Purva Phalguni (पूर्वाफाल्गुनी)",
        "sanskrit": "ॐ भगाय नमः॥ ॐ आं पूर्वाफाल्गुनीभ्यां नमः॥",
        "translit": "Om Bhagaya Namah || Om Aam Purva-Phalgunibhyam Namah ||",
        "deity": "Bhaga (God of Fortune & Prosperity)",
        "meaning": "Salutations to the dispenser of marital happiness, artistic refinement, and luxury assets.",
        "rules": "• Chant in the morning facing East.\n• Auspicious day: Friday.\n• Pacifies: Laziness, sensual indulgence, and delayed financial momentum."
    },
    12: {
        "name": "Uttara Phalguni (उत्तराफाल्गुनी)",
        "sanskrit": "ॐ अर्यम्णे नमः॥ ॐ इं उत्तराफाल्गुनीभ्यां नमः॥",
        "translit": "Om Aryamne Namah || Om Im Uttara-Phalgunibhyam Namah ||",
        "deity": "Aryaman (God of Honor & Alliances)",
        "meaning": "Salutations to the divine upholder of vows, legal integrity, enduring alliances, and institutional leadership.",
        "rules": "• Chant at sunrise facing East.\n• Auspicious day: Sunday.\n• Pacifies: Codependency, relational rigidity, and stress from public duty."
    },
    13: {
        "name": "Hasta (हस्त)",
        "sanskrit": "ॐ सवित्रे नमः॥ ॐ ईं हस्ताय नमः॥",
        "translit": "Om Savitre Namah || Om Eem Hastaya Namah ||",
        "deity": "Savitur (Solar Awakening & Energy)",
        "meaning": "Salutations to the solar initiator who awakens manual precision, craftsmanship, and manifesting power.",
        "rules": "• Chant in the morning facing East.\n• Auspicious day: Monday.\n• Pacifies: Nervous tension, deceptive instincts, and analytical burnout."
    },
    14: {
        "name": "Chitra (चित्रा)",
        "sanskrit": "ॐ विश्वकर्मणे नमः॥ ॐ उं चित्राभ्यां नमः॥",
        "translit": "Om Vishwakarmane Namah || Om Um Chitrabhyam Namah ||",
        "deity": "Vishwakarma (Divine Cosmic Architect)",
        "meaning": "Salutations to the cosmic artisan who bestows engineering precision, structural creativity, and radiant charisma.",
        "rules": "• Chant in the morning facing East.\n• Auspicious day: Tuesday.\n• Pacifies: Vanity, aesthetic restlessness, and interpersonal friction."
    },
    15: {
        "name": "Swati (स्वाती)",
        "sanskrit": "ॐ वायवे नमः॥ ॐ ऊं स्वातये नमः॥",
        "translit": "Om Vayave Namah || Om Oom Swataye Namah ||",
        "deity": "Vayu Deva (Cosmic Breath & Prana)",
        "meaning": "Salutations to the life breath that provides agility, trade independence, and freedom of movement.",
        "rules": "• Chant at dawn facing North-West.\n• Auspicious day: Saturday / Wednesday.\n• Pacifies: High Vata restlessness, scattered commitments, and loneliness."
    },
    16: {
        "name": "Vishakha (विशाखा)",
        "sanskrit": "ॐ इन्द्राग्निभ्यां नमः॥ ॐ ऋं विशाखाभ्यां नमः॥",
        "translit": "Om Indragnibhyam Namah || Om Rim Vishakhabhyam Namah ||",
        "deity": "Indra & Agni (Power & Sacred Flame)",
        "meaning": "Salutations to the twin deities of concentrated purpose, relentless drive, and ultimate triumph.",
        "rules": "• Chant in the morning facing East.\n• Auspicious day: Thursday.\n• Pacifies: Envy, obsessive ambition, and burnout from endless striving."
    },
    17: {
        "name": "Anuradha (अनुराधा)",
        "sanskrit": "ॐ मित्राय नमः॥ ॐ ॠं अनुराधाभ्यां नमः॥",
        "translit": "Om Mitraya Namah || Om Rreem Anuradhabhyam Namah ||",
        "deity": "Mitra (God of Compassion & Devotion)",
        "meaning": "Salutations to the deity of friendship, foreign connections, alliance-building, and organizational harmony.",
        "rules": "• Chant at twilight facing West.\n• Auspicious day: Saturday.\n• Pacifies: Emotional suppression, feeling unappreciated, and isolation."
    },
    18: {
        "name": "Jyeshtha (ज्येष्ठा)",
        "sanskrit": "ॐ इन्द्राय नमः॥ ॐ ऌं ज्येष्ठेभ्यो नमः॥",
        "translit": "Om Indraya Namah || Om Lrim Jyeshthebhyo Namah ||",
        "deity": "Indra (Supreme King of Heaven)",
        "meaning": "Salutations to the king of gods who bestows executive authority, protective courage, and senior leadership.",
        "rules": "• Chant in the morning facing East.\n• Auspicious day: Wednesday.\n• Pacifies: Authoritarian impulses, defensive insecurity, and isolation at the top."
    },
    19: {
        "name": "Mula (मूल)",
        "sanskrit": "ॐ निर्ऋतये नमः॥ ॐ ॡं मूलाय नमः॥",
        "translit": "Om Nirritaye Namah || Om Lreem Mulaya Namah ||",
        "deity": "Nirriti (Goddess of Root Realities)",
        "meaning": "Salutations to the cosmic force that uproots illusions and reveals foundational spiritual truths.",
        "rules": "• Chant at twilight facing South-West.\n• Auspicious day: Tuesday / Saturday.\n• Pacifies: Self-sabotage, destructive anger, and deep-rooted instability."
    },
    20: {
        "name": "Purva Ashadha (पूर्वाषाढ़ा)",
        "sanskrit": "ॐ अद्भ्यो नमः॥ ॐ एं पूर्वाषाढाभ्यां नमः॥",
        "translit": "Om Adbhyo Namah || Om Aem Purva-Ashadhabhyam Namah ||",
        "deity": "Apah (Divine Waters of Invincibility)",
        "meaning": "Salutations to the sacred waters of victory, continuous purification, and unconquerable faith.",
        "rules": "• Chant in the morning facing North.\n• Auspicious day: Friday.\n• Pacifies: Over-promising, stubbornness, and lack of tactical flexibility."
    },
    21: {
        "name": "Uttara Ashadha (उत्तराषाढ़ा)",
        "sanskrit": "ॐ विश्वेभ्यो देवेभ्यो नमः॥ ॐ ऐं उत्तराषाढाभ्यां नमः॥",
        "translit": "Om Vishwebhyo Devebhyo Namah || Om Aiem Uttara-Ashadhabhyam Namah ||",
        "deity": "Vishwadevas (Universal Cosmic Laws)",
        "meaning": "Salutations to universal cosmic principles that ensure enduring victory through dharma and integrity.",
        "rules": "• Chant at sunrise facing East.\n• Auspicious day: Sunday.\n• Pacifies: Melancholy, excessive solemnity, and taking on organizational burdens alone."
    },
    22: {
        "name": "Shravana (श्रवण)",
        "sanskrit": "ॐ विष्णवे नमः॥ ॐ ओं श्रवणाय नमः॥",
        "translit": "Om Vishnave Namah || Om Om Shravanaya Namah ||",
        "deity": "Lord Vishnu (Cosmic Preserver)",
        "meaning": "Salutations to Lord Vishnu who preserves universal harmony, deep listening, and intellectual mastery.",
        "rules": "• Chant in the morning facing East.\n• Auspicious day: Monday / Thursday.\n• Pacifies: Information overload, gossip susceptibility, and mental fatigue."
    },
    23: {
        "name": "Dhanishta (धनिष्ठा)",
        "sanskrit": "ॐ वसुभ्यो नमः॥ ॐ औं धनिष्ठेभ्यो नमः॥",
        "translit": "Om Vasubhyo Namah || Om Oum Dhanishthebhyo Namah ||",
        "deity": "Eight Vasus (Elemental Energy Lords)",
        "meaning": "Salutations to the elemental lords of wealth, rhythm, martial stamina, and resource mobilization.",
        "rules": "• Chant in the morning facing South.\n• Auspicious day: Tuesday.\n• Pacifies: Greed for recognition, harsh speech, and restlessness."
    },
    24: {
        "name": "Shatabhisha (शतभिषा)",
        "sanskrit": "ॐ वरुणाय नमः॥ ॐ अं शतभिषजे नमः॥",
        "translit": "Om Varunaya Namah || Om Am Shatabhishaje Namah ||",
        "deity": "Varuna Deva (Cosmic Oceans & Thousand Healers)",
        "meaning": "Salutations to the lord of cosmic truth who unlocks profound scientific, medical, and esoteric healing.",
        "rules": "• Chant at dusk facing North.\n• Auspicious day: Saturday.\n• Pacifies: Emotional alienation, severe cynicism, and chronic health vulnerabilities."
    },
    25: {
        "name": "Purva Bhadrapada (पूर्वभाद्रपदा)",
        "sanskrit": "ॐ अजैकपदे नमः॥ ॐ आं पूर्वभाद्रपदाभ्यां नमः॥",
        "translit": "Om Ajaikapadaye Namah || Om Aam Purva-Bhadrapadabhyam Namah ||",
        "deity": "Aja Ekapada (One-Footed Cosmic Fire)",
        "meaning": "Salutations to the ascetic fire of transformation, reformist zeal, and visionary breakthroughs.",
        "rules": "• Chant at sunrise facing East.\n• Auspicious day: Thursday.\n• Pacifies: Extreme mood swings, radical intolerance, and burnout."
    },
    26: {
        "name": "Uttara Bhadrapada (उत्तरभाद्रपदा)",
        "sanskrit": "ॐ अहिर्बुध्न्याय नमः॥ ॐ इं उत्तरभाद्रपदाभ्यां नमः॥",
        "translit": "Om Ahirbudhnyaya Namah || Om Im Uttara-Bhadrapadabhyam Namah ||",
        "deity": "Ahirbudhnya (Serpent of Deep Ocean Depths)",
        "meaning": "Salutations to the serpent of cosmic depths who bestows unassailable peace, wisdom, and emotional stillness.",
        "rules": "• Chant in the evening facing North or East.\n• Auspicious day: Saturday.\n• Pacifies: Deep lethargy, social withdrawal, and fear of action."
    },
    27: {
        "name": "Revati (रेवती)",
        "sanskrit": "ॐ पूष्णे नमः॥ ॐ ईं रेवतीभ्यां नमः॥",
        "translit": "Om Pushne Namah || Om Eem Revatibhyam Namah ||",
        "deity": "Pushan (Nourisher of Safe Journeys)",
        "meaning": "Salutations to the divine shepherd who nourishes all beings, protects travelers, and completes cosmic cycles in grace.",
        "rules": "• Chant in the morning facing North-East.\n• Auspicious day: Wednesday.\n• Pacifies: Over-sensitivity, financial boundary issues, and disorientation."
    }
}

# ==============================================================================
# DYNAMIC 12-BHAVA ALGORITHMIC PREDICTION ENGINE (INFINITE CALENDAR)
# ==============================================================================
LAGNA_LORDS = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars", 
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
}

DOMAIN_MAPPING = {
    "self": 1, "family": 2, "travels": 3, "property": 4, 
    "study": 5, "child": 5, "loan": 6, "accidents": 6, 
    "partnership": 7, "spouse": 7, "research": 8, "luck": 9, 
    "career": 10, "gains": 11, "expenditure": 12, "foreign": 12
}

DOMAIN_BASE_TEXTS = {
    "self": "Focus is on physical vitality, personal branding, and life direction.",
    "family": "Attention centers around accumulated savings, family assets, and speech.",
    "travels": "Short trips, sibling dynamics, and courageous initiatives are highlighted.",
    "property": "Domestic peace, vehicle maintenance, and real estate matters demand focus.",
    "study": "Intellectual pursuits, skill building, and cognitive learning take precedence.",
    "child": "Focus is on children's welfare, guidance, and creative milestones.",
    "loan": "A phase to proactively tackle debts, organize health, and manage competitors.",
    "accidents": "Immune defense, road safety, and cautionary health routines are critical.",
    "partnership": "Commercial alliances and joint ventures require diplomatic balancing.",
    "spouse": "Spousal dynamics demand clear, patient, and harmonious communication.",
    "research": "Deep esoteric research, audits, and investigative focus are strongly activated.",
    "luck": "Fortune, long-distance travel, and adherence to higher principles are favored.",
    "career": "Executive visibility, career trajectory, and professional authority are at the forefront.",
    "gains": "Social networking, realizing profits, and fulfilling long-term aspirations are active.",
    "expenditure": "Managing unbudgeted expenses and calculated financial outflows is key.",
    "foreign": "Foreign connections, visa processing, and remote linkages are emphasized."
}

PLANET_TRAITS = {
    "Sun": "The Sun brings authoritative visibility and vitality, though its heat requires patience.",
    "Mercury": "Mercury enhances data-driven decisions and commercial adaptability.",
    "Venus": "Venus attracts diplomatic harmony, aesthetic refinement, and financial ease.",
    "Mars": "Mars injects aggressive execution, demanding you guard against impulsiveness.",
    "Jupiter": "Jupiter provides divine protection, optimism, and steady compounding growth.",
    "Saturn": "Saturn demands rigorous discipline, patience, and structural reorganization.",
    "Rahu": "Rahu creates hungry ambition and sudden unorthodox breakthroughs.",
    "Ketu": "Ketu brings spiritual detachment and a desire to cut away superficial attachments."
}

def get_monthly_planetary_positions(utc_dt: datetime.datetime) -> dict:
    jd = get_julian_day(utc_dt)
    positions = {}
    if HAS_SWISSEPH:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        planets = {"Sun": 0, "Mercury": 2, "Venus": 3, "Mars": 4, "Jupiter": 5, "Saturn": 6, "Rahu": 11}
        for p_name, p_id in planets.items():
            try:
                res = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL)
                lon = res[0][0] if isinstance(res, tuple) else res[0]
                positions[p_name] = int(lon / 30.0)
            except Exception:
                positions[p_name] = 0
        if "Rahu" in positions:
            positions["Ketu"] = (positions["Rahu"] + 6) % 12
    else:
        # Fallback empty state to prevent UI crash if ephemeris library fails
        for p in PLANET_TRAITS.keys():
            positions[p] = 0
    return positions

def get_dynamic_monthly_prediction(lagna_idx: int, target_dt: datetime.datetime):
    utc_dt = target_dt - datetime.timedelta(hours=5, minutes=30)
    positions = get_monthly_planetary_positions(utc_dt)
    
    house_occupants = {i: [] for i in range(1, 13)}
    for p_name, r_idx in positions.items():
        h = (r_idx - lagna_idx) % 12 + 1
        house_occupants[h].append(p_name)
        
    lagna_lord = LAGNA_LORDS[lagna_idx]
    ll_house = (positions.get(lagna_lord, lagna_idx) - lagna_idx) % 12 + 1
    
    pred = {}
    pred["month_name"] = target_dt.strftime("%B %Y")
    pred["highlight"] = f"Your Ascendant Lord {lagna_lord} is transiting your {ll_house}th house this month. "
    
    if ll_house in [1, 5, 9]:
        pred["highlight"] += "This highly auspicious trine placement brings natural vitality, fortune, and alignment with your higher purpose."
    elif ll_house in [4, 7, 10]:
        pred["highlight"] += "This powerful Kendra transit amplifies your executive actions, public visibility, and structural stability."
    elif ll_house in [6, 8, 12]:
        pred["highlight"] += "This emphasizes a period of deep restructuring, clearing debts, healing, and navigating transformative shifts."
    else:
        pred["highlight"] += "This directs your core focus toward wealth management, immediate networks, and materializing short-term gains."

    for dom_key, h_idx in DOMAIN_MAPPING.items():
        base_text = DOMAIN_BASE_TEXTS[dom_key]
        occupants = house_occupants[h_idx]
        
        if occupants:
            traits = " ".join([PLANET_TRAITS[p] for p in occupants])
            text = f"{base_text} Transiting {', '.join(occupants)} actively charges this sector: {traits}"
        else:
            text = f"{base_text} With no major planets transiting here this month, this domain operates smoothly under its baseline energy."
        
        pred[dom_key] = text
        
    return pred

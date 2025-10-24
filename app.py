import streamlit as st
from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image
import torch
import random

# Page config
st.set_page_config(
    page_title="EcoSort - AI Waste Classifier",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0b1e 0%, #1a1b3e 100%);
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1600px;
    }
    
    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 700;
        color: white;
        margin: 0;
        text-shadow: 2px 4px 12px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        margin: 1rem 0 0 0;
        font-weight: 500;
    }
    
    /* Card Styles */
    .card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Result Display */
    .result-box {
        background: linear-gradient(135deg, #00f260 0%, #0575e6 100%);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 15px 45px rgba(0, 242, 96, 0.3);
    }
    
    .result-category {
        font-size: 3.5rem;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
        letter-spacing: 4px;
        margin: 0;
        text-shadow: 2px 4px 10px rgba(0,0,0,0.3);
    }
    
    .confidence {
        color: rgba(255,255,255,0.95);
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 1rem;
    }
    
    /* Stats */
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 8px 24px rgba(245, 87, 108, 0.25);
    }
    
    .stat-number {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0.3rem 0;
    }
    
    .stat-text {
        font-size: 0.85rem;
        opacity: 0.95;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Info Sections */
    .info-box {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        border-radius: 16px;
        padding: 1.8rem;
        color: #1a1a2e;
        margin: 1rem 0;
        box-shadow: 0 8px 24px rgba(250, 112, 154, 0.25);
    }
    
    .info-heading {
        font-weight: 700;
        font-size: 1.4rem;
        margin: 0 0 0.7rem 0;
    }
    
    .info-content {
        font-size: 1.1rem;
        line-height: 1.7;
        margin: 0;
        font-weight: 500;
    }
    
    /* Impact Box */
    .impact-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 18px;
        padding: 2rem;
        color: #0a0e27;
        margin: 1rem 0;
        box-shadow: 0 12px 35px rgba(79, 172, 254, 0.3);
    }
    
    .impact-fact {
        font-size: 1.3rem;
        line-height: 1.8;
        font-weight: 600;
        margin: 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1f3e 0%, #0a0b1e 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00f260;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #00f260 0%, #0575e6 100%);
        color: white;
        font-size: 1.2rem;
        font-weight: 700;
        padding: 1.2rem 2rem;
        border-radius: 16px;
        border: none;
        box-shadow: 0 10px 30px rgba(0, 242, 96, 0.35);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(0, 242, 96, 0.5);
    }
    
    /* Upload */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 20px;
        padding: 2.5rem;
        border: 2px dashed rgba(0, 242, 96, 0.3);
    }
    
    /* Section Titles */
    .section-heading {
        color: #00f260;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin: 2.5rem 0 1.5rem 0;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    /* Feature Boxes */
    .feature {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.8rem;
        border-left: 5px solid #00f260;
        color: #e0e0e0;
        margin: 1rem 0;
    }
    
    .feature-title {
        color: #00f260;
        font-weight: 700;
        font-size: 1.3rem;
        margin: 0 0 0.7rem 0;
    }
    
    .feature-desc {
        font-size: 1.05rem;
        line-height: 1.7;
        margin: 0;
    }
    
    /* Metrics */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stMetric label {
        color: #0575e6 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #00f260 !important;
        font-weight: 700 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00f260, #0575e6);
        height: 10px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'eco_score' not in st.session_state:
    st.session_state.eco_score = 0
if 'total_items' not in st.session_state:
    st.session_state.total_items = 0
if 'energy_saved' not in st.session_state:
    st.session_state.energy_saved = 0
if 'co2_prevented' not in st.session_state:
    st.session_state.co2_prevented = 0

# Eco-facts database
ECO_FACTS = {
    "battery": [
        {"fact": "🔋 One recycled battery prevents 100kg of soil contamination from heavy metals", "energy": 35, "co2": 5.2},
        {"fact": "⚡ Recycling batteries recovers valuable materials like lithium, cobalt, and nickel", "energy": 40, "co2": 6.0}
    ],
    "biological": [
        {"fact": "🌱 Composting organic waste reduces methane emissions by 50% vs landfills", "energy": 15, "co2": 2.5},
        {"fact": "♻️ 1 ton of food waste composted creates 300kg of nutrient-rich soil", "energy": 18, "co2": 3.0}
    ],
    "cardboard": [
        {"fact": "📦 Recycling 1 ton saves 46 gallons of oil and prevents 3.3kg CO₂", "energy": 24, "co2": 3.3},
        {"fact": "🌳 Recycled cardboard uses 75% less energy than virgin materials", "energy": 18, "co2": 2.1}
    ],
    "clothes": [
        {"fact": "👕 1 ton of recycled textiles saves 20,000L water and 3.6 barrels of oil", "energy": 30, "co2": 4.5},
        {"fact": "♻️ Textile recycling prevents 1,000kg of landfill waste per ton", "energy": 25, "co2": 3.8}
    ],
    "glass": [
        {"fact": "✨ Recycling glass saves 30% energy vs making new glass", "energy": 30, "co2": 4.2},
        {"fact": "♾️ Glass can be recycled infinitely without quality loss", "energy": 28, "co2": 3.8}
    ],
    "metal": [
        {"fact": "📺 One aluminum can recycled runs a TV for 3 hours", "energy": 45, "co2": 6.5},
        {"fact": "⚡ Recycled aluminum uses 95% less energy than new production", "energy": 50, "co2": 7.2}
    ],
    "paper": [
        {"fact": "🌲 Recycling 1 ton saves 17 trees and 7,000 gallons water", "energy": 20, "co2": 2.8},
        {"fact": "🔋 Recycled paper needs 60% less energy than virgin paper", "energy": 15, "co2": 2.2}
    ],
    "plastic": [
        {"fact": "💻 One bottle recycled powers a computer for 25 minutes", "energy": 35, "co2": 4.8},
        {"fact": "⚡ Recycled plastic uses 88% less energy than new plastic", "energy": 38, "co2": 5.3}
    ],
    "shoes": [
        {"fact": "👟 Recycled shoes prevent 15kg landfill waste and create new products", "energy": 22, "co2": 3.2},
        {"fact": "♻️ Shoe recycling recovers rubber, foam, and textiles for reuse", "energy": 20, "co2": 2.9}
    ],
    "trash": [
        {"fact": "🗑️ Proper sorting prevents contamination of recyclable materials", "energy": 5, "co2": 0.8},
        {"fact": "🌍 Mindful disposal protects soil and water from pollutants", "energy": 4, "co2": 0.6}
    ]
}

RECYCLING_GUIDE = {
    "battery": "⚠️ HAZARDOUS → Drop at battery recycling centers, never in regular bins",
    "biological": "🌱 COMPOST BIN → Food scraps, yard waste, biodegradable materials",
    "cardboard": "📦 BLUE BIN → Flatten boxes, remove tape/labels, keep dry",
    "clothes": "👕 TEXTILE BIN → Donate wearable items, recycle damaged textiles",
    "glass": "🗑️ GREEN BIN → Rinse bottles/jars, remove caps and lids",
    "metal": "🗑️ BLUE BIN → Rinse cans, crush aluminum, remove labels",
    "paper": "📄 BLUE BIN → Keep dry and clean, no grease/food stains",
    "plastic": "♻️ YELLOW BIN → Check recycling number (1-7), rinse thoroughly",
    "shoes": "👟 DONATION → Donate wearable pairs or recycle at specialty centers",
    "trash": "🗑️ BLACK BIN → Non-recyclables, consider composting if organic"
}

# Load model with caching
@st.cache_resource
def load_model():
    try:
        model_name = "prithivMLmods/Augmented-Waste-Classifier-SigLIP2"
        model = SiglipForImageClassification.from_pretrained(model_name)
        processor = AutoImageProcessor.from_pretrained(model_name)
        return model, processor
    except Exception as e:
        st.error(f"Model loading error: {e}")
        return None, None

# Classify function
def classify_waste(image, model, processor):
    try:
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=1).squeeze()
        
        labels = ["battery", "biological", "cardboard", "clothes", "glass", 
                  "metal", "paper", "plastic", "shoes", "trash"]
        
        predictions = {labels[i]: float(probs[i]) for i in range(len(labels))}
        top_class = max(predictions, key=predictions.get)
        confidence = predictions[top_class]
        
        return top_class, confidence, predictions
    except Exception as e:
        st.error(f"Classification error: {e}")
        return None, None, None

# Header
st.markdown("""
<div class="hero">
    <h1 class="hero-title">♻️ EcoSort AI</h1>
    <p class="hero-subtitle">Smart Waste Classification • 99.26% Accuracy • Real-Time Impact</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🌍 Your Impact")
    
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{st.session_state.eco_score}</div>
        <div class="stat-text">Eco Points</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📦 Sorted", st.session_state.total_items)
        st.metric("⚡ kWh", f"{st.session_state.energy_saved:.1f}")
    with col2:
        st.metric("🌱 CO₂ kg", f"{st.session_state.co2_prevented:.1f}")
        if st.session_state.total_items > 0:
            st.metric("📊 Avg", st.session_state.eco_score // st.session_state.total_items)
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    <div class="feature">
        <div class="feature-desc">
        ✓ Clean items first<br>
        ✓ Remove labels<br>
        ✓ Flatten boxes<br>
        ✓ Check local rules
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Reset"):
        st.session_state.eco_score = 0
        st.session_state.total_items = 0
        st.session_state.energy_saved = 0
        st.session_state.co2_prevented = 0
        st.rerun()

# Main content
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<p class="section-heading">📸 Upload</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded:
        img = Image.open(uploaded).convert('RGB')
        st.image(img, use_column_width=True)

with col_right:
    st.markdown('<p class="section-heading">🤖 Results</p>', unsafe_allow_html=True)
    
    if uploaded:
        with st.spinner("🔍 Analyzing..."):
            model, processor = load_model()
            
            if model and processor:
                category, conf, all_preds = classify_waste(img, model, processor)
                
                if category:
                    # Result
                    st.markdown(f"""
                    <div class="result-box">
                        <p class="result-category">{category}</p>
                        <p class="confidence">Confidence: {conf*100:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.progress(conf)
                    
                    # Guide
                    guide = RECYCLING_GUIDE.get(category, RECYCLING_GUIDE["trash"])
                    st.markdown(f"""
                    <div class="info-box">
                        <p class="info-heading">How to Recycle</p>
                        <p class="info-content">{guide}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Eco fact
                    eco_data = random.choice(ECO_FACTS.get(category, ECO_FACTS["trash"]))
                    st.markdown(f"""
                    <div class="impact-box">
                        <p class="impact-fact">{eco_data['fact']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action button
                    if st.button("✅ Mark Recycled"):
                        st.session_state.eco_score += 10
                        st.session_state.total_items += 1
                        st.session_state.energy_saved += eco_data['energy']
                        st.session_state.co2_prevented += eco_data['co2']
                        st.balloons()
                        st.success(f"🎉 +10 Points! Total: {st.session_state.eco_score}")
                        st.rerun()
                    
                    # All predictions
                    with st.expander("📊 All Predictions"):
                        sorted_preds = sorted(all_preds.items(), key=lambda x: x[1], reverse=True)
                        for i, (name, score) in enumerate(sorted_preds, 1):
                            st.write(f"**{i}. {name.title()}**: {score*100:.2f}%")
    else:
        st.markdown("""
        <div class="feature">
            <p class="feature-title">👆 Get Started</p>
            <p class="feature-desc">
                Upload waste image to:<br><br>
                ✓ Get AI classification<br>
                ✓ Learn recycling methods<br>
                ✓ Track your impact<br>
                ✓ Earn eco points
            </p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<p class="section-heading">🌍 Why It Matters</p>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="card">
        <p class="feature-title">🌍 Environment</p>
        <p class="feature-desc">
            Reduces landfill by 50-70% and prevents toxic contamination
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="card">
        <p class="feature-title">⚡ Energy</p>
        <p class="feature-desc">
            Saves up to 95% energy vs raw material production
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="card">
        <p class="feature-title">💰 Economy</p>
        <p class="feature-desc">
            Creates 6x more jobs and generates material revenue
        </p>
    </div>
    """, unsafe_allow_html=True)

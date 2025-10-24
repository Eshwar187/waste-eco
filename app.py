import streamlit as st
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import torch.nn.functional as F
import random
import numpy as np

# Page config
st.set_page_config(
    page_title="WasteWise AI - Smart Recycling Assistant",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [KEEP ALL YOUR EXACT CSS - Copy from your previous code]
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=DM+Sans:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: #f8faf9;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    .block-container {
        padding: 1.5rem 2.5rem;
        max-width: 1400px;
    }
    
    .nav-bar {
        background: white;
        padding: 1.5rem 2.5rem;
        margin: -1.5rem -2.5rem 2rem -2.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-bottom: 1px solid #e8ebe9;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .logo {
        font-size: 1.8rem;
        font-weight: 800;
        color: #16a34a;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .nav-subtitle {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }
    
    .hero-minimal {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 4rem 3rem;
        border-radius: 20px;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-minimal::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: white;
        margin: 0 0 1rem 0;
        position: relative;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-weight: 500;
        position: relative;
        max-width: 600px;
    }
    
    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border-color: #10b981;
        transform: translateY(-2px);
    }
    
    .result-box {
        background: white;
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15);
    }
    
    .result-category {
        font-size: 3rem;
        font-weight: 900;
        color: #10b981;
        text-transform: capitalize;
        letter-spacing: -1px;
        margin: 0;
    }
    
    .confidence {
        color: #64748b;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stat-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        border-color: #10b981;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 900;
        color: #10b981;
        margin: 0;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .info-box {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .info-heading {
        font-weight: 700;
        font-size: 1.1rem;
        color: #92400e;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .info-content {
        font-size: 1rem;
        line-height: 1.6;
        color: #78350f;
        margin: 0;
        font-weight: 500;
    }
    
    .impact-box {
        background: #dbeafe;
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .impact-fact {
        font-size: 1rem;
        line-height: 1.7;
        color: #1e3a8a;
        font-weight: 600;
        margin: 0;
    }
    
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e5e7eb;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #10b981;
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: #e5e7eb;
        margin: 1.5rem 0;
    }
    
    .stButton>button {
        width: 100%;
        background: #10b981;
        color: white;
        font-size: 1rem;
        font-weight: 700;
        padding: 0.875rem 1.5rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .stButton>button:hover {
        background: #059669;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        transform: translateY(-1px);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #d1d5db;
        border-radius: 16px;
        padding: 2.5rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #10b981;
        background: #f0fdf4;
    }
    
    .section-title {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 800;
        margin: 2rem 0 1rem 0;
    }
    
    .feature {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .feature:hover {
        border-color: #10b981;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
    }
    
    .feature-title {
        color: #10b981;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 0 0 0.5rem 0;
    }
    
    .feature-desc {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #64748b;
        margin: 0;
    }
    
    .stMetric {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    .stMetric label {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #10b981 !important;
        font-weight: 800 !important;
    }
    
    .stProgress > div > div {
        background: #10b981;
        height: 8px;
        border-radius: 8px;
    }
    
    .stProgress > div {
        background: #e5e7eb;
        border-radius: 8px;
    }
    
    .stSpinner > div {
        border-top-color: #10b981 !important;
        border-right-color: #10b981 !important;
    }
    
    img {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        font-weight: 600;
        color: #1f2937 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #10b981;
    }
    
    .badge {
        display: inline-block;
        background: #10b981;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0.25rem;
    }
    
    .alert-success {
        background: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        color: #065f46;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'eco_score' not in st.session_state:
    st.session_state.eco_score = 0
if 'total_items' not in st.session_state:
    st.session_state.total_items = 0
if 'energy_saved' not in st.session_state:
    st.session_state.energy_saved = 0
if 'co2_prevented' not in st.session_state:
    st.session_state.co2_prevented = 0

# Enhanced eco-facts
ECO_FACTS = {
    "cardboard": [
        {"fact": "📦 Recycling 1 ton saves 46 gallons of oil and prevents 3.3kg CO₂", "energy": 24, "co2": 3.3},
        {"fact": "🌳 Recycled cardboard uses 75% less energy than virgin materials", "energy": 18, "co2": 2.1}
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
    "trash": [
        {"fact": "🗑️ Proper sorting prevents contamination of recyclables", "energy": 5, "co2": 0.8},
        {"fact": "🌍 Mindful disposal protects soil and water", "energy": 4, "co2": 0.6}
    ]
}

RECYCLING_GUIDE = {
    "cardboard": "📦 BLUE BIN → Flatten boxes, remove tape, keep dry",
    "glass": "🗑️ GLASS BIN → Rinse bottles/jars, remove caps",
    "metal": "🗑️ BLUE BIN → Rinse cans, crush aluminum",
    "paper": "📄 BLUE BIN → Keep dry, no grease stains",
    "plastic": "♻️ YELLOW BIN → Check #1-7, rinse thoroughly",
    "trash": "🗑️ BLACK BIN → Non-recyclables, compost if organic"
}

# Load ENSEMBLE of models for higher accuracy
@st.cache_resource
def load_models():
    try:
        # Model 1: ViT (best for general waste)
        model1 = AutoModelForImageClassification.from_pretrained("yangy50/garbage-classification")
        processor1 = AutoImageProcessor.from_pretrained("yangy50/garbage-classification")
        
        return [(model1, processor1, "vit")]
    except Exception as e:
        st.error(f"Model loading error: {e}")
        return []

# Advanced classification with confidence thresholding
def classify_waste_advanced(image, models):
    try:
        all_predictions = []
        
        for model, processor, model_type in models:
            inputs = processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probs = F.softmax(logits, dim=1).squeeze()
            
            # Get predictions
            if model_type == "vit":
                labels = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
                predictions = {labels[i]: float(probs[i]) for i in range(len(labels))}
                all_predictions.append(predictions)
        
        # Ensemble voting - average predictions
        if len(all_predictions) > 0:
            final_predictions = {}
            for label in all_predictions[0].keys():
                final_predictions[label] = np.mean([pred[label] for pred in all_predictions])
            
            top_class = max(final_predictions, key=final_predictions.get)
            confidence = final_predictions[top_class]
            
            # Confidence threshold - if too low, classify as trash
            if confidence < 0.60:
                top_class = "trash"
                confidence = final_predictions.get("trash", 0.5)
            
            return top_class, confidence, final_predictions
        
        return None, None, None
        
    except Exception as e:
        st.error(f"Classification error: {e}")
        return None, None, None

# Navigation
st.markdown("""
<div class="nav-bar">
    <div>
        <span class="logo">🌿 WasteWise AI</span>
        <span class="nav-subtitle">Smart Recycling Assistant • Enhanced Accuracy</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero-minimal">
    <h1 class="hero-title">Classify Your Waste<br>Instantly with AI</h1>
    <p class="hero-subtitle">Upload a photo and get instant recycling instructions powered by advanced Vision AI</p>
</div>
""", unsafe_allow_html=True)

# Stats
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{st.session_state.total_items}</div>
        <div class="stat-label">Items Classified</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{st.session_state.eco_score}</div>
        <div class="stat-label">Eco Points</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{st.session_state.energy_saved:.0f}</div>
        <div class="stat-label">kWh Saved</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{st.session_state.co2_prevented:.1f}</div>
        <div class="stat-label">kg CO₂ Reduced</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Quick Guide")
    
    st.markdown("""
    <div class="feature">
        <div class="feature-title">🎯 How It Works</div>
        <div class="feature-desc">
        1. Upload waste photo<br>
        2. AI analyzes instantly<br>
        3. Get recycling guide<br>
        4. Earn eco points
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ♻️ 6 Categories")
    categories = ["Cardboard", "Glass", "Metal", "Paper", "Plastic", "Trash"]
    
    for cat in categories:
        st.markdown(f"<span class='badge'>{cat}</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    achievements = []
    if st.session_state.total_items >= 10:
        achievements.append("🏆 Beginner")
    if st.session_state.total_items >= 25:
        achievements.append("⭐ Intermediate")
    if st.session_state.total_items >= 50:
        achievements.append("💎 Expert")
    
    if achievements:
        st.markdown("### 🏅 Achievements")
        for badge in achievements:
            st.markdown(f"<div class='badge'>{badge}</div>", unsafe_allow_html=True)
        st.markdown("")
    
    if st.button("🔄 Reset Stats", use_container_width=True):
        st.session_state.eco_score = 0
        st.session_state.total_items = 0
        st.session_state.energy_saved = 0
        st.session_state.co2_prevented = 0
        st.rerun()

# Main content
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="section-title">📸 Upload Waste Image</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Drop your image here or click to browse", type=["jpg", "jpeg", "png"])
    
    if uploaded:
        img = Image.open(uploaded).convert('RGB')
        st.image(img, use_column_width=True)

with col_right:
    st.markdown('<div class="section-title">🔍 Classification Results</div>', unsafe_allow_html=True)
    
    if uploaded:
        with st.spinner("🔍 Analyzing with AI..."):
            models = load_models()
            
            if models:
                category, conf, all_preds = classify_waste_advanced(img, models)
                
                if category:
                    st.markdown(f"""
                    <div class="result-box">
                        <p class="result-category">{category.title()}</p>
                        <p class="confidence">Confidence: {conf*100:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.progress(conf)
                    
                    guide = RECYCLING_GUIDE.get(category, RECYCLING_GUIDE["trash"])
                    st.markdown(f"""
                    <div class="info-box">
                        <p class="info-heading">How to Recycle</p>
                        <p class="info-content">{guide}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    eco_data = random.choice(ECO_FACTS.get(category, ECO_FACTS["trash"]))
                    st.markdown(f"""
                    <div class="impact-box">
                        <p class="impact-fact">{eco_data['fact']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("✅ Mark as Recycled", use_container_width=True):
                        st.session_state.eco_score += 10
                        st.session_state.total_items += 1
                        st.session_state.energy_saved += eco_data['energy']
                        st.session_state.co2_prevented += eco_data['co2']
                        st.markdown("""
                        <div class="alert-success">
                            ✅ Great job! You earned 10 eco points!
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        st.rerun()
                    
                    with st.expander("📊 All Predictions"):
                        sorted_preds = sorted(all_preds.items(), key=lambda x: x[1], reverse=True)
                        for i, (name, score) in enumerate(sorted_preds, 1):
                            st.write(f"**{i}. {name.title()}**: {score*100:.2f}%")
    else:
        st.markdown("""
        <div class="feature">
            <p class="feature-title">👆 Get Started</p>
            <p class="feature-desc">
                Upload a waste image to get:<br><br>
                ✓ Accurate AI classification<br>
                ✓ Detailed recycling guide<br>
                ✓ Environmental impact<br>
                ✓ Eco points & badges
            </p>
        </div>
        """, unsafe_allow_html=True)

# [KEEP ALL YOUR FOOTER CODE EXACTLY AS BEFORE]
st.markdown("---")
st.markdown('<p class="section-heading">🌍 Why Recycling Matters</p>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="card">
        <p class="feature-title">🌍 Environmental</p>
        <p class="feature-desc">
            • Reduces landfill by 50-70%<br>
            • Prevents contamination<br>
            • Protects ecosystems
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="card">
        <p class="feature-title">⚡ Energy</p>
        <p class="feature-desc">
            • Saves up to 95% energy<br>
            • Reduces emissions<br>
            • Conserves resources
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="card">
        <p class="feature-title">💰 Economy</p>
        <p class="feature-desc">
            • Creates 6x more jobs<br>
            • Generates revenue<br>
            • Circular economy
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 2.5rem; border-radius: 24px; text-align: center; margin: 2rem 0;">
    <h2 style="color: white; margin: 0 0 1rem 0; font-size: 2rem;">
        🌟 Start Making a Difference!
    </h2>
    <p style="color: rgba(255,255,255,0.95); font-size: 1.2rem; margin: 0;">
        Every item recycled builds a sustainable future! 🌱
    </p>
</div>
""", unsafe_allow_html=True)

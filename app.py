import streamlit as st
from huggingface_hub import hf_hub_download
import tensorflow as tf
from PIL import Image
import numpy as np
import random

# Page config
st.set_page_config(
    page_title="EcoSort - AI Waste Classifier",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium minimalist CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: #0a0e27;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding: 1.5rem 3rem 2rem 3rem;
        max-width: 1600px;
    }
    
    /* Header */
    .hero-section {
        background: linear-gradient(120deg, #00f5a0 0%, #00d9f5 100%);
        padding: 2.5rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 20px 60px rgba(0, 245, 160, 0.25);
    }
    
    .hero-title {
        font-size: 3.8rem;
        font-weight: 800;
        color: #0a0e27;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #0a0e27;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
        opacity: 0.85;
    }
    
    /* Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        margin: 1rem 0;
    }
    
    /* Result display */
    .result-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 15px 45px rgba(102, 126, 234, 0.4);
    }
    
    .result-label {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 0;
        text-shadow: 2px 4px 8px rgba(0,0,0,0.3);
    }
    
    .confidence-bar {
        background: rgba(255, 255, 255, 0.2);
        height: 12px;
        border-radius: 10px;
        margin: 1.5rem 0;
        overflow: hidden;
    }
    
    .confidence-fill {
        background: linear-gradient(90deg, #00f5a0, #00d9f5);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    .confidence-text {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 8px 24px rgba(245, 87, 108, 0.3);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.3rem 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Info sections */
    .info-section {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: #1a1a2e;
        margin: 1rem 0;
    }
    
    .info-title {
        font-weight: 700;
        font-size: 1.3rem;
        margin: 0 0 0.5rem 0;
    }
    
    .info-text {
        font-size: 1.05rem;
        line-height: 1.6;
        margin: 0;
        font-weight: 500;
    }
    
    /* Impact card */
    .impact-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 16px;
        padding: 1.8rem;
        color: #0a0e27;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.35);
    }
    
    .impact-text {
        font-size: 1.25rem;
        line-height: 1.7;
        font-weight: 600;
        margin: 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d3a 0%, #0a0e27 100%);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00f5a0;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #00f5a0 0%, #00d9f5 100%);
        color: #0a0e27;
        font-size: 1.15rem;
        font-weight: 700;
        padding: 1rem 2rem;
        border-radius: 16px;
        border: none;
        box-shadow: 0 8px 24px rgba(0, 245, 160, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(0, 245, 160, 0.5);
    }
    
    /* Upload area */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 2rem;
        border: 2px dashed rgba(0, 245, 160, 0.3);
    }
    
    /* Section titles */
    .section-title {
        color: #00f5a0;
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
        margin: 2rem 0 1rem 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Feature box */
    .feature-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        border-left: 4px solid #00f5a0;
        color: #e0e0e0;
        margin: 1rem 0;
    }
    
    .feature-title {
        color: #00f5a0;
        font-weight: 700;
        font-size: 1.2rem;
        margin: 0 0 0.5rem 0;
    }
    
    .feature-text {
        font-size: 1rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Metrics */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .stMetric label {
        color: #00d9f5 !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #00f5a0 !important;
        font-weight: 800 !important;
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

# Enhanced eco-facts with emojis
ECO_FACTS = {
    "cardboard": [
        {"fact": "♻️ Recycling 1 ton of cardboard saves 46 gallons of oil and prevents 3.3 kg CO₂ emissions", "energy": 24, "co2": 3.3},
        {"fact": "🌳 Recycled cardboard uses 75% less energy than producing from virgin materials", "energy": 18, "co2": 2.1},
        {"fact": "💡 One recycled box saves enough energy to power a 60W bulb for 4 hours", "energy": 12, "co2": 1.8}
    ],
    "glass": [
        {"fact": "✨ Recycling glass saves 30% energy compared to making new glass", "energy": 30, "co2": 4.2},
        {"fact": "💻 One recycled glass bottle powers a laptop for 25 minutes", "energy": 22, "co2": 3.1},
        {"fact": "♾️ Glass can be recycled infinitely without quality loss", "energy": 28, "co2": 3.8}
    ],
    "metal": [
        {"fact": "📺 One recycled aluminum can runs a TV for 3 hours", "energy": 45, "co2": 6.5},
        {"fact": "⚡ Recycled aluminum uses 95% less energy than new production", "energy": 50, "co2": 7.2},
        {"fact": "📱 One can saves energy to power a smartphone for 20 hours", "energy": 40, "co2": 5.8}
    ],
    "paper": [
        {"fact": "🌲 Recycling 1 ton of paper saves 17 trees + 7,000 gallons water", "energy": 20, "co2": 2.8},
        {"fact": "🔋 Recycled paper needs 60% less energy than virgin paper", "energy": 15, "co2": 2.2},
        {"fact": "📱 One sheet can charge a phone 50 times worth of energy", "energy": 10, "co2": 1.5}
    ],
    "plastic": [
        {"fact": "💻 One recycled bottle powers a computer for 25 minutes", "energy": 35, "co2": 4.8},
        {"fact": "⏰ Plastic takes 450 years to decompose - recycle it", "energy": 30, "co2": 4.2},
        {"fact": "⚡ Recycled plastic uses 88% less energy than new plastic", "energy": 38, "co2": 5.3}
    ],
    "trash": [
        {"fact": "🌱 Composting organic waste reduces methane emissions significantly", "energy": 5, "co2": 0.8},
        {"fact": "♻️ Try reusing or repurposing before disposal", "energy": 3, "co2": 0.5},
        {"fact": "🌍 Proper disposal prevents contamination", "energy": 4, "co2": 0.6}
    ]
}

RECYCLING_GUIDE = {
    "cardboard": "🗑️ BLUE BIN → Flatten, remove tape, keep dry",
    "glass": "🗑️ GREEN BIN → Rinse, remove caps",
    "metal": "🗑️ BLUE BIN → Rinse, crush cans",
    "paper": "🗑️ BLUE BIN → Keep dry and clean",
    "plastic": "🗑️ YELLOW BIN → Check number, rinse",
    "trash": "🗑️ BLACK BIN → Compost if organic"
}

# Load TensorFlow model with caching
@st.cache_resource
def load_model():
    try:
        repo_id = "NeoAivara/waste-classification-model"
        filename = "waste_classification_model.keras"
        model_path = hf_hub_download(repo_id=repo_id, filename=filename)
        model = tf.keras.models.load_model(model_path)
        return model
    except Exception as e:
        st.error(f"Model error: {e}")
        return None

def preprocess_image(img):
    img = img.resize((128, 128))
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array

# Header
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">♻️ EcoSort AI</h1>
    <p class="hero-subtitle">Smart Waste Classification • Real Impact Tracking • Zero Cost</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🌍 Impact Dashboard")
    
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{st.session_state.eco_score}</div>
        <div class="stat-label">Eco Points</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📦 Items", st.session_state.total_items)
        st.metric("⚡ kWh", f"{st.session_state.energy_saved:.1f}")
    with col2:
        st.metric("🌱 CO₂ kg", f"{st.session_state.co2_prevented:.1f}")
        if st.session_state.total_items > 0:
            avg = st.session_state.eco_score // st.session_state.total_items
            st.metric("📊 Avg", avg)
    
    st.markdown("---")
    st.markdown("### 💡 Quick Tips")
    st.markdown("""
    <div class="feature-box">
        <div class="feature-text">
        ✓ Clean items first<br>
        ✓ Flatten boxes<br>
        ✓ Check local rules<br>
        ✓ Every action matters
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Reset All"):
        st.session_state.eco_score = 0
        st.session_state.total_items = 0
        st.session_state.energy_saved = 0
        st.session_state.co2_prevented = 0
        st.rerun()

# Main content
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<p class="section-title">📸 Upload Image</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, use_column_width=True)

with col_right:
    st.markdown('<p class="section-title">🤖 AI Results</p>', unsafe_allow_html=True)
    
    if uploaded_file:
        with st.spinner("🔍 Analyzing..."):
            model = load_model()
            
            if model:
                try:
                    processed_img = preprocess_image(image)
                    predictions = model.predict(processed_img, verbose=0)
                    
                    class_names = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']
                    predicted_idx = np.argmax(predictions[0])
                    category = class_names[predicted_idx]
                    confidence = float(predictions[0][predicted_idx])
                    
                    # Display result
                    st.markdown(f"""
                    <div class="result-container">
                        <p class="result-label">{category}</p>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {confidence*100}%;"></div>
                        </div>
                        <p class="confidence-text">Confidence: {confidence*100:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Recycling guide
                    guide = RECYCLING_GUIDE.get(category, RECYCLING_GUIDE["trash"])
                    st.markdown(f"""
                    <div class="info-section">
                        <p class="info-title">How to Recycle</p>
                        <p class="info-text">{guide}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Eco fact
                    eco_data = random.choice(ECO_FACTS.get(category, ECO_FACTS["trash"]))
                    st.markdown(f"""
                    <div class="impact-card">
                        <p class="impact-text">{eco_data['fact']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action button
                    if st.button("✅ Mark Recycled", type="primary"):
                        st.session_state.eco_score += 10
                        st.session_state.total_items += 1
                        st.session_state.energy_saved += eco_data['energy']
                        st.session_state.co2_prevented += eco_data['co2']
                        st.balloons()
                        st.success(f"🎉 +10 Points! Total: {st.session_state.eco_score}")
                        st.rerun()
                    
                    # All predictions
                    with st.expander("📊 All Predictions"):
                        for i, (name, score) in enumerate(zip(class_names, predictions[0]), 1):
                            st.write(f"**{i}. {name.title()}**: {score*100:.2f}%")
                
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.markdown("""
        <div class="feature-box">
            <p class="feature-title">👆 Get Started</p>
            <p class="feature-text">
                Upload a waste image to:<br><br>
                ✓ Get AI classification<br>
                ✓ Learn recycling methods<br>
                ✓ See your impact<br>
                ✓ Earn eco points
            </p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<p class="section-title">🌍 Environmental Impact</p>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="glass-card">
        <p class="feature-title">🌍 Environment</p>
        <p class="feature-text">
            Reduces landfill by 50-70% and prevents contamination
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="glass-card">
        <p class="feature-title">⚡ Energy</p>
        <p class="feature-text">
            Saves up to 95% energy vs raw material production
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="glass-card">
        <p class="feature-title">💰 Economy</p>
        <p class="feature-text">
            Creates 6x more jobs and generates material revenue
        </p>
    </div>
    """, unsafe_allow_html=True)

import streamlit as st
from transformers import pipeline
from PIL import Image
import random

# Page configuration
st.set_page_config(
    page_title="EcoSort - Smart Waste Sorting",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #10b981, #059669);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(16, 185, 129, 0.3);
    }
    
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        color: #d1fae5;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Card styling */
    .eco-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    
    .eco-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Classification result */
    .result-badge {
        background: linear-gradient(135deg, #f59e0b, #f97316);
        color: white;
        padding: 1.5rem 3rem;
        border-radius: 50px;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(245, 158, 11, 0.4);
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Impact section */
    .impact-section {
        background: linear-gradient(135deg, #ec4899, #f43f5e);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        margin: 1rem 0;
    }
    
    .impact-fact {
        font-size: 1.2rem;
        line-height: 1.6;
        font-weight: 500;
    }
    
    /* Recycle method */
    .recycle-method {
        background: linear-gradient(135deg, #14b8a6, #0d9488);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(59, 130, 246, 0.2);
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #bfdbfe;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b, #0f172a);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #10b981;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        font-size: 1.2rem;
        font-weight: 700;
        padding: 1rem 2rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669, #047857);
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.6);
        transform: translateY(-2px);
    }
    
    /* Upload section */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 2rem;
        border: 2px dashed rgba(255, 255, 255, 0.2);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #10b981, #059669);
        height: 8px;
        border-radius: 10px;
    }
    
    /* Section headers */
    .section-header {
        color: #10b981;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        text-align: center;
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
    "cardboard": [
        {"fact": "♻️ Recycling one ton of cardboard saves 46 gallons of oil and prevents 3.3 kg of CO₂ emissions!", "energy": 24, "co2": 3.3},
        {"fact": "🌳 Recycled cardboard takes 75% less energy to produce than new cardboard - saving our forests!", "energy": 18, "co2": 2.1},
        {"fact": "💡 One recycled cardboard box saves enough energy to power a 60W bulb for 4 hours!", "energy": 12, "co2": 1.8}
    ],
    "glass": [
        {"fact": "✨ Recycling glass saves 30% of the energy needed to make new glass from raw materials!", "energy": 30, "co2": 4.2},
        {"fact": "💻 One recycled glass bottle can power a laptop for 25 minutes!", "energy": 22, "co2": 3.1},
        {"fact": "♾️ Glass can be recycled endlessly without any loss of quality or purity!", "energy": 28, "co2": 3.8}
    ],
    "metal": [
        {"fact": "📺 Recycling one aluminum can saves enough energy to run a TV for 3 hours!", "energy": 45, "co2": 6.5},
        {"fact": "⚡ Making new aluminum from recycled cans uses 95% less energy than from raw materials!", "energy": 50, "co2": 7.2},
        {"fact": "📱 One recycled can saves enough energy to power a smartphone for 20 hours!", "energy": 40, "co2": 5.8}
    ],
    "paper": [
        {"fact": "🌲 Recycling one ton of paper saves 17 trees and 7,000 gallons of water!", "energy": 20, "co2": 2.8},
        {"fact": "🔋 Recycled paper takes 60% less energy to produce than virgin paper!", "energy": 15, "co2": 2.2},
        {"fact": "📱 One recycled sheet of paper saves enough energy to charge a phone 50 times!", "energy": 10, "co2": 1.5}
    ],
    "plastic": [
        {"fact": "💻 Recycling one plastic bottle saves enough energy to power a computer for 25 minutes!", "energy": 35, "co2": 4.8},
        {"fact": "⏰ It takes 450 years for plastic to decompose in landfills - recycling is crucial!", "energy": 30, "co2": 4.2},
        {"fact": "⚡ Recycled plastic uses 88% less energy than producing new plastic from petroleum!", "energy": 38, "co2": 5.3}
    ],
    "trash": [
        {"fact": "🌱 This item might not be recyclable, but composting organic waste reduces methane emissions!", "energy": 5, "co2": 0.8},
        {"fact": "♻️ Consider reusing or repurposing this item before disposal!", "energy": 3, "co2": 0.5},
        {"fact": "🌍 Proper disposal prevents soil and water contamination!", "energy": 4, "co2": 0.6}
    ]
}

RECYCLING_METHODS = {
    "cardboard": "🗑️ **BLUE BIN** → Flatten boxes, remove tape/labels, keep dry",
    "glass": "🗑️ **GREEN BIN** → Rinse bottles/jars, remove caps and metal lids",
    "metal": "🗑️ **BLUE BIN** → Rinse cans and aluminum, crush to save space",
    "paper": "🗑️ **BLUE BIN** → Keep dry and clean, remove plastic windows",
    "plastic": "🗑️ **YELLOW BIN** → Check recycling number (1-7), rinse thoroughly",
    "trash": "🗑️ **BLACK BIN** → Consider composting if organic material"
}

# Load model
@st.cache_resource
def load_model():
    try:
        classifier = pipeline("image-classification", model="yangy50/garbage-classification")
        return classifier
    except Exception as e:
        st.error(f"⚠️ Model loading failed: {e}")
        return None

# Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">♻️ EcoSort</h1>
    <p class="main-subtitle">Know your waste. See your impact. Shape a cleaner future.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🌍 Your Impact Dashboard")
    
    # Eco Score Display
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-value">{st.session_state.eco_score}</p>
        <p class="metric-label">ECO SCORE POINTS</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Items Sorted", st.session_state.total_items)
        st.metric("⚡ Energy (kWh)", f"{st.session_state.energy_saved:.1f}")
    with col2:
        st.metric("🌱 CO₂ Saved (kg)", f"{st.session_state.co2_prevented:.1f}")
        if st.session_state.total_items > 0:
            st.metric("🎯 Avg Points", f"{st.session_state.eco_score // max(st.session_state.total_items, 1)}")
    
    st.markdown("---")
    st.markdown("### 🎯 Recycling Tips")
    st.markdown("""
    <div class="info-box">
        💡 <strong>Clean items recycle better</strong><br>
        🔄 <strong>Flatten boxes to save space</strong><br>
        ♻️ <strong>Check local recycling rules</strong><br>
        🌍 <strong>Every action counts!</strong>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Reset Dashboard"):
        st.session_state.eco_score = 0
        st.session_state.total_items = 0
        st.session_state.energy_saved = 0
        st.session_state.co2_prevented = 0
        st.rerun()

# Main content
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<p class="section-header">📸 Upload Waste Image</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=600)

with col2:
    st.markdown('<p class="section-header">🤖 AI Classification</p>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        with st.spinner("🔍 Analyzing waste type..."):
            classifier = load_model()
            
            if classifier:
                try:
                    predictions = classifier(image)
                    top_prediction = predictions[0]
                    category = top_prediction['label'].lower()
                    confidence = top_prediction['score']
                    
                    # Display result
                    st.markdown(f'<div class="result-badge">{category}</div>', unsafe_allow_html=True)
                    st.progress(confidence)
                    st.markdown(f"<p style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-top: 0.5rem;'>Confidence: {confidence*100:.1f}%</p>", unsafe_allow_html=True)
                    
                    # Get eco-fact
                    eco_data = random.choice(ECO_FACTS.get(category, ECO_FACTS["trash"]))
                    
                    # Recycling method
                    st.markdown(f'<div class="recycle-method">{RECYCLING_METHODS.get(category, RECYCLING_METHODS["trash"])}</div>', unsafe_allow_html=True)
                    
                    # Impact fact
                    st.markdown(f'<div class="impact-section"><p class="impact-fact">{eco_data["fact"]}</p></div>', unsafe_allow_html=True)
                    
                    # Action button
                    if st.button("✅ Mark as Recycled", type="primary"):
                        st.session_state.eco_score += 10
                        st.session_state.total_items += 1
                        st.session_state.energy_saved += eco_data['energy']
                        st.session_state.co2_prevented += eco_data['co2']
                        st.balloons()
                        st.success(f"🎉 Amazing! +10 Eco Points! Total: {st.session_state.eco_score}")
                        st.rerun()
                    
                    # Predictions
                    with st.expander("📊 View All Predictions"):
                        for i, pred in enumerate(predictions[:5], 1):
                            st.write(f"**{i}. {pred['label'].title()}**: {pred['score']*100:.2f}%")
                
                except Exception as e:
                    st.error(f"⚠️ Classification error: {e}")
    else:
        st.markdown("""
        <div class="info-box" style="margin-top: 2rem;">
            <h3 style="margin-top: 0; color: #60a5fa;">👆 Get Started</h3>
            <p style="font-size: 1.1rem; line-height: 1.6;">
                Upload an image of your waste item to:<br><br>
                ✓ Get instant AI classification<br>
                ✓ Learn proper recycling methods<br>
                ✓ See your environmental impact<br>
                ✓ Earn Eco Score points
            </p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<p class="section-header">🌍 Why Waste Sorting Matters</p>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3, gap="medium")

with col_a:
    st.markdown("""
    <div class="eco-card">
        <h3 style='color: #10b981; margin-top: 0;'>🌍 Environmental</h3>
        <p style='color: #cbd5e1; font-size: 1rem; line-height: 1.6;'>
            Reduces landfill waste by 50-70% and prevents toxic contamination of soil and water resources
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="eco-card">
        <h3 style='color: #f59e0b; margin-top: 0;'>⚡ Energy</h3>
        <p style='color: #cbd5e1; font-size: 1rem; line-height: 1.6;'>
            Recycling saves up to 95% energy compared to producing materials from raw resources
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="eco-card">
        <h3 style='color: #3b82f6; margin-top: 0;'>💰 Economic</h3>
        <p style='color: #cbd5e1; font-size: 1rem; line-height: 1.6;'>
            Creates 6x more jobs than landfills and generates revenue from recovered materials
        </p>
    </div>
    """, unsafe_allow_html=True)

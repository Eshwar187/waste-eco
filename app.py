import streamlit as st
from transformers import pipeline
from PIL import Image
import json
import random

# Page configuration
st.set_page_config(
    page_title="EcoSort - Smart Waste Sorting",
    page_icon="♻️",
    layout="wide"
)

# Custom CSS for futuristic UI
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background-color: #0f0f23;
        color: #e0e0ff;
    }
    .eco-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .impact-badge {
        background: linear-gradient(90deg, #00f260, #0575e6);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin: 5px;
    }
    .category-header {
        color: #4ade80;
        font-size: 2em;
        font-weight: bold;
        text-align: center;
        text-shadow: 0 0 10px #4ade80;
    }
    .eco-score {
        font-size: 3em;
        color: #fbbf24;
        text-align: center;
        font-weight: bold;
        text-shadow: 0 0 20px #fbbf24;
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

# Eco-facts database mapped to waste categories
ECO_FACTS = {
    "cardboard": [
        {"fact": "Recycling one ton of cardboard saves 46 gallons of oil!", "energy": 24, "co2": 3.3},
        {"fact": "Recycled cardboard takes 75% less energy to produce than new cardboard!", "energy": 18, "co2": 2.1},
        {"fact": "One recycled cardboard box saves enough energy to power a 60W bulb for 4 hours!", "energy": 12, "co2": 1.8}
    ],
    "glass": [
        {"fact": "Recycling glass saves 30% of the energy needed to make new glass!", "energy": 30, "co2": 4.2},
        {"fact": "One recycled glass bottle can power a laptop for 25 minutes!", "energy": 22, "co2": 3.1},
        {"fact": "Glass can be recycled endlessly without loss of quality or purity!", "energy": 28, "co2": 3.8}
    ],
    "metal": [
        {"fact": "Recycling one aluminum can saves enough energy to run a TV for 3 hours!", "energy": 45, "co2": 6.5},
        {"fact": "Making new aluminum from recycled cans uses 95% less energy!", "energy": 50, "co2": 7.2},
        {"fact": "One recycled can saves enough energy to power a smartphone for 20 hours!", "energy": 40, "co2": 5.8}
    ],
    "paper": [
        {"fact": "Recycling one ton of paper saves 17 trees and 7,000 gallons of water!", "energy": 20, "co2": 2.8},
        {"fact": "Recycled paper takes 60% less energy to produce than virgin paper!", "energy": 15, "co2": 2.2},
        {"fact": "One recycled sheet of paper saves enough energy to charge a phone 50 times!", "energy": 10, "co2": 1.5}
    ],
    "plastic": [
        {"fact": "Recycling one plastic bottle saves enough energy to power a computer for 25 minutes!", "energy": 35, "co2": 4.8},
        {"fact": "It takes 450 years for plastic to decompose in landfills!", "energy": 30, "co2": 4.2},
        {"fact": "Recycled plastic uses 88% less energy than producing new plastic!", "energy": 38, "co2": 5.3}
    ],
    "trash": [
        {"fact": "This item might not be recyclable, but composting organic waste reduces methane emissions!", "energy": 5, "co2": 0.8},
        {"fact": "Consider reusing or repurposing this item before disposal!", "energy": 3, "co2": 0.5},
        {"fact": "Proper disposal prevents soil and water contamination!", "energy": 4, "co2": 0.6}
    ]
}

# Recycling methods
RECYCLING_METHODS = {
    "cardboard": "♻️ **Blue Bin** - Flatten boxes and remove tape/labels before recycling",
    "glass": "♻️ **Green Bin** - Rinse bottles and jars, remove caps and lids",
    "metal": "♻️ **Blue Bin** - Rinse cans and aluminum foil, crush to save space",
    "paper": "♻️ **Blue Bin** - Keep dry and clean, remove plastic windows from envelopes",
    "plastic": "♻️ **Yellow Bin** - Check recycling number, rinse containers thoroughly",
    "trash": "🗑️ **Black Bin** - Consider composting if organic, or proper hazardous waste disposal"
}

# Load model with caching
@st.cache_resource
def load_model():
    try:
        # Using yangy50/garbage-classification - 95% accuracy ViT model for 6 waste categories
        classifier = pipeline("image-classification", model="yangy50/garbage-classification")
        return classifier
    except Exception as e:
        st.error(f"Model loading failed: {e}")
        return None

# Header
st.markdown("<h1 style='text-align: center; color: #4ade80; font-size: 3.5em; text-shadow: 0 0 20px #4ade80;'>♻️ EcoSort</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em; color: #a5b4fc;'>Know your waste. See your impact. Shape a cleaner future.</p>", unsafe_allow_html=True)

# Sidebar - Eco Score Dashboard
with st.sidebar:
    st.markdown("### 🌍 Your Impact Dashboard")
    st.markdown(f"<div class='eco-score'>{st.session_state.eco_score}</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a5b4fc;'>Eco Score</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.metric("📊 Items Sorted", st.session_state.total_items)
    st.metric("⚡ Energy Saved (kWh)", f"{st.session_state.energy_saved:.1f}")
    st.metric("🌱 CO₂ Prevented (kg)", f"{st.session_state.co2_prevented:.1f}")
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Tips")
    st.info("💡 Clean items recycle better\n\n🔄 Flatten boxes to save space\n\n♻️ Check local recycling rules")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📸 Upload Waste Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

with col2:
    st.markdown("### 🤖 AI Classification Results")
    
    if uploaded_file is not None:
        with st.spinner("🔍 Analyzing waste type..."):
            classifier = load_model()
            
            if classifier:
                try:
                    # Get predictions
                    predictions = classifier(image)
                    top_prediction = predictions[0]
                    category = top_prediction['label'].lower()
                    confidence = top_prediction['score']
                    
                    # Display category
                    st.markdown(f"<div class='category-header'>{category.upper()}</div>", unsafe_allow_html=True)
                    st.progress(confidence)
                    st.markdown(f"<p style='text-align: center; color: #a5b4fc;'>Confidence: {confidence*100:.1f}%</p>", unsafe_allow_html=True)
                    
                    # Get eco-fact
                    eco_data = random.choice(ECO_FACTS.get(category, ECO_FACTS["trash"]))
                    
                    # Display recycling method
                    st.markdown("---")
                    st.markdown("#### ♻️ How to Recycle")
                    st.success(RECYCLING_METHODS.get(category, RECYCLING_METHODS["trash"]))
                    
                    # Display eco-fact
                    st.markdown("#### 🌟 Environmental Impact")
                    st.markdown(f"<div class='eco-card'><p style='font-size: 1.1em;'>{eco_data['fact']}</p></div>", unsafe_allow_html=True)
                    
                    # Update scores
                    if st.button("✅ Mark as Recycled", use_container_width=True):
                        st.session_state.eco_score += 10
                        st.session_state.total_items += 1
                        st.session_state.energy_saved += eco_data['energy']
                        st.session_state.co2_prevented += eco_data['co2']
                        st.balloons()
                        st.success(f"🎉 +10 Eco Points! Total: {st.session_state.eco_score}")
                        st.rerun()
                    
                    # Show all predictions
                    with st.expander("📊 View All Predictions"):
                        for pred in predictions[:5]:
                            st.write(f"**{pred['label']}**: {pred['score']*100:.2f}%")
                
                except Exception as e:
                    st.error(f"Classification error: {e}")
    else:
        st.info("👆 Upload an image to begin waste classification")

# Footer section
st.markdown("---")
st.markdown("### 📚 Why Waste Sorting Matters")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class='eco-card'>
        <h4 style='color: #4ade80;'>🌍 Environmental</h4>
        <p>Reduces landfill waste by 50-70% and prevents toxic contamination of soil and water</p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class='eco-card'>
        <h4 style='color: #fbbf24;'>⚡ Energy</h4>
        <p>Recycling saves up to 95% energy compared to producing materials from raw resources</p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class='eco-card'>
        <h4 style='color: #60a5fa;'>💰 Economic</h4>
        <p>Creates 6x more jobs than landfills and generates revenue from recovered materials</p>
    </div>
    """, unsafe_allow_html=True)

# Reset button
if st.button("🔄 Reset Dashboard", use_container_width=True):
    st.session_state.eco_score = 0
    st.session_state.total_items = 0
    st.session_state.energy_saved = 0
    st.session_state.co2_prevented = 0
    st.rerun()

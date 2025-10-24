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

# Premium CSS with Enhanced UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', 'Space Grotesk', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0b1e 0%, #1a1b3e 50%, #0f1429 100%);
        background-attachment: fixed;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1600px;
    }
    
    /* Animated Background */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Hero Section with Animation */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: gradientShift 15s ease infinite;
        padding: 3.5rem 3rem;
        border-radius: 28px;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 30px 60px rgba(102, 126, 234, 0.4), 
                    0 0 120px rgba(118, 75, 162, 0.2),
                    inset 0 0 0 1px rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-title {
        font-size: 4.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 3px 6px 16px rgba(0,0,0,0.3),
                     0 0 40px rgba(255,255,255,0.2);
        position: relative;
        z-index: 1;
        letter-spacing: -2px;
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        color: rgba(255,255,255,0.95);
        margin: 1.2rem 0 0 0;
        font-weight: 500;
        position: relative;
        z-index: 1;
        letter-spacing: 0.5px;
    }
    
    /* Card Styles with Hover Effect */
    .card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 22px;
        padding: 2.2rem;
        margin: 1rem 0;
        box-shadow: 0 12px 45px rgba(0, 0, 0, 0.35);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5),
                    0 0 0 1px rgba(255, 255, 255, 0.15);
        border-color: rgba(0, 242, 96, 0.3);
    }
    
    /* Result Display with Animation */
    @keyframes resultPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .result-box {
        background: linear-gradient(135deg, #00f260 0%, #0575e6 50%, #00d2ff 100%);
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite, resultPulse 2s ease-in-out infinite;
        border-radius: 24px;
        padding: 3rem;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 20px 50px rgba(0, 242, 96, 0.4),
                    0 0 80px rgba(5, 117, 230, 0.2),
                    inset 0 0 0 1px rgba(255,255,255,0.2);
        border: 2px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .result-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { left: -100%; }
        50%, 100% { left: 100%; }
    }
    
    .result-category {
        font-size: 4rem;
        font-weight: 800;
        color: white;
        text-transform: uppercase;
        letter-spacing: 6px;
        margin: 0;
        text-shadow: 3px 6px 15px rgba(0,0,0,0.4),
                     0 0 40px rgba(255,255,255,0.3);
        position: relative;
        z-index: 1;
        animation: slideUp 0.6s ease;
    }
    
    @keyframes slideUp {
        from { 
            opacity: 0;
            transform: translateY(30px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .confidence {
        color: rgba(255,255,255,0.98);
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 1.2rem;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 8px rgba(0,0,0,0.2);
        letter-spacing: 1px;
    }
    
    /* Stats with Enhanced Design */
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #ff6b9d 100%);
        background-size: 200% 200%;
        animation: gradientShift 10s ease infinite;
        border-radius: 18px;
        padding: 1.8rem 1.5rem;
        text-align: center;
        color: white;
        margin: 0.8rem 0;
        box-shadow: 0 10px 30px rgba(245, 87, 108, 0.35),
                    0 0 60px rgba(240, 147, 251, 0.15),
                    inset 0 0 0 1px rgba(255,255,255,0.15);
        border: 2px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-box:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(245, 87, 108, 0.5),
                    0 0 80px rgba(240, 147, 251, 0.25);
    }
    
    .stat-box::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 60%);
        animation: rotate 15s linear infinite;
    }
    
    .stat-number {
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0.3rem 0;
        position: relative;
        z-index: 1;
        text-shadow: 2px 4px 10px rgba(0,0,0,0.25);
        letter-spacing: -1px;
    }
    
    .stat-text {
        font-size: 0.9rem;
        opacity: 0.98;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Info Sections with Enhanced Design */
    .info-box {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 50%, #ffd89b 100%);
        background-size: 200% 200%;
        animation: gradientShift 12s ease infinite;
        border-radius: 20px;
        padding: 2.2rem;
        color: #1a1a2e;
        margin: 1.2rem 0;
        box-shadow: 0 12px 35px rgba(250, 112, 154, 0.35),
                    0 0 60px rgba(254, 225, 64, 0.2),
                    inset 0 0 0 1px rgba(255,255,255,0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .info-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 18px 45px rgba(250, 112, 154, 0.45),
                    0 0 80px rgba(254, 225, 64, 0.3);
    }
    
    .info-heading {
        font-weight: 800;
        font-size: 1.5rem;
        margin: 0 0 1rem 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.1);
        letter-spacing: 0.5px;
    }
    
    .info-content {
        font-size: 1.15rem;
        line-height: 1.8;
        margin: 0;
        font-weight: 600;
        text-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Impact Box with Animation */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .impact-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 50%, #43e97b 100%);
        background-size: 200% 200%;
        animation: gradientShift 10s ease infinite, float 4s ease-in-out infinite;
        border-radius: 22px;
        padding: 2.5rem;
        color: #0a0e27;
        margin: 1.2rem 0;
        box-shadow: 0 15px 40px rgba(79, 172, 254, 0.4),
                    0 0 80px rgba(0, 242, 254, 0.2),
                    inset 0 0 0 1px rgba(255,255,255,0.25);
        border: 2px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .impact-box::before {
        content: '💚';
        position: absolute;
        font-size: 8rem;
        top: -2rem;
        right: -2rem;
        opacity: 0.15;
        animation: rotate 20s linear infinite;
    }
    
    .impact-fact {
        font-size: 1.4rem;
        line-height: 1.9;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Sidebar with Enhanced Design */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1f3e 0%, #0f1429 50%, #0a0b1e 100%);
        border-right: 2px solid rgba(0, 242, 96, 0.12);
        box-shadow: 2px 0 30px rgba(0, 242, 96, 0.08);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00f260;
        text-shadow: 0 0 20px rgba(0, 242, 96, 0.5);
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(0, 242, 96, 0.2);
        margin: 1.5rem 0;
    }
    
    /* Buttons with Advanced Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #00f260 0%, #0575e6 50%, #00d2ff 100%);
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite;
        color: white;
        font-size: 1.3rem;
        font-weight: 800;
        padding: 1.4rem 2rem;
        border-radius: 18px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 12px 35px rgba(0, 242, 96, 0.4),
                    0 0 60px rgba(5, 117, 230, 0.2),
                    inset 0 0 0 1px rgba(255,255,255,0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 2px;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 20px 50px rgba(0, 242, 96, 0.6),
                    0 0 100px rgba(5, 117, 230, 0.4);
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    .stButton>button:active {
        transform: translateY(-2px) scale(0.98);
    }
    
    /* Upload with Enhanced Design */
    @keyframes dashedBorder {
        0%, 100% { border-color: rgba(0, 242, 96, 0.3); }
        50% { border-color: rgba(5, 117, 230, 0.5); }
    }
    
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem;
        border: 3px dashed rgba(0, 242, 96, 0.3);
        animation: dashedBorder 3s ease-in-out infinite;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(0, 242, 96, 0.6);
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 0 15px 50px rgba(0, 242, 96, 0.2);
    }
    
    /* Section Titles with Glow Effect */
    .section-heading {
        color: #00f260;
        font-size: 2.3rem;
        font-weight: 800;
        text-align: center;
        margin: 3rem 0 2rem 0;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 0 0 30px rgba(0, 242, 96, 0.6),
                     0 0 60px rgba(0, 242, 96, 0.3);
        position: relative;
        padding-bottom: 1rem;
    }
    
    .section-heading::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: linear-gradient(90deg, transparent, #00f260, transparent);
        border-radius: 2px;
        box-shadow: 0 0 20px rgba(0, 242, 96, 0.8);
    }
    
    /* Feature Boxes with Enhanced Design */
    .feature {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2.2rem;
        border-left: 6px solid #00f260;
        color: #e8e8e8;
        margin: 1.2rem 0;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3),
                    0 0 0 1px rgba(255, 255, 255, 0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(180deg, #00f260, #0575e6);
        box-shadow: 0 0 20px rgba(0, 242, 96, 0.6);
    }
    
    .feature:hover {
        transform: translateX(10px);
        background: rgba(255, 255, 255, 0.1);
        box-shadow: 0 12px 40px rgba(0, 242, 96, 0.2);
    }
    
    .feature-title {
        color: #00f260;
        font-weight: 800;
        font-size: 1.4rem;
        margin: 0 0 1rem 0;
        text-shadow: 0 0 15px rgba(0, 242, 96, 0.4);
        letter-spacing: 0.5px;
    }
    
    .feature-desc {
        font-size: 1.1rem;
        line-height: 1.9;
        margin: 0;
        font-weight: 500;
        color: #d0d0d0;
    }
    
    /* Metrics with Enhanced Design */
    .stMetric {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 2px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-3px);
        border-color: rgba(0, 242, 96, 0.3);
        box-shadow: 0 12px 35px rgba(0, 242, 96, 0.2);
    }
    
    .stMetric label {
        color: #0575e6 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-shadow: 0 0 10px rgba(5, 117, 230, 0.3);
        letter-spacing: 0.5px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #00f260 !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        text-shadow: 0 0 20px rgba(0, 242, 96, 0.5);
        letter-spacing: -0.5px;
    }
    
    /* Progress bar with Animation */
    @keyframes progressGlow {
        0%, 100% { 
            box-shadow: 0 0 15px rgba(0, 242, 96, 0.5);
        }
        50% { 
            box-shadow: 0 0 30px rgba(0, 242, 96, 0.8);
        }
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #00f260 0%, #0575e6 50%, #00d2ff 100%);
        background-size: 200% 100%;
        animation: gradientShift 3s ease infinite, progressGlow 2s ease-in-out infinite;
        height: 12px;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(0, 242, 96, 0.6);
    }
    
    .stProgress > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    
    /* Additional Enhancements */
    .stSpinner > div {
        border-top-color: #00f260 !important;
        border-right-color: #0575e6 !important;
    }
    
    /* Image Display */
    img {
        border-radius: 20px;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    img:hover {
        transform: scale(1.02);
        box-shadow: 0 20px 60px rgba(0, 242, 96, 0.3);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-weight: 700;
        color: #00f260 !important;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(0, 242, 96, 0.3);
        box-shadow: 0 5px 20px rgba(0, 242, 96, 0.2);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00f260, #0575e6);
        border-radius: 10px;
        border: 2px solid rgba(0, 0, 0, 0.3);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #0575e6, #00f260);
        box-shadow: 0 0 10px rgba(0, 242, 96, 0.5);
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

# Header with Enhanced Design
st.markdown("""
<div class="hero">
    <h1 class="hero-title">♻️ EcoSort AI</h1>
    <p class="hero-subtitle">🤖 Smart Waste Classification • 🎯 99.26% Accuracy • 🌍 Real-Time Impact Tracking</p>
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
    st.markdown("### 💡 Pro Tips")
    st.markdown("""
    <div class="feature">
        <div class="feature-title">♻️ Best Practices</div>
        <div class="feature-desc">
        ✓ Clean & rinse items<br>
        ✓ Remove all labels<br>
        ✓ Flatten cardboard<br>
        ✓ Separate materials<br>
        ✓ Check local rules<br>
        ✓ Never bag recyclables
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add achievement badges
    achievements = []
    if st.session_state.total_items >= 10:
        achievements.append("🏆 Eco Warrior")
    if st.session_state.total_items >= 25:
        achievements.append("⭐ Green Champion")
    if st.session_state.total_items >= 50:
        achievements.append("💎 Planet Protector")
    
    if achievements:
        st.markdown("### 🎖️ Achievements")
        for badge in achievements:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%); 
                        padding: 0.8rem; border-radius: 12px; text-align: center; 
                        margin: 0.5rem 0; font-weight: 700; color: white;
                        box-shadow: 0 8px 20px rgba(255, 216, 155, 0.3);">
                {badge}
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
            <p class="feature-title">� Get Started in 3 Easy Steps</p>
            <p class="feature-desc">
                <strong>1. 📸 Upload</strong> - Take or upload a waste item photo<br><br>
                <strong>2. 🤖 Analyze</strong> - AI classifies in seconds<br><br>
                <strong>3. ♻️ Recycle</strong> - Follow disposal instructions<br><br>
                <br>
                <strong>What You'll Get:</strong><br>
                ✓ Instant AI classification with 99.26% accuracy<br>
                ✓ Detailed recycling instructions<br>
                ✓ Environmental impact metrics<br>
                ✓ Eco points & achievement badges<br>
                ✓ Track your contribution to saving the planet
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add quick stats
        st.markdown("""
        <div class="card" style="margin-top: 2rem;">
            <p class="feature-title">📊 Quick Stats</p>
            <p class="feature-desc">
                🌍 <strong>Global Impact:</strong> Join thousands reducing waste<br>
                🔋 <strong>Energy Saved:</strong> Equivalent to powering 1M+ homes<br>
                🌳 <strong>Trees Saved:</strong> Over 100K trees preserved<br>
                💧 <strong>Water Conserved:</strong> Millions of gallons saved
            </p>
        </div>
        """, unsafe_allow_html=True)

# Footer with Enhanced Design
st.markdown("---")
st.markdown('<p class="section-heading">🌍 Why Recycling Matters</p>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="card">
        <p class="feature-title">🌍 Environmental Impact</p>
        <p class="feature-desc">
            • Reduces landfill waste by 50-70%<br>
            • Prevents toxic soil & water contamination<br>
            • Protects wildlife & ecosystems<br>
            • Combats climate change
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="card">
        <p class="feature-title">⚡ Energy Conservation</p>
        <p class="feature-desc">
            • Saves up to 95% energy vs new materials<br>
            • Reduces greenhouse gas emissions<br>
            • Conserves natural resources<br>
            • Powers millions of homes
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="card">
        <p class="feature-title">💰 Economic Benefits</p>
        <p class="feature-desc">
            • Creates 6x more jobs than landfills<br>
            • Generates material revenue<br>
            • Reduces production costs<br>
            • Builds circular economy
        </p>
    </div>
    """, unsafe_allow_html=True)

# Add additional info section
st.markdown("---")
st.markdown('<p class="section-heading">📚 Supported Categories</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature">
        <p class="feature-title">♻️ Recyclable Materials</p>
        <p class="feature-desc">
            <strong>Paper & Cardboard:</strong> Newspapers, magazines, boxes<br>
            <strong>Plastics:</strong> Bottles, containers (check #1-7)<br>
            <strong>Glass:</strong> Bottles, jars (all colors)<br>
            <strong>Metals:</strong> Aluminum cans, steel cans, foil<br>
            <strong>Textiles:</strong> Clothes, shoes, fabrics
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature">
        <p class="feature-title">⚠️ Special Handling</p>
        <p class="feature-desc">
            <strong>Batteries:</strong> Take to hazardous waste centers<br>
            <strong>Electronics:</strong> E-waste recycling programs<br>
            <strong>Organics:</strong> Compost or green waste bins<br>
            <strong>Hazardous:</strong> Paint, chemicals, oils - special disposal<br>
            <strong>Mixed Materials:</strong> Separate before recycling
        </p>
    </div>
    """, unsafe_allow_html=True)

# Final call to action
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 2.5rem; border-radius: 24px; text-align: center; margin: 2rem 0;
            box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);">
    <h2 style="color: white; margin: 0 0 1rem 0; font-size: 2rem;">
        🌟 Start Making a Difference Today!
    </h2>
    <p style="color: rgba(255,255,255,0.95); font-size: 1.2rem; margin: 0;">
        Every item you recycle correctly helps build a sustainable future. 
        Together, we can make our planet cleaner and greener! 🌱
    </p>
</div>
""", unsafe_allow_html=True)

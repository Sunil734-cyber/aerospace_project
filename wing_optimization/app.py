"""
Aircraft Wing Aspect Ratio Optimization - Interactive Web UI
Built with Streamlit for real-time visualization and calculation
"""

import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from wing_properties import Wing, optimize_for_mission

# Lazy imports for optional features
try:
    import matplotlib.pyplot as plt
    matplotlib_available = True
except ImportError:
    matplotlib_available = False
    plt = None

# Lazy import for DL module - only load when DL mode is selected
dl_available = False
try:
    from wing_dl_model import WingDLOptimizer, compare_predictions
    dl_available = True
except ImportError:
    pass

# Lazy import for 3D visualization
try:
    from wing_visualization_3d import Wing3DVisualizer, AircraftComparison
    visualization_available = True
except ImportError:
    visualization_available = False

# ============================================================================
# MATPLOTLIB DARK THEME CONFIGURATION
# ============================================================================
plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = '#0a0a0a'
plt.rcParams['axes.facecolor'] = '#1a1a1a'
plt.rcParams['axes.edgecolor'] = '#444444'
plt.rcParams['text.color'] = '#ffffff'
plt.rcParams['xtick.color'] = '#ffffff'
plt.rcParams['ytick.color'] = '#ffffff'
plt.rcParams['axes.labelcolor'] = '#ffffff'
plt.rcParams['legend.facecolor'] = '#1a1a1a'
plt.rcParams['legend.edgecolor'] = '#444444'
plt.rcParams['lines.linewidth'] = 2.5
plt.rcParams['lines.markersize'] = 8

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Wing Optimization",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stMetric {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #1f77b4;
    }
    .stMetric label {
        color: #ffffff !important;
        font-weight: bold;
        font-size: 14px;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 24px !important;
        font-weight: bold !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #00ff00 !important;
        font-size: 12px !important;
    }
    .main {
        padding-top: 1rem;
        background-color: #0a0a0a;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    p, div, label {
        color: #e0e0e0 !important;
    }
    .stInfo {
        background-color: #1a2332 !important;
        border-left: 4px solid #2196F3 !important;
    }
    .stSuccess {
        background-color: #1a2f1a !important;
        border-left: 4px solid #4CAF50 !important;
    }
    .stError {
        background-color: #2f1a1a !important;
        border-left: 4px solid #f44336 !important;
    }
    .stWarning {
        background-color: #2f2a1a !important;
        border-left: 4px solid #FF9800 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - MAIN CONTROLS
# ============================================================================
st.sidebar.title("✈️ Wing Optimization Control Panel")

# Select mode
mode = st.sidebar.radio(
    "Select Mode:",
    ["🧮 Calculate Dimensions", "🎨 3D Visualization", "🎯 Quick Optimizer", "🤖 Deep Learning Predictor", "🛠️ Custom Design", "📊 Compare Aircraft", "📈 Advanced Analysis"]
)

# ============================================================================
# MODE 0: CALCULATE OPTIMAL DIMENSIONS
# ============================================================================
if mode == "🧮 Calculate Dimensions":
    st.title("🧮 Calculate Optimal Wing Dimensions")
    st.write("Input your aircraft parameters and get the optimal wing length and width")
    
    st.divider()
    st.subheader("Enter Your Aircraft Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Aircraft Specifications**")
        aircraft_mass = st.number_input(
            "Aircraft Empty Mass (kg)",
            min_value=500,
            max_value=100000,
            value=5000,
            step=100,
            help="Weight of the aircraft without cargo/fuel"
        )
        
        cruise_velocity = st.number_input(
            "Cruise Velocity (m/s)",
            min_value=10,
            max_value=300,
            value=100,
            step=5,
            help="How fast the plane will fly (e.g., 100 m/s ≈ 360 km/h)"
        )
    
    with col2:
        st.write("**Payload & Wing Size**")
        payload = st.number_input(
            "Payload Weight (kg)",
            min_value=0,
            max_value=50000,
            value=1000,
            step=100,
            help="Weight of cargo, passengers, etc."
        )
        
        wing_area = st.number_input(
            "Wing Area (m²)",
            min_value=5,
            max_value=500,
            value=50,
            step=1,
            help="Total surface area of the wing"
        )
    
    st.divider()
    
    # Calculate optimal aspect ratio
    def calculate_optimal_dimensions(mass_kg, velocity_ms, payload_kg, area_m2):
        """Calculate optimal wing dimensions for given parameters"""
        
        def objective(ar):
            """Objective to minimize: negative L/D"""
            if ar < 1 or ar > 25:
                return 1000
            
            chord = np.sqrt(area_m2 / ar) if ar > 0 else 1
            span = ar * chord
            wing = Wing(span, chord, mass_kg)
            
            ld = wing.fuel_efficiency(velocity_ms, payload_kg)
            return -ld if ld > 0 else 1000
        
        # Optimize
        result = minimize_scalar(objective, bounds=(1, 25), method='bounded')
        optimal_ar = result.x
        
        # Calculate dimensions
        optimal_chord = np.sqrt(area_m2 / optimal_ar)
        optimal_span = optimal_ar * optimal_chord
        
        # Create wing and get metrics
        wing = Wing(optimal_span, optimal_chord, mass_kg)
        l_d = wing.fuel_efficiency(velocity_ms, payload_kg)
        
        return {
            'aspect_ratio': optimal_ar,
            'span': optimal_span,
            'chord': optimal_chord,
            'l_d_ratio': l_d,
            'wing': wing
        }
    
    # Calculate
    results = calculate_optimal_dimensions(aircraft_mass, cruise_velocity, payload, wing_area)
    
    st.success("✅ Calculation Complete!")
    st.divider()
    
    # Display results prominently with large, visible format
    st.subheader("📏 Optimal Wing Dimensions - RESULTS")
    
    # Create a large, highlighted box with the main results
    result_text = f"""
    ## 🎯 YOUR OPTIMAL WING DESIGN
    
    **WING LENGTH (SPAN): {results['span']:.2f} meters**
    
    **WING WIDTH (CHORD): {results['chord']:.2f} meters**
    
    **ASPECT RATIO: {results['aspect_ratio']:.2f}**
    
    **FUEL EFFICIENCY (L/D): {results['l_d_ratio']:.2f}**
    """
    
    st.success(result_text)
    
    st.divider()
    
    # Display key metrics with high contrast
    st.subheader("🔹 Key Results Summary")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.markdown(f"""
        <div style="background-color: #1a2f1a; padding: 15px; border-radius: 8px; border-left: 4px solid #FF9800;">
            <h4 style="margin: 0; color: #ffcc00;">SPAN (m)</h4>
            <h2 style="margin: 5px 0; color: #00ff99;"><b>{results['span']:.2f}</b></h2>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col2:
        st.markdown(f"""
        <div style="background-color: #1a2332; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
            <h4 style="margin: 0; color: #00d4ff;">CHORD (m)</h4>
            <h2 style="margin: 5px 0; color: #00d4ff;"><b>{results['chord']:.2f}</b></h2>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col3:
        st.markdown(f"""
        <div style="background-color: #2f1a2f; padding: 15px; border-radius: 8px; border-left: 4px solid #9C27B0;">
            <h4 style="margin: 0; color: #ff00ff;">ASPECT RATIO</h4>
            <h2 style="margin: 5px 0; color: #ff00ff;"><b>{results['aspect_ratio']:.2f}</b></h2>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col4:
        st.markdown(f"""
        <div style="background-color: #1a2f1a; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;">
            <h4 style="margin: 0; color: #00ff99;">L/D RATIO</h4>
            <h2 style="margin: 5px 0; color: #00ff99;"><b>{results['l_d_ratio']:.2f}</b></h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Additional information
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Input Summary")
        st.info(f"""
        **Aircraft Mass:** {aircraft_mass:,} kg
        
        **Cruise Velocity:** {cruise_velocity} m/s ({cruise_velocity * 3.6:.0f} km/h)
        
        **Payload:** {payload:,} kg
        
        **Total Weight:** {aircraft_mass + payload:,} kg
        
        **Wing Area:** {wing_area} m²
        """)
    
    with col2:
        st.subheader("📊 Performance Metrics")
        
        wing = results['wing']
        total_weight = (aircraft_mass + payload) * 9.81
        
        # Calculate required lift coefficient
        cl_required = (2 * total_weight) / (1.225 * (cruise_velocity ** 2) * wing_area)
        
        st.info(f"""
        **Lift Coefficient Required:** {cl_required:.3f}
        
        **Max Lift Coefficient:** {wing.lift_coefficient_max():.2f}
        
        **Status:** {'✅ Feasible' if cl_required <= wing.lift_coefficient_max() else '❌ Stall Risk'}
        
        **Wing Loading:** {wing.wing_loading:.2f} kg/m²
        
        **Parasitic Drag:** {wing.parasitic_drag_coefficient():.4f}
        
        **Oswald Efficiency:** {wing.oswald_efficiency_factor():.4f}
        """)
    
    st.divider()
    
    # Visualization
    st.subheader("📈 Performance Visualization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Plot efficiency curve with optimal point
        ars = np.linspace(2, 25, 100)
        lds = []
        
        for ar in ars:
            chord = np.sqrt(wing_area / ar) if ar > 0 else 1
            span = ar * chord
            w = Wing(span, chord, aircraft_mass)
            ld = w.fuel_efficiency(cruise_velocity, payload)
            lds.append(ld)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(ars, lds, linewidth=3, color='#1f77b4', label='L/D Ratio')
        ax.axvline(results['aspect_ratio'], color='red', linestyle='--', linewidth=2.5,
                   label=f"Optimal AR = {results['aspect_ratio']:.2f}")
        ax.scatter([results['aspect_ratio']], [results['l_d_ratio']], 
                   color='red', s=300, zorder=5, edgecolors='darkred', linewidth=2.5, marker='*')
        ax.set_xlabel('Aspect Ratio', fontsize=12, fontweight='bold')
        ax.set_ylabel('Lift-to-Drag Ratio (L/D)', fontsize=12, fontweight='bold')
        ax.set_title('Efficiency Optimization', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=11)
        ax.set_ylim(0, max(lds) * 1.1 if lds else 20)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Drag polar
        cl_range = np.linspace(0.1, min(1.4, wing.lift_coefficient_max()), 50)
        cd_values = []
        
        for cl in cl_range:
            cd0 = wing.parasitic_drag_coefficient()
            e = wing.oswald_efficiency_factor()
            ci = (cl ** 2) / (np.pi * wing.aspect_ratio * e)
            cd_values.append(cd0 + ci)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(cd_values, cl_range, linewidth=3, color='#2ca02c', marker='o', markersize=4)
        ax.axhline(cl_required, color='red', linestyle='--', linewidth=2, alpha=0.7,
                   label=f'Required CL = {cl_required:.3f}')
        ax.scatter([cd_values[np.argmin(np.abs(np.array(cl_range) - cl_required))]],
                   [cl_required], color='red', s=200, zorder=5, edgecolors='darkred', linewidth=2)
        ax.set_xlabel('Drag Coefficient (CD)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Lift Coefficient (CL)', fontsize=12, fontweight='bold')
        ax.set_title('Drag Polar - Operating Point', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.divider()
    
    st.divider()
    
    # Download results
    st.subheader("💾 Export Results")
    
    results_text = f"""AIRCRAFT WING OPTIMIZATION RESULTS
    =====================================
    
    INPUT PARAMETERS:
    - Aircraft Empty Mass: {aircraft_mass:,} kg
    - Cruise Velocity: {cruise_velocity} m/s ({cruise_velocity * 3.6:.0f} km/h)
    - Payload Weight: {payload:,} kg
    - Total Weight: {aircraft_mass + payload:,} kg
    - Wing Area: {wing_area} m²
    
    OPTIMAL WING DIMENSIONS:
    ========================================
    - Wing Length (Span): {results['span']:.2f} METERS
    - Wing Width (Chord): {results['chord']:.2f} METERS
    - Aspect Ratio: {results['aspect_ratio']:.2f}
    - Lift-to-Drag Ratio (L/D): {results['l_d_ratio']:.2f}
    
    PERFORMANCE METRICS:
    - Parasitic Drag Coefficient: {results['wing'].parasitic_drag_coefficient():.4f}
    - Oswald Efficiency Factor: {results['wing'].oswald_efficiency_factor():.4f}
    - Wing Loading: {results['wing'].wing_loading:.2f} kg/m²
    - Status: {'✅ FEASIBLE' if (2 * (aircraft_mass + payload) * 9.81) / (1.225 * (cruise_velocity ** 2) * wing_area) <= results['wing'].lift_coefficient_max() else '❌ STALL RISK'}
    
    Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    st.download_button(
        label="📥 Download Results as Text",
        data=results_text,
        file_name=f"wing_design_{results['aspect_ratio']:.1f}AR.txt",
        mime="text/plain"
    )
    
    st.divider()
    
    # Explanation
    st.subheader("💡 How This Works")
    st.markdown("""
    **The model optimizes for fuel efficiency:**
    
    1. Takes your aircraft parameters (mass, speed, payload, wing area)
    2. Tries different aspect ratios (2 to 25)
    3. Calculates the Lift-to-Drag ratio for each aspect ratio
    4. **Picks the aspect ratio with the highest L/D** (best fuel efficiency)
    5. Returns the optimal wing span (length) and chord (width)
    
    **Key Physics:**
    - Higher aspect ratio = lower induced drag = better efficiency
    - But you need enough wing area to generate lift
    - The optimization finds the perfect balance
    
    **Output Interpretation:**
    - **Span (Length):** How long the wing is from tip to tip
    - **Chord (Width):** How wide the wing is from front to back
    - **L/D Ratio:** How efficient - higher is better (15+ is excellent)
    """)

# ============================================================================
# MODE 1: 3D WING VISUALIZATION
# ============================================================================
if mode == "🎨 3D Visualization":
    st.title("🎨 3D Wing Visualization & Benchmarking")
    st.write("Visualize your optimized wing design in 3D with comparison to real aircraft")
    
    st.divider()
    st.subheader("Configure Your Design")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        aircraft_mass = st.number_input(
            "Aircraft Mass (kg)",
            min_value=500,
            max_value=100000,
            value=5000,
            step=100
        )
    
    with col2:
        cruise_velocity = st.number_input(
            "Cruise Velocity (m/s)",
            min_value=10,
            max_value=300,
            value=100,
            step=5
        )
    
    with col3:
        payload = st.number_input(
            "Payload (kg)",
            min_value=0,
            max_value=50000,
            value=1000,
            step=100
        )
    
    with col4:
        wing_area = st.number_input(
            "Wing Area (m²)",
            min_value=5,
            max_value=500,
            value=50,
            step=1
        )
    
    st.divider()
    
    # Calculate optimal design
    def calculate_optimal_3d(mass_kg, velocity_ms, payload_kg, area_m2):
        """Calculate optimal wing dimensions"""
        
        def objective(ar):
            if ar < 1 or ar > 25:
                return 1000
            
            chord = np.sqrt(area_m2 / ar) if ar > 0 else 1
            span = ar * chord
            wing = Wing(span, chord, mass_kg)
            
            ld = wing.fuel_efficiency(velocity_ms, payload_kg)
            return -ld if ld > 0 else 1000
        
        result = minimize_scalar(objective, bounds=(1, 25), method='bounded')
        optimal_ar = result.x
        
        optimal_chord = np.sqrt(area_m2 / optimal_ar)
        optimal_span = optimal_ar * optimal_chord
        
        wing = Wing(optimal_span, optimal_chord, mass_kg)
        l_d = wing.fuel_efficiency(velocity_ms, payload_kg)
        
        return {
            'aspect_ratio': optimal_ar,
            'span': optimal_span,
            'chord': optimal_chord,
            'l_d_ratio': l_d,
            'wing': wing
        }
    
    results = calculate_optimal_3d(aircraft_mass, cruise_velocity, payload, wing_area)
    wing = results['wing']
    
    st.success(f"✅ Optimal Design: Span={results['span']:.2f}m | Chord={results['chord']:.2f}m | AR={results['aspect_ratio']:.2f} | L/D={results['l_d_ratio']:.2f}")
    
    st.divider()
    
    # ===== 3D VISUALIZATION TABS =====
    tab1, tab2, tab3, tab4 = st.tabs(["📐 3D Interactive Wing", "🔍 Multi-View Analysis", "⚡ Aerodynamic View", "📊 Aircraft Comparison"])
    
    with tab1:
        st.subheader("Interactive 3D Wing Model")
        st.write("Rotate, zoom, and pan to explore the wing from all angles")
        
        visualizer = Wing3DVisualizer(
            results['span'],
            results['chord'],
            results['aspect_ratio'],
            wing.wing_area
        )
        
        fig_3d = visualizer.create_3d_visualization()
        st.plotly_chart(fig_3d, use_container_width=True)
        
        st.info("""
        **🔵 Upper Surface (Blue):** High-pressure area generating lift
        **🔴 Lower Surface (Red):** Lower-pressure area contributing to lift generation
        
        The wing tapers toward the tips for structural efficiency and better handling.
        """)
    
    with tab2:
        st.subheader("Multi-View Technical Analysis")
        st.write("Isometric, Top, and Side views for technical design review")
        
        fig_multiview = visualizer.create_multiview_comparison()
        st.plotly_chart(fig_multiview, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Span", f"{results['span']:.2f} m")
        with col2:
            st.metric("Chord", f"{results['chord']:.2f} m")
        with col3:
            st.metric("Aspect Ratio", f"{results['aspect_ratio']:.2f}")
    
    with tab3:
        st.subheader("Aerodynamic Properties Visualization")
        st.write("Wing with color-coded lift distribution and performance metrics")
        
        fig_aero = visualizer.create_annotated_view(
            results['l_d_ratio'],
            wing.wing_loading,
            wing.oswald_efficiency_factor()
        )
        st.plotly_chart(fig_aero, use_container_width=True)
        
        st.markdown("""
        **Color Intensity:** Represents lift distribution across the wing
        - **Brighter colors (near root):** Higher lift generation
        - **Darker colors (near tip):** Lower lift generation
        
        This distribution is optimal for minimizing induced drag.
        """)
    
    with tab4:
        st.subheader("Benchmarking Against Real Aircraft")
        
        # Find similar aircraft
        comparison_data, similar_name = AircraftComparison.create_comparison_table(
            results['span'],
            results['chord'],
            results['aspect_ratio'],
            wing.wing_area
        )
        
        # Display comparison table
        st.write(f"**Your design is most similar to: {similar_name}**")
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
        
        st.divider()
        
        # Benchmarking scatter plot
        st.subheader("Design Space Comparison")
        fig_benchmark = AircraftComparison.create_benchmarking_chart(
            results['aspect_ratio'],
            wing.wing_area
        )
        st.plotly_chart(fig_benchmark, use_container_width=True)
        
        st.info(f"""
        **Why {similar_name}?**
        
        Your design's aspect ratio and wing area are closest to this real aircraft.
        This suggests your design would have similar:
        - Structural complexity
        - Cruise characteristics
        - Maneuverability profiles
        
        **Design Placement:**
        - ⭐ **Your Design (RED STAR):** Shows where your optimized design sits in the aircraft design space
        - Other manufacturers' aircraft provide context for what's practically feasible
        """)
    
    st.divider()
    
    # Summary metrics
    st.subheader("📋 Complete Design Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #1a2f1a; padding: 15px; border-radius: 8px; border-left: 4px solid #FF9800;">
            <h4 style="margin: 0; color: #ffcc00;">SPAN (m)</h4>
            <h2 style="margin: 5px 0; color: #00ff99;"><b>{results['span']:.2f}</b></h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: #1a2332; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
            <h4 style="margin: 0; color: #00d4ff;">CHORD (m)</h4>
            <h2 style="margin: 5px 0; color: #00d4ff;"><b>{results['chord']:.2f}</b></h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background-color: #2f1a2f; padding: 15px; border-radius: 8px; border-left: 4px solid #9C27B0;">
            <h4 style="margin: 0; color: #ff00ff;">ASPECT RATIO</h4>
            <h2 style="margin: 5px 0; color: #ff00ff;"><b>{results['aspect_ratio']:.2f}</b></h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background-color: #1a2f1a; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;">
            <h4 style="margin: 0; color: #00ff99;">L/D RATIO</h4>
            <h2 style="margin: 5px 0; color: #00ff99;"><b>{results['l_d_ratio']:.2f}</b></h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Performance Analysis")
        total_weight = (aircraft_mass + payload) * 9.81
        cl_required = (2 * total_weight) / (1.225 * (cruise_velocity ** 2) * wing.wing_area)
        
        st.metric("Status", "✅ Feasible" if cl_required <= wing.lift_coefficient_max() else "❌ Stall Risk")
        st.metric("Wing Loading", f"{wing.wing_loading:.2f} kg/m²")
        st.metric("Oswald Efficiency", f"{wing.oswald_efficiency_factor():.4f}")
    
    with col2:
        st.subheader("Aerodynamic Coefficients")
        st.metric("Max Lift Coefficient", f"{wing.lift_coefficient_max():.2f}")
        st.metric("Parasitic Drag", f"{wing.parasitic_drag_coefficient():.4f}")
        st.metric("Required CL", f"{cl_required:.3f}")

# ============================================================================
# MODE 2: QUICK OPTIMIZER
# ============================================================================
if mode == "🎯 Quick Optimizer":
    st.title("🎯 Quick Wing Optimizer")
    st.write("Automatically find the best wing aspect ratio for your mission")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Mission Selection")
        mission = st.selectbox(
            "Choose Aircraft Mission:",
            ["Glider", "Regional Airliner", "Cargo Transport", "Fighter Jet"],
            index=1
        )
        
        mission_map = {
            "Glider": "glider",
            "Regional Airliner": "regional",
            "Cargo Transport": "cargo",
            "Fighter Jet": "fighter"
        }
        
        mission_key = mission_map[mission]
        
        # Get optimization results
        wing, metrics = optimize_for_mission(mission_key)
        
        st.success(f"✓ Optimized for {mission}")
        
        # Display metrics
        st.metric("Optimal Aspect Ratio", f"{metrics['optimal_aspect_ratio']:.2f}")
        st.metric("Lift-to-Drag Ratio", f"{metrics['fuel_efficiency_ld']:.2f}")
        st.metric("Cruise Speed", f"{metrics['cruise_velocity_ms']} m/s")
    
    with col2:
        st.subheader("Wing Dimensions")
        st.metric("Wing Span", f"{wing.span:.2f} m")
        st.metric("Wing Chord", f"{wing.chord:.2f} m")
        st.metric("Wing Area", f"{wing.wing_area:.2f} m²")
        st.metric("Wing Loading", f"{wing.wing_loading:.2f} kg/m²")
    
    st.divider()
    
    # Visualization
    st.subheader("Efficiency Curves")
    col1, col2 = st.columns(2)
    
    with col1:
        # Plot L/D vs Aspect Ratio for this mission
        ars = np.linspace(2, 20, 100)
        lds = []
        
        mission_params = {
            'glider': {'velocity': 50, 'payload': 200},
            'regional': {'velocity': 120, 'payload': 2500},
            'cargo': {'velocity': 80, 'payload': 5000},
            'fighter': {'velocity': 200, 'payload': 1000}
        }
        
        params = mission_params[mission_key]
        
        for ar in ars:
            chord = np.sqrt(50 / ar) if ar > 0 else 1
            span = ar * chord
            w = Wing(span, chord, 5000)
            ld = w.fuel_efficiency(params['velocity'], params['payload'])
            lds.append(ld)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(ars, lds, linewidth=3, color='#1f77b4', label='L/D Ratio')
        ax.axvline(metrics['optimal_aspect_ratio'], color='red', linestyle='--', 
                   linewidth=2, label=f"Optimal AR = {metrics['optimal_aspect_ratio']:.2f}")
        ax.scatter([metrics['optimal_aspect_ratio']], [metrics['fuel_efficiency_ld']], 
                   color='red', s=200, zorder=5, edgecolors='darkred', linewidth=2)
        ax.set_xlabel('Aspect Ratio', fontsize=12, fontweight='bold')
        ax.set_ylabel('Lift-to-Drag Ratio', fontsize=12, fontweight='bold')
        ax.set_title(f'Efficiency: {mission}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Drag polar
        cl_range = np.linspace(0.1, 1.4, 50)
        cd_values = []
        
        for cl in cl_range:
            cd0 = 0.025
            e = wing.oswald_efficiency_factor()
            ci = (cl ** 2) / (np.pi * wing.aspect_ratio * e)
            cd_values.append(cd0 + ci)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(cd_values, cl_range, linewidth=3, color='#2ca02c', marker='o', markersize=4)
        ax.set_xlabel('Drag Coefficient (CD)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Lift Coefficient (CL)', fontsize=12, fontweight='bold')
        ax.set_title('Drag Polar', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

# ============================================================================
# MODE 3: DEEP LEARNING PREDICTOR
# ============================================================================
if mode == "🤖 Deep Learning Predictor":
    st.title("🤖 Deep Learning Wing Optimizer")
    st.write("AI-powered aspect ratio prediction using neural networks trained on aerodynamic data")
    
    st.divider()
    
    if not dl_available:
        st.error("❌ Deep Learning module requires TensorFlow, which is not available in Python 3.14+")
        st.info("""
        **Why is TensorFlow unavailable?**
        
        TensorFlow doesn't have official support for Python 3.14 yet. However, you can still use all other features:
        - 🧮 Calculate Dimensions (physics-based optimization)
        - 🎨 3D Visualization
        - 🎯 Quick Optimizer
        - 🛠️ Custom Design
        - 📊 Compare Aircraft
        - 📈 Advanced Analysis
        
        **What's available:**
        All the physics-based optimization works perfectly! The DL predictor was meant to provide faster predictions,
        but the traditional aerodynamic methods are accurate and don't require deep learning.
        """)
    else:
        st.success("✅ TensorFlow is available - DL predictor ready!")
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["🎯 Prediction", "📊 Mission Comparison", "ℹ️ Model Info"])
        
        # ================================================================
        # TAB 1: PREDICTION
        # ================================================================
        with tab1:
            st.subheader("AI Aspect Ratio Predictor")
            st.write("Enter aircraft parameters to get optimal wing aspect ratio prediction")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Aircraft Parameters**")
                mass = st.slider("Aircraft Mass (kg)", 1000.0, 500000.0, 5000.0, 100.0)
                speed = st.slider("Cruise Speed (m/s)", 20.0, 300.0, 100.0, 5.0)
            
            with col2:
                st.write("**Flight Environment**")
                altitude = st.slider("Cruise Altitude (m)", 0.0, 15000.0, 3000.0, 500.0)
                mission = st.selectbox("Mission Type", ["Regional", "Cargo", "Fighter", "Glider"])
            
            st.divider()
            
            # Calculate predictions
            col_pred1, col_pred2 = st.columns(2)
            
            with col_pred1:
                # Use DL model if available
                try:
                    dl_optimizer = WingDLOptimizer()
                    dl_optimizer.train()  # Generate and train on synthetic data
                    dl_prediction = dl_optimizer.predict(mass, speed, altitude, mission)
                    
                    st.metric("🤖 DL Predicted AR", f"{dl_prediction:.2f}")
                except Exception as e:
                    st.warning(f"⚠️ DL prediction unavailable: {str(e)}")
                    dl_prediction = None
            
            with col_pred2:
                # Always available: physics-based optimization
                physics_wing, physics_metrics = optimize_for_mission(mission_type=mission.lower(), aircraft_mass=mass)
                st.metric("⚙️ Physics Predicted AR", f"{physics_metrics['optimal_aspect_ratio']:.2f}")
            
            st.divider()
            
            # Create wing with predicted AR and show analysis
            predicted_ar = dl_prediction if dl_prediction else physics_metrics['optimal_aspect_ratio']
            
            # Estimate wing dimensions
            wing_span = np.sqrt(predicted_ar * 360)  # Assume ~360 m² reference area
            wing = Wing(wing_span, wing_span / predicted_ar, mass)
            
            col_analysis1, col_analysis2, col_analysis3, col_analysis4 = st.columns(4)
            
            with col_analysis1:
                st.metric("Aspect Ratio", f"{wing.aspect_ratio:.2f}")
            with col_analysis2:
                st.metric("Wing Span (m)", f"{wing.span:.1f}")
            with col_analysis3:
                st.metric("Wing Area (m²)", f"{wing.wing_area:.1f}")
            with col_analysis4:
                ld_ratio = wing.fuel_efficiency(100)  # Nominal cruise speed
                st.metric("L/D Ratio", f"{ld_ratio:.2f}")
            
            # Aerodynamic performance chart
            st.write("**Aerodynamic Performance at Different Speeds**")
            
            speeds = np.linspace(20, 300, 20)
            lift_drag_ratios = [wing.fuel_efficiency(v) for v in speeds]
            
            if matplotlib_available:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(speeds, lift_drag_ratios, 'o-', linewidth=2.5, markersize=6, color='#00d4ff')
                ax.set_xlabel('Cruise Speed (m/s)', fontsize=12)
                ax.set_ylabel('Lift/Drag Ratio', fontsize=12)
                ax.set_title('Aerodynamic Efficiency vs Flight Speed', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        
        # ================================================================
        # TAB 2: MISSION COMPARISON
        # ================================================================
        with tab2:
            st.subheader("Compare Predictions Across Missions")
            st.write("See how aspect ratio recommendations differ for various mission profiles")
            
            input_col1, input_col2 = st.columns(2)
            
            with input_col1:
                comp_mass = st.slider("Aircraft Mass (kg)", 1000.0, 500000.0, 5000.0, 100.0, key="comp_mass")
                comp_speed = st.slider("Cruise Speed (m/s)", 20.0, 300.0, 100.0, 5.0, key="comp_speed")
            
            with input_col2:
                comp_altitude = st.slider("Cruise Altitude (m)", 0.0, 15000.0, 3000.0, 500.0, key="comp_altitude")
            
            st.divider()
            
            # Compare all missions
            missions = ["Glider", "Regional", "Cargo", "Fighter"]
            comparison_data = []
            
            for m in missions:
                physics_wing, physics_metrics = optimize_for_mission(mission_type=m.lower(), aircraft_mass=comp_mass)
                
                try:
                    dl_opt = WingDLOptimizer()
                    dl_opt.train()
                    dl_ar = dl_opt.predict(comp_mass, comp_speed, comp_altitude, m.lower())
                except:
                    dl_ar = physics_metrics['optimal_aspect_ratio']
                
                comparison_data.append({
                    'Mission': m,
                    'Physics AR': physics_metrics['optimal_aspect_ratio'],
                    'DL AR': dl_ar,
                    'Physics L/D': physics_metrics['fuel_efficiency_ld'],
                    'Difference': abs(dl_ar - physics_metrics['optimal_aspect_ratio'])
                })
            
            df_comparison = pd.DataFrame(comparison_data)
            
            # Display comparison table
            st.dataframe(df_comparison, use_container_width=True)
            
            # Visualization
            if matplotlib_available:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
                
                # AR Comparison
                x_pos = np.arange(len(missions))
                width = 0.35
                ax1.bar(x_pos - width/2, df_comparison['Physics AR'], width, label='Physics', alpha=0.8)
                ax1.bar(x_pos + width/2, df_comparison['DL AR'], width, label='Deep Learning', alpha=0.8)
                ax1.set_xlabel('Mission Type', fontsize=11)
                ax1.set_ylabel('Aspect Ratio', fontsize=11)
                ax1.set_title('Aspect Ratio Comparison by Mission', fontsize=12, fontweight='bold')
                ax1.set_xticks(x_pos)
                ax1.set_xticklabels(missions)
                ax1.legend()
                ax1.grid(True, alpha=0.3, axis='y')
                
                # L/D Comparison
                ax2.bar(missions, df_comparison['Physics L/D'], alpha=0.8, color='#ff7f0e')
                ax2.set_xlabel('Mission Type', fontsize=11)
                ax2.set_ylabel('L/D Ratio', fontsize=11)
                ax2.set_title('Aerodynamic Efficiency by Mission', fontsize=12, fontweight='bold')
                ax2.grid(True, alpha=0.3, axis='y')
                
                plt.tight_layout()
                st.pyplot(fig)
        
        # ================================================================
        # TAB 3: MODEL INFORMATION
        # ================================================================
        with tab3:
            st.subheader("Deep Learning Model Information")
            
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.info("""
                **Model Architecture**
                - Input features: 4 (mass, speed, altitude, mission type)
                - Hidden layers: 3 (128 → 64 → 32 neurons)
                - Output: 1 (optimal aspect ratio)
                - Activation: ReLU (hidden), Linear (output)
                - Optimizer: Adam
                - Loss: Mean Squared Error
                """)
            
            with col_info2:
                st.info("""
                **Training Data**
                - Synthetic samples: 500+
                - Source: Physics-based aerodynamic simulations
                - Features: Mass, speed, altitude, mission type
                - Target: Optimal aspect ratio (0.5 - 25.0)
                - Normalization: StandardScaler
                """)
            
            st.divider()
            
            st.write("**Model Performance Metrics**")
            
            # Generate test predictions to estimate accuracy
            test_configs = [
                {"mass": 5000, "speed": 100, "altitude": 3000, "mission": "Regional"},
                {"mass": 50000, "speed": 200, "altitude": 5000, "mission": "Cargo"},
                {"mass": 2000, "speed": 50, "altitude": 1000, "mission": "Glider"},
                {"mass": 15000, "speed": 250, "altitude": 8000, "mission": "Fighter"},
            ]
            
            test_results = []
            
            try:
                dl_opt = WingDLOptimizer()
                dl_opt.train()
                dl_available_test = True
            except:
                dl_available_test = False
            
            for config in test_configs:
                physics_wing, physics_metrics = optimize_for_mission(
                    mission_type=config["mission"].lower(),
                    aircraft_mass=config["mass"]
                )
                
                if dl_available_test:
                    try:
                        dl_ar = dl_opt.predict(
                            config["mass"],
                            config["speed"],
                            config["altitude"],
                            config["mission"].lower()
                        )
                    except:
                        dl_ar = physics_metrics['optimal_aspect_ratio']
                else:
                    dl_ar = physics_metrics['optimal_aspect_ratio']
                
                error = abs(dl_ar - physics_metrics['optimal_aspect_ratio']) / physics_metrics['optimal_aspect_ratio'] * 100
                
                test_results.append({
                    'Config': f"{config['mission']} ({config['mass']}kg)",
                    'Physics AR': physics_metrics['optimal_aspect_ratio'],
                    'DL AR': dl_ar,
                    'Error %': error
                })
            
            df_test = pd.DataFrame(test_results)
            st.dataframe(df_test, use_container_width=True)
            
            avg_error = df_test['Error %'].mean()
            st.metric("Average prediction error", f"{avg_error:.2f}%", delta="Lower is better")
            
            st.divider()
            
            st.write("**Future Enhancements**")
            st.markdown("""
            - [ ] Real-world flight data integration
            - [ ] Multi-objective optimization (performance vs. weight)
            - [ ] Drag polar prediction
            - [ ] Structural analysis integration
            - [ ] Historical aircraft database
            - [ ] Transfer learning from larger datasets
            """)


# ============================================================================
# MODE 5: CUSTOM DESIGN
# ============================================================================
elif mode == "🛠️ Custom Design":
    st.title("🛠️ Custom Wing Design")
    st.write("Design a custom wing and analyze its performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Wing Dimensions")
        span = st.slider("Wing Span (m)", 5.0, 80.0, 35.0, 1.0)
        chord = st.slider("Wing Chord (m)", 1.0, 15.0, 8.0, 0.5)
        mass = st.slider("Aircraft Mass (kg)", 1000.0, 10000.0, 5000.0, 100.0)
    
    with col2:
        st.subheader("Flight Conditions")
        velocity = st.slider("Cruise Velocity (m/s)", 20.0, 250.0, 100.0, 5.0)
        payload = st.slider("Payload (kg)", 0.0, 10000.0, 1000.0, 100.0)
    
    # Create wing with custom parameters
    wing = Wing(span, chord, mass)
    
    st.divider()
    
    # Display wing properties
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Aspect Ratio", f"{wing.aspect_ratio:.2f}")
    with col2:
        st.metric("Wing Area", f"{wing.wing_area:.2f} m²")
    with col3:
        st.metric("Wing Loading", f"{wing.wing_loading:.2f} kg/m²")
    with col4:
        st.metric("Oswald Efficiency", f"{wing.oswald_efficiency_factor():.3f}")
    
    st.divider()
    
    # Calculate aerodynamic properties
    cl_required = (2 * (mass + payload) * 9.81) / (1.225 * (velocity ** 2) * wing.wing_area)
    
    if cl_required <= wing.lift_coefficient_max():
        lift_n = wing.calculate_lift(velocity, cl_required)
        drag_n = wing.calculate_drag(velocity, cl_required)
        ld = lift_n / drag_n if drag_n > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Lift (kN)", f"{lift_n/1000:.2f}")
        with col2:
            st.metric("Drag (kN)", f"{drag_n/1000:.2f}")
        with col3:
            st.metric("L/D Ratio", f"{ld:.2f}", delta="Higher is better")
        with col4:
            st.metric("CL Required", f"{cl_required:.3f}")
        
        st.success(f"✓ Flight is feasible (CL = {cl_required:.3f} < CL_max = {wing.lift_coefficient_max()})")
    else:
        st.error(f"❌ Flight not feasible - wing cannot generate enough lift (CL required = {cl_required:.3f} > CL_max = {wing.lift_coefficient_max()})")
    
    st.divider()
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Lift and Drag vs Velocity
        velocities = np.linspace(20, 250, 50)
        lifts = []
        drags = []
        
        for v in velocities:
            cl = (2 * (mass + payload) * 9.81) / (1.225 * (v ** 2) * wing.wing_area)
            if cl <= wing.lift_coefficient_max():
                lift = wing.calculate_lift(v, cl)
                drag = wing.calculate_drag(v, cl)
                lifts.append(lift / 1000)
                drags.append(drag / 1000)
            else:
                lifts.append(np.nan)
                drags.append(np.nan)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(velocities, lifts, linewidth=2.5, label='Lift (kN)', color='#1f77b4')
        ax.plot(velocities, drags, linewidth=2.5, label='Drag (kN)', color='#d62728')
        ax.axvline(velocity, color='green', linestyle='--', linewidth=2, alpha=0.7, label=f'Cruise ({velocity} m/s)')
        ax.set_xlabel('Velocity (m/s)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Force (kN)', fontsize=11, fontweight='bold')
        ax.set_title('Lift & Drag vs Velocity', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # L/D vs Velocity
        lds = []
        for v in velocities:
            cl = (2 * (mass + payload) * 9.81) / (1.225 * (v ** 2) * wing.wing_area)
            if cl <= wing.lift_coefficient_max():
                lift = wing.calculate_lift(v, cl)
                drag = wing.calculate_drag(v, cl)
                lds.append(lift / drag if drag > 0 else np.nan)
            else:
                lds.append(np.nan)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(velocities, lds, linewidth=3, color='#2ca02c', marker='o', markersize=3)
        ax.axvline(velocity, color='red', linestyle='--', linewidth=2, alpha=0.7, label=f'Cruise')
        ax.set_xlabel('Velocity (m/s)', fontsize=11, fontweight='bold')
        ax.set_ylabel('L/D Ratio', fontsize=11, fontweight='bold')
        ax.set_title('Efficiency vs Velocity', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)

# ============================================================================
# MODE 6: COMPARE AIRCRAFT
# ============================================================================
elif mode == "📊 Compare Aircraft":
    st.title("📊 Aircraft Comparison")
    st.write("Compare optimal wing designs across different missions")
    
    # Get optimization data for all missions
    missions = ['glider', 'regional', 'cargo', 'fighter']
    mission_names = ['Glider', 'Regional Airliner', 'Cargo Transport', 'Fighter Jet']
    results = []
    
    for mission_key, mission_name in zip(missions, mission_names):
        wing, metrics = optimize_for_mission(mission_key)
        results.append({
            'Mission': mission_name,
            'AR': metrics['optimal_aspect_ratio'],
            'L/D': metrics['fuel_efficiency_ld'],
            'Speed (m/s)': metrics['cruise_velocity_ms'],
            'Span (m)': f"{wing.span:.2f}",
            'Chord (m)': f"{wing.chord:.2f}",
            'Area (m²)': f"{wing.wing_area:.2f}"
        })
    
    df = pd.DataFrame(results)
    
    st.subheader("Summary Table")
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ['#ff7f0e', '#2ca02c', '#d62728', '#1f77b4']
        bars = ax.barh(mission_names, [r['AR'] for r in results], color=colors, edgecolor='black', linewidth=1.5)
        
        for bar, ar in zip(bars, [r['AR'] for r in results]):
            width = bar.get_width()
            ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, f'{ar:.2f}',
                   ha='left', va='center', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('Optimal Aspect Ratio', fontsize=12, fontweight='bold')
        ax.set_title('Optimal Aspect Ratios by Mission', fontsize=13, fontweight='bold')
        ax.set_xlim(0, 27)
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.barh(mission_names, [r['L/D'] for r in results], color=colors, edgecolor='black', linewidth=1.5)
        
        for bar, ld in zip(bars, [r['L/D'] for r in results]):
            width = bar.get_width()
            ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, f'{ld:.2f}',
                   ha='left', va='center', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('Lift-to-Drag Ratio', fontsize=12, fontweight='bold')
        ax.set_title('Fuel Efficiency by Mission', fontsize=13, fontweight='bold')
        ax.set_xlim(0, 23)
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        st.pyplot(fig)
    
    st.divider()
    
    # L/D curves for all missions
    st.subheader("Efficiency Curves - All Missions")
    
    ars = np.linspace(2, 20, 100)
    
    mission_params = {
        'glider': {'velocity': 50, 'payload': 200},
        'regional': {'velocity': 120, 'payload': 2500},
        'cargo': {'velocity': 80, 'payload': 5000},
        'fighter': {'velocity': 200, 'payload': 1000}
    }
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors_line = ['#ff7f0e', '#2ca02c', '#d62728', '#1f77b4']
    
    for (mission_key, mission_name), color in zip(zip(missions, mission_names), colors_line):
        lds = []
        params = mission_params[mission_key]
        
        for ar in ars:
            chord = np.sqrt(50 / ar) if ar > 0 else 1
            span = ar * chord
            w = Wing(span, chord, 5000)
            ld = w.fuel_efficiency(params['velocity'], params['payload'])
            lds.append(ld)
        
        ax.plot(ars, lds, linewidth=2.5, label=mission_name, color=color, marker='o', markersize=2, markevery=10)
    
    ax.set_xlabel('Aspect Ratio', fontsize=12, fontweight='bold')
    ax.set_ylabel('Lift-to-Drag Ratio (L/D)', fontsize=12, fontweight='bold')
    ax.set_title('Fuel Efficiency Comparison Across All Missions', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 25)
    plt.tight_layout()
    st.pyplot(fig)

# ============================================================================
# MODE 7: ADVANCED ANALYSIS
# ============================================================================
elif mode == "📈 Advanced Analysis":
    st.title("📈 Advanced Analysis")
    st.write("Deep dive into aerodynamic relationships and trade-offs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        aspect_ratio = st.slider("Aspect Ratio", 2.0, 20.0, 10.0, 0.5)
    with col2:
        velocity = st.slider("Velocity (m/s)", 20, 300, 100, 10)
    with col3:
        mass = st.slider("Total Mass (kg)", 1000, 10000, 5000, 100)
    
    # Create wing with constant area
    wing_area = 50
    chord = np.sqrt(wing_area / aspect_ratio)
    span = aspect_ratio * chord
    wing = Wing(span, chord, mass)
    
    st.divider()
    
    # Display detailed properties
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Wing Geometry")
        st.metric("Aspect Ratio", f"{wing.aspect_ratio:.2f}")
        st.metric("Span", f"{wing.span:.2f} m")
        st.metric("Chord", f"{wing.chord:.2f} m")
    
    with col2:
        st.subheader("Aerodynamic Coefficients")
        st.metric("Oswald Efficiency (e)", f"{wing.oswald_efficiency_factor():.4f}")
        st.metric("Parasitic Drag (CD0)", f"{wing.parasitic_drag_coefficient():.4f}")
        st.metric("Max Lift Coefficient", f"{wing.lift_coefficient_max():.2f}")
    
    with col3:
        st.subheader("Loading & Efficiency")
        st.metric("Wing Loading", f"{wing.wing_loading:.2f} kg/m²")
        ld = wing.fuel_efficiency(velocity, 1000)
        st.metric("L/D @ Cruise", f"{ld:.2f}")
    
    st.divider()
    
    # Drag breakdown
    st.subheader("Drag Polars & Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Drag Polar Curve**")
        cl_range = np.linspace(0, 1.5, 50)
        cd_values = []
        cd0_values = []
        ci_values = []
        
        for cl in cl_range:
            cd0 = wing.parasitic_drag_coefficient()
            e = wing.oswald_efficiency_factor()
            ci = (cl ** 2) / (np.pi * wing.aspect_ratio * e)
            cd = cd0 + ci
            cd_values.append(cd)
            cd0_values.append(cd0)
            ci_values.append(ci)
        
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.plot(cd_values, cl_range, linewidth=3, color='#1f77b4', label='Total Drag (CD)')
        ax.plot(cd0_values, cl_range, linewidth=2, linestyle='--', color='#ff7f0e', label='Parasitic (CD₀)')
        ax.plot(ci_values, cl_range, linewidth=2, linestyle='--', color='#2ca02c', label='Induced (CDᵢ)')
        ax.set_xlabel('Drag Coefficient', fontsize=11, fontweight='bold')
        ax.set_ylabel('Lift Coefficient (CL)', fontsize=11, fontweight='bold')
        ax.set_title('Drag Polar', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.write("**Induced Drag vs AR**")
        ar_range = np.linspace(1, 25, 100)
        cl_fixed = 0.5
        induced_drag = []
        
        for ar in ar_range:
            e = 0.95
            ci = (cl_fixed ** 2) / (np.pi * ar * e)
            induced_drag.append(ci)
        
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.plot(ar_range, induced_drag, linewidth=3, color='#d62728')
        ax.axvline(aspect_ratio, color='green', linestyle='--', linewidth=2, alpha=0.7, label=f'Current AR ({aspect_ratio:.1f})')
        ax.scatter([aspect_ratio], [(cl_fixed**2)/(np.pi*aspect_ratio*0.95)], 
                  color='green', s=150, zorder=5, edgecolors='darkgreen', linewidth=2)
        ax.set_xlabel('Aspect Ratio', fontsize=11, fontweight='bold')
        ax.set_ylabel('Induced Drag Coefficient', fontsize=11, fontweight='bold')
        ax.set_title(f'Induced Drag (CL = {cl_fixed})', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col3:
        st.write("**L/D Envelope**")
        velocities = np.linspace(30, 300, 100)
        lds = []
        
        for v in velocities:
            cl = (2 * (mass + 1000) * 9.81) / (1.225 * (v ** 2) * wing.wing_area)
            if cl <= wing.lift_coefficient_max():
                ld = wing.fuel_efficiency(v, 1000)
                lds.append(ld)
            else:
                lds.append(np.nan)
        
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.plot(velocities, lds, linewidth=3, color='#2ca02c')
        ax.axvline(velocity, color='red', linestyle='--', linewidth=2, alpha=0.7, label=f'Cruise ({velocity} m/s)')
        ld_cruise = wing.fuel_efficiency(velocity, 1000)
        ax.scatter([velocity], [ld_cruise], color='red', s=150, zorder=5, edgecolors='darkred', linewidth=2)
        ax.set_xlabel('Velocity (m/s)', fontsize=11, fontweight='bold')
        ax.set_ylabel('L/D Ratio', fontsize=11, fontweight='bold')
        ax.set_title('Efficiency Envelope', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 20)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.divider()
    
    # Physics insights
    st.subheader("📚 Physics Insights")
    
    e = wing.oswald_efficiency_factor()
    induced_drag_coeff = (0.5 ** 2) / (np.pi * aspect_ratio * e)
    parasitic = wing.parasitic_drag_coefficient()
    
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        st.info(f"""
        **Induced Drag Explanation:**
        
        The dominant drag component at cruise speeds depends on aspect ratio:
        
        $$C_{{D,i}} = \\frac{{C_L^2}}{{\\pi AR \\cdot e}}$$
        
        Current values:
        - Aspect Ratio: {aspect_ratio:.2f}
        - Oswald Efficiency: {e:.3f}
        - Induced Drag (CL=0.5): {induced_drag_coeff:.5f}
        
        **Key insight:** Every doubling of AR cuts induced drag in half!
        """)
    
    with insight_col2:
        st.info(f"""
        **Trade-off Analysis:**
        
        **High AR (12-20):**
        ✓ Lower induced drag
        ✓ Better fuel efficiency (higher L/D)
        ✗ Heavier wing structure
        ✗ Slower response to controls
        ✗ Taller landing gear needed
        
        **Low AR (4-6):**
        ✓ Faster responses
        ✓ Simpler structure
        ✗ Higher induced drag
        ✗ More fuel needed
        ✗ Limited range
        """)

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Aircraft Wing Aspect Ratio Optimization</strong></p>
        <p>Interactive analysis tool for aerodynamic design optimization</p>
        <small>Powered by NumPy, Matplotlib, SciPy, and Streamlit</small>
    </div>
""", unsafe_allow_html=True)

# 🖥️ Wing Optimization UI - User Guide

## Quick Start

### Option 1: Double-Click to Launch (Windows)
Simply double-click **`run_ui.bat`** in the project folder. The UI will automatically open in your default browser.

### Option 2: Command Line
```bash
streamlit run app.py
```

The UI will open at: **http://localhost:8501**

---

## 🎯 Features Overview

### **1️⃣ Quick Optimizer**
- Instantly find the best aspect ratio for your mission
- Choose from: Glider, Regional Airliner, Cargo Transport, Fighter Jet
- See optimal dimensions and efficiency metrics
- Interactive efficiency curves with optimization point marked

### **2️⃣ Custom Design**
- Design your own wing with exact specifications
- Adjust: Wing span, chord, aircraft mass, velocity, payload
- Real-time aerodynamic calculations
- Visual feedback: Can it fly or will it stall?
- Performance curves at different speeds
- Lift, Drag, and L/D ratio display

### **3️⃣ Compare Aircraft**
- Side-by-side comparison of all mission types
- Summary table with dimensions and efficiency
- Bar charts comparing aspect ratios and L/D ratios
- Overlay efficiency curves for all missions
- Identify optimal designs at a glance

### **4️⃣ Advanced Analysis**
- Deep dive into aerodynamic relationships
- Adjust AR, velocity, and mass with sliders
- View drag polars (lift vs drag coefficient)
- Induced drag vs aspect ratio curves
- L/D efficiency envelopes
- Physics explanations with equations
- Trade-off analysis insights

---

## 📊 What Each Chart Shows

### **L/D Curve**
- Shows how efficiency changes with aspect ratio
- Higher curves = better fuel efficiency
- Red dot marks the optimal design point

### **Drag Polar**
- Visualizes the relationship between lift and drag
- Separate lines for total, parasitic, and induced drag
- Helps understand drag components

### **Efficiency Envelope**
- Shows optimal efficiency at different speeds
- Higher L/D = lower fuel consumption
- Shows the "sweet spot" for cruise speed

### **Drag Coefficient vs AR**
- Demonstrates why high AR improves efficiency
- Inverse relationship: Higher AR → Lower drag
- Visual proof of the aerodynamic principle

---

## 🎓 Key Learnings

From the UI, you'll discover:

✅ **High Aspect Ratio Benefits:**
- Much better fuel efficiency (higher L/D)
- Can fly longer on same fuel
- Best for: Gliders, cargo, commercial aircraft

❌ **High Aspect Ratio Drawbacks:**
- Heavier wing structure
- Slower maneuverability
- Needs taller landing gear

✅ **Low Aspect Ratio Benefits:**
- Lighter structure
- Faster control response
- Better for high-speed flight

❌ **Low Aspect Ratio Drawbacks:**
- More induced drag
- Higher fuel consumption
- Limited range

---

## 🧮 The Math Behind It

The key equation shown throughout:

$$C_D = C_{D0} + \frac{C_L^2}{\pi \cdot AR \cdot e}$$

This shows:
- **Parasitic drag (C_D0)**: Independent of lift, depends on speed
- **Induced drag**: Inverse proportion to AR - **this is why AR matters!**

For every doubling of aspect ratio, you cut induced drag in half.

---

## 💡 Tips for Using the UI

1. **Quick Optimizer**: Start here to understand what's optimal for each mission type

2. **Custom Design**: Use sliders to explore "what if" scenarios
   - Try different wing sizes with same payload
   - See how speed affects efficiency
   - Find the feasible flight envelope

3. **Compare Aircraft**: Understand why real aircraft have their current designs
   - Gliders: AR very high → max efficiency
   - Fighters: AR very low → agility over efficiency
   - Commercial: AR moderate → balance both

4. **Advanced Analysis**: Dig into the physics
   - Watch how induced drag changes with AR
   - See the trade-off between speed and efficiency
   - Understand Oswald efficiency factor

---

## 🔧 Customization

Want to modify the UI? Edit **`app.py`**:

- Change color scheme (look for hex colors like `#1f77b4`)
- Add new missions (modify `mission_params` dictionaries)
- Adjust slider ranges for different analyses
- Add new visualization types

---

## ⚙️ System Requirements

- Python 3.8+
- Windows 10/11
- Internet browser (for web UI)

All dependencies are already installed in the virtual environment.

---

## 🆘 Troubleshooting

**"Cannot find streamlit"**
```bash
pip install streamlit
```

**"Port 8501 already in use"**
```bash
streamlit run app.py --server.port 8502
```

**"ModuleNotFoundError: wing_properties"**
- Make sure `run_ui.bat` or terminal is in the same directory as `wing_properties.py`

---

## 📞 Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `R` | Rerun app |
| `C` | Clear cache |
| `K` | Open command menu |

---

## 🚀 Next Steps

1. **Explore Quick Optimizer** to see optimal designs
2. **Try Custom Design** with different parameters
3. **Compare Aircraft** to understand real-world choices
4. **Dive into Advanced Analysis** for physics insights

Enjoy exploring aerodynamic optimization! ✈️

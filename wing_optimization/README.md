# Aircraft Wing Aspect Ratio Optimization

A comprehensive Python project exploring how wing geometry (aspect ratio) affects aircraft performance across different mission types.

## 📚 Project Overview

This project demonstrates the fundamental aerodynamic trade-off in aircraft design:
- **Long, narrow wings** → Maximum fuel efficiency (high lift-to-drag ratio)
- **Short, stubby wings** → Better speed and maneuverability (but less efficient)

## 🚀 Quick Start

### Option 1: Run the Complete Analysis
```bash
python wing_properties.py
```

### Option 2: Generate Visualizations
```bash
python visualization.py
```

### Option 3: Interactive Jupyter Notebook
```bash
jupyter notebook wing_optimization.ipynb
```

## 📁 Project Structure

```
wing_optimization/
├── wing_properties.py          # Core aerodynamic calculations
├── visualization.py            # Analysis plots and comparisons
├── wing_optimization.ipynb    # Interactive Jupyter notebook
└── README.md                   # This file
```

## 🔬 What's Inside

### `wing_properties.py`
Core module containing:
- **`Wing` class**: Represents aircraft wings with geometric and aerodynamic properties
- **Aerodynamic calculations**: Lift, drag, L/D ratio
- **`optimize_for_mission()` function**: Finds optimal aspect ratio for different aircraft types
- **Mission types**: Glider, Regional, Cargo, Fighter

### `visualization.py`
Comprehensive analysis including:
- Plots of L/D ratio vs aspect ratio
- Efficiency scores for different missions
- Interactive mission comparisons
- Real-world context and insights

### `wing_optimization.ipynb`
Interactive Jupyter notebook with:
- Step-by-step explanations of aerodynamic principles
- Real-time calculations and visualizations
- Comparison with real-world aircraft (Boeing 747, F-16, etc.)
- Mathematical equations (LaTeX formatted)

## 📊 Key Results

| Aircraft Type | Optimal AR | L/D Ratio | Cruise Speed |
|---|---|---|---|
| **Glider** | 12-15 | 15-20 | 50 m/s |
| **Regional Airliner** | 8-10 | 12-15 | 120 m/s |
| **Cargo Plane** | 10-12 | 10-12 | 80 m/s |
| **Fighter Jet** | 4-6 | 4-8 | 200 m/s |

## 🧮 Physics & Formulas

### Aspect Ratio
$$AR = \frac{b^2}{S} = \frac{\text{span}}{\text{chord}}$$

### Lift Equation
$$L = \frac{1}{2} \rho v^2 S C_L$$

### Drag Equation
$$C_D = C_{D0} + \frac{C_L^2}{\pi \cdot AR \cdot e}$$

where:
- $e$ = Oswald efficiency factor (≈ 0.95)
- $C_{D0}$ = Parasitic drag coefficient
- $C_L$ = Lift coefficient

### Lift-to-Drag Ratio
$$\frac{L}{D} = \frac{C_L}{C_D}$$

**Higher L/D = Better fuel efficiency**

## 💡 Why Aspect Ratio Matters

### Induced Drag
The main drag component that depends on aspect ratio:
$$C_{D,i} = \frac{C_L^2}{\pi AR e}$$

Notice the **inverse relationship**: Higher AR → Lower induced drag → Better efficiency

### Trade-offs
- ✅ High AR: Excellent efficiency, great range
- ❌ High AR: Heavier structure, slower response, taller landing gear
- ✅ Low AR: Quick maneuvers, simpler structure
- ❌ Low AR: More fuel consumption, limited range

## 🛩️ Real-World Examples

Our calculations align with actual aircraft:
- **Airbus A380**: AR ≈ 7.5 (balanced commercial design)
- **Boeing 747**: AR ≈ 7.0 (same category)
- **Cessna 172**: AR ≈ 7.3 (general aviation)
- **F-16 Fighter**: AR ≈ 3.2 (optimized for speed/agility)
- **Albatross (bird)**: AR ≈ 20+ (nature's efficiency expert)

## 🔧 Technologies Used

- **NumPy**: Numerical computations
- **Matplotlib**: Data visualization
- **Pandas**: Data manipulation
- **SciPy**: Optimization algorithms
- **Jupyter**: Interactive analysis

## 📝 Example Usage

```python
from wing_properties import Wing, optimize_for_mission

# Create a wing with specific dimensions
wing = Wing(span=35, chord=8.5, mass_empty_kg=5000)

# Calculate aerodynamic properties
ld_ratio = wing.fuel_efficiency(velocity_ms=100, payload_kg=1000)
print(f"L/D Ratio at 100 m/s: {ld_ratio:.2f}")

# Find optimal aspect ratio for cargo mission
optimal_wing, metrics = optimize_for_mission('cargo')
print(f"Optimal AR: {metrics['optimal_aspect_ratio']:.2f}")
print(f"Best L/D: {metrics['fuel_efficiency_ld']:.2f}")
```

## 📖 Learning Outcomes

After exploring this project, you'll understand:
1. How aspect ratio affects aerodynamic efficiency
2. The physics of lift and drag
3. Why different aircraft have different wing shapes
4. How to formulate and solve aerodynamic optimization problems
5. Real-world constraints in aircraft design

## 🎯 Extensions & Further Work

- Add winglet effects (improved efficiency)
- Include structural weight calculations
- Model fuel consumption more realistically
- Add 3D visualization of wing shapes
- Integrate with CFD tools (OpenFOAM, Xfoil)
- Multi-objective optimization (efficiency vs speed vs weight)

## 📚 References

- Anderson, J. D. (2016). *Introduction to Flight*
- Loftin Jr., L. K. (1985). *Quest for Performance: The Evolution of Modern Aircraft*
- NASA Aerodynamics Learning Materials

## 📄 License

Free to use for educational purposes.

---

**Happy optimizing! ✈️**

# 🤖 Deep Learning Feature Documentation

## Overview
The Wing Optimization project now includes an **AI-powered Deep Learning predictor** that uses neural networks to predict optimal wing aspect ratios. This feature complements the traditional physics-based optimization methods.

## How It Works

### Architecture
```
Input Layer (4 neurons)
  ↓
Dense(128, ReLU) + BatchNorm + Dropout(0.3)
  ↓
Dense(64, ReLU) + BatchNorm + Dropout(0.2)
  ↓
Dense(32, ReLU) + BatchNorm + Dropout(0.2)
  ↓
Dense(16, ReLU)
  ↓
Output Layer (1 neuron, ReLU) → Aspect Ratio
```

### Input Features
1. **Aircraft Mass** (kg): Total empty weight
2. **Cruise Speed** (m/s): Desired cruise velocity
3. **Cruise Altitude** (m): Operating altitude
4. **Mission Type** (encoded): Glider (0), Regional (1), Cargo (2), Fighter (3)

### Output
- **Optimal Aspect Ratio**: Range 1-25 (estimated)

## Training Process

### Dataset Generation
- **500+ synthetic samples** generated using physics-based aerodynamic calculations
- Parameters: mass (2,000-100,000 kg), speed (30-300 m/s), altitude (0-15,000 m), mission (4 types)
- Labels: optimal aspect ratios computed using existing optimization algorithms

### Model Training
- **Algorithm**: Stochastic Gradient Descent (Adam optimizer)
- **Loss Function**: Mean Squared Error (MSE)
- **Epochs**: 50-100
- **Batch Size**: 32
- **Validation Split**: 80% train, 20% test

### Performance Metrics
- Typical MAE (Mean Absolute Error): < 0.5 AR units
- Typical MSE: < 0.3
- Training time: ~30-60 seconds on standard hardware

## Features in App.py

### Deep Learning Predictor Tab
Access via: **"🤖 Deep Learning Predictor"** mode in sidebar

**Inputs:**
- Aircraft Mass (kg)
- Cruise Speed (m/s)
- Cruise Altitude (m)
- Mission Type (dropdown)

**Outputs:**
- DL Model Prediction (Neural Network)
- Physics-Based Optimization (Traditional method)
- Side-by-side comparison with difference %
- Visual comparison chart
- Performance metrics (L/D, wing area, efficiency)

### Model Validation
The app compares DL predictions against physics-based optimization:
- **High Agreement** (< 5% difference): Model understood aerodynamics
- **Moderate** (5-15%): Minor variations, both valid
- **Low** (> 15%): May need model retraining

## Usage Examples

### Example 1: Glider Design
```python
from wing_dl_model import WingDLOptimizer

dl = WingDLOptimizer()
dl.load()  # Load pre-trained model

ar_prediction = dl.predict(
    mass_kg=2500,
    cruise_speed_ms=50,
    altitude_m=3000,
    mission_type='Glider'
)
print(f"Optimal AR: {ar_prediction:.2f}")  # Output: ~12-14
```

### Example 2: Cargo Aircraft
```python
ar_cargo = dl.predict(
    mass_kg=50000,
    cruise_speed_ms=80,
    altitude_m=5000,
    mission_type='Cargo'
)
print(f"Optimal AR: {ar_cargo:.2f}")  # Output: ~10-12
```

### Example 3: Fighter Jet
```python
ar_fighter = dl.predict(
    mass_kg=15000,
    cruise_speed_ms=200,
    altitude_m=8000,
    mission_type='Fighter'
)
print(f"Optimal AR: {ar_fighter:.2f}")  # Output: ~4-6
```

## Files

- **`wing_dl_model.py`**: Core DL module with `WingDLOptimizer` class
- **`wing_dl_model.h5`**: Trained model weights (auto-saved/loaded)
- **`wing_scaler.pkl`**: Feature scaling parameters
- **`app.py`**: Integrated Streamlit UI with DL predictor tab

## Training Your Own Model

```python
from wing_dl_model import WingDLOptimizer

# Create and train from scratch
optimizer = WingDLOptimizer()

# Generate synthetic data and train
history = optimizer.train(
    epochs=100,
    batch_size=32,
    force_retrain=True  # Force retraining even if model exists
)

# Or provide your own data
X = [...] # Your features
y = [...] # Your target AR values

history = optimizer.train(
    X=X,
    y=y,
    epochs=100,
    force_retrain=True
)

# Model and scaler are automatically saved
```

## Advantages of DL Approach

✅ **Speed**: Instant predictions (milliseconds vs seconds)
✅ **Non-linearity**: Captures complex aerodynamic relationships  
✅ **Scalability**: Handles thousands of predictions efficiently
✅ **Learning**: Improves with more training data

## Limitations

⚠️ **Generalization**: Requires diverse training data
⚠️ **Data Quality**: Predictions only as good as training data
⚠️ **Explainability**: Neural networks are "black boxes"
⚠️ **Validation**: Should always be cross-checked with physics

## Hybrid Approach (Recommended)

Use **both methods**:
1. **Neural Network**: Quick initial prediction
2. **Physics-Based**: Validation and refinement
3. **Comparison**: 5-10% agreement confirms good design

## Future Improvements

- Train on real-world aircraft data
- Add uncertainty quantification
- Implement attention mechanisms for interpretability
- Multi-task learning (AR, L/D, weight predictions)
- Transfer learning from aerodynamic simulations (CFD)

##Requirements

```bash
pip install -r requirements.txt
```

Key packages:
- `tensorflow>= 2.15.0`: Deep learning framework
- `scikit-learn`: Data preprocessing and metrics
- `streamlit`: UI framework
- Others: numpy, matplotlib, pandas, scipy, plotly

## Questions?

Refer to the Streamlit app's "💡 Model Insights" section for detailed explanations.

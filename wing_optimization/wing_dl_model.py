"""
Deep Learning Model for Wing Optimization
Predicts optimal aspect ratios using neural networks trained on aerodynamic data
"""

import numpy as np
import pandas as pd
from wing_properties import Wing, optimize_for_mission
import pickle
import os
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Lazy imports for tensorflow - only import when needed
tensorflow_available = False
keras_available = False

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    tensorflow_available = True
    keras_available = True
except ImportError:
    pass


class WingDLOptimizer:
    """Deep learning-based wing optimization predictor"""
    
    def __init__(self, model_path='wing_dl_model.h5', scaler_path='wing_scaler.pkl'):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.feature_names = ['mass_kg', 'cruise_speed_ms', 'cruise_altitude_m', 'mission_type_encoded']
        
    def generate_training_data(self, n_samples=500):
        """
        Generate synthetic training data using physics-based calculations
        
        Args:
            n_samples: Number of training samples to generate
            
        Returns:
            X: Training features (mass, speed, altitude, mission)
            y: Target optimal aspect ratios
        """
        np.random.seed(42)
        
        # Define ranges for parameters
        masses = np.random.uniform(2000, 100000, n_samples)  # kg
        speeds = np.random.uniform(30, 300, n_samples)  # m/s
        altitudes = np.random.uniform(0, 15000, n_samples)  # meters
        missions = np.random.randint(0, 4, n_samples)  # 0=Glider, 1=Regional, 2=Cargo, 3=Fighter
        
        X = np.column_stack([masses, speeds, altitudes, missions])
        y = []
        
        print(f"Generating {n_samples} training samples...")
        mission_names = ['Glider', 'Regional', 'Cargo', 'Fighter']
        
        for i, (mass, speed, altitude, mission) in enumerate(zip(masses, speeds, altitudes, missions)):
            if i % 100 == 0:
                print(f"  Sample {i}/{n_samples}")
            
            # Use physics-based optimization to get optimal AR
            mission_key = mission_names[mission]
            
            # Call optimize_for_mission with correct parameters
            wing, metrics = optimize_for_mission(mission_type=mission_key.lower(), aircraft_mass=int(mass))
            optimal_ar = metrics.get('optimal_aspect_ratio', 8.0)
            
            y.append(optimal_ar)
        
        y = np.array(y)
        print("Training data generation complete!")
        return X, y
    
    def build_model(self, input_shape=4):
        """
        Build neural network model for aspect ratio prediction
        
        Args:
            input_shape: Number of input features
            
        Returns:
            Compiled Keras model
        """
        if not tensorflow_available or not keras_available:
            raise ImportError("TensorFlow and Keras are required for DL model. Install with: pip install tensorflow")
        
        model = keras.Sequential([
            layers.Input(shape=(input_shape,)),
            
            # First dense block
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Second dense block
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Third dense block
            layers.Dense(32, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Output layer (aspect ratio prediction)
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='relu')  # AR is always positive
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']  # Only use mae to avoid Keras 3.x serialization issues
        )
        
        return model
    
    def train(self, X=None, y=None, epochs=100, batch_size=32, force_retrain=False):
        """
        Train the deep learning model
        
        Args:
            X: Training features (if None, generates synthetic data)
            y: Training targets (if None, generates synthetic data)
            epochs: Number of training epochs
            batch_size: Batch size for training
            force_retrain: Force retraining even if model exists
        """
        # Check if model already exists
        if os.path.exists(self.model_path) and not force_retrain:
            print(f"Model already exists at {self.model_path}")
            self.load()
            return
        
        # Generate training data if not provided
        if X is None or y is None:
            X, y = self.generate_training_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Build and train model
        self.model = self.build_model(input_shape=X_train_scaled.shape[1])
        
        print("Training model...")
        history = self.model.fit(
            X_train_scaled, y_train,
            validation_data=(X_test_scaled, y_test),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0
        )
        
        # Evaluate
        test_loss, test_mae = self.model.evaluate(X_test_scaled, y_test, verbose=0)
        print(f"\nTraining complete!")
        print(f"Test MAE: {test_mae:.4f}")
        print(f"Test Loss (MSE): {test_loss:.4f}")
        
        # Save model and scaler
        self.save()
        
        return history
    
    def predict(self, mass_kg, cruise_speed_ms, altitude_m=0, mission_type='Regional'):
        """
        Predict optimal aspect ratio for given parameters
        
        Args:
            mass_kg: Aircraft mass in kg
            cruise_speed_ms: Cruise speed in m/s
            altitude_m: Cruise altitude in meters
            mission_type: One of ['Glider', 'Regional', 'Cargo', 'Fighter']
            
        Returns:
            Predicted optimal aspect ratio
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model not loaded. Call train() or load() first.")
        
        # Encode mission type
        mission_map = {'Glider': 0, 'Regional': 1, 'Cargo': 2, 'Fighter': 3}
        mission_encoded = mission_map.get(mission_type, 1)
        
        # Create input
        X = np.array([[mass_kg, cruise_speed_ms, altitude_m, mission_encoded]])
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled, verbose=0)[0][0]
        return float(prediction)
    
    def save(self):
        """Save model and scaler to disk"""
        if self.model is None:
            raise ValueError("No model to save. Train first.")
        
        self.model.save(self.model_path)
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"Model saved to {self.model_path}")
        print(f"Scaler saved to {self.scaler_path}")
    
    def load(self):
        """Load model and scaler from disk"""
        if not tensorflow_available or not keras_available:
            raise ImportError("TensorFlow and Keras are required. Install with: pip install tensorflow")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        try:
            # Suppress TensorFlow warnings during model loading to avoid Keras 3.x deserialization issues
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                self.model = keras.models.load_model(self.model_path, compile=False)
                # Recompile with compatible metrics
                self.model.compile(
                    optimizer=keras.optimizers.Adam(learning_rate=0.001),
                    loss='mse',
                    metrics=['mae']
                )
        except Exception as e:
            # If loading fails, raise with clearer message
            raise RuntimeError(f"Failed to load DL model. This is expected with certain TensorFlow versions. Details: {str(e)}")
        
        if os.path.exists(self.scaler_path):
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
        
        print(f"Model loaded from {self.model_path}")
        return self.model


def compare_predictions(mass_kg, cruise_speed_ms, altitude_m=0, mission_type='Regional'):
    """
    Compare predictions from physics-based and DL methods
    
    Args:
        mass_kg: Aircraft mass in kg
        cruise_speed_ms: Cruise speed in m/s
        altitude_m: Cruise altitude in meters
        mission_type: Mission type
        
    Returns:
        Dictionary with both predictions and comparison
    """
    # Physics-based prediction
    wing = Wing(span=40, chord=20, mass_empty_kg=int(mass_kg))
    physics_ar, physics_ld = optimize_for_mission(wing, mission_type, cruise_speed_ms)
    
    # DL prediction
    try:
        dl_optimizer = WingDLOptimizer()
        dl_optimizer.load()
        dl_ar = dl_optimizer.predict(mass_kg, cruise_speed_ms, altitude_m, mission_type)
    except:
        dl_ar = None
    
    result = {
        'physics_ar': physics_ar,
        'physics_ld': physics_ld,
        'dl_ar': dl_ar,
        'difference_percent': None
    }
    
    if dl_ar is not None:
        result['difference_percent'] = abs(dl_ar - physics_ar) / physics_ar * 100
    
    return result

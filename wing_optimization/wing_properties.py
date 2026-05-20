"""
Wing Aspect Ratio Optimization Module
Calculates aerodynamic properties based on wing geometry
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar, minimize


class Wing:
    """Represents an aircraft wing and its aerodynamic properties"""
    
    def __init__(self, span, chord, mass_empty_kg=5000):
        """
        Initialize a wing
        
        Args:
            span: Wing span in meters (length, tip to tip)
            chord: Average chord (width) in meters
            mass_empty_kg: Empty aircraft mass in kg
        """
        self.span = span
        self.chord = chord
        self.mass_empty_kg = mass_empty_kg
        self.mass = mass_empty_kg  # Alias for compatibility
        self.aspect_ratio = span / chord
        self.wing_area = span * chord
        self.wing_loading = mass_empty_kg / self.wing_area
        
    def __repr__(self):
        return f"Wing(AR={self.aspect_ratio:.2f}, Area={self.wing_area:.2f}m²)"
    
    # Aerodynamic constants
    AIR_DENSITY = 1.225  # kg/m³ at sea level
    SPEED_OF_SOUND = 343  # m/s at sea level
    
    def lift_coefficient_ideal(self):
        """
        Ideal lift coefficient (simplified)
        Higher aspect ratio = more efficient lift generation
        """
        return 1.2 + (0.15 * np.log(self.aspect_ratio + 1))
    
    def lift_coefficient_max(self):
        """Maximum lift coefficient before stall"""
        return 1.5
    
    def parasitic_drag_coefficient(self):
        """Parasite drag coefficient (zero-lift drag) - mainly friction"""
        return 0.025
    
    def oswald_efficiency_factor(self):
        """Oswald efficiency factor - accounts for real-world losses"""
        return 0.95 * (1 - 0.02 * np.exp(-0.02 * self.aspect_ratio))
    
    def drag_coefficient(self, lift_coeff):
        """
        Compute drag coefficient using lift-induced drag equation
        Oswald efficiency factor accounts for real-world losses
        
        CD = CD0 + (CL^2) / (π * AR * e)
        """
        cd0 = self.parasitic_drag_coefficient()
        oswald_efficiency = self.oswald_efficiency_factor()
        
        induced_drag = (lift_coeff ** 2) / (np.pi * self.aspect_ratio * oswald_efficiency)
        total_cd = cd0 + induced_drag
        return total_cd
    
    def calculate_lift(self, velocity_ms, lift_coeff):
        """
        Calculate lift force
        Lift = 0.5 * ρ * V² * S * CL
        where ρ = air density, V = velocity, S = wing area, CL = lift coefficient
        """
        lift_n = 0.5 * self.AIR_DENSITY * (velocity_ms ** 2) * self.wing_area * lift_coeff
        return lift_n
    
    def calculate_drag(self, velocity_ms, lift_coeff):
        """
        Calculate drag force
        Drag = 0.5 * ρ * V² * S * CD
        """
        cd = self.drag_coefficient(lift_coeff)
        drag_n = 0.5 * self.AIR_DENSITY * (velocity_ms ** 2) * self.wing_area * cd
        return drag_n
    
    def fuel_efficiency(self, velocity_ms, payload_kg=1000):
        """
        Calculate fuel efficiency (lift-to-drag ratio at a given speed)
        This approximates fuel consumption efficiency
        
        Higher L/D = better fuel efficiency
        Assumes level flight: Lift ≈ Weight
        """
        total_weight = (self.mass_empty_kg + payload_kg) * 9.81  # Convert to Newtons
        
        # For level flight, we need lift = weight
        # CL = 2 * Weight / (ρ * V² * S)
        lift_coeff = (2 * total_weight) / (self.AIR_DENSITY * (velocity_ms ** 2) * self.wing_area)
        
        # Clamp CL to realistic values
        if lift_coeff > self.lift_coefficient_max():
            return 0  # Stall condition, not feasible
        
        lift_n = self.calculate_lift(velocity_ms, lift_coeff)
        drag_n = self.calculate_drag(velocity_ms, lift_coeff)
        
        if drag_n == 0:
            return float('inf')
        
        l_d_ratio = lift_n / drag_n
        return l_d_ratio
    
    def max_lift_capability(self, velocity_ms):
        """
        Maximum lift achievable at a given speed
        (before stall, typically CL_max ≈ 1.5)
        """
        cl_max = self.lift_coefficient_max()
        max_lift = self.calculate_lift(velocity_ms, cl_max)
        return max_lift
    
    def cruise_efficiency_score(self, cruise_velocity_ms=100, payload_kg=1000):
        """
        Efficiency score for cruising (0-100)
        Combines fuel efficiency and lift capability
        """
        l_d = self.fuel_efficiency(cruise_velocity_ms, payload_kg)
        max_lift = self.max_lift_capability(cruise_velocity_ms)
        total_weight_n = (self.mass_empty_kg + payload_kg) * 9.81
        
        if l_d <= 0:
            return 0
        
        # Normalize: ideal L/D ≈ 15, good ranges 10-20
        efficiency = min(100, (l_d / 15) * 100)
        
        # Check if wing can generate enough lift
        if max_lift < total_weight_n:
            efficiency = efficiency * 0.5
        
        return efficiency


def optimize_for_mission(mission_type='cargo', aircraft_mass=5000):
    """
    Find optimal aspect ratio for different mission types
    
    Args:
        mission_type: 'cargo', 'fighter', 'glider', 'regional'
        aircraft_mass: Empty aircraft mass in kg
    
    Returns:
        optimal_wing: Wing object with optimal aspect ratio
        metrics: Dictionary of performance metrics
    """
    
    mission_params = {
        'cargo': {
            'cruise_velocity': 80,  # m/s (slower, heavy payload)
            'payload': 5000,
            'description': 'Heavy payload, fuel efficiency priority'
        },
        'fighter': {
            'cruise_velocity': 200,  # m/s (very fast)
            'payload': 2000,
            'description': 'Speed and maneuverability priority'
        },
        'glider': {
            'cruise_velocity': 50,  # m/s (very slow)
            'payload': 200,
            'description': 'Maximum lift-to-drag ratio for soaring'
        },
        'regional': {
            'cruise_velocity': 120,  # m/s (moderate speed)
            'payload': 2500,
            'description': 'Balance speed and efficiency'
        }
    }
    
    if mission_type not in mission_params:
        raise ValueError(f"Unknown mission type: {mission_type}")
    
    params = mission_params[mission_type]
    
    # Objective function: minimize negative efficiency (to maximize)
    def objective(aspect_ratio):
        if aspect_ratio < 1 or aspect_ratio > 20:
            return 1000  # Penalty for unrealistic values
        
        # Create a wing with this aspect ratio
        # For simplicity, keep wing area constant, vary span/chord
        constant_area = 50  # m²
        chord = np.sqrt(constant_area / aspect_ratio)
        span = aspect_ratio * chord
        
        wing = Wing(span, chord, aircraft_mass)
        score = wing.cruise_efficiency_score(params['cruise_velocity'], params['payload'])
        
        return -score  # Negative because we're minimizing
    
    # Find optimal aspect ratio
    result = minimize_scalar(objective, bounds=(2, 15), method='bounded')
    optimal_ar = result.x
    
    # Create optimal wing
    constant_area = 50
    optimal_chord = np.sqrt(constant_area / optimal_ar)
    optimal_span = optimal_ar * optimal_chord
    optimal_wing = Wing(optimal_span, optimal_chord, aircraft_mass)
    
    metrics = {
        'mission': mission_type,
        'optimal_aspect_ratio': optimal_ar,
        'cruise_velocity_ms': params['cruise_velocity'],
        'fuel_efficiency_ld': optimal_wing.fuel_efficiency(params['cruise_velocity'], params['payload']),
        'efficiency_score': optimal_wing.cruise_efficiency_score(params['cruise_velocity'], params['payload']),
        'description': params['description']
    }
    
    return optimal_wing, metrics


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("WING ASPECT RATIO OPTIMIZATION")
    print("=" * 60)
    
    # Create sample wings with different aspect ratios
    print("\n1. Comparing wings with different aspect ratios:\n")
    
    aspect_ratios = [4, 8, 12, 15]
    for ar in aspect_ratios:
        chord = np.sqrt(50 / ar)
        span = ar * chord
        wing = Wing(span, chord)
        efficiency = wing.cruise_efficiency_score(cruise_velocity_ms=100)
        print(f"  AR={ar:2d}: {wing} | Efficiency: {efficiency:.1f}/100")
    
    # Optimize for different missions
    print("\n2. Optimal aspect ratios for different missions:\n")
    
    for mission in ['glider', 'regional', 'cargo', 'fighter']:
        wing, metrics = optimize_for_mission(mission)
        print(f"  {mission.upper()}:")
        print(f"    Optimal AR: {metrics['optimal_aspect_ratio']:.2f}")
        print(f"    L/D Ratio: {metrics['fuel_efficiency_ld']:.2f}")
        print(f"    Efficiency Score: {metrics['efficiency_score']:.1f}/100")
        print()

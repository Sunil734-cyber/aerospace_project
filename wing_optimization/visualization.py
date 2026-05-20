"""
Wing Visualization and Analysis
Plots aerodynamic properties vs aspect ratio
"""

import numpy as np
import matplotlib.pyplot as plt
from wing_properties import Wing, optimize_for_mission


def plot_aspect_ratio_analysis():
    """
    Create comprehensive plots showing how aspect ratio affects performance
    """
    
    aspect_ratios = np.linspace(2, 18, 50)
    wing_area = 50  # m² (constant)
    
    # Calculate metrics for each aspect ratio
    fuel_efficiency_cargo = []
    fuel_efficiency_fighter = []
    fuel_efficiency_glider = []
    max_lift_100ms = []
    
    for ar in aspect_ratios:
        chord = np.sqrt(wing_area / ar)
        span = ar * chord
        wing = Wing(span, chord, mass_empty_kg=5000)
        
        # Cargo mission (80 m/s, 5000 kg payload)
        fuel_efficiency_cargo.append(wing.fuel_efficiency(80, 5000))
        
        # Fighter mission (200 m/s, low payload)
        fuel_efficiency_fighter.append(wing.fuel_efficiency(200, 1000))
        
        # Glider mission (50 m/s, light payload)
        fuel_efficiency_glider.append(wing.fuel_efficiency(50, 200))
        
        # Max lift at 100 m/s
        max_lift_100ms.append(wing.max_lift_capability(100))
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Aircraft Wing Aspect Ratio Optimization', fontsize=16, fontweight='bold')
    
    # Plot 1: Fuel Efficiency vs Aspect Ratio
    ax = axes[0, 0]
    ax.plot(aspect_ratios, fuel_efficiency_cargo, 'o-', label='Cargo (80 m/s)', linewidth=2)
    ax.plot(aspect_ratios, fuel_efficiency_fighter, 's-', label='Fighter (200 m/s)', linewidth=2)
    ax.plot(aspect_ratios, fuel_efficiency_glider, '^-', label='Glider (50 m/s)', linewidth=2)
    ax.set_xlabel('Aspect Ratio (Span/Chord)', fontweight='bold')
    ax.set_ylabel('Lift-to-Drag Ratio (L/D)', fontweight='bold')
    ax.set_title('Fuel Efficiency vs Aspect Ratio')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 25)
    
    # Plot 2: Efficiency Score Comparison
    ax = axes[0, 1]
    efficiency_scores_cargo = []
    efficiency_scores_fighter = []
    efficiency_scores_glider = []
    
    for ar in aspect_ratios:
        chord = np.sqrt(wing_area / ar)
        span = ar * chord
        wing = Wing(span, chord, mass_empty_kg=5000)
        efficiency_scores_cargo.append(wing.cruise_efficiency_score(80, 5000))
        efficiency_scores_fighter.append(wing.cruise_efficiency_score(200, 1000))
        efficiency_scores_glider.append(wing.cruise_efficiency_score(50, 200))
    
    ax.plot(aspect_ratios, efficiency_scores_cargo, 'o-', label='Cargo', linewidth=2)
    ax.plot(aspect_ratios, efficiency_scores_fighter, 's-', label='Fighter', linewidth=2)
    ax.plot(aspect_ratios, efficiency_scores_glider, '^-', label='Glider', linewidth=2)
    ax.set_xlabel('Aspect Ratio (Span/Chord)', fontweight='bold')
    ax.set_ylabel('Efficiency Score (0-100)', fontweight='bold')
    ax.set_title('Overall Efficiency Score vs Aspect Ratio')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Max Lift Capability
    ax = axes[1, 0]
    ax.plot(aspect_ratios, np.array(max_lift_100ms) / 1000, 'g-', linewidth=2.5)
    ax.axhline(y=49.05, color='r', linestyle='--', label='Empty Weight (5000 kg)', linewidth=2)
    ax.axhline(y=98.1, color='orange', linestyle='--', label='With 5000 kg Payload', linewidth=2)
    ax.set_xlabel('Aspect Ratio (Span/Chord)', fontweight='bold')
    ax.set_ylabel('Max Lift at 100 m/s (kN)', fontweight='bold')
    ax.set_title('Maximum Lift Capability')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Mission Comparison
    ax = axes[1, 1]
    missions = ['Glider', 'Regional', 'Cargo', 'Fighter']
    optimal_ars = []
    efficiency_scores = []
    
    for mission in ['glider', 'regional', 'cargo', 'fighter']:
        wing, metrics = optimize_for_mission(mission)
        optimal_ars.append(metrics['optimal_aspect_ratio'])
        efficiency_scores.append(metrics['efficiency_score'])
    
    colors = ['#ff7f0e', '#2ca02c', '#d62728', '#1f77b4']
    bars = ax.barh(missions, optimal_ars, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (bar, ar) in enumerate(zip(bars, optimal_ars)):
        ax.text(ar + 0.2, bar.get_y() + bar.get_height()/2, 
                f'{ar:.2f}', va='center', fontweight='bold')
    
    ax.set_xlabel('Optimal Aspect Ratio', fontweight='bold')
    ax.set_title('Optimal Aspect Ratios by Mission Type')
    ax.set_xlim(0, 16)
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('wing_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: wing_analysis.png")
    plt.show()


def print_optimization_summary():
    """
    Print detailed optimization results for all mission types
    """
    print("\n" + "=" * 80)
    print("WING ASPECT RATIO OPTIMIZATION RESULTS")
    print("=" * 80)
    
    missions = [
        ('glider', 'Sailplane - maximize gliding efficiency'),
        ('regional', 'Regional airliner - balance efficiency and speed'),
        ('cargo', 'Cargo transport - heavy payload, long range'),
        ('fighter', 'Fighter jet - speed and maneuverability'),
    ]
    
    results = []
    
    for mission_key, description in missions:
        wing, metrics = optimize_for_mission(mission_key)
        results.append((mission_key.upper(), description, metrics, wing))
        
        print(f"\n{mission_key.upper()}")
        print(f"Description: {description}")
        print(f"  • Optimal Aspect Ratio: {metrics['optimal_aspect_ratio']:.2f}")
        print(f"  • Wing Dimensions: Span={wing.span:.2f}m, Chord={wing.chord:.2f}m")
        print(f"  • Cruise Velocity: {metrics['cruise_velocity_ms']} m/s")
        print(f"  • Lift-to-Drag Ratio (L/D): {metrics['fuel_efficiency_ld']:.2f}")
        print(f"  • Efficiency Score: {metrics['efficiency_score']:.1f}/100")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHTS:")
    print("=" * 80)
    print("""
1. GLIDERS: Need HIGHEST aspect ratio (12-15) for maximum fuel efficiency
   → Long, narrow wings = minimal drag, maximum L/D ratio
   
2. REGIONAL AIRCRAFT: Moderate aspect ratio (8-10)
   → Balance speed and efficiency for commercial viability
   
3. CARGO PLANES: Also need high aspect ratio (10-12)
   → Heavy payloads need generous lift, long wings provide this efficiently
   
4. FIGHTERS: Lowest aspect ratio (4-6)
   → Short, stubby wings for maneuverability and speed (less drag at high speeds)
   → Can't maintain level flight as efficiently, but combat performance matters more

WHY THIS HAPPENS:
  • High aspect ratio = less induced drag = better L/D = better fuel efficiency
  • BUT: High aspect ratio = heavier wing structure, slower response
  • Low aspect ratio = more drag = worse fuel efficiency BUT more agile, handles
    high speeds better (parasitic drag dominates at high speed)
""")


if __name__ == "__main__":
    plot_aspect_ratio_analysis()
    print_optimization_summary()

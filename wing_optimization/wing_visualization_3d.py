"""
3D Wing Visualization Module
Generates interactive 3D rendered wings with multiple viewing angles
Uses Plotly for Streamlit compatibility
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Wing3DVisualizer:
    """Generate 3D visualizations of aircraft wings"""
    
    def __init__(self, span, chord, aspect_ratio, wing_area):
        """
        Initialize visualizer with wing parameters
        
        Args:
            span: Wing span in meters
            chord: Average chord in meters
            aspect_ratio: Aspect ratio (span/chord)
            wing_area: Total wing area in m²
        """
        self.span = span
        self.chord = chord
        self.aspect_ratio = aspect_ratio
        self.wing_area = wing_area
    
    def generate_wing_surface(self):
        """Generate 3D surface mesh for the wing"""
        
        # Wing coordinates
        half_span = self.span / 2
        
        # Create mesh grid along span and chord
        y = np.linspace(-half_span, half_span, 20)  # span-wise
        x = np.linspace(0, self.chord, 30)          # chord-wise
        
        X, Y = np.meshgrid(x, y)
        
        # Elliptical wing cross-section (more realistic than rectangular)
        taper_ratio = 0.6  # Wing tapers toward tip
        
        chord_distribution = self.chord * (1 - (1 - taper_ratio) * np.abs(Y) / half_span)
        
        # Create upper and lower surfaces with slight thickness
        thickness = 0.02 * self.chord
        
        # Upper surface (cambered airfoil shape)
        Z_upper = thickness * (1 - (X / self.chord) ** 2) * (1 - np.abs(Y) / half_span)
        
        # Lower surface (must be array, not scalar!)
        Z_lower = np.ones_like(Z_upper) * (-thickness * 0.3)
        
        return X, Y, Z_upper, Z_lower, chord_distribution
    
    def create_3d_visualization(self):
        """Create interactive 3D wing visualization"""
        
        X, Y, Z_upper, Z_lower, _ = self.generate_wing_surface()
        
        # Convert numpy arrays to native Python lists for Plotly
        X_list = [[float(x) for x in row] for row in X]
        Y_list = [[float(y) for y in row] for row in Y]
        Z_upper_list = [[float(z) for z in row] for row in Z_upper]
        Z_lower_list = [[float(z) for z in row] for row in Z_lower]
        
        fig = go.Figure()
        
        # Upper surface
        fig.add_trace(go.Surface(
            x=X_list, y=Y_list, z=Z_upper_list,
            colorscale='Blues',
            showscale=False,
            name='Upper Surface',
            opacity=0.9,
            hovertemplate='<b>Upper Surface</b><br>X: %{x:.2f}m<br>Y: %{y:.2f}m<br>Z: %{z:.3f}m<extra></extra>'
        ))
        
        # Lower surface
        fig.add_trace(go.Surface(
            x=X_list, y=Y_list, z=Z_lower_list,
            colorscale='Reds',
            showscale=False,
            name='Lower Surface',
            opacity=0.85,
            hovertemplate='<b>Lower Surface</b><br>X: %{x:.2f}m<br>Y: %{y:.2f}m<br>Z: %{z:.3f}m<extra></extra>'
        ))
        
        # Add wing outline
        outline_y = np.array([-self.span/2, self.span/2])
        outline_x = np.array([0, self.chord])
        
        for y_val in outline_y:
            fig.add_trace(go.Scatter3d(
                x=outline_x,
                y=[y_val, y_val],
                z=[0, 0],
                mode='lines',
                line=dict(color='black', width=3),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add wing tips (vertical lines)
        fig.add_trace(go.Scatter3d(
            x=[0, self.chord],
            y=[-self.span/2, -self.span/2],
            z=[0, 0],
            mode='lines',
            line=dict(color='black', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter3d(
            x=[0, self.chord],
            y=[self.span/2, self.span/2],
            z=[0, 0],
            mode='lines',
            line=dict(color='black', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'<b>3D Wing Visualization</b><br><sub>Span: {self.span:.2f}m | Chord: {self.chord:.2f}m | AR: {self.aspect_ratio:.2f}</sub>',
            scene=dict(
                xaxis=dict(title='Chord (m)', backgroundcolor='rgb(230,230,230)'),
                yaxis=dict(title='Span (m)', backgroundcolor='rgb(230,230,230)'),
                zaxis=dict(title='Height (m)', backgroundcolor='rgb(230,230,230)'),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            height=700,
            showlegend=True,
            hovermode='closest'
        )
        
        return fig
    
    def create_multiview_comparison(self):
        """Create isometric, top, and side views"""
        
        X, Y, Z_upper, Z_lower, _ = self.generate_wing_surface()
        
        # Convert to native Python lists
        X_list = [[float(x) for x in row] for row in X]
        Y_list = [[float(y) for y in row] for row in Y]
        Z_upper_list = [[float(z) for z in row] for row in Z_upper]
        Z_lower_list = [[float(z) for z in row] for row in Z_lower]
        Z_zeros = [[0.0 for _ in row] for row in X]
        
        fig = make_subplots(
            rows=1, cols=3,
            specs=[[{'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}]],
            subplot_titles=('Isometric View', 'Top View', 'Side View')
        )
        
        # Isometric view
        fig.add_trace(
            go.Surface(x=X_list, y=Y_list, z=Z_upper_list, colorscale='Blues', showscale=False, name='Upper'),
            row=1, col=1
        )
        fig.add_trace(
            go.Surface(x=X_list, y=Y_list, z=Z_lower_list, colorscale='Reds', showscale=False, name='Lower'),
            row=1, col=1
        )
        
        # Top view (looking down)
        fig.add_trace(
            go.Surface(x=X_list, y=Y_list, z=Z_zeros, colorscale='Greys', showscale=False, opacity=0.3),
            row=1, col=2
        )
        fig.add_trace(
            go.Surface(x=X_list, y=Y_list, z=Z_upper_list, colorscale='Blues', showscale=False),
            row=1, col=2
        )
        
        # Side view (looking from the side)
        X_side = np.linspace(0, self.chord, 30)
        Z_side = np.linspace(-0.1, 0.1, 20)
        X_side_mesh, Z_side_mesh = np.meshgrid(X_side, Z_side)
        Y_side_mesh = np.zeros_like(X_side_mesh)
        
        X_side_list = [[float(x) for x in row] for row in X_side_mesh]
        Y_side_list = [[float(y) for y in row] for row in Y_side_mesh]
        Z_side_list = [[float(z) for z in row] for row in Z_side_mesh]
        
        fig.add_trace(
            go.Surface(x=X_side_list, y=Y_side_list, z=Z_side_list, colorscale='Greens', showscale=False),
            row=1, col=3
        )
        
        # Update all subplots
        fig.update_scenes(
            xaxis=dict(title='Chord (m)'),
            yaxis=dict(title='Span (m)'),
            zaxis=dict(title='Height (m)')
        )
        
        fig.update_layout(
            title_text=f'<b>Multi-View Wing Analysis</b><br><sub>Span: {self.span:.2f}m | Chord: {self.chord:.2f}m | AR: {self.aspect_ratio:.2f}</sub>',
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_annotated_view(self, l_d_ratio, wing_loading, oswald_efficiency):
        """Create wing view with aerodynamic annotations"""
        
        X, Y, Z_upper, Z_lower, chord_dist = self.generate_wing_surface()
        
        # Convert to native Python lists
        X_list = [[float(x) for x in row] for row in X]
        Y_list = [[float(y) for y in row] for row in Y]
        Z_upper_list = [[float(z) for z in row] for row in Z_upper]
        
        fig = go.Figure()
        
        # Wing surface with color gradient based on lift distribution
        # Higher lift near root, lower near tip
        lift_distribution = 1 - np.abs(Y) / (self.span / 2)
        lift_list = [[float(l) for l in row] for row in lift_distribution]
        
        fig.add_trace(go.Surface(
            x=X_list, y=Y_list, z=Z_upper_list,
            surfacecolor=lift_list,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Lift<br>Distribution'),
            name='Lift Distribution'
        ))
        
        # Add annotations on the wing
        fig.add_annotation(
            x=0.5, y=0.5, 
            text=f'<b>AERODYNAMIC PROPERTIES</b><br>' +
                 f'L/D Ratio: {l_d_ratio:.2f}<br>' +
                 f'Wing Loading: {wing_loading:.2f} kg/m²<br>' +
                 f'Oswald Efficiency: {oswald_efficiency:.3f}',
            xref='paper', yref='paper',
            showarrow=False,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='black',
            borderwidth=2,
            font=dict(size=11),
            xanchor='center'
        )
        
        fig.update_layout(
            title=f'<b>Wing with Aerodynamic Annotations</b><br><sub>Span: {self.span:.2f}m | Chord: {self.chord:.2f}m | AR: {self.aspect_ratio:.2f}</sub>',
            scene=dict(
                xaxis=dict(title='Chord (m)'),
                yaxis=dict(title='Span (m)'),
                zaxis=dict(title='Height (m)'),
                camera=dict(eye=dict(x=1.2, y=1.5, z=1.3))
            ),
            height=700,
            showlegend=True
        )
        
        return fig


class AircraftComparison:
    """Real aircraft database and comparison"""
    
    REAL_AIRCRAFT = {
        'Boeing 747': {
            'span': 68.4,
            'chord': 10.7,
            'aspect_ratio': 6.5,
            'wing_area': 511,
            'cruise_speed': 121,
            'mission': 'Long-range airliner'
        },
        'F-16 Fighter': {
            'span': 9.45,
            'chord': 5.8,
            'aspect_ratio': 3.2,
            'wing_area': 27.9,
            'cruise_speed': 215,
            'mission': 'High-speed fighter'
        },
        'Cessna 172': {
            'span': 11.0,
            'chord': 1.7,
            'aspect_ratio': 7.3,
            'wing_area': 16.2,
            'cruise_speed': 50,
            'mission': 'General aviation'
        },
        'Albatross': {
            'span': 3.5,
            'chord': 0.25,
            'aspect_ratio': 14.0,
            'wing_area': 0.88,
            'cruise_speed': 12,
            'mission': 'Long-range glider/soaring'
        },
        'Airbus A380': {
            'span': 79.8,
            'chord': 12.5,
            'aspect_ratio': 7.5,
            'wing_area': 845,
            'cruise_speed': 113,
            'mission': 'Extra-large airliner'
        }
    }
    
    @classmethod
    def find_similar_aircraft(cls, aspect_ratio, wing_area):
        """Find most similar existing aircraft"""
        
        min_diff = float('inf')
        similar = None
        
        for name, specs in cls.REAL_AIRCRAFT.items():
            # Calculate similarity using AR and wing area
            ar_diff = abs(specs['aspect_ratio'] - aspect_ratio)
            area_diff = abs(specs['wing_area'] - wing_area) / specs['wing_area']
            
            diff = ar_diff + area_diff
            
            if diff < min_diff:
                min_diff = diff
                similar = (name, specs)
        
        return similar
    
    @classmethod
    def create_comparison_table(cls, user_span, user_chord, user_ar, user_area):
        """Create detailed comparison table with real aircraft"""
        
        similar_name, similar_specs = cls.find_similar_aircraft(user_ar, user_area)
        
        comparison_data = {
            'Parameter': ['Span (m)', 'Chord (m)', 'Aspect Ratio', 'Wing Area (m²)', 'Cruise Speed (m/s)', 'Mission Type'],
            'Your Design': [
                f'{user_span:.2f}',
                f'{user_chord:.2f}',
                f'{user_ar:.2f}',
                f'{user_area:.2f}',
                'TBD',
                'Custom'
            ],
            similar_name: [
                f'{similar_specs["span"]:.2f}',
                f'{similar_specs["chord"]:.2f}',
                f'{similar_specs["aspect_ratio"]:.2f}',
                f'{similar_specs["wing_area"]:.2f}',
                f'{similar_specs["cruise_speed"]:.2f}',
                similar_specs['mission']
            ]
        }
        
        return comparison_data, similar_name
    
    @classmethod
    def create_benchmarking_chart(cls, user_ar, user_area):
        """Create scatter plot comparing design to real aircraft"""
        
        fig = go.Figure()
        
        # Plot all real aircraft
        for name, specs in cls.REAL_AIRCRAFT.items():
            fig.add_trace(go.Scatter(
                x=[specs['aspect_ratio']],
                y=[specs['wing_area']],
                mode='markers+text',
                name=name,
                marker=dict(size=12, line=dict(color='black', width=1.5)),
                text=name,
                textposition='top center',
                hovertemplate='<b>%{text}</b><br>AR: %{x:.2f}<br>Area: %{y:.1f} m²<extra></extra>'
            ))
        
        # Plot user design
        fig.add_trace(go.Scatter(
            x=[user_ar],
            y=[user_area],
            mode='markers+text',
            name='Your Design',
            marker=dict(size=15, color='red', symbol='star', line=dict(color='darkred', width=2)),
            text='YOUR DESIGN',
            textposition='top center',
            hovertemplate='<b>Your Design</b><br>AR: %{x:.2f}<br>Area: %{y:.1f} m²<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Design Benchmarking</b><br><sub>Your Design vs Real Aircraft</sub>',
            xaxis_title='Aspect Ratio',
            yaxis_title='Wing Area (m²)',
            hovermode='closest',
            width=900,
            height=600,
            plot_bgcolor='rgba(240,240,240,0.5)',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray'),
            font=dict(size=11)
        )
        
        return fig

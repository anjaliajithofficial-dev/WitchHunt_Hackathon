# demo/prosthetic_simulator.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import torch

class ProstheticHandSimulator:
    """
    Interactive simulator demonstrating AxonNova controlling a prosthetic hand.
    """
    def __init__(self, model):
        self.model = model
        self.hand_positions = {
            'thumb': 0.0, 'index': 0.0, 'middle': 0.0,
            'ring': 0.0, 'pinky': 0.0
        }
        
        # Movement to finger mapping
        self.movement_mapping = {
            'rest': {'thumb': 0, 'index': 0, 'middle': 0, 'ring': 0, 'pinky': 0},
            'grasp': {'thumb': 0.8, 'index': 0.7, 'middle': 0.7, 'ring': 0.6, 'pinky': 0.5},
            'fist': {'thumb': 0.9, 'index': 0.9, 'middle': 0.9, 'ring': 0.9, 'pinky': 0.9},
            'point': {'thumb': 0.2, 'index': 0.9, 'middle': 0.1, 'ring': 0.1, 'pinky': 0.1},
            'peace': {'thumb': 0.3, 'index': 0.9, 'middle': 0.9, 'ring': 0.1, 'pinky': 0.1}
        }
        
    def visualize(self, neural_signal, prediction):
        """Create real-time visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Neural signal
        axes[0, 0].plot(neural_signal.numpy())
        axes[0, 0].set_title('Neural Signal Input')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Amplitude')
        
        # Prediction probabilities
        movement_names = ['rest', 'grasp', 'release', 'flex', 'extend', 
                         'thumb', 'point', 'peace', 'fist']
        axes[0, 1].barh(movement_names, prediction)
        axes[0, 1].set_title('Movement Prediction Probabilities')
        
        # Hand visualization
        axes[1, 0].axis('off')
        axes[1, 0].set_title('Prosthetic Hand State')
        
        # Finger position bars
        fingers = list(self.hand_positions.keys())
        positions = list(self.hand_positions.values())
        axes[1, 1].bar(fingers, positions, color='skyblue')
        axes[1, 1].set_title('Finger Positions')
        axes[1, 1].set_ylim(0, 1)
        
        plt.tight_layout()
        plt.show()
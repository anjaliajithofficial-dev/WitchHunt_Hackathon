# utils/explainability.py
import torch
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict

class ExplainabilityModule:
    """
    Provides explanations for why a neural pathway was triggered.
    """
    def __init__(self, model, feature_names: List[str] = None):
        self.model = model
        self.feature_names = feature_names or [f"channel_{i}" for i in range(128)]
        self.explanation_history = []
        
    def feature_importance(self, input_tensor: torch.Tensor, target_neuron: int = None) -> np.ndarray:
        """
        Compute feature importance using gradient-based attribution.
        Simplified SHAP-like approach.
        """
        input_tensor.requires_grad_(True)
        
        # Forward pass
        output, complexity, active = self.model(input_tensor.unsqueeze(0))
        
        # Backward pass for gradients
        if target_neuron is not None:
            output[0, target_neuron].backward()
        else:
            output.sum().backward()
            
        # Importance = |gradients| * input
        gradients = input_tensor.grad
        importance = (gradients * input_tensor).abs().detach().numpy()
        
        return importance.flatten()
    
    def pathway_explanation(self, input_tensor: torch.Tensor) -> Dict:
        """Explain which neural pathways were activated"""
        with torch.no_grad():
            # Get model's dynamic layer activations
            if hasattr(self.model, 'dynamic_synapse'):
                _, complexity, active_neurons = self.model.dynamic_synapse(input_tensor.unsqueeze(0), training=False)
                
                explanation = {
                    'input_complexity': complexity,
                    'active_layers': len(active_neurons),
                    'synaptic_activity': active_neurons,
                    'reasoning': self._generate_reasoning(complexity, active_neurons)
                }
                self.explanation_history.append(explanation)
                return explanation
        
        return {'error': 'Model does not support pathway explanation'}
    
    def _generate_reasoning(self, complexity: float, activity: List[float]) -> str:
        """Generate human-readable explanation"""
        if complexity < 0.3:
            return "Low input complexity detected - minimal synaptic pathway activated for efficiency."
        elif complexity < 0.7:
            return f"Moderate complexity (score: {complexity:.2f}) - {len(activity)} synaptic layers engaged for balanced processing."
        else:
            return f"High complexity input (score: {complexity:.2f}) - Full synaptic network deployed for detailed analysis."
    
    def visualize_decision_path(self, input_tensor: torch.Tensor):
        """Visualize which features triggered the decision"""
        importances = self.feature_importance(input_tensor)
        top_features = np.argsort(importances)[-10:]
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Feature importance plot
        axes[0].barh(range(len(importances[:50])), importances[:50])
        axes[0].set_title('Top 50 Feature Importances')
        axes[0].set_xlabel('Importance Score')
        axes[0].set_ylabel('Feature Index')
        
        # Input signal visualization
        axes[1].plot(input_tensor.numpy())
        axes[1].set_title('Input Neural Signal')
        axes[1].set_xlabel('Time (samples)')
        axes[1].set_ylabel('Amplitude (µV)')
        
        plt.tight_layout()
        plt.show()
        
        return top_features
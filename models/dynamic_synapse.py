# models/dynamic_synapse.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class DynamicSynapticLayer(nn.Module):
    """
    Implements dynamic synaptic scaling - automatically adjusts 
    network depth based on input complexity.
    """
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, complexity_threshold: float = 0.6):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.complexity_threshold = complexity_threshold
        
        # Base layers (always active)
        self.input_layer = nn.Linear(input_dim, hidden_dim)
        self.batch_norm = nn.BatchNorm1d(hidden_dim)
        
        # Dynamically activated layers (synaptic scaling)
        self.dynamic_layers = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Linear(hidden_dim, hidden_dim)
        ])
        
        self.output_layer = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(0.2)
        
        # Track activation states for explainability
        self.active_neurons = []
        
    def compute_input_complexity(self, x: torch.Tensor) -> float:
        """Estimates input complexity to determine how many layers to activate"""
        # Using entropy and variance as complexity metrics
        variance = torch.var(x).item()
        entropy = -torch.sum(F.softmax(x, dim=1) * F.log_softmax(x, dim=1), dim=1).mean().item()
        complexity = (variance + entropy) / 2
        return min(1.0, complexity / self.complexity_threshold)
    
    def forward(self, x: torch.Tensor, training: bool = True):
        complexity_score = self.compute_input_complexity(x)
        
        # Determine how many dynamic layers to activate
        num_active_layers = min(int(np.ceil(complexity_score * len(self.dynamic_layers))), len(self.dynamic_layers))
        
        # Forward pass through base layers
        x = F.relu(self.input_layer(x))
        x = self.batch_norm(x)
        x = self.dropout(x)
        
        # Record active neurons for explainability
        self.active_neurons = []
        
        # Dynamic layers activation (synaptic scaling)
        for i, layer in enumerate(self.dynamic_layers[:num_active_layers]):
            x = F.relu(layer(x))
            self.active_neurons.append(x.detach().mean().item())
            if training:
                x = self.dropout(x)
        
        # Output
        output = self.output_layer(x)
        return output, complexity_score, self.active_neurons


class SynapticPruningModule(nn.Module):
    """
    Mimics biological synaptic pruning - deactivates unnecessary neurons during inference.
    """
    def __init__(self, network: nn.Module, pruning_threshold: float = 0.15):
        super().__init__()
        self.network = network
        self.pruning_threshold = pruning_threshold
        self.neuron_importance = {}
        self.pruned_neurons = set()
        
    def compute_neuron_importance(self, activation_history):
        """Track which neurons are frequently activated"""
        for name, activations in activation_history.items():
            avg_activation = np.mean(activations)
            if avg_activation < self.pruning_threshold:
                self.pruned_neurons.add(name)
                
    def forward(self, x, record_activations=True):
        activations = {}
        
        # Custom forward pass with pruning
        x = self.network.input_layer(x)
        activations['input_layer'] = x.detach().numpy().flatten()
        
        x = F.relu(x)
        x = self.network.batch_norm(x)
        
        return x, activations
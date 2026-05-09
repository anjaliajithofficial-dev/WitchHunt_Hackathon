# inference/guardrail_layer.py
import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Optional

class GuardrailLayer:
    """
    Ethics-by-design guardrails that filter outputs against
    safety and bias benchmarks in real-time.
    """
    def __init__(self, bias_threshold: float = 0.05, safety_threshold: float = 0.1):
        self.bias_threshold = bias_threshold
        self.safety_threshold = safety_threshold
        self.bias_metrics = []
        
        # Define safe ranges for prosthetic control signals
        self.safe_ranges = {
            'force': (0.0, 10.0),      # Newtons
            'velocity': (0.0, 2.0),     # m/s
            'angle': (-30.0, 120.0),    # degrees
            'frequency': (0.0, 100.0)   # Hz
        }
        
    def detect_bias(self, predictions: np.ndarray, sensitive_attributes: Optional[dict] = None) -> Tuple[bool, float]:
        """Detect potential bias in predictions"""
        # Calculate demographic parity
        if sensitive_attributes:
            # Simplified bias detection
            mean_pred = np.mean(predictions)
            group_means = []
            for group, indices in sensitive_attributes.items():
                if len(indices) > 0:
                    group_means.append(np.mean(predictions[indices]))
            
            if len(group_means) > 1:
                max_bias = max(group_means) - min(group_means)
                is_biased = max_bias > self.bias_threshold
                return is_biased, max_bias
                
        return False, 0.0
    
    def safety_check(self, output_signals: dict) -> Tuple[bool, list]:
        """Verify outputs are within safe operating ranges"""
        violations = []
        
        for signal_name, value in output_signals.items():
            if signal_name in self.safe_ranges:
                min_val, max_val = self.safe_ranges[signal_name]
                if value < min_val or value > max_val:
                    violations.append({
                        'signal': signal_name,
                        'value': value,
                        'allowed_range': (min_val, max_val)
                    })
                    
        is_safe = len(violations) == 0
        return is_safe, violations
    
    def filter_output(self, raw_output: dict) -> dict:
        """Apply both bias and safety filters"""
        # Safety first - critical for prosthetics
        is_safe, violations = self.safety_check(raw_output)
        
        if not is_safe:
            # Clamp to safe values
            filtered = raw_output.copy()
            for violation in violations:
                signal = violation['signal']
                min_val, max_val = violation['allowed_range']
                filtered[signal] = np.clip(raw_output[signal], min_val, max_val)
            return filtered, {'was_filtered': True, 'violations': violations}
        
        return raw_output, {'was_filtered': False, 'violations': []}
    
    def log_ethics_metrics(self, predictions: np.ndarray):
        """Maintain metrics for ethics auditing"""
        self.bias_metrics.append({
            'timestamp': len(self.bias_metrics),
            'mean_prediction': np.mean(predictions),
            'std_prediction': np.std(predictions)
        })
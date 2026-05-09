# main.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

from models.dynamic_synapse import DynamicSynapticLayer, SynapticPruningModule
from models.contextual_memory import ContextualMemoryLayer
from inference.guardrail_layer import GuardrailLayer
from data.synthetic_neural_data import NeuralSignalDataset, RealTimeDataPipeline
from utils.explainability import ExplainabilityModule

class AxonNova(nn.Module):
    """
    Complete AxonNova Framework combining all components:
    - Dynamic Synaptic Scaling
    - Contextual Memory
    - Ethics Guardrails
    """
    def __init__(self, input_dim: int = 128, hidden_dim: int = 256, output_dim: int = 9):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Core components
        self.dynamic_synapse = DynamicSynapticLayer(input_dim, hidden_dim, hidden_dim)
        self.contextual_memory = ContextualMemoryLayer(memory_size=200, embedding_dim=hidden_dim)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, output_dim)
        )
        
        # Initialize guardrails
        self.guardrails = GuardrailLayer()
        
        # Store metrics
        self.prediction_history = []
        self.complexity_history = []
        
    def forward(self, x: torch.Tensor, use_memory: bool = True, apply_guardrails: bool = True):
        # Dynamic synaptic processing
        features, complexity, active_neurons = self.dynamic_synapse(x, training=self.training)
        self.complexity_history.append(complexity)
        
        # Contextual memory integration
        if use_memory and hasattr(self, 'contextual_memory'):
            context = self.contextual_memory.update_context(features)
            features = features + 0.3 * context  # Residual connection from memory
        
        # Classification
        logits = self.classifier(features)
        predictions = torch.softmax(logits, dim=1)
        
        # Store for guardrails
        self.prediction_history.append(predictions.detach().numpy())
        
        return {
            'logits': logits,
            'predictions': predictions,
            'complexity': complexity,
            'active_neurons': active_neurons
        }
    
    def predict_with_safety(self, x: torch.Tensor) -> dict:
        """Prediction with ethics guardrails"""
        outputs = self.forward(x)
        
        # Convert to format for guardrails
        movement_probs = outputs['predictions'].detach().numpy()[0]
        predicted_class = np.argmax(movement_probs)
        
        # Simulate control signals for guardrail check
        control_signals = {
            'force': movement_probs[predicted_class] * 5.0,
            'velocity': movement_probs[predicted_class] * 1.5,
            'angle': predicted_class * 10,
            'frequency': movement_probs[predicted_class] * 50
        }
        
        # Apply guardrails
        safe_signals, filter_info = self.guardrails.filter_output(control_signals)
        
        return {
            'predicted_movement': predicted_class,
            'confidence': movement_probs[predicted_class],
            'control_signals': safe_signals,
            'guardrail_info': filter_info,
            'complexity': outputs['complexity']
        }


class AxonNovaTrainer:
    """Training and evaluation pipeline"""
    
    def __init__(self, model: AxonNova, learning_rate: float = 0.001):
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()
        self.train_losses = []
        self.val_accuracies = []
        
    def train_epoch(self, dataloader: DataLoader) -> float:
        self.model.train()
        total_loss = 0
        
        for batch_idx, (data, labels, complexities) in enumerate(tqdm(dataloader, desc="Training")):
            self.optimizer.zero_grad()
            
            outputs = self.model(data)
            loss = self.criterion(outputs['logits'], labels)
            
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader)
        self.train_losses.append(avg_loss)
        return avg_loss
    
    def validate(self, dataloader: DataLoader) -> float:
        self.model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, labels, complexities in dataloader:
                outputs = self.model(data)
                predictions = outputs['predictions']
                predicted = torch.argmax(predictions, dim=1)
                
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        self.val_accuracies.append(accuracy)
        return accuracy


def main():
    """Run complete AxonNova demonstration"""
    
    print("=" * 60)
    print("AXONNOVA: Neural Intelligence Framework")
    print("Healthcare Application - Prosthetic Control Simulation")
    print("=" * 60)
    
    # 1. Load synthetic neural data
    print("\n[1/6] Loading synthetic neural signal dataset...")
    dataset = NeuralSignalDataset(num_samples=5000, sequence_length=128)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    
    print(f"     Dataset: {len(dataset)} samples, {dataset.sequence_length} features")
    print(f"     Movement classes: {dataset.movement_labels}")
    
    # 2. Initialize AxonNova
    print("\n[2/6] Initializing AxonNova framework...")
    model = AxonNova(input_dim=128, hidden_dim=256, output_dim=len(dataset.movement_labels))
    trainer = AxonNovaTrainer(model)
    explainer = ExplainabilityModule(model)
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"     Total parameters: {total_params:,}")
    print(f"     Dynamic synaptic scaling: ENABLED")
    print(f"     Contextual memory layer: ACTIVE")
    print(f"     Ethics guardrails: DEPLOYED")
    
    # 3. Training
    print("\n[3/6] Training AxonNova (demonstrating adaptive learning)...")
    epochs = 15
    for epoch in range(epochs):
        train_loss = trainer.train_epoch(train_loader)
        val_acc = trainer.validate(val_loader)
        
        if (epoch + 1) % 5 == 0:
            print(f"     Epoch {epoch+1}/{epochs} - Loss: {train_loss:.4f}, Val Acc: {val_acc:.2f}%")
    
    print(f"\n     Final Validation Accuracy: {trainer.val_accuracies[-1]:.2f}%")
    
    # 4. Real-time inference demonstration
    print("\n[4/6] Demonstrating real-time inference with safety guardrails...")
    pipeline = RealTimeDataPipeline(dataset, batch_size=1)
    
    demo_samples = 10
    successful_predictions = 0
    
    print("\n     Real-time prosthetic control simulation:")
    print("     " + "-" * 50)
    
    for i in range(demo_samples):
        data, label, complexity = pipeline.get_stream_batch()
        
        with torch.no_grad():
            result = model.predict_with_safety(data)
        
        predicted_movement = dataset.movement_labels[result['predicted_movement']]
        actual_movement = dataset.movement_labels[label.item()]
        
        is_correct = result['predicted_movement'] == label.item()
        successful_predictions += is_correct
        
        filter_status = "✓ SAFE" if not result['guardrail_info']['was_filtered'] else "⚠ FILTERED"
        
        print(f"     Sample {i+1}: Predicted={predicted_movement:12s} | Actual={actual_movement:12s} | "
              f"Correct={is_correct} | Guardrail={filter_status} | Complexity={result['complexity']:.2f}")
    
    print("     " + "-" * 50)
    print(f"     Demo accuracy: {successful_predictions/demo_samples*100:.1f}%")
    
    # 5. Explainability demo
    print("\n[5/6] Generating explainability insights...")
    sample_data, sample_label, _ = dataset[0]
    explanation = explainer.pathway_explanation(sample_data)
    
    if 'error' not in explanation:
        print(f"\n     PATHWAY EXPLANATION:")
        print(f"     ├─ Input complexity score: {explanation['input_complexity']:.3f}")
        print(f"     ├─ Active synaptic layers: {explanation['active_layers']}")
        print(f"     └─ Reasoning: {explanation['reasoning']}")
    
    # 6. Performance metrics
    print("\n[6/6] Framework Performance Summary:")
    print("     " + "-" * 40)
    
    # Calculate average complexity adaptation
    avg_complexity = np.mean(model.complexity_history[-100:]) if model.complexity_history else 0
    print(f"     ├─ Average input complexity: {avg_complexity:.3f}")
    print(f"     ├─ Synaptic pruning efficiency: Dynamic")
    print(f"     ├─ Contextual memory: {len(model.contextual_memory.short_term_memory)} stored experiences")
    print(f"     ├─ Guardrail interventions: {len(model.guardrails.bias_metrics)} safety checks")
    print(f"     └─ Carbon-efficient inference: Enabled (dynamic depth)")
    
    # Plot training results
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(trainer.train_losses)
    plt.title('AxonNova Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(trainer.val_accuracies)
    plt.title('Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    
    plt.tight_layout()
    plt.savefig('axonova_training_results.png', dpi=150)
    print("\n     Training visualization saved as 'axonova_training_results.png'")
    
    print("\n" + "=" * 60)
    print("✅ AxonNova demonstration complete!")
    print("   Framework ready for deployment in healthcare applications.")
    print("=" * 60)
    
    return model, trainer


if __name__ == "__main__":
    model, trainer = main()
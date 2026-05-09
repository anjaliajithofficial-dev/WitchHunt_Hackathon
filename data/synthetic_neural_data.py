# data/synthetic_neural_data.py
import numpy as np
from scipy import signal
import torch
from torch.utils.data import Dataset, DataLoader

class NeuralSignalDataset(Dataset):
    """
    Generates synthetic EEG/EMG-like signals for prosthetic control simulation.
    These mimic real neural signals for hand/wrist movements.
    """
    def __init__(self, num_samples: int = 10000, sequence_length: int = 128, noise_level: float = 0.1):
        self.num_samples = num_samples
        self.sequence_length = sequence_length
        self.noise_level = noise_level
        
        # Movement classes (what we're predicting)
        self.movement_labels = [
            'rest', 'grasp', 'release', 'flex_wrist', 'extend_wrist',
            'thumb_oppose', 'index_point', 'peace_sign', 'fist'
        ]
        
        self.data, self.labels, self.complexities = self._generate_dataset()
        
    def _generate_neural_burst(self, duration: int, frequency: float, amplitude: float) -> np.ndarray:
        """Generate synthetic neural burst pattern"""
        t = np.linspace(0, duration / 100, duration)  # simulate at 100Hz
        burst = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Add realistic envelope (rise and decay)
        envelope = np.exp(-((t - duration/200) ** 2) / (2 * (duration/400) ** 2))
        return burst * envelope * 10
    
    def _generate_sample(self, movement_idx: int) -> np.ndarray:
        """Generate a single neural signal sample"""
        # Each movement has characteristic frequency patterns
        base_frequencies = {
            0: [0.0],      # rest - baseline
            1: [8.0, 12.0],   # grasp - alpha/beta
            2: [5.0, 8.0],    # release - theta
            3: [12.0, 20.0],  # flex wrist - beta
            4: [12.0, 20.0],  # extend wrist - beta
            5: [20.0, 30.0],  # thumb oppose - gamma
            6: [20.0, 30.0],  # index point - gamma
            7: [15.0, 25.0],  # peace sign - beta/gamma
            8: [10.0, 15.0]   # fist - alpha/beta
        }
        
        freqs = base_frequencies.get(movement_idx, [5.0, 15.0])
        signal_data = np.zeros(self.sequence_length)
        
        for freq in freqs:
            amplitude = np.random.uniform(0.5, 1.5)
            burst = self._generate_neural_burst(self.sequence_length, freq, amplitude)
            signal_data += burst
        
        # Add background noise (simulating real neural activity)
        noise = np.random.normal(0, self.noise_level, self.sequence_length)
        signal_data += noise
        
        # Add realistic artifacts (muscle noise, eye blinks)
        if np.random.random() < 0.1:
            artifact_duration = np.random.randint(5, 20)
            artifact_start = np.random.randint(0, self.sequence_length - artifact_duration)
            signal_data[artifact_start:artifact_start + artifact_duration] += np.random.uniform(-2, 2, artifact_duration)
        
        return signal_data
    
    def _generate_dataset(self):
        data = []
        labels = []
        complexities = []
        
        for i in range(self.num_samples):
            movement_idx = np.random.randint(len(self.movement_labels))
            sample = self._generate_sample(movement_idx)
            
            # Add temporal structure for complexity
            complexity = np.std(sample) + abs(np.mean(sample))
            
            data.append(sample)
            labels.append(movement_idx)
            complexities.append(complexity)
        
        return torch.FloatTensor(data), torch.LongTensor(labels), torch.FloatTensor(complexities)
    
    def __len__(self):
        return self.num_samples
    
    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx], self.complexities[idx]

class RealTimeDataPipeline:
    """
    Simulates Redis Pub/Sub for real-time data ingestion
    """
    def __init__(self, dataset: NeuralSignalDataset, batch_size: int = 32):
        self.dataset = dataset
        self.batch_size = batch_size
        self.stream_idx = 0
        
    def get_stream_batch(self):
        """Simulates real-time data stream"""
        start = self.stream_idx
        end = min(start + self.batch_size, len(self.dataset))
        
        if start >= len(self.dataset):
            self.stream_idx = 0
            start = 0
            end = self.batch_size
            
        batch_data = self.dataset.data[start:end]
        batch_labels = self.dataset.labels[start:end]
        batch_complexities = self.dataset.complexities[start:end]
        
        self.stream_idx = end
        return batch_data, batch_labels, batch_complexities
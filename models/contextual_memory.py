# models/contextual_memory.py
import torch
import torch.nn as nn
from collections import deque
import numpy as np

class ContextualMemoryLayer(nn.Module):
    """
    Dedicated sub-system that retains short-term task data
    to improve repetitive decision-making.
    """
    def __init__(self, memory_size: int = 100, embedding_dim: int = 128):
        super().__init__()
        self.memory_size = memory_size
        self.embedding_dim = embedding_dim
        
        # Short-term memory buffer (FIFO)
        self.short_term_memory = deque(maxlen=memory_size)
        
        # Memory encoding network
        self.memory_encoder = nn.Linear(embedding_dim, embedding_dim)
        
        # Attention mechanism for memory retrieval
        self.attention = nn.MultiheadAttention(embed_dim=embedding_dim, num_heads=4, batch_first=True)
        
        # Current task context
        self.current_context = None
        
    def store(self, embedding: torch.Tensor, label: str = None):
        """Store experience in short-term memory"""
        memory_item = {
            'embedding': embedding.detach(),
            'timestamp': len(self.short_term_memory),
            'label': label
        }
        self.short_term_memory.append(memory_item)
        
    def retrieve(self, query: torch.Tensor, k: int = 5):
        """Retrieve k most relevant memories"""
        if len(self.short_term_memory) == 0:
            return None
            
        # Compute similarity with stored memories
        memories = torch.stack([item['embedding'] for item in self.short_term_memory])
        
        # Attention-based retrieval
        query = query.unsqueeze(0).unsqueeze(0)  # (1, 1, dim)
        memories = memories.unsqueeze(0)  # (1, seq_len, dim)
        
        attended, attention_weights = self.attention(query, memories, memories)
        
        # Get top-k indices
        top_k_idx = torch.topk(attention_weights.squeeze(), min(k, len(self.short_term_memory))).indices
        
        retrieved_memories = [self.short_term_memory[idx] for idx in top_k_idx]
        return retrieved_memories
    
    def update_context(self, current_embedding: torch.Tensor):
        """Update current task context based on recent memory"""
        relevant_memories = self.retrieve(current_embedding, k=3)
        if relevant_memories:
            context_vector = torch.mean(torch.stack([m['embedding'] for m in relevant_memories]), dim=0)
            self.current_context = context_vector
        else:
            self.current_context = current_embedding
            
        return self.current_context
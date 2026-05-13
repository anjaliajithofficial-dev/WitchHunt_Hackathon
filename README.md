# AxonNova - Neural Intelligence Framework 🧠

**AxonNova** is a next-generation neural intelligence framework designed to bridge the gap between static
AI models and dynamic, real-world applications. Specifically optimized for
**Healthcare and Prosthetic Control**, the framework utilizes biological principles like synaptic scaling
and contextual memory to provide real-time, explainable, and safe neural signal interpretation.

---

## 🚀 Core Innovations

### 1. Dynamic Synaptic Scaling

Unlike traditional models with fixed architectures, AxonNova's `DynamicSynapticLayer` automatically adjusts its network depth based on input complexity.

- **Low Complexity:** Minimal layers are activated to save power and reduce latency.
- **High Complexity:** The full synaptic network is deployed for deep analysis.
- **Efficiency:** Achieves a significantly lower carbon footprint through dynamic inference.

### 2. Contextual Memory Layer

The `ContextualMemoryLayer` mimics short-term human memory. It retains a buffer of recent neural states using an **Attention Mechanism**, allowing the model to improve decision-making during repetitive tasks (e.g., holding a steady grasp).

### 3. Ethics-by-Design Guardrails

Critical for medical applications, the `GuardrailLayer` provides real-time safety filtering:

- **Safety Benchmarks:** Ensures prosthetic force, velocity, and angles remain within anatomical limits.
- **Bias Detection:** Monitors demographic parity in predictions to ensure equitable performance.

### 4. Explainable AI (XAI)

The `ExplainabilityModule` provides transparency into the "Black Box." It generates human-readable reasoning for every movement prediction, mapping specific neural bursts to activated synaptic pathways.

---

## 🛠️ System Architecture

The framework is modularized into several key components:

- **`main.py`**: The central orchestrator that integrates the AI components into the unified AxonNova class.
- **`models/`**:
  - `dynamic_synapse.py`: Implements adaptive depth and synaptic pruning.
  - `contextual_memory.py`: Manages the FIFO memory buffer and attention-based retrieval.
- **`inference/`**:
  - `guardrail_layer.py`: Handles safety checks and output filtering.
- **`data/`**:
  - `synthetic_neural_data.py`: Generates EEG/EMG-like signals for 9 movement classes: _Rest, Grasp, Release, Flex, Extend, Thumb Oppose, Point, Peace, and Fist._
- **`web/`**:
  - `index.html` & `script.js`: A sophisticated real-time dashboard for monitoring signal strength, prediction confidence, and system metrics.

---

## 📊 Dashboard & Visualization

The AxonNova Web Dashboard provides a real-time window into the framework's brain:

- **Neural Signal Visualizer:** Live canvas rendering of input data.
- **Movement Distribution:** Probability charts for all supported gestures.
- **Synaptic Activation Stats:** Visualization of which layers are currently active.
- **Reasoning Chain:** Step-by-step logic display for why a decision was made.

---

### Prerequisites

- Python 3.8+
- PyTorch
- NumPy, SciPy, Matplotlib
- Flask (for the Web Dashboard)

---

### 🎯 Performance Metrics

Accuracy: ~78.2% on synthetic neural validation sets.

Parameters: ~659K (optimized for edge deployment).

Inference Speed: Real-time (<10ms).

Adaptability: Dynamic complexity scoring (0.0 to 1.0).

---

### 🌿 Sustainability

AxonNova is built with "Green AI" principles. By deactivating unnecessary neurons and layers during
low-complexity inputs, the framework reduces computational waste by up to 42% compared to static dense networks.

---

## Demo Website

The project includes a web dashboard where you can:

- See real-time neural signal graphs
- Watch the AI predict movements
- Read explanations for each decision
- View safety guardrail status

---

## 📊 Dashboard & Visualization

                               ![AxonNova Dashboard]

(./screenshots/dashboard_img.png)
(./screenshots/live_demo_img.png)
(./screenshots/live_demo_img2.png)
(./screenshots/explainability_img.png)
(./screenshots/metrics_img.png)
(./screenshots/metrics_img2.png)
The AxonNova Web Dashboard provides a real-time window into the framework's brain...

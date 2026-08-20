## 1. Candidate Models for Local Deployment

To ensure comprehensive evaluation, the following open-source Large Language Models (LLMs) will be tested. The selection
covers a spectrum of parameter sizes to balance computational constraints against response accuracy.

* **Mistral (7B):** A highly efficient baseline model known for robust reasoning capabilities.
* **Qwen 2.5 (7B / Coder):** Chosen for its strong instruction-following performance and efficiency.
* **Meta Llama 3 (8B):** An industry standard with high context retention, serving as a primary benchmark for response
  quality.
* **Google Gemma 2 (2B & 9B):** Selected to evaluate edge computing feasibility. The 2B parameter version will be tested
  for its potential deployment directly on patient endpoint devices.
* **Microsoft Phi-3 Mini (3.8B):** A highly optimized small language model, evaluated for its high efficiency and low
  memory footprint on constrained hardware.

*Note: Google Vertex AI models will be utilized strictly as cloud-based evaluation baselines and as the automated "
Judge" in quality testing, not for final local deployment.*

---

## 2. Testing Methodology and Evaluation Criteria

The evaluation of the aforementioned models will be conducted using a structured, multi-tier testing pipeline.

### 2.1. Hardware and Performance Profiling

Models will be evaluated locally to quantify their computational overhead.

* **Time to First Token (TTFT):** Measuring the latency from prompt submission to the initial system output to assess
  real-time conversational suitability.
* **Inference Latency:** Calculating the average token generation speed (tokens per second).
* **Resource Utilization:** Monitoring peak RAM and GPU allocation during inference to ensure compatibility with
  standard, non-specialized hardware.

### 2.2. Automated Quality Assessment (LLM-as-a-Judge)

To scale the evaluation of qualitative responses, an automated testing pipeline will be implemented.

* **Framework Integration:** Using a cloud-based high-parameter model (e.g., via Google Vertex AI) to act as an
  automated judge.
* **Faithfulness Metric:** Verifying that the model's output strictly adheres to the provided knowledge base without
  generating hallucinations.
* **Answer Relevance:** Assessing how accurately the generated response addresses the specific emotional or educational
  context of the patient's query.

### 2.3. Safety and Guardrails Verification

Strict safety testing is mandatory due to the healthcare context of the application.

* **Medical Trap Red-Teaming:** Injecting queries designed to solicit medical diagnoses or specific treatment
  modifications (e.g., insulin dosage changes).
* **Boundary Enforcement:** Validating that the model reliably refuses to provide medical advice and explicitly directs
  the user to a qualified healthcare professional.

### 2.4. CI/CD Integration for Continuous Evaluation

The evaluation scripts and datasets will be integrated into a CI/CD pipeline.

* **Automated Regression Testing:** Every modification to the system prompts, document knowledge base, or adapter logic
  will trigger an automated test run against the predefined dataset to ensure performance and safety metrics do not
  degrade over time.

### 2.5. Execution Environments

While the final deployment of the system is strictly local, the experimental and evaluation phase supports two execution
environments:

* **Local Execution:** The experiment runs natively or via Docker containers on local hardware. This tests the edge
  computing approach, validating the performance of smaller models under strict hardware constraints without reliance on
  external cloud infrastructure.
* **Google Colab (Cloud Execution):** For rapid evaluation and access to cloud GPUs (e.g., NVIDIA T4) during the testing
  phase, the experiment can be executed in Google Colab. The automated setup is triggered using the following commands:

  ```python
  import os
  from google.colab import userdata
  os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")
  os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
  !rm -rf ai-medical-assistant
  !git clone -b dev https://github.com/Stereopapa/ai-medical-assistant.git
  %cd ai-medical-assistant
  !bash experiments/setup_and_run_colab.sh
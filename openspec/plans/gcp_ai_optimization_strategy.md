# GCP AI Optimization Strategy for Oideachais

## 1. Executive Summary
This document outlines a deep, cost-effective strategy to maximize the initial £200 Google Cloud Platform (GCP) credits for the `Oideachais` platform. Our approach adheres strictly to our open-source ethos by utilizing a hybrid AI architecture that blends Google's managed AI ecosystem (Gemini, Gemma) with leading open-source models (Qwen-VL, GLM) and integrations (Zed.AI). 

We establish a unified, well-documented architecture that allows the platform to stay safely within the GCP ecosystem while securely interfacing with internal and external open-source capabilities.

## 2. Core Strategic Principles
1.  **Strict Open-Source First:** Prioritize open weights, open standards (OpenAI API compatibility layer), and open-source middleware.
2.  **Radical Credit Optimization:** Use GCP serverless free tiers (Cloud Run, Cloud Functions) and Spot VMs to stretch the £200 runway significantly beyond standard operating timelines.
3.  **Unified Ecosystem:** Maintain a single secure gateway within GCP. This centralizes logging, manages API keys natively via Google Secret Manager, and ensures all outbound calls route through our controlled infrastructure.

## 3. The Unified "Stay in GCP" Architecture

To seamlessly route calls between proprietary and open-source models without leaving the GCP security perimeter, we will deploy a unified AI Gateway (e.g., **LiteLLM** or **Pydantic AI Gateway**).

### Deployment Mechanics
1.  **Serverless Gateway:** Deploy the AI Gateway via Docker to **Cloud Run**. 
    *   *Cost Benefit:* Cloud Run offers a generous free tier (2 million requests/month). It scales to zero when not in use, ensuring 0 baseline cost.
2.  **Native Integrations:** Connect the Gateway to Google Secret Manager to hold credentials for Vertex AI or any external fallback APIs.
3.  **Internal VPC Routing:** Configure the Gateway to route traffic to internally hosted open-source models (via Private IP) to avoid egress charges.

## 4. Deploying the AI Ecosystem

### 4.1 Google AI Ecosystem (Vertex AI)
*   **Gemini (1.5 Flash/Pro):** Used primarily for heavy reasoning, multimodal analysis, and complex coding tasks where context windows are critical.
    *   *Optimization:* Utilize Vertex AI endpoints and implement **Prompt Caching** to significantly drop the token input costs.
*   **Gemma (Open Weights):** Deployed via Vertex AI Model Garden as our primary safe, lightweight, on-demand language model. By using managed endpoints rather than provisioning dedicated GPUs for smaller models, we minimize idle costs.

### 4.2 Validated Open-Source Integrations
*   **Qwen-VL & GLM:**
    *   *Deployment:* Provision a **Compute Engine Spot VM** (e.g., `n1-standard-4` with 1x NVIDIA T4 or L4 GPU) attached to the same VPC network as the Cloud Run Gateway.
    *   *Serving:* Use high-throughput open-source inference engines like `vLLM` or `Ollama` via Docker on the VM.
    *   *Optimization:* Spot VMs offer 60-91% discounts. Implement a lightweight Cloud Function triggered by the Gateway or a Cloud Scheduler that spins up the VM only during active development/usage hours, and shuts it down afterward.
*   **Zed.AI (Collaborative Coding Workflow):**
    *   Configure Zed's custom model provider to point directly to our **Cloud Run Gateway URL**.
    *   This allows the development team to utilize Zed's powerful AI features while consuming the £200 GCP credits (routing to Gemini or our hosted Qwen-VL/GLM) instead of paying for separate, external AI subscriptions.

## 5. Step-by-Step Implementation Roadmap

1.  **Foundation & Budgets:** 
    *   Set strict GCP billing alarms at £50, £100, £150, and £190.
    *   Setup Google Secret Manager for all keys.
2.  **Deploy AI Gateway:**
    *   Create a Dockerized LiteLLM instance.
    *   Deploy to Cloud Run (allow unauthenticated internal VPC access, but restrict public access with GCP IAM / API keys).
3.  **Configure Vertex AI:**
    *   Enable Vertex AI APIs.
    *   Add Gemini 1.5 Flash and Gemma routing rules to the Gateway.
4.  **Provision Spot VM for OS Models:**
    *   Write a Terraform or startup script for a T4 Spot VM that automatically pulls the `vLLM` container and pre-loads Qwen-VL/GLM weights from a GCP Cloud Storage bucket (free tier).
    *   Configure the Gateway to route `qwen` or `glm` model requests to the VM's internal IP.
5.  **Connect Client Endpoints:**
    *   Point Zed.AI custom configuration to the Gateway.
    *   Point the `Oideachais` backend environment variables to the Gateway.

## 6. Conclusion
By channeling all requests through a serverless open-source AI Gateway hosted on Cloud Run, and aggressively leveraging Vertex AI alongside heavily discounted Spot VMs for Qwen-VL/GLM, `Oideachais` can maintain a robust, open-source aligned AI infrastructure. This setup ensures the £200 credit is spent purely on essential compute and tokens, with zero waste on idle infrastructure.
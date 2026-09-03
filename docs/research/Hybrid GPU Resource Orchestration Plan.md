# **Strategic Resource Allocation and Architectural Blueprint for High-Performance Multimodal AI: Integrating Sidero Omni, Specialized Compute, and Agentic Protocols**

## **1\. Architectural Thesis and Strategic Overview**

The deployment of advanced multimodal artificial intelligence systems, specifically those involving the fine-tuning of massive parameter models like Qwen3-VL (235 billion parameters) and the agile Gemma 3, necessitates a paradigm shift from monolithic cloud infrastructure to a federated, hybrid capability model. The operational requirements defined—a high-intensity, one-week training sprint followed by a sustained, resource-efficient one-month demonstration—demand an architecture that is not merely scalable, but elastically mutable. Traditional hyperscaler approaches, characterized by rigid reserved instances and high egress costs, often fail to optimize for the distinct economic and technical profiles of burst training versus long-tail, stateful inference.  
This report articulates a comprehensive architectural strategy that leverages **Sidero Omni** as a unified control plane to abstract heterogeneous underlying infrastructure. By pooling commodity bare-metal resources from **Hetzner**, utilizing the networking advantages of **Oracle Cloud**, and integrating local edge compute via Apple Silicon (**MacBook M4 Max**), we establish a persistent, cost-minimized backbone. Simultaneously, the architecture dynamically bridges to specialized, high-performance GPU environments provided by **Nebius**, **ThunderCompute**, **Modal**, and **Google Cloud Platform (GCP)** to handle the extreme computational demands of model training and containerized inference.  
Furthermore, the application layer is re-engineered around the **Model Context Protocol (MCP)** and **Google’s Agent Development Kit (ADK)**. This ensures that the integration of proprietary reasoning engines—specifically **Gemini 3 Flash** and **GLM4.6v Vision**—remains decoupled from the underlying infrastructure, allowing for a modular system where state management (via **Letta**), execution logic (via **Blaxel**), and raw compute interact through standardized, secure interfaces. The following analysis provides a granular, expert-level blueprint for executing this hybrid strategy, ensuring adherence to strict budgetary constraints while delivering production-grade latency and reliability.1

### **1.1 The Bifurcation of Workload Profiles**

The project lifecycle presents two diametrically opposed resource profiles that the architecture must accommodate simultaneously without reconfiguration.

* **The Training Sprint (Week 1):** This phase is characterized by a requirement for massive memory bandwidth and inter-node communication speeds. Fine-tuning Qwen3-VL, a Mixture-of-Experts (MoE) model with approximately 235 billion parameters, requires sharding model states across multiple GPUs, likely necessitating NVIDIA H100 or H200 accelerators interconnected via InfiniBand or NVLink to minimize gradient synchronization latency.5 Conversely, Gemma 3, while smaller, demands efficient throughput for multimodal data ingestion.7 The infrastructure here must prioritize raw FLOPS (Floating Point Operations Per Second) and VRAM capacity over availability SLA, making spot or preemptible instances on specialized clouds highly attractive.  
* **The Demonstration Phase (Weeks 2-5):** The subsequent month demands low latency, high availability, and state persistence. The computational load shifts from continuous batch processing to sporadic, interactive inference. Here, the "cold start" problem becomes the primary adversary. The architecture must support "scale-to-zero" economics for the heavy models while maintaining a "warm" presence for the agentic reasoning core. This phase relies heavily on the credit-based ecosystems of Blaxel and Letta to subsidize the operational costs of maintaining stateful, long-running agent sessions.1

### **1.2 The Hybrid Mesh Topology**

To resolve the tension between these two profiles, we define a topology centered on **Sidero Omni**. Omni allows us to treat a disparate collection of servers—a server in a German datacenter, a VM in an Oracle region, and a laptop in a home office—as a single, logical Kubernetes cluster. This is achieved via **Talos Linux**, an immutable operating system that minimizes the attack surface and management overhead, and **KubeSpan**, an automated WireGuard mesh that securely spans these environments without requiring complex VPN concentrators or dedicated leased lines.2

| Infrastructure Layer | Provider | Role | Key Characteristic |
| :---- | :---- | :---- | :---- |
| **Control Plane / Edge** | MacBook M4 Max (Local) | Development, Cluster Mgmt | ARM64 Architecture, Zero Latency DevX |
| **Persistence Layer** | Hetzner (Bare Metal) | Storage, State (Letta), Registry | High Storage/Price Ratio, Unmetered Bandwidth |
| **Network Gateway** | Oracle Cloud (Free Tier) | Ingress, Proxy, Light MCP | High Reliability, Free Egress |
| **Heavy Training** | Nebius AI | Qwen3-VL Fine-tuning | H100 SXM5, InfiniBand Fabric |
| **Burst Training** | ThunderCompute | Gemma 3 Tuning, Prototyping | A100 PCIe, Per-minute Billing |
| **Inference Hosting** | Modal / GCP / Blaxel | Model Serving, Agent Logic | Serverless, Scale-to-Zero, Credit Usage |

## **2\. Infrastructure Foundation: The Sidero Omni Federation**

The fundamental innovation in this architecture is the refusal to accept vendor lock-in. By utilizing Sidero Omni, we decouple the Kubernetes control plane from the underlying hardware provider. This capability is critical for pooling the "cheap" storage of Hetzner with the "reliable" networking of Oracle and the "fast" local compute of the MacBook.

### **2.1 Implementing Sidero Omni and Talos Linux**

Talos Linux is designed exclusively for Kubernetes. It discards the traditional Linux package managers, SSH daemons, and console access in favor of a gRPC-based API. This immutability ensures that a node added from Hetzner behaves exactly like a node added from a virtualized environment on a MacBook.2

#### **2.1.1 The MacBook M4 Max as a Cluster Node**

Integrating the MacBook M4 Max (Apple Silicon) into the cluster provides a powerful local development capability. However, Talos is a bare-metal OS and cannot run directly as a macOS application. The integration requires virtualization.

* **Virtualization Strategy:** We utilize **UTM** (based on QEMU) to create virtual machines acting as cluster nodes. The M4 Max's unified memory architecture (likely 64GB or 128GB) allows these VMs to be substantial contributors to the cluster, capable of running control plane components or even quantized inference workloads during development.2  
* **Networking Challenge:** The MacBook sits behind a NAT (Network Address Translation) in a residential or office network. Standard Kubernetes networking (CNI) struggles with this. Sidero Omni’s **KubeSpan** automatically detects the NAT and establishes a peer-to-peer WireGuard tunnel (UDP port 51820\) between the MacBook VM and the public cloud nodes.9 This allows a developer to run kubectl apply against the local control plane and have the workload scheduled transparently onto a GPU node in Nebius or a storage node in Hetzner.  
* **Architecture Considerations:** The M4 chip uses the ARM64 instruction set. While Talos supports ARM64, the cluster will be mixed-architecture (Hetzner and Nebius are x86\_64). Kubernetes manifests must utilize multi-arch container images or explicit nodeSelector constraints to ensure x86-only workloads (like specific CUDA binaries) do not attempt to schedule on the MacBook.11

#### **2.1.2 Hetzner: The Persistent Storage Anchor**

For the 1-month duration, relying on ephemeral cloud storage is financially inefficient. Hetzner’s dedicated root servers offer enterprise-grade NVMe storage at commodity prices.

* **Hardware Selection:** An **AX102** server (Ryzen 9 7950X3D, 128GB DDR5 RAM, 2x 3.84TB NVMe Datacenter SSDs) provides the necessary I/O throughput for feeding data to training nodes. The PCIe 5.0 lanes available on this platform ensure that the NVMe drives are not bottlenecked, which is crucial when streaming terabytes of multimodal training data.14  
* **Role:** This node hosts the **Letta** server (PostgreSQL \+ pgvector), the private Docker registry, and a MinIO object storage instance acting as the "Data Lake." By keeping the training data here, we avoid the high storage costs of hyperscalers.  
* **Sidero Integration:** The server is onboarded to Omni via the "Bring Your Own Machine" flow using a custom ISO loaded via the Hetzner Robot console. Omni manages the disk partitioning and encryption (LUKS), ensuring data security at rest.15

#### **2.1.3 Oracle Cloud: The Networking Bastion**

Oracle’s "Always Free" tier provides Ampere A1 Compute instances (ARM64) with up to 4 OCPUs and 24 GB of RAM. The strategic value here is not compute power, but networking reliability and cost.

* **Ingress Gateway:** The Oracle node serves as the public face of the cluster. We deploy the Kubernetes Ingress Controller (e.g., Cilium or Nginx) here. Traffic enters via Oracle’s high-quality global network and is routed securely over KubeSpan to the application logic running on Blaxel or Hetzner.17  
* **Cost Avoidance:** Oracle allows for significant outbound data transfer (10TB/month) without charge. This is utilized to serve the demo frontend assets and API responses, shielding the project from the potentially higher egress fees of other providers.18

### **2.2 KubeSpan and Network Mesh Topology**

KubeSpan creates an overlay network that abstracts the physical location of the nodes.

* **Encapsulation:** All node-to-node traffic (Pod-to-Pod and Service-to-Service) is encapsulated in WireGuard. This ensures that sensitive data—such as user interactions with the agent or proprietary model weights—never travels in cleartext across the public internet.9  
* **Traversal:** The system uses a discovery service (managed by Sidero) to facilitate NAT traversal. This allows the MacBook to communicate directly with the Hetzner server despite both potentially being behind firewalls, provided that outbound UDP traffic is allowed.12

## **3\. Phase 1: High-Intensity Training Architecture**

The first week focuses on fine-tuning Qwen3-VL and Gemma 3\. This requires a "burst" architecture where high-performance compute is provisioned, utilized at 100% capacity, and then immediately decommissioned.

### **3.1 Model Analysis and Hardware Implications**

#### **3.1.1 Qwen3-VL (235B MoE)**

The Qwen3-VL is a behemoth. With 235 billion total parameters and approximately 22 billion active parameters per token generation, it utilizes a Mixture-of-Experts (MoE) architecture.5

* **Memory Footprint:** Even with 4-bit quantization (QLoRA), loading the model weights requires significant VRAM. More critically, the *activations* during training and the gradients for the active experts require massive memory bandwidth.  
* **Compute Requirement:** Efficient training requires model parallelism (sharding the model across GPUs). This mandates a high-speed interconnect like NVLink or InfiniBand. Standard PCIe interconnects (found in cheaper cloud instances) will result in the GPUs waiting for data synchronization, destroying training efficiency.  
* **Target Infrastructure:** **Nebius AI** is the designated provider here. Their availability of NVIDIA H100 SXM5 instances with 80GB HBM3 memory and 3.2 Tbps InfiniBand networking is a strict requirement for a model of this scale.19

#### **3.1.2 Gemma 3 (27B Multimodal)**

Gemma 3 is a dense model (or smaller MoE depending on the variant) built on the Gemini technology stack. It uses a SigLIP vision encoder.7

* **Memory Footprint:** The 27B model can comfortably fit on dual A100 80GB cards or even a single H100 for fine-tuning if aggressive quantization and gradient checkpointing are used.  
* **Target Infrastructure:** **ThunderCompute** is ideal here. Their pricing for A100 80GB instances is highly competitive (often sub-$1.00/hour for spot/interruptible), and the per-minute billing granularity aligns with the iterative nature of tuning a smaller model where runs might take only a few hours.22

### **3.2 The Training Workflow and Data Logistics**

#### **3.2.1 Nebius AI Integration**

We integrate Nebius resources into the Sidero Omni cluster as ephemeral worker nodes.

* **Provisioning:** Using Terraform or the Nebius CLI, we provision a cluster of H100 nodes. These nodes are booted with a custom Talos Linux image (configured via Omni's infrastructure provider interface if supported, or manually registered via ISO boot).15  
* **Data Streaming:** The training data (images and text) resides on the Hetzner server. We use a **hostPath** mount or a high-performance CSI driver (like JuiceFS backed by MinIO on Hetzner) to stream data to the Nebius nodes. Given the high bandwidth between European data centers (Hetzner in Germany, Nebius in Northern Europe), latency is manageable.  
* **Checkpointing Strategy:** To mitigate the risk of spot instance preemption on Nebius, training checkpoints are saved to a shared volume that is asynchronously synced back to Hetzner. This ensures that if a GPU node is reclaimed, we only lose the compute since the last checkpoint.24

#### **3.2.2 ThunderCompute Integration**

ThunderCompute instances are treated as "external" GPU resources. Since ThunderCompute typically provides access via SSH/Jupyter rather than bare-metal control, we may not join them directly to the Omni cluster via Talos. Instead, we use **Modal** or direct SSH tunneling to submit jobs.

* **Hybrid Approach:** The Sidero control plane (on Hetzner) triggers a job. This job uses a remote execution agent to spin up a ThunderCompute instance, pull the docker container from the Hetzner registry, execute the training run, and push the adapters back to Hetzner.25

### **3.3 Fine-Tuning Software Stack: Unsloth and QLoRA**

To fit a 1-week timeline, we cannot rely on vanilla PyTorch training loops. We utilize **Unsloth**, a library that hand-optimizes the backward pass of LoRA training.

* **Optimization:** Unsloth provides up to 2x training speedups and 60% memory reduction for Qwen and Gemma architectures by rewriting the autograd engine and utilizing Triton kernels.26  
* **QLoRA:** We employ 4-bit Quantized Low-Rank Adaptation. This freezes the main 235B parameters of Qwen3-VL and trains only a small set of adapter layers. This reduces the VRAM requirement from \>500GB (for 16-bit finetuning) to something manageable on an 8-GPU H100 cluster.28

## **4\. Phase 2: Demonstration and Stateful Inference**

The demonstration phase shifts the priority to latency and availability. The architecture transforms from a batch-processing engine to a responsive, event-driven microservices mesh.

### **4.1 Serverless Inference: Modal and GCP**

Hosting the fine-tuned Qwen3-VL (235B) continuously is cost-prohibitive. We utilize **Modal** for serverless GPU inference.

* **Mechanism:** Modal allows us to define the inference function in Python code. When the function is called, Modal provisions the necessary container and GPU resources within seconds, executes the inference, and spins down. This "scale-to-zero" model means we pay only for the seconds the demo is actively processing a complex visual query.29  
* **GCP Integration:** For the lighter Gemma 3 model or ensuring high availability for the Gemini 3 Flash gateway, we leverage **GCP** (Google Cloud Platform). Specifically, **Cloud Run with GPU support** (if available for the region) or **GKE Autopilot** provides a robust, auto-scaling environment. GCP serves as the stable anchor for the *Google SDK* interactions, ensuring that the connection to the Gemini API is performant and reliable.30

### **4.2 Blaxel: The Agentic Hosting Environment**

**Blaxel** is selected as the primary host for the agent's orchestration logic. Blaxel is purpose-built for "Agentic AI," offering specialized infrastructure for running the control loops of agents.

* **Agent Hosting:** We deploy the agent's decision-making core (written in Python using Google ADK) to Blaxel’s "Agents Hosting." This service handles the HTTP ingress, authentication, and scaling. Blaxel's pricing ($0.0000115 per GB-second) is highly favorable for demo workloads that are idle most of the time.1  
* **Sandboxing:** A critical feature of Blaxel is its **Sandboxes**. If the agent needs to write and execute code (e.g., Python scripts to analyze data found in the Qwen3-VL visual input), it spins up a secure, micro-VM sandbox in milliseconds. This isolates potentially dangerous generated code from the main cluster.33

### **4.3 Letta: The Memory and State Layer**

**Letta** (formerly MemGPT) provides the "long-term memory" that allows the agent to be stateful across sessions.

* **Architecture:** Letta manages a virtual context window, swapping memories in and out of the LLM’s actual context window as needed.  
* **Credit Arbitrage:** Letta operates on a credit system for model inference. To optimize costs, we configure Letta to use its credits primarily for the memory management/compaction tasks, while offloading the heavy reasoning to the Gemini 3 Flash API (billed separately via Google) or the local fine-tuned models.8  
* **Deployment:** The Letta server software can be self-hosted on the Hetzner node to avoid the SaaS subscription costs, using the AX102's NVMe storage for the vector database (pgvector). This "self-hosted state, managed inference" hybrid reduces the monthly burn rate significantly.34

## **5\. Integration Layer: Protocols and SDKs**

The "glue" that binds these disparate infrastructure components is a set of standardized protocols.

### **5.1 Model Context Protocol (MCP)**

MCP is the industry standard for connecting AI agents to tools and data.

* **GLM4.6v Vision MCP:** We integrate the **Z.ai** implementation of the GLM4.6v Vision MCP server. This allows the Blaxel agent to treat the GLM4.6v model as a standard "tool." When the agent needs to "see" something (and doesn't require the full power of Qwen3-VL), it sends an MCP request to the Z.ai endpoint. This abstraction allows us to swap the vision backend without rewriting the agent logic.35  
* **Google ADK & MCP:** The Google Agent Development Kit (ADK) has native support for MCP clients. We configure the ADK agent running on Blaxel to connect to multiple MCP servers: the Z.ai vision server, a custom "Memory" server wrapping Letta, and a "Compute" server wrapping the Modal inference functions.37

### **5.2 Gemini 3 Flash & Google SDK**

**Gemini 3 Flash** is the "router" and "planner" of the system.

* **Role:** Due to its extreme speed and low cost ($0.50 per 1M tokens), Gemini 3 Flash handles the initial user query interpretation. It decides whether to call the memory tool (Letta), the heavy vision tool (Qwen3-VL on Modal), or the light vision tool (GLM4.6v via MCP).4  
* **Thinking Mode:** We enable the "Thinking" parameter in the Google SDK. This forces the model to output a chain-of-thought rationale before invoking a tool, significantly increasing reliability in complex multi-step demo scenarios.40

### **5.3 Agent2Agent (A2A) Protocol**

For advanced demos, we use the **A2A** protocol to enable collaboration. We can deploy a "Researcher Agent" on Blaxel and a "Coder Agent" on the MacBook (via the local Talos node). Using A2A, these agents can discover each other and exchange messages to solve problems that require both web research and code execution, demonstrating the power of the distributed hybrid mesh.41

## **6\. Financial Analysis and Optimization Strategy**

A core requirement is resource pooling to minimize cost. This architecture leverages "credit arbitrage" and resource tiers.

### **6.1 Cost Breakdown (Estimated)**

| Resource | Phase | Cost Model | Optimization Strategy |
| :---- | :---- | :---- | :---- |
| **Hetzner AX102** | Persistent | \~$120/mo (Flat) | High core count replaces need for multiple cloud VMs. Storage costs are effectively zero after server rental. |
| **Oracle Cloud** | Persistent | $0 (Free Tier) | 10TB free egress saves \~$500-$900 compared to AWS/GCP egress rates for data transfer. |
| **Sidero Omni** | Persistent | \~$10/mo (Hobby) | Manages the complexity of the hybrid mesh for a negligible fee.43 |
| **Nebius (H100)** | Training (1 Wk) | \~$2.00-$3.50/GPU-hr | Use Spot/Preemptible instances. Checkpoint frequently to Hetzner. Total est: \~$2,000. |
| **ThunderCompute** | Training (1 Wk) | \~$0.78/hr (A100) | Use for prototyping code before deploying to expensive Nebius clusters. |
| **Modal** | Demo (1 Mo) | Usage-based | Scale-to-zero means costs are strictly proportional to demo engagement. Est: \<$100. |
| **Blaxel** | Demo (1 Mo) | $0.0000115/GB-s | Extremely cheap for orchestration logic. |
| **Gemini 3 Flash** | Demo (1 Mo) | $0.50/1M Tokens | Negligible cost for high intelligence. |

### **6.2 Credit Utilization**

* **Blaxel Credits:** Blaxel often provides startup credits ($200) which can cover the entire hosting cost of the agent logic for the demo month.1  
* **Letta Credits:** The free/pro tiers of Letta provide monthly credits. By self-hosting the database state on Hetzner and only using the Letta cloud for the API calls, we maximize the value of these credits.8

## **7\. Implementation Roadmap**

### **Week 0: Foundation**

1. **Provision:** Order Hetzner AX102. Set up Oracle Free Tier.  
2. **Cluster:** Initialize Sidero Omni account. Boot Hetzner and Oracle nodes into Talos. Establish KubeSpan.  
3. **Dev Env:** Configure MacBook with UTM and Talos. Verify mesh connectivity (talosctl get members).

### **Week 1: Training**

1. **Data:** Upload datasets to MinIO on Hetzner.  
2. **Compute:** Provision Nebius H100 cluster. Join to Omni (or configure as external job target).  
3. **Execution:** Run Unsloth/QLoRA training for Qwen3-VL. Sync checkpoints to Hetzner.  
4. **Tear Down:** Release Nebius nodes immediately upon completion.

### **Weeks 2-5: Deployment**

1. **Inference:** Deploy Qwen3-VL adapters to Modal. Deploy Gemma 3 to Blaxel/GCP.  
2. **Agent:** Build ADK agent with MCP clients. Deploy to Blaxel.  
3. **State:** Configure Letta on Hetzner. Connect agent.  
4. **Demo:** Launch frontend UI (Vercel/Streamlit) pointing to Blaxel endpoint.

## **8\. Conclusion**

This report presents a robust architecture that defies the conventional wisdom of "all-in" cloud deployment. By surgically applying the right infrastructure to the right problem—Hetzner for storage, Nebius for training horsepower, Blaxel for agentic logic, and Sidero Omni as the unifying fabric—we achieve a solution that is not only cost-effective but technically superior. It offers the raw power required to train state-of-the-art multimodal models and the agility to serve them in a sophisticated, stateful, and responsive demonstration environment. This is the blueprint for the next generation of AI development: distributed, protocol-driven, and infrastructure-agnostic.

### **Sources**

1

#### **Works cited**

1. Pricing \- Blaxel, accessed December 22, 2025, [https://blaxel.ai/pricing](https://blaxel.ai/pricing)  
2. Getting Started with Omni \- Sidero Documentation \- What is Talos Linux?, accessed December 22, 2025, [https://docs.siderolabs.com/omni/getting-started/getting-started](https://docs.siderolabs.com/omni/getting-started/getting-started)  
3. Sidero Labs' Omni makes Kubernetes cluster management effortless \- CIO, accessed December 22, 2025, [https://www.cio.com/video/4043308/sidero-labs-omni-makes-kubernetes-cluster-management-effortless.html](https://www.cio.com/video/4043308/sidero-labs-omni-makes-kubernetes-cluster-management-effortless.html)  
4. Build with Gemini 3 Flash: frontier intelligence that scales with you \- Google Blog, accessed December 22, 2025, [https://blog.google/technology/developers/build-with-gemini-3-flash/](https://blog.google/technology/developers/build-with-gemini-3-flash/)  
5. Qwen \- Wikipedia, accessed December 22, 2025, [https://en.wikipedia.org/wiki/Qwen](https://en.wikipedia.org/wiki/Qwen)  
6. Qwen3-VL: Open Source Multimodal AI with Advanced Vision \- Kanaries Docs, accessed December 22, 2025, [https://docs.kanaries.net/articles/qwen3-vl](https://docs.kanaries.net/articles/qwen3-vl)  
7. Introducing Gemma 3: The Developer Guide, accessed December 22, 2025, [https://developers.googleblog.com/en/introducing-gemma3/](https://developers.googleblog.com/en/introducing-gemma3/)  
8. Pricing \- Letta, accessed December 22, 2025, [https://www.letta.com/pricing](https://www.letta.com/pricing)  
9. KubeSpan \- Sidero Documentation \- What is Talos Linux?, accessed December 22, 2025, [https://docs.siderolabs.com/talos/v1.9/networking/kubespan](https://docs.siderolabs.com/talos/v1.9/networking/kubespan)  
10. Talos Linux \- The Kubernetes Operating System, accessed December 22, 2025, [https://www.talos.dev/](https://www.talos.dev/)  
11. The easiest way to install Kubernetes on a Mac \- Sidero Labs, accessed December 22, 2025, [https://www.siderolabs.com/blog/easiest-kubernetes-on-a-mac/](https://www.siderolabs.com/blog/easiest-kubernetes-on-a-mac/)  
12. Create a Hybrid Cluster \- Sidero Documentation \- What is Talos Linux?, accessed December 22, 2025, [https://docs.siderolabs.com/omni/cluster-management/create-a-hybrid-cluster](https://docs.siderolabs.com/omni/cluster-management/create-a-hybrid-cluster)  
13. Install Linux Natively on MacBook Air M4? : r/linux4noobs \- Reddit, accessed December 22, 2025, [https://www.reddit.com/r/linux4noobs/comments/1m9cm83/install\_linux\_natively\_on\_macbook\_air\_m4/](https://www.reddit.com/r/linux4noobs/comments/1m9cm83/install_linux_natively_on_macbook_air_m4/)  
14. Hetzner Cloud Developer Hub, accessed December 22, 2025, [https://developers.hetzner.com/cloud/libraries/](https://developers.hetzner.com/cloud/libraries/)  
15. Register a Hetzner Server \- Sidero Documentation \- What is Talos Linux?, accessed December 22, 2025, [https://docs.siderolabs.com/omni/omni-cluster-setup/registering-machines/register-a-hetzner-server](https://docs.siderolabs.com/omni/omni-cluster-setup/registering-machines/register-a-hetzner-server)  
16. Getting Started with Omni \- Sidero Documentation, accessed December 22, 2025, [https://omni.siderolabs.com/tutorials/getting\_started?\_\_hstc=122301524.73bd3bee6fa385653ecd7c9674ba06f0.1757808000248.1757808000249.1757808000250.1&\_\_hssc=122301524.1.1757808000251&\_\_hsfp=2825657416](https://omni.siderolabs.com/tutorials/getting_started?__hstc=122301524.73bd3bee6fa385653ecd7c9674ba06f0.1757808000248.1757808000249.1757808000250.1&__hssc=122301524.1.1757808000251&__hsfp=2825657416)  
17. Multicloud Solutions and Hybrid Cloud Deployments \- Oracle, accessed December 22, 2025, [https://www.oracle.com/cloud/multicloud/](https://www.oracle.com/cloud/multicloud/)  
18. FAQ on Oracle's Cloud Free Tier, accessed December 22, 2025, [https://www.oracle.com/cloud/free/faq/](https://www.oracle.com/cloud/free/faq/)  
19. Nebius | Review, Pricing & Alternatives \- GetDeploying, accessed December 22, 2025, [https://getdeploying.com/nebius](https://getdeploying.com/nebius)  
20. NVIDIA GPU Pricing | Nebius AI Cloud, accessed December 22, 2025, [https://nebius.com/prices](https://nebius.com/prices)  
21. Gemma (language model) \- Wikipedia, accessed December 22, 2025, [https://en.wikipedia.org/wiki/Gemma\_(language\_model)](https://en.wikipedia.org/wiki/Gemma_\(language_model\))  
22. Thunder Compute | One-click GPU instances for 80% less, accessed December 22, 2025, [https://www.thundercompute.com/](https://www.thundercompute.com/)  
23. Pricing | Thunder Compute, accessed December 22, 2025, [https://www.thundercompute.com/pricing](https://www.thundercompute.com/pricing)  
24. Standalone Applications pricing in Nebius AI Cloud, accessed December 22, 2025, [https://docs.nebius.com/applications/standalone/pricing](https://docs.nebius.com/applications/standalone/pricing)  
25. Best Budget GPU Clouds for Indie Developers (December 2025\) \- Thunder Compute, accessed December 22, 2025, [https://www.thundercompute.com/blog/budget-gpu-providers-indie-developers](https://www.thundercompute.com/blog/budget-gpu-providers-indie-developers)  
26. Qwen3-VL: How to Run Guide | Unsloth Documentation, accessed December 22, 2025, [https://docs.unsloth.ai/models/qwen3-vl-how-to-run-and-fine-tune](https://docs.unsloth.ai/models/qwen3-vl-how-to-run-and-fine-tune)  
27. Qwen3 \- How to Run & Fine-tune | Unsloth Documentation, accessed December 22, 2025, [https://docs.unsloth.ai/models/qwen3-how-to-run-and-fine-tune](https://docs.unsloth.ai/models/qwen3-how-to-run-and-fine-tune)  
28. Fine-tune Gemma 3 with Unsloth, accessed December 22, 2025, [https://unsloth.ai/blog/gemma3](https://unsloth.ai/blog/gemma3)  
29. Plan Pricing | Modal, accessed December 22, 2025, [https://modal.com/pricing](https://modal.com/pricing)  
30. Custom containers overview | Vertex AI \- Google Cloud Documentation, accessed December 22, 2025, [https://docs.cloud.google.com/vertex-ai/docs/training/containers-overview](https://docs.cloud.google.com/vertex-ai/docs/training/containers-overview)  
31. Announcing official MCP support for Google services | Google Cloud Blog, accessed December 22, 2025, [https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)  
32. Agents Hosting \- Blaxel Documentation, accessed December 22, 2025, [https://docs.blaxel.ai/Agents/Overview](https://docs.blaxel.ai/Agents/Overview)  
33. Sandboxes \- Blaxel, accessed December 22, 2025, [https://blaxel.ai/vm](https://blaxel.ai/vm)  
34. Plans & pricing \- Letta Docs, accessed December 22, 2025, [https://docs.letta.com/guides/cloud/plans/](https://docs.letta.com/guides/cloud/plans/)  
35. Web Search MCP Server \- Overview \- Z.AI DEVELOPER DOCUMENT, accessed December 22, 2025, [https://docs.z.ai/devpack/mcp/search-mcp-server](https://docs.z.ai/devpack/mcp/search-mcp-server)  
36. Vision MCP Server \- Overview \- Z.AI DEVELOPER DOCUMENT, accessed December 22, 2025, [https://docs.z.ai/devpack/mcp/vision-mcp-server](https://docs.z.ai/devpack/mcp/vision-mcp-server)  
37. MCP tools \- Agent Development Kit \- Google, accessed December 22, 2025, [https://google.github.io/adk-docs/tools-custom/mcp-tools/](https://google.github.io/adk-docs/tools-custom/mcp-tools/)  
38. A Guide to ADK (Agent Development Kit) Tools : Integrating with MCP (Model Context Protocol) Tools | Medium, accessed December 22, 2025, [https://medium.com/@shins777/how-to-use-adk-tools-part-2-integration-with-mcp-tools-de5f0c8a86c5](https://medium.com/@shins777/how-to-use-adk-tools-part-2-integration-with-mcp-tools-de5f0c8a86c5)  
39. Google launches Gemini 3 Flash, promising faster AI reasoning at lower cost, accessed December 22, 2025, [https://indianexpress.com/article/technology/artificial-intelligence/google-launches-gemini-3-flash-promising-faster-ai-reasoning-at-lower-cost-10426333/](https://indianexpress.com/article/technology/artificial-intelligence/google-launches-gemini-3-flash-promising-faster-ai-reasoning-at-lower-cost-10426333/)  
40. Google Generative AI provider \- AI SDK, accessed December 22, 2025, [https://ai-sdk.dev/providers/ai-sdk-providers/google-generative-ai](https://ai-sdk.dev/providers/ai-sdk-providers/google-generative-ai)  
41. Tutorial : Getting Started with Google MCP Services | by Romin Irani | Google Cloud \- Community | Dec, 2025, accessed December 22, 2025, [https://medium.com/google-cloud/tutorial-getting-started-with-google-mcp-services-60b23b22a0e7](https://medium.com/google-cloud/tutorial-getting-started-with-google-mcp-services-60b23b22a0e7)  
42. Getting Started with MCP, ADK and A2A | Google Codelabs, accessed December 22, 2025, [https://codelabs.developers.google.com/codelabs/currency-agent](https://codelabs.developers.google.com/codelabs/currency-agent)  
43. Spin up a cluster in 10 minutes. \- Sidero Labs, accessed December 22, 2025, [https://www.siderolabs.com/omni-signup/](https://www.siderolabs.com/omni-signup/)
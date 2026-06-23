# **Architectural Blueprint for the "Celtic Knowledge Grid": A Decentralized, Agentic, and Gamified Educational Ecosystem**

## **Executive Summary**

This report presents a comprehensive architectural analysis and strategic roadmap for the development of a decentralized, open-source educational environment anchored in Celtic mythology and powered by autonomous agentic workflows. The proposed system aims to transcend the limitations of traditional Learning Management Systems (LMS) and speculative "Play-to-Earn" models by establishing a "Learn-to-Earn" economy based on technical utility and reputation.  
The core of this architecture is the integration of the **x402 protocol**, a revival of the dormant HTTP 402 "Payment Required" status code, which enables autonomous software agents to negotiate value transfers—specifically a custom Celtic utility currency—without human intervention. This capability is critical for reducing friction in a gamified environment where students, represented by digital "Familiars," navigate a "Pokémon Go" style curriculum map.  
To support this agentic economy, the report evaluates the **Model Context Protocol (MCP)** and its user interface extension, **mcp-ui**, as the standard for delivering interactive assessments (MCQs) and rich media directly within agent chat interfaces. By decoupling the interface from the backend logic, mcp-ui allows for dynamic, context-aware educational experiences that adapt to the learner's progress.  
The visual identity of the platform—centered on the hero Cúchulainn and intricate Celtic knotwork—requires a sophisticated generative AI pipeline. This document provides a comparative technical analysis of **Bria’s Fibo**, **ComfyUI**, and **InvokeAI**, recommending specific workflows to ensure topological authenticity in generated Celtic art through structured JSON prompting and ControlNet guidance.  
Finally, the report addresses the infrastructure requirements for a persistent, stateful world. Through a detailed comparison of **SpacetimeDB** and **Convex**, and referencing the architecture of the MMORPG *BitCraft Online*, we demonstrate why a "database-as-server" model is essential for maintaining the low-latency synchronization required for multiplayer curriculum traversal and team-based mechanics. This synthesis of protocols, AI, and database theory offers a blueprint for a sovereign educational territory where knowledge is the only currency of value.

## ---

**1\. The Agentic Economy: x402 Protocol and the Celtic Utility Token**

The integration of a custom currency into an educational ecosystem requires a rigorous distinction between financial speculation and technical utility. In this architecture, the Celtic currency functions not as a tradable asset for profit, but as a measurement of "energy," "access," and "reputation"—a digital manifestation of the ancient Irish concept of *enech* (honor price). The **x402 protocol** serves as the technological rail that allows this value to flow seamlessly between students, content modules, and autonomous agents.

### **1.1 The "Original Sin" of the Web and the x402 Renaissance**

The development of the World Wide Web was marked by a critical omission: the lack of a native payment layer. While HTTP defined status codes for success (200), redirection (300), and client errors (400), the code 402 Payment Required was reserved for future use but never standardized.1 This "original sin" forced the internet into business models predicated on advertising and data surveillance, or siloed subscription walls that fragment information access.2  
The **x402 protocol** addresses this historical gap by creating a universal standard for machine-to-machine (M2M) and agent-to-agent payments. In the context of an educational game, x402 allows for granular, usage-based interaction models that are impossible with traditional payment gateways. Instead of a student buying a monthly subscription, their autonomous agent negotiates access to specific "Knowledge Nodes" (curriculum modules) in real-time, paying micro-amounts of the Celtic utility token based on the computational resources consumed or the prestige of the content.1

#### **1.1.1 The Technical Anatomy of the x402 Handshake**

The x402 protocol operates through a standardized request-response cycle that integrates payment directly into the HTTP transport layer. This mechanism is particularly advantageous for decentralized applications (dApps) where state is maintained on a blockchain but interaction happens over the web.  
1\. Resource Discovery and Request:  
The interaction begins when a student's agent (the client) requests a protected resource. For example, the student attempts to enter the "Forge of Algorithms," a gamified module for learning sorting algorithms. The agent sends a standard HTTP GET request to the resource URI (e.g., https://api.celtic-world.edu/modules/algorithms/forge).1  
2\. The 402 Challenge:  
The server, recognizing that the resource is gated, intercepts the request. Instead of returning a 403 Forbidden, it responds with a 402 Payment Required status code. Crucially, the response includes a PAYMENT-REQUIRED header or body containing a base64-encoded JSON object. This object details the payment terms:

* **Amount:** e.g., "5 KN" (Knowledge Knots, the Celtic utility token).  
* **Beneficiary:** The address of the content creator or the DAO treasury.  
* **Network:** The CAIP-2 identifier for the blockchain network (e.g., eip155:8453 for Base).6  
* **Expiration:** A timestamp after which the quote is invalid.

3\. Agentic Authorization (EIP-712 and EIP-3009):  
The agent parses this challenge. Because the system utilizes EIP-712 (Typed Data Signing), the agent can construct a structured, human-readable message for the user to sign, or sign it autonomously if pre-authorized.8  
Crucially, the x402 ecosystem supports EIP-3009 (Transfer with Authorization).6 This standard allows a user to sign a message authorizing a transfer of tokens without broadcasting a transaction themselves. This is vital for the "non-financial" feel of the game: the student does not need to hold ETH for gas. They simply sign a cryptographic intent: "I authorize the transfer of 5 Knowledge Knots to the Forge."  
4\. Header Injection and Retry:  
The agent attaches the signed authorization to a new header, typically X-PAYMENT or PAYMENT-SIGNATURE, and retries the original request.1 This keeps the payment logic coupled tightly with the resource request, maintaining statelessness.  
5\. Verification and Facilitator Settlement:  
The server receives the request with the signature. Instead of running a full blockchain node to verify the transaction (which would be resource-intensive), the server forwards the payload to a Facilitator service. The Facilitator is a specialized infrastructure component that:

* Cryptographically verifies the signature against the user's public address.  
* Checks for replay attacks (using nonces).  
* Submits the transaction to the blockchain, paying the gas fees (acting as a Paymaster).1  
* Returns a transaction hash or settlement confirmation to the server.

6\. Resource Delivery:  
Upon receiving confirmation from the Facilitator, the server returns 200 OK and the educational content.

### **1.2 The Celtic Utility Token: Design and Semantics**

The currency in this ecosystem—let's designate it **"Tuath"** (representing the tribe/people)—functions as a utility token rather than a speculative asset. Its design must discourage hoarding and incentivize participation, aligning with the "Learn-to-Earn" philosophy where earnings are proof of competence.12

#### **1.2.1 Technical Standards for Utility**

To function within the x402 framework and the proposed "gasless" user experience, the Tuath token must adhere to specific ERC standards on an EVM-compatible chain (like Base or Arbitrum).

* **ERC-20:** The base standard for fungibility.  
* **EIP-2612 (Permit):** This extension allows for approval via signatures. It enables the "meta-transaction" flow where the Facilitator spends the tokens on the user's behalf after verifying the signature. This removes the friction of the two-step Approve \-\> TransferFrom pattern that plagues standard DeFi UX.9  
* **EIP-3009:** As mentioned, this adds further flexibility for transfer authorizations, specifically designed to separate the signing of a transfer from its execution, enabling x402's "payment-in-header" mechanism.8

#### **1.2.2 Economic Mechanics: Sinks and Faucets**

To prevent the token from becoming a financial instrument, the economy must be circular and closed-loop regarding external fiat value.

* **Faucets (Minting):** Tokens are minted *only* through educational verification. When a student completes a "Pokémon Go" style traversal node and passes the associated mcp-ui quiz, the SpacetimeDB backend triggers a minting function. The amount minted corresponds to the difficulty of the module.  
* **Sinks (Burning):** Tokens are required to access advanced features.  
  * **Asset Generation:** Minting a custom "Cúchulainn" avatar requires a significant amount of Tuath. This burns the tokens, removing them from circulation and representing the "energy" expended to acquire the asset.14  
  * **Reputation Staking:** To form a team or "Clan," students must stake Tuath. This stake is slashed if the team engages in academic dishonesty or toxic behavior, introducing a mechanism for social coordination and governance.16

### **1.3 Facilitator Infrastructure: Sovereignty vs. Convenience**

The **Facilitator** is the bridge between the HTTP web and the blockchain. While commercial providers like Coinbase Developer Platform (CDP) offer hosted facilitators 17, a non-profit educational project should prioritize sovereignty and censorship resistance.  
Self-Hosted Architecture:  
Using the open-source x402-rs (Rust implementation) or x402-ao-facilitator, the project can deploy its own facilitator.11

* **Docker Deployment:** The facilitator runs as a containerized service alongside the game server. It requires configuration with a private key (for the gas payer wallet) and an RPC URL for the chosen blockchain (e.g., Base Sepolia for testing).11  
* **Custom Token Allow-listing:** A self-hosted facilitator allows the project to explicitly support the custom Tuath token. Commercial facilitators typically default to USDC. By configuring the facilitator to accept Tuath, the project ensures that the educational currency is the primary medium of exchange.8

## ---

**2\. Gamified Learning Interfaces: The Role of MCP and mcp-ui**

The user interface (UX) for agentic interactions has traditionally been limited to text streams. However, for a gamified educational environment involving map traversal and quizzes, a purely textual interface is insufficient. The **Model Context Protocol (MCP)** and its UI extension, **mcp-ui**, provide the solution by standardizing how agents discover tools and render interactive components.

### **2.1 The Model Context Protocol (MCP) Landscape**

MCP functions as a "USB-C for AI applications," standardizing the connection between AI agents (Hosts) and external data sources or tools (Servers).5  
In the proposed architecture:

* **MCP Server:** The educational game backend (built on SpacetimeDB) acts as the MCP server. It exposes "tools" such as get\_current\_location, start\_quiz, and mint\_asset.  
* **MCP Client:** The student's frontend interface (a web app or chat window) acts as the MCP client/host.

### **2.2 mcp-ui: Embedding Interactive Pedagogy**

**mcp-ui** extends the core MCP specification to allow servers to return rich, interactive user interface components instead of just text or JSON data.22 This capability is transformative for educational assessment.

#### **2.2.1 Mechanics of UI Resources**

When an agent invokes a tool, the MCP server can return a **UIResource**. This object instructs the client on what to render. mcp-ui supports three primary resource types, each serving a distinct function in the gamified environment 22:

1. **Inline HTML (text/html):**  
   * *Use Case:* Simple, ephemeral widgets like a single multiple-choice question (MCQ) or a "Sign Transaction" button for x402 payments.  
   * *Implementation:* The server returns a string of HTML/CSS/JS. The client renders this within a sandboxed iframe for security. This allows for immediate, lightweight interactions without network overhead for external assets.23  
2. **External URLs (text/uri-list):**  
   * *Use Case:* Complex, persistent views like the "Pokémon Go" style world map or a 3D inventory viewer.  
   * *Implementation:* The server returns a URL (e.g., https://game.celtic-world.edu/map/zone/ulster). The client embeds this in an iframe. This allows the game to leverage full WebGL capabilities (using libraries like React Three Fiber) while remaining embedded in the agent's context.22  
3. **Remote DOM (application/vnd.mcp-ui.remote-dom):**  
   * *Use Case:* Native-feeling components that need to match the host application's styling perfectly (e.g., a standardized "Quest Log" or "Wallet Balance").  
   * *Implementation:* The server sends a JSON description of the DOM structure and event handlers. The client renders this using its own native component library. This is the most secure method as it prevents arbitrary script execution.26

#### **2.2.2 The Gamified MCQ Workflow with mcp-ui**

The integration of MCQs into the agentic flow demonstrates the power of mcp-ui:

1. **Trigger:** A student's avatar arrives at the "Dolmen of Derivatives" on the map. The student asks their agent, "What challenge lies here?"  
2. **Tool Execution:** The agent calls the get\_node\_challenge tool on the MCP server.  
3. **Resource Generation:** The server retrieves a calculus problem from the database. It constructs a UIResource (Inline HTML) containing the problem text, LaTeX-rendered equations, and interactive radio buttons for answers. The visual style uses CSS classes defined by the game's Celtic theme (e.g., class="celtic-border").  
4. **Rendering & Interaction:** The client renders the quiz. The student selects an answer and clicks "Submit."  
5. **Bi-directional Communication:** The UI component uses the postMessage API (standardized by MCP-UI) to send the selected answer back to the agent host. This is a crucial security feature; the iframe cannot directly access the agent's memory or wallet, but communicates intent via a structured protocol.27  
6. **Resolution:** The agent receives the message {"type": "tool\_call", "name": "submit\_answer", "args": {"answer\_id": "B"}}. It forwards this to the server. If correct, the server awards Tuath tokens and the agent displays a "Success" UI component.

## ---

**3\. Generative AI for Educational Assets: Authenticity and Automation**

A core gamification element is the acquisition of unique digital assets—NFTs representing characters (like Cúchulainn) or artifacts (Spears, Shields). To maintain the educational integrity of the "Celtic" theme, these assets must be culturally authentic. Standard AI models often fail to replicate the strict topological rules of Celtic knotwork (where lines must weave over and under continuously without breaking). We analyze three pipelines for this purpose: **Bria Fibo**, **ComfyUI**, and **InvokeAI**.

### **3.1 Bria Fibo: The JSON-Native Specialist**

**Bria Fibo** is uniquely suited for agentic workflows due to its **JSON-native architecture**.29 Unlike standard diffusion models that interpret natural language prompts probabilistically (often leading to "hallucinations" or inconsistencies), Fibo is trained to interpret structured JSON schemas.

#### **3.1.1 Deterministic Asset Generation**

In an RPG-style game, assets have specific attributes (Level, Class, Equipment). Translating these into natural language prompts is imprecise. Fibo accepts a JSON payload, allowing the game logic to map data structures directly to visual output:

JSON

{  
  "subject": "Cúchulainn",  
  "attributes": {  
    "weapon": "Gáe Bulg",  
    "clothing": "Level 5 Tunic",  
    "mood": "Battle Frenzy"  
  },  
  "style": {  
    "art\_period": "La Tène",  
    "medium": "Oil Painting",  
    "complexity": "High"  
  }  
}

This structured approach ensures that when a student upgrades their avatar from Level 1 to Level 5, the visual output changes predictably (e.g., the tunic becomes more ornate) while preserving the character's identity.29

#### **3.1.2 Solving the "Knotwork Problem" with "Inspire" Mode**

Authentic Celtic art requires geometric precision. Fibo's **"Inspire" mode** allows the system to feed a reference image—such as a vector-perfect black-and-white knot pattern—into the generation process. Fibo uses this image as a structural "skeleton" while applying the requested texture and style (e.g., "carved gold"). This ensures the generated knotwork maintains topological consistency, avoiding the "impossible geometry" errors common in standard models.29

### **3.2 ComfyUI: The Modular Node Graph**

**ComfyUI** offers a highly granular, node-based architecture for Stable Diffusion workflows.32 It is the preferred choice for complex, multi-stage generation pipelines that require heavy customization.

#### **3.2.1 ControlNet Integration for Topology**

For assets where geometric rigor is paramount (e.g., a shield with a specific family crest), ComfyUI's integration with **ControlNet** is indispensable.

* **The Workflow:** The game server stores a library of valid SVG knot patterns. When a student earns a "Shield of Logic," the server rasterizes the corresponding SVG and sends it to the ComfyUI API along with a text prompt.  
* **Canny/Depth ControlNet:** A ControlNet node (configured for Canny edge detection or Depth maps) forces the diffusion model to adhere strictly to the lines of the input image. This guarantees that the "over-under" weaving of the knot is preserved in the final rendered image.32  
* **Automation:** Libraries like comfy-catapult allow the SpacetimeDB backend to trigger these workflows programmatically, treating the image generator as a reliable function call.34

### **3.3 InvokeAI: The Unified API**

**InvokeAI** focuses on a unified graph architecture ("Invocations") and a professional developer experience. Its standout feature for this project is **Metadata Embedding**.35

* **Proof of Provenance:** InvokeAI can embed the generation metadata (the prompt, seed, and settings) directly into the image file header. In an educational context, this allows the NFT to carry its own "DNA." A student could drag their Cúchulainn image into a verifier tool, which reads the metadata to confirm it was generated legitimately by the game server and not forged.

### **3.4 Recommended Pipeline Strategy**

A hybrid approach optimizes for both character consistency and geometric accuracy:

1. **Character Assets (Avatars):** Use **Bria Fibo** via its API. Its ability to "Refine" images allows the avatar to evolve visually as the student learns, adding scars, items, or age without losing the character's likeness.29  
2. **Artifacts (Knots/Shields):** Use **ComfyUI** with ControlNet. This ensures that the cultural heritage of Celtic art is respected by strictly enforcing the geometry of the designs.33

## ---

**4\. Backend Infrastructure: The Case for SpacetimeDB**

Modern game development is shifting from the traditional "Client-Server-Database" triad to "Database-as-Backend" architectures. For a persistent, stateful world like the proposed "Celtic Knowledge Grid," we analyze **SpacetimeDB** and **Convex**, using the architecture of *BitCraft Online* as a reference.

### **4.1 SpacetimeDB: The "Database is the Server"**

SpacetimeDB is the engine powering *BitCraft Online*, a massively multiplayer sandbox game. Its defining architectural decision is to run the application logic *inside* the database process.36

#### **4.1.1 In-Memory Performance and Zero-Copy**

In traditional architectures, reading the state of a player (e.g., position, inventory) involves querying a database (Postgres/Redis), serializing the data, sending it to the game server, processing logic, and writing it back. This introduces latency.  
SpacetimeDB loads the entire active state into memory. Game logic (written in Rust or C\# and compiled to WebAssembly) runs directly against this memory. This eliminates the "serialization tax," allowing for extremely high throughput (millions of transactions per second) and low latency (\~100 microseconds).36 This is critical for the "Pokémon Go" traversal aspect, where the system must constantly query spatial indices to see if a student is near a "Knowledge Node" or another student.

#### **4.1.2 Reducers and Procedures: The x402 Bridge**

SpacetimeDB distinguishes between two types of logic modules, a distinction that is vital for integrating external protocols like x402.

* **Reducers:** These are pure, ACID-transactional functions that update the database state. They must be deterministic and cannot have side effects (i.e., they cannot make external HTTP calls). For example, move\_player(x, y) is a reducer.38  
* **Procedures:** Introduced in version 1.10, Procedures allow for side effects, including outbound HTTP requests.39 **This is the architectural key to x402 integration.**  
  * *Workflow:* When a student wants to pay for a course, the client calls a Procedure initiate\_payment().  
  * *External Call:* The Procedure makes an HTTP POST request to the self-hosted x402 Facilitator to generate the payment challenge.  
  * *State Update:* The Procedure returns the challenge to the client. Once the client signs and the Facilitator confirms settlement, the Facilitator calls a callback webhook or the client invokes a Reducer with the proof, updating the game state (unlocking the course).

#### **4.1.3 Single-Shard Persistence**

Like *BitCraft*, the educational world should be a single, persistent shard. SpacetimeDB manages this natively. Every change—a student planting a "Tree of Knowledge," a team building a "Fortress of Physics"—is a permanent row in the database, visible to all other students in real-time via subscription queries.37

### **4.2 Convex: The Reactive Serverless Alternative**

Convex positions itself as a "reactive backend as a service." It combines a document-oriented database with a serverless function environment.

* **Reactivity:** Convex excels at pushing state updates to clients. If a record changes, all subscribed clients are updated automatically. This is excellent for chat apps or turn-based games.41  
* **Statelessness:** Unlike SpacetimeDB's persistent game loop, Convex functions are ephemeral. While efficient for sporadic updates, this model can become expensive and complex for a real-time world where entities (agents, NPCs) require constant simulation loops.41  
* **Cost Structure:** Convex typically charges per function invocation. In a game where every step on the map might trigger a check, SpacetimeDB's model (often based on reserved capacity or "energy") is more predictable and scalable for high-frequency interactions.

### **4.3 Comparison Table**

| Feature | SpacetimeDB | Convex |
| :---- | :---- | :---- |
| **Paradigm** | Database *is* the Server (Stateful) | Serverless Functions \+ DB (Reactive) |
| **Logic Location** | In-memory (WASM modules) | Ephemeral Cloud Functions |
| **Latency** | Ultra-low (Zero-copy access) | Low (Network overhead dependent) |
| **HTTP Outbound** | Supported via **Procedures** 39 | Supported via Actions |
| **Best For** | Real-time MMOs, Simulation | Chat, Leaderboards, Async Apps |
| **BitCraft Ref** | Used for main game loop & world state | Not used (Architecturally distinct) |

**Conclusion:** For a "Pokémon Go" style traversal game with real-time multiplayer interactions, **SpacetimeDB** provides the necessary performance and architectural coherence.

## ---

**5\. Comparative Analysis of Open-Source Web3 Learning Projects**

To align the "Celtic Knowledge Grid" with the ethos of the decentralized web, we examine three pioneering projects: **Kernel**, **Open Campus**, and **BuidlGuidl**. These serve as benchmarks for community governance, tokenomics, and gamification.

### **5.1 Kernel: The Community of Inquiry**

**Kernel** represents the philosophical "North Star" for non-profit Web3 education.

* **Model:** It rejects the "bootcamp" model in favor of a "peer-to-peer lifelong network." The focus is on "transformation, not information".42  
* **Structure:** The curriculum ("The Kernel Book") is open-source. Learning happens in 8-week cohorts ("Blocks").  
* **Relevance:** The Celtic project should adopt Kernel's emphasis on human connection. The "Tuath" token should not just be earned from bots but also gifted between peers. If Student A helps Student B solve a physics problem, Student B should be able to "tip" Student A in Tuath. This transforms the currency into a metric of **social trust** and altruism, mirroring the gifting culture of ancient Celtic societies.42

### **5.2 Open Campus: The Protocol for Ownership**

**Open Campus** (associated with Animoca Brands and TinyTap) focuses on the "financialization" of education infrastructure (EduFi).

* **Publisher NFTs:** This mechanism allows teachers to tokenize their courses. Holders of the NFT ("Co-publishers") promote the content and earn a share of the revenue it generates.44  
* **Relevance:** While our project is "utility-based," the concept of **Publisher NFTs** is powerful for sustainability. Student teams could create "Study Guides" or "Map Annotations" (e.g., "Safe path through the Logic Forest"). By minting these as NFTs, they gain a stake in the ecosystem. If other students find these guides helpful (verified by upvotes/usage), the creators earn Tuath tokens. This incentivizes the creation of high-quality Open Educational Resources (OER).44

### **5.3 BuidlGuidl: The Gamification of Mastery**

**BuidlGuidl**, led by Austin Griffith, is the gold standard for gamified technical learning (e.g., "Speed Run Ethereum").

* **Dynamic NFTs:** BuidlGuidl uses "Loogies"—SVG-based NFTs that change appearance based on on-chain state and interactions.  
* **Proof of Work:** Access to the "Guidl" is gated by completing technical challenges (shipping a dApp).  
* **Relevance:** The "Cúchulainn" avatar must be a **Dynamic NFT**. It should start as the child "Sétanta." As the student passes x402-gated checkpoints (verified via SpacetimeDB), the smart contract updates the NFT's metadata (e.g., level: warrior). This state change triggers the Bria Fibo pipeline to visually evolve the avatar—adding the "warp spasm" effect or the Gáe Bulg spear. This provides a visible, verifiable badge of mastery.47

## ---

**6\. Synthesis: Technical Implementation Strategy**

This section synthesizes the analysis into a concrete build plan for the "Celtic Knowledge Grid."

### **Phase 1: The Sovereign Infrastructure**

* **Backend:** Deploy a self-hosted **SpacetimeDB** instance. Define the schema in Rust: Student (Identity), Position (Spatial Index), Wallet (Tuath Balance), and Asset (NFT Metadata).  
* **Payment:** Deploy a **Dockerized x402-rs Facilitator**. Configure it to listen to the Base Sepolia testnet and whitelist the custom Tuath ERC-20 contract.19

### **Phase 2: The Agentic Loop**

* **Client:** Build a React Native app with @mcp-ui/client and a map library (react-map-gl).  
* **Agent Logic:** Implement SpacetimeDB Procedures for request\_payment.  
  * *Scenario:* A student wants to unlock the "Book of Kells" module.  
  * *Action:* Client calls unlock\_module().  
  * *Procedure:* SpacetimeDB calls the x402 Facilitator, gets the signature payload, and returns a 402 with the payload to the client.  
  * *Signing:* The agent presents the mcp-ui "Sign Transaction" widget.  
  * *Settlement:* The signature is sent to the Facilitator. Upon success, SpacetimeDB runs the grant\_access Reducer.

### **Phase 3: The Asset Factory**

* **Pipeline:** Set up a secure API gateway that wraps **Bria Fibo**.  
* **Trigger:** When a grant\_access Reducer completes a milestone, it emits an event.  
* **Generation:** A listening service constructs the JSON prompt: { "subject": "Cúchulainn", "action": "holding a scroll", "style": "Book of Kells" }. It calls Fibo, mints the result to IPFS, and updates the student's inventory in SpacetimeDB.

### **Phase 4: Social Dynamics**

* **Team Bonding:** Use SpacetimeDB's relational tables to link Student identities into Team structs.  
* **The "Help" Mechanic:** Implement an MCP tool request\_help. When invoked, it queries SpacetimeDB for nearby students. It sends a notification (via MCP) to their agents. If a peer accepts and successfully tutors the requester (verified by the requester passing a subsequent quiz), the system transfers Tuath tokens from the requester (or the DAO treasury) to the tutor, fostering the "Kernel" spirit of peer learning.

## **Conclusion**

The "Celtic Knowledge Grid" represents a convergence of the most advanced protocols in Web3 and AI. By leveraging **x402** for frictionless, agentic value transfer, **mcp-ui** for embedded interactive pedagogy, and **SpacetimeDB** for a persistent, shared reality, this architecture creates an educational environment that is arguably "alive." It is a system where reputation is verifiable, assets are culturally and topologically authentic, and the economy is designed to serve the learner's growth rather than the speculator's wallet.

#### **Works cited**

1. Building agentic and programmatic payments with x402 and Privy, accessed on December 15, 2025, [https://privy.io/blog/building-agentic-and-programmatic-payments-with-x402-and-privy](https://privy.io/blog/building-agentic-and-programmatic-payments-with-x402-and-privy)  
2. x402: An AI-Native Payment Protocol for the Web | by Jung-Hua Liu | Oct, 2025 | Medium, accessed on December 15, 2025, [https://medium.com/@gwrx2005/x402-an-ai-native-payment-protocol-for-the-web-419358450936](https://medium.com/@gwrx2005/x402-an-ai-native-payment-protocol-for-the-web-419358450936)  
3. What is x402? \- Ledger, accessed on December 15, 2025, [https://www.ledger.com/academy/topics/economics-and-regulation/what-is-x402](https://www.ledger.com/academy/topics/economics-and-regulation/what-is-x402)  
4. What is x402 Protocol: The HTTP-Based Payment Standard for Onchain Commerce, accessed on December 15, 2025, [https://blog.thirdweb.com/what-is-x402-protocol-the-http-based-payment-standard-for-onchain-commerce/](https://blog.thirdweb.com/what-is-x402-protocol-the-http-based-payment-standard-for-onchain-commerce/)  
5. Autonomous API & MCP Server Payments with x402 | Zuplo Blog, accessed on December 15, 2025, [https://zuplo.com/blog/mcp-api-payments-with-x402](https://zuplo.com/blog/mcp-api-payments-with-x402)  
6. Network & Token Support | x402 \- GitBook, accessed on December 15, 2025, [https://x402.gitbook.io/x402/core-concepts/network-and-token-support](https://x402.gitbook.io/x402/core-concepts/network-and-token-support)  
7. FAQ \- Coinbase Developer Documentation, accessed on December 15, 2025, [https://docs.cdp.coinbase.com/x402/support/faq](https://docs.cdp.coinbase.com/x402/support/faq)  
8. Network Support \- Coinbase Developer Documentation, accessed on December 15, 2025, [https://docs.cdp.coinbase.com/x402/network-support](https://docs.cdp.coinbase.com/x402/network-support)  
9. Add ERC20-Permit and Permit2 Support by AmazingAng · Pull Request \#485 · coinbase/x402 \- GitHub, accessed on December 15, 2025, [https://github.com/coinbase/x402/pull/485](https://github.com/coinbase/x402/pull/485)  
10. coinbase/x402: A payments protocol for the internet. Built on HTTP. \- GitHub, accessed on December 15, 2025, [https://github.com/coinbase/x402](https://github.com/coinbase/x402)  
11. loadnetwork/x402-ao-facilitator: x402 payments in Rust: verify, settle, and monitor payments over HTTP 402 flows | supports ao tokens \- GitHub, accessed on December 15, 2025, [https://github.com/loadnetwork/x402-ao-facilitator](https://github.com/loadnetwork/x402-ao-facilitator)  
12. Learn To Earn A Beginners The Basics Of Investing And Business Peter Lynch, accessed on December 15, 2025, [https://recruit.foreignaffairs.gov.fj/fetch.php/E0AG6B/312772/LearnToEarnABeginnersTheBasicsOfInvestingAndBusinessPeterLynch.pdf](https://recruit.foreignaffairs.gov.fj/fetch.php/E0AG6B/312772/LearnToEarnABeginnersTheBasicsOfInvestingAndBusinessPeterLynch.pdf)  
13. How to Make Passive Income With Crypto \- BitDegree, accessed on December 15, 2025, [https://www.bitdegree.org/crypto/tutorials/how-to-make-passive-income-with-crypto](https://www.bitdegree.org/crypto/tutorials/how-to-make-passive-income-with-crypto)  
14. Google Agentic Payments Protocol \+ x402: Agents Can Now Actually Pay Each Other, accessed on December 15, 2025, [https://www.coinbase.com/developer-platform/discover/launches/google\_x402](https://www.coinbase.com/developer-platform/discover/launches/google_x402)  
15. Building Autonomous Payment Agents with x402 \- Base Documentation, accessed on December 15, 2025, [https://docs.base.org/base-app/agents/x402-agents](https://docs.base.org/base-app/agents/x402-agents)  
16. Exploring the x402 Protocol for Internet-Native Payments \- Permit.io, accessed on December 15, 2025, [https://www.permit.io/blog/exploring-the-x402-protocol-for-internet-native-payments](https://www.permit.io/blog/exploring-the-x402-protocol-for-internet-native-payments)  
17. Welcome to x402 \- Coinbase Developer Documentation, accessed on December 15, 2025, [https://docs.cdp.coinbase.com/x402/welcome](https://docs.cdp.coinbase.com/x402/welcome)  
18. Facilitator \- Coinbase Developer Documentation, accessed on December 15, 2025, [https://docs.cdp.coinbase.com/x402/core-concepts/facilitator](https://docs.cdp.coinbase.com/x402/core-concepts/facilitator)  
19. x402-rs \- Avalanche Builder Hub \- Avax.network, accessed on December 15, 2025, [https://build.avax.network/integrations/x402-rs](https://build.avax.network/integrations/x402-rs)  
20. accessed on December 15, 2025, [https://www.vellum.ai/blog/mcp-ui-and-the-future-of-agentic-commerce\#:\~:text=Before%20diving%20into%20MCP%20UI,use%20services%20without%20custom%20integrations.](https://www.vellum.ai/blog/mcp-ui-and-the-future-of-agentic-commerce#:~:text=Before%20diving%20into%20MCP%20UI,use%20services%20without%20custom%20integrations.)  
21. Shopify and the Model Context Protocol (MCP) in E-Commerce \- FRANKI T, accessed on December 15, 2025, [https://www.francescatabor.com/articles/2025/8/14/shopify-and-the-model-context-protocol-mcp-in-e-commerce](https://www.francescatabor.com/articles/2025/8/14/shopify-and-the-model-context-protocol-mcp-in-e-commerce)  
22. MCP UI & The Future of Agentic Commerce \- Vellum AI, accessed on December 15, 2025, [https://www.vellum.ai/blog/mcp-ui-and-the-future-of-agentic-commerce](https://www.vellum.ai/blog/mcp-ui-and-the-future-of-agentic-commerce)  
23. MCP-UI: A Technical Overview of Interactive Agent Interfaces \- WorkOS, accessed on December 15, 2025, [https://workos.com/blog/mcp-ui-a-technical-deep-dive-into-interactive-agent-interfaces](https://workos.com/blog/mcp-ui-a-technical-deep-dive-into-interactive-agent-interfaces)  
24. MCP UI: Breaking the text wall with interactive components (2025) \- Shopify Engineering, accessed on December 15, 2025, [https://shopify.engineering/mcp-ui-breaking-the-text-wall](https://shopify.engineering/mcp-ui-breaking-the-text-wall)  
25. MCP-UI Just Gave MCP a Frontend \- Medium, accessed on December 15, 2025, [https://medium.com/@kenzic/mcp-ui-just-gave-mcp-a-frontend-aea0ebc02253](https://medium.com/@kenzic/mcp-ui-just-gave-mcp-a-frontend-aea0ebc02253)  
26. MCP-UI-Org/mcp-ui: UI over MCP. Create next-gen UI experiences with the protocol and SDK\! \- GitHub, accessed on December 15, 2025, [https://github.com/MCP-UI-Org/mcp-ui](https://github.com/MCP-UI-Org/mcp-ui)  
27. MCP Apps: Bringing Interactive UIs to AI Conversations \- fka.dev, accessed on December 15, 2025, [https://blog.fka.dev/blog/2025-11-22-mcp-apps-101-bringing-interactive-uis-to-ai-conversations/](https://blog.fka.dev/blog/2025-11-22-mcp-apps-101-bringing-interactive-uis-to-ai-conversations/)  
28. SEP-1865: MCP Apps \- Interactive User Interfaces for MCP by idosal · Pull Request \#1865 \- GitHub, accessed on December 15, 2025, [https://github.com/modelcontextprotocol/modelcontextprotocol/pull/1865](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/1865)  
29. briaai/FIBO \- Hugging Face, accessed on December 15, 2025, [https://huggingface.co/briaai/FIBO](https://huggingface.co/briaai/FIBO)  
30. FIBO Open-Source T2I Model Built for Pro-Level Creative Control \- Bria.ai, accessed on December 15, 2025, [https://bria.ai/fibo](https://bria.ai/fibo)  
31. Identify if has celtic knots using AI \- Nyckel, accessed on December 15, 2025, [https://www.nyckel.com/pretrained-classifiers/if-has-celtic-knots-identifier/](https://www.nyckel.com/pretrained-classifiers/if-has-celtic-knots-identifier/)  
32. How to Use ComfyUI API with Python: A Complete Guide | by Shawn Wong | Medium, accessed on December 15, 2025, [https://medium.com/@next.trail.tech/how-to-use-comfyui-api-with-python-a-complete-guide-f786da157d37](https://medium.com/@next.trail.tech/how-to-use-comfyui-api-with-python-a-complete-guide-f786da157d37)  
33. Celtic Artists strike back at Ai \- The HORNELL SUN, accessed on December 15, 2025, [https://hornellsun.com/2025/06/09/celtic-artists-strike-back-at-ai/](https://hornellsun.com/2025/06/09/celtic-artists-strike-back-at-ai/)  
34. realazthat/comfy-catapult: Programmatically schedule ComfyUI workflows via the ComfyUI API \- GitHub, accessed on December 15, 2025, [https://github.com/realazthat/comfy-catapult](https://github.com/realazthat/comfy-catapult)  
35. Invocation API \- Invoke, accessed on December 15, 2025, [https://invoke-ai.github.io/InvokeAI/nodes/invocation-api/](https://invoke-ai.github.io/InvokeAI/nodes/invocation-api/)  
36. SpacetimeDB, accessed on December 15, 2025, [https://spacetimedb.com/](https://spacetimedb.com/)  
37. SpacetimeDB and BitCraft \- Clockwork Labs, accessed on December 15, 2025, [https://clockwork-labs.medium.com/spacetimedb-and-bitcraft-bc957a7faf40](https://clockwork-labs.medium.com/spacetimedb-and-bitcraft-bc957a7faf40)  
38. reducer in spacetimedb \- Rust \- Docs.rs, accessed on December 15, 2025, [https://docs.rs/spacetimedb/latest/spacetimedb/attr.reducer.html](https://docs.rs/spacetimedb/latest/spacetimedb/attr.reducer.html)  
39. clockworklabs/SpacetimeDB v1.10.0 on GitHub \- NewReleases.io, accessed on December 15, 2025, [https://newreleases.io/project/github/clockworklabs/SpacetimeDB/release/v1.10.0](https://newreleases.io/project/github/clockworklabs/SpacetimeDB/release/v1.10.0)  
40. Procedures \- Overview | SpacetimeDB docs, accessed on December 15, 2025, [https://spacetimedb.com/docs/procedures](https://spacetimedb.com/docs/procedures)  
41. Tinkering With SpacetimeDB \- mikecann.blog, accessed on December 15, 2025, [https://mikecann.blog/posts/tinkering-with-spacetime-db](https://mikecann.blog/posts/tinkering-with-spacetime-db)  
42. kernel-community/kernel: A knowledge repository for Web 3\. Learn how to think about and build a better web here. \- GitHub, accessed on December 15, 2025, [https://github.com/kernel-community/kernel](https://github.com/kernel-community/kernel)  
43. Kernel Community, accessed on December 15, 2025, [https://www.kernel.community/](https://www.kernel.community/)  
44. Open Campus price today, EDU to USD live price, marketcap and chart | CoinMarketCap, accessed on December 15, 2025, [https://coinmarketcap.com/currencies/open-campus/](https://coinmarketcap.com/currencies/open-campus/)  
45. Open Campus (EDU) Live Price, Open Campus Team and Founder | TokenInsight, accessed on December 15, 2025, [https://tokeninsight.com/en/coins/open-campus/team](https://tokeninsight.com/en/coins/open-campus/team)  
46. Animoca Brands acquires TinyTap, the leading platform for user generated educational content | NFT CULTURE, accessed on December 15, 2025, [https://www.nftculture.com/nft-news/animoca-brands-acquires-tinytap-the-leading-platform-for-user-generated-educational-content/](https://www.nftculture.com/nft-news/animoca-brands-acquires-tinytap-the-leading-platform-for-user-generated-educational-content/)  
47. Nairobi Mini Hack \- HackQuest, accessed on December 15, 2025, [https://www.hackquest.io/hackathons/Nairobi-Mini-Hack](https://www.hackquest.io/hackathons/Nairobi-Mini-Hack)  
48. eth.dev \- BuidlGuidl v3, accessed on December 15, 2025, [https://v3.buidlguidl.com/build/SWShhE7MXO6GoijdlQjh](https://v3.buidlguidl.com/build/SWShhE7MXO6GoijdlQjh)
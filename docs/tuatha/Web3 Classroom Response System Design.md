# **Architectural Blueprint for "Cianfhoghlaim": A Decentralized, Physical-Digital Educational Ecosystem**

## **1\. Introduction: The Convergence of Constructivism and Sovereign Technology**

The educational landscape is currently navigating a critical fracture between the pedagogical imperative for student-centred, active learning and the logistical constraints of traditional, high-stakes assessment environments. Research into the Irish post-primary mathematics classroom highlights a persistent reliance on "direct transmission" teaching methodologies, largely driven by examination pressures and a lack of infrastructure to support more investigative, constructivist approaches.1 Constructivism, which posits that learners actively construct knowledge through experience and reflection rather than passively receiving it, requires frequent, low-stakes feedback loops to be effective. However, the administrative burden of generating this feedback manually often forces educators back into traditionalist practices.  
The proposed "Cianfhoghlaim" ecosystem represents a radical synthesis of these pedagogical needs with the emerging capabilities of decentralized Web3 technologies, real-time distributed systems, and privacy-preserving Artificial Intelligence. By integrating a physical Classroom Response System (CRS)—modeled on the "Plickers" mechanic—with a Massively Multiplayer Online (MMO) game state managed by SpacetimeDB and a tokenized economy on the Solana blockchain, the project aims to gamify the acquisition of Celtic languages and cultural heritage.1 This report provides a comprehensive architectural analysis of this ecosystem, detailing the technical implementation of the physical-digital bridge via Kotlin Multiplatform (KMP), the real-time state synchronization via SpacetimeDB, and the "Pedagogical Oracle" pattern required to secure the "Learn-to-Earn" economy on the blockchain.

### **1.1 The Pedagogical Value of Tangible Interfaces**

The decision to utilize a Plickers-like interface—where students answer questions by rotating physical cards encoded with fiducial markers—is not merely a logistical convenience but a profound pedagogical strategy. The "digital divide" remains a significant barrier in Educational Technology (EdTech), where reliance on 1:1 student devices can exacerbate socioeconomic inequalities.1 By shifting the hardware requirement entirely to the teacher's device, the system ensures inclusivity. Furthermore, the physical act of rotating a card to select an answer (A, B, C, or D) introduces a tactile element to the assessment process, anchoring abstract concepts in physical action, which can aid retention.  
From a sociotechnical perspective, this mechanics transforms the teacher's device into a powerful edge node. It captures high-fidelity analog data (the visual state of the classroom), digitizes it through computer vision, and broadcasts it to the digital realm. This data stream does not merely record grades; it drives the "Anam" (Soul) economy of the game world, translating academic effort directly into digital agency.1 The immediacy of this feedback satisfies the constructivist requirement for "assessment for learning," allowing students to visualize their progress instantly through the evolution of their digital avatars.

### **1.2 The Shift to "Sovereign Education"**

Central to the Cianfhoghlaim proposal is the concept of "Sovereign AI" and a decentralized economy. Traditional Learning Management Systems (LMS) lock student data into proprietary silos, where it holds no value to the student beyond the institution. In contrast, the proposed architecture issues Verifiable Credentials (VCs) via the European Blockchain Services Infrastructure (EBSI) and rewards progress with "Tuath" utility tokens.1 This establishes a model of "Sovereign Education" where the learner owns their achievements, their data, and the value they generate.  
The technical realization of this vision requires a rigorous "Pedagogical Oracle." Because the blockchain is agnostic to the physical world, it requires a trusted source of truth to verify that learning has actually occurred. The teacher's device, running the KMP scanner, acts as this oracle. The integrity of the entire economic model relies on the accuracy, security, and real-time performance of this scanning interface and its synchronization with the backend state engine.

## **2\. The Physical-Digital Interface: Client-Side Computer Vision with Kotlin Multiplatform**

The foundational interaction of the Cianfhoghlaim ecosystem is the scanning of fiducial markers. To ensure a seamless user experience across the diverse hardware landscape of educational institutions, the scanning application must be built using Kotlin Multiplatform (KMP), enabling shared business logic across Android and iOS while leveraging platform-specific hardware acceleration.

### **2.1 The Mathematics of Fiducial Markers: ArUco vs. QR Codes**

A critical distinction must be made between standard QR codes and the fiducial markers required for this system. Standard QR codes are designed to be rotation-invariant; they contain three "finder patterns" that allow scanning algorithms to reorient the data payload regardless of how the code is held.2 However, the Plickers mechanic *relies* on rotation to convey information. A student holding the card with side 'A' up intends a different answer than if side 'B' were up.  
Therefore, the system must utilize **ArUco markers** (or a similar fiducial system like AprilTags). ArUco markers consist of a black border and an inner binary matrix (e.g., 4x4 or 6x6 bits). This structure enables two critical capabilities:

1. **High-Speed Detection:** The high-contrast black border facilitates rapid contour detection, allowing modern mobile devices to detect and decode dozens of markers in a single video frame.3  
2. **Pose Estimation:** Because the physical size of the marker is known, the computer vision algorithm can solve the "Perspective-n-Point" (PnP) problem. This calculates the marker's 3D pose relative to the camera, returning a rotation vector ($\\vec{r}$) and a translation vector ($\\vec{t}$).3

#### **2.1.1 The Orientation Algorithm**

To determine the student's answer, the system must calculate the rotation of the marker relative to the camera's vertical axis. Standard QR scanners abstract this detail away, making them unsuitable. Using the corner points returned by an ArUco detector (typically indexed $0$ to $3$ starting from the canonical top-left), the orientation logic is derived geometrically.  
Let the detected corners be $C\_0, C\_1, C\_2, C\_3$.  
The "Up" vector of the marker in image space can be approximated as $\\vec{V}\_{marker} \= \\frac{C\_0 \+ C\_1}{2} \- \\frac{C\_2 \+ C\_3}{2}$ (the vector from the bottom edge midpoint to the top edge midpoint).  
The "Up" vector of the camera frame is defined as $\\vec{V}\_{cam} \= (0, \-1)$ (assuming a standard Cartesian coordinate system where $y$ increases downwards).  
The angle $\\theta$ is calculated as the angle between $\\vec{V}\_{marker}$ and $\\vec{V}\_{cam}$. The answer is then bucketed:

* $\\theta \\in \[-45^\\circ, 45^\\circ\] \\rightarrow$ **Answer A**  
* $\\theta \\in \[45^\\circ, 135^\\circ\] \\rightarrow$ **Answer B** (assuming clockwise rotation corresponds to B)  
* $\\theta \\in \[135^\\circ, 225^\\circ\] \\rightarrow$ **Answer C**  
* $\\theta \\in \[225^\\circ, 315^\\circ\] \\rightarrow$ **Answer D**

This geometric analysis must happen locally on the client device (Edge Computing) to ensure the 60fps responsiveness required for a smooth User Interface (UI), preventing the "laggy" feel that disrupts classroom flow.

### **2.2 Implementing Computer Vision in Kotlin Multiplatform**

Integrating high-performance computer vision into KMP presents specific challenges, as KMP does not currently support direct C++ interoperability (the language of OpenCV) in the shared source set. A "Platform-Interface, Native-Implementation" architecture is required.

#### **2.2.1 The Infrastructure Layer**

The shared KMP module should define an interface MarkerScanner:

Kotlin

interface MarkerScanner {  
    fun scanFrame(frameData: ByteArray, width: Int, height: Int, rotation: Int): List\<DetectedMarker\>  
}

data class DetectedMarker(  
    val id: Int,  
    val corners: List\<Point\>,  
    val pose: Pose3D? \= null  
)

Android Implementation (JNI & CameraX):  
On Android, the implementation leverages the Java Native Interface (JNI) to bridge Kotlin and the OpenCV C++ library.

1. **CameraX:** The ImageAnalysis use case provides access to the camera buffer. It is crucial to handle the YUV\_420\_888 format efficiently, converting the Y plane (luminance) to a cv::Mat for detection without unnecessary memory copying.5  
2. **OpenCV Wrapper:** A custom C++ wrapper is necessary because the official OpenCV Android SDK is heavy. The **opencv-mobile** project is highly recommended; it provides a minimal build of OpenCV (stripping GUI components like highgui) optimized for binary size, which is critical for mobile app performance.6  
3. **JNI Bridge:** A JNI function Java\_com\_cianfhoghlaim\_cv\_NativeScanner\_detect accepts the byte array, passes it to cv::aruco::detectMarkers, and returns a serialized array of IDs and corner coordinates to Kotlin.

iOS Implementation (Objective-C++ & AVFoundation):  
On iOS, the bridge is facilitated by Objective-C++.

1. **AVFoundation:** The AVCaptureVideoDataOutput provides CMSampleBuffer objects.  
2. **Objective-C++ Wrapper:** Since Swift cannot call C++ directly, an Objective-C++ (.mm) wrapper class OpenCVWrapper is created. This class imports the OpenCV C++ headers and exposes an Objective-C API.7  
3. **C-Interop:** Kotlin/Native can interact seamlessly with Objective-C. The KMP module imports the OpenCVWrapper header via cinterop, allowing the shared Kotlin logic to invoke the scanner.8

#### **2.2.2 ML Kit vs. OpenCV Trade-off**

While Google's ML Kit offers a simpler API and is optimized for mobile hardware, its Barcode Scanning API primarily targets standard QR/Barcode decoding. Although it returns cornerPoints 9, it lacks the specialized dictionary generation (Hamming distance optimization) and pose estimation functions (estimatePoseSingleMarkers) of ArUco. For a simple 2D implementation, ML Kit is sufficient and reduces build complexity. However, for the "Augmented Reality" aspects hinted at in the user's research (e.g., projecting 3D content onto the cards), OpenCV is the superior choice due to its robust 3D pose estimation capabilities.3

### **2.3 The Feedback Loop: Visualizing the "Oracle"**

In keeping with Hattie's "Visible Learning," the UI must provide immediate visual feedback. The KMP Compose Multiplatform UI layer overlays the camera preview with augmented information. When a marker is detected:

1. A bounding box is drawn around the card (Green for correct, Red for incorrect, or Neutral for "registered").  
2. The student's name (resolved from the local cache of SpacetimeDB data) floats above the card.  
3. The selected answer (A/B/C/D) is displayed for the teacher's verification.

This augmented reality view allows the teacher to "see" the cognitive state of the room in real-time, fulfilling the constructivist goal of immediate, formative feedback.1

## **3\. The Real-Time State Engine: SpacetimeDB**

The backend architecture is defined by the choice of **SpacetimeDB**, a "database-as-server" technology. This represents a paradigm shift from traditional n-tier architectures (Database \-\> Backend API \-\> WebSocket Server \-\> Client). In SpacetimeDB, the application logic lives *inside* the database as stored procedures called **Reducers**, and clients connect directly to the database via WebSockets to synchronize state.11

### **3.1 Schema Design for a Gamified Classroom**

The database schema must support high-frequency updates from the "Pedagogical Oracle" (the teacher's scanner) while maintaining the persistent state of the MMO economy. Using SpacetimeDB's Rust SDK, the schema is defined structurally.  
Table: StudentIdentity  
This table links the physical world to the digital and blockchain realms.

Rust

\#\[spacetimedb::table(name \= student\_identity, public)\]  
pub struct StudentIdentity {  
    \#\[primary\_key\]  
    pub identity: Identity,      // SpacetimeDB internal identity  
    pub marker\_id: u32,          // The physical Plickers card ID (1-63)  
    pub class\_id: u32,           // Foreign key to the Class table  
    pub wallet\_pubkey: String,   // Solana Wallet Address (for the Tuath economy)  
    pub xp\_total: u64,           // Academic XP (off-chain)  
}

Table: ActivePoll  
This table manages the transient state of the current assessment.

Rust

\#\[spacetimedb::table(name \= active\_poll, public)\]  
pub struct ActivePoll {  
    \#\[primary\_key\]  
    pub poll\_id: u64,  
    pub question\_text: String,  
    pub correct\_option: String,  // "A", "B", "C", "D"  
    pub status: String,          // "Open", "Closed", "Grading"  
    pub started\_at: Timestamp,  
}

Table: PollResponse  
This table records the stream of answers from the "Oracle."

Rust

\#\[spacetimedb::table(name \= poll\_response, public)\]  
pub struct PollResponse {  
    \#\[primary\_key\]  
    \#\[auto\_inc\]  
    pub id: u64,  
    pub poll\_id: u64,  
    pub student\_marker\_id: u32,  
    pub selected\_option: String,  
    pub timestamp: Timestamp,  
}

### **3.2 Reducers: The Transactional Game Loop**

Reducers are the atomic units of logic. Because SpacetimeDB is single-threaded per module, reducers are serialized, ensuring ACID compliance without complex locking mechanisms.12  
Reducer: submit\_scan\_batch  
The teacher's client does not send a request for every single frame or every single detected marker. This would flood the network. Instead, the KMP client debounces detections and sends a batch update every 200-500ms containing the current state of all visible markers.

Rust

\#\[spacetimedb::reducer\]  
pub fn submit\_scan\_batch(ctx: \&ReducerContext, poll\_id: u64, scans: Vec\<(u32, String)\>) {  
    // scans is a list of (marker\_id, answer) tuples  
    let poll \= ctx.db.active\_poll().poll\_id().find(poll\_id).expect("Poll not active");  
    if poll.status\!= "Open" { return; }

    for (marker, answer) in scans {  
        // Upsert logic: Update the student's current answer if it changed  
        // This allows students to correct themselves before the poll closes  
    }  
}

Reducer: conclude\_poll  
When the teacher closes the question, this reducer runs the grading logic. It calculates XP gains, updates the StudentIdentity table, and triggers the "Learn-to-Earn" mechanisms. Importantly, this reducer acts as the bridge to the Web3 layer by emitting events that the external Oracle service listens for.12

### **3.3 The Wire Protocol: BSATN and Client Synchronization**

SpacetimeDB communicates using **BSATN** (Binary Spacetime Algebraic Type Notation), a custom binary serialization format designed for high performance and zero-copy deserialization.13

* **The Challenge:** Currently, SpacetimeDB officially supports SDKs for Rust, C\#, and TypeScript.14 There is no official Kotlin SDK.  
* **The Solution:** To implement the KMP client, the developer must implement a BSATN serializer/deserializer in Kotlin.  
  * **BSATN Structure:** BSATN is a little-endian binary format. SumTypes (enums) are encoded as a tag byte followed by the variant data. ProductTypes (structs) are encoded as the concatenation of their field encodings.13  
  * **WebSocket Protocol:** The client connects via WebSocket to /v1/database/{name}/subscribe. The server sends an initial SubscriptionUpdate containing the current table state, followed by incremental TransactionUpdate messages whenever a reducer modifies the data.15  
  * **Alternative:** If implementing a full binary protocol is too resource-intensive, the client can fall back to **SATS-JSON**, a JSON representation of the algebraic types supported by the HTTP API.16 However, for a real-time MMO experience with 30+ concurrent entity updates, the binary efficiency of BSATN is highly preferable to minimize latency.17

## **4\. The Economic Layer: Web3 Integration on Solana**

The "Cianfhoghlaim" project aims to transform academic effort into "Tuath" tokens—a utility currency representing *enech* (honor). The user has selected **Solana** for its high throughput and low transaction costs, which are essential for a system involving micro-transactions (e.g., earning small amounts of token for every correct answer).1

### **4.1 The "Pedagogical Oracle" Pattern**

A fundamental limitation of SpacetimeDB (and WASM sandboxes in general) is the inability to initiate arbitrary network requests (like HTTP calls to an RPC node) directly from a reducer.18 Furthermore, holding a hot wallet private key inside a shared database module poses security risks.  
To bridge the gap between the SpacetimeDB state and the Solana blockchain, we must implement the **"Pedagogical Oracle"** pattern (a variation of the Transactional Outbox pattern).

1. **State Transition:** When the conclude\_poll reducer runs and determines that Student A has earned 10 Tuath, it inserts a record into a PendingTx table.  
   Rust  
   \#\[spacetimedb::table(name \= pending\_tx, public)\]  
   pub struct PendingTx {  
       \#\[primary\_key\]  
       \#\[auto\_inc\]  
       pub id: u64,  
       pub student\_identity: Identity,  
       pub wallet\_address: String,  
       pub amount: u64,  
       pub status: String, // "Pending", "Processing", "Confirmed"  
   }

2. **The Oracle Service:** An external, trusted service (written in Rust or Node.js using the solana-web3.js or solana-client libraries) subscribes to the PendingTx table via WebSocket.19  
3. **Execution:** When the Oracle receives an insert event for PendingTx:  
   * It verifies the integrity of the request.  
   * It constructs a Solana transaction (e.g., an SPL Token transfer or mint instruction).  
   * It signs the transaction using the **Game Authority Keypair** (a secure hot wallet).  
   * It submits the transaction to the Solana cluster via RPC.  
4. **Confirmation:** Upon transaction finality, the Oracle calls a confirm\_tx reducer in SpacetimeDB to update the PendingTx status to "Confirmed" and notify the client UI.

### **4.2 The x402 Protocol: Agentic Payments**

The user's research proposes the **x402 protocol** for agentic payments.1 In this context, x402 serves as the mechanism for *spending* "Tuath" tokens to access premium content or fast-travel services (e.g., Manannán’s ship).  
**Implementation Flow:**

1. **Challenge:** The student's agent (client) requests access to a "Knowledge Node." The server responds with a 402 Payment Required header containing a payment challenge (amount, recipient, nonce).  
2. **Authorization:** The agent signs a message using the student's wallet (e.g., via a mobile wallet adapter or embedded wallet like Privy) authorizing the transfer of "Tuath" tokens.  
3. **Meta-Transaction:** To ensure a "gasless" experience for the student (who may not hold SOL), the signed authorization is sent to the **Facilitator** (the Oracle service).  
4. **Settlement:** The Facilitator wraps the student's signature into a transaction, pays the SOL gas fee, and submits it to the blockchain. This utilizes Solana's capability for fee-payer delegation.20

### **4.3 Verifiable Credentials (VCs) and EBSI**

For high-stakes assessments (e.g., end-of-term exams), simple tokens are insufficient. The system integrates with the **European Blockchain Services Infrastructure (EBSI)** to issue tamper-proof Verifiable Credentials.1

* **Mechanism:** When a student completes a "Sovereignty Quest" (a major curriculum milestone), the Oracle triggers the issuance of a W3C-compliant VC (JSON-LD format).  
* **Anchoring:** The *hash* of this credential is anchored on the Solana blockchain (or a dedicated identity sidechain) to prove its existence and timestamp without revealing the sensitive grade data publicly.1  
* **Storage:** The full credential is stored in the student's personal data vault (off-chain), giving them sovereignty over their academic record.

## **5\. Privacy-Preserving AI: Federated Learning**

The project emphasizes "Sovereign AI" to protect student data, particularly sensitive voice recordings used for pronunciation practice in Celtic languages.

### **5.1 The Syft-Flower Stack**

To comply with GDPR and protect minors, raw biometric data must never leave the student's device. The architecture utilizes a **Federated Learning (FL)** approach using the **Syft-Flower** stack.1

1. **Local Training:** The KMP mobile app integrates a lightweight ML runtime (e.g., TensorFlow Lite or ONNX Runtime). When a student practices a phrase ("Oral Exam" battle mode), the local model calculates the error (gradient) relative to the expected pronunciation.  
2. **Differential Privacy:** Before uploading these gradients, the **Syft** library applies Differential Privacy (DP) mechanisms, injecting statistical noise. This ensures that the server cannot reverse-engineer the original voice sample from the update.1  
3. **Aggregation:** The **Flower** server aggregates these noisy gradients from thousands of students to improve the global "Scoil" model, which is then redistributed to devices. This allows the system to learn diverse dialects (e.g., Donegal vs. Kerry Irish) without centralizing surveillance data.

## **6\. Implementation Roadmap and Recommendations**

### **6.1 Phase 1: The Core Scanner (KMP \+ SpacetimeDB)**

* **Goal:** Establish the physical-digital loop.  
* **Action:** Implement the ArUco scanner using opencv-mobile in KMP. Build the SpacetimeDB schema for Students, Polls, and Responses. Implement the submit\_scan\_batch reducer.  
* **Critical Task:** Develop a Kotlin implementation of the BSATN deserializer to enable high-performance networking.

### **6.2 Phase 2: The Economic Bridge (Solana Oracle)**

* **Goal:** Enable "Learn-to-Earn."  
* **Action:** Deploy the SPL Token "Tuath" on Solana Devnet. Build the Rust-based Oracle service to poll the PendingTx table and execute token mints/transfers. Implement the confirm\_tx feedback loop.

### **6.3 Phase 3: The Sovereign AI Layer**

* **Goal:** Privacy-preserving voice recognition.  
* **Action:** Integrate syft and flower clients into the Android/iOS application. Implement the "Oral Exam" game mode that triggers local training rounds.

### **6.4 Phase 4: Production and Scaling**

* **Goal:** Robustness and Security.  
* **Action:** Audit the Oracle service for security (key management is critical). Optimize SpacetimeDB indexes for high-frequency polling. Implement anti-cheating logic in the scanner (e.g., randomizing answer mappings per student).

## **7\. Conclusion**

"Cianfhoghlaim" represents a sophisticated synthesis of pedagogical theory and frontier technology. By leveraging the **Plickers** mechanic, it bypasses the hardware limitations of the traditional classroom, ensuring equity. By utilizing **SpacetimeDB**, it achieves the real-time responsiveness required for an engaging MMO experience. And by integrating **Solana** via a secure Oracle pattern, it transforms academic engagement into a sovereign economic asset.  
This architecture offers a robust, scalable path toward a "Learn-to-Earn" ecosystem that values privacy, community, and cultural heritage. The technical complexity—particularly in the custom KMP-OpenCV bridge and the BSATN networking layer—is significant, but the payoff is a uniquely resilient platform that truly empowers the learner. The resulting system does not merely digitize education; it re-engineers the incentives of learning itself.

| Component | Technology Choice | Rationale |
| :---- | :---- | :---- |
| **Client App** | Kotlin Multiplatform (KMP) | Shared business logic across iOS/Android; native performance. |
| **Marker Detection** | ArUco (via OpenCV) | Robust orientation detection; high-speed batch processing; pose estimation. |
| **Backend State** | SpacetimeDB | "Database-as-server" for low-latency MMO state; ACID compliance. |
| **Networking** | WebSockets \+ BSATN | Binary protocol for minimal overhead and high-frequency updates. |
| **Blockchain** | Solana | High throughput; low cost for micro-transactions; SPL Token standard. |
| **Integration** | Oracle Pattern | Secure bridge between deterministic DB logic and external blockchain. |
| **AI Privacy** | Federated Learning (Syft/Flower) | GDPR compliance; local training on sensitive voice/handwriting data. |

#### **Works cited**

1. Action Research Project \- Plickers.pdf  
2. Cards Overview \- Plickers, accessed December 16, 2025, [https://help.plickers.com/hc/en-us/articles/360009089113-Cards-Overview](https://help.plickers.com/hc/en-us/articles/360009089113-Cards-Overview)  
3. Detection of ArUco Markers \- OpenCV Documentation, accessed December 16, 2025, [https://docs.opencv.org/4.x/d5/dae/tutorial\_aruco\_detection.html](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)  
4. Improved Pose Estimation of Aruco Tags Using a Novel 3D Placement Strategy \- PMC, accessed December 16, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7506853/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7506853/)  
5. Compiling and Using OpenCV on Android from C++ (Without OpenCVManager) | sisik, accessed December 16, 2025, [https://sisik.eu/blog/android/ndk/opencv-without-java](https://sisik.eu/blog/android/ndk/opencv-without-java)  
6. nihui/opencv-mobile: The minimal opencv for Android, iOS, ARM Linux, Windows, Linux, MacOS, HarmonyOS, WebAssembly, watchOS, tvOS, visionOS \- GitHub, accessed December 16, 2025, [https://github.com/nihui/opencv-mobile](https://github.com/nihui/opencv-mobile)  
7. How to Call Native C++ Code from a Kotlin Multiplatform Project | by Abdullah Al Masud, accessed December 16, 2025, [https://medium.com/@dev.almasud/how-to-call-native-c-code-from-a-kotlin-multiplatform-project-a9d98e9b1700](https://medium.com/@dev.almasud/how-to-call-native-c-code-from-a-kotlin-multiplatform-project-a9d98e9b1700)  
8. iOS Specific Integration Challenges With Kotlin Multiplatform | by Eduardo Santos \- Medium, accessed December 16, 2025, [https://medium.com/@eduardofelipi/ios-specific-integration-challenges-with-kotlin-multiplatform-75c6fa7a932e](https://medium.com/@eduardofelipi/ios-specific-integration-challenges-with-kotlin-multiplatform-75c6fa7a932e)  
9. MLKitBarcodeScanning Framework Reference | ML Kit \- Google for Developers, accessed December 16, 2025, [https://developers.google.com/ml-kit/reference/swift/mlkitbarcodescanning/api/reference/Classes/Barcode](https://developers.google.com/ml-kit/reference/swift/mlkitbarcodescanning/api/reference/Classes/Barcode)  
10. Build a Real-Time ArUco Detection Plugin with OpenCV for Android & Unity 6 \- Medium, accessed December 16, 2025, [https://medium.com/@weifan\_83639/build-a-real-time-aruco-detection-plugin-with-opencv-for-android-unity-6-7eeb59e66f56](https://medium.com/@weifan_83639/build-a-real-time-aruco-detection-plugin-with-opencv-for-android-unity-6-7eeb59e66f56)  
11. SpacetimeDB, accessed December 16, 2025, [https://spacetimedb.com/](https://spacetimedb.com/)  
12. reducer in spacetimedb \- Rust \- Docs.rs, accessed December 16, 2025, [https://docs.rs/spacetimedb/latest/spacetimedb/attr.reducer.html](https://docs.rs/spacetimedb/latest/spacetimedb/attr.reducer.html)  
13. BSATN Data Format | SpacetimeDB docs, accessed December 16, 2025, [https://spacetimedb.com/docs/bsatn/](https://spacetimedb.com/docs/bsatn/)  
14. Rust Reference | SpacetimeDB docs, accessed December 16, 2025, [https://spacetimedb.com/docs/sdks/rust](https://spacetimedb.com/docs/sdks/rust)  
15. SpacetimeDB/crates/client-api-messages/src/websocket.rs at master \- GitHub, accessed December 16, 2025, [https://github.com/clockworklabs/SpacetimeDB/blob/master/crates/client-api-messages/src/websocket.rs](https://github.com/clockworklabs/SpacetimeDB/blob/master/crates/client-api-messages/src/websocket.rs)  
16. Subscription Reference | SpacetimeDB docs, accessed December 16, 2025, [https://spacetimedb.com/docs/subscriptions/](https://spacetimedb.com/docs/subscriptions/)  
17. TigerBeetle is a most interesting database | Hacker News, accessed December 16, 2025, [https://news.ycombinator.com/item?id=45436534](https://news.ycombinator.com/item?id=45436534)  
18. Overview | SpacetimeDB docs, accessed December 16, 2025, [https://spacetimedb.com/docs/](https://spacetimedb.com/docs/)  
19. TypeScript Reference | SpacetimeDB docs, accessed December 16, 2025, [https://spacetimedb.com/docs/sdks/typescript/](https://spacetimedb.com/docs/sdks/typescript/)  
20. web3.js \- Adding signers for 'signTransactionMessageWithSigners' \- and is it related to setTransactionMessageFeePayer vs. setTransactionMessageFeePayerSigner \- Solana Stack Exchange, accessed December 16, 2025, [https://solana.stackexchange.com/questions/20509/adding-signers-for-signtransactionmessagewithsigners-and-is-it-related-to-se](https://solana.stackexchange.com/questions/20509/adding-signers-for-signtransactionmessagewithsigners-and-is-it-related-to-se)
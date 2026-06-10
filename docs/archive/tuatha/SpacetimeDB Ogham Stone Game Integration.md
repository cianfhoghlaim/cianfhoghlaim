# **Architectural Specification: Decentralized Geospatial Procedural Generation Systems for the 'Anam' Project**

## **1\. Introduction: The Convergence of Heritage, Hyper-Scale, and Decentralized State**

The contemporary landscape of interactive entertainment is witnessing a profound convergence between persistent, real-time multiplayer environments and the immutable, distributed ledgers of blockchain technology. This report presents a comprehensive architectural specification for a Location-Based Game (LBG) titled "Anam," which seeks to synthesize ancient epigraphic heritage with modern decentralized infrastructure. The core technical objective is the procedural generation of "Anam" (Soul) particles—dynamic visual entities within a Unity client—whose properties are deterministically governed by the geospatial and archaeological attributes of Ogham stones distributed throughout the British Isles.  
Unlike traditional game architectures that rely on a fragmented stack of API servers, caching layers, and external databases, the proposed architecture leverages **SpacetimeDB**, a novel "database-as-server" technology. By executing game logic as **Rust WebAssembly (Wasm)** modules directly within the database's transaction loop, the system achieves the sub-millisecond latency required for real-time geospatial interactions.1 This architectural paradigm shifts the computation of state away from ephemeral application servers and into the persistence layer itself, ensuring that the "world state" is always consistent, queryable, and reactive.  
Furthermore, the "Anam" project integrates a sophisticated economic and asset layer built upon the **Solana** blockchain. Utilizing the newly released **Metaplex Core** standard, the game assets are modeled as Dynamic Non-Fungible Tokens (dNFTs) capable of on-chain evolution—changing their metadata in response to player movement and interaction history without incurring the high costs associated with legacy token standards.3 The game currency, "Ogham Coin," is implemented as a Solana SPL token, with bridging mechanisms to Ethereum to ensure broad liquidity and interoperability.5  
This report provides an exhaustive technical analysis of the entire stack. It details the ingestion pipelines for the Celtic Inscribed Stones Project (CISP) dataset, the implementation of custom geospatial indexing algorithms within Rust Wasm modules, the orchestration of secure cross-chain transactions via oracle relayers, and the optimization of client-side particle rendering using Unity’s Visual Effect Graph (VFX Graph). The result is a blueprint for a "living" digital archive where the ancient landscape of the British Isles drives the behavior of a futuristic, decentralized economy.

## ---

**2\. The Archaeological Data Foundation: Ogham Stone Ingestion and Normalization**

The procedural generation engine at the heart of the "Anam" project is not driven by arbitrary noise functions, but by a structured archaeological dataset. The fidelity of the "Anam" particles depends entirely on the accurate ingestion, normalization, and semantic mapping of Ogham stone data.

### **2.1. Ogham: The Epigraphic Context**

Ogham is an Early Medieval alphabet, used primarily to write the early Irish language, and later Old Irish. It consists of a series of strokes—notches or lines—cut into the edge (arris) of a stone or wood.7 The alphabet is historically grouped into four *aicmí* (families), each containing five letters. This structure is intrinsically digital, resembling a base-5 counting system or a primitive barcode, making it uniquely suitable for algorithmic interpretation in a game context.9  
The stones themselves serve as the geospatial anchors for the game. Distributed across Ireland, Scotland, Wales, Dumnonia (Devon/Cornwall), and the Isle of Man, they mark territories, graves, or memorials.7 The texts are often genealogical, following the formula "X son of Y" (e.g., *MAQI-DECEDA*), linking the physical location to a specific ancestral identity.10 This "identity" is the seed data for the "Anam" particle: the visual representation of the ancestor's soul.

### **2.2. Primary Data Sources**

To construct the game world, we must ingest data from two primary academic repositories, reconciling their disparate formats and coordinate systems.

#### **2.2.1. The Celtic Inscribed Stones Project (CISP)**

The CISP database, completed by University College London, is the definitive academic corpus for non-Runic inscriptions in the Celtic-speaking world from AD 400–1000.11

* **Data Structure:** CISP organizes data into three relational categories: SITE (geography), STONE (physical object), and INSCRIPTION (text).11  
* **Utility:** This source provides the "DNA" for the procedural generation. The INSCRIPTION table allows us to parse the Ogham text (e.g., "CUNACENA") 13 and map specific phonemes to visual particle effects (e.g., the letter 'C' (Coll/Hazel) triggers a specific color palette).  
* **Access:** The data is available as a downloadable dataset via the Archaeology Data Service.11

#### **2.2.2. The Megalithic Portal**

While CISP provides deep metadata, the Megalithic Portal offers superior geospatial accessibility, often crowdsourced and verified by GPS.

* **Data Structure:** The Portal offers data in GeoJSON, CSV, and KML formats, specifically tagged with site types like "Ogham Stone" or "Inscribed Stone".14  
* **Utility:** This serves as the primary source for the latitude and longitude coordinates required for the location-based gameplay. The Portal's data often includes precise "visited" coordinates that correct older, vague archaeological grid references.

**Table 1: Data Source Reconciliation Strategy**

| Attribute | CISP Database | Megalithic Portal | Integration Strategy |
| :---- | :---- | :---- | :---- |
| **Coordinate System** | Irish Grid / National Grid (Legacy) | WGS84 (Decimal Degrees) | Use Portal for position; CISP for validation. |
| **Site Identification** | Academic Site ID (e.g., KE065-078) | Unique Portal ID / URL | Fuzzy string matching on Site Name \+ Radius check. |
| **Epigraphy** | Transliterated Text & Analysis | Descriptive Text | Prioritize CISP reading for RNG seeding. |
| **Dating** | 4th–10th Century AD ranges | General categorization | Use CISP dating to determine "Anam" intensity. |

### **2.3. The ETL Pipeline: From GeoJSON to SpacetimeDB**

The Extract, Transform, Load (ETL) pipeline is responsible for converting raw archaeological data into a format that the SpacetimeDB Rust module can query efficiently in real-time.

#### **2.3.1. Coordinate Normalization**

Archaeological data in the British Isles is frequently recorded using the **Irish Transverse Mercator (ITM)** or the **British National Grid (BNG)**.16 Game engines (Unity) and GPS systems (mobile devices) operate on the **WGS84** ellipsoid (latitude/longitude). The pipeline must implement a reprojection step using a library like proj4 (in the preprocessing Python/Rust script) before the data enters the database.

* **Input:** ITM Coordinates: 630844, 593197\.16  
* **Transformation:** Apply Helmert transformation to convert to ETRS89/WGS84.  
* **Output:** Lat: 52.089832, Long: \-7.549906.

#### **2.3.2. Struct Mapping in Rust**

The SpacetimeDB module defines the schema for the world data. Unlike a traditional SQL database where schema is defined in DDL, SpacetimeDB defines schema via Rust structs annotated with \#\[spacetimedb::table\].17  
We define a Stone table that acts as the immutable registry of all game locations.

Rust

// lib.rs \- SpacetimeDB Module  
use spacetimedb::{table, spacetimedb};

\#\[table(name \= ogham\_stone, public)\]  
pub struct OghamStone {  
    \#\[primary\_key\]  
    pub id: u32,               // Derived from Megalithic Portal ID  
    pub cisp\_id: String,       // Cross-reference to CISP  
    pub lat: f64,              // WGS84 Latitude  
    pub long: f64,             // WGS84 Longitude  
    pub name: String,          // e.g., "Coolmagort VII"  
    pub inscription: String,   // e.g., "MAQI-DECEDA"  
    pub aicme\_affinity: u8,    // 1-4, determining elemental type  
    pub dating\_century: u8,    // e.g., 5 (5th Century)  
}

The aicme\_affinity field is a derived integer calculated during the ETL process. It analyzes the inscription text to find the dominant character group (Aicme Beith, Aicme Uath, etc.), which subsequently determines the elemental alignment of the Anam particle (e.g., Earth, Water, Air, Fire).9

## ---

**3\. SpacetimeDB Architecture: The "Database-as-Server" Paradigm**

The architectural differentiator of the "Anam" project is its utilization of SpacetimeDB. In traditional MMO architectures, a game server (simulating the world) communicates with a database (persisting the world) over a network. This introduces latency, synchronization headaches, and "gold dupe" vulnerabilities where the simulation state drifts from the persisted state.2  
SpacetimeDB collapses this stack. The application logic is compiled to WebAssembly and uploaded *into* the database. The database *is* the server.

### **3.1. The Rust Module and WebAssembly**

The server-side logic is written in Rust, leveraging its memory safety and type system, and compiled to the wasm32-unknown-unknown target.1 This Wasm blob is deployed to the SpacetimeDB host.  
The implications for the "Anam" project are significant:

1. **Atomic Reducers:** All game logic occurs inside "Reducers"—functions that take a context and arguments. Each reducer execution is a single ACID transaction. When a player moves or collects an Anam, the update is atomic. Either the movement happens and the persistence updates, or it fails entirely. There is no "intermediate" state.2  
2. **Zero-Latency Access:** The reducer has direct access to the in-memory tables. There is no SELECT \* FROM... over a TCP socket. The data is accessed via pointer lookups in the Wasm memory space, enabling extremely high-throughput geospatial queries.19

### **3.2. Client-Side Subscriptions vs. Server-Side Filtering**

SpacetimeDB employs a subscription model. The Unity client does not request data via HTTP GET; instead, it opens a WebSocket and subscribes to SQL queries.22

* **Query:** SELECT \* FROM AnamParticle WHERE owner\_id \= @identity  
* **Mechanism:** The server pushes updates to the client whenever the result set of this query changes. This is "incremental view maintenance" for game state.

For the geospatial component, we cannot simply SELECT \* FROM Stones. That would send 1,200+ rows to the client. Instead, we must implement a mechanism where the client subscribes only to the "Local Grid Bucket" they are inhabiting. This requires dynamic subscription management in the Unity client, updating the subscription query as the player moves across grid boundaries.23

## ---

**4\. Geospatial Engineering in Rust Wasm: The Indexing Challenge**

One of the critical technical hurdles in using SpacetimeDB for location-based gaming is the current lack of native geospatial types (like PostGIS GEOMETRY) and spatial indices (like R-Trees) within the core SQL engine.22 While SpacetimeDB supports standard B-Tree indexes 25, these are insufficient for efficient "K-Nearest Neighbor" (KNN) or "Points Within Radius" queries required for checking player proximity to stones.  
Therefore, the geospatial indexing logic must be implemented *within the Rust module* itself.

### **4.1. The "No\_Std" Constraint and Crate Selection**

The Rust module runs in a Wasm environment, which is roughly equivalent to a no\_std environment in terms of system access (no file system, restricted networking). While std is available, we cannot link against C libraries like libgeos or GDAL. We must use pure-Rust geospatial libraries.26  
The **geo** crate is the standard for geospatial primitives in Rust and is Wasm-compatible. It provides the Haversine distance formula, which is essential for calculating the great-circle distance between the player's GPS coordinates and the stone locations.28

### **4.2. Implementing a Uniform Grid Spatial Index**

To avoid an $O(N)$ scan of all 1,200+ stones every time a player moves (which would consume excessive compute units), we implement a **Uniform Grid** (or Spatial Hashing) index.

#### **4.2.1. The Bucket Key Algorithm**

The world map (specifically the British Isles) is divided into fixed-size rectangular buckets. A bucket size of roughly 0.01 degrees (\~1.11 km) is appropriate for the density of Ogham stones.  
We define a helper function to convert a coordinate to a bucket ID:

$$BucketID \= \\lfloor Latitude \\times 100 \\rfloor \\times 1,000,000 \+ \\lfloor Longitude \\times 100 \\rfloor$$  
This maps 2D space into a 1D integer space (the bucket\_id) which can be indexed using SpacetimeDB's native B-Tree index.20

#### **4.2.2. The Spatial Index Table**

We introduce a secondary table to accelerate lookups.

Rust

\#\[table(name \= spatial\_grid, public)\]  
pub struct SpatialGrid {  
    \#\[primary\_key\]  
    pub bucket\_id: i64,  
    pub stone\_ids: Vec\<u32\>, // List of stones residing in this 1km sector  
}

When the init reducer loads the Ogham data, it also populates this SpatialGrid table. It iterates through all stones, calculates their bucket ID, and pushes the stone ID to the corresponding vector.

### **4.3. The Proximity Query Logic**

When a player's position updates, the reducer executes the following logic to find interactable stones:

1. **Calculate Player Bucket:** Determine the bucket\_id for the player's current lat/long.  
2. **Identify Neighbors:** Calculate the IDs of the 8 surrounding buckets (Moore neighborhood) to handle edge cases where a player is near a bucket boundary.  
3. **Fetch Candidates:** Retrieve the stone\_ids from the SpatialGrid table for these 9 buckets. This reduces the search space from \~1,200 stones to typically \<5 stones.  
4. Precise Distance Check: Iterate through the candidate stones and apply the Haversine formula:

   $$d \= 2R \\cdot \\arcsin\\left(\\sqrt{\\sin^2\\left(\\frac{\\Delta\\phi}{2}\\right) \+ \\cos \\phi\_1 \\cdot \\cos \\phi\_2 \\cdot \\sin^2\\left(\\frac{\\Delta\\lambda}{2}\\right)}\\right)$$

   If $d \< InteractionRadius$ (e.g., 50 meters), the player is considered "at" the stone.28

## ---

**5\. The 'Anam' Particle System: Procedural Generation Logic**

The "Anam" is the central collectible of the game—a digital soul. Its visual appearance is not static; it is procedurally generated based on the specific attributes of the Ogham stone and the environmental conditions at the moment of discovery.

### **5.1. Deterministic Seeding from Epigraphy**

To ensure that every player sees the same particle at the same stone (shared reality), the generation algorithm must be deterministic. We use the Ogham inscription string as a seed.

* **Seed Generation:** Seed \= Hash(Stone.Inscription \+ Stone.Dating)  
* **Color Palette:** The 20 letters of the Ogham alphabet are named after trees (e.g., *Beith*/Birch, *Luis*/Rowan, *Fern*/Alder).9 We map these to color vectors.  
  * *Beith (B)* \-\> Birch \-\> Silver/White  
  * *Duir (D)* \-\> Oak \-\> Deep Green/Brown  
  * *Tinne (T)* \-\> Holly \-\> Dark Green/Red  
* **Turbulence/Volatility:** Derived from the Stone.Condition field in the CISP dataset. A "Damaged" or "Fragmented" stone generates a highly volatile, flickering particle, whereas an "Intact" stone generates a stable, laminar flow particle.

### **5.2. Dynamic Environmental Modifiers (Scheduled Reducers)**

The "Anam" is described as "changing." This implies it reacts to time. SpacetimeDB supports **Scheduled Reducers**, which are functions triggered at specific timestamps or intervals.29  
We implement a WorldTick reducer that runs every 15 minutes.

* **Function:** It updates a GlobalState table containing DayNightCycle (0.0 to 1.0) and CelestialAlignment values.  
* **Effect:** The Anam particle's visual logic (client-side) subscribes to this GlobalState. At night, the particles might glow with higher intensity (luminescence), while during the day they appear more crystalline (refraction).

### **5.3. The 'Resonance' Resource**

Proximity to a stone generates "Resonance." This is a calculated value in the PlayerState table.

* **Formula:** $ResonanceRate \= \\frac{BaseRate}{Distance^2 \+ 1}$  
* **Persistence:** The update\_position reducer increments the player's accumulated Resonance based on this rate. This Resonance is the raw material required to "capture" the Anam and mint it as an NFT.

## ---

**6\. Client-Side Realization: Unity and the VFX Graph**

The Unity engine serves as the visualizer for the SpacetimeDB state. It does not perform the authoritative game logic; it interpolates and renders the data streams.

### **6.1. SpacetimeDB SDK Integration**

The Unity client integrates the **SpacetimeDB C\# SDK**.30 This SDK handles the WebSocket connection, serialization (using the SpacetimeDB.Type attribute), and event dispatching.  
Optimization for High-Frequency Updates:  
Handling 30-60 updates per second for particle data can generate significant garbage collection (GC) pressure in C\#.

* **Struct-Based Data:** We generate C\# structs rather than classes for the table rows to utilize stack memory where possible.  
* **Object Pooling:** We utilize the SpacetimeDB.Type generated classes but map them to a pre-allocated pool of VFXControllers in the scene to avoid instantiating new GameObjects for every particle update.32

### **6.2. Visual Effect Graph (VFX Graph) Architecture**

We utilize Unity's **VFX Graph** for rendering the Anam particles. Unlike the legacy Shuriken particle system, VFX Graph runs on the GPU, allowing for millions of particles—necessary to achieve the "ethereal" look of a soul.33

#### **6.2.1. Parameter Binding**

The connection between the database state and the GPU is bridged via "Exposed Properties" in the VFX Graph.33

* **Resonance (DB) \-\> Spawn Rate (VFX):** The Resonance value from the PlayerState table is passed to the SetFloat API of the Visual Effect component.  
* **Element (DB) \-\> Gradient (VFX):** The AicmeAffinity integer is used to sample from a Texture2D look-up table within the shader graph, effectively changing the color palette without CPU overhead.  
* **Distance (DB) \-\> Attractor Force (VFX):** As the player approaches, the Distance calculated by the server is passed to a "Point Attractor" node in the VFX graph, causing the particles to swirl towards the player's avatar.

C\#

// AnamVFXController.cs  
public void OnSpacetimeDBUpdate(AnamRow row) {  
    // Efficiently set parameters using Cached Property IDs to avoid string hashing  
    vfxComponent.SetFloat(IDs.Resonance, row.resonance);  
    vfxComponent.SetVector3(IDs.ColorTarget, ElementMap.GetColor(row.aicme));  
      
    if (row.is\_captured) {  
        vfxComponent.SendEvent(IDs.OnCaptureEvent); // Trigger "suck in" animation  
    }  
}

## ---

**7\. Blockchain Integration Layer 1: Solana and Metaplex Core**

The "Anam" particles are not merely ephemeral graphics; they are persistent digital assets. When a player accumulates enough Resonance, they can "crystallize" the particle into a **Dynamic NFT (dNFT)** on the **Solana** blockchain.

### **7.1. Why Metaplex Core?**

We select the **Metaplex Core** standard over the legacy Token Metadata standard or SPL Token 2022 extensions.

* **Single Account Architecture:** Metaplex Core drastically reduces the number of accounts required to mint an NFT. Legacy standards required a Mint Account, Token Account, Metadata Account, and Edition Account. Core uses a single Asset Account. This reduces minting costs (Rent) by \>80% and simplifies indexing.3  
* **Low Compute:** The optimized instruction set allows for more complex logic (like our game evolution mechanics) to fit within Solana's compute budget per transaction.

### **7.2. The Dynamic Metadata Plugin System**

The defining feature of the "Anam" is that it *changes*. It evolves based on the player's journey. Metaplex Core handles this via its **Plugin** architecture.4  
We utilize the **Attributes Plugin** to store game data directly on-chain:

* Origin\_Stone\_ID: Immutable (The ID of the stone where it was found).  
* Evolution\_Stage: Mutable (Increases as the player visits more stones).  
* Resonance\_Charge: Mutable (Fluctuates based on interaction).

### **7.3. The Relayer Pattern for Transaction Signing**

A critical architectural constraint is that the SpacetimeDB module (Wasm) cannot securely hold the private key required to sign Solana transactions (it is a shared execution environment).1  
To solve this, we implement a **Trusted Relayer Service**:

1. **Trigger:** The SpacetimeDB module approves an evolution (e.g., "Level Up"). It inserts a row into a PendingTransaction table.  
2. **Detection:** A Node.js service (The Relayer), running in a secure environment (e.g., AWS KMS), subscribes to PendingTransaction via the SpacetimeDB SDK.23  
3. **Execution:** The Relayer detects the new row. It constructs a Solana transaction using @metaplex-foundation/umi.4  
4. **Signing:** The Relayer signs the transaction using the Game Studio's authority key (which is the UpdateAuthority of the NFT collection).  
5. **Submission:** The transaction calls the UpdateV1 instruction on the Metaplex Core program, modifying the on-chain Attributes plugin of the user's NFT.  
6. **Callback:** Upon confirmation, the Relayer calls a SpacetimeDB reducer to mark the transaction as complete, keeping the database and blockchain in sync.

## ---

**8\. Blockchain Integration Layer 2: Economics and Bridging**

The economic engine of the game is the "Ogham Coin," an SPL Token on Solana that facilitates trade and marketplace interactions.

### **8.1. Ogham Coin (SPL Token)**

The currency acts as the "energy" of the system.

* **Minting:** Players earn "Soft Ogham" in the database by discovering stones. To move this on-chain, they initiate a withdrawal. The Relayer Service handles the MintTo or Transfer instruction from a treasury wallet to the player's Solana wallet.36  
* **Utility:** Ogham Coin is required to "recharge" Anam particles that have decayed or to purchase "Vessels" (another NFT type) to hold them.

### **8.2. Cross-Chain Interoperability: Bridging to Ethereum**

While Solana provides the speed for gameplay, Ethereum provides deep liquidity and prestige markets. The requirement to use Ethereum is satisfied via a **Lock-and-Mint Bridge** architecture, utilizing protocols like **Wormhole**.6  
**The Bridging Workflow:**

1. **Locking (Solana):** The player sends their Anam dNFT or Ogham Tokens to a specific Bridge Smart Contract on Solana.  
2. **Guardian Verification:** The Wormhole Guardian network observes this transaction and produces a Verified Action Approval (VAA).6  
3. **Minting (Ethereum):** The player submits this VAA to the corresponding Bridge Contract on Ethereum.  
4. **Asset Creation:** The Ethereum contract mints a "Wrapped Anam" (ERC-721) or "Wrapped Ogham" (ERC-20).

*Constraint Note:* Dynamic metadata updates are prohibitively expensive on Ethereum Mainnet. Therefore, the "Wrapped Anam" on Ethereum will likely be a *static snapshot* of the particle at the moment of bridging. If the player wants to evolve the particle further, they must bridge it back to Solana.

## ---

**9\. Security and Integrity**

### **9.1. GPS Spoofing Mitigation**

In LBG titles, location spoofing is the primary attack vector.

* **Speed Heuristics:** The SpacetimeDB reducer calculates the velocity between the current position update and the previous one. If $Velocity \> 100 km/h$ (and the player is not in "Travel Mode"), the update is rejected.  
* **Jitter Analysis:** Real GPS signals have statistical noise. A stream of perfectly static coordinates or linear movement indicates a bot/emulator. The Rust module can maintain a rolling variance of the last 10 coordinates to detect synthetic inputs.

### **9.2. Transaction Authority**

The UpdateAuthority for the Metaplex Core collection is the "Key to the Kingdom." It allows changing the metadata of any player's NFT.

* **Security:** This key is never exposed to the client or the SpacetimeDB module. It lives exclusively in the **Fireblocks** or **AWS KMS** environment accessed by the Relayer Service.37  
* **Delegation:** For advanced gameplay, we can use Metaplex Core's **Update Delegate Plugin** to assign specific update rights to a Program Derived Address (PDA), effectively creating an on-chain smart contract that acts as the arbiter of evolution, removing the centralized Relayer from the trust loop in the future.

## ---

**10\. Conclusion**

The "Anam" project architecture represents a pioneering fusion of archaeology, high-performance distributed computing, and decentralized finance. By utilizing **SpacetimeDB**, we eliminate the synchronization latency that plagues traditional multiplayer games, allowing the "world state" to be the single source of truth. By grounding the procedural generation in the **CISP Ogham dataset**, we ensure the game has deep cultural resonance and variety. Finally, by building on **Solana's Metaplex Core**, we create a digital asset class that is not static, but lives and evolves alongside the player.  
This is not merely a game; it is a location-aware, cryptographically verified extension of the ancient history of the British Isles, turning 1,500-year-old stones into the nodes of a futuristic digital network.

### **10.1. Technical Stack Summary**

| Layer | Technology | Function |
| :---- | :---- | :---- |
| **Persistence** | SpacetimeDB | Authoritative Game State, User Accounts, Spatial Index. |
| **Logic** | Rust (Wasm) | Movement validation, Spatial Queries, Procedural Generation. |
| **Geospatial** | geo crate (Rust) | Haversine distance, Coordinate systems. |
| **Client** | Unity 2022 LTS | Rendering, Input, AR/GPS interface. |
| **Visuals** | VFX Graph (Unity) | GPU-accelerated particle rendering of Anam souls. |
| **Blockchain** | Solana (Mainnet) | dNFTs (Metaplex Core), Currency (SPL). |
| **Bridging** | Wormhole | Transfer of assets to Ethereum (ERC-721/ERC-20). |
| **Middleware** | Node.js / umi | Transaction Relayer/Signer service. |

The infrastructure is scalable, secure, and uniquely positioned to define the next generation of "Real-World Assets" in gaming.

#### **Works cited**

1. spacetimedb \- Rust \- Docs.rs, accessed December 19, 2025, [https://docs.rs/spacetimedb/latest/spacetimedb/](https://docs.rs/spacetimedb/latest/spacetimedb/)  
2. SpacetimeDB, accessed December 19, 2025, [https://spacetimedb.com/](https://spacetimedb.com/)  
3. NFTs on Solana | Metaplex Core \- Blueshift, accessed December 19, 2025, [https://learn.blueshift.gg/courses/nfts-on-solana/metaplex-core](https://learn.blueshift.gg/courses/nfts-on-solana/metaplex-core)  
4. What is Metaplex Core and How to Mint Your First Core NFT | Quicknode Guides, accessed December 19, 2025, [https://www.quicknode.com/guides/solana-development/nfts/metaplex-core](https://www.quicknode.com/guides/solana-development/nfts/metaplex-core)  
5. What is the Solana-Base bridge, and how does it work? \- OneSafe Blog, accessed December 19, 2025, [https://www.onesafe.io/blog/solana-base-bridge-cross-chain-transactions](https://www.onesafe.io/blog/solana-base-bridge-cross-chain-transactions)  
6. Top 5 Bridges to Solana: Your Guide to Bringing Assets to Solana | CoinGecko, accessed December 19, 2025, [https://www.coingecko.com/learn/top-solana-bridges](https://www.coingecko.com/learn/top-solana-bridges)  
7. ogham stones | The Heritage Council, accessed December 19, 2025, [https://www.heritagecouncil.ie/content/files/Ogham-Stones.pdf](https://www.heritagecouncil.ie/content/files/Ogham-Stones.pdf)  
8. Ogham Stones of Ireland, accessed December 19, 2025, [http://www.megalithicireland.com/Ogham%20Stones%20Page%201.htm](http://www.megalithicireland.com/Ogham%20Stones%20Page%201.htm)  
9. Celtic Ogham Stones and Ogham Script \- The Irish Place, accessed December 19, 2025, [https://www.theirishplace.com/heritage/megalithic-monuments/celtic-ogham-stones-ogham-script/](https://www.theirishplace.com/heritage/megalithic-monuments/celtic-ogham-stones-ogham-script/)  
10. CIIC 203\. Coolmagort VII, Co. Kerry \- Ogham in 3D, accessed December 19, 2025, [https://ogham.celt.dias.ie/version2013/stone.php?lang=en\&site=Coolmagort\&stone=203.\_Coolmagort\_VII\&stoneinfo=description](https://ogham.celt.dias.ie/version2013/stone.php?lang=en&site=Coolmagort&stone=203._Coolmagort_VII&stoneinfo=description)  
11. Celtic Inscribed Stones Project: Overview \- Archaeology Data Service, accessed December 19, 2025, [https://archaeologydataservice.ac.uk/archives/view/cisp\_2003/overview.cfm](https://archaeologydataservice.ac.uk/archives/view/cisp_2003/overview.cfm)  
12. Celtic Inscribed Stones Project: Introduction \- Archaeology Data Service, accessed December 19, 2025, [https://archaeologydataservice.ac.uk/archives/view/cisp\_2003/](https://archaeologydataservice.ac.uk/archives/view/cisp_2003/)  
13. Investigating Ogham Stones \- ArcGIS StoryMaps, accessed December 19, 2025, [https://storymaps.arcgis.com/stories/e2bae547de45485586427d528995d852](https://storymaps.arcgis.com/stories/e2bae547de45485586427d528995d852)  
14. The Megalithic Portal \- Wikipedia, accessed December 19, 2025, [https://en.wikipedia.org/wiki/The\_Megalithic\_Portal](https://en.wikipedia.org/wiki/The_Megalithic_Portal)  
15. GeoJSON to CSV Converter Online | MyGeodata Cloud, accessed December 19, 2025, [https://mygeodata.cloud/converter/geojson-to-csv](https://mygeodata.cloud/converter/geojson-to-csv)  
16. Historic Environment Viewer, accessed December 19, 2025, [https://heritagedata.maps.arcgis.com/apps/webappviewer/index.html?id=0c9eb9575b544081b0d296436d8f60f8\&query=18a4b61b268-layer-9%2CSMRS%2CWA031-045002-](https://heritagedata.maps.arcgis.com/apps/webappviewer/index.html?id=0c9eb9575b544081b0d296436d8f60f8&query=18a4b61b268-layer-9,SMRS,WA031-045002-)  
17. Rust Quickstart | SpacetimeDB docs, accessed December 19, 2025, [https://spacetimedb.com/docs/modules/rust/quickstart/](https://spacetimedb.com/docs/modules/rust/quickstart/)  
18. 2 \- Connecting to SpacetimeDB, accessed December 19, 2025, [https://spacetimedb.com/docs/unity/part-2](https://spacetimedb.com/docs/unity/part-2)  
19. SpacetimeDB and BitCraft \- Clockwork Labs, accessed December 19, 2025, [https://clockwork-labs.medium.com/spacetimedb-and-bitcraft-bc957a7faf40](https://clockwork-labs.medium.com/spacetimedb-and-bitcraft-bc957a7faf40)  
20. spacetimedb \- crates.io: Rust Package Registry, accessed December 19, 2025, [https://crates.io/crates/spacetimedb](https://crates.io/crates/spacetimedb)  
21. C\# Quickstart | SpacetimeDB docs, accessed December 19, 2025, [https://spacetimedb.com/docs/modules/c-sharp/quickstart](https://spacetimedb.com/docs/modules/c-sharp/quickstart)  
22. SQL Reference | SpacetimeDB docs, accessed December 19, 2025, [https://spacetimedb.com/docs/sql/](https://spacetimedb.com/docs/sql/)  
23. Subscription Reference | SpacetimeDB docs, accessed December 19, 2025, [https://spacetimedb.com/docs/subscriptions/](https://spacetimedb.com/docs/subscriptions/)  
24. Are there any database that support spatial-temporal indexes? \[closed\], accessed December 19, 2025, [https://gis.stackexchange.com/questions/469888/are-there-any-database-that-support-spatial-temporal-indexes](https://gis.stackexchange.com/questions/469888/are-there-any-database-that-support-spatial-temporal-indexes)  
25. TypeScript Reference | SpacetimeDB docs, accessed December 19, 2025, [https://spacetimedb.com/docs/modules/typescript/](https://spacetimedb.com/docs/modules/typescript/)  
26. geoarrow-wasm, accessed December 19, 2025, [https://geoarrow.org/geoarrow-rs/js/](https://geoarrow.org/geoarrow-rs/js/)  
27. Are all Rust libs on crates compatible with WASM \- Reddit, accessed December 19, 2025, [https://www.reddit.com/r/rust/comments/g80pv0/are\_all\_rust\_libs\_on\_crates\_compatible\_with\_wasm/](https://www.reddit.com/r/rust/comments/g80pv0/are_all_rust_libs_on_crates_compatible_with_wasm/)  
28. Real-Time Geospatial Intelligence: Leveraging Rust WebAssembly and Predictive AI for Browser-Based Spatial Queries. | by Leonardo de Melo | Medium, accessed December 19, 2025, [https://medium.com/@LeonardoDeMeloWeb/real-time-geospatial-intelligence-leveraging-rust-webassembly-and-predictive-ai-for-browser-based-a608ca5ed7c2](https://medium.com/@LeonardoDeMeloWeb/real-time-geospatial-intelligence-leveraging-rust-webassembly-and-predictive-ai-for-browser-based-a608ca5ed7c2)  
29. 3 \- Gameplay | SpacetimeDB docs, accessed December 19, 2025, [https://spacetimedb.com/docs/unreal/part-3](https://spacetimedb.com/docs/unreal/part-3)  
30. 1 \- Setup | SpacetimeDB docs, accessed December 19, 2025, [https://spacetimedb.com/docs/unity/part-1](https://spacetimedb.com/docs/unity/part-1)  
31. SpacetimeDB C\# Support \- Visual Studio Marketplace, accessed December 19, 2025, [https://marketplace.visualstudio.com/items?itemName=SpacetimeDBUnofficial.spacetimedb-csharp](https://marketplace.visualstudio.com/items?itemName=SpacetimeDBUnofficial.spacetimedb-csharp)  
32. Special optimizations \- Unity \- Manual, accessed December 19, 2025, [https://docs.unity3d.com/560/Documentation/Manual/BestPracticeUnderstandingPerformanceInUnity8.html](https://docs.unity3d.com/560/Documentation/Manual/BestPracticeUnderstandingPerformanceInUnity8.html)  
33. Visual Effect Component API | Visual Effect Graph | 7.1.8 \- Unity \- Manual, accessed December 19, 2025, [https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@7.1/manual/ComponentAPI.html](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@7.1/manual/ComponentAPI.html)  
34. Visual Effect component API | Visual Effect Graph | 10.2.2, accessed December 19, 2025, [https://docs.unity.cn/Packages/com.unity.visualeffectgraph@10.2/manual/ComponentAPI.html](https://docs.unity.cn/Packages/com.unity.visualeffectgraph@10.2/manual/ComponentAPI.html)  
35. An On-Chain Introduction To Metaplex Core \- DaoPlays, accessed December 19, 2025, [https://www.daoplays.org/blog/core\_p1](https://www.daoplays.org/blog/core_p1)  
36. Solana-web3.js Tutorial \- Send a Solana transaction in 3 Minutes \- Chainstack, accessed December 19, 2025, [https://chainstack.com/solana-web3-js-tutorial-send-a-solana-transaction/](https://chainstack.com/solana-web3-js-tutorial-send-a-solana-transaction/)  
37. fireblocks-solana-signer \- crates.io: Rust Package Registry, accessed December 19, 2025, [https://crates.io/crates/fireblocks-solana-signer](https://crates.io/crates/fireblocks-solana-signer)
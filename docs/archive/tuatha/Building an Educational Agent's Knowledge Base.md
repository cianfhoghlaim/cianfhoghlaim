# **Architecting the Autonomous Epistemologist: A Technical Blueprint for Agentic Knowledge Acquisition and Dynamic Domain Modeling**

## **Executive Summary**

The paradigm of automated information retrieval is undergoing a fundamental shift from static, procedural web scraping to dynamic, agentic knowledge acquisition. Traditional extract-transform-load (ETL) pipelines, while robust for structured data, falter when confronted with the semantic ambiguity and structural volatility of the open web. This report details a comprehensive technical architecture for an educational agent capable of autonomously constructing, maintaining, and refining a sophisticated knowledge base across heterogeneous domains. The proposed system integrates **Agno** (formerly Phi Data) for cognitive orchestration, **Dagster** for asset-centric data engineering, **dlt** (Data Load Tool) for high-fidelity ingestion, and **BAML** (Boundary Abstract Modeling Language) for structured extraction with dynamic schema evolution.  
We explore the implementation of a "self-healing" ontology where the agent utilizes BAML’s TypeBuilder to detect schema drift in real-time—such as identifying new API endpoints in Cloudflare documentation or evolving consensus mechanisms in Ethereum—and autonomously proposes structural updates to its internal model. This addresses the critical challenge of "schema sprawl" by enforcing a rigid core ontology while allowing flexible, controlled extensions.  
The architecture emphasizes a **High User Experience (UX)** for the data engineer through Dagster’s software-defined assets (SDAs), providing visual lineage and observability from raw HTML stored in **Cloudflare R2** to analytical tables in **DuckDB** and temporal knowledge graphs in **Graphiti**. By leveraging **Model Context Protocol (MCP)** servers, the system decouples the agent’s reasoning engine from the underlying data infrastructure, creating a standardized interface for accessing semantic indices (**CocoIndex**) and relational graphs (**Cognee/Graphiti**).  
This analysis applies this architecture to four distinct "Base Nodes of Understanding": the decentralized ledger technology of **Ethereum** (contrasted with **Coinbase**), the edge infrastructure of **Cloudflare**, the hierarchical policy framework of the **UK Education System**, and the object-oriented architecture of the **Godot Game Engine**. Through deep domain modeling, we demonstrate how this stack transforms raw information into actionable, interconnected insight.

## ---

**1\. The Philosophical Shift: From Tasks to Assets in Agentic Engineering**

The design of autonomous knowledge systems requires a departure from imperative, task-based orchestration toward a declarative, asset-based philosophy. In traditional scraping workflows, success is defined by the completion of a script (e.g., "Run scrape\_schools.py"). In an agentic workflow, success is defined by the materialization of a high-quality data asset (e.g., "The uk\_schools\_registry table is fresh and passes schema validation").

### **1.1 The Asset-Centric Paradigm with Dagster**

Dagster provides the foundational control plane for this architecture by treating data artifacts—files, tables, and graphs—as first-class citizens. Unlike orchestrators that manage "tasks," Dagster manages "Software-Defined Assets" (SDAs). This is crucial for an educational agent that must vouch for the provenance of its knowledge. When the agent asserts that "Godot 4.3 introduced the TileMapLayer node," the asset graph allows us to trace this fact back to the specific HTML file in Cloudflare R2, the BAML extraction run that parsed it, and the dlt job that ingested it.1  
This approach significantly enhances the developer experience (UX). Instead of debugging a failed task log, the engineer interacts with the asset lineage. If the ethereum\_gas\_fees asset is stale, Dagster visually indicates which upstream dependency (e.g., the etherscan\_scraper asset) failed to materialize. This visibility is essential when managing a complex graph of dependencies across disparate domains like cryptocurrency and education.

### **1.2 The Cognitive Kernel: Agno (Phi Data)**

While Dagster manages the flow of data, Agno provides the reasoning engine. Agno (formerly Phi Data) is selected for its lightweight, Pythonic approach to agent construction, which contrasts with the heavier, graph-based abstractions of LangGraph for purely agentic behaviors.3 Agno agents are designed to be "Model Agnostic" and highly performant, with instantiation times in the microseconds, making them ideal for embedding within high-throughput data pipelines.  
In this architecture, Agno agents are not just chatbots; they are "Headless Knowledge Workers." An Agno agent is responsible for the semantic interpretation of data. When dlt ingests a raw document, an Agno agent is triggered to analyze it using BAML tools. The agent determines if the document contains new concepts that require schema expansion. This integration of probabilistic reasoning (Agno) into deterministic pipelines (Dagster) constitutes the core innovation of this architecture.

### **1.3 The Universal Interface: Model Context Protocol (MCP)**

To prevent vendor lock-in and spaghetti code, we strictly adhere to the Model Context Protocol (MCP). MCP provides a standardized way for the Agno agent to interface with its memory and tools. Instead of hardcoding connection strings to DuckDB or Neo4j within the agent's prompt, we deploy MCP servers that expose these resources as standardized tools.5  
This decoupling allows for a modular "Plug-and-Play" architecture. The mcp-duckdb server exposes analytical capabilities (e.g., "Run a SQL query to compare pupil counts"), while the mcp-graphiti server exposes associative memory (e.g., "Find all entities related to 'Smart Contracts' valid between 2020 and 2022").7 The Agno agent simply consumes these tools, oblivious to the underlying complexity.

## ---

**2\. Ingestion Architecture: High-Fidelity Data Acquisition**

The foundation of any knowledge base is its ingestion layer. For an educational agent, this layer must be robust, respecting the polite constraints of web scraping while ensuring no data is lost. We utilize **dlt (Data Load Tool)** for its schema inference and incremental loading capabilities, targeting **Cloudflare R2** as a cost-effective, S3-compatible data lake.

### **2.1 The Unified Data Lake (Cloudflare R2)**

Cloudflare R2 is chosen for its zero-egress fee model, which is critical for an agent that frequently reads and re-reads its own archives to generate embeddings or train small models. We structure the R2 bucket into three distinct zones, mirroring the "Medallion" architecture but adapted for unstructured semantic data.

| Zone | Path Structure | Content Type | Retention Policy | Description |
| :---- | :---- | :---- | :---- | :---- |
| **Raw (Bronze)** | s3://base/raw/{domain}/{date}/{hash}.html | HTML, JSON, PDF | Permanent | The exact byte-for-byte copy of the source material. This allows for "Time Travel" re-extraction if our BAML schemas improve later. |
| **Extracted (Silver)** | s3://base/extracted/{domain}/{schema\_ver}/{id}.json | Structured JSON | Versioned | The output of BAML extraction functions. Validated against the domain ontology but strictly hierarchical (document-oriented). |
| **Knowledge (Gold)** | s3://base/knowledge/{index\_type}/{shard}.parquet | Parquet, Vector Indices | Current State | Analytical tables for DuckDB and semantic indices for CocoIndex. Optimized for query performance. |

### **2.2 Incremental Loading with dlt**

The educational agent must monitor dynamic sources—such as the daily release of OFSTED reports or real-time Ethereum block data—without re-downloading the entire internet. dlt handles this through its state management engine, which persists cursors (e.g., last\_modified timestamps or high\_water\_mark IDs) directly alongside the data in R2 or a dedicated state table.9  
When the uk\_schools\_ingest asset runs in Dagster:

1. It initializes the dlt pipeline with the filesystem destination pointing to R2.10  
2. It retrieves the state from the previous run (e.g., last\_inspection\_date: 2025-01-01).  
3. The scraper uses this cursor to request only inspections published after this date.  
4. dlt writes the new records to R2 and updates the state.

This mechanism ensures the pipeline is idempotent and resilient. If the job fails, dlt's state is not updated, ensuring the next run retries the missing data automatically.

### **2.3 Integration with Dagster Assets**

We wrap dlt pipelines within Dagster assets to provide observability. Using the @dlt\_assets decorator, we can project the internal tables created by dlt (e.g., schools, inspections, curriculum) as distinct assets in the Dagster lineage graph.1

Python

from dagster import AssetExecutionContext, Definitions  
from dagster\_dlt import DagsterDltResource, dlt\_assets  
from dlt\_sources.uk\_education import education\_source

@dlt\_assets(  
    dlt\_source=education\_source(),  
    dlt\_pipeline=dlt.pipeline(  
        pipeline\_name="education\_ingest",  
        destination="filesystem",  
        dataset\_name="uk\_education",  
        progress="log"  
    ),  
    name="education\_raw\_data",  
    group\_name="ingestion"  
)  
def education\_assets(context: AssetExecutionContext, dlt: DagsterDltResource):  
    yield from dlt.run(context=context)

This integration gives the "High User Experience" requested: the data engineer sees exactly when the education\_raw\_data asset was last materialized, how many rows were inserted, and can trigger a backfill directly from the UI if the underlying dlt schema changes.

## ---

**3\. Structural Intelligence: BAML and Dynamic Ontology**

The defining challenge of extracting knowledge from the web is "Schema Sprawl." Web data is messy and volatile. A rigid schema breaks constantly; a loose schema provides no value. We address this using **BAML (Boundary Abstract Modeling Language)**, which treats prompts as strongly typed functions with "fuzzy" parsing capabilities.12

### **3.1 The Schema Sprawl Problem**

In standard approaches, if we define a School schema with a rating field expecting "Good" or "Bad", and the source changes to "Grade A" or "Grade B", the pipeline crashes. Alternatively, if we make every field string, we lose the ability to query the data meaningfully (e.g., "Find all schools with rating \> 3").

### **3.2 Dynamic Schema Evolution with TypeBuilder**

Our solution leverages BAML’s TypeBuilder to create a **Self-Healing Ontology**. The workflow is as follows:

1. **Core Schema Definition:** We define a strict "Core" schema in BAML files. This represents the invariant properties of the domain (e.g., a School *must* have a name and a location).  
2. **Flexible Extension:** We define an "Extension" map or use the @@dynamic attribute on enums and classes to allow runtime expansion.14  
3. **Drift Detection:** When the Agno agent encounters data that doesn't fit the Core schema (e.g., a new energy\_efficiency\_rating field in a Cloudflare product page), the BAML parser flags this deviation.  
4. **Proposal Generation:** A specialized "Ontologist Agent" examines the deviation and uses TypeBuilder to propose a schema update. It might suggest adding energy\_rating as a float to the CloudflareProduct class.  
5. **Runtime Adaptation:** The pipeline temporarily adopts this dynamic schema to complete the current extraction job without data loss.  
6. **Human-in-the-Loop Consolidation:** The proposed schema changes are logged as "Schema Patch" assets in Dagster. An engineer reviews these patches and merges them into the permanent .baml definitions, effectively allowing the ontology to evolve with the domain.

### **3.3 Schema-Aligned Parsing (SAP)**

We utilize BAML's Schema-Aligned Parsing (SAP) to maximize extraction resilience. SAP allows the LLM to output "thinking" tokens or preamble text before generating the JSON, which significantly improves reasoning capability without breaking the parser.15 This is distinct from strict "JSON Mode" in other frameworks, which often forces the LLM to commit to a structure before it has fully "thought through" the content.  
For example, when extracting complex financial data from Coinbase, the model can output:  
"Analyzing the custody report... The assets are segregated... Okay, generating JSON:"  
{ "custody\_model": "segregated",... }  
BAML’s SAP ignores the preamble and cleanly extracts the typed object, ensuring high-fidelity data capture.

## ---

**4\. Semantic and Temporal Indexing: CocoIndex and Graphiti**

Structured data is useful, but *connected* data is knowledgeable. We employ a dual-indexing strategy: **CocoIndex** for semantic vector search and **Graphiti** for temporal knowledge graphs.

### **4.1 Incremental Semantic Indexing (CocoIndex)**

CocoIndex provides the semantic memory for the agent. It is configured to watch the R2 bucket for new extracted/ artifacts. Unlike standard vector stores that require full re-indexing, CocoIndex uses a **Flow Fingerprint** mechanism.16

* **Logic Hashing:** CocoIndex hashes the transformation logic (the chunking and embedding code). If we change the embedding model from text-embedding-3-small to voyage-large-2, CocoIndex automatically invalidates the index and reprocesses the data.  
* **Incremental Updates:** When dlt adds a new file to R2, CocoIndex detects the event via SQS or polling. It processes *only* the new file, chunking it according to domain-specific rules (e.g., splitting Godot docs by class methods) and adding it to the vector store.  
* **Data Lineage:** CocoIndex tracks which source file produced which vectors. If a file is deleted from R2 (e.g., a redacted OFSTED report), CocoIndex automatically removes the corresponding vectors, maintaining strict consistency.

### **4.2 Temporal Knowledge Graph (Graphiti)**

Standard knowledge graphs are static; they capture facts as they are *now*. However, for domains like Cryptocurrency or Software Development, *when* a fact was true is as important as the fact itself. Graphiti allows us to model this temporal dimension.19  
The "Cognify" Step with Cognee:  
Before insertion into Graphiti, we use Cognee to disambiguate entities.21 Cognee analyzes the extracted entities (e.g., "ETH", "Ether", "Ethereum 2.0") and resolves them to a single canonical node (Ethereum). It then identifies relationships based on the BAML ontology.  
Graphiti Ingestion:  
The Agno agent uses the mcp-graphiti server to insert "Episodes" of knowledge.

* **Episode:** "Godot 4.0 Release Notes."  
* **Facts:**  
  * RigidBody \----\> RigidBody3D  
  * KinematicBody \----\> CharacterBody3D

This temporal edge allows the agent to answer questions like: *"How did the physics API change between Godot 3 and 4?"* A static graph would simply show two conflicting node names; Graphiti reveals the evolutionary lineage.

## ---

**5\. Domain Analysis I: Cryptocurrency (Ethereum & Coinbase)**

To demonstrate the architecture, we apply it to the complex, fast-moving domain of cryptocurrency. We contrast the decentralized, protocol-heavy nature of Ethereum with the corporate, regulatory-heavy nature of Coinbase.

### **5.1 Ethereum: The Protocol Ontology**

For Ethereum, the "Base Nodes of Understanding" are technical constructs. The schema must capture the deterministic rules of the blockchain.  
**BAML Schema: Ethereum Protocol**

Code snippet

class EthereumProtocol {  
  consensus\_mechanism ConsensusType  
  execution\_layer ExecutionSpecs  
  consensus\_layer ConsensusSpecs  
  eips ImprovementProposal  
}

class ImprovementProposal {  
  eip\_number int  
  title string  
  status EIPStatus // Draft, Review, Final, Withdrawn  
  category string // Core, Networking, Interface, ERC  
  created\_date string  
}

enum ConsensusType {  
  ProofOfWork @description("Pre-Merge legacy mechanism")  
  ProofOfStake @description("Current Gasper mechanism")  
}

**Graph Modeling:**

* **Nodes:** EIP-1559, The Merge, Vitalik Buterin, Geth.  
* **Edges:** EIP-1559 \----\> FeeMechanism. The Merge \----\> ProofOfWork.

The agent scrapes ethereum.org and EIP repositories. Using dlt, it incrementally loads new EIPs. Graphiti allows the agent to visualize the dependency tree of EIPs (e.g., "Which EIPs does the upcoming Pectra upgrade depend on?").

### **5.2 Coinbase: The Corporate Ontology**

Coinbase represents the intersection of crypto and traditional finance (TradFi). The schema here focuses on products, custody, and regulatory status.  
**BAML Schema: Coinbase Corporate**

Code snippet

class CorporateEntity {  
  name string  
  ticker string? // COIN  
  licenses RegulatoryLicense  
  custody\_assets string  
  products ExchangeProduct  
}

class RegulatoryLicense {  
  jurisdiction string // e.g., "New York", "Singapore"  
  license\_type string // "BitLicense", "MPI"  
  issuing\_body string  
}

class ExchangeProduct {  
  name string // "Coinbase Prime", "Base"  
  target\_audience AudienceType // Retail, Institutional, Developer  
}

Comparative Insight:  
By maintaining these two distinct ontologies in the same Graphiti instance, the agent can draw powerful cross-domain insights. It can link Coinbase Base (a Corporate Product) to Ethereum L2 (a Protocol Concept) via an IS\_BUILT\_ON edge. This allows the agent to answer: "How does Coinbase's Base chain impact Ethereum's scalability roadmap?"

## ---

**6\. Domain Analysis II: Infrastructure (Cloudflare)**

Cloudflare is a massive, sprawling platform. The challenge here is **Product Hierarchy** and **Feature Velocity**. Cloudflare frequently renames products or bundles them differently (e.g., "Cloudflare Access" becoming part of "Zero Trust").

### **6.1 The Infrastructure Ontology**

We model Cloudflare as a graph of **Services**, **Runtimes**, and **Locations**.  
**BAML Schema: Cloudflare Infrastructure**

Code snippet

class CloudflareService {  
  product\_name string  
  category ServiceCategory // Compute, Storage, Network, Security  
  pricing\_model PricingModel  
  compatibility CompatibilityLayer  
}

class CompatibilityLayer {  
  runtime string // "Node.js", "Python", "Rust"  
  api\_standard string // "S3", "WinterCG"  
}

enum ServiceCategory {  
  Workers @description("Serverless Compute")  
  R2 @description("Object Storage")  
  DurableObjects @description("Stateful Compute")  
  ZeroTrust  
}

### **6.2 Deep Dive: R2 and Workers**

The agent scrapes the Cloudflare Developer Docs.

* **R2 Node:** Identified as Object Storage, S3 Compatible.  
* **Workers Node:** Identified as Serverless, V8 Isolate.  
* **Edge:** Workers \----\> R2.

User Experience in Analysis:  
A user asks: "Can I use Python in Cloudflare Workers?"  
The agent queries the mcp-graphiti server. It finds the Workers node and traverses the SUPPORTS\_LANGUAGE edges. It sees a temporal edge:

* Workers \----\> Python.  
  This allows the agent to give a nuanced answer: "Yes, Python support was added recently (Beta), unlike JavaScript which is native."

## ---

**7\. Domain Analysis III: UK Education System**

This domain differs significantly from the tech domains. It is characterized by **Rigid Hierarchies**, **Government Codes**, and **Geo-Spatial Data**.

### **7.1 The GIAS (Get Information About Schools) Ontology**

We ingest the "Get Information About Schools" register. This is a massive CSV/API dataset containing metadata for every school in the UK.  
**BAML Schema: Educational Institution**

Code snippet

class UKSchool {  
  urn string @description("Unique Reference Number")  
  la\_code string @description("Local Authority Code")  
  establishment\_name string  
  phase\_of\_education string // Primary, Secondary  
  type\_of\_establishment string // Academy, Maintained, Free School  
  trust\_name string? @description("Multi-Academy Trust Name if applicable")  
    
  census\_data CensusMetrics?  
}

class CensusMetrics {  
  total\_pupils int  
  fsm\_percentage float @description("Percentage eligible for Free School Meals")  
  sen\_percentage float @description("Percentage with Special Educational Needs")  
}

### **7.2 The OFSTED Inspection Ontology**

OFSTED reports are unstructured PDFs or HTML pages. This is where BAML shines. We define an extraction function to parse the qualitative judgments into quantitative data.

Code snippet

class InspectionReport {  
  inspection\_date string  
  publication\_date string  
  overall\_effectiveness OfstedRating  
  quality\_of\_education OfstedRating  
  safeguarding\_is\_effective boolean  
    
  key\_findings string @description("Bulleted list of main strengths/weaknesses")  
}

enum OfstedRating {  
  Outstanding  
  Good  
  RequiresImprovement  
  Inadequate  
}

### **7.3 Graph Modeling of Trusts**

A critical insight in UK education is the rise of **Multi-Academy Trusts (MATs)**. A MAT is a corporate entity that runs multiple schools.

* **Nodes:** School, Trust, LocalAuthority.  
* **Edges:** School\_A \----\> Trust\_X. School\_A \----\> Manchester.

The agent can perform "Network Analysis" via mcp-duckdb.

* *Query:* "Calculate the average OFSTED rating for all schools managed by 'United Learning Trust' vs. 'Ark Schools'."  
* *Mechanism:* The agent joins the School table with the Inspection table in DuckDB, grouping by trust\_name.

## ---

**8\. Domain Analysis IV: Software Development (Godot Engine)**

Godot represents a "Code-as-Data" domain. The documentation is a reflection of the underlying C++ class structure.

### **8.1 The Class Reference Ontology**

The "Base Nodes" here are the classes themselves.  
**BAML Schema: Godot API**

Code snippet

class GodotClass {  
  name string  
  inherits string?  
  category string // Core, 2D, 3D, UI  
  brief\_description string  
    
  signals SignalDef  
  methods MethodDef  
  properties PropertyDef  
}

class MethodDef {  
  name string  
  return\_type string  
  arguments ArgDef  
}

### **8.2 The Inheritance Graph**

Godot's power comes from its inheritance tree (Node \-\> CanvasItem \-\> Node2D \-\> Sprite2D).

* **Graphiti Modeling:** We explicitly model the INHERITS relationship.  
* **Semantic Search:** If a user asks "How do I move a sprite?", CocoIndex retrieves the Sprite2D docs. If the docs don't mention "move" explicitly (because the method position is inherited from Node2D), the Graphiti graph allows the agent to "walk up" the inheritance tree to find the relevant property in the parent class.

Comparative Synthesis:  
The agent can contrast Godot's node system with Unity's component system (if we were to add Unity later) by analyzing the density of the inheritance graph vs. composition edges.

## ---

**9\. Data Storage and Analytical Layer: DuckDB**

While Graphiti handles connections and CocoIndex handles semantics, **DuckDB** handles bulk analytics. It serves as the "Left Brain" of the agent—logical, statistical, and rigorous.

### **9.1 The Lakehouse Pattern with httpfs**

We do not load data *into* DuckDB in the traditional sense. Instead, we use DuckDB's httpfs extension to query the Parquet files sitting in R2 directly. This keeps the architecture stateless and incredibly cheap.  
**Layered Data Modeling in DuckDB:**

1. **Bronze Layer (View):** SELECT \* FROM read\_json\_auto('s3://base/extracted/godot/\*.json')  
   * Direct view over the BAML output.  
2. **Silver Layer (Table):** CREATE TABLE godot\_classes AS SELECT...  
   * Cleaned, typed, and deduplicated data.  
   * dlt manages the schema evolution of these tables.  
3. **Gold Layer (Aggregates):**  
   * avg\_methods\_per\_class: A pre-computed metric useful for complexity analysis.

### **9.2 MCP-DuckDB Integration**

The mcp-duckdb server exposes a query\_sql tool. The Agno agent uses this for high-level reasoning.

* *User Query:* "Is the complexity of Godot classes increasing?"  
* *Agent Action:* Generates SQL: SELECT version, AVG(len(methods)) FROM godot\_classes GROUP BY version.  
* *Result:* "Yes, the average method count rose from 12 in Godot 3.x to 15 in Godot 4.x."

## ---

**10\. Conclusion and Future Outlook**

This report outlines a rigorous technical architecture for an autonomous educational agent. By combining **Agno's** cognitive flexibility with **Dagster's** engineering rigor, we create a system that is both intelligent and reliable.  
The integration of **dlt** and **Cloudflare R2** solves the ingestion scale problem, while **BAML** addresses the fragility of structured extraction through dynamic schemas. The dual-indexing strategy of **CocoIndex** (Semantic) and **Graphiti** (Temporal) allows the agent to reason about the "what," "how," and "when" of knowledge.  
The application of this architecture to Ethereum, Cloudflare, UK Education, and Godot demonstrates its versatility. Whether parsing government policy codes or compiling game engine API references, the system maintains a coherent "Base Node" ontology that evolves with the domain.  
This is the future of agentic knowledge: not a static database, but a living, breathing organism of information, self-correcting and ever-expanding, designed to provide deep, verified insight to its users.

# ---

**Technical Appendix: Implementation Specifications**

## **A1. BAML Schemas for Core Domains**

### **A1.1 Godot Engine Schema**

Code snippet

class GodotClass {  
    name string @description("The class name, e.g., RigidBody3D")  
    inherits string? @description("Parent class name")  
    description string  
    version string @description("Godot version, e.g., 4.3")  
      
    signals GodotSignal  
    properties GodotProperty  
    methods GodotMethod  
}

class GodotSignal {  
    name string  
    arguments string  
}

class GodotProperty {  
    name string  
    type string  
    default\_value string?  
}

class GodotMethod {  
    name string  
    return\_type string  
    arguments MethodArg  
}

class MethodArg {  
    name string  
    type string  
}

function ExtractGodotClass(html: string) \-\> GodotClass {  
    client GPT4o  
    prompt \#"  
        Extract the Godot class definition from this HTML documentation.  
        Pay attention to the inheritance chain and signal definitions.  
          
        {{ html }}  
          
        {{ ctx.output\_format }}  
    "\#  
}

### **A1.2 UK Education (OFSTED & GIAS)**

Code snippet

class UKSchool {  
    urn string @description("Unique Reference Number")  
    name string  
    local\_authority string  
    phase string // Primary, Secondary, etc.  
    type string // Academy, Maintained  
    trust string?  
      
    inspection\_history Inspection  
    census CensusData?  
}

class Inspection {  
    date string  
    rating OfstedRating  
    report\_link string  
}

class CensusData {  
    total\_pupils int  
    fsm\_percent float  
    sen\_percent float  
}

enum OfstedRating {  
    Outstanding  
    Good  
    RequiresImprovement  
    Inadequate  
    NotGraded  
}

### **A1.3 Ethereum Protocol**

Code snippet

class EthereumConcept {  
    name string  
    type ConceptType // EIP, Upgrade, Client, Tool  
    description string  
      
    // For EIPs  
    eip\_number int?  
    status EIPStatus?  
    authors string  
      
    // For Upgrades  
    activation\_epoch int?  
    included\_eips int  
}

enum ConceptType {  
    EIP  
    NetworkUpgrade  
    ExecutionClient  
    ConsensusClient  
}

enum EIPStatus {  
    Draft  
    Review  
    LastCall  
    Final  
    Withdrawn  
}

## **A2. Dagster Asset Definition (Python)**

Python

from dagster import asset, AssetExecutionContext  
from dlt.sources.helpers import requests  
import dlt

@asset(group\_name="ingestion")  
def godot\_docs\_raw(context: AssetExecutionContext):  
    """  
    Incrementally scrapes Godot documentation.  
    """  
    pipeline \= dlt.pipeline(  
        pipeline\_name="godot\_docs",  
        destination="filesystem", \# R2  
        dataset\_name="godot\_raw",  
    )  
      
    @dlt.resource(write\_disposition="merge", primary\_key="url")  
    def godot\_scraper(last\_scraped=dlt.sources.incremental("last\_modified")):  
        \# Mocking the scraping logic  
        urls \= \["https://docs.godotengine.org/en/stable/classes/class\_node.html"\]  
        for url in urls:  
            \# check last\_modified header...  
            yield {  
                "url": url,  
                "html": "\<html\>...\</html\>",  
                "last\_modified": "2025-01-01"  
            }

    info \= pipeline.run(godot\_scraper)  
    context.log.info(info)

## **A3. Agno Agent with MCP Configuration**

Python

from agno.agent import Agent  
from agno.models.anthropic import Claude  
from agno.tools.mcp import MCPTools

\# MCP Configuration for our Knowledge Base  
knowledge\_mcp \= MCPTools(  
    transport="sse",  
    url="http://localhost:8000/sse",  
    name="knowledge\_base",  
    description="Access to DuckDB analytics and Graphiti knowledge graph."  
)

agent \= Agent(  
    name="EduAgent",  
    model=Claude(id="claude-3-5-sonnet"),  
    tools=\[knowledge\_mcp\],  
    instructions=,  
    markdown=True  
)

## **A4. CocoIndex Flow Configuration**

Python

from cocoindex import Flow, Source, Transform  
from cocoindex.sources import S3Source  
from cocoindex.embeddings import OpenAIEmbeddings

\# Connect to R2  
r2\_source \= S3Source(  
    bucket="edu-agent-data",  
    prefix="extracted/",  
    endpoint\_url="https://\<ACCOUNT\_ID\>.r2.cloudflarestorage.com"  
)

flow \= Flow(name="semantic\_indexer", source=r2\_source)

\# Transformation: Embed the 'description' or 'content' field  
flow.add\_step(Transform(  
    input="description",  
    output="vector",  
    fn=OpenAIEmbeddings(model="text-embedding-3-small")  
))

\# Result is automatically indexed by CocoIndex's vector engine

#### **Works cited**

1. Dagster & dlt (Pythonic), accessed December 16, 2025, [https://docs.dagster.io/integrations/libraries/dlt/dlt-pythonic](https://docs.dagster.io/integrations/libraries/dlt/dlt-pythonic)  
2. Deploy with Dagster | dlt Docs \- dltHub, accessed December 16, 2025, [https://dlthub.com/docs/walkthroughs/deploy-a-pipeline/deploy-with-dagster](https://dlthub.com/docs/walkthroughs/deploy-a-pipeline/deploy-with-dagster)  
3. Agno: The agent framework for Python teams \- WorkOS, accessed December 16, 2025, [https://workos.com/blog/agno-the-agent-framework-for-python-teams](https://workos.com/blog/agno-the-agent-framework-for-python-teams)  
4. Agno Framework: A Lightweight Library for Building Multimodal Agents \- Analytics Vidhya, accessed December 16, 2025, [https://www.analyticsvidhya.com/blog/2025/03/agno-framework/](https://www.analyticsvidhya.com/blog/2025/03/agno-framework/)  
5. MCP tools \- Agent Development Kit \- Google, accessed December 16, 2025, [https://google.github.io/adk-docs/tools-custom/mcp-tools/](https://google.github.io/adk-docs/tools-custom/mcp-tools/)  
6. Top 7 Frameworks to Add MCP to Your Agents (with Code) — 2025 Edition | by Vivek Raj, accessed December 16, 2025, [https://aws.plainenglish.io/top-7-frameworks-to-add-mcp-to-your-agents-with-code-2025-edition-6763f2465589](https://aws.plainenglish.io/top-7-frameworks-to-add-mcp-to-your-agents-with-code-2025-edition-6763f2465589)  
7. Graphiti MCP Server \- LobeHub, accessed December 16, 2025, [https://lobehub.com/mcp/getzep-graphiti-mcp-server](https://lobehub.com/mcp/getzep-graphiti-mcp-server)  
8. Graphiti MCP Server \- FalkorDB Docs, accessed December 16, 2025, [https://docs.falkordb.com/agentic-memory/graphiti-mcp-server.html](https://docs.falkordb.com/agentic-memory/graphiti-mcp-server.html)  
9. Incremental loading | dlt Docs \- dltHub, accessed December 16, 2025, [https://dlthub.com/docs/general-usage/incremental-loading](https://dlthub.com/docs/general-usage/incremental-loading)  
10. Cloud storage and filesystem | dlt Docs \- dltHub, accessed December 16, 2025, [https://dlthub.com/docs/dlt-ecosystem/destinations/filesystem](https://dlthub.com/docs/dlt-ecosystem/destinations/filesystem)  
11. Using dlt with Dagster, accessed December 16, 2025, [https://dagster.io/integrations/dagster-dlt](https://dagster.io/integrations/dagster-dlt)  
12. Boundary Documentation: Welcome, accessed December 16, 2025, [https://docs.boundaryml.com/home](https://docs.boundaryml.com/home)  
13. BoundaryML/baml: The AI framework that adds the engineering to prompt engineering (Python/TS/Ruby/Java/C\#/Rust/Go compatible) \- GitHub, accessed December 16, 2025, [https://github.com/BoundaryML/baml](https://github.com/BoundaryML/baml)  
14. Dynamic Types \- TypeBuilder | Boundary Documentation \- BAML, accessed December 16, 2025, [https://docs.boundaryml.com/guide/baml-advanced/dynamic-types](https://docs.boundaryml.com/guide/baml-advanced/dynamic-types)  
15. Prompting vs JSON Mode vs Function Calling vs Constrained Generation vs SAP \- BAML, accessed December 16, 2025, [https://boundaryml.com/blog/schema-aligned-parsing](https://boundaryml.com/blog/schema-aligned-parsing)  
16. Extracting Intake Forms with BAML and CocoIndex, accessed December 16, 2025, [https://cocoindex.io/blogs/extraction-baml](https://cocoindex.io/blogs/extraction-baml)  
17. Building Intelligent Codebase Indexing with CocoIndex: A Deep Dive into Semantic Code Search \- Medium, accessed December 16, 2025, [https://medium.com/@cocoindex.io/building-intelligent-codebase-indexing-with-cocoindex-a-deep-dive-into-semantic-code-search-e93ae28519c5](https://medium.com/@cocoindex.io/building-intelligent-codebase-indexing-with-cocoindex-a-deep-dive-into-semantic-code-search-e93ae28519c5)  
18. CocoIndex Changelog 2025-10-19, accessed December 16, 2025, [https://cocoindex.io/blogs/cocoindex-changelog-2025-10-19](https://cocoindex.io/blogs/cocoindex-changelog-2025-10-19)  
19. Graphiti \- FalkorDB Docs, accessed December 16, 2025, [https://docs.falkordb.com/agentic-memory/graphiti.html](https://docs.falkordb.com/agentic-memory/graphiti.html)  
20. Graphiti: Knowledge Graph Memory for an Agentic World \- Neo4j, accessed December 16, 2025, [https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)  
21. Cognee, accessed December 16, 2025, [https://www.cognee.ai/](https://www.cognee.ai/)  
22. Build a Knowledge Graph from a Python Repo: A Simple Guide \- Cognee, accessed December 16, 2025, [https://www.cognee.ai/blog/deep-dives/repo-to-knowledge-graph](https://www.cognee.ai/blog/deep-dives/repo-to-knowledge-graph)
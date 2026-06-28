# **Architectural Blueprint for Autonomous Reverse Engineering and Asset Reconstruction Systems: A Deep Research Report**

## **1\. Introduction: The Paradigm Shift to Agentic Analysis**

The field of software reverse engineering (SRE), specifically within the closed ecosystems of mobile gaming and proprietary game engines, is undergoing a foundational transformation. Historically, SRE has been a discipline defined by manual labor, requiring specialized human analysts to dissect compiled binaries, map hex dumps to logic, and painstakingly reconstruct asset pipelines. This process, while effective, is inherently unscalable and siloed. The emergence of large multimodal models (LMMs) with extended context windows, exemplified by Z.ai’s GLM-4.6, coupled with agentic orchestration frameworks like Agno (formerly Phidata) and structured data protocols like BAML, has enabled the creation of autonomous systems capable of semantically "understanding" both compiled code and dynamic gameplay simultaneously.  
This report outlines the architecture for a comprehensive **Deep Insight & Asset Reconstruction Engine (DIARE)**. This system is not merely an extraction tool; it is a cognitive engine designed to reverse-engineer the creative and logical intent behind a game. By synthesizing static analysis (decompiling.ipa files), dynamic analysis (gameplay video processing), and agentic reasoning, the proposed architecture transforms opaque binary artifacts into structured, manageable assets within a modern web ecosystem powered by TypeScript, React, and Storybook. The integration of the Model Context Protocol (MCP) ensures that disparate tools—from Ghidra and Frida to FFmpeg and UnityPy—operate as a unified, interoperable toolset for AI agents. This shift from "human-in-the-loop" to "agent-in-the-loop" workflows reserves human expertise for high-level architectural decisions while agents manage the granular complexity of asset extraction, classification, and visualization.1  
The implications of this architecture are profound. For game developers, it offers a path to automated legacy code recovery and asset migration. For security researchers, it provides a scalable method to detect vulnerabilities, unauthorized asset usage, or privacy violations in compiled applications. For content creators and archivists, it streamlines the analysis of game mechanics and visual styles, preserving digital history in a structured, accessible format. The following sections systematically deconstruct this architecture, moving from the foundational AI models and protocols to the specific mechanics of reverse-engineering game engines, and finally to the synthesis of a user-facing asset management dashboard powered by Generative UI.5

## **2\. The Cognitive Core: Z.ai GLM-4.6 and Multimodal Reasoning**

The cognitive core of the DIARE architecture is tasked with interpreting the multimodal data streams inherent to video games. Games are complex multimedia artifacts comprising visual feedback (pixels), logic (code), and narrative (text). Traditional reverse engineering tools address these modalities in isolation: a decompiler sees code, a video player sees pixels. To gain holistic insight, an agent must perceive the game as a human does—watching the screen while simultaneously understanding the underlying logic.

### **2.1 GLM-4.6 Capabilities in Code and Vision Contexts**

Z.ai’s GLM-4.6 model serves as the optimal backbone for this pipeline due to its specific architectural optimizations. Unlike generic Large Language Models (LLMs) that may struggle with the specialized syntax of decompiled code or the visual nuances of gameplay, GLM-4.6 integrates native Function Calling and multimodal understanding with a massive 128k token context window.1 In a reverse engineering context, this extended context length is critical. A single decompiled script, a complex shader file, or a hex dump of a game level can easily exceed the limits of smaller models. The ability to process approximately 150 pages of documentation or complex code in a single pass allows the agent to maintain "state awareness" across different files in a game's archive, linking a variable definition in one file to its usage in another without losing context.1  
Furthermore, GLM-4.6's "Visual Web Search" and analysis workflow capabilities can be effectively repurposed for "Visual Game Analysis." Instead of searching the web, the agent searches the frame buffer of a gameplay video. It can identify UI elements, character states, particle effects, and physics interactions visually, then correlate these observations with the decompiled code. For instance, if the visual agent detects a "Critical Hit" text appearing on the screen with a specific red color code, it can query the code analysis agent to locate the function responsible for rendering text with that specific hex color, effectively bridging the semantic gap between "what happens" (gameplay) and "how it happens" (code).1

### **2.2 The "Deep Research" Paradigm for Game Mechanics**

The system utilizes GLM-4.6’s "Deep Research" capabilities to perform iterative hypothesis testing, a process fundamental to reverse engineering. When a human engineer encounters an unknown file format—such as a custom .dat file in a Godot game or an encrypted asset bundle in Unity—they formulate a hypothesis (e.g., "this header looks like Zlib compression"), test it by writing a script, analyze the error, and iterate. GLM-4.6 can simulate this reasoning loop. By leveraging its "Thinking Mode" (similar to OpenAI's reasoning models but integrated into GLM-4.6's workflow), the model can outline a plan to decode the file format, generate a Python script to parse it, analyze the execution logs, and self-correct the script until the data is successfully extracted. This iterative, self-correcting behavior is essential for handling the obfuscation, custom encryption, and proprietary formats common in commercial iOS binaries.10  
The model's API compatibility with OpenAI standards further simplifies integration. Developers can utilize existing OpenAI SDKs to interface with Z.ai, changing only the base URL and API key. This allows the DIARE architecture to leverage the vast ecosystem of tools built for OpenAI while utilizing the specific strengths of GLM-4.6 in long-context understanding and multimodal function calling.12

## **3\. Orchestration Layer: Agno and the Agentic Workflow**

While GLM-4.6 provides the raw intelligence, the Agno framework (formerly Phidata) provides the nervous system that coordinates action. An "agent" in isolation is merely a text processor; an agent in Agno is a stateful entity with memory, tools, and a distinct role. For a task as complex as reverse engineering an entire iOS application, a monolithic agent approach is prone to failure due to context drift, hallucination, and the sheer volume of tasks. Instead, DIARE employs a **Multi-Agent System (MAS)** architecture managed by Agno, leveraging its ability to instantiate agents in microseconds and manage persistent state.2

### **3.1 The Agentic Hierarchy and Role Specialization**

The architecture defines a hierarchy of specialized agents, each encapsulating a specific domain of knowledge and a set of tools. This separation of concerns ensures that the context window of each agent remains focused on its specific task, reducing error rates.

| Agent Role | Responsibility | Tools (MCP/Python) | Contextual Focus |
| :---- | :---- | :---- | :---- |
| **The Overseer (Orchestrator)** | Manages the high-level goal (e.g., "Extract all assets from app.ipa"). Decomposes tasks, assigns them to sub-agents, and synthesizes final reports. | Workflow State Manager, User Interaction (AgUI) | Global Project State, User Intent |
| **The Cryptographer** | Handles decryption of the iOS binary (FairPlay) and entitlement analysis. Manages the interface with the jailbroken device environment. | Frida, Clutch, ldid, codesign, usbmuxd | Binary Headers, Entitlements, Encryption Keys |
| **The Archeologist (Extractor)** | Identifies the game engine (Unity/Unreal/Godot) via file signatures and selects the appropriate extraction strategy. | UnityPy, GodotPckTool, u4pak, file command | File Signatures, Archive Structures |
| **The Watcher (Visual Analyst)** | Analyzes gameplay video to identify mechanics, UI layouts, and asset usage context. Extracts UI sprites from video frames. | FFmpeg, OpenCV, GLM-4.6V | Video Frames, UI Taxonomy, OCR Data |
| **The Architect (Asset Manager)** | Structures extracted data into React components and Storybook stories. Uploads assets to the Headless DAM. | TypeScript Compiler, React Templates, File System | Design System Schema, Component Library |

Agno’s efficiency is paramount here. With agent instantiation times in the microseconds (\~3μs), the system can dynamically spin up thousands of micro-agents to handle individual files or frames without significant overhead. This allows for massive parallelism: while one sub-team of agents is analyzing the 3D models of a character using UnityPy, another can be processing gameplay video frames with FFmpeg, all coordinated by the Overseer using Agno’s "Team" structures.2

### **3.2 Memory, Persistence, and "Culture"**

Reverse engineering is inherently an accumulation of knowledge. An insight gained about a global variable in one script (e.g., \_playerHealth) must be available when analyzing a referencing script hours later. Agno’s built-in memory and knowledge layers (Agentic RAG) solve this problem. The "Culture" feature—shared long-term collective memory—allows agents to deposit findings (e.g., "Function 0x10045A is the health regen logic") into a vector database (like PgVector). Subsequent agents working on related tasks can query this collective knowledge base, preventing redundant analysis and ensuring consistency across the extraction process. This shared state is critical when correlating dynamic analysis (Frida logs) with static analysis (decompiled code).2

## **4\. The Connectivity Layer: Model Context Protocol (MCP)**

A major challenge in automated reverse engineering is the "N x M" integration problem: connecting N different AI models to M different, often obscure, command-line tools (CLIs). The Model Context Protocol (MCP) eliminates the need for custom glue code for every tool interaction. By wrapping standard reverse engineering utilities as MCP Servers, we provide a standardized interface that any MCP-compliant agent (like those built with Agno) can utilize. This standardizes the "hands" of the agent, allowing it to interact with the OS and external tools safely and predictably.15

### **4.1 Standardizing Tool Interaction via MCP**

In the DIARE architecture, every external interaction is mediated through MCP. This abstracts the complexity of the underlying OS and tool parameters from the agent's logic.

* **FileSystem MCP:** Instead of giving the agent raw shell access, which poses significant security risks, a scoped FileSystem MCP server restricts the agent to the project directory. The agent requests list\_files or read\_file, and the MCP server handles the safe execution, preventing accidental deletion of system files or access to unauthorized directories.16  
* **Decompiler MCP:** Tools like UnityPy or GodotPckTool are wrapped as Python-based MCP servers. The agent doesn't need to know the specific CLI arguments or Python syntax for UnityPy; it simply calls the extract\_assets(file\_path) tool exposed by the MCP server. The server translates this semantic request into the specific library calls required to unpack the Unity bundle. This decoupling means that if UnityPy updates its API, only the MCP server needs modification, not the agent's prompts.17  
* **FFmpeg MCP:** For video analysis, an FFmpeg MCP server provides tools like extract\_frames, detect\_scene\_change, or get\_audio\_track. This allows the "Watcher" agent to surgically manipulate video files without hallucinating complex, error-prone FFmpeg flags. The agent requests "extract frames every 5 seconds," and the MCP server executes the precise ffmpeg \-i video.mp4 \-vf fps=1/5 out%d.png command.20

## **5\. Structured Data Extraction: The Role of BAML**

One of the most pervasive failures in LLM pipelines is the generation of malformed structured data. When an agent is asked to "extract all character stats from this decompiled file," a standard prompt often results in inconsistent JSON, missing fields, or hallucinated data types. This is where BAML (Boundary Abstract Model Language) becomes a critical infrastructure component. BAML treats prompts as strictly typed functions, enforcing a schema on the LLM's output before it ever reaches the application logic.23

### **5.1 Defining Schemas for Game Assets**

In the context of game assets, the data structures are often complex and nested. A game character might have a structure involving base stats, current equipment, active buffs, and a 3D mesh reference. BAML allows us to define these structures explicitly using a TypeScript-like syntax that compiles into enforced prompts.

Code snippet

class GameStat {  
  name string  
  value float  
  is\_percentage bool  
}

class CharacterAsset {  
  id string  
  name string  
  mesh\_path string  
  texture\_paths string  
  base\_stats GameStat  
  engine\_type string  
}

function ExtractCharacterInfo(code\_snippet: string) \-\> CharacterAsset {  
  client "openai/gpt-4o" // or Z.ai GLM-4.6 compatible client  
  prompt \#"  
    Analyze the following code and extract the character definition.  
    {{ code\_snippet }}  
    {{ ctx.output\_format }}  
  "\#  
}

When the Agno agent invokes a tool to analyze a file, it doesn't just ask the LLM to "return JSON." It calls a compiled BAML function. BAML handles the prompt construction, parsing, and—crucially—correction. If the model returns a string for a float field, BAML's specialized parser attempts to fix it or raises a structured error, preventing the pipeline from crashing silently.25

### **5.2 Resilience to "Dirty" Data**

Reverse engineering inputs are notoriously "dirty." Decompiled code often contains mangled variable names (var\_a, func\_01), incomplete syntax, or binary artifacts. BAML is designed to be resilient to this. Its fuzzy parsing logic can extract valid partial objects even from noisy inputs, which is essential when the "Archeologist" agent is sifting through thousands of obfuscated files. This ensures that the downstream Asset Management system receives clean, type-safe data, regardless of the chaotic nature of the source material.27

## **6\. Phase 1: Ingestion and Static Analysis Pipeline**

The first operational phase of DIARE focuses on acquiring the raw materials: the game binary (.ipa) and its embedded assets. This phase requires overcoming iOS security measures and handling the proprietary formats of modern game engines.

### **6.1 iOS Decryption and IPA Extraction**

iOS applications are distributed in an encrypted .ipa format, protected by Apple's FairPlay DRM. Traditional static analysis on an encrypted binary yields nothing but entropy. The pipeline typically requires a jailbroken device or a specialized virtualization environment (like Corellium) where the app can be launched, decrypted in memory by the OS loader, and then dumped.  
The "Cryptographer" agent orchestrates this process via a **Frida**\-based toolchain. While traditional methods rely on manual usage of tools like Clutch or frida-ios-dump, the agentic approach wraps these into an automated workflow. The agent connects to the device (via usbmuxd), launches the target app, and injects a Frida payload to dump the decrypted Mach-O binary and repackage the IPA.28

* **Tool:** frida-tools (Python bindings) allows the agent to interact with the device programmatically. The agent uses frida-ps \-U to list processes and frida-trace to verify the app is running before initiating the dump.30  
* **Triage and Framework Analysis:** Once the decrypted IPA is obtained, the agent parses the Info.plist and binary headers to determine which frameworks are linked. This is a crucial "triage" step. If the agent detects UnityFramework.framework, it routes the task to the Unity extraction pipeline. If it sees libUE4.so or Unreal, it routes to the Unreal pipeline. If it detects libgodot.so, it routes to the Godot pipeline.28

### **6.2 The Engine Router: Unity, Godot, and Unreal**

Once the IPA structure is accessible, the "Archeologist" agent scans for signature files to identify the engine and selects the appropriate extraction strategy.

#### **6.2.1 Unity Asset Extraction**

Unity games pack assets into .assets files or AssetBundles. The standard tool for human engineers is AssetStudio, but for a headless agent, **UnityPy** is the superior choice. UnityPy is a Python library that allows for the reading, unpacking, and modification of Unity assets without the need for the Unity Editor.33

* **Workflow:** The agent uses a Python script wrapping UnityPy to iterate through all Data directories. It identifies objects of type Texture2D, Mesh, Shader, and TextAsset.  
* **Optimization with BAML:** Instead of blindly extracting everything, the agent uses BAML-defined criteria to filter assets. For example, "Extract only Texture2D objects larger than 1024x1024" or "Find all TextAssets containing the string 'HP'". This significantly reduces processing time and storage overhead.  
* **Conversion:** Unity meshes are proprietary. The agent uses UnityPy to export them as .obj or .gltf (GL Transmission Format), which is the standard for the web-based asset manager we will build later.33

#### **6.2.2 Godot Package Extraction**

Godot games typically bundle data into .pck files. The agent utilizes **GodotPckTool** (wrapped as a CLI tool in the MCP server) to unpack these archives. Since Godot resources (.tscn, .tres) are text-based (TOML-like), they are highly amenable to LLM analysis.

* **Insight:** The agent can read a .tscn (scene) file directly to understand the hierarchy of the game's UI or level design. BAML schemas can map the Godot node structure (e.g., Node2D, Sprite, AnimationPlayer) into a generic "Scene Graph" object that can be visualized in the frontend.35

#### **6.2.3 Unreal Engine Data**

Unreal uses .pak files. The agent employs tools like u4pak or PyPAKParser to unpack these.37 Unreal's assets (.uasset) are binary and notoriously difficult to parse without the specific engine version's serialization code. Here, the agent might rely on string extraction (using the strings command via FileSystem MCP) to find referencing paths and names, rather than full binary reconstruction, unless a specialized tool like UModel can be scripted to run headlessly.39

## **7\. Phase 2: Dynamic Analysis and Gameplay Insight**

Static analysis provides the *what* (the assets), but dynamic analysis provides the *how* (the behavior). This phase involves the "Watcher" agent analyzing gameplay recordings to extract mechanics, UI flows, and contextual usage of the assets found in Phase 1\.

### **7.1 Computer Vision for Gameplay Telemetry**

The agent utilizes **GLM-4.6V** to watch video files. Unlike simple object detection, this model performs semantic reasoning over time.

* **UI Decomposition:** The agent identifies HUD elements (Health Bars, Ammo Counters, Minimaps). By comparing these visual elements with the Texture2D assets extracted in Phase 1, the agent can link a specific image file (e.g., sprite\_atlas\_04.png) to its in-game function ("Player Health Bar Background").40  
* **Event Log Extraction:** Using BAML schemas, the agent watches the video and generates a structured log of events: \`\`. This effectively reverse-engineers the analytics stream the developers might have used.42

### **7.2 Agent-Driven Frida Instrumentation**

To deepen the analysis, the agent can actively probe the running game using Frida. This is a "Grey Box" approach. The visual agent sees an event (e.g., "Score increased"), and the orchestration agent instructs the "Cryptographer" to scan memory for values that changed simultaneously.

* **Automated Hooking:** The agent can write and inject Frida scripts (JavaScript/Python) to hook functions found during static analysis. For instance, if the static analysis identifies a function named updateScore(int), the agent injects a hook to log the arguments every time it is called.  
* **Correlation:** By correlating the video timestamp with the Frida log timestamp, the system confirms the function's purpose. This creates a feedback loop: Static Analysis suggests a target, Dynamic Analysis validates it, and Visual Analysis provides the context.30

## **8\. Phase 3: The Headless Asset Management Ecosystem**

The data generated by the extraction phases—thousands of 3D models, textures, audio files, and metadata records—must be organized. A traditional file folder is insufficient. We require a **Headless Digital Asset Management (DAM)** system that integrates with modern frontend workflows.

### **8.1 The Headless DAM Concept**

A headless DAM decouples the storage and management logic from the presentation layer. For this architecture, tools like **Mudstack** or **Echo3D** are exemplary. They offer robust APIs for pushing and pulling 3D assets, version control for large binaries, and automated optimization (e.g., compressing textures or converting model formats).45

* **Role of Agno Agent:** The "Architect" agent acts as the API client for the DAM. It uploads the extracted GLB files to Echo3D or Mudstack via their SDKs. It attaches metadata extracted via BAML (e.g., character\_class: "Warrior", poly\_count: 4500\) as tags to the asset in the DAM.  
* **Optimization:** These platforms often include server-side processing. When the agent uploads a high-res raw texture extracted from the IPA, the DAM can automatically generate web-optimized thumbnails and compressed versions for the UI.45

### **8.2 The Frontend Stack: React, TypeScript, and R3F**

To visualize these assets, the system employs a modern React stack. This is where the "Reverse Engineering" output transforms into a "Game Development" input.

* **React Three Fiber (R3F):** This library allows for the rendering of 3D content within the React ecosystem using declarative components. The extracted GLTF/GLB models are loaded into the browser canvas using R3F's useLoader and GLTFLoader. This enables the user to rotate, zoom, and inspect the reverse-engineered models directly in the web dashboard.49  
* **Storybook Integration:** Storybook is the standard for UI component development. In this pipeline, it serves as the "Catalog" for the extracted assets. The agent can automatically generate .stories.tsx files for each extracted asset.  
  * *Example:* For a character model Hero.glb, the agent generates a Hero.stories.tsx file that imports the model and renders it within an R3F Canvas in Storybook. This creates an interactive, searchable library of every asset in the game, accessible to designers and developers without needing to open Unity or a hex editor.52

## **9\. Phase 4: The Agent-User Interaction (AgUI) Layer**

The final bridge is the interface between the human operator and the agent swarm. **AgUI (Agent-User Interaction)** protocols standardize how the agent presents its findings. Instead of dumping text into a chat window, the agent utilizes **Generative UI** to build custom interfaces on the fly.5

### **9.1 Generative UI Components**

When the user asks, "Show me all the weapons extracted from the binary," the agent doesn't just list filenames. It constructs a JSON payload describing a UI component—a grid of cards, each containing a 3D preview (via R3F), the weapon's stats (extracted via BAML), and a download link. The frontend, utilizing AgUI libraries, renders this specification into a functional React component.56

### **9.2 Human-in-the-Loop Validation**

Reverse engineering is probabilistic. The agent might misclassify a "Staff" as a "Sword." AgUI facilitates Human-in-the-Loop (HITL) workflows. The agent can present a "Confidence Score" alongside its classification. If the confidence is low, it renders a UI element asking the user to confirm or correct the tag. This feedback is fed back into the agent's memory (Agno's knowledge base), improving future classifications.2

## **10\. Technical Implementation Guide: A Narrative Walkthrough**

### **10.1 Setting Up the Agno Agent Ecosystem**

The implementation begins with defining the Agno framework as the central nervous system. We define a ReverseEngineeringAgent that utilizes MCPTools to communicate with our specialized sub-systems.

Python

from agno.agent import Agent  
from agno.models.z\_ai import GLM4\_6 \# Adapter for Z.ai compatible API  
from agno.tools.mcp import MCPTools  
from agno.knowledge import AgentKnowledge  
from agno.vectordb.pgvector import PgVector

\# 1\. Define Knowledge Base for Asset Context  
knowledge\_base \= AgentKnowledge(  
    vector\_db=PgVector(  
        table\_name="game\_assets",  
        db\_url="postgresql+psycopg://user:pass@localhost:5432/assets\_db"  
    )  
)

\# 2\. Configure MCP Tools for External CLIs  
\# We assume local MCP servers running for FileSystem and our Custom Decompiler  
decompiler\_mcp \= MCPTools(  
    name="decompiler\_tools",  
    transport="stdio",  
    command="python",  
    args=\["mcp\_servers/decompiler\_server.py"\]  
)

ffmpeg\_mcp \= MCPTools(  
    name="video\_tools",  
    transport="stdio",  
    command="npx",  
    args=\["-y", "ffmpeg-mcp"\]  
)

\# 3\. Initialize the Orchestrator Agent  
overseer\_agent \= Agent(  
    name="Overseer",  
    model=GLM4\_6(api\_key="z-ai-key", id="glm-4.6"),  
    tools=\[decompiler\_mcp, ffmpeg\_mcp\],  
    knowledge=knowledge\_base,  
    instructions=,  
    show\_tool\_calls=True,  
    markdown=True  
)

Ref: 2

### **10.2 Building the Custom MCP Decompiler Server**

To bridge the gap between the agent and tools like UnityPy, we create a custom MCP server. This server exposes functions that the LLM can call directly.

Python

\# mcp\_servers/decompiler\_server.py  
from mcp.server.fastmcp import FastMCP  
import UnityPy  
import os

mcp \= FastMCP("UnityExtractor")

@mcp.tool()  
def extract\_unity\_assets(file\_path: str, output\_dir: str) \-\> str:  
    """  
    Extracts Texture2D and Mesh assets from a Unity AssetBundle or.assets file.  
    Args:  
        file\_path: Absolute path to the unity file.  
        output\_dir: Directory to save extracted files.  
    """  
    if not os.path.exists(output\_dir):  
        os.makedirs(output\_dir)  
      
    extracted\_count \= 0  
    env \= UnityPy.load(file\_path)  
      
    for obj in env.objects:  
        \# Extract Textures  
        if obj.type.name \== "Texture2D":  
            data \= obj.read()  
            dest \= os.path.join(output\_dir, f"{data.name}.png")  
            data.image.save(dest)  
            extracted\_count \+= 1  
              
        \# Extract Meshes (Conceptual \- requires obj conversion logic)  
        elif obj.type.name \== "Mesh":  
            \# Logic to export mesh to.obj via UnityPy  
            pass

    return f"Successfully extracted {extracted\_count} assets to {output\_dir}"

if \_\_name\_\_ \== "\_\_main\_\_":  
    mcp.run()

This Python script uses the mcp SDK to turn the extract\_unity\_assets function into a tool callable by the Agno agent. The agent doesn't need to know how to use UnityPy; it just knows it has a tool to "Extract Unity Assets".17

### **10.3 Visualizing with React, Storybook, and R3F**

The extracted assets require visualization. We use a React application integrated with Storybook to serve as our "Asset Browser."  
Step 1: The R3F Viewer Component  
We create a generic viewer for the .gltf/.glb files extracted from the game.

JavaScript

// src/components/ModelViewer.tsx  
import React, { Suspense } from 'react';  
import { Canvas } from '@react-three/fiber';  
import { OrbitControls, useGLTF, Stage } from '@react-three/drei';

function Model({ url }: { url: string }) {  
  const { scene } \= useGLTF(url);  
  return \<primitive object={scene} /\>;  
}

export const ModelViewer \= ({ modelUrl }: { modelUrl: string }) \=\> {  
  return (  
    \<div style={{ height: '500px', width: '100%' }}\>  
      \<Canvas shadows dpr={} camera={{ fov: 50 }}\>  
        \<Suspense fallback={null}\>  
          \<Stage environment="city" intensity={0.6}\>  
            \<Model url={modelUrl} /\>  
          \</Stage\>  
        \</Suspense\>  
        \<OrbitControls autoRotate /\>  
      \</Canvas\>  
    \</div\>  
  );  
};

Ref: 34  
Step 2: Automating Story Generation  
The Agno agent, upon successfully extracting and converting a model (e.g., Hero.glb), can physically write a new Storybook file to the frontend project using the FileSystem MCP.

JavaScript

// Generated by Agno Agent: src/stories/Hero.stories.tsx  
import React from 'react';  
import { ComponentStory, ComponentMeta } from '@storybook/react';  
import { ModelViewer } from '../components/ModelViewer';

export default {  
  title: 'GameAssets/Characters/Hero',  
  component: ModelViewer,  
} as ComponentMeta\<typeof ModelViewer\>;

const Template: ComponentStory\<typeof ModelViewer\> \= (args) \=\> \<ModelViewer {...args} /\>;

export const Default \= Template.bind({});  
Default.args \= {  
  modelUrl: '/assets/models/Hero.glb', // Path to extracted asset  
};

This closes the loop: Extraction \-\> Conversion \-\> Component Generation \-\> Visualization. The user simply opens Storybook and sees the new assets appear in the sidebar.52

## **11\. Technical Considerations and Workflow Integration**

Developing this pipeline requires careful consideration of the disparate technologies involved.

### **11.1 Environment Isolation**

The extraction tools (Frida, UnityPy) often require specific Python versions or system-level dependencies (like usbmuxd). To manage this, the MCP servers should be containerized (Docker). The Agno agents communicate with these containers over HTTP or stdio, keeping the main orchestration environment clean and stable.2

### **11.2 Token Economics and Cost Management**

Analyzing an entire game involves processing millions of tokens.

* **Optimization:** BAML helps reduce token usage by stripping unnecessary context and enforcing concise outputs.25  
* **Routing:** The "Overseer" agent should use smaller, faster models (like GLM-4.6-Flash or local models) for trivial tasks (e.g., file sorting) and reserve the heavy GLM-4.6 (100B+) models for complex logic analysis or decompilation.8

### **11.3 Legal and Ethical Boundaries**

It is imperative to note that reverse engineering proprietary assets sits in a legal grey area. This architecture is powerful—potentially too powerful. Use of such a pipeline must strictly adhere to interoperability laws (like the DMCA exemptions for interoperability in the US) and the Terms of Service of the target applications. The system is best deployed for internal asset recovery, security auditing, or academic analysis rather than commercial cloning.

## **12\. Conclusion: The Future of Autonomous Insight**

The DIARE architecture represents a quantum leap in reverse engineering. By fusing the raw analytical power of tools like UnityPy and Frida with the cognitive reasoning of GLM-4.6 and the structured orchestration of Agno and BAML, we move from manual "digging" to automated "archeology." The resulting system does not just dump files; it reconstructs context, preserves meaning, and presents the "soul" of the software in a modern, interactive Storybook dashboard. This is the future of asset management: intelligent, autonomous, and deeply integrated.

#### **Works cited**

1. GLM-4.6V: Open Source Multimodal Models with Native Tool Use \- Z.ai Chat, accessed December 16, 2025, [https://z.ai/blog/glm-4.6v](https://z.ai/blog/glm-4.6v)  
2. agno-agi/agno: The unified stack for multi-agent systems. \- GitHub, accessed December 16, 2025, [https://github.com/agno-agi/agno](https://github.com/agno-agi/agno)  
3. Build a Python MCP Client to Test Servers From Your Terminal, accessed December 16, 2025, [https://realpython.com/python-mcp-client/](https://realpython.com/python-mcp-client/)  
4. Agno Framework: A Lightweight Library for Building Multimodal Agents \- Analytics Vidhya, accessed December 16, 2025, [https://www.analyticsvidhya.com/blog/2025/03/agno-framework/](https://www.analyticsvidhya.com/blog/2025/03/agno-framework/)  
5. AG-UI Overview \- Agent User Interaction Protocol, accessed December 16, 2025, [https://docs.ag-ui.com/introduction](https://docs.ag-ui.com/introduction)  
6. QIAGEN Ingenuity Pathway Analysis (IPA), accessed December 16, 2025, [https://digitalinsights.qiagen.com/products-overview/discovery-insights-portfolio/analysis-and-visualization/qiagen-ipa/](https://digitalinsights.qiagen.com/products-overview/discovery-insights-portfolio/analysis-and-visualization/qiagen-ipa/)  
7. Leveraging LLM Agents for Automated Video Game Testing \- arXiv, accessed December 16, 2025, [https://arxiv.org/html/2509.22170v1](https://arxiv.org/html/2509.22170v1)  
8. zai-org/GLM-4.6V \- Hugging Face, accessed December 16, 2025, [https://huggingface.co/zai-org/GLM-4.6V](https://huggingface.co/zai-org/GLM-4.6V)  
9. GLM-4.6V \- Z.AI DEVELOPER DOCUMENT, accessed December 16, 2025, [https://docs.z.ai/guides/vlm/glm-4.6v](https://docs.z.ai/guides/vlm/glm-4.6v)  
10. GLM-4.6 \- Z.AI DEVELOPER DOCUMENT, accessed December 16, 2025, [https://docs.z.ai/guides/llm/glm-4.6](https://docs.z.ai/guides/llm/glm-4.6)  
11. GLM-4.5 \- Z.AI DEVELOPER DOCUMENT, accessed December 16, 2025, [https://docs.z.ai/guides/llm/glm-4.5](https://docs.z.ai/guides/llm/glm-4.5)  
12. accessed December 16, 2025, [https://docs.z.ai/guides/develop/openai/python\#:\~:text=Z.AI%20provides%20interfaces%20compatible,API%20key%20and%20base%20URL.](https://docs.z.ai/guides/develop/openai/python#:~:text=Z.AI%20provides%20interfaces%20compatible,API%20key%20and%20base%20URL.)  
13. OpenAI Python SDK \- Z.AI DEVELOPER DOCUMENT, accessed December 16, 2025, [https://docs.z.ai/guides/develop/openai/python](https://docs.z.ai/guides/develop/openai/python)  
14. Agno: The agent framework for Python teams \- WorkOS, accessed December 16, 2025, [https://workos.com/blog/agno-the-agent-framework-for-python-teams](https://workos.com/blog/agno-the-agent-framework-for-python-teams)  
15. Model Context Protocol (MCP). MCP is an open protocol that… | by Aserdargun | Nov, 2025, accessed December 16, 2025, [https://medium.com/@aserdargun/model-context-protocol-mcp-e453b47cf254](https://medium.com/@aserdargun/model-context-protocol-mcp-e453b47cf254)  
16. What is Model Context Protocol (MCP)? A guide \- Google Cloud, accessed December 16, 2025, [https://cloud.google.com/discover/what-is-model-context-protocol](https://cloud.google.com/discover/what-is-model-context-protocol)  
17. The official Python SDK for Model Context Protocol servers and clients \- GitHub, accessed December 16, 2025, [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)  
18. MCP tools \- Agent Development Kit \- Google, accessed December 16, 2025, [https://google.github.io/adk-docs/tools-custom/mcp-tools/](https://google.github.io/adk-docs/tools-custom/mcp-tools/)  
19. Model Context Protocol (MCP): A comprehensive introduction for developers \- Stytch, accessed December 16, 2025, [https://stytch.com/blog/model-context-protocol-introduction/](https://stytch.com/blog/model-context-protocol-introduction/)  
20. ffmpeg-mcp \- An MCP tool based on FFmpeg command line, supporting video search, cropping, splicing, and playback, accessed December 16, 2025, [https://mcp.aibase.com/server/1916343659848769537](https://mcp.aibase.com/server/1916343659848769537)  
21. The Ultimate Guide to the Video Editor (FFMpeg) MCP Server by Kush Agrawal \- Skywork.ai, accessed December 16, 2025, [https://skywork.ai/skypage/en/ultimate-guide-video-editor-ffmpeg/1979070038955118592](https://skywork.ai/skypage/en/ultimate-guide-video-editor-ffmpeg/1979070038955118592)  
22. ffmpeg-mcp | MCP Servers \- LobeHub, accessed December 16, 2025, [https://lobehub.com/mcp/yubraaj11-ffmpeg-mcp](https://lobehub.com/mcp/yubraaj11-ffmpeg-mcp)  
23. Extracting Intake Forms with BAML and CocoIndex, accessed December 16, 2025, [https://cocoindex.io/blogs/extraction-baml](https://cocoindex.io/blogs/extraction-baml)  
24. Action Item Extraction | Boundary Documentation, accessed December 16, 2025, [https://docs.boundaryml.com/examples/prompt-engineering/action-item-extraction](https://docs.boundaryml.com/examples/prompt-engineering/action-item-extraction)  
25. Seven Features That Make BAML Ideal for AI Developers \- Gradient Flow, accessed December 16, 2025, [https://gradientflow.com/seven-features-that-make-baml-ideal-for-ai-developers/](https://gradientflow.com/seven-features-that-make-baml-ideal-for-ai-developers/)  
26. Get structured output from a Language Model using BAML | Thomas Queste, accessed December 16, 2025, [https://www.tomsquest.com/blog/2024/08/get-structured-output-from-llm-using-baml/](https://www.tomsquest.com/blog/2024/08/get-structured-output-from-llm-using-baml/)  
27. Every Way To Get Structured Output From LLMs | BAML Blog, accessed December 16, 2025, [https://boundaryml.com/blog/structured-output-from-llms](https://boundaryml.com/blog/structured-output-from-llms)  
28. GhidraEnjoyr/iOS-Reverse-Engineering \- GitHub, accessed December 16, 2025, [https://github.com/GhidraEnjoyr/iOS-Reverse-Engineering](https://github.com/GhidraEnjoyr/iOS-Reverse-Engineering)  
29. Reverse engineering macOS/iOS/iPadOS \- GitHub Gist, accessed December 16, 2025, [https://gist.github.com/programming086/0b53cde2686bca7767332ed25b4a26ec](https://gist.github.com/programming086/0b53cde2686bca7767332ed25b4a26ec)  
30. Frida • A world-class dynamic instrumentation toolkit | Observe and reprogram running programs on Windows, macOS, GNU/Linux, iOS, watchOS, tvOS, Android, FreeBSD, and QNX, accessed December 16, 2025, [https://frida.re/](https://frida.re/)  
31. iOS | Frida • A world-class dynamic instrumentation toolkit, accessed December 16, 2025, [https://frida.re/docs/ios/](https://frida.re/docs/ios/)  
32. How to Reverse Engineer an iOS App: Tips and Tools \- Apriorit, accessed December 16, 2025, [https://www.apriorit.com/dev-blog/how-to-reverse-engineer-an-ios-app](https://www.apriorit.com/dev-blog/how-to-reverse-engineer-an-ios-app)  
33. UnityPy is python module that makes it possible to extract/unpack and edit Unity assets \- GitHub, accessed December 16, 2025, [https://github.com/K0lb3/UnityPy](https://github.com/K0lb3/UnityPy)  
34. Configure 3D models with react-three-fiber \- LogRocket Blog, accessed December 16, 2025, [https://blog.logrocket.com/configure-3d-models-react-three-fiber/](https://blog.logrocket.com/configure-3d-models-react-three-fiber/)  
35. hhyyrylainen/GodotPckTool: Standalone tool for extracting and creating Godot .pck files \- GitHub, accessed December 16, 2025, [https://github.com/hhyyrylainen/GodotPckTool](https://github.com/hhyyrylainen/GodotPckTool)  
36. tehskai/godot-unpacker \- GitHub, accessed December 16, 2025, [https://github.com/tehskai/godot-unpacker](https://github.com/tehskai/godot-unpacker)  
37. panzi/u4pak: unpack, pack, list, check and mount Unreal Engine 4 .pak archives \- GitHub, accessed December 16, 2025, [https://github.com/panzi/u4pak](https://github.com/panzi/u4pak)  
38. PyPAKParser \- PyPI, accessed December 16, 2025, [https://pypi.org/project/PyPAKParser/](https://pypi.org/project/PyPAKParser/)  
39. Extracting and Packing: Basic Tools Usage | PW Modding Wiki, accessed December 16, 2025, [https://modding.pw/guides/basic-tools-usage](https://modding.pw/guides/basic-tools-usage)  
40. Instance Segmentation Method of User Interface Component of Games \- MDPI, accessed December 16, 2025, [https://www.mdpi.com/2076-3417/10/18/6502](https://www.mdpi.com/2076-3417/10/18/6502)  
41. Extracting Machine Learning Training Data from Video Games – UI element analysis for model training preparation \- Mikołak, accessed December 16, 2025, [https://xn--mikoak-6db.net/blog/2024/blog-extracting-data-2-ui-element-analysis.html](https://xn--mikoak-6db.net/blog/2024/blog-extracting-data-2-ui-element-analysis.html)  
42. \[1809.06201\] Player Experience Extraction from Gameplay Video \- arXiv, accessed December 16, 2025, [https://arxiv.org/abs/1809.06201](https://arxiv.org/abs/1809.06201)  
43. Player Experience Extraction from Gameplay Video | Proceedings of the AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment, accessed December 16, 2025, [https://ojs.aaai.org/index.php/AIIDE/article/view/13024](https://ojs.aaai.org/index.php/AIIDE/article/view/13024)  
44. MASTG-TOOL-0039: Frida for iOS \- OWASP Mobile Application Security, accessed December 16, 2025, [https://mas.owasp.org/MASTG/tools/ios/MASTG-TOOL-0039/](https://mas.owasp.org/MASTG/tools/ios/MASTG-TOOL-0039/)  
45. echo3D | 3D Digital Asset Management for Enterprises, accessed December 16, 2025, [https://www.echo3d.com/](https://www.echo3d.com/)  
46. Mudstack for AEC, accessed December 16, 2025, [https://mudstack.com/aec](https://mudstack.com/aec)  
47. Digital Asset Management \- Mudstack, accessed December 16, 2025, [https://mudstack.com/digital-asset-management](https://mudstack.com/digital-asset-management)  
48. Mudstack API: Getting Started, accessed December 16, 2025, [https://docs.mudstack.com/api-reference/getting-started](https://docs.mudstack.com/api-reference/getting-started)  
49. Scaling performance \- React Three Fiber, accessed December 16, 2025, [https://r3f.docs.pmnd.rs/advanced/scaling-performance](https://r3f.docs.pmnd.rs/advanced/scaling-performance)  
50. Loading assets in React Three Fiber \- Zero to Hero \- Aaron Claes, accessed December 16, 2025, [https://aaronclaes.be/blogs/react-three-fiber/loading-assets](https://aaronclaes.be/blogs/react-three-fiber/loading-assets)  
51. Loading Models \- React Three Fiber \- Poimandres, accessed December 16, 2025, [https://r3f.docs.pmnd.rs/tutorials/loading-models](https://r3f.docs.pmnd.rs/tutorials/loading-models)  
52. Pmndrs drei | Showcase \- Storybook, accessed December 16, 2025, [https://storybook.js.org/showcase/pmndrs-drei/](https://storybook.js.org/showcase/pmndrs-drei/)  
53. Manage React Three Fiber components with Storybook | by tatsuya shitomi \- Medium, accessed December 16, 2025, [https://medium.com/@t\_shi/manage-react-three-fiber-components-with-storybook-f4c06ee8ce44](https://medium.com/@t_shi/manage-react-three-fiber-components-with-storybook-f4c06ee8ce44)  
54. AG-UI Integration with Agent Framework \- Microsoft Learn, accessed December 16, 2025, [https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/](https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/)  
55. AG-UI: the Agent-User Interaction Protocol. Bring Agents into Frontend Applications. \- GitHub, accessed December 16, 2025, [https://github.com/ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui)  
56. Generative UI: Understanding Agent-Powered Interfaces | CopilotKit, accessed December 16, 2025, [https://www.copilotkit.ai/generative-ui](https://www.copilotkit.ai/generative-ui)  
57. Agent-Generated UI | ONE Platform \- one.ie, accessed December 16, 2025, [https://one.ie/connections/agui/](https://one.ie/connections/agui/)  
58. Create a Local AgentOS with Agno in Under 30 Lines of Python Code \- Tinz Twins Hub, accessed December 16, 2025, [https://tinztwinshub.com/software-engineering/create-an-agent-os-with-agno/](https://tinztwinshub.com/software-engineering/create-an-agent-os-with-agno/)  
59. Z.ai releases GLM-4.6V: A 9B "Flash" model that beats Qwen2-VL-8B,128k context and completely FREE via API. : r/singularity \- Reddit, accessed December 16, 2025, [https://www.reddit.com/r/singularity/comments/1phcju3/zai\_releases\_glm46v\_a\_9b\_flash\_model\_that\_beats/](https://www.reddit.com/r/singularity/comments/1phcju3/zai_releases_glm46v_a_9b_flash_model_that_beats/)
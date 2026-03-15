Fine-Tuning Plan for Crypto Domain Models

Part A: Data Type Compatibility by Model

Each target model has different capabilities and input expectations. Below we map suitable data types

for fine-tuning each model, and how to preprocess those data for effective training:

Qwen3-VL (Vision-Language Model)

•

Structured Data (APIs, On-Chain): Partially appropriate. Qwen3-VL’s strength is multi-modal

understanding, so purely numeric or structured data (like JSON from CoinGecko or DeFiLlama)

isn’t a natural fit unless transformed. One approach is to convert structured data to textual or

visual form. For example, you can turn API responses into descriptive text (“The BTC price is

$34,000, up 5% today.”) or plot the data into charts/images and use those images as input. If

using text conversion, ensure it’s in a natural language format, since Qwen3-VL can be fine-

tuned on text alone as well. However, the model won’t inherently perform numeric calculations;

any structured numeric info should be contextualized in text.

•

Unstructured Text (Reports, Proposals): Yes – appropriate. Qwen3-VL can be fine-tuned on plain

text data (research papers, governance forum posts, etc.) similar to a regular LLM. This can

improve its domain knowledge. Preprocessing involves text extraction and cleaning (e.g. OCR

PDFs, remove formatting). Because Qwen3-VL is an Instruct model, formatting the fine-tuning

data in an instruction-response style can help (e.g. prompt with a question from a report and the

model’s answer). You can fine-tune purely on text if needed, but note that Qwen3-VL is a heavier

model than a text-only LLM if you’re not leveraging its vision capabilities.

•

Visual Data (Dashboards, Screenshots): Yes – highly appropriate. As a vision-language model,

Qwen3-VL is designed to intake images alongside text. Fine-tuning on screenshots of crypto

dashboards (e.g. Aave UI, Ethena charts) paired with explanatory text or Q&A is ideal.

Preprocessing: you’ll need image–text pairs. Prepare a dataset where each entry contains an

image (e.g. a PNG screenshot) and an associated text (like a caption, description, or question-

answer about the image). Ensure images are normalized (e.g. resized consistently) and possibly

downsampled to reduce memory use. Qwen3-VL’s training process will involve feeding the image

through its visual encoder and the text through the language model, so the fine-tuning data

might be formatted as special tokens plus text. (In Unsloth’s framework, for example, you use a

command to load images during training.) By fine-tuning with such data, Qwen3-VL can learn to

interpret new visual layouts or dashboards. Note: Qwen3-VL can even be extended to video

frames or object detection tasks with advanced fine-tuning, though that requires specialized

data and is beyond typical use cases.

GPT-OSS (Open-Source GPT by OpenAI)

•

Structured Data (APIs, On-Chain): Yes, with text formatting. GPT-OSS is a pure text generative

model (20B or 120B parameters), so it cannot ingest raw structured data directly. To fine-tune on

structured crypto data (prices, blockchain metrics), represent the data as text in the training

prompts. For example, you might feed tabular data as CSV-like text, or embed JSON in a

markdown code block within a prompt, and train GPT-OSS to interpret it. Another approach is to

augment prompts with summaries of structured data (e.g. “BTC price: $34k, 24h change:

+5%. ETH TVL: 20M…” followed by a question). Preprocess by flattening API JSON to key-value

1

lines or creating natural language statements. While GPT-OSS can handle numeric information in

text form, keep prompts reasonable in length or use its extended context for large data dumps.

If extremely large structured inputs are needed, GPT-OSS’s 128k token context may handle it, but

fine-tuning on very long sequences will require substantial GPU memory.

•

Unstructured Text (Reports, Proposals): Yes – ideal. GPT-OSS excels at language tasks, making

it well-suited for fine-tuning on research reports, whitepapers, forum discussions, etc.

Preprocessing involves standard NLP cleaning: remove irrelevant metadata, split long

documents into chunks (within the model’s context size), and possibly format as instruction-

response if doing supervised fine-tuning. For example, you can take a governance proposal and

form a Q&A pair or an instruction (“Summarize this proposal”) with a reference summary as the

target output. Because GPT-OSS is an instruction-tuned chat model, it’s beneficial to present

fine-tuning data in a conversational format (e.g. user message and assistant answer) to align

with its pretraining style. OpenAI’s Harmony format or a ChatML/ShareGPT format can be used

for multi-turn data. Ensure the text is tokenized properly (GPT-OSS uses a GPT-3.5/4-like

tokenizer; Unsloth provides tools for this).

•

Visual Data: Not applicable. GPT-OSS has no built-in vision component, so it cannot take images

as input. You should not fine-tune GPT-OSS on images. If you need to handle visual data, you’d

either convert images to text (e.g. via OCR or by providing image descriptions as input text) or

choose a multi-modal model. In summary, GPT-OSS should be fine-tuned only on text-based

representations of data.

Finance-Llama-8B

•

Structured Data: Possibly, via text conversion. Finance-Llama-8B is a specialized Llama 8B model

fine-tuned for financial tasks. It’s a text-generation model, so like other LLMs it only “sees” text. If

you have structured financial datasets (say, time-series or balance sheets), you’d preprocess

these into text (for instance, feed a series of numbers as a comma-separated string, or as a

natural language statement: “Revenue grew 10% QoQ to $X…”). Finance-Llama has domain

knowledge of finance, but providing raw tables without context won’t be effective. Instead,

consider augmenting structured data with explanatory text or embedding them in a prompt

template (maybe a mini-CSV in markdown format that the model can be taught to read). In

essence, treat structured input as data-to-text conversion for fine-tuning purposes.

•

Unstructured Text: Yes – primary use case. Finance-Llama-8B was specifically fine-tuned on a

large corpus of financial Q&A, reports, and multi-turn dialogs. It’s well suited to digesting news

articles, analyst reports, regulatory filings, etc. Preprocess by cleaning the text and potentially

structuring it as instruction-following examples. For instance, you could use prompt

completions: “User: Explain the key points of this earnings report… Assistant: (detailed answer)”

or simple QA pairs about a document. Because the base model is already domain-tuned, you

don’t need an enormous dataset to teach it new facts – a targeted corpus of relevant text (few

thousand examples) can refine it further. If doing classification tasks (e.g., sentiment of a news

piece), you might attach a special format in the prompt and fine-tune accordingly. But generally,

unstructured financial text is ideal training material.

•

Visual Data: No. Finance-Llama-8B is a text-only LLM (based on Llama architecture, no vision).

You should not feed images or PDFs directly. Convert any visuals (like a stock chart or a

screenshot of a financial dashboard) into text descriptions before using them. If visual analysis is

needed, a separate vision model or multimodal model would be required – this model itself

cannot interpret images.

Qwen3-Bifrost-SOL-4B

•

Structured Data: Limited, via text. Qwen3-Bifrost-SOL-4B is a fine-tuned Qwen 4B model geared

towards the Solana blockchain domain (smart contract Q&A, coding). It’s fundamentally a text

2

generation model (similar to Llama in architecture). If you want to fine-tune it on structured on-

chain data (e.g. transaction tables, blockchain metrics), you’ll need to represent those as text.

Possible strategies: describe on-chain metrics in sentences (“There were 1.2M transactions on

Solana today, up 5% from yesterday.”), or feed key–value pairs in a pseudo-JSON or YAML format

in the prompt. The model’s small size (4B) means it has limited capacity, so keep inputs concise.

It won’t natively perform quantitative analysis, but you can train it to emit analysis given textual

stats. The bottom line is to convert any structured Solana data into Solana-related narratives or

Q&A for training.

•

Unstructured Text: Yes – very appropriate. Qwen3-Bifrost-SOL was specifically trained on textual

Q&A about Solana development. Fine-tuning it further on Solana docs, developer guides, or forum

Q&A can enhance its expertise. Preprocess text from Solana governance proposals, tutorials, or

dev chats by cleaning and formatting as Q&A or instruction dialogues. For example, take a piece

of Solana documentation and form a question the doc answers, using that as a training pair.

Since the model was optimized for technical Q&A and code (Rust and TypeScript code examples

are part of its training), you can include code snippets in your fine-tuning data. Make sure to

format code with proper markdown formatting in the prompt so the model learns to handle it.

This model likely has a shorter context (around 2k tokens as fine-tuned), so split long texts and

avoid examples that exceed the context window.

•

Visual Data: Not supported. Qwen3-Bifrost-SOL-4B has no vision capability. It cannot be fine-

tuned on images or diagrams directly. If you have something like a Solana block explorer

screenshot or a flowchart you want it to understand, you’d need to describe it in text.

Otherwise, consider coupling this model with a separate vision model if image analysis of

blockchain data is required.

CryptoBERT (Sentiment Analysis Model)

•

Structured Data: Not directly. CryptoBERT is an encoder-based model (BERT architecture) fine-

tuned for classifying sentiment in crypto text

1

. It expects text inputs (tweets, posts) and

outputs a sentiment class. It isn’t designed to ingest structured numerical data or multi-modal

input. If you have structured market data you want to incorporate (say, sentiment scores aligned

with price movements), you cannot feed that to CryptoBERT’s architecture unless you create a

hybrid input (e.g. appending numeric features as tokens to the text, which is experimental and

not typical). The best you can do is join structured info with text, for example: “<Text post>. [BTC

+5% in 24h]” as one input string, and try to fine-tune the model to use that bracketed info. But

this is non-standard. Generally, keep inputs textual for CryptoBERT.

•

Unstructured Text: Yes – exclusively. CryptoBERT was built to analyze social media and news text

in crypto

1

. Fine-tuning it further would mean training on text labeled with sentiment or other

categories. For instance, if you have a new dataset of crypto Reddit comments with sentiment

labels, you can fine-tune CryptoBERT on it. Preprocessing for BERT involves tokenizing text to the

model’s max sequence length (CryptoBERT was trained with max length 128 tokens for

classification). Clean the text (remove URLs, lowercase, etc. as appropriate) and ensure class

labels are consistent (“Bullish”, “Bearish”, etc., or whatever scheme the model expects). Use the

Hugging Face Trainer or similar to train the classification head on your new data. Because

CryptoBERT is already domain-specific, fine-tuning should be done carefully to avoid

catastrophic forgetting – a smaller learning rate and perhaps freezing lower layers could help

retain its general crypto language understanding while adapting to new data nuances.

•

Visual Data: No. CryptoBERT cannot process images. Any sentiment signals from images (like a

meme or a chart with annotations) would need to be described in text and then fed to the

model. But typically, sentiment analysis models rely purely on text content. If images (e.g. an

image posted on Twitter) carry sentiment, you’d need a separate pipeline to interpret those

visuals.

3

CryptoTrader-LM (Trading Signal Generator)

•

Structured Data: Yes, with the right formatting. CryptoTrader-LM is a specialized model that

predicts trading actions (buy, sell, hold) based on inputs like news and possibly price history. It’s

built on a language model (Mistral-8B instruct, fine-tuned with LoRA), so it primarily handles text.

However, trading decisions often involve structured inputs (prices, indicators). Fine-tuning

CryptoTrader-LM can include structured data if you represent it textually. For example, you might

feed a prompt: “BTC 24h change: -3%; Sentiment: negative. News: ... [headline] ... -> What is the

action?” and have the target output as “Sell”. In practice, you can prepend a set format of key

metrics before the news text. Preprocessing: decide on a schema (like a fixed-order list of

indicators as text) and ensure every training example follows it. This essentially teaches the

model to parse structured info encoded as text. Another strategy is to generate a textual

summary of relevant metrics and include that in the prompt. Keep the structured part concise to

fit with the textual part within the model’s context.

•

Unstructured Text: Yes – core component. CryptoTrader-LM uses news articles and tweets as

inputs for its trading signal predictions. Fine-tuning it on more text data (e.g. recent crypto news

with expert annotations of “buy/sell” decisions) will improve its performance. Preprocess news

articles by truncating to relevant parts (to avoid context overflow), and label them with the

desired signal. The fine-tuning data could be formatted as: Input: “[News text] \nQuestion: Given

the above news, should we buy, sell, or hold [asset]? \nAnswer:”, Output: “Sell”. By presenting it in

a Q&A or instruction form, you leverage the instruct tuning of the base model. Ensure a

balanced dataset (roughly equal buy/sell/hold examples) to prevent bias. Also, include a variety

of contexts (bull market news, bear market news, neutral updates) so the model learns nuanced

signals. If available, you might also include some rationale text in the training outputs (e.g. an

explanation before the final decision) to encourage the model to reason, though that depends

on whether you want the model to justify its decisions or just output the signal.

•

Visual Data: Not directly. CryptoTrader-LM doesn’t natively handle images or charts. If you want

to incorporate chart patterns or other visual cues, you’d again need to convert them to text (“The

price chart shows a head-and-shoulders pattern…”). However, identifying patterns from images is

a very different task; it’s better left to a vision model or by pre-processing with technical analysis

libraries to yield textual indicators that CryptoTrader-LM can consume. In summary, treat

CryptoTrader-LM as a text-based model: feed it numbers and facts as words, and it will output

text (like “Buy” or “Sell”).

Part B: Fine-Tuning Implementation Workflows

We outline three training/evaluation workflows, focusing on reproducibility, efficient resource use, and

any model-specific quirks. Each workflow covers dataset prep, toolchain/environment setup, compute

needs, example training commands, and output formats.

1. Fine-Tuning Qwen3-VL and GPT-OSS on Thundercompute with Unsloth

Overview: We will use the Unsloth library on a Thundercompute GPU instance to fine-tune Qwen3-VL

(8B vision-language model) and GPT-OSS (20B text model). Unsloth provides optimized training (QLoRA

and other tricks) that drastically reduce VRAM requirements, making fine-tuning feasible on modest

GPUs. Thundercompute will host the training environment (with NVIDIA GPUs) and we’ll leverage its

high-performance instances (including a prototyping mode for cost savings).

•

Dataset Preparation:  For  Qwen3-VL, prepare a  multimodal dataset  of image-text pairs. For

example, you might compile a set of screenshots from crypto dashboards or dApp UIs and pair

each with a descriptive caption or a question-answer. Ensure you have the images in a accessible

4

directory and a metadata file (e.g. JSON or CSV) that lists each image file and its corresponding
text.   If   fine-tuning   Qwen3-VL   for   VQA,   entries   might   look   like:   {"image":   "path/to/
img.png", "question": "What’s the current ETH collateral value?", "answer":

"Approximately   $5M"} .   Unsloth   can   accept   such   data;   it   provides   utilities   for   vision   fine-

tuning (it allows commands to load images during training). For GPT-OSS, prepare your dataset

in a JSONL or ShareGPT-style format with instruction-response pairs. Each line could be a JSON
with fields like  {"user": "…", "assistant": "…"} . If you have only raw text (e.g., a corpus

of news or proposals), you may convert it into prompted QA form or simply use it for continued
pre-training. Unsloth’s dataset guides suggest using their  standardize_sharegpt  function to

format data consistently. Make sure to split a portion as validation set to monitor training loss.

Model-specific quirk: GPT-OSS is specialized for reasoning; to preserve that, include some chain-

of-thought examples in the fine-tuning data (ideally >75% of the data should involve reasoning

steps) if your task can benefit from it.

•

Toolchain & Environment Setup: Launch a Thundercompute instance with a suitable GPU. For

GPT-OSS 20B QLoRA fine-tuning, even a single 16 GB GPU (like NVIDIA T4) can work, but 24 GB+

is safer for speed. Qwen3-VL 8B with images will also fit in 16–24 GB (Unsloth reports free Colab

T4 is enough for 8B). On Thundercompute, you might choose an A100 40GB for headroom. Use

Prototyping mode for lower cost, which is compatible with Unsloth fine-tuning jobs. Once the

instance is up (Ubuntu or similar OS pre-installed), set up the environment:

•

Install Unsloth and its model zoo:  pip install --upgrade --force-reinstall --no-
cache-dir unsloth unsloth_zoo . This will also install PyTorch and other dependencies.

Unsloth includes support for QLoRA, LoRA, etc., so no need to separately install bitsandbytes or

PEFT – it’s handled internally.

•

Ensure you have git LFS or Hugging Face CLI if you’ll download base models from HF. Unsloth

can auto-download certain models if you provide the HF repo name. Thundercompute instances

should have internet and enough disk (e.g., 200 GB if you’re pulling a 120B model; for 20B and

8B, ~30–40 GB is fine).

•

If fine-tuning Qwen3-VL, also install any image libraries needed. Unsloth likely uses PIL or

OpenCV under the hood to load images. The Unsloth Vision Fine-tuning guide suggests it
handles images natively, but ensure libraries like Pillow ( pip install Pillow ) are present.

•

(Optional)  Thundercompute CLI:  If you want to manage the instance via CLI, you could use
tnr  (Thunder CLI) to monitor usage. But this isn’t required for the training itself.

•

Compute   Configuration:  For  GPT-OSS-20B,   Unsloth’s   QLoRA   approach   requires   ~14   GB   GPU

VRAM. Thus, a single A100 16GB (if available) or more commonly an A100 40GB (which gives

plenty of headroom for larger batch sizes or longer sequences) can be used. If you plan to fine-

tune the 120B GPT-OSS, you’ll need at least ~65 GB VRAM with QLoRA – in practice an 80 GB A100

in prototyping mode is a good choice. For Qwen3-VL 8B, a 16 GB GPU is sufficient for QLoRA or

LoRA   fine-tuning   (Colab   T4   works   in   Unsloth’s   example),   but   if   you   use   larger   variants   (e.g.,

Qwen3-VL-32B), you’d want a 40 GB GPU or multi-GPU setup. Thundercompute does allow multi-

GPU instances; Unsloth supports multi-GPU training if needed, but for our models we likely stick

to single GPU. Set your instance with at least 4 vCPUs and 30+ GB RAM to handle data loading.

High-level: an A100 40GB, 4 vCPU, 80 GB RAM instance in prototyping mode would comfortably

handle both training runs one at a time. (After finishing one model, you could reuse the instance

for the other.)

•

Training   Procedure   (Unsloth):  Unsloth   provides   a   high-level   API.   You   can   either   use   their

Jupyter notebook flow or write a short Python script. Here’s an outline using Python code:

5

•

Load the base model: Unsloth has model names for its zoo. For GPT-OSS 20B, you might do:

import unsloth

model = unsloth.load_model("unsloth/gpt-oss-20b-bnb-4bit", mode="QLoRA")

This would load the 4-bit quantized base model (in memory-efficient format) ready for QLoRA

fine-tuning. For Qwen3-VL, similarly:

model = unsloth.load_model("Qwen3-VL-8B", mode="QLoRA")

(Note: The exact model identifier might differ; Unsloth might have its own naming or you can

provide the HF repo name. Also, Qwen3-VL likely requires specifying it’s a vision model; Unsloth’s

docs show examples of loading it in their notebooks.)

•

Prepare data loaders: Unsloth can take a list or dataset object. If you have JSONL, you could do:

data = unsloth.load_data("data/train.jsonl")

val_data = unsloth.load_data("data/val.jsonl")

If your data is in memory as Python lists of dicts, that works too. For vision data, Unsloth might
expect the path in the text (e.g., a placeholder token or a special syntax like  <image>path/to/
img.png</image> ). However, Unsloth’s vision fine-tuning guide suggests an interactive

approach; in script form, they likely have a way to feed images (perhaps by providing a custom

collate that loads image bytes). We might use their notebooks as a template – for simplicity,

assume we have a function that yields (image_tensor, text) pairs for training.

•

Fine-tune: Unsloth abstracts the training loop. For example:

unsloth.train(model, data, val_data=val_data, epochs=3, batch_size=1,

lr=2e-5)

This would start the fine-tuning process. Unsloth automatically uses P.E.F.T. (like LoRA/QLoRA)

under the hood and will apply gradient checkpointing, etc., to optimize VRAM. We follow logs it

prints (it will likely show loss, etc.). We set hyperparameters: since these are already pre-trained

large models, a low learning rate (e.g. 2e-5 to 1e-4) is used to avoid overwriting knowledge.

Unsloth’s default QLoRA config will use 16-bit optimizers with 4-bit base weights, which is

efficient. Note: For GPT-OSS, ensure the context length used during training matches your needs

– if your fine-tuning data has, say, 4k token examples, it’s fine. If you want to utilize the full 128k

context, you’d need to enable Unsloth’s FlexAttention (which it may do by default) to handle long

context with less memory. For Qwen3-VL, ensure images are being fed correctly – perhaps start

with single-image examples before trying multi-image (Unsloth supports multi-image training

•

with some config changes).
Monitoring and Checkpoints: During training, monitor GPU usage (Thundercompute’s  tnr
status  or nvidia-smi) and training loss. Unsloth might save intermediate checkpoints. If the

instance has limited disk, be mindful of checkpoint sizes (QLoRA adapters are small, but if you

merge into full model it can be tens of GB). If training is long, you can snapshot the

Thundercompute instance (or better, configure output to go to a mounted volume or directly to

Hugging Face Hub).

6

•

Completion – Save model:  Once training is done (say after 3 epochs or when validation loss

stops   improving),   save   the   fine-tuned   model.   With   Unsloth,   if   using   QLoRA,   you   have   a   few

options:

◦

Save the LoRA adapters:  model.save_pretrained("my-gptoss-lora")  would save

the lora layers (and maybe a merged model config). This is very lightweight (few hundred

MB or less).

◦

Merge and save full model: Unsloth recently allows merging QLoRA weights into a full 16-

bit model for export
model.save_pretrained_merged("my-model-merged", tokenizer) , which yields

. This can be done with

2

a HuggingFace-format model (e.g., HF checkpoint with .bin or .safetensors weights)

3

.

For GPT-OSS, this is useful if you want to run the model outside Unsloth (since originally

QLoRA fine-tunes were only runnable inside Unsloth, this merge step unlocks them for

normal inference

2

). For Qwen3-VL, similarly you can merge if needed.

◦

Save to GGUF/llama.cpp: Unsloth can directly export to GGUF for llama.cpp by merging

and quantizing in one step
function or convert the HF model with  llama.cpp  quantization script. Unsloth’s

. For example, after merging, you could use their built-in

4

documentation notes that saving Qwen3-VL to GGUF is supported now that llama.cpp

supports it

4

.

•

Expected Output: We will have fine-tuned models for each:

•

GPT-OSS-20B fine-tuned – likely saved as a LoRA adapter plus instructions to merge, or already

merged into a HF model (which could be ~40GB in bf16). If storage is an issue, keep the adapter

separate (a few GB) and later apply it to the base model when needed.

•

Qwen3-VL-8B fine-tuned – this will include the vision projection and language weights. If using

LoRA,   you’ll   have   adapter   weights   for   both   the   vision   and   language   components.   We   might

output   a   merged   FP16   checkpoint   (~16GB).   Alternatively,   we   could   directly   export   a   GGUF

quantized model for inference (for example a 4-bit Qwen3-VL GGUF which might be ~2–3GB).

The   output   format   depends   on   usage:   for   deployment   on   Hugging   Face   or   transformer

pipelines, HF checkpoint is best; for local inference on llama.cpp, a GGUF is convenient.

•

Reproducibility   &   Notes:  Document   all   hyperparameters   and   random   seeds   used.   Unsloth

tends   to   hide   some   complexity,   but   you   can   set   a   seed   via   environment   variable   or   in   code
( unsloth.set_seed(42) ). Because Thundercompute instances are ephemeral, make sure to

backup the output (download the model files to a safe storage or push to Hugging Face Hub)

before terminating the instance. In terms of GPU constraints, Unsloth’s ability to train GPT-OSS in

14GB VRAM is a major enabler – without it, a naive fine-tuning would require >60GB VRAM due

to   GPT-OSS’s   mixture-of-experts   architecture.   Similarly,   Qwen3-VL   training   is   accelerated   by

Unsloth’s optimizations (they claim 1.7× faster and 60% less VRAM). Leverage these by sticking to

Unsloth’s training routines. One quirk for Qwen3-VL: handling images in training – ensure that

the data pipeline feeds images correctly. Unsloth’s vision notebook uses an interactive approach

(with a special CLI to load images), but in script form, you may need to load image tensors and

pass them to the model’s forward function. Unsloth likely provides an API to register an image

with  a  placeholder  token  in  the  prompt.  Check  their  docs  for  “/image”  usage  as  seen  in  the

example (loading images via a command). Once everything is set, fine-tuning these models on

Thundercompute via Unsloth should be efficient and relatively fast (expect a few hours for a

couple epochs on 20B with a single GPU, possibly faster due to 1.5× speed improvements).

7

2. Fine-Tuning Hugging Face Models on Thundercompute (Finance-Llama,

CryptoBERT, CryptoTrader-LM, Qwen3-Bifrost)

Overview:  In   this   workflow,   we   fine-tune   models   available   on   Hugging   Face   (Finance-Llama-8B,

CryptoBERT,   CryptoTrader-LM,   and   Qwen3-Bifrost-4B)   using   standard   Hugging   Face   Trainer   or   PEFT

(parameter-efficient   fine-tuning)   methods.   We’ll   still   utilize   Thundercompute’s   GPU   instances   for   the

heavy lifting, but without Unsloth – instead, using   Transformers, Accelerate, and PEFT libraries. We will

consider   methods   like  LoRA/QLoRA  for   efficiency   and   potentially  DPO   (Direct   Preference

Optimization) if we have preference data (e.g., for refining a model with human feedback).

•

Dataset Preparation: Prepare each model’s fine-tuning dataset according to its task:

•

Finance-Llama-8B: If doing an instruction tuning or Q&A task, format the dataset as instructions

with ideal answers. Since Finance-Llama is already tuned on a wide range of financial tasks,

identify what gap you’re trying to fill. For instance, you might have a dataset of recent financial

news and want the model to summarize or extract insights. Format: a prompt that includes the

news text or a question about it, and the target output as the summary/answer. If doing

classification (say, predict stock sentiment), format each example as a single input text with a

label. Ensure the data is split into training and validation.

•

CryptoBERT: This is a classification model (sequence classification). Dataset should consist of texts

(tweets, posts) with a sentiment label. Likely labels are {Bullish, Bearish, Neutral} or similar. You’ll

convert these to numeric labels 0/1/2 for training. Use the same label mapping CryptoBERT was

originally trained on (if continuing training) to maintain consistency. Preprocessing: tokenize and

perhaps truncate to 128 tokens as recommended. Because CryptoBERT is based on BERT/

RoBERTa, make sure to use the corresponding tokenizer (e.g., AutoTokenizer for ElKulako/

cryptobert).

•

CryptoTrader-LM: This model likely expects input text (news + possibly some market info) and

outputs a decision. If fine-tuning for better accuracy, you need a dataset of news articles or

social media updates with an associated action label (buy/sell/hold). You might format each

training example as a small prompt: e.g., "[NEWS]: Fed increases interest rates… [BTC] What should

the trader do?" -> * and the target is "Sell". Alternatively, since CryptoTrader-LM was fine-tuned from

Mistral using LoRA, it might have been done in a conversational style. If the original model card

provides a format, use that. Otherwise, be consistent – possibly treat it as a single-turn instruction:

Input: (news)… Output: (decision)*.

•

Qwen3-Bifrost-4B: This is a chat-style model for Solana Q&A. Prepare data as dialogues or QA

pairs about Solana. For example, you might gather Q&A from Solana docs or StackExchange.

Format them as conversation: User: "How do I create a PDA in Solana?" Assistant: "To create a

Program Derived Address, you need to … [detailed answer]". Because it’s a smaller model, avoid

extremely long answers. If you’re adding knowledge (like new Solana protocol details), ensure

the prompt provides enough context or the question is answerable from what the model should

know after fine-tuning.

•

General   preprocessing:  For   all   models,   clean   the   text   (remove   unnecessary   whitespace,   fix

encoding), and consider tokenization needs. Finance-Llama and Qwen3-Bifrost are generative
models (use   AutoModelForCausalLM ), so their datasets can be prepared in text form with

  tokens   delineating   user   and   assistant

special
is
AutoModelForSequenceClassification ,   so   you’ll   create   a   Dataset   with   text   and
label   fields. It’s useful to use the Hugging Face   datasets   library to handle splitting and

  CryptoBERT

  needed.

if

shuffling. Also, for LoRA/QLoRA, keep an eye on sequence lengths – longer sequences increase

memory use quadratically, so truncate or segment data to manageable lengths (e.g., Finance-

Llama might handle 2048 or 4096 tokens; don’t feed entire 10k-token reports in one go).

8

•

Environment  &  Tools  Setup:  On  Thundercompute,  create  an  instance  with  appropriate  GPU

depending on model size. For 8B models (Finance-Llama, CryptoTrader-LM), a single 16 GB GPU

can suffice if using 8-bit or LoRA fine-tuning. However, to be safe (and if you want faster training

with larger batches), consider an A100 40GB. For CryptoBERT (110M params) and Qwen3-Bifrost

(4B), these are small and can easily fine-tune on even a T4 16GB or smaller – you could run those

on CPU in a pinch, but GPU will be much faster.

•

Install required libraries:

pip install transformers==4.33 peft==0.5.0 accelerate==0.21

bitsandbytes==0.41 datasets==2.14

(versions are for example; pick latest compatible versions).  transformers  for the model APIs,
peft  for LoRA/QLoRA,  bitsandbytes  for 4-bit quant,  accelerate  to handle device
placement or multi-GPU if needed, and  datasets  to load data. Also install  torch  (likely

already present) with CUDA support.

•

•

If using QLoRA: BitsAndBytes will enable loading models in 4-bit. Ensure that the GPU has
compute capability for 8-bit matmul (most modern GPUs do). You might need to do  pip
install bitsandbytes  which we included.
If using DPO (Direct Preference Optimization): Install  trl  (Transformers Reinforcement
Learning) library:  pip install trl==0.4.7 . DPO is a newer method, possibly implemented

in trl or as custom code. It requires a dataset of comparison between outputs. If you have such

data (e.g., model output vs a preferred output), you can apply DPO instead of supervised fine-

tuning. For our scope, you might not have this data, but we mention it as an option. Using DPO

would involve a different training loop (minimizing a special loss that compares model logits on

preferred vs non-preferred outputs). It’s more complex, so unless explicitly needed (e.g., to align

CryptoTrader-LM with a reward like Sharpe ratio by comparing trades), a standard supervised

fine-tune or LoRA is easier.

•

Thundercompute specifics: Use the  tnr  CLI or web console to start the instance in production

mode  if you encounter any weird issues with prototyping (especially if using custom kernels in

bitsandbytes, though prototyping mode claims to support common ML frameworks). For multi-
GPU (probably not needed here), you could start an instance with   --num-gpus 2   and use
accelerate  to launch distributed training. But given model sizes, single GPU is fine.

•

Compute Resources and PEFT Strategy:

•

For LoRA fine-tuning: This keeps most of the model frozen and trains small adapter matrices

(which greatly reduces memory). For an 8B model, LoRA will use maybe 1–2 GB of VRAM extra for

the adapters and optimizer states. You can likely fine-tune Finance-Llama-8B or CryptoTrader-LM

on a 16 GB GPU with LoRA with decent batch sizes (e.g., batch 4 or 8).

•

For QLoRA: This would quantize the model to 4-bit and then apply LoRA on top. The benefit is

you can even fine-tune larger models or fit bigger batches. For 8B, QLoRA might be overkill (8B

fits in 16-bit on 16GB just fine), but it can let you train 8B on smaller GPUs or free up memory for

longer sequences. For example, Finance-Llama-8B in 4-bit might only occupy ~4GB of VRAM,

leaving room for a big batch or longer context.

•

Decide based on experimentation: LoRA (16-bit adapters on 16-bit model) vs QLoRA (16-bit

adapters on 4-bit model). QLoRA requires a bit more care (transformers integration of 4-bit
might need  model = AutoModelForCausalLM.from_pretrained(...,

9

load_in_4bit=True, device_map="auto", trust_remote_code=True) , then wrapping
with  peft.LoraModel ).

•

For CryptoBERT: Given it’s small, you might do a full fine-tune (update all weights) – it’s only

~110M parameters, which is feasible on a GPU in a few hours. But you could also use LoRA here

(PEFT supports BERT fine-tuning too). LoRA might be useful if you want to regularize changes or

have limited data. However, often classification fine-tuning just trains the final layer or a few

layers. An alternative is simply to add a new classification head and train that (which is effectively

what was originally done). Since CryptoBERT already has a classification head, you’ll be updating

that primarily.

•

Instance choice: e.g., For running all these, an A100 40GB could even multi-task (but it’s simpler

to do sequentially). If doing sequentially, you could even choose a smaller GPU for CryptoBERT

and Qwen-Bifrost (like a T4 16GB to save cost). But to keep one environment, go with A100 and

you have plenty of RAM for all. In Thundercompute, you pay per minute, so you might spin up a

powerful instance, fine-tune all models one after another (each might take <1 hour for small

ones, a couple hours for 8B with a good setup), save outputs, then shut it down.

•

Training Scripts Examples: We’ll illustrate two scenarios – one for a generative model (Finance-

Llama-8B using LoRA via PEFT) and one for a classification model (CryptoBERT full fine-tune).

•

Finance-Llama-8B with LoRA:

import torch

from transformers import AutoModelForCausalLM, AutoTokenizer,

TrainingArguments, Trainer

from peft import LoraConfig, get_peft_model

model_name = "tarun7r/Finance-Llama-8B"

# base model on HF

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(

model_name,

load_in_8bit=True, device_map="auto",

# use 8-bit base for memory

save

)

# Prepare LoRA config – e.g., rank=16, target some layers

lora_config = LoraConfig(

r=16, lora_alpha=32, target_modules=["q_proj","v_proj"], # target

key attention proj in Llama

lora_dropout=0.05, bias="none"

)

model = get_peft_model(model, lora_config)

# Prepare data

def format_examples(example):

return tokenizer(example["prompt"], text_target=example["response"],

truncation=True)

dataset = ...

# load your dataset, e.g., using datasets library

tokenized_data = dataset.map(format_examples, batched=True)

training_args = TrainingArguments(

output_dir="./finetune-finance-llama",

per_device_train_batch_size=4,

num_train_epochs=2,

10

learning_rate=2e-4,

fp16=True,

logging_steps=50,

save_steps=100,

save_total_limit=2,

)

trainer = Trainer(model=model, args=training_args,

train_dataset=tokenized_data["train"],

eval_dataset=tokenized_data["validation"])

trainer.train()

This script loads the base model in 8-bit mode (to save memory) and wraps it with LoRA. We
target specific modules (for Llama, often  q_proj / v_proj  in attention layers are targeted by

LoRA by convention). We then tokenize the prompt-response pairs. The Trainer will handle

feeding data and performing gradient updates on the LoRA adapter weights (the rest of the

model in 8-bit stays frozen). We use FP16 mixed precision for speed. After training, the
trainer.save_model()  will save the model with LoRA layers (it will include the base model in

8-bit form plus LoRA). We might instead want to save just the LoRA adapters: we can do
model.save_pretrained("finance-llama-lora-adapter")  which using PEFT will save a
small  .bin  with the LoRA weights and a config.

•

CryptoBERT fine-tuning: (Sequence classification)

from transformers import AutoModelForSequenceClassification,

AutoTokenizer, TrainingArguments, Trainer

model_name = "ElKulako/cryptobert"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForSequenceClassification.from_pretrained(model_name,

num_labels=3)

# Prepare dataset

dataset = ...

# load your sentiment labeled data, e.g., as HuggingFace

Dataset

def tokenize_func(example):

return tokenizer(example["text"], truncation=True, max_length=128)

tokenized = dataset.map(tokenize_func, batched=True)

training_args = TrainingArguments(

output_dir="./cryptobert-finetune",

per_device_train_batch_size=16,

num_train_epochs=3,

learning_rate=2e-5,

evaluation_strategy="epoch",

logging_steps=100

)

trainer = Trainer(model=model, args=training_args,

train_dataset=tokenized["train"], eval_dataset=tokenized["validation"])

trainer.train()

This simply fine-tunes the whole model (including embeddings and encoder) on the classification

task. CryptoBERT is small, so a batch of 16 and full precision should be fine on a GPU. After

11

training, we’ll have a new model checkpoint in  ./cryptobert-finetune  with an updated

classification head. (Because the model was already pretrained on similar data, you might also

freeze lower layers and just train the final layer for a quick adaptation, but here we do full fine-

tune for completeness.)

•

Note on QLoRA or DPO: If we wanted to use QLoRA for, say, Qwen3-Bifrost (4B is small though) or

if   we   had   a   20B   model   in   HF   to   fine-tune,   we   could   use   a   similar   approach   as   above   but
load_in_4bit=True   with   bnb_4bit_quant_type="nf4"   etc.,  and  then  wrap  with  LoRA.

Hugging Face’s documentation for QLoRA provides a training script template (essentially using
bitsandbytes  and  peft.LoraConfig ). Since our models in this section are moderate size,

we didn’t strictly need QLoRA, but it’s an option if memory was very constrained. For DPO, if we
had   reward   model   comparisons,   we   would   use   trl.DPOTrainer   instead   of   the   standard

Trainer. This would require pairs of model outputs with preferences. Given this is an advanced

scenario and we don’t have such data prepared, we skip detailed code, but one would initialize a

DPOTrainer with the base model (e.g., Finance-Llama) and a reward model or preference dataset,

and train with a specific loss function to make the model’s outputs align with preferred ones.

DPO can be thought of as a way to fine-tune without RL rollouts, directly from static preference-

labeled data (if available).

•

Output and Checkpoints: For each model, we’ll save the fine-tuned weights:

•

Finance-Llama-8B with LoRA: we’ll have either a merged model or a LoRA adapter. It’s often

convenient to just keep the LoRA adapter (few MBs) and later merge if needed for deployment.

We can push this to Hugging Face Hub (e.g., a repo with the adapter and a README on how to

apply it to base model).

•

CryptoBERT: we’ll get a new set of weights (around 400 MB if fp32) which represent the fine-

tuned sentiment classifier. Save as HF format (pytorch_model.bin or better, use
Trainer.save_model()  which creates all necessary files including tokenizer config).

•

CryptoTrader-LM: similarly, if fine-tuned via LoRA on top of Mistral-8B, output a LoRA adapter.

The original CryptoTrader-LM was LoRA-finetuned on Mistral, so one approach is actually to start

from Mistral-8B model and apply two LoRAs (original + your new) or merge the original first. A

simpler way: get the full weights of CryptoTrader-LM if available (the author might have

published a merged version on Hugging Face). If not, you can load Mistral-8B and apply a new

LoRA as if training from scratch on your data (effectively creating a variant CryptoTrader). In any

case, save whichever format you end up with (LoRA or full model) for use.

•

Qwen3-Bifrost-4B: save the fine-tuned model (4B is ~8GB in fp16). Since it’s small, full weight

update  is  possible;  but  you  might  still  do  LoRA  to  be  efficient.  Save  either  the  full  model  or

adapter. Possibly convert to FP16 safetensors for easier loading later. Document that this model

remains under MIT license (Bifrost’s license is MIT).

•

Model-Specific Quirks & Tips:

•

Finance-Llama-8B: It’s already domain-finetuned, so monitor for overfitting if your dataset is

small. You might use a low LR and few epochs. It also supports multi-turn conversation – if your

fine-tuning data is single-turn, the model might lose a bit of its multi-turn capability, but that’s

usually fine. If keeping multi-turn, include some dialogues in training.

•

CryptoBERT: Being a classifier, ensure the class distribution in training isn’t skewed. If it is,

consider weighting the loss or oversampling. Also, since it’s based on BERTweet (a RoBERTa

variant), use the appropriate tokenizer (which we did) – sometimes people mistakenly use BERT

12

tokenizer and get worse results. Also note the context limit ~128 tokens for best performance –

don’t feed very long texts; if needed, break text or summarize before classification.

•

CryptoTrader-LM: Because it produces a discrete label, you might actually treat this as

classification (like classify the action). However, it’s fundamentally a generative model, so you

could either train it to output the words “Buy/Sell/Hold” (generative style with a language

modeling loss on those tokens) or add a classification head. The original approach likely did

generative fine-tuning (the model outputs the word as completion). We followed that by

formatting the prompt and having the single-token answer. Ensure during training that the label

token is treated properly (you might want to add special tokens for “Buy” etc., or just rely on the

existing vocabulary). If using generative loss, pack the prompt and answer together so that only
the answer contributes to loss (in HF Trainer, you can use  labels  that mask the prompt part).

This detail is important for correctness.

•

Qwen3-Bifrost-4B: This model being only 4B might struggle with very long or complex inputs.

Fine-tune on relatively short prompts (maybe a few hundred tokens at most). Also, Qwen might
have its own tokenizer (ensure using  QwenTokenizer  if available via  transformers  with
trust_remote_code=True  perhaps). After fine-tuning, test it on some Solana questions to

see if it improved. Sometimes small models can lose knowledge if fine-tuned hard on a narrow

set, so consider using a lower learning rate or fewer epochs to retain general ability.

•

DPO and others: If you do have human preference data later (e.g., ranked outputs from

CryptoTrader-LM), you could fine-tune with DPO or pairwise loss. That would involve a custom
training loop (possibly using  trl  library’s DPOTrainer). Keep in mind that DPO or RLHF-type

fine-tuning often requires careful hyperparam tuning to not diverge. On Thundercompute, you

have the freedom to experiment, but always monitor that the model’s responses don’t collapse

to some trivial output (like always “Buy”).

•

Thundercompute usage:  as before, ensure you save models off-instance. Also, use  Accelerate  if

needed   to   utilize   multiple   GPUs   or   mixed   precision   easily.   For   example,   you   could   wrap   the
Trainer with   accelerate launch   if you had multiple GPUs to split the model (not needed

here, but an option for bigger models). Given all these models are relatively small, single-GPU

training is straightforward. The training time for these on an A100: CryptoBERT (maybe <1 hour

for a few epochs on millions of posts), Qwen3-Bifrost (maybe 1-2 hours for a few epochs on 1k

QA pairs as in the Bifrost dataset), Finance-Llama-8B (with 500k dataset might be longer, but if

you’re   only   fine-tuning   on   a   subset   or   new   data,   it   could   be   a   few   hours),   CryptoTrader-LM

(depends on data size, likely not huge).

•

Outputs & Formats: All fine-tuned models will be saved in Hugging Face Transformers format

(since we used that ecosystem). Specifically:

•

Generative models (Finance-Llama, CryptoTrader-LM, Qwen3-Bifrost): saved as directories with

config.json, tokenizer files, and either merged weight files or adapter weights plus base

reference. If we used LoRA without merging, the output directory will contain the LoRA config

and weights (usually named adapter_model.bin or similar) along with a small config. We should

document how to use it (e.g., “Load base model X and apply this adapter via PEFT to get the final

model”).

•

Classification model (CryptoBERT): saved similarly with config (num_labels=3) and

pytorch_model.bin containing the classifier head and base model.

•

We can also export any of these to ONNX or TorchScript if needed for deployment, but that’s

beyond fine-tuning scope.

•

If we want to use them with llama.cpp or other inference, we’d need to convert (especially for the

Llama-based ones). For instance, we might later quantize Finance-Llama-8B to GGUF for local
use. This can be done by converting the HF checkpoint to a  llama.bin  and then running

13

quantize . Similarly for Qwen3-Bifrost if we want. However, we’ll cover local quantization more

in the next section.

3. Local Model Deployment on MacBook (M4, 48GB RAM) with llama.cpp and llama-

swap

Overview:  In this scenario, we use a MacBook Pro (M4 chip with 48GB unified memory) to run and

prompt the fine-tuned models – specifically GPT-OSS and Qwen3-VL – using llama.cpp and llama-swap.

We assume we have obtained GGUF-format quantized models for GPT-OSS and Qwen3-VL. The focus is

on how to load and use these models efficiently on local hardware, and what options exist for further

tuning or quantization on Mac.

•

Model Conversion to GGUF: First, convert the fine-tuned models (GPT-OSS and Qwen3-VL) into

GGUF format, which is the format compatible with llama.cpp (the latest generation of GGML). If

you fine-tuned using Unsloth as above, you may already have a GGUF or at least a HF model that

can be converted. For GPT-OSS-20B, use the conversion tools from llama.cpp:

•

Obtain the FP16 HuggingFace model (if you only have LoRA, merge it as described to get a full

model

2

). Ensure you have the model in 16-bit floating weights (probably split across multiple

files due to size).
Use the  convert.py  script from llama.cpp (which might need a config for GPT-OSS since it’s

•

not Llama architecture; however, Unsloth’s notes suggest they made it compatible by treating it

similar to Llama for conversion). Alternatively, Unsloth might have directly provided a GGUF. In

fact, Unsloth’s documentation points to their uploaded GPT-OSS 20B GGUF

5

 – you could

download that directly if it aligns with your fine-tuned version, or replicate the conversion.

•

For Qwen3-VL-8B, Unsloth has provided an 8B GGUF as well. Since Qwen3-VL is multi-modal, the

GGUF actually consists of two files: the main model (language + vision transformer weights) and

a mmproj file which contains the projection layers that integrate the vision output into the
language model. You should have both: e.g.  Qwen3-VL-8B.gguf  and  Qwen3-VL-8B-
mmproj.gguf  (the second might be F16 even if the first is quantized).

•

Quantization: On Mac 48GB, you can afford relatively high quantization levels. For GPT-OSS 20B,

a 4-bit quant (Q4_K_M or similar) is about 10GB, which easily fits in 48GB RAM. You might even

try 5-bit or 6-bit for better accuracy (Q6_K ~ 20GB for 20B model, should fit too, as 20B * 6 bits

~15 GB + overhead). The exact sizes for GPT-OSS quant are not given, but likely similar to

Llama’s. Start with a 4-bit to ensure performance. For Qwen3-VL-8B, a Q4 quant will be much

smaller (maybe ~3GB total). You could use Q5 or even 8-bit since 8B in 8-bit is ~8GB which is fine.

The Mac’s metal backend can handle up to 8-bit, but 4-bit gives more headroom if you want to

run two models simultaneously.

•

Tools: If you prefer a one-click approach, Ollama is an alternative on Mac that can pull models in

a quantized form. For example, Finance-Llama and others are on Ollama library. In fact, Finance-

Llama-8B is available in Q4 form on Ollama. Similarly, GPT-OSS might be on Ollama’s library as

well (since Thundercompute’s guide used Ollama to run GPT-OSS 120B). But here we focus on

llama.cpp and llama-swap for flexibility.

•

Setting up llama.cpp on Mac:

•

Compile llama.cpp with Metal support. On Apple Silicon, you can do:

14

git clone https://github.com/ggerganov/llama.cpp.git

cd llama.cpp

make cc=mps

This enables the MPS (Metal Performance Shaders) backend for GPU acceleration. With 48GB
unified memory, you can load large models. The compilation will produce a  main  binary and
possibly the server binary (if you run  make server  to build  llama.cpp  server for OpenAI

API compatibility).

•

Verify you can run a test: for example, download a small GGUF model (like a 7B) and run
./main -m model.gguf -p "Hello"  to ensure it works.

•

For multi-modal Qwen3-VL, there may be a special branch or build. Unsloth references a
llama-mtmd-cli  binary which likely stands for multi-modal CLI. It suggests that the main

branch of llama.cpp has merged support for Qwen’s image input (“just supported it” as of their
). Possibly by 2025, llama.cpp can handle an extra  --mmproj  argument (as shown in

docs

4

the unsloth example) to load the image projection weights. Indeed, in Unsloth’s example they

run:

./llama.cpp/llama-mtmd-cli \

--model Qwen3-VL-8B-Instruct.gguf \

--mmproj mmproj-F16.gguf \

--n-gpu-layers 99 ... --ctx-size 8192

The  llama-mtmd-cli  might be either a patched version or a script that calls  main  with

multi-modal support. Check llama.cpp’s repository or wiki for Qwen-VL support. It might require
enabling CMake flags for multi-modal or using a separate branch like  multi-gpu  or similar. As
of now, assume we can use a command-line flag in the standard  main  or  server  to load
mmproj ( --mmproj ). If not, use the unsloth fork or binary they provided.

•

Once compiled, place your model files in a directory (e.g.,   ~/models ). For GPT-OSS-20B, you
might have  gpt-oss-20b-q4_K_M.gguf  (quantized model file). For Qwen3-VL, you have two

files as noted. These files can be quite large, but all fit in the 48GB RAM.

•

Using llama-swap for multiple models: llama-swap  is a lightweight Go server that acts as a

proxy to route requests to different local models (running on llama.cpp or similar) based on the

model name requested. This is perfect if you want to run both GPT-OSS and Qwen3-VL on the

same machine and switch between them without manually loading/unloading each time.

•

Configuration: Create a YAML config (say  ~/.llama-swap/config.yaml ). A minimal setup:

models:

gpt-oss-20b:

cmd: llama-server --port ${PORT} --model /models/gpt-oss-20b-

q4_K_M.gguf --threads 12

qwen3-vl:

cmd: llama-server --port ${PORT} --model /models/Qwen3-VL-8B-

Instruct-Q4_0.gguf --mmproj /models/Qwen3-VL-8B-mmproj.gguf --threads 12

15

Here we define two model entries. We use  llama-server  (which is the HTTP server version of
llama.cpp) as the backend. We pass the model file path and for Qwen, the  --mmproj  path as
well.  ${PORT}  is a placeholder that llama-swap uses to assign unique ports. We also set  --
threads 12  to utilize 12 CPU threads (tune this based on the Mac’s CPU cores for optimal
throughput, and  --n-gpu-layers  or similar can be set but on Metal backend it will offload as

•

much as possible automatically).
Run llama-swap:  llama-swap --config /path/to/config.yaml --listen localhost:
8080 . It will start up and launch the two model servers on separate ports internally. By default,

llama-swap listens on an OpenAI-compatible API endpoint on the port you specify (8080 in this

case).

•

Testing swap: You can open a browser or use curl to test:

curl http://localhost:8080/v1/models

This should list  gpt-oss-20b  and  qwen3-vl  as available models via the API. If you have the

OpenAI Python API, you could even do:

import openai

openai.api_base = "http://localhost:8080/v1"

openai.ChatCompletion.create(model="gpt-oss-20b",

messages=[{"role":"user","content":"Hello"}])

and get a completion. llama-swap will ensure the  gpt-oss-20b  model is loaded into memory

and handle the generation. If next you call the API with model="qwen3-vl", it will swap to that – it
might unload the GPT-OSS if memory is low or if configured to (llama-swap has a  ttl  for

unloading after idle). With 48GB, you might even keep both loaded if quantized small enough

(e.g., Qwen3-VL 8B Q4 ~ 3GB + GPT-OSS 20B Q4 ~ 10GB = ~13GB, which is fine).
The llama-swap web UI is available at  http://localhost:8080/ui  for monitoring. This can

•

show logs and which models are active.

•

Essentially, llama-swap gives you a local “OpenAI API” server that can handle multiple models

seamlessly,  which  is  great  for  development  and  testing.  It  eliminates  the  hassle  of  manually

loading models each time; you just specify the model name in your API call or UI dropdown and

it handles the rest.

•

Prompting and Utilizing Models Locally:

•

GPT-OSS on Mac: Once running via llama.cpp, you can prompt it like any chat model. Keep in

mind GPT-OSS was trained with a certain prompt format (the Harmony format or a system

message, etc.) – but Unsloth’s GGUF likely includes a fixed prompt template for it. If using the
OpenAI API compatibility through llama-swap, you can just provide  messages=[...]  and it

should behave reasonably (llama.cpp’s server has a built-in OpenAI-compatible chat handling; it

might use a default prompt template for chat completion). You may need to experiment a bit to

see if the model expects a specific system token. The Unsloth documentation mentions they

applied chat template fixes to their GGUFs

5

 so that usage via jinja templates works well. So

likely it will behave similar to other chat models out-of-the-box.

•

Qwen3-VL on Mac: Using it locally means you can do vision-and-language tasks. llama.cpp with

multi-modal allows you to input an image by specifying a special token. In the CLI, Unsloth did it
interactively with  /image  command. For programmatic use, if you use the OpenAI API

16

approach, I suspect there’s an extension: possibly the image is sent as part of the prompt with a

special tag or you might first call an endpoint to upload the image. This isn’t standard OpenAI

API (OpenAI’s API doesn’t support image input in chat completions at the moment), but

llama.cpp’s server might have a way (maybe not via OpenAI endpoint, perhaps via the custom

endpoints). If needed, you can use the raw llama.cpp CLI for Qwen3-VL: e.g.:

./main -m Qwen3-VL-8B-Instruct.gguf --mmproj Qwen3-VL-8B-mmproj.gguf -p

"<img_path>/path/to/dashboard.png</img_path> Explain what this dashboard

shows."

(This is speculative; the actual syntax might differ). It could also require encoding the image to

base64 and including as a special token. Checking Qwen’s documentation from Alibaba might

reveal the intended usage. Since Unsloth’s interactive method is known, one could script it: first

issue a special token to load image, then the question. For simplicity, if using swap’s UI, one

could implement a small hack: load the image separately via a command-line then ask through

UI. Given this complexity, a pragmatic approach on Mac: use Qwen3-VL’s abilities for still images

by running the CLI manually when needed, since automating image queries via API is not trivial.

•

Both models will run slower than on an A100 GPU, but Apple’s 20-core GPU + 48GB memory is
quite capable. Expect something like 5–10 tokens/sec for 20B at 4-bit on Mac (just an estimate).

Qwen3-VL 8B will be faster per token, but each image will also incur some processing (the vision

module forward pass). Still, for moderate-length outputs this is fine.

•

Local Fine-tuning Options: Even on Mac, you have some finetuning or quantization abilities:

•

Quantization on Mac: You can quantize models on the Mac itself using llama.cpp’s  quantize

tool. However, quantizing a large model can be slow and requires loading the full FP16 model in
RAM (which for 20B is ~40GB – fits in 48GB, but leaves little else). It’s doable: you’d run  ./
quantize model-f16.gguf model-q4.gguf q4_K_M  for example. It might take tens of

minutes. It might be easier to quantize on a beefier machine or download a pre-quantized

version (as we assumed).

•

Fine-tuning on Mac: 48GB RAM is quite a lot, but remember the M-series GPU is not as fast as

discrete GPUs. You could fine-tune smaller models on CPU/GPU. For example, CryptoBERT or

Qwen3-Bifrost 4B could potentially be fine-tuned on the Mac’s GPU using MPS. PyTorch MPS

backend supports training, though it’s not as optimized as CUDA. It would work for small models

– one might get away with it for experimentation. For larger models like 8B or 20B, training on

Mac is generally not practical due to speed, even if memory suffices (it would be very slow and

MPS might not handle autograd for 4-bit quant yet). However, you could do inference fine on

those quantized models as we plan.

•

LoRA on Mac: If you really want to fine-tune, say, the 8B model on Mac, you could try a LoRA

approach with a very low LR and small batch, using CPU offloading. PEFT with MPS is not well-
tested, but you could attempt: load model with  device_map={"": "mps"}  and do
.to("mps")  and train. The 48GB unified memory might hold an 8B model in 16-bit (~16GB)

plus overhead. It’s borderline but possible. The training would be slow (maybe single-digit it/s).

So, for serious fine-tuning, using Thundercompute or another GPU is recommended (which we

did in earlier parts). On Mac, stick to prompt generation and perhaps very minor fine-tune

experiments.

•

Prompt tuning / lora merging: Another local option is lora merging or switching. Because llama-

swap   can   hot-swap   models,   you   could   even   have   different   LoRA   versions   of   a   model   and

dynamically choose them. For example, you could keep base GPT-OSS and have different LoRA

17

deltas for different styles, and swap which one is merged depending on the request. llama-swap

doesn’t   natively   do   LoRA   merging   on   the   fly,   but   you   could   pre-merge   and   host   each   as   a

separate model ID. This is more of an advanced use-case, but worth noting if you have multiple

fine-tuned variants.

•

Reproducibility and Performance on Mac:  Running locally introduces variability (background

processes, thermal throttling on a laptop, etc.). For reproducible prompting, set the random seed
in llama.cpp ( -r <seed>  in CLI or via API provide  temperature  and  top_p  but seed might

not   be   exposed   in   OpenAI   API   mode   –   you   might   have   to   use   the   raw   llama.cpp   CLI   for

deterministic output with a given seed). The Mac’s Metal backend is deterministic as far as we

know, but small differences can occur vs. CUDA.

•

With 48GB RAM, you have flexibility to choose quantization vs full precision. Full FP16 inference

for a 20B model would be ~40GB – it might just fit, but it will be very slow on CPU. The Metal

GPU can’t do 16-bit for such a model due to limited cores. So quantization is key to speed. A

good compromise might be 4-bit weight quant with some 16-bit activations, which llama.cpp

does by default (it uses FP16 for activations). Higher quant (like Q6_K) might improve quality if

speed is tolerable. You can experiment with different quant files – the table from the HF repo

shows options. If you want the absolute best quality and can accept slower gen, Q8_0 (8-bit)

quant is nearly lossless and would be ~two times bigger than 4-bit. On 48GB RAM, you could

even load GPT-OSS 20B in Q8 (which might be ~20+ GB) and still have room.

•

Make sure to use Metal acceleration (on by default when compiled with MPS). If you see the

GPU memory not being utilized and CPU pegged, then something is wrong – possibly you didn’t
compile for MPS correctly. With correct setup, you should see  Using Apple Metal  in output

and ~ (model size) memory wired on the Mac.

•

For multi-modal, test a simple image prompt on Qwen3-VL to ensure it actually processes it. For

example,   try   an   image   with   clear   content   (like   a   screenshot   of   a   price   chart)   and   ask   a

straightforward   question.   Compare   the   answer   with   expectation.   Multi-modal   models   can

sometimes require prompt engineering (maybe something like: "Image: <describe image or just

ensure   the   image   is   provided>   Question:   ...   Answer:").   Consult   any   Qwen-VL   examples   from

Alibaba for the best format.

•

Conclusion (Local Workflow): With llama.cpp and llama-swap, a MacBook with ample memory

becomes a mini server for your fine-tuned models. You can chat with GPT-OSS about crypto

news, then ask Qwen3-VL to analyze a chart screenshot – all locally. While training these models

on Mac is not practical beyond small scale, quantized  inference is very feasible and convenient.

This setup is reproducible (no external API needed) and private (data stays local). It’s a great way

to test your fine-tuned models in an environment similar to production, and using llama-swap’s

OpenAI-compatible   API   means   you   can   even   integrate   it   with   tools   or   apps   that   expect   an

OpenAI API (just point them to your local endpoint).

In summary, we have mapped data types to each model’s capabilities (Part A) and provided detailed

plans to fine-tune those models in both cloud (Thundercompute with Unsloth or HF trainers) and local

(llama.cpp   on   Mac)   environments.   Following   these   plans   will   ensure   that   each   model   is   tuned   with

appropriate data and methods, while respecting hardware constraints and leveraging optimizations like

LoRA/QLoRA. By documenting each step and using the cited tools, one can confidently reproduce the

fine-tuning and deploy the models for various crypto-related NLP tasks.

18

1

ElKulako/cryptobert · Hugging Face

https://huggingface.co/ElKulako/cryptobert

2

3

5

gpt-oss: How to Run & Fine-tune | Unsloth Documentation

https://docs.unsloth.ai/models/gpt-oss-how-to-run-and-fine-tune

4

Qwen3-VL: Run & Fine-tune | Unsloth Documentation

https://docs.unsloth.ai/models/qwen3-vl-run-and-fine-tune

19


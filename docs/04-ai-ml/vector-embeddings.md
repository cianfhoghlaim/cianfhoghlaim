---
title: "Vector Embeddings & Semantic Search"
domain: ai_ml
date: 2026-06-06
migration_source: docs/bunchloch/meaisínfhoghlaim + docs/bunchloch/teanga
ccc_query_hints: ["vector embeddings lancedb qdrant semantic search ducklake iceberg vector database"]
source_files: "11 files from meaisínfhoghlaim and teanga"
---
# Vector Embeddings & Semantic Search

> Merged from 11 source files across the meaisínfhoghlaim and teanga document collections. Migration date: 2026-06-06.

## Table of Contents

- [transformers](#transformers-md)
- [ai-compute-allocation-strategy](#ai-compute-allocation-strategy-md)
- [Asset Management for Full-Stack App](#asset-management-for-full-stack-app-md)
- [geoai-Geospatial Workflow & Particle Effects(1)](#geoai-geospatial-workflow---particle-effects-1--md)
- [Geospatial Workflow & Particle Effects(1)](#geospatial-workflow---particle-effects-1--md)
- [Ibis, LanceDB, and Data Stack Integration](#ibis--lancedb--and-data-stack-integration-md)
- [From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg](#from-bi-to-ai--a-modern-lakehouse-stack-with-lance)
- [Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray](#productionalize-ai-workloads-with-lance-namespace-)
- [Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray(1)](#productionalize-ai-workloads-with-lance-namespace-)
- [Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray](#productionalize-ai-workloads-with-lance-namespace-)
- [Using MotherDuck with PlanetScale — PlanetScale](#using-motherduck-with-planetscale---planetscale-md)

---

## transformers

<!-- BEGIN: original content from transformers.md -->

*Source: `docs/bunchloch/meaisínfhoghlaim/transformers.md` (8910 words, 362 lines)*

# Transformers.js

  State-of-the-art Machine Learning for the Web

Run 🤗 Transformers directly in your browser, with no need for a server!

Transformers.js is designed to be functionally equivalent to Hugging Face's [transformers](https://github.com/huggingface/transformers) python library, meaning you can run the same pretrained models using a very similar API. These models support common tasks in different modalities, such as:
  - 📝 **Natural Language Processing**: text classification, named entity recognition, question answering, language modeling, summarization, translation, multiple choice, and text generation.
  - 🖼️ **Computer Vision**: image classification, object detection, segmentation, and depth estimation.
  - 🗣️ **Audio**: automatic speech recognition, audio classification, and text-to-speech.
  - 🐙 **Multimodal**: embeddings, zero-shot audio classification, zero-shot image classification, and zero-shot object detection.

Transformers.js uses [ONNX Runtime](https://onnxruntime.ai/) to run models in the browser. The best part about it, is that you can easily [convert](#convert-your-models-to-onnx) your pretrained PyTorch, TensorFlow, or JAX models to ONNX using [🤗 Optimum](https://github.com/huggingface/optimum#onnx--onnx-runtime). 

For more information, check out the full [documentation](https://huggingface.co/docs/transformers.js).

## Quick tour

It's super simple to translate from existing code! Just like the python library, we support the `pipeline` API. Pipelines group together a pretrained model with preprocessing of inputs and postprocessing of outputs, making it the easiest way to run models with the library.

Python (original)
Javascript (ours)

```python
from transformers import pipeline

# Allocate a pipeline for sentiment-analysis
pipe = pipeline('sentiment-analysis')

out = pipe('I love transformers!')
# [{'label': 'POSITIVE', 'score': 0.999806941}]
```

```javascript
import { pipeline } from '@huggingface/transformers';

// Allocate a pipeline for sentiment-analysis
const pipe = await pipeline('sentiment-analysis');

const out = await pipe('I love transformers!');
// [{'label': 'POSITIVE', 'score': 0.999817686}]
```

You can also use a different model by specifying the model id or path as the second argument to the `pipeline` function. For example:
```javascript
// Use a different model for sentiment-analysis
const pipe = await pipeline('sentiment-analysis', 'Xenova/bert-base-multilingual-uncased-sentiment');
```

By default, when running in the browser, the model will be run on your CPU (via WASM). If you would like
to run the model on your GPU (via WebGPU), you can do this by setting `device: 'webgpu'`, for example:
```javascript
// Run the model on WebGPU
const pipe = await pipeline('sentiment-analysis', 'Xenova/distilbert-base-uncased-finetuned-sst-2-english', {
  device: 'webgpu',
});
```

For more information, check out the [WebGPU guide](./guides/webgpu).

> [!WARNING]
> The WebGPU API is still experimental in many browsers, so if you run into any issues,
> please file a [bug report](https://github.com/huggingface/transformers.js/issues/new?title=%5BWebGPU%5D%20Error%20running%20MODEL_ID_GOES_HERE&assignees=&labels=bug,webgpu&projects=&template=1_bug-report.yml).

In resource-constrained environments, such as web browsers, it is advisable to use a quantized version of
the model to lower bandwidth and optimize performance. This can be achieved by adjusting the `dtype` option,
which allows you to select the appropriate data type for your model. While the available options may vary
depending on the specific model, typical choices include `"fp32"` (default for WebGPU), `"fp16"`, `"q8"`
(default for WASM), and `"q4"`. For more information, check out the [quantization guide](./guides/dtypes).
```javascript
// Run the model at 4-bit quantization
const pipe = await pipeline('sentiment-analysis', 'Xenova/distilbert-base-uncased-finetuned-sst-2-english', {
  dtype: 'q4',
});
```

## Contents

The documentation is organized into 4 sections:
1. **GET STARTED** provides a quick tour of the library and installation instructions to get up and running.
2. **TUTORIALS** are a great place to start if you're a beginner! We also include sample applications for you to play around with!
3. **DEVELOPER GUIDES** show you how to use the library to achieve a specific goal.
4. **API REFERENCE** describes all classes and functions, as well as their available parameters and types.

## Examples

Want to jump straight in? Get started with one of our sample applications/templates, which can be found [here](https://github.com/huggingface/transformers.js-examples).

| Name              | Description                      | Links                   |
|-------------------|----------------------------------|-------------------------------|
| Whisper Web       | Speech recognition w/ Whisper    | [code](https://github.com/xenova/whisper-web), [demo](https://huggingface.co/spaces/Xenova/whisper-web) |
| Doodle Dash       | Real-time sketch-recognition game | [blog](https://huggingface.co/blog/ml-web-games), [code](https://github.com/xenova/doodle-dash), [demo](https://huggingface.co/spaces/Xenova/doodle-dash) |
| Code Playground   | In-browser code completion website | [code](https://github.com/huggingface/transformers.js/tree/main/examples/code-completion/), [demo](https://huggingface.co/spaces/Xenova/ai-code-playground) |
| Semantic Image Search (client-side) | Search for images with text | [code](https://github.com/huggingface/transformers.js/tree/main/examples/semantic-image-search-client/), [demo](https://huggingface.co/spaces/Xenova/semantic-image-search-client) |
| Semantic Image Search (server-side) | Search for images with text (Supabase) | [code](https://github.com/huggingface/transformers.js/tree/main/examples/semantic-image-search/), [demo](https://huggingface.co/spaces/Xenova/semantic-image-search) |
| Vanilla JavaScript | In-browser object detection     | [video](https://scrimba.com/scrim/cKm9bDAg), [code](https://github.com/huggingface/transformers.js/tree/main/examples/vanilla-js/), [demo](https://huggingface.co/spaces/Scrimba/vanilla-js-object-detector) |
| React             | Multilingual translation website | [code](https://github.com/huggingface/transformers.js/tree/main/examples/react-translator/), [demo](https://huggingface.co/spaces/Xenova/react-translator) |
| Text to speech (client-side) | In-browser speech synthesis | [code](https://github.com/huggingface/transformers.js/tree/main/examples/text-to-speech-client/), [demo](https://huggingface.co/spaces/Xenova/text-to-speech-client) |
| Browser extension | Text classification extension    | [code](https://github.com/huggingface/transformers.js/tree/main/examples/extension/) |
| Electron          | Text classification application  | [code](https://github.com/huggingface/transformers.js/tree/main/examples/electron/)  |
| Next.js (client-side) | Sentiment analysis (in-browser inference) | [code](https://github.com/huggingface/transformers.js/tree/main/examples/next-client/), [demo](https://huggingface.co/spaces/Xenova/next-example-app) |
| Next.js (server-side) | Sentiment analysis (Node.js inference) | [code](https://github.com/huggingface/transformers.js/tree/main/examples/next-server/), [demo](https://huggingface.co/spaces/Xenova/next-server-example-app) |
| Node.js           | Sentiment analysis API           | [code](https://github.com/huggingface/transformers.js/tree/main/examples/node/)      |
| Demo site         | A collection of demos | [code](https://github.com/huggingface/transformers.js/tree/main/examples/demo-site/), [demo](https://huggingface.github.io/transformers.js/) |

Check out the Transformers.js [template](https://huggingface.co/new-space?template=static-templates%2Ftransformers.js) on Hugging Face to get started in one click!

## Supported tasks/models

Here is the list of all tasks and architectures currently supported by Transformers.js.
If you don't see your task/model listed here or it is not yet supported, feel free
to open up a feature request [here](https://github.com/huggingface/transformers.js/issues/new/choose).

To find compatible models on the Hub, select the "transformers.js" library tag in the filter menu (or visit [this link](https://huggingface.co/models?library=transformers.js)).
You can refine your search by selecting the task you're interested in (e.g., [text-classification](https://huggingface.co/models?pipeline_tag=text-classification&library=transformers.js)).

### Tasks

#### Natural Language Processing

| Task                     | ID | Description | Supported? |
|--------------------------|----|-------------|------------|
| [Fill-Mask](https://huggingface.co/tasks/fill-mask)                     | `fill-mask`   | Masking some of the words in a sentence and predicting which words should replace those masks. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.FillMaskPipeline)[(models)](https://huggingface.co/models?pipeline_tag=fill-mask&library=transformers.js) |
| [Question Answering](https://huggingface.co/tasks/question-answering)   | `question-answering`   | Retrieve the answer to a question from a given text. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.QuestionAnsweringPipeline)[(models)](https://huggingface.co/models?pipeline_tag=question-answering&library=transformers.js) |
| [Sentence Similarity](https://huggingface.co/tasks/sentence-similarity) | `sentence-similarity`  | Determining how similar two texts are. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.FeatureExtractionPipeline)[(models)](https://huggingface.co/models?pipeline_tag=sentence-similarity&library=transformers.js) |
| [Summarization](https://huggingface.co/tasks/summarization)             |  `summarization`  | Producing a shorter version of a document while preserving its important information. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.SummarizationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=summarization&library=transformers.js) |
| [Table Question Answering](https://huggingface.co/tasks/table-question-answering) |  `table-question-answering`  | Answering a question about information from a given table. | ❌ |
| [Text Classification](https://huggingface.co/tasks/text-classification)      | `text-classification` or `sentiment-analysis`  | Assigning a label or class to a given text. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.TextClassificationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=text-classification&library=transformers.js) |
| [Text Generation](https://huggingface.co/tasks/text-generation#completion-generation-models)          | `text-generation`  | Producing new text by predicting the next word in a sequence. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.TextGenerationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=text-generation&library=transformers.js) |
| [Text-to-text Generation](https://huggingface.co/tasks/text-generation#text-to-text-generation-models)  | `text2text-generation`  | Converting one text sequence into another text sequence. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.Text2TextGenerationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=text2text-generation&library=transformers.js) |
| [Token Classification](https://huggingface.co/tasks/token-classification)     | `token-classification` or `ner`  | Assigning a label to each token in a text. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.TokenClassificationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=token-classification&library=transformers.js) |
| [Translation](https://huggingface.co/tasks/translation)              |  `translation`  | Converting text from one language to another. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.TranslationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=translation&library=transformers.js) |
| [Zero-Shot Classification](https://huggingface.co/tasks/zero-shot-classification) | `zero-shot-classification`  | Classifying text into classes that are unseen during training.  | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ZeroShotClassificationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=zero-shot-classification&library=transformers.js) |
| [Feature Extraction](https://huggingface.co/tasks/feature-extraction)         |  `feature-extraction`  | Transforming raw data into numerical features that can be processed while preserving the information in the original dataset. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.FeatureExtractionPipeline)[(models)](https://huggingface.co/models?pipeline_tag=feature-extraction&library=transformers.js) |

#### Vision

| Task                     | ID | Description | Supported? |
|--------------------------|----|-------------|------------|
| [Background Removal](https://huggingface.co/tasks/image-segmentation#background-removal)       | `background-removal`   | Isolating the main subject of an image by removing or making the background transparent. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.BackgroundRemovalPipeline)[(models)](https://huggingface.co/models?other=background-removal&library=transformers.js) |
| [Depth Estimation](https://huggingface.co/tasks/depth-estimation)         |  `depth-estimation`  | Predicting the depth of objects present in an image. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.DepthEstimationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=depth-estimation&library=transformers.js) |
| [Image Classification](https://huggingface.co/tasks/image-classification)                | `image-classification`   | Assigning a label or class to an entire image. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ImageClassificationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=image-classification&library=transformers.js) |
| [Image Segmentation](https://huggingface.co/tasks/image-segmentation)       | `image-segmentation`   | Divides an image into segments where each pixel is mapped to an object. This task has multiple variants such as instance segmentation, panoptic segmentation and semantic segmentation. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ImageSegmentationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=image-segmentation&library=transformers.js) |
| [Image-to-Image](https://huggingface.co/tasks/image-to-image)      |  `image-to-image` | Transforming a source image to match the characteristics of a target image or a target image domain. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ImageToImagePipeline)[(models)](https://huggingface.co/models?pipeline_tag=image-to-image&library=transformers.js) |
| [Mask Generation](https://huggingface.co/tasks/mask-generation)            |  `mask-generation`  | Generate masks for the objects in an image. | ❌ |
| [Object Detection](https://huggingface.co/tasks/object-detection)            | `object-detection`   | Identify objects of certain defined classes within an image. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ObjectDetectionPipeline)[(models)](https://huggingface.co/models?pipeline_tag=object-detection&library=transformers.js) |
| [Video Classification](https://huggingface.co/tasks/video-classification) |  n/a  | Assigning a label or class to an entire video. | ❌ |
| [Unconditional Image Generation](https://huggingface.co/tasks/unconditional-image-generation)      |  n/a   | Generating images with no condition in any context (like a prompt text or another image). | ❌ |
| [Image Feature Extraction](https://huggingface.co/tasks/image-feature-extraction)         |  `image-feature-extraction`  | Transforming raw data into numerical features that can be processed while preserving the information in the original image. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ImageFeatureExtractionPipeline)[(models)](https://huggingface.co/models?pipeline_tag=image-feature-extraction&library=transformers.js) |

#### Audio

| Task                     | ID | Description | Supported? |
|--------------------------|----|-------------|------------|
| [Audio Classification](https://huggingface.co/tasks/audio-classification)         |  `audio-classification`  | Assigning a label or class to a given audio. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.AudioClassificationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=audio-classification&library=transformers.js) |
| [Audio-to-Audio](https://huggingface.co/tasks/audio-to-audio)         |  n/a  | Generating audio from an input audio source. | ❌ |
| [Automatic Speech Recognition](https://huggingface.co/tasks/automatic-speech-recognition)         | `automatic-speech-recognition`  | Transcribing a given audio into text. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.AutomaticSpeechRecognitionPipeline)[(models)](https://huggingface.co/models?pipeline_tag=automatic-speech-recognition&library=transformers.js) |
| [Text-to-Speech](https://huggingface.co/tasks/text-to-speech)         | `text-to-speech` or `text-to-audio` | Generating natural-sounding speech given text input. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.TextToAudioPipeline)[(models)](https://huggingface.co/models?pipeline_tag=text-to-audio&library=transformers.js) |

#### Tabular

| Task                     | ID | Description | Supported? |
|--------------------------|----|-------------|------------|
| [Tabular Classification](https://huggingface.co/tasks/tabular-classification)         |  n/a  | Classifying a target category (a group) based on set of attributes. | ❌ |
| [Tabular Regression](https://huggingface.co/tasks/tabular-regression)         |  n/a  | Predicting a numerical value given a set of attributes. | ❌ |

#### Multimodal

| Task                     | ID | Description | Supported? |
|--------------------------|----|-------------|------------|
| [Document Question Answering](https://huggingface.co/tasks/document-question-answering)         | `document-question-answering`  | Answering questions on document images. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.DocumentQuestionAnsweringPipeline)[(models)](https://huggingface.co/models?pipeline_tag=document-question-answering&library=transformers.js) |
| [Image-to-Text](https://huggingface.co/tasks/image-to-text)         |  `image-to-text`  | Output text from a given image. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ImageToTextPipeline)[(models)](https://huggingface.co/models?pipeline_tag=image-to-text&library=transformers.js) |
| [Text-to-Image](https://huggingface.co/tasks/text-to-image)         |  `text-to-image`  | Generates images from input text.  | ❌ |
| [Visual Question Answering](https://huggingface.co/tasks/visual-question-answering)         |  `visual-question-answering`  | Answering open-ended questions based on an image. | ❌ |
| [Zero-Shot Audio Classification](https://huggingface.co/learn/audio-course/chapter4/classification_models#zero-shot-audio-classification) | `zero-shot-audio-classification`  | Classifying audios into classes that are unseen during training. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ZeroShotAudioClassificationPipeline)[(models)](https://huggingface.co/models?other=zero-shot-audio-classification&library=transformers.js) |
| [Zero-Shot Image Classification](https://huggingface.co/tasks/zero-shot-image-classification) | `zero-shot-image-classification`  | Classifying images into classes that are unseen during training. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ZeroShotImageClassificationPipeline)[(models)](https://huggingface.co/models?pipeline_tag=zero-shot-image-classification&library=transformers.js) |
| [Zero-Shot Object Detection](https://huggingface.co/tasks/zero-shot-object-detection) | `zero-shot-object-detection`  | Identify objects of classes that are unseen during training. | ✅ [(docs)](https://huggingface.co/docs/transformers.js/api/pipelines#module_pipelines.ZeroShotObjectDetectionPipeline)[(models)](https://huggingface.co/models?other=zero-shot-object-detection&library=transformers.js) |

#### Reinforcement Learning

| Task                     | ID | Description | Supported? |
|--------------------------|----|-------------|------------|
| [Reinforcement Learning](https://huggingface.co/tasks/reinforcement-learning)   |  n/a  | Learning from actions by interacting with an environment through trial and error and receiving rewards (negative or positive) as feedback. | ✅ |

### Models

1. **[ALBERT](https://huggingface.co/docs/transformers/model_doc/albert)** (from Google Research and the Toyota Technological Institute at Chicago) released with the paper [ALBERT: A Lite BERT for Self-supervised Learning of Language Representations](https://huggingface.co/papers/1909.11942), by Zhenzhong Lan, Mingda Chen, Sebastian Goodman, Kevin Gimpel, Piyush Sharma, Radu Soricut.
1. **[Arcee](https://huggingface.co/docs/transformers/model_doc/arcee)** (from Arcee AI) released with the blog post [Announcing Arcee Foundation Models](https://www.arcee.ai/blog/announcing-the-arcee-foundation-model-family) by Fernando Fernandes, Varun Singh, Charles Goddard, Lucas Atkins, Mark McQuade, Maziyar Panahi, Conner Stewart, Colin Kealty, Raghav Ravishankar, Lucas Krauss, Anneketh Vij, Pranav Veldurthi, Abhishek Thakur, Julien Simon, Scott Zembsch, Benjamin Langer, Aleksiej Cecocho, Maitri Patel.
1. **[Audio Spectrogram Transformer](https://huggingface.co/docs/transformers/model_doc/audio-spectrogram-transformer)** (from MIT) released with the paper [AST: Audio Spectrogram Transformer](https://huggingface.co/papers/2104.01778) by Yuan Gong, Yu-An Chung, James Glass.
1. **[BART](https://huggingface.co/docs/transformers/model_doc/bart)** (from Facebook) released with the paper [BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension](https://huggingface.co/papers/1910.13461) by Mike Lewis, Yinhan Liu, Naman Goyal, Marjan Ghazvininejad, Abdelrahman Mohamed, Omer Levy, Ves Stoyanov and Luke Zettlemoyer.
1. **[BEiT](https://huggingface.co/docs/transformers/model_doc/beit)** (from Microsoft) released with the paper [BEiT: BERT Pre-Training of Image Transformers](https://huggingface.co/papers/2106.08254) by Hangbo Bao, Li Dong, Furu Wei.
1. **[BERT](https://huggingface.co/docs/transformers/model_doc/bert)** (from Google) released with the paper [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://huggingface.co/papers/1810.04805) by Jacob Devlin, Ming-Wei Chang, Kenton Lee and Kristina Toutanova.
1. **[Blenderbot](https://huggingface.co/docs/transformers/model_doc/blenderbot)** (from Facebook) released with the paper [Recipes for building an open-domain chatbot](https://huggingface.co/papers/2004.13637) by Stephen Roller, Emily Dinan, Naman Goyal, Da Ju, Mary Williamson, Yinhan Liu, Jing Xu, Myle Ott, Kurt Shuster, Eric M. Smith, Y-Lan Boureau, Jason Weston.
1. **[BlenderbotSmall](https://huggingface.co/docs/transformers/model_doc/blenderbot-small)** (from Facebook) released with the paper [Recipes for building an open-domain chatbot](https://huggingface.co/papers/2004.13637) by Stephen Roller, Emily Dinan, Naman Goyal, Da Ju, Mary Williamson, Yinhan Liu, Jing Xu, Myle Ott, Kurt Shuster, Eric M. Smith, Y-Lan Boureau, Jason Weston.
1. **[BLOOM](https://huggingface.co/docs/transformers/model_doc/bloom)** (from BigScience workshop) released by the [BigScience Workshop](https://bigscience.huggingface.co/).
1. **[CamemBERT](https://huggingface.co/docs/transformers/model_doc/camembert)** (from Inria/Facebook/Sorbonne) released with the paper [CamemBERT: a Tasty French Language Model](https://huggingface.co/papers/1911.03894) by Louis Martin*, Benjamin Muller*, Pedro Javier Ortiz Suárez*, Yoann Dupont, Laurent Romary, Éric Villemonte de la Clergerie, Djamé Seddah and Benoît Sagot.
1. **[Chinese-CLIP](https://huggingface.co/docs/transformers/model_doc/chinese_clip)** (from OFA-Sys) released with the paper [Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese](https://huggingface.co/papers/2211.01335) by An Yang, Junshu Pan, Junyang Lin, Rui Men, Yichang Zhang, Jingren Zhou, Chang Zhou.
1. **[CLAP](https://huggingface.co/docs/transformers/model_doc/clap)** (from LAION-AI) released with the paper [Large-scale Contrastive Language-Audio Pretraining with Feature Fusion and Keyword-to-Caption Augmentation](https://huggingface.co/papers/2211.06687) by Yusong Wu, Ke Chen, Tianyu Zhang, Yuchen Hui, Taylor Berg-Kirkpatrick, Shlomo Dubnov.
1. **[CLIP](https://huggingface.co/docs/transformers/model_doc/clip)** (from OpenAI) released with the paper [Learning Transferable Visual Models From Natural Language Supervision](https://huggingface.co/papers/2103.00020) by Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, Ilya Sutskever.
1. **[CLIPSeg](https://huggingface.co/docs/transformers/model_doc/clipseg)** (from University of Göttingen) released with the paper [Image Segmentation Using Text and Image Prompts](https://huggingface.co/papers/2112.10003) by Timo Lüddecke and Alexander Ecker.
1. **[CodeGen](https://huggingface.co/docs/transformers/model_doc/codegen)** (from Salesforce) released with the paper [A Conversational Paradigm for Program Synthesis](https://huggingface.co/papers/2203.13474) by Erik Nijkamp, Bo Pang, Hiroaki Hayashi, Lifu Tu, Huan Wang, Yingbo Zhou, Silvio Savarese, Caiming Xiong.
1. **[CodeLlama](https://huggingface.co/docs/transformers/model_doc/llama_code)** (from MetaAI) released with the paper [Code Llama: Open Foundation Models for Code](https://ai.meta.com/research/publications/code-llama-open-foundation-models-for-code/) by Baptiste Rozière, Jonas Gehring, Fabian Gloeckle, Sten Sootla, Itai Gat, Xiaoqing Ellen Tan, Yossi Adi, Jingyu Liu, Tal Remez, Jérémy Rapin, Artyom Kozhevnikov, Ivan Evtimov, Joanna Bitton, Manish Bhatt, Cristian Canton Ferrer, Aaron Grattafiori, Wenhan Xiong, Alexandre Défossez, Jade Copet, Faisal Azhar, Hugo Touvron, Louis Martin, Nicolas Usunier, Thomas Scialom, Gabriel Synnaeve.
1. **[Cohere](https://huggingface.co/docs/transformers/main/model_doc/cohere)** (from Cohere) released with the paper [Command-R: Retrieval Augmented Generation at Production Scale]() by Cohere.
1. **[ConvBERT](https://huggingface.co/docs/transformers/model_doc/convbert)** (from YituTech) released with the paper [ConvBERT: Improving BERT with Span-based Dynamic Convolution](https://huggingface.co/papers/2008.02496) by Zihang Jiang, Weihao Yu, Daquan Zhou, Yunpeng Chen, Jiashi Feng, Shuicheng Yan.
1. **[ConvNeXT](https://huggingface.co/docs/transformers/model_doc/convnext)** (from Facebook AI) released with the paper [A ConvNet for the 2020s](https://huggingface.co/papers/2201.03545) by Zhuang Liu, Hanzi Mao, Chao-Yuan Wu, Christoph Feichtenhofer, Trevor Darrell, Saining Xie.
1. **[ConvNeXTV2](https://huggingface.co/docs/transformers/model_doc/convnextv2)** (from Facebook AI) released with the paper [ConvNeXt V2: Co-designing and Scaling ConvNets with Masked Autoencoders](https://huggingface.co/papers/2301.00808) by Sanghyun Woo, Shoubhik Debnath, Ronghang Hu, Xinlei Chen, Zhuang Liu, In So Kweon, Saining Xie.
1. **[D-FINE](https://huggingface.co/docs/transformers/model_doc/d_fine)** (from University of Science and Technology of China) released with the paper [D-FINE: Redefine Regression Task in DETRs as Fine-grained Distribution Refinement](https://huggingface.co/papers/2410.13842) by Yansong Peng, Hebei Li, Peixi Wu, Yueyi Zhang, Xiaoyan Sun, Feng Wu.
1. **[DAC](https://huggingface.co/docs/transformers/model_doc/dac)** (from Descript) released with the paper [Descript Audio Codec: High-Fidelity Audio Compression with Improved RVQGAN](https://huggingface.co/papers/2306.06546) by Rithesh Kumar, Prem Seetharaman, Alejandro Luebs, Ishaan Kumar, Kundan Kumar.
1. **[DeBERTa](https://huggingface.co/docs/transformers/model_doc/deberta)** (from Microsoft) released with the paper [DeBERTa: Decoding-enhanced BERT with Disentangled Attention](https://huggingface.co/papers/2006.03654) by Pengcheng He, Xiaodong Liu, Jianfeng Gao, Weizhu Chen.
1. **[DeBERTa-v2](https://huggingface.co/docs/transformers/model_doc/deberta-v2)** (from Microsoft) released with the paper [DeBERTa: Decoding-enhanced BERT with Disentangled Attention](https://huggingface.co/papers/2006.03654) by Pengcheng He, Xiaodong Liu, Jianfeng Gao, Weizhu Chen.
1. **[Decision Transformer](https://huggingface.co/docs/transformers/model_doc/decision_transformer)** (from Berkeley/Facebook/Google) released with the paper [Decision Transformer: Reinforcement Learning via Sequence Modeling](https://huggingface.co/papers/2106.01345) by Lili Chen, Kevin Lu, Aravind Rajeswaran, Kimin Lee, Aditya Grover, Michael Laskin, Pieter Abbeel, Aravind Srinivas, Igor Mordatch.
1. **[DeiT](https://huggingface.co/docs/transformers/model_doc/deit)** (from Facebook) released with the paper [Training data-efficient image transformers & distillation through attention](https://huggingface.co/papers/2012.12877) by Hugo Touvron, Matthieu Cord, Matthijs Douze, Francisco Massa, Alexandre Sablayrolles, Hervé Jégou.
1. **[Depth Anything](https://huggingface.co/docs/transformers/main/model_doc/depth_anything)** (from University of Hong Kong and TikTok) released with the paper [Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data](https://huggingface.co/papers/2401.10891) by Lihe Yang, Bingyi Kang, Zilong Huang, Xiaogang Xu, Jiashi Feng, Hengshuang Zhao.
1. **Depth Pro** (from Apple) released with the paper [Depth Pro: Sharp Monocular Metric Depth in Less Than a Second](https://huggingface.co/papers/2410.02073) by Aleksei Bochkovskii, Amaël Delaunoy, Hugo Germain, Marcel Santos, Yichao Zhou, Stephan R. Richter, Vladlen Koltun.
1. **[DETR](https://huggingface.co/docs/transformers/model_doc/detr)** (from Facebook) released with the paper [End-to-End Object Detection with Transformers](https://huggingface.co/papers/2005.12872) by Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas Usunier, Alexander Kirillov, Sergey Zagoruyko.
1. **[DINOv2](https://huggingface.co/docs/transformers/model_doc/dinov2)** (from Meta AI) released with the paper [DINOv2: Learning Robust Visual Features without Supervision](https://huggingface.co/papers/2304.07193) by Maxime Oquab, Timothée Darcet, Théo Moutakanni, Huy Vo, Marc Szafraniec, Vasil Khalidov, Pierre Fernandez, Daniel Haziza, Francisco Massa, Alaaeldin El-Nouby, Mahmoud Assran, Nicolas Ballas, Wojciech Galuba, Russell Howes, Po-Yao Huang, Shang-Wen Li, Ishan Misra, Michael Rabbat, Vasu Sharma, Gabriel Synnaeve, Hu Xu, Hervé Jegou, Julien Mairal, Patrick Labatut, Armand Joulin, Piotr Bojanowski.
1. **[DINOv2 with Registers](https://huggingface.co/docs/transformers/model_doc/dinov2_with_registers)** (from Meta AI) released with the paper [DINOv2 with Registers](https://huggingface.co/papers/2309.16588) by Timothée Darcet, Maxime Oquab, Julien Mairal, Piotr Bojanowski.
1. **[DINOv3](https://huggingface.co/docs/transformers/model_doc/dinov3)** (from Meta AI) released with the paper [DINOv3](https://huggingface.co/papers/2508.10104) by Oriane Siméoni, Huy V. Vo, Maximilian Seitzer, Federico Baldassarre, Maxime Oquab, Cijo Jose, Vasil Khalidov, Marc Szafraniec, Seungeun Yi, Michaël Ramamonjisoa, Francisco Massa, Daniel Haziza, Luca Wehrstedt, Jianyuan Wang, Timothée Darcet, Théo Moutakanni, Leonel Sentana, Claire Roberts, Andrea Vedaldi, Jamie Tolan, John Brandt, Camille Couprie, Julien Mairal, Hervé Jégou, Patrick Labatut, Piotr Bojanowski.
1. **[DistilBERT](https://huggingface.co/docs/transformers/model_doc/distilbert)** (from HuggingFace), released together with the paper [DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter](https://huggingface.co/papers/1910.01108) by Victor Sanh, Lysandre Debut and Thomas Wolf. The same method has been applied to compress GPT2 into [DistilGPT2](https://github.com/huggingface/transformers/tree/main/examples/research_projects/distillation), RoBERTa into [DistilRoBERTa](https://github.com/huggingface/transformers/tree/main/examples/research_projects/distillation), Multilingual BERT into [DistilmBERT](https://github.com/huggingface/transformers/tree/main/examples/research_projects/distillation) and a German version of DistilBERT.
1. **[DiT](https://huggingface.co/docs/transformers/model_doc/dit)** (from Microsoft Research) released with the paper [DiT: Self-supervised Pre-training for Document Image Transformer](https://huggingface.co/papers/2203.02378) by Junlong Li, Yiheng Xu, Tengchao Lv, Lei Cui, Cha Zhang, Furu Wei.
1. **[Donut](https://huggingface.co/docs/transformers/model_doc/donut)** (from NAVER), released together with the paper [OCR-free Document Understanding Transformer](https://huggingface.co/papers/2111.15664) by Geewook Kim, Teakgyu Hong, Moonbin Yim, Jeongyeon Nam, Jinyoung Park, Jinyeong Yim, Wonseok Hwang, Sangdoo Yun, Dongyoon Han, Seunghyun Park.
1. **[DPT](https://huggingface.co/docs/transformers/master/model_doc/dpt)** (from Intel Labs) released with the paper [Vision Transformers for Dense Prediction](https://huggingface.co/papers/2103.13413) by René Ranftl, Alexey Bochkovskiy, Vladlen Koltun.
1. **[EdgeTAM](https://huggingface.co/docs/transformers/model_doc/edgetam)** (from Facebook) released with the paper [EdgeTAM: On-Device Track Anything Model](https://huggingface.co/papers/2501.07256) by Chong Zhou, Chenchen Zhu, Yunyang Xiong, Saksham Suri, Fanyi Xiao, Lemeng Wu, Raghuraman Krishnamoorthi, Bo Dai, Chen Change Loy, Vikas Chandra, Bilge Soran.
1. **[EfficientNet](https://huggingface.co/docs/transformers/model_doc/efficientnet)** (from Google Brain) released with the paper [EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks](https://huggingface.co/papers/1905.11946) by Mingxing Tan, Quoc V. Le.
1. **[ELECTRA](https://huggingface.co/docs/transformers/model_doc/electra)** (from Google Research/Stanford University) released with the paper [ELECTRA: Pre-training text encoders as discriminators rather than generators](https://huggingface.co/papers/2003.10555) by Kevin Clark, Minh-Thang Luong, Quoc V. Le, Christopher D. Manning.
1. **ERNIE-4.5** (from Baidu ERNIE Team) released with the blog post [Announcing the Open Source Release of the ERNIE 4.5 Model Family](https://ernie.baidu.com/blog/posts/ernie4.5/) by the Baidu ERNIE Team.
1. **[ESM](https://huggingface.co/docs/transformers/model_doc/esm)** (from Meta AI) are transformer protein language models.  **ESM-1b** was released with the paper [Biological structure and function emerge from scaling unsupervised learning to 250 million protein sequences](https://www.pnas.org/content/118/15/e2016239118) by Alexander Rives, Joshua Meier, Tom Sercu, Siddharth Goyal, Zeming Lin, Jason Liu, Demi Guo, Myle Ott, C. Lawrence Zitnick, Jerry Ma, and Rob Fergus. **ESM-1v** was released with the paper [Language models enable zero-shot prediction of the effects of mutations on protein function](https://doi.org/10.1101/2021.07.09.450648) by Joshua Meier, Roshan Rao, Robert Verkuil, Jason Liu, Tom Sercu and Alexander Rives. **ESM-2 and ESMFold** were released with the paper [Language models of protein sequences at the scale of evolution enable accurate structure prediction](https://doi.org/10.1101/2022.07.20.500902) by Zeming Lin, Halil Akin, Roshan Rao, Brian Hie, Zhongkai Zhu, Wenting Lu, Allan dos Santos Costa, Maryam Fazel-Zarandi, Tom Sercu, Sal Candido, Alexander Rives.
1. **EXAONE** (from LG AI Research) released with the papers [EXAONE 3.0 7.8B Instruction Tuned Language Model](https://huggingface.co/papers/2408.03541) and [EXAONE 3.5: Series of Large Language Models for Real-world Use Cases](https://huggingface.co/papers/2412.04862) by the LG AI Research team.
1. **[Falcon](https://huggingface.co/docs/transformers/model_doc/falcon)** (from Technology Innovation Institute) by Almazrouei, Ebtesam and Alobeidli, Hamza and Alshamsi, Abdulaziz and Cappelli, Alessandro and Cojocaru, Ruxandra and Debbah, Merouane and Goffinet, Etienne and Heslow, Daniel and Launay, Julien and Malartic, Quentin and Noune, Badreddine and Pannier, Baptiste and Penedo, Guilherme.
1. **FastViT** (from Apple) released with the paper [FastViT: A Fast Hybrid Vision Transformer using Structural Reparameterization](https://huggingface.co/papers/2303.14189) by Pavan Kumar Anasosalu Vasu, James Gabriel, Jeff Zhu, Oncel Tuzel and Anurag Ranjan.
1. **[FLAN-T5](https://huggingface.co/docs/transformers/model_doc/flan-t5)** (from Google AI) released in the repository [google-research/t5x](https://github.com/google-research/t5x/blob/main/docs/models.md#flan-t5-checkpoints) by Hyung Won Chung, Le Hou, Shayne Longpre, Barret Zoph, Yi Tay, William Fedus, Eric Li, Xuezhi Wang, Mostafa Dehghani, Siddhartha Brahma, Albert Webson, Shixiang Shane Gu, Zhuyun Dai, Mirac Suzgun, Xinyun Chen, Aakanksha Chowdhery, Sharan Narang, Gaurav Mishra, Adams Yu, Vincent Zhao, Yanping Huang, Andrew Dai, Hongkun Yu, Slav Petrov, Ed H. Chi, Jeff Dean, Jacob Devlin, Adam Roberts, Denny Zhou, Quoc V. Le, and Jason Wei
1. **Florence2** (from Microsoft) released with the paper [Florence-2: Advancing a Unified Representation for a Variety of Vision Tasks](https://huggingface.co/papers/2311.06242) by Bin Xiao, Haiping Wu, Weijian Xu, Xiyang Dai, Houdong Hu, Yumao Lu, Michael Zeng, Ce Liu, Lu Yuan.
1. **[Gemma](https://huggingface.co/docs/transformers/main/model_doc/gemma)** (from Google) released with the paper [Gemma: Open Models Based on Gemini Technology and Research](https://blog.google/technology/developers/gemma-open-models/) by the Gemma Google team.
1. **[Gemma2](https://huggingface.co/docs/transformers/main/model_doc/gemma2)** (from Google) released with the paper [Gemma2: Open Models Based on Gemini Technology and Research](https://blog.google/technology/developers/google-gemma-2/) by the Gemma Google team.
1. **[Gemma3](https://huggingface.co/docs/transformers/main/model_doc/gemma3)** (from Google) released with the paper [Introducing Gemma 3: The most capable model you can run on a single GPU or TPU](https://blog.google/technology/developers/gemma-3/) by the Gemma Google team.
1. **[Gemma3n](https://huggingface.co/docs/transformers/main/model_doc/gemma3n)** (from Google) released with the paper [Announcing Gemma 3n preview: powerful, efficient, mobile-first AI](https://developers.googleblog.com/en/introducing-gemma-3n/) by the Gemma Google team.
1. **[GLM](https://huggingface.co/docs/transformers/main/model_doc/glm)** (from the GLM Team, THUDM & ZhipuAI) released with the paper [ChatGLM: A Family of Large Language Models from GLM-130B to GLM-4 All Tools](https://huggingface.co/papers/2406.12793v2) by Team GLM: Aohan Zeng, Bin Xu, Bowen Wang, Chenhui Zhang, Da Yin, Dan Zhang, Diego Rojas, Guanyu Feng, Hanlin Zhao, Hanyu Lai, Hao Yu, Hongning Wang, Jiadai Sun, Jiajie Zhang, Jiale Cheng, Jiayi Gui, Jie Tang, Jing Zhang, Jingyu Sun, Juanzi Li, Lei Zhao, Lindong Wu, Lucen Zhong, Mingdao Liu, Minlie Huang, Peng Zhang, Qinkai Zheng, Rui Lu, Shuaiqi Duan, Shudan Zhang, Shulin Cao, Shuxun Yang, Weng Lam Tam, Wenyi Zhao, Xiao Liu, Xiao Xia, Xiaohan Zhang, Xiaotao Gu, Xin Lv, Xinghan Liu, Xinyi Liu, Xinyue Yang, Xixuan Song, Xunkai Zhang, Yifan An, Yifan Xu, Yilin Niu, Yuantao Yang, Yueyan Li, Yushi Bai, Yuxiao Dong, Zehan Qi, Zhaoyu Wang, Zhen Yang, Zhengxiao Du, Zhenyu Hou, Zihan Wang.
1. **[GLPN](https://huggingface.co/docs/transformers/model_doc/glpn)** (from KAIST) released with the paper [Global-Local Path Networks for Monocular Depth Estimation with Vertical CutDepth](https://huggingface.co/papers/2201.07436) by Doyeon Kim, Woonghyun Ga, Pyungwhan Ahn, Donggyu Joo, Sehwan Chun, Junmo Kim.
1. **[GPT Neo](https://huggingface.co/docs/transformers/model_doc/gpt_neo)** (from EleutherAI) released in the repository [EleutherAI/gpt-neo](https://github.com/EleutherAI/gpt-neo) by Sid Black, Stella Biderman, Leo Gao, Phil Wang and Connor Leahy.
1. **[GPT NeoX](https://huggingface.co/docs/transformers/model_doc/gpt_neox)** (from EleutherAI) released with the paper [GPT-NeoX-20B: An Open-Source Autoregressive Language Model](https://huggingface.co/papers/2204.06745) by Sid Black, Stella Biderman, Eric Hallahan, Quentin Anthony, Leo Gao, Laurence Golding, Horace He, Connor Leahy, Kyle McDonell, Jason Phang, Michael Pieler, USVSN Sai Prashanth, Shivanshu Purohit, Laria Reynolds, Jonathan Tow, Ben Wang, Samuel Weinbach
1. **[GPT-2](https://huggingface.co/docs/transformers/model_doc/gpt2)** (from OpenAI) released with the paper [Language Models are Unsupervised Multitask Learners](https://blog.openai.com/better-language-models/) by Alec Radford*, Jeffrey Wu*, Rewon Child, David Luan, Dario Amodei** and Ilya Sutskever**.
1. **[GPT-J](https://huggingface.co/docs/transformers/model_doc/gptj)** (from EleutherAI) released in the repository [kingoflolz/mesh-transformer-jax](https://github.com/kingoflolz/mesh-transformer-jax/) by Ben Wang and Aran Komatsuzaki.
1. **[GPTBigCode](https://huggingface.co/docs/transformers/model_doc/gpt_bigcode)** (from BigCode) released with the paper [SantaCoder: don't reach for the stars!](https://huggingface.co/papers/2301.03988) by Loubna Ben Allal, Raymond Li, Denis Kocetkov, Chenghao Mou, Christopher Akiki, Carlos Munoz Ferrandis, Niklas Muennighoff, Mayank Mishra, Alex Gu, Manan Dey, Logesh Kumar Umapathi, Carolyn Jane Anderson, Yangtian Zi, Joel Lamy Poirier, Hailey Schoelkopf, Sergey Troshin, Dmitry Abulkhanov, Manuel Romero, Michael Lappert, Francesco De Toni, Bernardo García del Río, Qian Liu, Shamik Bose, Urvashi Bhattacharyya, Terry Yue Zhuo, Ian Yu, Paulo Villegas, Marco Zocca, Sourab Mangrulkar, David Lansky, Huu Nguyen, Danish Contractor, Luis Villa, Jia Li, Dzmitry Bahdanau, Yacine Jernite, Sean Hughes, Daniel Fried, Arjun Guha, Harm de Vries, Leandro von Werra.
1. **[Granite](https://huggingface.co/docs/transformers/main/model_doc/granite)** (from IBM) released with the paper [Power Scheduler: A Batch Size and Token Number Agnostic Learning Rate Scheduler](https://huggingface.co/papers/2408.13359) by Yikang Shen, Matthew Stallone, Mayank Mishra, Gaoyuan Zhang, Shawn Tan, Aditya Prasad, Adriana Meza Soria, David D. Cox, Rameswar Panda.
1. **[GraniteMoeHybrid](https://huggingface.co/docs/transformers/main/model_doc/granitemoehybrid)** (from IBM) released with the blog post [IBM Granite 4.0: hyper-efficient, high performance hybrid models for enterprise](https://www.ibm.com/new/announcements/ibm-granite-4-0-hyper-efficient-high-performance-hybrid-models) by the IBM Granite team.
1. **[Grounding DINO](https://huggingface.co/docs/transformers/model_doc/grounding-dino)** (from IDEA-Research) released with the paper [Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection](https://huggingface.co/papers/2303.05499) by Shilong Liu, Zhaoyang Zeng, Tianhe Ren, Feng Li, Hao Zhang, Jie Yang, Qing Jiang, Chunyuan Li, Jianwei Yang, Hang Su, Jun Zhu, Lei Zhang.
1. **[GroupViT](https://huggingface.co/docs/transformers/model_doc/groupvit)** (from UCSD, NVIDIA) released with the paper [GroupViT: Semantic Segmentation Emerges from Text Supervision](https://huggingface.co/papers/2202.11094) by Jiarui Xu, Shalini De Mello, Sifei Liu, Wonmin Byeon, Thomas Breuel, Jan Kautz, Xiaolong Wang.
1. **[Helium](https://huggingface.co/docs/transformers/main/model_doc/helium)** (from the Kyutai Team) released with the blog post [Announcing Helium-1 Preview](https://kyutai.org/2025/01/13/helium.html) by the Kyutai Team.
1. **[HerBERT](https://huggingface.co/docs/transformers/model_doc/herbert)** (from Allegro.pl, AGH University of Science and Technology) released with the paper [KLEJ: Comprehensive Benchmark for Polish Language Understanding](https://www.aclweb.org/anthology/2020.acl-main.111.pdf) by Piotr Rybak, Robert Mroczkowski, Janusz Tracz, Ireneusz Gawlik.
1. **[Hiera](https://huggingface.co/docs/transformers/model_doc/hiera)** (from Meta) released with the paper [Hiera: A Hierarchical Vision Transformer without the Bells-and-Whistles](https://huggingface.co/papers/2306.00989) by Chaitanya Ryali, Yuan-Ting Hu, Daniel Bolya, Chen Wei, Haoqi Fan, Po-Yao Huang, Vaibhav Aggarwal, Arkabandhu Chowdhury, Omid Poursaeed, Judy Hoffman, Jitendra Malik, Yanghao Li, Christoph Feichtenhofer.
1. **[Hubert](https://huggingface.co/docs/transformers/model_doc/hubert)** (from Facebook) released with the paper [HuBERT: Self-Supervised Speech Representation Learning by Masked Prediction of Hidden Units](https://huggingface.co/papers/2106.07447) by Wei-Ning Hsu, Benjamin Bolte, Yao-Hung Hubert Tsai, Kushal Lakhotia, Ruslan Salakhutdinov, Abdelrahman Mohamed.
1. **[I-JEPA](https://huggingface.co/docs/transformers/model_doc/ijepa)** (from Meta) released with the paper [Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture](https://huggingface.co/papers/2301.08243) by Mahmoud Assran, Quentin Duval, Ishan Misra, Piotr Bojanowski, Pascal Vincent, Michael Rabbat, Yann LeCun, Nicolas Ballas.
1. **[Idefics3](https://huggingface.co/docs/transformers/model_doc/idefics3)** (from Hugging Face) released with the paper [Building and better understanding vision-language models: insights and future directions](https://huggingface.co/papers/2408.12637) by Hugo Laurençon, Andrés Marafioti, Victor Sanh, Léo Tronchon.
1. **JAIS** (from Core42) released with the paper [Jais and Jais-chat: Arabic-Centric Foundation and Instruction-Tuned Open Generative Large Language Models](https://huggingface.co/papers/2308.16149) by Neha Sengupta, Sunil Kumar Sahu, Bokang Jia, Satheesh Katipomu, Haonan Li, Fajri Koto, William Marshall, Gurpreet Gosal, Cynthia Liu, Zhiming Chen, Osama Mohammed Afzal, Samta Kamboj, Onkar Pandit, Rahul Pal, Lalit Pradhan, Zain Muhammad Mujahid, Massa Baali, Xudong Han, Sondos Mahmoud Bsharat, Alham Fikri Aji, Zhiqiang Shen, Zhengzhong Liu, Natalia Vassilieva, Joel Hestness, Andy Hock, Andrew Feldman, Jonathan Lee, Andrew Jackson, Hector Xuguang Ren, Preslav Nakov, Timothy Baldwin, Eric Xing.
1. **Janus** (from DeepSeek) released with the paper [Janus: Decoupling Visual Encoding for Unified Multimodal Understanding and Generation](https://huggingface.co/papers/2410.13848) Chengyue Wu, Xiaokang Chen, Zhiyu Wu, Yiyang Ma, Xingchao Liu, Zizheng Pan, Wen Liu, Zhenda Xie, Xingkai Yu, Chong Ruan, Ping Luo.
1. **JinaCLIP** (from Jina AI) released with the paper [Jina CLIP: Your CLIP Model Is Also Your Text Retriever](https://huggingface.co/papers/2405.20204) by Andreas Koukounas, Georgios Mastrapas, Michael Günther, Bo Wang, Scott Martens, Isabelle Mohr, Saba Sturua, Mohammad Kalim Akram, Joan Fontanals Martínez, Saahil Ognawala, Susana Guzman, Maximilian Werk, Nan Wang, Han Xiao.
1. **LiteWhisper** (from University of Washington, Kotoba Technologies) released with the paper [LiteASR: Efficient Automatic Speech Recognition with Low-Rank Approximation](https://huggingface.co/papers/2502.20583) by Keisuke Kamahori, Jungo Kasai, Noriyuki Kojima, Baris Kasikci.
1. **[LongT5](https://huggingface.co/docs/transformers/model_doc/longt5)** (from Google AI) released with the paper [LongT5: Efficient Text-To-Text Transformer for Long Sequences](https://huggingface.co/papers/2112.07916) by Mandy Guo, Joshua Ainslie, David Uthus, Santiago Ontanon, Jianmo Ni, Yun-Hsuan Sung, Yinfei Yang.
1. **[LFM2](https://huggingface.co/docs/transformers/model_doc/lfm2)** (from Liquid AI) released with the blog post [Introducing LFM2: The Fastest On-Device Foundation Models on the Market](https://www.liquid.ai/blog/liquid-foundation-models-v2-our-second-series-of-generative-ai-models) by the Liquid AI Team.
1. **[LLaMA](https://huggingface.co/docs/transformers/model_doc/llama)** (from The FAIR team of Meta AI) released with the paper [LLaMA: Open and Efficient Foundation Language Models](https://huggingface.co/papers/2302.13971) by Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, Aurelien Rodriguez, Armand Joulin, Edouard Grave, Guillaume Lample.
1. **[Llama2](https://huggingface.co/docs/transformers/model_doc/llama2)** (from The FAIR team of Meta AI) released with the paper [Llama2: Open Foundation and Fine-Tuned Chat Models](https://huggingface.co/papers/2307.09288) by Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, Dan Bikel, Lukas Blecher, Cristian Canton Ferrer, Moya Chen, Guillem Cucurull, David Esiobu, Jude Fernandes, Jeremy Fu, Wenyin Fu, Brian Fuller, Cynthia Gao, Vedanuj Goswami, Naman Goyal, Anthony Hartshorn, Saghar Hosseini, Rui Hou, Hakan Inan, Marcin Kardas, Viktor Kerkez Madian Khabsa, Isabel Kloumann, Artem Korenev, Punit Singh Koura, Marie-Anne Lachaux, Thibaut Lavril, Jenya Lee, Diana Liskovich, Yinghai Lu, Yuning Mao, Xavier Martinet, Todor Mihaylov, Pushka rMishra, Igor Molybog, Yixin Nie, Andrew Poulton, Jeremy Reizenstein, Rashi Rungta, Kalyan Saladi, Alan Schelten, Ruan Silva, Eric Michael Smith, Ranjan Subramanian, Xiaoqing EllenTan, Binh Tang, Ross Taylor, Adina Williams, Jian Xiang Kuan, Puxin Xu, Zheng Yan, Iliyan Zarov, Yuchen Zhang, Angela Fan, Melanie Kambadur, Sharan Narang, Aurelien Rodriguez, Robert Stojnic, Sergey Edunov, Thomas Scialom.
1. **[Llama3](https://huggingface.co/docs/transformers/model_doc/llama3)** (from The FAIR team of Meta AI) released with the paper [The Llama 3 Herd of Models](https://huggingface.co/papers/2407.21783) by the Llama Team at Meta.
1. **[Llama4](https://huggingface.co/docs/transformers/model_doc/llama4)** (from The FAIR team of Meta AI) released with the blog post [The Llama 4 herd: The beginning of a new era of natively multimodal AI innovation](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) by the Llama Team at Meta.
1. **[LLaVa](https://huggingface.co/docs/transformers/model_doc/llava)** (from Microsoft Research & University of Wisconsin-Madison) released with the paper [Visual Instruction Tuning](https://huggingface.co/papers/2304.08485) by Haotian Liu, Chunyuan Li, Yuheng Li and Yong Jae Lee.
1. **[LLaVA-OneVision](https://huggingface.co/docs/transformers/model_doc/llava_onevision)** (from ByteDance & NTU & CUHK & HKUST) released with the paper [LLaVA-OneVision: Easy Visual Task Transfer](https://huggingface.co/papers/2408.03326) by Bo Li, Yuanhan Zhang, Dong Guo, Renrui Zhang, Feng Li, Hao Zhang, Kaichen Zhang, Yanwei Li, Ziwei Liu, Chunyuan Li
1. **[M2M100](https://huggingface.co/docs/transformers/model_doc/m2m_100)** (from Facebook) released with the paper [Beyond English-Centric Multilingual Machine Translation](https://huggingface.co/papers/2010.11125) by Angela Fan, Shruti Bhosale, Holger Schwenk, Zhiyi Ma, Ahmed El-Kishky, Siddharth Goyal, Mandeep Baines, Onur Celebi, Guillaume Wenzek, Vishrav Chaudhary, Naman Goyal, Tom Birch, Vitaliy Liptchinsky, Sergey Edunov, Edouard Grave, Michael Auli, Armand Joulin.
1. **[MarianMT](https://huggingface.co/docs/transformers/model_doc/marian)** Machine translation models trained using [OPUS](http://opus.nlpl.eu/) data by Jörg Tiedemann. The [Marian Framework](https://marian-nmt.github.io/) is being developed by the Microsoft Translator Team.
1. **[MaskFormer](https://huggingface.co/docs/transformers/model_doc/maskformer)** (from Meta and UIUC) released with the paper [Per-Pixel Classification is Not All You Need for Semantic Segmentation](https://huggingface.co/papers/2107.06278) by Bowen Cheng, Alexander G. Schwing, Alexander Kirillov.
1. **[mBART](https://huggingface.co/docs/transformers/model_doc/mbart)** (from Facebook) released with the paper [Multilingual Denoising Pre-training for Neural Machine Translation](https://huggingface.co/papers/2001.08210) by Yinhan Liu, Jiatao Gu, Naman Goyal, Xian Li, Sergey Edunov, Marjan Ghazvininejad, Mike Lewis, Luke Zettlemoyer.
1. **[mBART-50](https://huggingface.co/docs/transformers/model_doc/mbart)** (from Facebook) released with the paper [Multilingual Translation with Extensible Multilingual Pretraining and Finetuning](https://huggingface.co/papers/2008.00401) by Yuqing Tang, Chau Tran, Xian Li, Peng-Jen Chen, Naman Goyal, Vishrav Chaudhary, Jiatao Gu, Angela Fan.
1. **Metric3D** released with the paper [Metric3D: Towards Zero-shot Metric 3D Prediction from A Single Image](https://huggingface.co/papers/2307.10984) by Wei Yin, Chi Zhang, Hao Chen, Zhipeng Cai, Gang Yu, Kaixuan Wang, Xiaozhi Chen, Chunhua Shen.
1. **Metric3Dv2** released with the paper [Metric3Dv2: A Versatile Monocular Geometric Foundation Model for Zero-shot Metric Depth and Surface Normal Estimation](https://huggingface.co/papers/2404.15506) by Mu Hu, Wei Yin, Chi Zhang, Zhipeng Cai, Xiaoxiao Long, Kaixuan Wang, Hao Chen, Gang Yu, Chunhua Shen, Shaojie Shen.
1. **[MusicGen](https://huggingface.co/docs/transformers/model_doc/musicgen)** (from Meta) released with the paper [Simple and Controllable Music Generation](https://huggingface.co/papers/2306.05284) by Jade Copet, Felix Kreuk, Itai Gat, Tal Remez, David Kant, Gabriel Synnaeve, Yossi Adi and Alexandre Défossez.
1. **[MGP-STR](https://huggingface.co/docs/transformers/model_doc/mgp-str)** (from Alibaba Research) released with the paper [Multi-Granularity Prediction for Scene Text Recognition](https://huggingface.co/papers/2209.03592) by Peng Wang, Cheng Da, and Cong Yao.
1. **[Mimi](https://huggingface.co/docs/transformers/model_doc/mimi)** (from Kyutai) released with the paper [Moshi: a speech-text foundation model for real-time dialogue](https://huggingface.co/papers/2410.00037) by Alexandre Défossez, Laurent Mazaré, Manu Orsini, Amélie Royer, Patrick Pérez, Hervé Jégou, Edouard Grave and Neil Zeghidour.
1. **[Mistral](https://huggingface.co/docs/transformers/model_doc/mistral)** (from Mistral AI) by The [Mistral AI](https://mistral.ai) team: Albert Jiang, Alexandre Sablayrolles, Arthur Mensch, Chris Bamford, Devendra Singh Chaplot, Diego de las Casas, Florian Bressand, Gianna Lengyel, Guillaume Lample, Lélio Renard Lavaud, Lucile Saulnier, Marie-Anne Lachaux, Pierre Stock, Teven Le Scao, Thibaut Lavril, Thomas Wang, Timothée Lacroix, William El Sayed.
1. **[MMS](https://huggingface.co/docs/transformers/model_doc/mms)** (from Facebook) released with the paper [Scaling Speech Technology to 1,000+ Languages](https://huggingface.co/papers/2305.13516) by Vineel Pratap, Andros Tjandra, Bowen Shi, Paden Tomasello, Arun Babu, Sayani Kundu, Ali Elkahky, Zhaoheng Ni, Apoorv Vyas, Maryam Fazel-Zarandi, Alexei Baevski, Yossi Adi, Xiaohui Zhang, Wei-Ning Hsu, Alexis Conneau, Michael Auli.
1. **[MobileBERT](https://huggingface.co/docs/transformers/model_doc/mobilebert)** (from CMU/Google Brain) released with the paper [MobileBERT: a Compact Task-Agnostic BERT for Resource-Limited Devices](https://huggingface.co/papers/2004.02984) by Zhiqing Sun, Hongkun Yu, Xiaodan Song, Renjie Liu, Yiming Yang, and Denny Zhou.
1. **MobileCLIP** (from Apple) released with the paper [MobileCLIP: Fast Image-Text Models through Multi-Modal Reinforced Training](https://huggingface.co/papers/2311.17049) by Pavan Kumar Anasosalu Vasu, Hadi Pouransari, Fartash Faghri, Raviteja Vemulapalli, Oncel Tuzel.
1. **MobileLLM** (from Meta) released with the paper [MobileLLM: Optimizing Sub-billion Parameter Language Models for On-Device Use Cases](https://huggingface.co/papers/2402.14905) by Zechun Liu, Changsheng Zhao, Forrest Iandola, Chen Lai, Yuandong Tian, Igor Fedorov, Yunyang Xiong, Ernie Chang, Yangyang Shi, Raghuraman Krishnamoorthi, Liangzhen Lai, Vikas Chandra.
1. **[MobileNetV1](https://huggingface.co/docs/transformers/model_doc/mobilenet_v1)** (from Google Inc.) released with the paper [MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications](https://huggingface.co/papers/1704.04861) by Andrew G. Howard, Menglong Zhu, Bo Chen, Dmitry Kalenichenko, Weijun Wang, Tobias Weyand, Marco Andreetto, Hartwig Adam.
1. **[MobileNetV2](https://huggingface.co/docs/transformers/model_doc/mobilenet_v2)** (from Google Inc.) released with the paper [MobileNetV2: Inverted Residuals and Linear Bottlenecks](https://huggingface.co/papers/1801.04381) by Mark Sandler, Andrew Howard, Menglong Zhu, Andrey Zhmoginov, Liang-Chieh Chen.
1. **MobileNetV3** (from Google Inc.) released with the paper [Searching for MobileNetV3](https://huggingface.co/papers/1905.02244) by Andrew Howard, Mark Sandler, Grace Chu, Liang-Chieh Chen, Bo Chen, Mingxing Tan, Weijun Wang, Yukun Zhu, Ruoming Pang, Vijay Vasudevan, Quoc V. Le, Hartwig Adam.
1. **MobileNetV4** (from Google Inc.) released with the paper [MobileNetV4 - Universal Models for the Mobile Ecosystem](https://huggingface.co/papers/2404.10518) by Danfeng Qin, Chas Leichner, Manolis Delakis, Marco Fornoni, Shixin Luo, Fan Yang, Weijun Wang, Colby Banbury, Chengxi Ye, Berkin Akin, Vaibhav Aggarwal, Tenghui Zhu, Daniele Moro, Andrew Howard.
1. **[MobileViT](https://huggingface.co/docs/transformers/model_doc/mobilevit)** (from Apple) released with the paper [MobileViT: Light-weight, General-purpose, and Mobile-friendly Vision Transformer](https://huggingface.co/papers/2110.02178) by Sachin Mehta and Mohammad Rastegari.
1. **[MobileViTV2](https://huggingface.co/docs/transformers/model_doc/mobilevitv2)** (from Apple) released with the paper [Separable Self-attention for Mobile Vision Transformers](https://huggingface.co/papers/2206.02680) by Sachin Mehta and Mohammad Rastegari.
1. **[ModernBERT](https://huggingface.co/docs/transformers/model_doc/modernbert)** (from Answer.AI and LightOn) released with the paper [Smarter, Better, Faster, Longer: A Modern Bidirectional Encoder for Fast, Memory Efficient, and Long Context Finetuning and Inference](https://huggingface.co/papers/2412.13663) by Benjamin Warner, Antoine Chaffin, Benjamin Clavié, Orion Weller, Oskar Hallström, Said Taghadouini, Alexis Gallagher, Raja Biswas, Faisal Ladhak, Tom Aarsen, Nathan Cooper, Griffin Adams, Jeremy Howard, Iacopo Poli.
1. **[ModernBERT Decoder](https://huggingface.co/docs/transformers/model_doc/modernbert-decoder)** (from Johns Hopkins University and LightOn) released with the paper [Seq vs Seq: An Open Suite of Paired Encoders and Decoders](https://huggingface.co/papers/2507.11412) by Orion Weller, Kathryn Ricci, Marc Marone, Antoine Chaffin, Dawn Lawrie, Benjamin Van Durme.
1. **Moondream1** released in the repository [moondream](https://github.com/vikhyat/moondream) by vikhyat.
1. **[Moonshine](https://huggingface.co/docs/transformers/model_doc/moonshine)** (from Useful Sensors) released with the paper [Moonshine: Speech Recognition for Live Transcription and Voice Commands](https://huggingface.co/papers/2410.15608) by Nat Jeffries, Evan King, Manjunath Kudlur, Guy Nicholson, James Wang, Pete Warden.
1. **[MPNet](https://huggingface.co/docs/transformers/model_doc/mpnet)** (from Microsoft Research) released with the paper [MPNet: Masked and Permuted Pre-training for Language Understanding](https://huggingface.co/papers/2004.09297) by Kaitao Song, Xu Tan, Tao Qin, Jianfeng Lu, Tie-Yan Liu.
1. **[MPT](https://huggingface.co/docs/transformers/model_doc/mpt)** (from MosaicML) released with the repository [llm-foundry](https://github.com/mosaicml/llm-foundry/) by the MosaicML NLP Team.
1. **[MT5](https://huggingface.co/docs/transformers/model_doc/mt5)** (from Google AI) released with the paper [mT5: A massively multilingual pre-trained text-to-text transformer](https://huggingface.co/papers/2010.11934) by Linting Xue, Noah Constant, Adam Roberts, Mihir Kale, Rami Al-Rfou, Aditya Siddhant, Aditya Barua, Colin Raffel.
1. **[NanoChat](https://huggingface.co/docs/transformers/model_doc/nanochat)** released with the repository [nanochat: The best ChatGPT that $100 can buy](https://github.com/karpathy/nanochat) by Andrej Karpathy.
1. **NeoBERT** (from Chandar Research Lab) released with the paper [NeoBERT: A Next-Generation BERT](https://huggingface.co/papers/2502.19587) by Lola Le Breton, Quentin Fournier, Mariam El Mezouar, John X. Morris, Sarath Chandar.
1. **[NLLB](https://huggingface.co/docs/transformers/model_doc/nllb)** (from Meta) released with the paper [No Language Left Behind: Scaling Human-Centered Machine Translation](https://huggingface.co/papers/2207.04672) by the NLLB team.
1. **[Nougat](https://huggingface.co/docs/transformers/model_doc/nougat)** (from Meta AI) released with the paper [Nougat: Neural Optical Understanding for Academic Documents](https://huggingface.co/papers/2308.13418) by Lukas Blecher, Guillem Cucurull, Thomas Scialom, Robert Stojnic.
1. **[OLMo](https://huggingface.co/docs/transformers/master/model_doc/olmo)** (from Ai2) released with the paper [OLMo: Accelerating the Science of Language Models](https://huggingface.co/papers/2402.00838) by Dirk Groeneveld, Iz Beltagy, Pete Walsh, Akshita Bhagia, Rodney Kinney, Oyvind Tafjord, Ananya Harsh Jha, Hamish Ivison, Ian Magnusson, Yizhong Wang, Shane Arora, David Atkinson, Russell Authur, Khyathi Raghavi Chandu, Arman Cohan, Jennifer Dumas, Yanai Elazar, Yuling Gu, Jack Hessel, Tushar Khot, William Merrill, Jacob Morrison, Niklas Muennighoff, Aakanksha Naik, Crystal Nam, Matthew E. Peters, Valentina Pyatkin, Abhilasha Ravichander, Dustin Schwenk, Saurabh Shah, Will Smith, Emma Strubell, Nishant Subramani, Mitchell Wortsman, Pradeep Dasigi, Nathan Lambert, Kyle Richardson, Luke Zettlemoyer, Jesse Dodge, Kyle Lo, Luca Soldaini, Noah A. Smith, Hannaneh Hajishirzi.
1. **[OLMo2](https://huggingface.co/docs/transformers/master/model_doc/olmo2)** (from Ai2) released with the blog [OLMo 2: The best fully open language model to date](https://allenai.org/blog/olmo2) by the Ai2 OLMo team.
1. **OpenELM** (from Apple) released with the paper [OpenELM: An Efficient Language Model Family with Open-source Training and Inference Framework](https://huggingface.co/papers/2404.14619) by Sachin Mehta, Mohammad Hossein Sekhavat, Qingqing Cao, Maxwell Horton, Yanzi Jin, Chenfan Sun, Iman Mirzadeh, Mahyar Najibi, Dmitry Belenko, Peter Zatloukal, Mohammad Rastegari.
1. **[OPT](https://huggingface.co/docs/transformers/master/model_doc/opt)** (from Meta AI) released with the paper [OPT: Open Pre-trained Transformer Language Models](https://huggingface.co/papers/2205.01068) by Susan Zhang, Stephen Roller, Naman Goyal, Mikel Artetxe, Moya Chen, Shuohui Chen et al.
1. **[OWL-ViT](https://huggingface.co/docs/transformers/model_doc/owlvit)** (from Google AI) released with the paper [Simple Open-Vocabulary Object Detection with Vision Transformers](https://huggingface.co/papers/2205.06230) by Matthias Minderer, Alexey Gritsenko, Austin Stone, Maxim Neumann, Dirk Weissenborn, Alexey Dosovitskiy, Aravindh Mahendran, Anurag Arnab, Mostafa Dehghani, Zhuoran Shen, Xiao Wang, Xiaohua Zhai, Thomas Kipf, and Neil Houlsby.
1. **[OWLv2](https://huggingface.co/docs/transformers/model_doc/owlv2)** (from Google AI) released with the paper [Scaling Open-Vocabulary Object Detection](https://huggingface.co/papers/2306.09683) by Matthias Minderer, Alexey Gritsenko, Neil Houlsby.
1. **[PaliGemma](https://huggingface.co/docs/transformers/main/model_doc/paligemma)** (from Google) released with the papers [PaliGemma: A versatile 3B VLM for transfer](https://huggingface.co/papers/2407.07726) and [PaliGemma 2: A Family of Versatile VLMs for Transfer](https://huggingface.co/papers/2412.03555) by the PaliGemma Google team.
1. **[Parakeet](https://huggingface.co/docs/transformers/main/model_doc/parakeet)** (from NVIDIA) released with the blog post [Introducing the Parakeet ASR family](https://developer.nvidia.com/blog/pushing-the-boundaries-of-speech-recognition-with-nemo-parakeet-asr-models/) by the NVIDIA NeMo team.
1. **[PatchTSMixer](https://huggingface.co/docs/transformers/main/model_doc/patchtsmixer)** (from IBM) released with the paper [TSMixer: Lightweight MLP-Mixer Model for Multivariate Time Series Forecasting](https://huggingface.co/papers/2306.09364) by Vijay Ekambaram, Arindam Jati, Nam Nguyen, Phanwadee Sinthong, Jayant Kalagnanam.
1. **[PatchTST](https://huggingface.co/docs/transformers/main/model_doc/patchtst)** (from Princeton University, IBM) released with the paper [A Time Series is Worth 64 Words: Long-term Forecasting with Transformers](https://huggingface.co/papers/2211.14730) by Yuqi Nie, Nam H. Nguyen, Phanwadee Sinthong, Jayant Kalagnanam.
1. **[Phi](https://huggingface.co/docs/transformers/main/model_doc/phi)** (from Microsoft) released with the papers - [Textbooks Are All You Need](https://huggingface.co/papers/2306.11644) by Suriya Gunasekar, Yi Zhang, Jyoti Aneja, Caio César Teodoro Mendes, Allie Del Giorno, Sivakanth Gopi, Mojan Javaheripi, Piero Kauffmann, Gustavo de Rosa, Olli Saarikivi, Adil Salim, Shital Shah, Harkirat Singh Behl, Xin Wang, Sébastien Bubeck, Ronen Eldan, Adam Tauman Kalai, Yin Tat Lee and Yuanzhi Li, [Textbooks Are All You Need II: phi-1.5 technical report](https://huggingface.co/papers/2309.05463) by Yuanzhi Li, Sébastien Bubeck, Ronen Eldan, Allie Del Giorno, Suriya Gunasekar and Yin Tat Lee.
1. **[Phi3](https://huggingface.co/docs/transformers/main/model_doc/phi3)** (from Microsoft) released with the paper [Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone](https://huggingface.co/papers/2404.14219v2) by Marah Abdin, Sam Ade Jacobs, Ammar Ahmad Awan, Jyoti Aneja, Ahmed Awadallah, Hany Awadalla, Nguyen Bach, Amit Bahree, Arash Bakhtiari, Harkirat Behl, Alon Benhaim, Misha Bilenko, Johan Bjorck, Sébastien Bubeck, Martin Cai, Caio César Teodoro Mendes, Weizhu Chen, Vishrav Chaudhary, Parul Chopra, Allie Del Giorno, Gustavo de Rosa, Matthew Dixon, Ronen Eldan, Dan Iter, Amit Garg, Abhishek Goswami, Suriya Gunasekar, Emman Haider, Junheng Hao, Russell J. Hewett, Jamie Huynh, Mojan Javaheripi, Xin Jin, Piero Kauffmann, Nikos Karampatziakis, Dongwoo Kim, Mahoud Khademi, Lev Kurilenko, James R. Lee, Yin Tat Lee, Yuanzhi Li, Chen Liang, Weishung Liu, Eric Lin, Zeqi Lin, Piyush Madan, Arindam Mitra, Hardik Modi, Anh Nguyen, Brandon Norick, Barun Patra, Daniel Perez-Becker, Thomas Portet, Reid Pryzant, Heyang Qin, Marko Radmilac, Corby Rosset, Sambudha Roy, Olatunji Ruwase, Olli Saarikivi, Amin Saied, Adil Salim, Michael Santacroce, Shital Shah, Ning Shang, Hiteshi Sharma, Xia Song, Masahiro Tanaka, Xin Wang, Rachel Ward, Guanhua Wang, Philipp Witte, Michael Wyatt, Can Xu, Jiahang Xu, Sonali Yadav, Fan Yang, Ziyi Yang, Donghan Yu, Chengruidong Zhang, Cyril Zhang, Jianwen Zhang, Li Lyna Zhang, Yi Zhang, Yue Zhang, Yunan Zhang, Xiren Zhou.
1. **Phi3V** (from Microsoft) released with the paper [Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone](https://huggingface.co/papers/2404.14219v4) by Marah Abdin, Jyoti Aneja, Hany Awadalla, Ahmed Awadallah, Ammar Ahmad Awan, Nguyen Bach, Amit Bahree, Arash Bakhtiari, Jianmin Bao, Harkirat Behl, Alon Benhaim, Misha Bilenko, Johan Bjorck, Sébastien Bubeck, Martin Cai, Qin Cai, Vishrav Chaudhary, Dong Chen, Dongdong Chen, Weizhu Chen, Yen-Chun Chen, Yi-Ling Chen, Hao Cheng, Parul Chopra, Xiyang Dai, Matthew Dixon, Ronen Eldan, Victor Fragoso, Jianfeng Gao, Mei Gao, Min Gao, Amit Garg, Allie Del Giorno, Abhishek Goswami, Suriya Gunasekar, Emman Haider, Junheng Hao, Russell J. Hewett, Wenxiang Hu, Jamie Huynh, Dan Iter, Sam Ade Jacobs, Mojan Javaheripi, Xin Jin, Nikos Karampatziakis, Piero Kauffmann, Mahoud Khademi, Dongwoo Kim, Young Jin Kim, Lev Kurilenko, James R. Lee, Yin Tat Lee, Yuanzhi Li, Yunsheng Li, Chen Liang, Lars Liden, Xihui Lin, Zeqi Lin, Ce Liu, Liyuan Liu, Mengchen Liu, Weishung Liu, Xiaodong Liu, Chong Luo, Piyush Madan, Ali Mahmoudzadeh, David Majercak, Matt Mazzola, Caio César Teodoro Mendes, Arindam Mitra, Hardik Modi, Anh Nguyen, Brandon Norick, Barun Patra, Daniel Perez-Becker, Thomas Portet, Reid Pryzant, Heyang Qin, Marko Radmilac, Liliang Ren, Gustavo de Rosa, Corby Rosset, Sambudha Roy, Olatunji Ruwase, Olli Saarikivi, Amin Saied, Adil Salim, Michael Santacroce, Shital Shah, Ning Shang, Hiteshi Sharma, Yelong Shen, Swadheen Shukla, Xia Song, Masahiro Tanaka, Andrea Tupini, Praneetha Vaddamanu, Chunyu Wang, Guanhua Wang, Lijuan Wang , Shuohang Wang, Xin Wang, Yu Wang, Rachel Ward, Wen Wen, Philipp Witte, Haiping Wu, Xiaoxia Wu, Michael Wyatt, Bin Xiao, Can Xu, Jiahang Xu, Weijian Xu, Jilong Xue, Sonali Yadav, Fan Yang, Jianwei Yang, Yifan Yang, Ziyi Yang, Donghan Yu, Lu Yuan, Chenruidong Zhang, Cyril Zhang, Jianwen Zhang, Li Lyna Zhang, Yi Zhang, Yue Zhang, Yunan Zhang, Xiren Zhou.
1. **[PVT](https://huggingface.co/docs/transformers/main/model_doc/pvt)** (from Nanjing University, The University of Hong Kong etc.) released with the paper [Pyramid Vision Transformer: A Versatile Backbone for Dense Prediction without Convolutions](https://huggingface.co/papers/2102.12122) by Wenhai Wang, Enze Xie, Xiang Li, Deng-Ping Fan, Kaitao Song, Ding Liang, Tong Lu, Ping Luo, Ling Shao.
1. **PyAnnote** released in the repository [pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio) by Hervé Bredin.
1. **[Qwen2](https://huggingface.co/docs/transformers/model_doc/qwen2)** (from the Qwen team, Alibaba Group) released with the paper [Qwen Technical Report](https://huggingface.co/papers/2309.16609) by Jinze Bai, Shuai Bai, Yunfei Chu, Zeyu Cui, Kai Dang, Xiaodong Deng, Yang Fan, Wenbin Ge, Yu Han, Fei Huang, Binyuan Hui, Luo Ji, Mei Li, Junyang Lin, Runji Lin, Dayiheng Liu, Gao Liu, Chengqiang Lu, Keming Lu, Jianxin Ma, Rui Men, Xingzhang Ren, Xuancheng Ren, Chuanqi Tan, Sinan Tan, Jianhong Tu, Peng Wang, Shijie Wang, Wei Wang, Shengguang Wu, Benfeng Xu, Jin Xu, An Yang, Hao Yang, Jian Yang, Shusheng Yang, Yang Yao, Bowen Yu, Hongyi Yuan, Zheng Yuan, Jianwei Zhang, Xingxuan Zhang, Yichang Zhang, Zhenru Zhang, Chang Zhou, Jingren Zhou, Xiaohuan Zhou and Tianhang Zhu.
1. **[Qwen2-VL](https://huggingface.co/docs/transformers/model_doc/qwen2_vl)** (from the Qwen team, Alibaba Group) released with the paper [Qwen-VL: A Versatile Vision-Language Model for Understanding, Localization, Text Reading, and Beyond](https://huggingface.co/papers/2308.12966) by Jinze Bai, Shuai Bai, Shusheng Yang, Shijie Wang, Sinan Tan, Peng Wang, Junyang Lin, Chang Zhou, Jingren Zhou.
1. **[Qwen3](https://huggingface.co/docs/transformers/en/model_doc/qwen3)** (from the Qwen team, Alibaba Group) released with the blog post [Qwen3: Think Deeper, Act Faster](https://qwenlm.github.io/blog/qwen3/) by the Qwen team.
1. **[ResNet](https://huggingface.co/docs/transformers/model_doc/resnet)** (from Microsoft Research) released with the paper [Deep Residual Learning for Image Recognition](https://huggingface.co/papers/1512.03385) by Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun.
1. **[RF-DETR](https://huggingface.co/docs/transformers/model_doc/rf_detr)** (from Roboflow) released with the blog post [RF-DETR: A SOTA Real-Time Object Detection Model](https://blog.roboflow.com/rf-detr/) by Peter Robicheaux, James Gallagher, Joseph Nelson, Isaac Robinson.
1. **[RoBERTa](https://huggingface.co/docs/transformers/model_doc/roberta)** (from Facebook), released together with the paper [RoBERTa: A Robustly Optimized BERT Pretraining Approach](https://huggingface.co/papers/1907.11692) by Yinhan Liu, Myle Ott, Naman Goyal, Jingfei Du, Mandar Joshi, Danqi Chen, Omer Levy, Mike Lewis, Luke Zettlemoyer, Veselin Stoyanov.
1. **[RoFormer](https://huggingface.co/docs/transformers/model_doc/roformer)** (from ZhuiyiTechnology), released together with the paper [RoFormer: Enhanced Transformer with Rotary Position Embedding](https://huggingface.co/papers/2104.09864) by Jianlin Su and Yu Lu and Shengfeng Pan and Bo Wen and Yunfeng Liu.
1. **[RT-DETR](https://huggingface.co/docs/transformers/model_doc/rt_detr)** (from Baidu), released together with the paper [DETRs Beat YOLOs on Real-time Object Detection](https://huggingface.co/papers/2304.08069) by Yian Zhao, Wenyu Lv, Shangliang Xu, Jinman Wei, Guanzhong Wang, Qingqing Dang, Yi Liu, Jie Chen.
1. **[RT-DETRv2](https://huggingface.co/docs/transformers/model_doc/rt_detr_v2)** (from Baidu), released together with the paper [RT-DETRv2: Improved Baseline with Bag-of-Freebies for Real-Time Detection Transformer](https://huggingface.co/papers/2407.17140) by Wenyu Lv, Yian Zhao, Qinyao Chang, Kui Huang, Guanzhong Wang, Yi Liu.
1. **Sapiens** (from Meta AI) released with the paper [Sapiens: Foundation for Human Vision Models](https://huggingface.co/papers/2408.12569) by Rawal Khirodkar, Timur Bagautdinov, Julieta Martinez, Su Zhaoen, Austin James, Peter Selednik, Stuart Anderson, Shunsuke Saito.
1. **[SegFormer](https://huggingface.co/docs/transformers/model_doc/segformer)** (from NVIDIA) released with the paper [SegFormer: Simple and Efficient Design for Semantic Segmentation with Transformers](https://huggingface.co/papers/2105.15203) by Enze Xie, Wenhai Wang, Zhiding Yu, Anima Anandkumar, Jose M. Alvarez, Ping Luo.
1. **[Segment Anything](https://huggingface.co/docs/transformers/model_doc/sam)** (from Meta AI) released with the paper [Segment Anything](https://huggingface.co/papers/2304.02643v1.pdf) by Alexander Kirillov, Eric Mintun, Nikhila Ravi, Hanzi Mao, Chloe Rolland, Laura Gustafson, Tete Xiao, Spencer Whitehead, Alex Berg, Wan-Yen Lo, Piotr Dollar, Ross Girshick.
1. **[Segment Anything 2](https://huggingface.co/docs/transformers/model_doc/sam2)** (from Meta AI) released with the paper [SAM 2: Segment Anything in Images and Videos](https://huggingface.co/papers/2408.00714) by Nikhila Ravi, Valentin Gabeur, Yuan-Ting Hu, Ronghang Hu, Chaitanya Ryali, Tengyu Ma, Haitham Khedr, Roman Rädle, Chloe Rolland, Laura Gustafson, Eric Mintun, Junting Pan, Kalyan Vasudev Alwala, Nicolas Carion, Chao-Yuan Wu, Ross Girshick, Piotr Dollár, Christoph Feichtenhofer.
1. **[Segment Anything 3](https://huggingface.co/docs/transformers/model_doc/sam3)** (from Meta Superintelligence Labs) released with the paper [SAM 3: Segment Anything with Concepts](https://ai.meta.com/research/publications/sam-3-segment-anything-with-concepts/) by SAM 3D Team, Xingyu Chen, Fu-Jen Chu, Pierre Gleize, Kevin J Liang, Alexander Sax, Hao Tang, Weiyao Wang, Michelle Guo, Thibaut Hardin, Xiang Li, Aohan Lin, Jiawei Liu, Ziqi Ma, Anushka Sagar, Bowen Song, Xiaodong Wang, Jianing Yang, Bowen Zhang, Piotr Dollar, Georgia Gkioxari, Matt Feiszli, Jitendra Malik, Nicolas Carion, Laura Gustafson, Yuan-Ting Hu, Shoubhik Debnath, Ronghang Hu, Didac Suris Coll-Vinent, Chaitanya Ryali, Kalyan Vasudev Alwala, Haitham Khedr, Andrew Huang, Jie Lei, Tengyu Ma, Baishan Guo, Arpit Kalla, Markus Marks, Joseph Greer, Meng Wang, Peize Sun, Roman Rädle, Triantafyllos Afouras, Effrosyni Mavroudi, Katherine Xu, Tsung-Han Wu, Yu Zhou, Liliane Momeni, Rishi Hazra, Shuangrui Ding, Sagar Vaze, Francois Porcher, Feng Li, Siyuan Li, Aishwarya Kamath, Ho Kei Cheng, Piotr Dollar, Nikhila Ravi, Kate Saenko, Pengchuan Zhang, Christoph Feichtenhofer.
1. **[SigLIP](https://huggingface.co/docs/transformers/main/model_doc/siglip)** (from Google AI) released with the paper [Sigmoid Loss for Language Image Pre-Training](https://huggingface.co/papers/2303.15343) by Xiaohua Zhai, Basil Mustafa, Alexander Kolesnikov, Lucas Beyer.
1. **[SmolLM3](https://huggingface.co/docs/transformers/main/model_doc/smollm3) (from Hugging Face) released with the blog post [SmolLM3: smol, multilingual, long-context reasoner](https://huggingface.co/blog/smollm3) by the Hugging Face TB Research team.
1. **[SmolVLM](https://huggingface.co/docs/transformers/main/model_doc/smolvlm) (from Hugging Face) released with the blog posts [SmolVLM - small yet mighty Vision Language Model](https://huggingface.co/blog/smolvlm) and [SmolVLM Grows Smaller – Introducing the 250M & 500M Models!](https://huggingface.co/blog/smolervlm) by the Hugging Face TB Research team.
1. **SNAC** (from Papla Media, ETH Zurich) released with the paper [SNAC: Multi-Scale Neural Audio Codec](https://huggingface.co/papers/2410.14411) by Hubert Siuzdak, Florian Grötschla, Luca A. Lanzendörfer.
1. **[SpeechT5](https://huggingface.co/docs/transformers/model_doc/speecht5)** (from Microsoft Research) released with the paper [SpeechT5: Unified-Modal Encoder-Decoder Pre-Training for Spoken Language Processing](https://huggingface.co/papers/2110.07205) by Junyi Ao, Rui Wang, Long Zhou, Chengyi Wang, Shuo Ren, Yu Wu, Shujie Liu, Tom Ko, Qing Li, Yu Zhang, Zhihua Wei, Yao Qian, Jinyu Li, Furu Wei.
1. **[SqueezeBERT](https://huggingface.co/docs/transformers/model_doc/squeezebert)** (from Berkeley) released with the paper [SqueezeBERT: What can computer vision teach NLP about efficient neural networks?](https://huggingface.co/papers/2006.11316) by Forrest N. Iandola, Albert E. Shaw, Ravi Krishna, and Kurt W. Keutzer.
1. **[StableLm](https://huggingface.co/docs/transformers/model_doc/stablelm)** (from Stability AI) released with the paper [StableLM 3B 4E1T (Technical Report)](https://stability.wandb.io/stability-llm/stable-lm/reports/StableLM-3B-4E1T--VmlldzoyMjU4?accessToken=u3zujipenkx5g7rtcj9qojjgxpconyjktjkli2po09nffrffdhhchq045vp0wyfo) by Jonathan Tow, Marco Bellagente, Dakota Mahan, Carlos Riquelme Ruiz, Duy Phung, Maksym Zhuravinskyi, Nathan Cooper, Nikhil Pinnaparaju, Reshinth Adithyan, and James Baicoianu.
1. **[Starcoder2](https://huggingface.co/docs/transformers/main/model_doc/starcoder2)** (from BigCode team) released with the paper [StarCoder 2 and The Stack v2: The Next Generation](https://huggingface.co/papers/2402.19173) by Anton Lozhkov, Raymond Li, Loubna Ben Allal, Federico Cassano, Joel Lamy-Poirier, Nouamane Tazi, Ao Tang, Dmytro Pykhtar, Jiawei Liu, Yuxiang Wei, Tianyang Liu, Max Tian, Denis Kocetkov, Arthur Zucker, Younes Belkada, Zijian Wang, Qian Liu, Dmitry Abulkhanov, Indraneil Paul, Zhuang Li, Wen-Ding Li, Megan Risdal, Jia Li, Jian Zhu, Terry Yue Zhuo, Evgenii Zheltonozhskii, Nii Osae Osae Dade, Wenhao Yu, Lucas Krauß, Naman Jain, Yixuan Su, Xuanli He, Manan Dey, Edoardo Abati, Yekun Chai, Niklas Muennighoff, Xiangru Tang, Muhtasham Oblokulov, Christopher Akiki, Marc Marone, Chenghao Mou, Mayank Mishra, Alex Gu, Binyuan Hui, Tri Dao, Armel Zebaze, Olivier Dehaene, Nicolas Patry, Canwen Xu, Julian McAuley, Han Hu, Torsten Scholak, Sebastien Paquet, Jennifer Robinson, Carolyn Jane Anderson, Nicolas Chapados, Mostofa Patwary, Nima Tajbakhsh, Yacine Jernite, Carlos Muñoz Ferrandis, Lingming Zhang, Sean Hughes, Thomas Wolf, Arjun Guha, Leandro von Werra, and Harm de Vries.
1. **StyleTTS 2** (from Columbia University) released with the paper [StyleTTS 2: Towards Human-Level Text-to-Speech through Style Diffusion and Adversarial Training with Large Speech Language Models](https://huggingface.co/papers/2306.07691) by Yinghao Aaron Li, Cong Han, Vinay S. Raghavan, Gavin Mischler, Nima Mesgarani.
1. **Supertonic** (from Supertone) released with the paper [SupertonicTTS: Towards Highly Efficient and Streamlined Text-to-Speech System](https://huggingface.co/papers/2503.23108) by Hyeongju Kim, Jinhyeok Yang, Yechan Yu, Seunghun Ji, Jacob Morton, Frederik Bous, Joon Byun, Juheon Lee.
1. **[Swin Transformer](https://huggingface.co/docs/transformers/model_doc/swin)** (from Microsoft) released with the paper [Swin Transformer: Hierarchical Vision Transformer using Shifted Windows](https://huggingface.co/papers/2103.14030) by Ze Liu, Yutong Lin, Yue Cao, Han Hu, Yixuan Wei, Zheng Zhang, Stephen Lin, Baining Guo.
1. **[Swin2SR](https://huggingface.co/docs/transformers/model_doc/swin2sr)** (from University of Würzburg) released with the paper [Swin2SR: SwinV2 Transformer for Compressed Image Super-Resolution and Restoration](https://huggingface.co/papers/2209.11345) by Marcos V. Conde, Ui-Jin Choi, Maxime Burchi, Radu Timofte.
1. **[T5](https://huggingface.co/docs/transformers/model_doc/t5)** (from Google AI) released with the paper [Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer](https://huggingface.co/papers/1910.10683) by Colin Raffel and Noam Shazeer and Adam Roberts and Katherine Lee and Sharan Narang and Michael Matena and Yanqi Zhou and Wei Li and Peter J. Liu.
1. **[T5v1.1](https://huggingface.co/docs/transformers/model_doc/t5v1.1)** (from Google AI) released in the repository [google-research/text-to-text-transfer-transformer](https://github.com/google-research/text-to-text-transfer-transformer/blob/main/released_checkpoints.md#t511) by Colin Raffel and Noam Shazeer and Adam Roberts and Katherine Lee and Sharan Narang and Michael Matena and Yanqi Zhou and Wei Li and Peter J. Liu.
1. **[Table Transformer](https://huggingface.co/docs/transformers/model_doc/table-transformer)** (from Microsoft Research) released with the paper [PubTables-1M: Towards Comprehensive Table Extraction From Unstructured Documents](https://huggingface.co/papers/2110.00061) by Brandon Smock, Rohith Pesala, Robin Abraham.
1. **[TrOCR](https://huggingface.co/docs/transformers/model_doc/trocr)** (from Microsoft), released together with the paper [TrOCR: Transformer-based Optical Character Recognition with Pre-trained Models](https://huggingface.co/papers/2109.10282) by Minghao Li, Tengchao Lv, Lei Cui, Yijuan Lu, Dinei Florencio, Cha Zhang, Zhoujun Li, Furu Wei.
1. **Ultravox** (from Fixie.ai) released with the repository [fixie-ai/ultravox](https://github.com/fixie-ai/ultravox) by the Fixie.ai team.
1. **[UniSpeech](https://huggingface.co/docs/transformers/model_doc/unispeech)** (from Microsoft Research) released with the paper [UniSpeech: Unified Speech Representation Learning with Labeled and Unlabeled Data](https://huggingface.co/papers/2101.07597) by Chengyi Wang, Yu Wu, Yao Qian, Kenichi Kumatani, Shujie Liu, Furu Wei, Michael Zeng, Xuedong Huang.
1. **[UniSpeechSat](https://huggingface.co/docs/transformers/model_doc/unispeech-sat)** (from Microsoft Research) released with the paper [UNISPEECH-SAT: UNIVERSAL SPEECH REPRESENTATION LEARNING WITH SPEAKER AWARE PRE-TRAINING](https://huggingface.co/papers/2110.05752) by Sanyuan Chen, Yu Wu, Chengyi Wang, Zhengyang Chen, Zhuo Chen, Shujie Liu, Jian Wu, Yao Qian, Furu Wei, Jinyu Li, Xiangzhan Yu.
1. **[VaultGemma](https://huggingface.co/docs/transformers/main/model_doc/vaultgemma)** (from Google) released with the technical report [VaultGemma: A Differentially Private Gemma Model](https://services.google.com/fh/files/blogs/vaultgemma_tech_report.pdf) by the VaultGemma Google team.
1. **[Vision Transformer (ViT)](https://huggingface.co/docs/transformers/model_doc/vit)** (from Google AI) released with the paper [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://huggingface.co/papers/2010.11929) by Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, Neil Houlsby.
1. **[ViTMAE](https://huggingface.co/docs/transformers/model_doc/vit_mae)** (from Meta AI) released with the paper [Masked Autoencoders Are Scalable Vision Learners](https://huggingface.co/papers/2111.06377) by Kaiming He, Xinlei Chen, Saining Xie, Yanghao Li, Piotr Dollár, Ross Girshick.
1. **[ViTMatte](https://huggingface.co/docs/transformers/model_doc/vitmatte)** (from HUST-VL) released with the paper [ViTMatte: Boosting Image Matting with Pretrained Plain Vision Transformers](https://huggingface.co/papers/2305.15272) by Jingfeng Yao, Xinggang Wang, Shusheng Yang, Baoyuan Wang.
1. **[ViTMSN](https://huggingface.co/docs/transformers/model_doc/vit_msn)** (from Meta AI) released with the paper [Masked Siamese Networks for Label-Efficient Learning](https://huggingface.co/papers/2204.07141) by Mahmoud Assran, Mathilde Caron, Ishan Misra, Piotr Bojanowski, Florian Bordes, Pascal Vincent, Armand Joulin, Michael Rabbat, Nicolas Ballas.
1. **[ViTPose](https://huggingface.co/docs/transformers/model_doc/vitpose)** (from The University of Sydney) released with the paper [ViTPose: Simple Vision Transformer Baselines for Human Pose Estimation](https://huggingface.co/papers/2204.12484) by Yufei Xu, Jing Zhang, Qiming Zhang, Dacheng Tao.
1. **[VITS](https://huggingface.co/docs/transformers/model_doc/vits)** (from Kakao Enterprise) released with the paper [Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech](https://huggingface.co/papers/2106.06103) by Jaehyeon Kim, Jungil Kong, Juhee Son.
1. **[Voxtral](https://huggingface.co/docs/transformers/model_doc/voxtral)** (from Mistral AI) released with the paper [Voxtral](https://huggingface.co/papers/2507.13264) by Alexander H. Liu, Andy Ehrenberg, Andy Lo, Clément Denoix, Corentin Barreau, Guillaume Lample, Jean-Malo Delignon, Khyathi Raghavi Chandu, Patrick von Platen, Pavankumar Reddy Muddireddy, Sanchit Gandhi, Soham Ghosh, Srijan Mishra, Thomas Foubert, Abhinav Rastogi, Adam Yang, Albert Q. Jiang, Alexandre Sablayrolles, Amélie Héliou, Amélie Martin, Anmol Agarwal, Antoine Roux, Arthur Darcet, Arthur Mensch, Baptiste Bout, Baptiste Rozière, Baudouin De Monicault, Chris Bamford, Christian Wallenwein, Christophe Renaudin, Clémence Lanfranchi, Darius Dabert, Devendra Singh Chaplot, Devon Mizelle, Diego de las Casas, Elliot Chane-Sane, Emilien Fugier, Emma Bou Hanna, Gabrielle Berrada, Gauthier Delerce, Gauthier Guinet, Georgii Novikov, Guillaume Martin, Himanshu Jaju, Jan Ludziejewski, Jason Rute, Jean-Hadrien Chabran, Jessica Chudnovsky, Joachim Studnia, Joep Barmentlo, Jonas Amar, Josselin Somerville Roberts, Julien Denize, Karan Saxena, Karmesh Yadav, Kartik Khandelwal, Kush Jain, Lélio Renard Lavaud, Léonard Blier, Lingxiao Zhao, Louis Martin, Lucile Saulnier, Luyu Gao, Marie Pellat, Mathilde Guillaumin, Mathis Felardos, Matthieu Dinot, Maxime Darrin, Maximilian Augustin, Mickaël Seznec, Neha Gupta, Nikhil Raghuraman, Olivier Duchenne, Patricia Wang, Patryk Saffer, Paul Jacob, Paul Wambergue, Paula Kurylowicz, Philomène Chagniot, Pierre Stock, Pravesh Agrawal, Rémi Delacourt, Romain Sauvestre, Roman Soletskyi, Sagar Vaze, Sandeep Subramanian, Saurabh Garg, Shashwat Dalal, Siddharth Gandhi, Sumukh Aithal, Szymon Antoniak, Teven Le Scao, Thibault Schueller, Thibaut Lavril, Thomas Robert, Thomas Wang, Timothée Lacroix, Tom Bewley, Valeriia Nemychnikova, Victor Paltz , Virgile Richard, Wen-Ding Li, William Marshall, Xuanyu Zhang, Yihan Wan, Yunhao Tang.
1. **[Wav2Vec2](https://huggingface.co/docs/transformers/model_doc/wav2vec2)** (from Facebook AI) released with the paper [wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations](https://huggingface.co/papers/2006.11477) by Alexei Baevski, Henry Zhou, Abdelrahman Mohamed, Michael Auli.
1. **[Wav2Vec2-BERT](https://huggingface.co/docs/transformers/main/model_doc/wav2vec2-bert)** (from Meta AI) released with the paper [Seamless: Multilingual Expressive and Streaming Speech Translation](https://ai.meta.com/research/publications/seamless-multilingual-expressive-and-streaming-speech-translation/) by the Seamless Communication team.
1. **[WavLM](https://huggingface.co/docs/transformers/model_doc/wavlm)** (from Microsoft Research) released with the paper [WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing](https://huggingface.co/papers/2110.13900) by Sanyuan Chen, Chengyi Wang, Zhengyang Chen, Yu Wu, Shujie Liu, Zhuo Chen, Jinyu Li, Naoyuki Kanda, Takuya Yoshioka, Xiong Xiao, Jian Wu, Long Zhou, Shuo Ren, Yanmin Qian, Yao Qian, Jian Wu, Michael Zeng, Furu Wei.
1. **[Whisper](https://huggingface.co/docs/transformers/model_doc/whisper)** (from OpenAI) released with the paper [Robust Speech Recognition via Large-Scale Weak Supervision](https://cdn.openai.com/papers/whisper.pdf) by Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman, Christine McLeavey, Ilya Sutskever.
1. **[XLM](https://huggingface.co/docs/transformers/model_doc/xlm)** (from Facebook) released together with the paper [Cross-lingual Language Model Pretraining](https://huggingface.co/papers/1901.07291) by Guillaume Lample and Alexis Conneau.
1. **[XLM-RoBERTa](https://huggingface.co/docs/transformers/model_doc/xlm-roberta)** (from Facebook AI), released together with the paper [Unsupervised Cross-lingual Representation Learning at Scale](https://huggingface.co/papers/1911.02116) by Alexis Conneau*, Kartikay Khandelwal*, Naman Goyal, Vishrav Chaudhary, Guillaume Wenzek, Francisco Guzmán, Edouard Grave, Myle Ott, Luke Zettlemoyer and Veselin Stoyanov.
1. **[YOLOS](https://huggingface.co/docs/transformers/model_doc/yolos)** (from Huazhong University of Science & Technology) released with the paper [You Only Look at One Sequence: Rethinking Transformer in Vision through Object Detection](https://huggingface.co/papers/2106.00666) by Yuxin Fang, Bencheng Liao, Xinggang Wang, Jiemin Fang, Jiyang Qi, Rui Wu, Jianwei Niu, Wenyu Liu.



<!-- END: original content from transformers.md -->

---

## ai-compute-allocation-strategy

<!-- BEGIN: original content from ai-compute-allocation-strategy.md -->

*Source: `docs/bunchloch/meaisínfhoghlaim/ai-compute-allocation-strategy.md` (7463 words, 501 lines)*



# **A Strategic Blueprint for a Polyglot AI & Data Platform**

## **Part 1: The Unified Compute & Resource Allocation Strategy**

The foundation of this architecture is a unified compute and resource allocation strategy. This plan dictates how a diverse portfolio of premium AI APIs, specialized open-source models, and local hardware is provisioned, managed, and consumed. The primary objective is to move beyond simple, one-to-one task-to-model mapping and implement a sophisticated, hierarchical system. This system is designed to optimize for two critical, often opposing, vectors: maximum reasoning capability for complex tasks and minimum cost/latency for high-volume operations.  
This strategy is built on three pillars:

1. A tiered allocation framework that separates high-reasoning "Planner" models from high-speed "Worker" models.  
2. A centralized API gateway, leveraging LiteLLM and OpenRouter, to act as the single point of control for all AI calls, managing routing, cost, and abstraction.  
3. A clear cost-performance analysis defining the role of the M4 Max laptop as a powerful, zero-cost prototyping and development hub.

### **1.1 AI Compute Allocation Framework: A Tiered, Plan and Act Architecture**

The core of the allocation strategy is a hierarchical inference system. This "Plan and Act" model is a documented best practice for building robust and cost-effective agentic systems, as it reserves high-cost, high-reasoning models for tasks that require true cognition—such as planning, decomposition, and synthesis—while delegating well-defined, high-volume execution tasks to faster, cheaper models.1

#### **The Planner Tier (High Reasoning)**

This tier is reserved for the "brain" of the agentic system—the primary orchestrator within the Agno framework. Models in this tier must excel at understanding ambiguous, complex, multi-step user commands, decomposing them into a logical sequence of sub-tasks, and synthesizing the results from multiple "Worker" agents into a coherent final answer.1

* **Primary:** **GPT-5 Pro.** As the successor to GPT-4o, which is widely regarded as the "clear favorite" for orchestration layers 5, GPT-5 is the premier choice. Its design is centered on unified reasoning and state-of-the-art performance across domains 6, making it the most robust model available for interpreting user intent and planning complex workflows.  
* **Secondary:** **Claude Code Max.** This model serves as an excellent alternative or secondary option. Its primary strengths—a massive context window and SOTA performance in code-related reasoning 7—make it particularly suitable for "Planner" tasks that involve analyzing or refactoring large codebases or entire repositories, such as those packaged by Repomix.

#### **The Worker Tier (High Volume, Low Cost)**

This tier is the "workhorse" of the system.1 It is composed of models optimized for speed, low cost, and high throughput. These models are not intended to plan; they are designed to *execute* the simple, concrete, and well-defined sub-tasks generated by the "Planner" tier.8

* **Primary:** **Gemini 2.5 Flash.** This model is the ideal "workhorse." It is explicitly engineered for high-speed, low-cost execution, making it the default choice for high-volume, repetitive tasks.8 Its primary application will be as the engine for structured data extraction (the "Unstract" function from the project plan), where it can parse millions of documents or text chunks at a fraction of the cost of a "Planner" model.10 It is the designated "act" model in the "plan-and-act" workflow.8  
* **Secondary:** **Z.ai GLM Coding Max.** As a specialized coding model, this asset will serve as the default "Worker" for any task involving routine code generation, modification, or translation that does not warrant the full reasoning (and cost) of GPT-5 Pro or Claude Code Max.

#### **The Specialist Tier (Domain-Specific)**

This tier contains models with unique, non-textual capabilities, which are called upon by the "Planner" for specific domains.

* **Visual Analysis (VLM):** This is a critical specialty. The primary model will be the **Gemini 2.5 Pro** API, which has SOTA native document (PDF) and image understanding capabilities.10 This will be augmented by the project's own **fine-tuned Qwen3-VL** model 14, which will be hosted as a dedicated endpoint (detailed in Part 3.3). This custom model will handle domain-specific crypto charts and dashboards that the general-purpose Gemini may not understand.  
* **Safety & Filtering:** To ensure robust and secure agentic interactions, a guardrail model like **gpt-oss-safeguard-20b**, which is available via OpenRouter 15, will be configured as a filter for inputs and outputs, classifying content and preventing prompt injection or harmful responses.

This tiered approach is the only strategy that efficiently utilizes the entire spectrum of available API assets. Using a high-cost model like GPT-5 Pro for a high-volume "Worker" task, such as extracting text from 10,000 documents, would be financially irresponsible. Conversely, using a "Worker" model like Gemini 2.5 Flash to orchestrate a complex, multi-agent workflow would result in poor performance and logical failures.  
A concrete workflow example illustrates this:

1. A user issues a complex query to the "Master Planner" agent (running on **GPT-5 Pro**): "Analyze the latest Solana governance proposals, compare their technical arguments to the 'Qwen3-Bifrost-SOL-4B' model's knowledge base 14, and assess the potential impact."  
2. The "Planner" agent decomposes this into a multi-step plan.  
3. It first delegates to a web-search tool to find the proposal URLs.  
4. It then passes these URLs to the document processing pipeline (Crawl4AI \+ Docling), which uses the **Gemini 2.5 Pro (VLM)** or the **Qwen-VL** model to parse the complex PDF layouts.13  
5. The clean text from each proposal is passed in parallel to a "Worker" agent running on **Gemini 2.5 Flash**, with the prompt: "Extract all key technical arguments and proposed parameter changes from this text".11  
6. The "Planner" agent (GPT-5 Pro) collects the structured JSON outputs from all "Worker" agents.  
7. It then synthesizes these findings, formulates a query to the vector database containing the Qwen3-Bifrost-SOL-4B's knowledge, and generates the final, nuanced impact assessment.

This hierarchical process ensures that the most expensive compute (GPT-5 Pro) is used only for the two high-reasoning steps (planning and synthesis), while the high-volume, parallelizable work is handled by the low-cost Gemini 2.5 Flash.  
The following table provides a clear, actionable guide for this strategic allocation.

#### **Table 1: AI Compute Allocation Matrix**

| Task Category | Primary Compute | Secondary / Fallback | Not Recommended (Poor Cost/Perf) | Rationale |
| :---- | :---- | :---- | :---- | :---- |
| **1\. Agentic Orchestration (Planning)** | **GPT-5 Pro** (API) | Claude Code Max (API) | Gemini Flash, Local M4 Max | Highest-level reasoning and task decomposition is required.1 |
| **2\. High-Volume Text Extraction** | **Gemini 2.5 Flash** (API) | Z.ai GLM Max (API) | GPT-5 Pro, Claude Code Max | Cost-effective, high-speed, large-context "workhorse" model.8 |
| **3\. Complex Code Generation** | **Claude Code Max** (API) | GPT-5 Pro (API) | Gemini Flash | State-of-the-art code reasoning and large-context refactoring.7 |
| **4\. Routine Code Generation** | **Z.ai GLM Coding Max** (API) | GitHub Copilot (VSCode) | GPT-5 Pro | Specialized, lower-cost model for code-specific "worker" tasks. |
| **5\. VLM/OCR (Document Parsing)** | **Gemini 2.5 Pro** (API) | Fine-Tuned Qwen-VL (HF Pro) | GPT-5 Pro (if no vision) | SOTA native PDF/image understanding and structured output.10 |
| **6\. Local Dev & Prompt Testing** | **M4 Max (llama.cpp 7B/13B)** | Gemini 2.5 Flash (API) | GPT-5 Pro | Zero-cost, high-speed iteration for development loops. Private and secure.16 |
| **7\. Production Fine-Tuned Model** | **Hugging Face Pro Endpoint** | Google Cloud Endpoint | M4 Max (Laptop) | Deployed, scalable, and managed hosting for the custom Qwen-VL model.19 |

### **1.2 The Centralized Gateway: Architecting LiteLLM and OpenRouter**

The pre-configuration of LiteLLM is the most critical technical component for implementing the tiered strategy above. It will be architected as a *centralized, self-hosted proxy server* (LLM Gateway) 20, not merely used as a client-side Python library. This proxy becomes the *single, unified endpoint* for all internal services, including the Agno agent framework, Dagger CI/CD scripts, and even VSCode extensions.  
This architecture provides three essential functions:

1. **Centralized Key Management:** All provider API keys (OpenAI, Anthropic, Google, Z.ai, OpenRouter, Hugging Face) will be stored *only* in the LiteLLM proxy's configuration (e.g., a config.yaml file).23 All other applications (Agno, Dagger, etc.) will be keyless. They will authenticate to the proxy using a single, internally-generated LiteLLM key, dramatically simplifying security and key rotation.  
2. **Intelligent Routing:** The proxy configuration will define routing strategies to implement the tiered allocation framework.26  
3. **Unified Observability:** The proxy will be configured to log *every* request, response, token count, and cost to a central database (e.g., PostgreSQL) and stream detailed traces to Langfuse.27 This provides a single-pane-of-glass view into AI-related spend and performance across the entire organization.

The blueprint for the LiteLLM config.yaml will be as follows:

* **model\_list:** This section defines all *physical* compute assets, mapping them to specific provider credentials.24  
  * An entry for gpt-5-pro will point to the OpenAI API using the OPENAI\_API\_KEY.24  
  * An entry for claude-code-max will point to the Anthropic API using the ANTHROPIC\_API\_KEY.24  
  * Entries for gemini-2.5-pro and gemini-2.5-flash will point to the Google AI Studio API using the GEMINI\_API\_KEY.30  
  * An entry for openrouter/perplexity/sonar-pro will be defined to use the OpenRouter provider and its OPENROUTER\_API\_KEY.31  
  * An entry for custom/qwen-vl-tuned will point to the private Hugging Face Inference Endpoint (from Part 3.3).  
  * An entry for local-dev-model will point to the M4 Max's local llama.cpp server (from Part 1.3).32  
* **router:** This section defines the *virtual* model aliases (the "Plan and Act" tiers) that the Agno agents will call.  
  * A virtual model named "planner\_agent" will be defined. It will have a model\_list consisting of gpt-5-pro as the primary and claude-code-max as the fallback.26  
  * A virtual model named "worker\_agent" will be defined. It will route to a model\_list containing gemini-2.5-flash and z.ai-glm-max, using a cost\_based or least\_busy routing strategy.26  
  * The OpenRouter API key will be configured as the ultimate fallback for all other models, ensuring maximum availability.33

This architecture completely decouples the agent's logic from the physical model selection. The Agno agent framework (detailed in Part 5\) will be built without any hard-coded knowledge of "GPT" or "Claude." Instead, its agents will be configured to call task-based aliases like "planner\_agent" or "worker\_agent".35  
This is a superior architectural pattern. The Agno agent's code is simplified to model.call("worker\_agent",...). The LiteLLM proxy, not the agent, handles the complex, real-world logic: "Is Gemini Flash available? If not, try Z.ai GLM Max. If that fails, route to OpenRouter's mistral-small." This makes the agent logic clean, robust, and future-proof. Adding, removing, or changing API providers (e.g., if a new, cheaper model is released) becomes a simple config.yaml update in the LiteLLM proxy, without requiring a single line of code to be changed in the agentic application itself.

### **1.3 The Local Powerhouse: Cost-Performance Analysis of the M4 Max**

The 48GB M4 Max laptop is the cornerstone of the project's cost-control and rapid-prototyping strategy. Its primary function is to *eliminate* API costs during the 90% of development time spent on prompt engineering, logic debugging, and iterative testing.17
The 48GB of Unified Memory is the critical specification.17 This ample memory allows for the comfortable local execution of 33-billion parameter models at 4-bit quantization, and can potentially run models as large as 65B or 70B.36 While the M4 Max is significantly faster than previous generations 16, its inference speed on these large models will still be "unusable" for complex, real-time agentic coding tasks compared to a cloud API.16 Therefore, its role is not production inference, but *cost-free development*.

#### **The Three-Layer Local Inference Stack**

For multi-model local development, the architecture includes three complementary layers:

```
┌─────────────────────────────────────────────────────────────┐
│  Application Layer (Agno Agents, Dagger CI, VSCode)         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  LiteLLM Proxy (Unified API Gateway)                        │
│  - Single endpoint for all AI calls                         │
│  - Routes between cloud APIs and local models               │
│  - Cost tracking and observability                          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   Cloud APIs       llama-swap        Direct
   (GPT-5,          (VRAM Mgmt)       Local
    Claude)              │
                         ▼
                   llama.cpp server
                   (OpenAI-compatible)
```

1. **llama.cpp**: The inference engine providing OpenAI-compatible API at http://localhost:8080
2. **llama-swap**: VRAM management layer for hot-swapping between multiple models
3. **LiteLLM**: Unified routing layer that abstracts local vs cloud decisions

#### **llama-swap for Multi-Model Development**

When working with multiple local models (e.g., 7B for fast iteration, 70B for quality testing), llama-swap handles automatic model loading/unloading to prevent OOM errors:

```yaml
# llama-swap config.yaml
models:
  qwen-7b:
    path: /models/qwen2.5-7b-instruct-q4_k_m.gguf
    n_gpu_layers: 35
    ctx_size: 8192

  llama-70b:
    path: /models/llama-3.3-70b-q4_k_m.gguf
    n_gpu_layers: 60
    ctx_size: 4096

max_loaded_models: 1  # Auto-swap to prevent OOM
```

#### **Optimal Workflow**

The optimal workflow for leveraging the M4 Max is as follows:

1. **Setup:** The llama.cpp repository will be cloned and built locally with Metal (MPS) support enabled using the make cc=mps command. This ensures all inference is GPU-accelerated.38
2. **Model Acquisition:** Quantized GGUF models (e.g., 7B, 13B, or 33B variants) will be downloaded from Hugging Face.
3. **VRAM Management:** llama-swap runs in front of llama.cpp, handling model lifecycle and preventing memory exhaustion when switching between models.
4. **Local Server:** The llama.cpp server (./server) will be run. This instantly creates a high-performance, OpenAI-compatible API endpoint on http://localhost:8080.39
5. **LiteLLM Integration:** Both direct llama.cpp and llama-swap endpoints will be added as providers in a *development-specific* config.dev.yaml for the LiteLLM proxy (e.g., model\_name: "local\_dev\_model", litellm\_params: { "model": "openai/local-model", "api\_base": "http://localhost:8080/v1" }).32

This setup enables the "Dev-Loop" architecture, which is the "best way" to use the M4 Max. The development of complex Agno agents and BAML-structured outputs will require thousands of iterative test calls. Performing this iteration against the premium GPT-5 Pro API would be financially disastrous.  
Instead, the developer's workflow will be:

1. Write a new Agno agent or BAML file.  
2. Run the local test suite.  
3. The test suite is configured to call the local LiteLLM proxy.  
4. The proxy, using the config.dev.yaml, sees the call (e.g., to "planner\_agent") and routes it to the "local\_dev\_model" alias, which points to the llama.cpp server on localhost:8080.  
5. The developer receives an instant, free, and completely private response from the M4 Max.  
6. Once the agent's logic and prompt structure are validated, the developer runs a final "production" test by simply changing a single flag, which instructs LiteLLM to route the *exact same code and test* to the premium cloud APIs (GPT-5 Pro, Claude Code Max).

This workflow is only possible because llama.cpp provides an OpenAI-compatible API 39 and LiteLLM can treat any such API as a standard provider.25 This creates a seamless, powerful, and cost-effective development cycle.

## **Part 2: The Integrated Local Development Environment**

This section details the software configuration *on* the M4 Max, creating an integrated "cockpit" for polyglot development. This environment is designed to directly consume the compute strategies established in Part 1, maximizing developer ergonomics and velocity.

### **2.1 Maximizing the M4 Max Developer Experience (The Workflow)**

This provides the concrete, step-by-step commands for executing the "Dev-Loop" architecture described in Part 1.3.

1. **Step 1\. Install & Build llama.cpp:**  
   Bash  
   git clone https://github.com/ggerganov/llama.cpp.git  
   cd llama.cpp  
   make \-j cc=mps 

   This compiles llama.cpp with Apple Metal support for GPU acceleration.38  
2. **Step 2\. Download a GGUF Model:**  
   Bash  
   \# (Requires huggingface-cli: pip install huggingface-hub)  
   huggingface-cli download Qwen/Qwen2-7B-Instruct-GGUF qwen2-7b-instruct-q4\_K\_M.gguf \--local-dir./models

   A 7B model is recommended for high-speed local testing.  
3. **Step 3\. Run the Local OpenAI-Compatible Server:**  
   Bash  
   build/bin/Release/llama-server \-m models/qwen2-7b-instruct-q4\_K\_M.gguf \-c 4096 \--jinja

   This starts the server on http://localhost:8080, ready to accept API requests.38  
4. **Step 4\. Run the LiteLLM Proxy:**  
   Bash  
   \# (In a separate terminal)  
   \# Create config.dev.yaml  
   \# model\_list:  
   \#   \- model\_name: local-dev  
   \#     litellm\_params:  
   \#       model: openai/local  
   \#       api\_base: "http://localhost:8080/v1"  
   \#       api\_key: "unused"  
   \#   \- model\_name: planner\_agent \# Route planner to local for dev  
   \#     litellm\_params:  
   \#       model: openai/local  
   \#       api\_base: "http://localhost:8080/v1"  
   \#       api\_key: "unused"

   litellm \--config config.dev.yaml \--port 4000

   This starts the LiteLLM proxy on http://localhost:4000.32  
5. Step 5\. Develop & Test:  
   All Python scripts (Agno agents, BAML tests) will be configured with os.environ \= "http://localhost:4000/v1". Now, all application code runs against the local M4 Max for free.27

### **2.2 VSCode Super-Stack for Polyglot Development**

The suite of AI extensions is not redundant. When used strategically, they form a synergistic, multi-layered "Swiss Army knife" that maps directly to a developer's cognitive workflow. Using the wrong tool for the task (e.g., using an agentic tool for simple autocomplete) is inefficient. This workflow designates a specific role for each tool.

* **Layer 1: Inline Autocomplete (The "Typist")**  
  * **Tool:** **GitHub Copilot**.40  
  * **Workflow:** This is the passive, lowest-level, highest-speed loop. As the developer types, Copilot provides inline suggestions for the current line or block. Its primary use is for boilerplate, simple logic, and function completion.  
* **Layer 2: Chat & Refactoring (The "Reviewer")**  
  * **Tools:** **Claude Code** / **Codex**.42  
  * **Workflow:** This is an *active* loop. When a developer highlights an existing block of code, they will invoke the VSCode Chat view or a right-click context menu. Claude is noted for its superior ability to gather context from the entire file or project 43 and is the ideal choice for high-context tasks like: "Refactor this function," "Explain this complex class," or "Generate unit tests for this highlighted block." This layer is for *improving* existing code.  
* **Layer 3: Agentic Generation (The "Builder")**  
  * **Tools:** **RooCode** and **Agno Agents**.44  
  * **Workflow:** This is a *generative* loop. This is not for writing code line-by-line, but for *scaffolding* new features from a high-level command. The developer will use the RooCode panel to issue a natural language directive, such as: "Build a new Hono API route using the BAML schema 'UserProfile'" or "Create a new Dagger pipeline function to build the frontend." The RooCode 45 or an integrated Agno agent will then plan and execute this task, creating new files, modifying existing ones, and scaffolding the feature.  
* **Layer 4: Web Utility (The "Quick-Check")**  
  * **Tool:** **CodeWebChat**.47  
  * **Workflow:** This is the "out-of-band" utility. When a developer has a general, non-project-specific question (e.g., "What is the syntax for a Dagger recursive function?" or "What's the difference between two Python libraries?"), they will use the CodeWebChat panel. This provides a quick, free 48 interface to a web-based model like ChatGPT or Gemini 47 without polluting the project's chat context or requiring a browser.

A developer's workflow is not monolithic; it fluidly moves between typing, reviewing, and architecting. Using multiple AI extensions can be confusing if their roles are not defined. The workflow above provides this definition. GitHub Copilot is the established standard for inline autocomplete.41 However, it is often criticized for poor context-gathering on larger tasks.43 Claude is explicitly preferred for its high-context reasoning in a chat interface.43 This creates a natural and efficient split: Copilot for *typing*, Claude for *reviewing*.  
The agentic tools (RooCode, Agno) represent a completely different paradigm—*generation* (building new apps/features) 45, not *assistance*. Finally, CodeWebChat is a simple utility for web access.47 This 4-layer model (Typist, Reviewer, Builder, Utility) is therefore the optimal, non-conflicting ergonomic workflow to leverage *all* specified extensions.  
The following table provides a practical, one-page guide for the developer to follow.

#### **Table 2: VSCode AI Extension Workflow**

| Developer Task / Intent | Primary Tool | Action / Hotkey | Rationale |
| :---- | :---- | :---- | :---- |
| **Inline Autocomplete** ("The Typist") | **GitHub Copilot** | (auto-suggest as you type) | Fastest, line-level completion for boilerplate and simple logic.41 |
| **Block Refactor / Explanation** ("The Reviewer") | **Claude Code** / **Codex** | (Highlight code) \-\> Right-click \-\> "Claude:..." | High-context reasoning and refactoring for *existing* code blocks.43 |
| **Codebase Q\&A** ("The Navigator") | **Claude Code** / **Codex** | (Open Chat Panel) | Whole-project context-aware Q\&A ("Where is this function defined?"). |
| **New Component Generation** ("The Builder") | **RooCode** / **Agno Agent** | (RooCode Panel) \-\> "Build..." | Agentic, multi-file generation of *new* features from a prompt.45 |
| **General Web Query** ("The Utility") | **CodeWebChat** | (CWC Panel) \-\> "Chat..." | Quick, out-of-band access to web models like ChatGPT for general questions.47 |

## **Part 3: The End-to-End Data & ML Pipeline**

This part details the implementation of the project's data pipeline, a multi-stage workflow that transforms raw, multi-modal data from disparate sources into a unified, indexed, and queryable knowledge base. It also outlines the MLOps process for creating and deploying specialized, domain-specific models.

### **3.1 Ingestion Layer: DLT, Crawl4AI, and Repomix**

This layer, based on the "Stage Two" and integration plans 14, automates the acquisition of all required data types.

* **Structured API Data (DLT):** The DLT pipeline will be the primary tool for structured and semi-structured data.  
  * The implementation will leverage DLT's LLM-native scaffolding.14 The dlt init dlthub:github duckdb command will be used to auto-generate the initial pipeline code for GitHub data.14  
  * The github\_issues\_enhanced resource will be implemented as defined in stage\_2.md, using updated\_at as the dlt.sources.incremental cursor to ensure only new or updated issues are fetched, with stubs for future AI enrichment.14  
* **Unstructured Code Data (Git/Repomix):** To analyze the source code of crypto protocols, a two-step process will be used.  
  * First, the SparseCheckoutManager Python class from stage\_2.md will be implemented.14 This uses git sparse-checkout set to efficiently clone *only* relevant directories (e.g., src/, docs/, \*.md), avoiding heavy, unnecessary files.  
  * Second, the RepomixPackager class 14 will be used to execute the repomix \--compress \--output-format xml command. This packages the entire sparse repository into a single, token-efficient XML file, which serves as the primary context document for the Agno code analysis agents.  
* **Unstructured Web Data (Crawl4AI):** Crawl4AI will be configured to scrape crypto news sites, blogs, and governance forums.14 It will be orchestrated by DLT; a DLT resource will call the Crawl4AI library, which then fetches web content and PDFs, handing them off to the next stage of the pipeline.14

### **3.2 Advanced Document Processing: Docling, Qwen-VL, and Gemini**

This section details the critical "PDF Pipeline," which is essential for extracting data from complex visual documents like crypto whitepapers, audit reports, and dashboard screenshots.14

* **The Orchestrator (Docling):** While Crawl4AI *fetches* the PDFs, **Docling** will be the primary parsing framework. This is a crucial distinction. Crawl4AI will hand the raw PDF bytes to Docling.14 Docling's VlmPipeline 49 will be used, as it is specifically designed to route document pages to a Vision-Language Model (VLM) for layout-aware analysis, table extraction, and formula recognition.14  
* **The VLM Compute Choice (Hybrid Approach):** A hybrid strategy is required to balance cost, performance, and specialization.  
  * **Local Option (Qwen-VL on M4 Max):** For high-volume, private, or less complex documents, the fine-tuned Qwen-VL model 14 will be used. It will run as a GGUF on the M4 Max's llama.cpp server (as detailed in Part 1.3). The Docling VlmPipeline 49 will be configured to point to this local OpenAI-compatible endpoint (http://localhost:8080/v1).  
  * **Cloud Option (Gemini 2.5 Pro):** For high-complexity, high-value documents where accuracy is paramount, the pipeline will route to the **Gemini 2.5 Pro** API. Gemini is state-of-the-art for native PDF document processing, understanding complex layouts, charts, and tables directly.10 This call will be routed via the central LiteLLM proxy's "gemini-2.5-pro" alias.  
* **The Extractor (Up-leveling Unstract):** The original project plan identified a need for an "Unstract" component to perform LLM-powered structured data extraction from the parsed text.14 Given the available asset stack, this *function* will be implemented using a superior *tool*. Instead of integrating the Unstract platform, a dedicated Agno agent will be created that uses the **Gemini 2.5 Flash** API. Gemini Flash is cheaper, faster, and purpose-built for high-volume structured data extraction from text.11 This agent will consume the clean Markdown from Docling and return the required structured JSON, fulfilling the "Unstract" role more efficiently.

### **3.3 Specialized Fine-Tuning Workflow (Hugging Face Pro & Unsloth)**

This section provides the complete, step-by-step MLOps workflow for executing the fine-tuning plan 14, leveraging the Hugging Face Pro account, Google Cloud credits, and Unsloth.

1. **Step 1: Environment Setup (Google Cloud):** The £250 in Google Cloud credits will be used to provision a high-VRAM GPU-enabled VM (e.g., an A100 or H100 instance), as required for fine-tuning large models like GPT-OSS 20B.14  
2. **Step 2: Team & Data Setup (HF Pro):** The Hugging Face Pro account will be used to create a private "Organization" for the team.51 A new *private* Hugging Face Dataset repository will be created, and the cleaned, instruction-formatted crypto data (image-text pairs for Qwen-VL, text-text for GPT-OSS) 14 will be uploaded. This ensures the proprietary training data remains secure.52  
3. **Step 3: The Fine-Tuning Job (Unsloth on Google Cloud):**  
   * On the provisioned Google Cloud VM, pip install unsloth will be run.14  
   * A Python training script will be executed.55 This script will:  
     a. Use huggingface-cli login or login() from the huggingface\_hub library to authenticate with the HF Pro account token.52  
     b. Load the private dataset from the HF Pro Organization.  
     c. Load the base model (e.g., Qwen3-VL-8B or unsloth/gpt-oss-20b-bnb-4bit) using Unsloth's 4-bit QLoRA optimizations, which drastically reduce VRAM usage.14  
     d. Instantiate the SFTTrainer (Supervised Fine-tuning Trainer).55  
     e. Call trainer.train() to run the fine-tuning job.  
     f. Finally, call trainer.push\_to\_hub().56 This command will automatically save the resulting LoRA adapters and model configuration to a new, private model repository within the HF Pro Organization.  
4. **Step 4: Production Deployment (HF Pro):**  
   * Within the Hugging Face UI, the team will navigate to the newly created private model repository.  
   * Using the "Deploy" button, a **Hugging Face Inference Endpoint** will be instantiated.19 This is a fully managed, serverless API that hosts the fine-tuned model, providing a secure, scalable, and production-ready endpoint.57  
5. **Step 5: Integration:**  
   * The URL and API token for this new HF Inference Endpoint will be added to the central **LiteLLM proxy config.yaml** (from Part 1.2) under a new alias, such as custom/qwen-vl-crypto.

This workflow represents a professional, secure, and repeatable MLOps cycle. It correctly separates concerns: the Google Cloud credits are used for *ephemeral compute* (the resource-intensive training job), while the Hugging Face Pro account is used as the *persistent MLOps platform*—managing private data, versioning private models, and serving the final model in production.19

## **Part 4: The Production CI/CD & MLOps Framework**

This part details the "productionization" of the entire stack, creating a fully automated MLOps framework that translates code from a Git commit into a live, deployed, and secured service. This framework is built on Dagger for CI (Continuous Integration) and Komodo/Pangolin for CD (Continuous Deployment).

### **4.1 Dagger-Powered CI/CD (CI-as-Code)**

All CI/CD pipeline logic will be removed from traditional YAML files and implemented in code using Dagger, as outlined in the integration plan.14 This "CI-as-Code" approach is ideal for a polyglot monorepo, as it allows the build logic to be written in Python or TypeScript, co-located with the application code.  
A central Dagger pipeline script (e.g., ci/pipeline.py) will be created to orchestrate the entire build-test-publish lifecycle:

* **Unified Build Function:** A single build() function will orchestrate the building of all containerizeable components in parallel.  
  * build\_frontend(): A Dagger function that starts from a node:20 container, mounts the frontend/ directory, executes npm install and npm run build using Dagger's caching, and exports the resulting dist folder.  
  * build\_agent\_service(): A Dagger function starting from a python:3.11 container, mounting the backend/ directory, running pip install, and packaging the Agno, BAML, and LiteLLM proxy application code.  
  * build\_data\_pipeline(): A separate Dagger function for containerizing the DLT/Crawl4AI ingestion scripts.  
* **Unified Test Function:** A test() function will execute all integration tests. This function will leverage Dagger's **service container** capability 14 to spin up ephemeral services needed for testing, such as a PostgreSQL database (for DLT/SQLMesh), a DragonflyDB container (for caching tests), and the local llama.cpp server (for agent logic tests). This ensures tests run in a clean, isolated, and production-like environment every time.  
* **Unified Publish Function:** A main ci() function will be the entry point. It will call build() and test(). If both succeed, it will build the final, production-ready Docker images, tag them (e.g., with the Git SHA), and publish() them to a container registry (like GitHub Container Registry or a private HF Pro registry).

This Dagger-based approach is the "best way" to handle the CI for this polyglot monorepo. A single dagger.py script can coordinate the build for both the Python backend and the TypeScript frontend, sharing context, maximizing caching, and running steps in parallel.14 This is significantly more maintainable, powerful, and less error-prone than managing a complex web of interdependent GitHub Actions YAML files.

### **4.2 Automated GitOps with Komodo and Pangolin (CD-as-Code)**

This section details the automated handoff from Dagger (CI) to Komodo (CD), following the GitOps workflow.14

* **The Handoff:** The final, successful step of the Dagger ci() pipeline will be a simple curl or Python requests call that triggers a secure **Komodo webhook**.14  
* **Komodo's Role (Deployment):** Komodo, running on the provisioned Hetzner/OCI servers, is the GitOps deployment manager. Upon receiving the webhook, Komodo is configured to perform its core loop:  
  1. git pull the main branch of the repository to get the latest docker-compose.yml.  
  2. docker-compose pull to download the new container images that Dagger just published.  
  3. docker-compose up \-d to restart the services with the new images, performing a rolling update.  
* **Pangolin's Role (Zero-Trust Networking):** Pangolin is the secure networking and access-control layer for all deployed services.14  
  * **Internal Access (Private Model):** The **Pangolin Olm VPN** (Private Access Model) will be implemented.14 All internal dashboards and services (e.g., the Langfuse UI, Komodo admin panel, Dozzle container logs) will be defined as "Site Resources".14 These services will *not* have public DNS records and will be completely invisible to the internet. Team members must first connect to the network using the Olm VPN client to access these internal URLs. This is the most secure posture.  
  * **External Access (Public Model):** The **Pangolin Domain** (Public Access Model) will be used to expose *one and only one* service: the LiteLLM proxy server.14 Pangolin will provision a public domain (e.g., api.yourdomain.com), terminate HTTPS, and route traffic to the internal LiteLLM container. This creates the single, secure, public-facing gateway that the Agno agents and other external applications will use. This endpoint is, in turn, secured at the application layer by LiteLLM's own API key authentication.

## **Part 5: The Agentic Reasoning & Application Layer**

This part details the implementation of the "brain" of the system. It integrates the Agno agent framework, the BAML reliability layer, and the centralized compute gateway from Part 1 to build the "Crypto Analysis AI Agent System".14

### **5.1 Architecting the Agno Multi-Agent System**

The system will be built using Agno's multi-agent framework 59, based on the hierarchical "Plan and Act" model (from Part 1.1).

* **The "Master Planner" Agent:**  
  * **Framework:** This agent will be defined using agno.agent.Agent.59  
  * **Model:** It will be configured to call the "planner\_agent" alias from the LiteLLM proxy (which, in production, maps to GPT-5 Pro).  
  * **Tools:** It will be provisioned with a set of tools to orchestrate the system, including:  
    1. delegate\_task(task: str, agent\_alias: str): A tool that allows the Planner to call other "Worker" agents (e.g., "worker\_agent" or "code\_analysis\_agent").  
    2. query\_knowledge\_base(query: str): A tool to perform semantic search against the CocoIndex/Cognee vector store.14  
    3. search\_web(query: str): A tool for real-time data acquisition.  
* **The "Worker" Agents:** A pool of specialized agents will be created to execute concrete tasks delegated by the Planner.  
  * **DataExtractorAgent:** This agent runs on the "worker\_agent" alias (Gemini 2.5 Flash). Its sole purpose is to receive a URL or block of text and a BAML schema name, and return the extracted structured JSON.11  
  * **CodeAnalysisAgent:** This agent runs on the "z.ai-glm-max" alias. It receives a code snippet (e.g., from the Repomix context) and a task (e.g., "Find potential bugs," "Write documentation for this function").  
  * **VLMAnalysisAgent:** This agent runs on the "gemini-2.5-pro" alias (or the custom "custom/qwen-vl-crypto" alias). It receives an image or PDF page and a visual query.

### **5.2 Ensuring Reliability with BAML (AI-Generated BAML)**

A core requirement for a production agentic system is reliability. LLM outputs are probabilistic, but application code is not. We will use Boundary AI Markup Language (BAML) to enforce strict, schema-aligned, structured outputs from all agents.14  
This project will take a "meta-generative" approach to creating these BAML files. Writing complex BAML prompts and functions is a time-consuming task. The most powerful code-generation models (GPT-5 Pro, Claude Code Max) will be used to generate these BAML files.  
The workflow will be:

1. **Step 1: Define Intent (Python):** The developer defines the desired output structure as a simple Python dataclass or Pydantic model.  
   Python  
   \# (Example: user\_schema.py)  
   class CryptoProposalSummary:  
       title: str  
       protocol: str  
       key\_arguments: List\[str\]  
       impact\_assessment: str

2. **Step 2: Generate BAML (AI):** The developer uses a VSCode script (or the RooCode extension) to feed this class to **Claude Code Max** with a prompt: "Generate a BAML file that defines a function summarize\_proposal(text: str) \-\> CryptoProposalSummary. The function should robustly extract all fields from the provided text, paying close attention to the list of key\_arguments."  
3. **Step 3: AI Creates BAML:** The AI model generates the required .baml file.60  
4. **Step 4: Use in Agent (Python):** The BAML compiler generates Pydantic models from the `.baml` file. The Agno agent code can now use these generated Pydantic models as `response_model`, which is *guaranteed* to return a valid, type-checked CryptoProposalSummary object or raise an exception.

> **Note**: Agno uses Pydantic `response_model` natively. BAML's role is to define schemas in a DSL and generate the corresponding Pydantic models. The workflow is: BAML schema → Pydantic model → Agno agent.

This "AI-to-build-AI" workflow accelerates development, produces more robust and sophisticated prompts, and leverages the premium AI assets for the highest-leverage task: creating the reliability layer for all other agents.

### **5.3 Connecting Agents to Compute (The Final Integration)**

This section details the final piece of the architecture, connecting the Agno agent (Part 5.1) to the self-hosted LiteLLM proxy (Part 1.2), which is secured by Pangolin (Part 4.2).  
The implementation will follow the official Agno documentation for LiteLLM integration.35 The Agno agents will be instantiated to use a standard OpenAI client, but this client will be pointed *away* from OpenAI and *towards* the internal LiteLLM proxy's public-facing URL.  
An example agent configuration would look like this:

Python

from agno.agent import Agent  
from agno.models.openai import OpenAIChat \# Use the standard OpenAI client

\# This is the single, public URL for the LiteLLM proxy,   
\# secured and exposed by Pangolin.  
LITELLM\_PROXY\_BASE\_URL \= "https://api.yourdomain.com/v1" 

\# This is the internal API key generated by LiteLLM to protect its own endpoint.  
LITELLM\_API\_KEY \= "sk-litellm-internal-key-from-config" 

\# Configure the client to talk to our proxy  
\# The 'id' field here is the \*virtual model alias\* from the LiteLLM config  
client \= OpenAIChat(  
    id="planner\_agent",   
    api\_base=LITELLM\_PROXY\_BASE\_URL,  
    api\_key=LITELLM\_API\_KEY  
)

\# This agent is now configured to use the "planner\_agent" model.  
\# LiteLLM will handle routing this to GPT-5 Pro and its fallbacks.  
planner\_agent \= Agent(  
    name="MasterPlanner",  
    model=client,  
    instructions=  
)

This architecture completes the entire system loop. A call from the planner\_agent 59 is directed to the virtual "planner\_agent" alias. The request travels to the public URL api.yourdomain.com, which is secured by Pangolin.14 Pangolin routes the request internally to the LiteLLM proxy container. The LiteLLM proxy 26 validates the LITELLM\_API\_KEY, maps the "planner\_agent" alias to the gpt-5-pro model, retrieves the OPENAI\_API\_KEY from its private config, and makes the external call to OpenAI. The response flows all the way back, with the entire transaction being logged by LiteLLM and Langfuse.

## **Part 6: Unified Implementation Roadmap & Strategic Recommendations**

### **Implementation Roadmap**

This project will be executed in four distinct phases to manage complexity and ensure a stable, iterative rollout.

* **Phase 1: Foundation (Local & Cloud)**  
  1. **Local Setup:** Configure the M4 Max with the full VSCode "Super-Stack" and build the llama.cpp server.38  
  2. **Cloud Provisioning:** Provision the Hetzner/OCI compute server. Install and configure Komodo for GitOps deployment.14  
  3. **Gateway Deployment:** Containerize and deploy the LiteLLM proxy via Komodo.21 Create the master config.yaml file with all API keys and add the local-dev-model (pointing to localhost:8080).23  
  4. **Network Configuration:** Deploy Pangolin. Expose the LiteLLM proxy using the "Public Model" and secure all other internal services (Komodo UI, etc.) using the "Private (Olm VPN) Model".14  
* **Phase 2: Data & MLOps Pipeline (CI/CD)**  
  1. **CI/CD Implementation:** Write the core Dagger pipeline (dagger.py) for the polyglot monorepo, including build, test (with service containers), and publish functions.14  
  2. **MLOps Execution:** Execute the "Fine-Tuning Plan".14 Use Google Cloud credits for the Unsloth training job. Use the HF Pro account to store the private data, host the private model adapters, and deploy the final model as a managed Inference Endpoint.19  
  3. **Gateway Update:** Add the newly deployed HF Inference Endpoint's URL and token to the production LiteLLM config.yaml as a new "Specialist" model.  
* **Phase 3: Data Ingestion (The Pipeline)**  
  1. **Script Implementation:** Implement the data ingestion scripts: DLT for APIs 14, Crawl4AI for web fetching 14, and Repomix for code packaging.14  
  2. **Parsing Pipeline:** Implement the Docling VlmPipeline 14, configuring it to route to the LiteLLM proxy (which can then select between the local Qwen-VL or cloud Gemini 2.5 Pro).  
  3. **Orchestration:** Create a Dagger run\_ingestion() function that containerizes and executes this entire data pipeline.  
* **Phase 4: Agentic System (The Brain)**  
  1. **Reliability Layer:** Define all agent output schemas as Python Pydantic models. Use the premium code models (Claude Code Max, GPT-5 Pro) to "meta-generate" the corresponding BAML files.60  
  2. **Agent Orchestration:** Build the Agno multi-agent system, defining the "Master Planner" and its "Worker" agents.59  
  3. **Final Integration:** Connect the Agno agents to the LiteLLM proxy's public URL, as detailed in Part 5.3, to complete the end-to-end system.35

### **Strategic Recommendations**

This analysis of the available assets and project goals concludes with three primary strategic recommendations that form the "best way" to implement this system:

1. **Abstraction is Key:** The LiteLLM proxy is the single most strategic asset in this stack. It *must* be implemented as a central, self-hosted gateway. It is the only component that should hold provider-level API keys. All other applications (Agno, Dagger, VSCode) must be configured to call the LiteLLM proxy's unified endpoint. This decouples the application logic from the rapidly changing compute market, controls costs, and provides total observability.  
2. **Tier Your Compute:** The "Planner/Worker" (or "Plan and Act") model is the only financially and technically viable way to use the specified portfolio of APIs. The premium, high-cost models (GPT-5 Pro, Claude Code Max) must be reserved *only* for high-reasoning orchestration and synthesis tasks. The fast, low-cost models (Gemini 2.5 Flash, Z.ai GLM) must be used for all high-volume, parallelizable execution tasks.  
3. **Leverage AI to Build AI:** The project has access to SOTA code generation models. These should be used for the highest-leverage meta-tasks to accelerate development and improve reliability. This includes using them to write the BAML reliability files (as described in Part 5.2) and to scaffold the DLT data pipelines (as described in Part 3.1).14 This approach treats the AI as a force multiplier for building the system itself.

#### **Works cited**

1. Reasoning best practices \- OpenAI API, accessed on November 9, 2025, [https://platform.openai.com/docs/guides/reasoning-best-practices](https://platform.openai.com/docs/guides/reasoning-best-practices)  
2. Strategic LLM Selection Guide \- CrewAI Documentation, accessed on November 9, 2025, [https://docs.crewai.com/en/learn/llm-selection-guide](https://docs.crewai.com/en/learn/llm-selection-guide)  
3. Cost optimization \- AWS Prescriptive Guidance, accessed on November 9, 2025, [https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-serverless/cost-optimization.html](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-serverless/cost-optimization.html)  
4. Taming the Beast: Cost Optimization Strategies for LLM API Calls in Production \- Medium, accessed on November 9, 2025, [https://medium.com/@ajayverma23/taming-the-beast-cost-optimization-strategies-for-llm-api-calls-in-production-11f16dbe2c39](https://medium.com/@ajayverma23/taming-the-beast-cost-optimization-strategies-for-llm-api-calls-in-production-11f16dbe2c39)  
5. GPT vs Claude vs Gemini for Agent Orchestration | by Devansh \- Medium, accessed on November 9, 2025, [https://machine-learning-made-simple.medium.com/gpt-vs-claude-vs-gemini-for-agent-orchestration-b3fbc584f0f7](https://machine-learning-made-simple.medium.com/gpt-vs-claude-vs-gemini-for-agent-orchestration-b3fbc584f0f7)  
6. Most powerful LLMs (Large Language Models) in 2025 \- Codingscape, accessed on November 9, 2025, [https://codingscape.com/blog/most-powerful-llms-large-language-models](https://codingscape.com/blog/most-powerful-llms-large-language-models)  
7. What's your Base/Premium model selection after GPT-5/Mini Release? : r/GithubCopilot, accessed on November 9, 2025, [https://www.reddit.com/r/GithubCopilot/comments/1nsksm8/whats\_your\_basepremium\_model\_selection\_after/](https://www.reddit.com/r/GithubCopilot/comments/1nsksm8/whats_your_basepremium_model_selection_after/)  
8. Best practices for optimizing top-model usage cost (Gemini 2.5, Sonnet 3.7, etc.)? : r/CLine, accessed on November 9, 2025, [https://www.reddit.com/r/CLine/comments/1k1813u/best\_practices\_for\_optimizing\_topmodel\_usage\_cost/](https://www.reddit.com/r/CLine/comments/1k1813u/best_practices_for_optimizing_topmodel_usage_cost/)  
9. Low-Cost LLMs: An API Price & Performance Comparison | IntuitionLabs, accessed on November 9, 2025, [https://intuitionlabs.ai/articles/low-cost-llm-comparison](https://intuitionlabs.ai/articles/low-cost-llm-comparison)  
10. Document understanding | Gemini API | Google AI for Developers, accessed on November 9, 2025, [https://ai.google.dev/gemini-api/docs/document-processing](https://ai.google.dev/gemini-api/docs/document-processing)  
11. Use Gemini 2.0 to speed up data processing | Google Cloud Blog, accessed on November 9, 2025, [https://cloud.google.com/blog/products/ai-machine-learning/use-gemini-2-0-to-speed-up-data-processing](https://cloud.google.com/blog/products/ai-machine-learning/use-gemini-2-0-to-speed-up-data-processing)  
12. How Gemini 2.0 Flash is Revolutionizing Table Extraction from PDFs: A Deep Dive with Real Benchmarks | by Infinity | Medium, accessed on November 9, 2025, [https://medium.com/@sahil0094/how-gemini-2-0-be927d57338a](https://medium.com/@sahil0094/how-gemini-2-0-be927d57338a)  
13. Gemini 2.5 Cost and Quality Comparison | Pricing & Performance \- Leanware, accessed on November 9, 2025, [https://www.leanware.co/insights/gemini-2-5-cost-quality-comparison](https://www.leanware.co/insights/gemini-2-5-cost-quality-comparison)  
14. End-to-End Workflow for Analyzing Local Git Repositories with DLT, CocoIndex, Repomix, Agno, and BAM.pdf  
15. Models \- OpenRouter, accessed on November 9, 2025, [https://openrouter.ai/models](https://openrouter.ai/models)  
16. MacBook M4 Max isn't great for LLMs : r/LocalLLaMA \- Reddit, accessed on November 9, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/1jn5uto/macbook\_m4\_max\_isnt\_great\_for\_llms/](https://www.reddit.com/r/LocalLLaMA/comments/1jn5uto/macbook_m4_max_isnt_great_for_llms/)  
17. The Best Local LLMs To Run On Every Mac (Apple Silicon) \- ApX Machine Learning, accessed on November 9, 2025, [https://apxml.com/posts/best-local-llm-apple-silicon-mac](https://apxml.com/posts/best-local-llm-apple-silicon-mac)  
18. llama.cpp guide \- Running LLMs locally, on any hardware, from scratch ::, accessed on November 9, 2025, [https://steelph0enix.github.io/posts/llama-cpp-guide/](https://steelph0enix.github.io/posts/llama-cpp-guide/)  
19. Run Inference on servers \- Hugging Face, accessed on November 9, 2025, [https://huggingface.co/docs/huggingface\_hub/en/guides/inference](https://huggingface.co/docs/huggingface_hub/en/guides/inference)  
20. LiteLLM: Flexible and Secure LLM Access for Organizations | by Infralovers GmbH \- Medium, accessed on November 9, 2025, [https://medium.com/@infralovers/litellm-flexible-and-secure-llm-access-for-organizations-4dd19720f04b](https://medium.com/@infralovers/litellm-flexible-and-secure-llm-access-for-organizations-4dd19720f04b)  
21. LiteLLM \- Getting Started, accessed on November 9, 2025, [https://docs.litellm.ai/docs/](https://docs.litellm.ai/docs/)  
22. LiteLLM \- Getting Started | liteLLM, accessed on November 9, 2025, [https://docs.litellm.ai/](https://docs.litellm.ai/)  
23. Setting API Keys, Base, Version \- LiteLLM, accessed on November 9, 2025, [https://docs.litellm.ai/docs/set\_keys](https://docs.litellm.ai/docs/set_keys)  
24. BerriAI/litellm: Python SDK, Proxy Server (LLM Gateway) to call 100+ LLM APIs in OpenAI format \- \[Bedrock, Azure, OpenAI, VertexAI, Cohere, Anthropic, Sagemaker, HuggingFace, Replicate, Groq\] \- GitHub, accessed on November 9, 2025, [https://github.com/BerriAI/litellm](https://github.com/BerriAI/litellm)  
25. Providers \- LiteLLM, accessed on November 9, 2025, [https://docs.litellm.ai/docs/providers](https://docs.litellm.ai/docs/providers)  
26. Load Balancing \- Router \- LiteLLM, accessed on November 9, 2025, [https://docs.litellm.ai/docs/routing](https://docs.litellm.ai/docs/routing)  
27. Cookbook: LiteLLM (Proxy) \+ Langfuse OpenAI Integration \+ @observe Decorator, accessed on November 9, 2025, [https://langfuse.com/guides/cookbook/integration\_litellm\_proxy](https://langfuse.com/guides/cookbook/integration_litellm_proxy)  
28. Comprehensive LiteLLM Configuration Guide (config.yaml with all options included), accessed on November 9, 2025, [https://dev.to/yigit-konur/comprehensive-litellm-configuration-guide-configyaml-with-all-options-included-3e65](https://dev.to/yigit-konur/comprehensive-litellm-configuration-guide-configyaml-with-all-options-included-3e65)  
29. Logging \- LiteLLM, accessed on November 9, 2025, [https://docs.litellm.ai/docs/proxy/logging](https://docs.litellm.ai/docs/proxy/logging)  
30. Gemini \- Google AI Studio \- LiteLLM, accessed on November 9, 2025, [https://docs.litellm.ai/docs/providers/gemini](https://docs.litellm.ai/docs/providers/gemini)  
31. OpenRouter \- LiteLLM, accessed on November 9, 2025, [https://docs.litellm.ai/docs/providers/openrouter](https://docs.litellm.ai/docs/providers/openrouter)  
32. LiteLLM Proxy (LLM Gateway), accessed on November 9, 2025, [https://docs.litellm.ai/docs/providers/litellm\_proxy](https://docs.litellm.ai/docs/providers/litellm_proxy)  
33. What are the advantage of LiteLLM over gateway like OpenRouter and Together \- Reddit, accessed on November 9, 2025, [https://www.reddit.com/r/LLMDevs/comments/1nxtmtv/what\_are\_the\_advantage\_of\_litellm\_over\_gateway/](https://www.reddit.com/r/LLMDevs/comments/1nxtmtv/what_are_the_advantage_of_litellm_over_gateway/)  
34. LiteLLM vs OpenRouter: Which is Best For You ? \- TrueFoundry, accessed on November 9, 2025, [https://www.truefoundry.com/blog/litellm-vs-openrouter](https://www.truefoundry.com/blog/litellm-vs-openrouter)  
35. LiteLLM \- Agno, accessed on November 9, 2025, [https://docs.agno.com/concepts/models/litellm](https://docs.agno.com/concepts/models/litellm)  
36. Advice Needed: Choosing the Right MacBook Pro Configuration for Local AI LLM Inference, accessed on November 9, 2025, [https://www.reddit.com/r/LocalLLM/comments/1gie5uq/advice\_needed\_choosing\_the\_right\_macbook\_pro/](https://www.reddit.com/r/LocalLLM/comments/1gie5uq/advice_needed_choosing_the_right_macbook_pro/)  
37. I did a quick test of MacBook M4 Max 128 GB token/second throughput across a few popular local LLMs (in the MLX format) \- Reddit, accessed on November 9, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/1i7b3r1/i\_did\_a\_quick\_test\_of\_macbook\_m4\_max\_128\_gb/](https://www.reddit.com/r/LocalLLaMA/comments/1i7b3r1/i_did_a_quick_test_of_macbook_m4_max_128_gb/)  
38. Best Ways to Run LLM Locally on Mac \- DEV Community, accessed on November 9, 2025, [https://dev.to/mehmetakar/5-ways-to-run-llm-locally-on-mac-cck](https://dev.to/mehmetakar/5-ways-to-run-llm-locally-on-mac-cck)  
39. guide : running gpt-oss with llama.cpp \#15396 \- GitHub, accessed on November 9, 2025, [https://github.com/ggml-org/llama.cpp/discussions/15396](https://github.com/ggml-org/llama.cpp/discussions/15396)  
40. Quickstart for GitHub Copilot, accessed on November 9, 2025, [https://docs.github.com/en/copilot/get-started/quickstart](https://docs.github.com/en/copilot/get-started/quickstart)  
41. GitHub Copilot in VS Code, accessed on November 9, 2025, [https://code.visualstudio.com/docs/copilot/overview](https://code.visualstudio.com/docs/copilot/overview)  
42. Using Claude Code with GitHub Copilot: A Guide | by Anders Sveen | Sep, 2025 | Medium, accessed on November 9, 2025, [https://anderssv.medium.com/using-claude-code-with-github-copilot-a-guide-42904ea6dce0](https://anderssv.medium.com/using-claude-code-with-github-copilot-a-guide-42904ea6dce0)  
43. Deploying Claude Code vs GitHub CoPilot for developers at a large (1000+ user) enterprise, accessed on November 9, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1m0yiab/deploying\_claude\_code\_vs\_github\_copilot\_for/](https://www.reddit.com/r/ClaudeAI/comments/1m0yiab/deploying_claude_code_vs_github_copilot_for/)  
44. Working with Large Projects | Roo Code Documentation, accessed on November 9, 2025, [https://docs.roocode.com/advanced-usage/large-projects](https://docs.roocode.com/advanced-usage/large-projects)  
45. Your Ultimate AI Coding Agent: Roo Code \+ Visual Studio Code \- YouTube, accessed on November 9, 2025, [https://www.youtube.com/watch?v=hRxjMTyB-GA](https://www.youtube.com/watch?v=hRxjMTyB-GA)  
46. Reflecting on building my first webapp with Roo-Code on VSCode : r/RooCode \- Reddit, accessed on November 9, 2025, [https://www.reddit.com/r/RooCode/comments/1j5jyq2/reflecting\_on\_building\_my\_first\_webapp\_with/](https://www.reddit.com/r/RooCode/comments/1j5jyq2/reflecting_on_building_my_first_webapp_with/)  
47. Code Web Chat \- Visual Studio Marketplace, accessed on November 9, 2025, [https://marketplace.visualstudio.com/items?itemName=robertpiosik.gemini-coder](https://marketplace.visualstudio.com/items?itemName=robertpiosik.gemini-coder)  
48. Exploring 7 Lesser Known AI Coding Extensions for VS Code \- Diploi, accessed on November 9, 2025, [https://diploi.com/blog/exploring-7-lesser-known-ai-coding-extensions](https://diploi.com/blog/exploring-7-lesser-known-ai-coding-extensions)  
49. Vision models \- Docling \- GitHub Pages, accessed on November 9, 2025, [https://docling-project.github.io/docling/usage/vision\_models/](https://docling-project.github.io/docling/usage/vision_models/)  
50. Gemini 2.0 vs. Agentic RAG: Who wins at Structured Information Extraction? | Unstructured, accessed on November 9, 2025, [https://unstructured.io/blog/gemini-2-0-vs-agentic-rag-who-wins-at-structured-information-extraction](https://unstructured.io/blog/gemini-2-0-vs-agentic-rag-who-wins-at-structured-information-extraction)  
51. PRO Account \- Hugging Face, accessed on November 9, 2025, [https://huggingface.co/pro](https://huggingface.co/pro)  
52. Fine-tuning \- Hugging Face, accessed on November 9, 2025, [https://huggingface.co/docs/transformers/en/training](https://huggingface.co/docs/transformers/en/training)  
53. Using hugging face models with private company data? \- Beginners, accessed on November 9, 2025, [https://discuss.huggingface.co/t/using-hugging-face-models-with-private-company-data/56403](https://discuss.huggingface.co/t/using-hugging-face-models-with-private-company-data/56403)  
54. Make LLM Fine-tuning 2x faster with Unsloth and TRL \- Hugging Face, accessed on November 9, 2025, [https://huggingface.co/blog/unsloth-trl](https://huggingface.co/blog/unsloth-trl)  
55. Fine-Tuning Your First Large Language Model (LLM) with PyTorch and Hugging Face, accessed on November 9, 2025, [https://huggingface.co/blog/dvgodoy/fine-tuning-llm-hugging-face](https://huggingface.co/blog/dvgodoy/fine-tuning-llm-hugging-face)  
56. Fine-tuning \- Hugging Face, accessed on November 9, 2025, [https://huggingface.co/docs/transformers/training](https://huggingface.co/docs/transformers/training)  
57. Deploy models with Hugging Face Inference Endpoints \- YouTube, accessed on November 9, 2025, [https://www.youtube.com/watch?v=ZQPm2-uR9zA](https://www.youtube.com/watch?v=ZQPm2-uR9zA)  
58. Run and manage Jobs \- Hugging Face, accessed on November 9, 2025, [https://huggingface.co/docs/huggingface\_hub/en/guides/jobs](https://huggingface.co/docs/huggingface_hub/en/guides/jobs)  
59. agno-agi/agno: Multi-agent framework, runtime and control plane. Built for speed, privacy, and scale. \- GitHub, accessed on November 9, 2025, [https://github.com/agno-agi/agno](https://github.com/agno-agi/agno)  
60. Stop Parsing LLMs with Regex: Build Production-Ready AI Features with Schema-Enforced Outputs \- DEV Community, accessed on November 9, 2025, [https://dev.to/dthompsondev/llm-structured-json-building-production-ready-ai-features-with-schema-enforced-outputs-4j2j](https://dev.to/dthompsondev/llm-structured-json-building-production-ready-ai-features-with-schema-enforced-outputs-4j2j)

<!-- END: original content from ai-compute-allocation-strategy.md -->

---

## Asset Management for Full-Stack App

*Source: `docs/bunchloch/teanga/Asset Management for Full-Stack App.md` (4341 words, 355 lines)*

# **Strategic Asset Management and Visual Architecture for Full-Stack Educational Platforms**

## **Executive Overview and Architectural Vision**

The development of a full-stack educational application targeting the Irish secondary school curriculum—specifically the Leaving Certificate—requires a sophisticated synthesis of pedagogical design, visual aesthetics, and robust software engineering. The modern educational technology landscape has shifted away from sterile, utilitarian interfaces toward gamified, engaging environments that borrow heavily from the visual language of video games. In this context, the decision to utilize a pixel art aesthetic is not merely a stylistic preference but a strategic functional choice. Pixel art, by its nature, offers distinct advantages in terms of file size optimization, visual clarity at small scales, and an inherent association with progression and achievement systems found in Role-Playing Games (RPGs). However, implementing this aesthetic within a modern React and Node.js ecosystem presents a unique set of technical challenges that differ significantly from handling standard photographic or vector assets.  
This report provides an exhaustive analysis of the end-to-end strategy for sourcing, creating, managing, and delivering digital assets for such a platform. It addresses the specific needs of niche curricula, such as Gaeilge (Irish Language), Agricultural Science, and Construction Studies, which are often underserved by generic stock photography libraries. Furthermore, it details the backend infrastructure required to manage these assets efficiently, comparing solutions like UploadThing and Cloudinary, and outlines the precise frontend engineering techniques necessary to render low-resolution art crisply on high-density displays. The analysis is grounded in the current ecosystem of 2024-2025, considering the latest capabilities of Next.js, the rise of AI-driven asset generation, and the evolving best practices for full-stack asset pipelines.

## **Visual Semiotics and Curriculum Representation**

The visual representation of academic subjects constitutes the primary navigational interface for the student. These icons act as semantic anchors; they must be instantly decoding the subject matter without linguistic friction. In the medium of pixel art, where resolution is limited (typically to grids of 16x16 or 32x32 pixels), the challenge of representation becomes acute. The designer must rely on metonymy—using a distinct part to represent the whole—to convey complex abstract concepts like "Business Studies" or "Applied Mathematics" within a constrained pixel grid.

### **The Gamification Metaphor in Education**

The utilization of pixel art inherently frames the educational journey as a game. This is a powerful psychological lever. When a student sees their subjects represented by icons that stylistically resemble an RPG inventory, the psychological association shifts from "work" to "progression."

* **Inventory Management:** The dashboard of subjects parallels the inventory screen of an RPG. Just as a player manages swords, potions, and maps, a student manages Mathematics, English, and Biology.  
* **Skill Trees:** The hierarchical nature of the Leaving Certificate (Subjects \> Levels \> Topics) maps perfectly to the "Skill Tree" visual metaphor common in games.  
* **Asset Cohesion:** The critical factor here is consistency. If the Mathematics icon is a flat vector while the Biology icon is a shaded pixel art sprite, the immersion breaks. The assets must share a "texel density" (the ratio of texture pixels to screen pixels) and a color palette to feel like part of a unified system.

### **Subject-Specific Asset Strategies**

The Irish Leaving Certificate curriculum contains subjects that defy the generic categorization found in most global asset packs. A nuanced sourcing strategy is required to represent these subjects accurately and respectfully.

#### **Gaeilge (Irish Language)**

Representing a language visually often defaults to national flags, but this can be reductive. For Gaeilge, the visual language must communicate "speaking" and "culture" simultaneously. The research indicates that while stock sites often use generic shamrocks or leprechaun hats, these can border on caricature. A more academic and respectful approach involves the synthesis of the national tricolour with communication symbols.1  
A pixel art speech bubble containing the green, white, and orange tricolour is the most effective semantic shorthand for "Oral Irish" or the language itself.3 For more advanced or literary aspects of the course (Prose, Poetry), iconography such as the Celtic Knot or the Harp offers a sophisticated alternative that avoids tourist tropes.4 The challenge with Celtic Knots in pixel art is the resolution; complex interlace patterns turn into noise at 32x32 pixels. Therefore, simplified knotwork or the bold silhouette of a Harp is preferable for readability at icon size.

#### **Agricultural Science**

"Ag Science" is a flagship subject in the Irish curriculum that bridges the gap between biology and industrial farming. Generic "science" icons (flasks) are insufficient, and generic "farm" icons (cute animals) are too infantile for secondary school students. The optimal source for these assets lies in the "Farming Simulation" game genre.6  
Asset packs designed for games like Stardew Valley or Harvest Moon often contain highly detailed, mature pixel art representations of tractors, wheat sheaves, soil cross-sections, and livestock.7 These assets are designed for adults/young adults and carry the correct tone of "technical farming" rather than "nursery rhyme farming." A pixelated tractor or a cross-section of a seed germinating serves as an excellent identifier for this subject.9

#### **Construction Studies and Engineering**

These practical subjects require precise differentiation. Construction Studies focuses on the built environment, while Engineering focuses on mechanics and precision.

* **Construction Studies:** Icons representing architectural blueprints, trowels, or house frames are ideal. The visual metaphor of a "House under construction" or a "Blueprint roll" works well in pixel art because the straight lines of architecture align with the pixel grid.10  
* **Engineering:** This requires mechanical precision. Icons of gears, calipers, or micrometers are appropriate. However, calipers consist of very fine lines which often disappear or alias badly in low-resolution pixel art. Heavier tools like a micrometer or a complex gear system are more readable.12

#### **Home Economics (Social and Scientific)**

This subject is multidisciplinary, covering food science, textiles, and sociology. The "Food" aspect is the easiest to represent visually and the most distinct from other subjects.  
The indie game development community has produced vast libraries of "RPG Food" assets—pixel art depictions of bread, meats, stews, and ingredients used in game crafting systems.14 These assets are often distinct, colorful, and appetizing, making them perfect for Home Economics. For a more comprehensive icon, a pixelated "Chef's Hat" or "Whisk" can complement the food imagery.16

#### **Mathematics and Applied Mathematics**

While seemingly generic, Math requires care in pixel art. A calculator is often indistinguishable from a mobile phone at low resolution. Geometric shapes (a set square, a protractor, or a 3D cube) are superior because their distinct silhouettes remain recognizable even when heavily pixelated.17 For Applied Mathematics, which involves mechanics, a projectile motion trajectory or a pulley system icon (often found in "Physics" or "Puzzle Game" asset packs) is effective.18

| Subject | Recommended Icon Concept | Potential Pitfalls | Optimal Source Category |
| :---- | :---- | :---- | :---- |
| **Gaeilge** | Speech Bubble w/ Tricolour | Stereotypical imagery (Leprechauns) | Language Learning / Flags |
| **Maths** | Set Square / Protractor | Calculator (looks like phone) | Education Vectors / Geomtry |
| **Ag Science** | Tractor / Germinating Seed | "Cute" farm animals | Farming Sim Game Assets |
| **Construction** | Blueprint / Trowel | Generic "House" icon | City Builder Assets |
| **Engineering** | Gear / Micrometer | Thin-line tools (Calipers) | Industrial/Sci-Fi Game Assets |
| **Home Ec** | Bread / Stew / Whisk | Fast food icons | RPG Food / Crafting Packs |

## **Strategic Sourcing of Digital Assets**

Building a coherent visual library requires a procurement strategy that balances quality, cost, and legal compliance. Relying on a single source is rarely feasible for a broad curriculum; thus, a hybrid approach of "Buy," "Convert," and "Generate" is recommended.

### **The "Buy" Strategy: Game Asset Marketplaces**

The highest quality pixel art is found not on stock photography sites, but on game development marketplaces. These assets are created by pixel artists specifically for digital interfaces, ensuring correct shading, palette consistency, and readability.  
**Itch.io** is the premier marketplace for this aesthetic.8

* **Icon Packs:** Packs such as "100 Skill Icons" or "RPG Inventory Packs" provide hundreds of items that can be metaphorically mapped to subjects (e.g., a "Scroll" for History, a "Potion" for Chemistry).20  
* **UI Kits:** Complete User Interface kits (buttons, panels, sliders) ensure that the surrounding application frame matches the subject icons.20  
* **Licensing:** Most assets on Itch.io are affordable ($5-$15) or donation-based. Many are released under Creative Commons Zero (CC0), allowing for unrestricted commercial use without attribution, which is ideal for a student or startup project.21

**CraftPix** offers an alternative with more standardized bundles.20 Their "Engineering Icons" and "Industrial" packs are particularly useful for the technical Leaving Cert subjects.23 The advantage of CraftPix is the "Mega Bundle" model, where one purchase provides thousands of thematically consistent assets.

### **The "Convert" Strategy: Vector-to-Pixel Pipelines**

For specific subjects where no game asset exists (e.g., "Technical Graphics" or specific religious symbols), standard vector stock sites (Shutterstock, Vecteezy) become the primary source.11 However, placing a high-resolution vector next to a pixel art icon creates visual dissonance. A conversion pipeline is necessary.

* **Sourcing:** Search for "flat icon" rather than "pixel art" to get clean, bold shapes.25  
* **Conversion:** Tools like **Pixelator** or **FFfuel's pppixelate** allow for the automated conversion of SVG/Vector images into pixel art.26 These tools apply a grid overlay and use nearest-neighbor downsampling to "blockify" the image.  
* **Manual Touch-up:** Automated conversion often leaves "stray pixels" or "jaggies" (anti-aliasing artifacts). A brief pass in a pixel art editor (like Aseprite) is usually required to clean up the outline and ensure the color palette matches the rest of the application.28

### **The "Generate" Strategy: AI-Driven Asset Creation**

The emergence of Generative AI offers a third path, particularly for creating bespoke assets that match a specific style guide.

* **Recraft.ai:** This tool is specifically architected for vector and icon generation. Unlike general image generators, it allows for strict style control. Its "Pixel Art" preset is highly effective because it respects the grid structure, preventing the "blurry pixel" look common in other AI models.29  
* **PixelLab.ai:** This tool is designed for game developers and can generate sprite sheets. It is particularly useful if the application requires animated icons (e.g., a biology heart that beats, or an atom that spins).30  
* **Prompt Engineering:** To maintain consistency, prompts must specify the view (e.g., "isometric"), the background ("white background"), and the style ("16-bit", "bold outline"). For example: *"Pixel art icon of a woodworking plane, isometric view, 32-bit style, thick black outline, white background"*.31

## **Infrastructure and Asset Management Architecture**

Once assets are sourced, the challenge shifts to management and delivery. In a full-stack Next.js and Node.js application, the architecture for handling images has significant implications for performance, cost, and developer experience.

### **Database Design and Schema Strategy**

A fundamental principle of modern web development is that **binary assets should not be stored in the database**. Storing images as BLOBs (Binary Large OBjects) in MongoDB or PostgreSQL bloats the database, complicates backups, and degrades performance. Instead, the database should store *references* to the assets.  
For a curriculum-based application, the schema must accommodate both static system assets (the default icons) and potentially dynamic user assets (custom diagrams or profile pictures).  
**Proposed Schema (TypeScript/Prisma/Mongoose):**

TypeScript

model Subject {  
  id          String   @id @default(cuid())  
  name        String   // e.g., "Agricultural Science"  
  slug        String   @unique // e.g., "ag-science"  
  category    Category // Enum: SCIENCE, HUMANITIES, etc.  
    
  // Asset Reference Object  
  icon        SubjectIcon?  
}

model SubjectIcon {  
  id          String   @id @default(cuid())  
  subjectId   String   @unique  
  subject     Subject  @relation(fields: \[subjectId\], references: \[id\])  
    
  // Storage Provider Agnostic Reference  
  provider    String   // "uploadthing" | "cloudinary" | "local"  
  fileKey     String   // The unique ID in the storage bucket  
  publicUrl   String   // The accessible CDN URL  
    
  // Metadata for Frontend Optimization  
  width       Int  
  height      Int  
  blurDataUrl String?  // Base64 string for loading placeholders  
  altText     String   // Critical for accessibility  
}

This schema decouples the asset from the storage provider, allowing the application to switch between providers (e.g., moving from UploadThing to S3) without breaking the data model. It also explicitly stores dimensions and accessibility data, which are crucial for the frontend \<Image\> component to prevent Cumulative Layout Shift (CLS).32

### **Storage Provider Analysis: UploadThing vs. Cloudinary**

For a student or startup project using Next.js, two primary contenders emerge for asset hosting: **UploadThing** and **Cloudinary**. Each represents a different philosophy.

#### **UploadThing: The "Next.js Native" Approach**

UploadThing is a wrapper around AWS S3 designed specifically for the Next.js "App Router" architecture. It emphasizes **Type Safety** and **Developer Experience (DX)**.

* **Architecture:** It uses "FileRoutes" defined on the server. The frontend uses generated hooks (useUploadThing) that are fully typed. If the server expects an image of max 4MB, the frontend typescript definitions will reflect that constraint.33  
* **Workflow:**  
  1. Define a route iconUploader in server/uploadthing.ts.  
  2. Use \<UploadButton endpoint="iconUploader" /\> in the React component.  
  3. On upload complete, the server callback receives the file metadata, which can be immediately saved to the database.35  
* **Pros:** Extremely easy to set up, perfect integration with Next.js Server Actions, no complex "signed URL" logic needed. Generous free tier (2GB storage) which is sufficient for thousands of pixel art icons.36  
* **Cons:** Limited transformation capabilities. It stores the file exactly as uploaded. If you need to resize or convert formats, you must do it *before* upload or use a separate worker.

#### **Cloudinary: The Digital Asset Management (DAM) Approach**

Cloudinary is a comprehensive media management platform. It stores images but also provides an on-the-fly processing engine.

* **Architecture:** Images are accessed via URLs that contain transformation instructions.  
  * Example: https://res.cloudinary.com/demo/image/upload/w\_32,h\_32,c\_scale,e\_pixelate/my\_icon.png  
* **Pros:** Powerful transformations. You can upload a high-res photo and have Cloudinary automatically resize it, convert it to WebP, and even apply a "pixelate" effect via the URL parameters.37 It automatically optimizes delivery format (f\_auto) based on the user's browser.38  
* **Cons:** The API is vast and complex. The "Credit" system for the free tier is a hybrid of bandwidth, storage, and transformations, making it harder to predict costs.39 For simple pixel art that is already optimized, Cloudinary's powerful features may be overkill.

**Recommendation:** For a project focused on **pixel art**, where the visual integrity of the asset is paramount and art is likely pre-created (not transformed on the fly), **UploadThing** is the superior architectural choice. It offers a simpler mental model, strictly typed integration with Next.js, and sufficient storage for low-weight pixel art assets. Cloudinary's transformations (like compression) can sometimes inadvertently introduce blurring or artifacts to pixel art if not carefully configured, whereas UploadThing serves the exact binary you upload.

## **Backend Asset Processing Pipeline**

To maintain quality, a robust application should not blindly accept uploads. A processing pipeline using **Node.js** ensures that all assets conform to the strict requirements of the pixel art aesthetic before they are stored.

### **Image Processing with sharp**

The **sharp** library is the industry standard for high-performance image processing in Node.js.41 It is significantly faster than ImageMagick and binds to libvips.  
For pixel art, the processing pipeline must be configured specifically to avoid **anti-aliasing**. Standard resizing algorithms (Lanczos, Bicubic) smooth out edges, which destroys the crisp "blocky" look of pixel art.  
**The "Pixel-Perfect" Processing Routine:**

JavaScript

import sharp from 'sharp';

export async function processPixelArtUpload(fileBuffer: Buffer) {  
  const image \= sharp(fileBuffer);  
  const metadata \= await image.metadata();

  // 1\. Enforce Dimensions (e.g., standardized 32x32 or 64x64)  
  // CRITICAL: Use 'nearest' kernel to preserve hard edges  
  const resizedBuffer \= await image  
   .resize(64, 64, {  
      fit: 'contain',  
      background: { r: 0, g: 0, b: 0, alpha: 0 }, // Transparent background  
      kernel: sharp.kernel.nearest   
    })  
   .toBuffer();

  // 2\. Format Conversion  
  // Convert to WebP for web performance, but ensure 'lossless' is true.  
  // Lossy compression creates "mosquito noise" artifacts around pixel edges.  
  const optimizedBuffer \= await sharp(resizedBuffer)  
   .webp({   
      lossless: true,  
      quality: 100   
    })  
   .toBuffer();

  return optimizedBuffer;  
}

This pipeline ensures that regardless of what the user uploads, the system stores a standardized, optimized, and visually consistent asset.43

### **Automation and CI/CD**

In a professional workflow, asset validation can be moved to the CI/CD pipeline. Scripts can be written to scan the /public/assets directory during a build.

* **Linting:** Check if any PNG is larger than 50KB (pixel art should be tiny).  
* **Dimension Check:** Ensure all icons are square.  
* **Metadata Stripping:** Automatically run tools to remove EXIF data (camera info, geolocation) from assets to protect privacy and reduce file size.44

## **Frontend Engineering: Rendering Pixel Art**

The frontend implementation is where the strategy succeeds or fails. Modern browsers are designed to smooth out images and text for readability. This default behavior is hostile to pixel art.

### **CSS Rendering Physics**

To display pixel art crisply, you must override the browser's interpolation algorithm. By default, browsers use **bilinear** or **bicubic** interpolation when an image is scaled up. This blurs the pixels. We need **Nearest Neighbor** interpolation.  
**The Universal CSS Class for Pixel Art:**

CSS

.pixel-art {  
  /\* The standard property \*/  
  image-rendering: pixelated;   
    
  /\* Firefox specific \*/  
  image-rendering: \-moz-crisp-edges;   
    
  /\* Safari/Webkit specific \*/  
  image-rendering: \-webkit-optimize-contrast;   
    
  /\* Generic fallback \*/  
  image-rendering: crisp-edges;  
}

This CSS tells the rendering engine: "When you stretch this image, do not blend the pixels. Just repeat them.".45

### **The Next.js \<Image\> Component Strategy**

The Next.js \<Image\> component is a powerful tool for performance, but its defaults are tuned for photography.

* **The Blur-Up Problem:** Next.js generates a low-res blurry placeholder for images while they load. For pixel art, a blurry placeholder looks like a rendering error. It is often better to disable the blur (placeholder="empty") or use a solid color placeholder for pixel art icons.  
* **The Optimization Problem:** If unoptimized={false} (default), Next.js will pass the image through its own optimization layer (using Vercel's image optimization). This might re-compress the image using lossy algorithms. For critical pixel art UI elements, using unoptimized={true} (serving the file exactly as stored) ensures no artifacts are introduced, provided the backend pipeline (using sharp) has already done the optimization.48

**Recommended Component Implementation:**

TypeScript

import Image from 'next/image';

interface PixelIconProps {  
  src: string;  
  alt: string;  
  size?: number; // Logical size (e.g., 32px)  
}

export const PixelIcon \= ({ src, alt, size \= 32 }: PixelIconProps) \=\> {  
  return (  
    \<div style={{ position: 'relative', width: size, height: size }}\>  
      \<Image  
        src={src}  
        alt={alt}  
        fill  
        sizes={\`${size}px\`}  
        className="pixel-art" // Applies the CSS described above  
        style={{  
          objectFit: 'contain',  
        }}  
        // Disable internal optimization to prevent re-compression artifacts  
        unoptimized={true}   
      /\>  
    \</div\>  
  );  
};

### **Layout Stability and Performance**

Web Vitals, specifically **Cumulative Layout Shift (CLS)**, are critical for educational apps where students are reading text. Images loading late and shifting the text can be frustrating.

* **Explicit Dimensions:** Always provide width and height (or aspect ratio) to the container. Even if the image loads late, the space is reserved.  
* **Caching:** Pixel art icons are "long-lived" static assets. The server should serve them with aggressive Cache-Control headers (e.g., public, max-age=31536000, immutable). This ensures that once a student downloads the "Math" icon, their browser never asks for it again for a year.50

## **Operational Workflows and Accessibility**

### **Accessibility in Pixel Art**

Educational applications must be accessible. Pixel art, while stylized, must still be interpretable by screen readers.

* **Alt Text Strategy:** Alt text should be descriptive but distinct from the UI text. If the icon is next to the word "Mathematics," the alt text should not be "Mathematics" (redundant). It should be "Pixel art icon of a set square and compass" or, if purely decorative, an empty string (alt="").41  
* **Contrast:** Pixel art often uses limited palettes. Ensure the contrast ratio between the icon's details and its background meets WCAG AA standards (4.5:1). A "bold outline" style (common in game assets) is excellent for this, as the black border provides high contrast against any background color.51

### **Managing the "Style Matrix"**

A common pitfall is the "resolution clash." This occurs when a 16x16 icon is placed next to a 32x32 icon, and they are both scaled to the same physical size on screen. The 16x16 icon will have "pixels" that look twice as big as the 32x32 icon.

* **The Rule of 1X:** Decide on a base resolution for the project (e.g., 1 logical pixel \= 2 physical pixels). All assets must adhere to this.  
* **Normalization:** If you source a 16x16 asset but your standard is 32x32, you must upscale the 16x16 asset by exactly 200% (using nearest neighbor) *before* bringing it into the app. This ensures that the "virtual pixel size" appears consistent across the entire interface.52

## **Conclusion**

The successful integration of pixel art into an educational full-stack application is an exercise in precision. It requires looking beyond standard stock libraries to the rich ecosystem of game development assets, particularly for niche Irish subjects where cultural nuance is essential. It demands a disciplined backend architecture that favors type safety and raw file integrity (UploadThing) over complex, potentially destructive on-the-fly transformations. Finally, it requires a frontend implementation that understands the unique physics of rendering blocky graphics on high-resolution screens.  
By adhering to the "Nearest Neighbor" scaling strategy, automating asset sanitization with sharp, and enforcing strict schema definitions in the database, developers can create a learning environment that is not only robust and performant but also taps into the engaging, gamified visual language that resonates with modern students. The result is a platform where the interface itself encourages interaction, turning the "chore" of study into a visually cohesive journey of progression.

#### **Works cited**

1. Ireland Culture Symbols Icons Set Pixel Stock Vector (Royalty Free) 373883650, accessed December 5, 2025, [https://www.shutterstock.com/image-vector/ireland-culture-symbols-icons-set-pixel-373883650](https://www.shutterstock.com/image-vector/ireland-culture-symbols-icons-set-pixel-373883650)  
2. Ireland Culture Symbols Icons Set Pixel Stock Vector (Royalty Free) 373883644, accessed December 5, 2025, [https://www.shutterstock.com/image-vector/ireland-culture-symbols-icons-set-pixel-373883644](https://www.shutterstock.com/image-vector/ireland-culture-symbols-icons-set-pixel-373883644)  
3. 219 Speaking Irish Stock Vectors and Vector Art | Shutterstock, accessed December 5, 2025, [https://www.shutterstock.com/search/speaking-irish?image\_type=vector](https://www.shutterstock.com/search/speaking-irish?image_type=vector)  
4. Celtic Knot Pixel Art by mortykins on DeviantArt, accessed December 5, 2025, [https://www.deviantart.com/mortykins/art/Celtic-Knot-Pixel-Art-260175961](https://www.deviantart.com/mortykins/art/Celtic-Knot-Pixel-Art-260175961)  
5. I'm working on pixel Celtic knots : r/PixelArt \- Reddit, accessed December 5, 2025, [https://www.reddit.com/r/PixelArt/comments/aim55g/im\_working\_on\_pixel\_celtic\_knots/](https://www.reddit.com/r/PixelArt/comments/aim55g/im_working_on_pixel_celtic_knots/)  
6. Free Agriculture Icons, Symbols & Images \- BioRender.com, accessed December 5, 2025, [https://www.biorender.com/categories/agriculture](https://www.biorender.com/categories/agriculture)  
7. Agriculture science icons \- Stock-illustrations \- iStock, accessed December 5, 2025, [https://www.istockphoto.com/illustrations/agriculture-science](https://www.istockphoto.com/illustrations/agriculture-science)  
8. Cute Fantasy RPG \- 16x16 top down pixel art asset pack by Kenmi \- Itch.io, accessed December 5, 2025, [https://kenmi-art.itch.io/cute-fantasy-rpg](https://kenmi-art.itch.io/cute-fantasy-rpg)  
9. Agriculture Science Icons stock illustrations \- iStock, accessed December 5, 2025, [https://www.istockphoto.com/illustrations/agriculture-science-icons](https://www.istockphoto.com/illustrations/agriculture-science-icons)  
10. Construction Tools Pixel Icons stock illustrations \- iStock, accessed December 5, 2025, [https://www.istockphoto.com/illustrations/construction-tools-pixel-icons](https://www.istockphoto.com/illustrations/construction-tools-pixel-icons)  
11. Pixel Art House Icon Set. Pixelated House, Symbol Of Home Or Building. Real Estate, Shelter Or Property. Isolated Illustration 68350291 Vector Art at Vecteezy, accessed December 5, 2025, [https://www.vecteezy.com/vector-art/68350291-pixel-art-house-icon-set-pixelated-house-symbol-of-home-or-building-real-estate-shelter-or-property-isolated-illustration](https://www.vecteezy.com/vector-art/68350291-pixel-art-house-icon-set-pixelated-house-symbol-of-home-or-building-real-estate-shelter-or-property-isolated-illustration)  
12. 6,497 Engineering Tools Icon High Res Illustrations \- Getty Images, accessed December 5, 2025, [https://www.gettyimages.in/illustrations/engineering-tools-icon](https://www.gettyimages.in/illustrations/engineering-tools-icon)  
13. Hammer Pixel Icon vectors \- Shutterstock, accessed December 5, 2025, [https://www.shutterstock.com/search/hammer-pixel-icon?image\_type=vector](https://www.shutterstock.com/search/hammer-pixel-icon?image_type=vector)  
14. 56+ Thousand Pixel Food Icon Royalty-Free Images, Stock Photos & Pictures | Shutterstock, accessed December 5, 2025, [https://www.shutterstock.com/search/pixel-food-icon](https://www.shutterstock.com/search/pixel-food-icon)  
15. Food Pixelated Icons 32×32 Pixel Art \- CraftPix.net, accessed December 5, 2025, [https://craftpix.net/product/food-pixelated-icons-32x32-pixel-art/](https://craftpix.net/product/food-pixelated-icons-32x32-pixel-art/)  
16. Pixel Art Food stock illustrations \- iStock, accessed December 5, 2025, [https://www.istockphoto.com/illustrations/pixel-art-food](https://www.istockphoto.com/illustrations/pixel-art-food)  
17. Pixel School Icon Set Illustrations & Vectors \- Dreamstime.com, accessed December 5, 2025, [https://www.dreamstime.com/illustration/pixel-school-icon-set.html](https://www.dreamstime.com/illustration/pixel-school-icon-set.html)  
18. Set of pixel art school subject icons Vector Image \- VectorStock, accessed December 5, 2025, [https://www.vectorstock.com/royalty-free-vector/set-of-pixel-art-school-subject-icons-vector-58611554](https://www.vectorstock.com/royalty-free-vector/set-of-pixel-art-school-subject-icons-vector-58611554)  
19. Pixel Art App Icons by Reff Pixels, accessed December 5, 2025, [https://reffpixels.itch.io/appicons](https://reffpixels.itch.io/appicons)  
20. CraftPix.net: 2D Game Assets Store & Free, accessed December 5, 2025, [https://craftpix.net/](https://craftpix.net/)  
21. Heys guys, here's a 2d classroom asset pack with \+3K sprites, it's free, clickable link below the first image or https://styloo.itch.io/2dclassroom : r/gamemaker \- Reddit, accessed December 5, 2025, [https://www.reddit.com/r/gamemaker/comments/1f5v3fy/heys\_guys\_heres\_a\_2d\_classroom\_asset\_pack\_with\_3k/](https://www.reddit.com/r/gamemaker/comments/1f5v3fy/heys_guys_heres_a_2d_classroom_asset_pack_with_3k/)  
22. Free asset pack: Pixelart medieval city builder : r/gamedev \- Reddit, accessed December 5, 2025, [https://www.reddit.com/r/gamedev/comments/mfa6f3/free\_asset\_pack\_pixelart\_medieval\_city\_builder/](https://www.reddit.com/r/gamedev/comments/mfa6f3/free_asset_pack_pixelart_medieval_city_builder/)  
23. Engineering Icons 32×32 Pixel Art \- CraftPix.net, accessed December 5, 2025, [https://craftpix.net/product/engineering-icons-32x32-pixel-art/](https://craftpix.net/product/engineering-icons-32x32-pixel-art/)  
24. Education Icons PNG Images | 240000+ Vector Icon Packs | Free Download On Pngtree, accessed December 5, 2025, [https://pngtree.com/so/education-icons](https://pngtree.com/so/education-icons)  
25. Open Book Pixel Art Icon Set Stock Vector (Royalty Free) 2675612387 \- Shutterstock, accessed December 5, 2025, [https://www.shutterstock.com/image-vector/open-book-pixel-art-icon-set-2675612387](https://www.shutterstock.com/image-vector/open-book-pixel-art-icon-set-2675612387)  
26. pppixelate: SVG pixel art pattern maker | fffuel, accessed December 5, 2025, [https://www.fffuel.co/pppixelate/](https://www.fffuel.co/pppixelate/)  
27. Pixel Art Converter \- Folge, accessed December 5, 2025, [https://folge.me/tools/pixel-art-converter](https://folge.me/tools/pixel-art-converter)  
28. PIXEL ART TUTORIAL: BASICS \- Derek Yu, accessed December 5, 2025, [https://www.derekyu.com/makegames/pixelart.html](https://www.derekyu.com/makegames/pixelart.html)  
29. Free AI Image Vectorizer: Convert PNG & JPG to SVG \- Recraft | AI, accessed December 5, 2025, [https://www.recraft.ai/ai-image-vectorizer](https://www.recraft.ai/ai-image-vectorizer)  
30. PixelLab \- AI Generator for Pixel Art Game Assets, accessed December 5, 2025, [https://www.pixellab.ai/](https://www.pixellab.ai/)  
31. Free AI Pixel Art Generator | Fast & Easy to Use \- getimg.ai, accessed December 5, 2025, [https://getimg.ai/use-cases/ai-pixel-art-generator](https://getimg.ai/use-cases/ai-pixel-art-generator)  
32. Optimizing Image Performance in Next.js: Best Practices for Fast, Visual Web Apps, accessed December 5, 2025, [https://geekyants.com/blog/optimizing-image-performance-in-nextjs-best-practices-for-fast-visual-web-apps](https://geekyants.com/blog/optimizing-image-performance-in-nextjs-best-practices-for-fast-visual-web-apps)  
33. Uploading Files \- UploadThing Docs, accessed December 5, 2025, [https://docs.uploadthing.com/uploading-files](https://docs.uploadthing.com/uploading-files)  
34. File Routes \- UploadThing Docs, accessed December 5, 2025, [https://docs.uploadthing.com/file-routes](https://docs.uploadthing.com/file-routes)  
35. uploadthing, accessed December 5, 2025, [https://uploadthing-beta.vercel.app/](https://uploadthing-beta.vercel.app/)  
36. uploadthing, accessed December 5, 2025, [https://uploadthing.com/](https://uploadthing.com/)  
37. Resize, crop, rotation | Uploadcare docs, accessed December 5, 2025, [https://uploadcare.com/docs/transformations/image/resize-crop/](https://uploadcare.com/docs/transformations/image/resize-crop/)  
38. 7 Free Digital Asset Management Software (not Open-Source) \- ImageKit, accessed December 5, 2025, [https://imagekit.io/blog/free-digital-asset-management-software-that-are-not-open-source/](https://imagekit.io/blog/free-digital-asset-management-software-that-are-not-open-source/)  
39. Cloudinary Pricing Tiers & Costs (Updated for 2025\) \- The Digital Project Manager, accessed December 5, 2025, [https://thedigitalprojectmanager.com/tools/cloudinary-pricing/](https://thedigitalprojectmanager.com/tools/cloudinary-pricing/)  
40. Compare Plans | Cloudinary, accessed December 5, 2025, [https://cloudinary.com/pricing/compare-plans](https://cloudinary.com/pricing/compare-plans)  
41. Components: Image \- Next.js, accessed December 5, 2025, [https://nextjs.org/docs/pages/api-reference/components/image](https://nextjs.org/docs/pages/api-reference/components/image)  
42. High performance Node.js image processing | sharp, accessed December 5, 2025, [https://sharp.pixelplumbing.com/](https://sharp.pixelplumbing.com/)  
43. A Deep Dive into Advanced Image Optimization Techniques used by Next.js \- Medium, accessed December 5, 2025, [https://medium.com/@aadityagupta400/unlocking-the-power-of-next-js-a-deep-dive-into-advanced-image-optimization-techniques-b1740b8d6a5f](https://medium.com/@aadityagupta400/unlocking-the-power-of-next-js-a-deep-dive-into-advanced-image-optimization-techniques-b1740b8d6a5f)  
44. Optimizing Images in Next.js: Beyond the Image Component | by Narayanan Sundaram, accessed December 5, 2025, [https://medium.com/@narayanansundar02/optimizing-images-in-next-js-beyond-the-image-component-b1353236408b](https://medium.com/@narayanansundar02/optimizing-images-in-next-js-beyond-the-image-component-b1353236408b)  
45. Crisp pixel art look with image-rendering \- Game development \- MDN Web Docs, accessed December 5, 2025, [https://developer.mozilla.org/en-US/docs/Games/Techniques/Crisp\_pixel\_art\_look](https://developer.mozilla.org/en-US/docs/Games/Techniques/Crisp_pixel_art_look)  
46. image-rendering \- CSS \- MDN Web Docs, accessed December 5, 2025, [https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/image-rendering](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/image-rendering)  
47. CSS image-rendering: pixelated. Scale Pixel Art Without Blur \- TheoSoti, accessed December 5, 2025, [https://theosoti.com/short/crispy-images/](https://theosoti.com/short/crispy-images/)  
48. Image Optimization \- Next.js, accessed December 5, 2025, [https://nextjs.org/docs/14/app/building-your-application/optimizing/images](https://nextjs.org/docs/14/app/building-your-application/optimizing/images)  
49. Image optimization for Next.js applications \- Uploadcare, accessed December 5, 2025, [https://uploadcare.com/blog/image-optimization-in-nextjs/](https://uploadcare.com/blog/image-optimization-in-nextjs/)  
50. How to Optimize Image Caching in Next.js for Blazing Fast Loading Times \- DEV Community, accessed December 5, 2025, [https://dev.to/melvinprince/how-to-optimize-image-caching-in-nextjs-for-blazing-fast-loading-times-3k8l](https://dev.to/melvinprince/how-to-optimize-image-caching-in-nextjs-for-blazing-fast-loading-times-3k8l)  
51. Graphics \- Keeping a consistent Pixel Art Style \- GameMaker Community, accessed December 5, 2025, [https://forum.gamemaker.io/index.php?threads/keeping-a-consistent-pixel-art-style.73243/](https://forum.gamemaker.io/index.php?threads/keeping-a-consistent-pixel-art-style.73243/)  
52. Consistency \- Saint11, accessed December 5, 2025, [https://saint11.art/blog/consistency/](https://saint11.art/blog/consistency/)

---

## geoai-Geospatial Workflow & Particle Effects(1)

*Source: `docs/bunchloch/teanga/geoai-Geospatial Workflow & Particle Effects(1).md` (3803 words, 341 lines)*

# **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP and WebGPU Rendering for Meteorological Particle Simulation**

## **Executive Summary**

The geospatial data science landscape is currently undergoing a structural revolution, transitioning from file-based, desktop-centric workflows to cloud-native, serverless architectures that prioritize zero-copy data transport and hardware-accelerated visualization. This report presents a comprehensive technical blueprint for a modern geospatial workflow, explicitly designed to ingest, process, and visualize high-velocity meteorological data from the **UK Met Office** and **GeoHive (Ireland)**. The proposed architecture leverages the **opengeos** and **giswqs** ecosystem to integrate **DuckDB**, **MotherDuck**, **PlanetScale**, **GeoParquet**, **Lonboard**, **Ibis**, and **Marimo**. The primary technical objective is to replicate "game-like" visual fidelity—specifically particle-based wind flow simulations—within a browser-based analytical environment.  
A central component of this analysis is a rigorous comparative evaluation against **SpacetimeDB**, an emerging "database-as-backend" technology. While SpacetimeDB offers a unified approach to state management ideal for multiplayer gaming logic, this report argues that the **DuckDB-GeoArrow-Lonboard** pipeline provides superior performance for scientific visualization. This advantage stems from its optimization for vectorized memory transport and client-side WebGPU compute, which decouples the visual simulation from the bandwidth constraints of server-authoritative state synchronization.  
This document serves as a foundational reference for data engineers and geospatial architects seeking to implement high-performance dashboards that bridge the gap between traditional GIS precision and modern video game graphics.

## ---

**1\. Introduction: The Convergence of GIS and Real-Time Graphics**

### **1.1 The Shift to Cloud-Native Geospatial**

Historically, Geographic Information Systems (GIS) have been characterized by heavy client-side software, monolithic spatial databases (like PostGIS), and intermediate file formats (Shapefiles, GeoJSON) that require significant serialization overhead. However, the emergence of the "Modern Data Stack" has introduced tools that are modular, ephemeral, and incredibly fast. This shift is typified by the "Cloud-Native Geospatial" paradigm, which emphasizes accessing data directly from object storage (S3) using range requests, rather than downloading entire datasets.  
The **opengeos** initiative, championed by researchers and developers such as Qiusheng Wu (giswqs), represents the vanguard of this movement.1 By prioritizing open-source tools that leverage binary formats and efficient memory management, this ecosystem allows for the processing of datasets—such as global weather models—that were previously the domain of supercomputers or dedicated workstations.

### **1.2 The Challenge of Game-Like Fidelity**

Users increasingly demand visualization interfaces that match the fluidity and responsiveness of video games. In the context of meteorology, this means moving beyond static isobars or "hedgehog" arrow plots to dynamic, animated particle systems that visualize wind flow as a continuous fluid medium. Achieving this requires a rendering pipeline that can handle hundreds of thousands of moving entities at 60 frames per second (FPS).  
This requirement creates a technical tension between **Analytical Precision** (the domain of SQL databases) and **Visual Performance** (the domain of Game Engines/GPUs). The workflow proposed herein seeks to resolve this tension by integrating a high-performance analytical engine (**DuckDB**) with a WebGPU-accelerated visualization library (**Lonboard**), mediated by a zero-copy transport layer (**GeoArrow**).

### **1.3 Scope of Analysis**

This report focuses on two primary meteorological datasets:

1. **Met Office (UK):** Global Spot Data and Atmospheric Model outputs.  
2. **GeoHive / Met Éireann (Ireland):** The HARMONIE-AROME high-resolution numerical weather prediction (NWP) model.

The analysis will detail the ingestion of these datasets, their normalization via **Ibis**, state management via **PlanetScale**, and final rendering in **Marimo** notebooks. It will then contrast this approach with **SpacetimeDB**, evaluating the trade-offs between a modular OLAP-centric stack and a unified, reducer-based simulation backend.

## ---

**2\. The Modern Geospatial Stack: Component Architecture**

The proposed architecture is not a monolithic application but a composable pipeline. Each tool is selected for its ability to handle specific types of complexity: computational, semantic, or visual.

### **2.1 The Computational Core: DuckDB and MotherDuck**

#### **2.1.1 DuckDB: The In-Process Analytical Engine**

**DuckDB** serves as the primary computational engine for this workflow. Often described as "SQLite for analytics," DuckDB is an embedded SQL OLAP database designed for vectorized query execution.3 Unlike row-oriented databases (PostgreSQL, MySQL), DuckDB organizes data by columns, which allows for highly efficient compression and CPU cache utilization—critical factors when processing the dense float arrays found in meteorological GRIB2 files.  
The pivotal feature for this workflow is the **DuckDB Spatial Extension**. This extension bundles the **GDAL** (Geospatial Data Abstraction Library) drivers, enabling DuckDB to function as a virtual file system. Through functions like ST\_Read, DuckDB can mount remote GRIB2 files (hosted on HTTP servers or S3 buckets) and query them directly as if they were local tables.4 This capability is fundamental to the "Cloud-Native" approach, as it eliminates the need for an intermediate ETL (Extract, Transform, Load) step to ingest massive weather model runs into a database before querying.

#### **2.1.2 MotherDuck: Hybrid Execution Strategy**

**MotherDuck** extends DuckDB into the cloud, enabling a serverless, collaborative data warehousing model. In the context of this workflow, MotherDuck solves the "Data Gravity" problem.

* **Historical Archive:** While local DuckDB instances are excellent for processing the "latest" forecast (hundreds of megabytes), analyzing historical trends (e.g., "Compare today's Storm Kathleen with 2014's Storm Darwin") involves terabytes of data. MotherDuck hosts this historical archive.  
* **Hybrid Querying:** The duckdb client can execute queries that join local data (the current forecast GRIB file) with remote data (historical climatology in MotherDuck). MotherDuck’s engine intelligently separates the query plan, executing the heavy aggregations in the cloud and returning only the results to the local Marimo client.5

### **2.2 The Transactional State Layer: PlanetScale**

While DuckDB handles immutable analytical data, an interactive application requires a mutable state: user preferences, saved viewports, annotation layers, and session management. **PlanetScale** fulfills this role.

#### **2.2.1 Architecture and Integration**

PlanetScale is built on **Vitess**, a database clustering system for horizontal scaling of MySQL (and now PostgreSQL). Recently, PlanetScale introduced support for PostgreSQL, including the **pg\_duckdb** extension.6 This integration is architecturally significant.

* **The "Lakehouse" Pattern:** By installing pg\_duckdb within PlanetScale, the transactional database acts as a gateway to the analytical warehouse. A user application can send a standard SQL query to PlanetScale to retrieve a user's saved location, and in the same transaction, join that location data with wind vector data residing in MotherDuck.7  
* **Performance:** PlanetScale’s architecture is optimized for high-concurrency, low-latency lookups (OLTP). This ensures that the application interface remains snappy (e.g., logging in, loading lists of saved maps) even while heavy analytical queries are processing in the background.

### **2.3 The Semantic Layer: Ibis**

One of the persistent challenges in geospatial engineering is "SQL Dialect Fatigue." Syntax varies between PostGIS, DuckDB Spatial, and BigQuery GIS. **Ibis** addresses this by providing a unified, Pythonic dataframe API that compiles to SQL.8

* **Expression Trees:** Unlike Pandas, which executes operations immediately (eager evaluation), Ibis builds a lazy expression tree. This allows the framework to optimize the query before execution.  
* **Engine Agnosticism:** By writing the geospatial transformation logic (e.g., table.filter(st\_intersects(...))) in Ibis, the workflow becomes decoupled from the backend. The same Python code can drive a local DuckDB instance during development and a MotherDuck or PlanetScale backend in production, simply by switching the connection object.9

### **2.4 The Transport Layer: GeoParquet and GeoArrow**

The bottleneck in most web-based GIS is serialization. Converting binary database rows into textual GeoJSON (a JSON-based format) requires expensive parsing and significantly inflates file size.

* **GeoParquet:** This format extends Apache Parquet to support geospatial types. It is used for the *persistent storage* of processed weather tiles. Its columnar compression (Snappy, Zstd) is highly effective for repetitive grid coordinates.10  
* **GeoArrow:** This is the *in-memory* standard. When DuckDB executes a query, it can output the result as an Arrow table—a contiguous block of memory. This binary buffer can be passed directly to Python and then to the JavaScript/GPU layer without serialization. This "Zero-Copy" transfer is the technological breakthrough that enables visualizing millions of particles in the browser.11

### **2.5 The Visualization Layer: Lonboard and Marimo**

**Lonboard** is a bridge library connecting Python data (GeoArrow) to **Deck.gl** (JavaScript/WebGL). **Marimo** is a next-generation reactive notebook environment.

* **Reactive Execution:** Unlike Jupyter, which maintains a hidden global state that can lead to out-of-order execution errors, Marimo treats the notebook as a Directed Acyclic Graph (DAG).13 If a user moves a time slider, Marimo automatically re-executes only the dependent cells (e.g., the DuckDB query and the map render), ensuring a responsive, glitch-free dashboard.  
* **WebGPU Context:** Marimo supports **AnyWidget**, a protocol for embedding modern JavaScript widgets. This allows the workflow to instantiate custom Deck.gl layers that utilize WebGPU compute shaders, bypassing the limitations of the standard DOM.14

## ---

**3\. Data Engineering: Ingesting UK and Irish Meteorological Data**

To visualize wind flow, the system must ingest **Vector Fields**: grids where every point contains a $U$ (Zonal/East-West) and $V$ (Meridional/North-South) component.

### **3.1 UK Met Office Data Structure**

The UK Met Office exposes data via the **Weather DataHub**. For high-fidelity visualisations, two primary products are relevant:

1. **Global Spot Data:** Provides point-based forecasts. While useful for validation, it lacks the spatial continuity required for particle simulation.15  
2. **Atmospheric Models (UKV / Global):** These provide gridded fields. The data is delivered in **GRIB2** format.

#### **3.1.1 GRIB2 Structure**

A GRIB2 (General Regularly-distributed Information in Binary form) file is a container format composed of multiple "messages." Each message corresponds to a specific variable (e.g., Wind Speed) at a specific vertical level (e.g., 10m above ground) and forecast step.

* **Section 0:** Indicator Section (File type).  
* **Section 3:** Grid Definition Template (Defining the geometry—Lat/Lon vs Rotated Pole).  
* **Section 4:** Product Definition Template (Parameter category: Momentum; Parameter number: U-component).  
* **Section 5:** Data Representation Template (Packing method, typically JPEG2000 or CCSDS).  
* **Section 7:** Data Template (The actual binary payload).

**Ingestion Strategy:** DuckDB's ST\_Read utilizes the GDAL GRIB driver. To extract the wind vectors, the query must filter by the GRIB "Element" or "Band." Typically, Band 1 is $U$ and Band 2 is $V$ in combined files, but often they are distributed as separate files.

### **3.2 Met Éireann (GeoHive) Data Structure**

Met Éireann operates the **HARMONIE-AROME** model, a Limited Area Model (LAM) focused on Ireland.

* **Resolution:** 2.5km horizontal grid.  
* **Update Cycle:** 54-hour forecasts produced every 3 hours (00Z, 03Z, etc.).  
* **Systems:** Historically **IREPS** (Irish Regional Ensemble Prediction System), recently upgraded to **DINI-EPS** (Denmark-Ireland-Netherlands-Iceland) collaboration.16

#### **3.2.1 Access via Open Data**

While GeoHive acts as the geospatial portal, the raw GRIB2 files are hosted on Met Éireann's Open Data HTTP servers (https://opendata.met.ie).

* **File Naming Convention:** Harmonie\_IRE\_2.5km\_wind\_YYYYMMDDHH.grib2.  
* **Projection:** HARMONIE uses a **Lambert Conformal Conic** projection (to minimize distortion over Ireland) or a Rotated Lat/Lon grid. This contrasts with the Global Met Office models which often use WGS84 (EPSG:4326).

Ingestion Challenge: Particle visualization libraries (Deck.gl) generally expect Web Mercator or WGS84 coordinates.  
Solution: The DuckDB ingestion query must perform an on-the-fly coordinate transformation (ST\_Transform) to reproject the HARMONIE vectors from Lambert Conformal to WGS84.

### **3.3 Harmonization via Ibis**

The power of Ibis lies in its ability to abstract these differences. We can define a "Virtual Schema" for wind data and map both sources to it.

| Standard Field | Met Office Source | Met Éireann Source |
| :---- | :---- | :---- |
| timestamp | forecast\_reference\_time \+ step | validityTime |
| geometry | ST\_Point(lon, lat) | ST\_Transform(ST\_Point(x,y), 2157, 4326\) |
| u\_vector | band\_1 (Param 2, Cat 2\) | u-component |
| v\_vector | band\_2 (Param 3, Cat 2\) | v-component |

**Table 1:** Schema Mapping for Wind Vector Normalization.

Python

\# Conceptual Ibis Normalization Logic  
import ibis

def normalize\_wind(table, source\_type):  
    if source\_type \== 'met\_office':  
        return table.select(  
            time='forecast\_time',  
            u=table\['wind\_u\_10m'\],  
            v=table\['wind\_v\_10m'\],  
            geometry=ibis.geo.point(table.lon, table.lat)  
        )  
    elif source\_type \== 'met\_eireann':  
        \# Apply projection transform if needed via expression  
        return table.select(  
            time='validity\_time',  
            u=table\['u\_10m'\],  
            v=table\['v\_10m'\],  
            geometry=ibis.geo.transform(table.geom, 4326\)  
        )

## ---

**4\. Visualization Mechanics: Creating "Game-Like" Particle Effects**

The requirement for "game-like" effects implies a level of interactivity and visual smoothness (60 FPS) that static map tiles cannot provide. In fluid dynamics visualization, this is achieved through **Lagrangian Particle Tracking**.

### **4.1 The Physics of Flow**

There are two ways to represent fluid flow:

1. **Eulerian:** Inspecting the fluid properties (velocity, pressure) at fixed points in space (the Grid). This is what the GRIB2 file contains.  
2. **Lagrangian:** Following specific particles as they move through space and time. This is what the visualization renders.

The Simulation Loop:  
To visualize the Eulerian data (grid) in a Lagrangian way (particles), the rendering engine must perform Numerical Integration.

$$P\_{t+1} \= P\_t \+ \\vec{V}(P\_t) \\cdot \\Delta t$$

Where:

* $P\_t$ is the particle position at time $t$.  
* $\\vec{V}(P\_t)$ is the velocity vector sampled from the grid at position $P\_t$.  
* $\\Delta t$ is the time step.

### **4.2 WebGPU and Deck.gl Implementation**

Simulating 100,000+ particles using this equation on a CPU is too slow for JavaScript. The solution uses **WebGPU** (or WebGL2 Transform Feedback) to perform this integration on the Graphics Processing Unit.

#### **4.2.1 The Texture Strategy**

Instead of passing 100,000 velocity values to the GPU every frame, we pass the "Vector Field" as a **Texture** (an image).

* **Red Channel:** Encodes the U-component (scaled to 0-255).  
* **Green Channel:** Encodes the V-component.  
* **Blue Channel:** (Optional) Encodes temperature or magnitude.

DuckDB reads the GRIB2 data and exports it not as a list of points, but as a binary image buffer (PNG or raw bytes). This buffer is uploaded to the GPU memory once.

#### **4.2.2 The Compute Shader**

A WebGPU Compute Shader runs for every particle instance:

1. **Sample:** It reads the particle's current coordinate $(x, y)$.  
2. **Lookup:** It samples the Velocity Texture at $(x, y)$ to get $\\vec{V}$.  
3. **Integrate:** It calculates the new position.  
4. **Boundary Check:** If the particle moves off-screen or exceeds a "lifetime" counter, it resets to a random position.

### **4.3 Extending Lonboard with AnyWidget**

**Lonboard** natively supports ScatterplotLayer and PathLayer, which are insufficient for this simulation loop. We must extend it using **AnyWidget**.  
**AnyWidget** allows us to write a custom JavaScript module that wraps a specialized Deck.gl layer (like ParticleLayer from the weatherlayers or deck.gl-particle community packages) and expose it to Python.17

* **Python Side (WindWidget.py):** Defines a class inheriting from anywidget.AnyWidget. It has Traitlets for u\_texture, v\_texture, particle\_count, and speed\_factor.  
* **JavaScript Side (widget.js):** Listens for changes to these traits. When the u\_texture changes (because the user moved the time slider in Marimo), the JS updates the Deck.gl layer's texture uniform.

Synchronization:  
Because Marimo uses a reactive execution graph, connecting the Time Slider to the DuckDB query automatically triggers the chain:  
Slider Move \-\> DuckDB Query \-\> Ibis Processing \-\> GeoArrow/Image Output \-\> AnyWidget Update \-\> GPU Render.  
This creates a seamless, "game-like" experience where the wind field shifts smoothly as the user scrubs through time.

## ---

**5\. Comparative Architecture: SpacetimeDB**

To fully evaluate the proposed stack, we must compare it against **SpacetimeDB**, a technology that fundamentally rethinks the relationship between the database and the application.

### **5.1 SpacetimeDB: The Database IS the Server**

Traditional architectures separate the Database (Postgres) from the Backend Server (Node.js/Python). **SpacetimeDB** unifies them. It is a relational database that executes application logic (written in Rust or C\#) *inside* the database transaction loop.18

* **Reducers:** Instead of API endpoints, you define "Reducers"—functions that mutate the database state.  
* **Tick Rate:** The database has a concept of "time" and can run scheduled reducers (e.g., update\_physics()) every tick.  
* **Client Sync:** Clients subscribe to tables. When a reducer changes a row, the database automatically pushes the update to the client SDK.

### **5.2 The Particle Effect Challenge in SpacetimeDB**

How would one implement the "Wind Particle" simulation in SpacetimeDB?

#### **5.2.1 Approach A: Server-Authoritative Particles**

In this model, every particle is a row in a Particles table: (id, x, y, velocity).

* A server-side reducer iterates through the table 60 times a second, updating $x$ and $y$ based on the wind field.  
* **Failure Mode:** This requires broadcasting the position of 100,000 particles to every connected client 60 times a second. The bandwidth requirement (approx 100MB/s) is impossible for web clients. SpacetimeDB is optimized for *game state* (inventory, player health, position of 50 players), not *dense simulation data*.20

#### **5.2.2 Approach B: Client-Side Simulation (The Hybrid)**

In this model, SpacetimeDB stores only the **Wind Field** (the grid data).

* The client connects and downloads the Wind Field.  
* The client performs the particle simulation locally (using Unity/C\# or JS).  
* **Comparison:** In this scenario, SpacetimeDB acts merely as a data distribution API. However, it lacks the specialized compression of GeoParquet or the range-request capabilities of DuckDB. It would require parsing the GRIB2 file into SpacetimeDB tables (inserting millions of rows), which is far less efficient than DuckDB's zero-copy ST\_Read.

### **5.3 Comparison Matrix**

| Feature | OpenGEOS Stack (DuckDB/Lonboard) | SpacetimeDB |
| :---- | :---- | :---- |
| **Primary Philosophy** | **Data Gravity:** Move compute to the data (SQL/WebGPU). | **Unified State:** Logic lives with the data (Reducers). |
| **Data Ingestion** | **Native:** Reads GRIB2/Parquet directly. Zero-ETL. | **Custom:** Requires writing parsers to import data into DB tables. |
| **Particle Simulation** | **Client-Side (GPU):** Simulates 1M+ particles at 60 FPS. | **Server-Side (CPU):** Bandwidth limited. **Client-Side:** Lacks native geospatial compression. |
| **State Synchronization** | **Manual:** Re-query on change. Good for analytics. | **Automatic:** Real-time push. Good for multiplayer interactions. |
| **Geospatial Support** | **Mature:** GDAL, Proj4, GeoArrow ecosystem. | **Nascent:** Basic geometric types, no complex projection support. |
| **Network Overhead** | **Low:** Sends compressed vector field once. | **High:** If simulating on server. Medium if sending raw table data. |
| **Best Use Case** | Scientific Visualization, High-Fidelity Dashboards. | MMORPGs, Chat, Lobbies, Inventory Systems. |

**Key Insight:** SpacetimeDB excels at **Consistency** (ensuring all players see the *exact same* state at the same time), whereas the OpenGEOS stack excels at **Throughput** and **Visual Fidelity** (rendering massive datasets smoothly). For visualization, where "good enough" synchronization is acceptable but dropped frames are not, the OpenGEOS stack is superior.

## ---

**6\. Implementation Workflow: The "Storm Watch" Dashboard**

This section provides a narrative walkthrough of implementing the system to visualize a hypothetical storm moving across the UK and Ireland.

### **6.1 Phase 1: Ingestion and Normalization (DuckDB & Ibis)**

The workflow begins with DuckDB. Using the spatial extension, we mount the S3 buckets containing the Met Office UKV model and the Met Éireann HARMONIE model.  
We write an Ibis script to define the "virtual table." This script standardizes the column names (mapping u-component-of-wind to u) and performs a coordinate transformation on the Irish data, projecting it from ITM to WGS84 to match the UK data. Crucially, this step does not download the data yet; it simply defines the compute graph.

### **6.2 Phase 2: State Definition (PlanetScale)**

A user connects to the dashboard. PlanetScale retrieves their profile. The user selects "Storm Ciara \- Feb 2020." PlanetScale stores this state: view\_center: \[53.5, \-4.0\], zoom: 6, timestamp: 2020-02-09T12:00:00Z.  
Through the pg\_duckdb extension, PlanetScale can query the metadata table in MotherDuck to confirm that data for this timestamp is available and "warm" (cached).

### **6.3 Phase 3: The Reactive Loop (Marimo & GeoArrow)**

The user launches the **Marimo** notebook.

1. **Slider Interaction:** The user drags the time slider.  
2. **Reactive Trigger:** Marimo detects the variable change. It triggers the Ibis/DuckDB query.  
3. **Execution:** DuckDB executes the query. It reads the relevant "chunks" of the GRIB2/GeoParquet files for that specific hour.  
4. **Zero-Copy Transfer:** DuckDB outputs a **GeoArrow Table**. This binary object contains the U and V vectors for the viewport.  
5. **Data-to-Texture:** A Python helper converts this grid into a PNG or binary texture.

### **6.4 Phase 4: The Render (Lonboard & WebGPU)**

The texture is passed to the **AnyWidget** running in the browser.

1. The custom WindLayer (Deck.gl) receives the new texture.  
2. The **WebGPU Compute Shader** updates. It instantly applies the new wind vectors to the 100,000 particles currently swirling on the screen.  
3. **Result:** The user sees the wind patterns shift instantly as the storm moves across the Irish Sea. The particles accelerate where the gradient is steep (high wind speed) and spiral into low-pressure centers.

## ---

**7\. Strategic Recommendations and Future Outlook**

The convergence of cloud-native data formats and browser-based GPU compute has rendered the traditional "GIS Server" architecture obsolete for high-performance visualization. The **OpenGEOS/DuckDB/Lonboard** stack represents the optimal path for creating game-like meteorological visualizations.

### **7.1 Recommendations**

1. **Adopt GeoParquet:** Convert incoming GRIB2 data to GeoParquet immediately. While DuckDB *can* read GRIB2, Parquet is orders of magnitude faster for repeated querying and supports better compression.  
2. **Use SpacetimeDB for Collaboration, Not Simulation:** If the dashboard requires multiplayer features (e.g., users drawing annotation lines on the map that others must see instantly), use SpacetimeDB to handle *that specific layer*. Do not attempt to pipe the massive wind field data through it.  
3. **Leverage WebGPU:** Monitor the maturity of WebGPU in Deck.gl (v9.0+). Migrating from WebGL2 to WebGPU will allow for even more complex simulations, such as particles interacting with 3D terrain (mountains) or changing color based on real-time temperature probing.

### **7.2 Conclusion**

By decoupling the **Analytical Plane** (DuckDB/MotherDuck) from the **Transactional Plane** (PlanetScale) and the **Visual Plane** (Lonboard/WebGPU), this architecture achieves the best of all worlds: the query speed of an OLAP engine, the reliability of an ACID database, and the visual fidelity of a modern video game. This is the future of geospatial intelligence.

#### **Works cited**

1. Preface \- Introduction to GIS Programming \- Qiusheng Wu, accessed December 18, 2025, [https://gispro.gishub.org/book/preface.html](https://gispro.gishub.org/book/preface.html)  
2. Qiusheng Wu giswqs \- GitHub, accessed December 18, 2025, [https://github.com/giswqs](https://github.com/giswqs)  
3. Performance Guide \- DuckDB, accessed December 18, 2025, [https://duckdb.org/docs/stable/guides/performance/overview](https://duckdb.org/docs/stable/guides/performance/overview)  
4. How to use DuckDB's ST\_Read function to read and convert zipped shapefiles \- Flother, accessed December 18, 2025, [https://www.flother.is/til/duckdb-st-read/](https://www.flother.is/til/duckdb-st-read/)  
5. MotherDuck Integrates with PlanetScale Postgres \- MotherDuck Blog, accessed December 18, 2025, [https://motherduck.com/blog/motherduck-planetscale-integration/](https://motherduck.com/blog/motherduck-planetscale-integration/)  
6. DuckDB and MotherDuck support for PlanetScale Postgres, accessed December 18, 2025, [https://planetscale.com/changelog/postgres-extension-pg-duckdb-motherduck](https://planetscale.com/changelog/postgres-extension-pg-duckdb-motherduck)  
7. Using MotherDuck with PlanetScale, accessed December 18, 2025, [https://planetscale.com/blog/using-motherduck-with-planetscale](https://planetscale.com/blog/using-motherduck-with-planetscale)  
8. Integration with Ibis \- DuckDB, accessed December 18, 2025, [https://duckdb.org/docs/stable/guides/python/ibis](https://duckdb.org/docs/stable/guides/python/ibis)  
9. Ibis \+ DuckDB geospatial: a match made on Earth :: SciPy 2024 :: pretalx, accessed December 18, 2025, [https://cfp.scipy.org/2024/talk/PSR9BP/](https://cfp.scipy.org/2024/talk/PSR9BP/)  
10. Lonboard \- Overture Maps Documentation, accessed December 18, 2025, [https://docs.overturemaps.org/examples/lonboard/](https://docs.overturemaps.org/examples/lonboard/)  
11. What's New in Lonboard | Kyle Barron, accessed December 18, 2025, [https://kylebarron.dev/blog/new-in-lonboard/](https://kylebarron.dev/blog/new-in-lonboard/)  
12. How it works? \- lonboard \- Development Seed, accessed December 18, 2025, [https://developmentseed.org/lonboard/latest/how-it-works/](https://developmentseed.org/lonboard/latest/how-it-works/)  
13. Mixing code with widgets \- Marimo, accessed December 18, 2025, [https://marimo.io/features/feat-widgets](https://marimo.io/features/feat-widgets)  
14. Build plugins with anywidget\! \- Marimo, accessed December 18, 2025, [https://marimo.io/blog/anywidget](https://marimo.io/blog/anywidget)  
15. Met Office Weather DataHub \- Met Office, accessed December 18, 2025, [https://www.metoffice.gov.uk/services/data/met-office-weather-datahub](https://www.metoffice.gov.uk/services/data/met-office-weather-datahub)  
16. Meteorological improvements. \- Met Éireann, accessed December 18, 2025, [https://opendata2.met.ie/opendata2/docs/NWP\_explained.odt](https://opendata2.met.ie/opendata2/docs/NWP_explained.odt)  
17. AnyWidget \- marimo, accessed December 18, 2025, [https://docs.marimo.io/api/inputs/anywidget/](https://docs.marimo.io/api/inputs/anywidget/)  
18. Overview | SpacetimeDB docs, accessed December 18, 2025, [https://spacetimedb.com/docs/](https://spacetimedb.com/docs/)  
19. SpacetimeDB, accessed December 18, 2025, [https://spacetimedb.com/](https://spacetimedb.com/)  
20. SpacetimeDB \- Hacker News, accessed December 18, 2025, [https://news.ycombinator.com/item?id=43631822](https://news.ycombinator.com/item?id=43631822)  
21. SpacetimeDB: A new database written in Rust that replaces your server entirely \- Reddit, accessed December 18, 2025, [https://www.reddit.com/r/programming/comments/15mgp4i/spacetimedb\_a\_new\_database\_written\_in\_rust\_that/](https://www.reddit.com/r/programming/comments/15mgp4i/spacetimedb_a_new_database_written_in_rust_that/)

---

## Geospatial Workflow & Particle Effects(1)

*Source: `docs/bunchloch/teanga/Geospatial Workflow & Particle Effects(1).md` (3803 words, 341 lines)*

# **Architectural Synthesis of High-Performance Geospatial Workflows: Integrating Cloud-Native OLAP and WebGPU Rendering for Meteorological Particle Simulation**

## **Executive Summary**

The geospatial data science landscape is currently undergoing a structural revolution, transitioning from file-based, desktop-centric workflows to cloud-native, serverless architectures that prioritize zero-copy data transport and hardware-accelerated visualization. This report presents a comprehensive technical blueprint for a modern geospatial workflow, explicitly designed to ingest, process, and visualize high-velocity meteorological data from the **UK Met Office** and **GeoHive (Ireland)**. The proposed architecture leverages the **opengeos** and **giswqs** ecosystem to integrate **DuckDB**, **MotherDuck**, **PlanetScale**, **GeoParquet**, **Lonboard**, **Ibis**, and **Marimo**. The primary technical objective is to replicate "game-like" visual fidelity—specifically particle-based wind flow simulations—within a browser-based analytical environment.  
A central component of this analysis is a rigorous comparative evaluation against **SpacetimeDB**, an emerging "database-as-backend" technology. While SpacetimeDB offers a unified approach to state management ideal for multiplayer gaming logic, this report argues that the **DuckDB-GeoArrow-Lonboard** pipeline provides superior performance for scientific visualization. This advantage stems from its optimization for vectorized memory transport and client-side WebGPU compute, which decouples the visual simulation from the bandwidth constraints of server-authoritative state synchronization.  
This document serves as a foundational reference for data engineers and geospatial architects seeking to implement high-performance dashboards that bridge the gap between traditional GIS precision and modern video game graphics.

## ---

**1\. Introduction: The Convergence of GIS and Real-Time Graphics**

### **1.1 The Shift to Cloud-Native Geospatial**

Historically, Geographic Information Systems (GIS) have been characterized by heavy client-side software, monolithic spatial databases (like PostGIS), and intermediate file formats (Shapefiles, GeoJSON) that require significant serialization overhead. However, the emergence of the "Modern Data Stack" has introduced tools that are modular, ephemeral, and incredibly fast. This shift is typified by the "Cloud-Native Geospatial" paradigm, which emphasizes accessing data directly from object storage (S3) using range requests, rather than downloading entire datasets.  
The **opengeos** initiative, championed by researchers and developers such as Qiusheng Wu (giswqs), represents the vanguard of this movement.1 By prioritizing open-source tools that leverage binary formats and efficient memory management, this ecosystem allows for the processing of datasets—such as global weather models—that were previously the domain of supercomputers or dedicated workstations.

### **1.2 The Challenge of Game-Like Fidelity**

Users increasingly demand visualization interfaces that match the fluidity and responsiveness of video games. In the context of meteorology, this means moving beyond static isobars or "hedgehog" arrow plots to dynamic, animated particle systems that visualize wind flow as a continuous fluid medium. Achieving this requires a rendering pipeline that can handle hundreds of thousands of moving entities at 60 frames per second (FPS).  
This requirement creates a technical tension between **Analytical Precision** (the domain of SQL databases) and **Visual Performance** (the domain of Game Engines/GPUs). The workflow proposed herein seeks to resolve this tension by integrating a high-performance analytical engine (**DuckDB**) with a WebGPU-accelerated visualization library (**Lonboard**), mediated by a zero-copy transport layer (**GeoArrow**).

### **1.3 Scope of Analysis**

This report focuses on two primary meteorological datasets:

1. **Met Office (UK):** Global Spot Data and Atmospheric Model outputs.  
2. **GeoHive / Met Éireann (Ireland):** The HARMONIE-AROME high-resolution numerical weather prediction (NWP) model.

The analysis will detail the ingestion of these datasets, their normalization via **Ibis**, state management via **PlanetScale**, and final rendering in **Marimo** notebooks. It will then contrast this approach with **SpacetimeDB**, evaluating the trade-offs between a modular OLAP-centric stack and a unified, reducer-based simulation backend.

## ---

**2\. The Modern Geospatial Stack: Component Architecture**

The proposed architecture is not a monolithic application but a composable pipeline. Each tool is selected for its ability to handle specific types of complexity: computational, semantic, or visual.

### **2.1 The Computational Core: DuckDB and MotherDuck**

#### **2.1.1 DuckDB: The In-Process Analytical Engine**

**DuckDB** serves as the primary computational engine for this workflow. Often described as "SQLite for analytics," DuckDB is an embedded SQL OLAP database designed for vectorized query execution.3 Unlike row-oriented databases (PostgreSQL, MySQL), DuckDB organizes data by columns, which allows for highly efficient compression and CPU cache utilization—critical factors when processing the dense float arrays found in meteorological GRIB2 files.  
The pivotal feature for this workflow is the **DuckDB Spatial Extension**. This extension bundles the **GDAL** (Geospatial Data Abstraction Library) drivers, enabling DuckDB to function as a virtual file system. Through functions like ST\_Read, DuckDB can mount remote GRIB2 files (hosted on HTTP servers or S3 buckets) and query them directly as if they were local tables.4 This capability is fundamental to the "Cloud-Native" approach, as it eliminates the need for an intermediate ETL (Extract, Transform, Load) step to ingest massive weather model runs into a database before querying.

#### **2.1.2 MotherDuck: Hybrid Execution Strategy**

**MotherDuck** extends DuckDB into the cloud, enabling a serverless, collaborative data warehousing model. In the context of this workflow, MotherDuck solves the "Data Gravity" problem.

* **Historical Archive:** While local DuckDB instances are excellent for processing the "latest" forecast (hundreds of megabytes), analyzing historical trends (e.g., "Compare today's Storm Kathleen with 2014's Storm Darwin") involves terabytes of data. MotherDuck hosts this historical archive.  
* **Hybrid Querying:** The duckdb client can execute queries that join local data (the current forecast GRIB file) with remote data (historical climatology in MotherDuck). MotherDuck’s engine intelligently separates the query plan, executing the heavy aggregations in the cloud and returning only the results to the local Marimo client.5

### **2.2 The Transactional State Layer: PlanetScale**

While DuckDB handles immutable analytical data, an interactive application requires a mutable state: user preferences, saved viewports, annotation layers, and session management. **PlanetScale** fulfills this role.

#### **2.2.1 Architecture and Integration**

PlanetScale is built on **Vitess**, a database clustering system for horizontal scaling of MySQL (and now PostgreSQL). Recently, PlanetScale introduced support for PostgreSQL, including the **pg\_duckdb** extension.6 This integration is architecturally significant.

* **The "Lakehouse" Pattern:** By installing pg\_duckdb within PlanetScale, the transactional database acts as a gateway to the analytical warehouse. A user application can send a standard SQL query to PlanetScale to retrieve a user's saved location, and in the same transaction, join that location data with wind vector data residing in MotherDuck.7  
* **Performance:** PlanetScale’s architecture is optimized for high-concurrency, low-latency lookups (OLTP). This ensures that the application interface remains snappy (e.g., logging in, loading lists of saved maps) even while heavy analytical queries are processing in the background.

### **2.3 The Semantic Layer: Ibis**

One of the persistent challenges in geospatial engineering is "SQL Dialect Fatigue." Syntax varies between PostGIS, DuckDB Spatial, and BigQuery GIS. **Ibis** addresses this by providing a unified, Pythonic dataframe API that compiles to SQL.8

* **Expression Trees:** Unlike Pandas, which executes operations immediately (eager evaluation), Ibis builds a lazy expression tree. This allows the framework to optimize the query before execution.  
* **Engine Agnosticism:** By writing the geospatial transformation logic (e.g., table.filter(st\_intersects(...))) in Ibis, the workflow becomes decoupled from the backend. The same Python code can drive a local DuckDB instance during development and a MotherDuck or PlanetScale backend in production, simply by switching the connection object.9

### **2.4 The Transport Layer: GeoParquet and GeoArrow**

The bottleneck in most web-based GIS is serialization. Converting binary database rows into textual GeoJSON (a JSON-based format) requires expensive parsing and significantly inflates file size.

* **GeoParquet:** This format extends Apache Parquet to support geospatial types. It is used for the *persistent storage* of processed weather tiles. Its columnar compression (Snappy, Zstd) is highly effective for repetitive grid coordinates.10  
* **GeoArrow:** This is the *in-memory* standard. When DuckDB executes a query, it can output the result as an Arrow table—a contiguous block of memory. This binary buffer can be passed directly to Python and then to the JavaScript/GPU layer without serialization. This "Zero-Copy" transfer is the technological breakthrough that enables visualizing millions of particles in the browser.11

### **2.5 The Visualization Layer: Lonboard and Marimo**

**Lonboard** is a bridge library connecting Python data (GeoArrow) to **Deck.gl** (JavaScript/WebGL). **Marimo** is a next-generation reactive notebook environment.

* **Reactive Execution:** Unlike Jupyter, which maintains a hidden global state that can lead to out-of-order execution errors, Marimo treats the notebook as a Directed Acyclic Graph (DAG).13 If a user moves a time slider, Marimo automatically re-executes only the dependent cells (e.g., the DuckDB query and the map render), ensuring a responsive, glitch-free dashboard.  
* **WebGPU Context:** Marimo supports **AnyWidget**, a protocol for embedding modern JavaScript widgets. This allows the workflow to instantiate custom Deck.gl layers that utilize WebGPU compute shaders, bypassing the limitations of the standard DOM.14

## ---

**3\. Data Engineering: Ingesting UK and Irish Meteorological Data**

To visualize wind flow, the system must ingest **Vector Fields**: grids where every point contains a $U$ (Zonal/East-West) and $V$ (Meridional/North-South) component.

### **3.1 UK Met Office Data Structure**

The UK Met Office exposes data via the **Weather DataHub**. For high-fidelity visualisations, two primary products are relevant:

1. **Global Spot Data:** Provides point-based forecasts. While useful for validation, it lacks the spatial continuity required for particle simulation.15  
2. **Atmospheric Models (UKV / Global):** These provide gridded fields. The data is delivered in **GRIB2** format.

#### **3.1.1 GRIB2 Structure**

A GRIB2 (General Regularly-distributed Information in Binary form) file is a container format composed of multiple "messages." Each message corresponds to a specific variable (e.g., Wind Speed) at a specific vertical level (e.g., 10m above ground) and forecast step.

* **Section 0:** Indicator Section (File type).  
* **Section 3:** Grid Definition Template (Defining the geometry—Lat/Lon vs Rotated Pole).  
* **Section 4:** Product Definition Template (Parameter category: Momentum; Parameter number: U-component).  
* **Section 5:** Data Representation Template (Packing method, typically JPEG2000 or CCSDS).  
* **Section 7:** Data Template (The actual binary payload).

**Ingestion Strategy:** DuckDB's ST\_Read utilizes the GDAL GRIB driver. To extract the wind vectors, the query must filter by the GRIB "Element" or "Band." Typically, Band 1 is $U$ and Band 2 is $V$ in combined files, but often they are distributed as separate files.

### **3.2 Met Éireann (GeoHive) Data Structure**

Met Éireann operates the **HARMONIE-AROME** model, a Limited Area Model (LAM) focused on Ireland.

* **Resolution:** 2.5km horizontal grid.  
* **Update Cycle:** 54-hour forecasts produced every 3 hours (00Z, 03Z, etc.).  
* **Systems:** Historically **IREPS** (Irish Regional Ensemble Prediction System), recently upgraded to **DINI-EPS** (Denmark-Ireland-Netherlands-Iceland) collaboration.16

#### **3.2.1 Access via Open Data**

While GeoHive acts as the geospatial portal, the raw GRIB2 files are hosted on Met Éireann's Open Data HTTP servers (https://opendata.met.ie).

* **File Naming Convention:** Harmonie\_IRE\_2.5km\_wind\_YYYYMMDDHH.grib2.  
* **Projection:** HARMONIE uses a **Lambert Conformal Conic** projection (to minimize distortion over Ireland) or a Rotated Lat/Lon grid. This contrasts with the Global Met Office models which often use WGS84 (EPSG:4326).

Ingestion Challenge: Particle visualization libraries (Deck.gl) generally expect Web Mercator or WGS84 coordinates.  
Solution: The DuckDB ingestion query must perform an on-the-fly coordinate transformation (ST\_Transform) to reproject the HARMONIE vectors from Lambert Conformal to WGS84.

### **3.3 Harmonization via Ibis**

The power of Ibis lies in its ability to abstract these differences. We can define a "Virtual Schema" for wind data and map both sources to it.

| Standard Field | Met Office Source | Met Éireann Source |
| :---- | :---- | :---- |
| timestamp | forecast\_reference\_time \+ step | validityTime |
| geometry | ST\_Point(lon, lat) | ST\_Transform(ST\_Point(x,y), 2157, 4326\) |
| u\_vector | band\_1 (Param 2, Cat 2\) | u-component |
| v\_vector | band\_2 (Param 3, Cat 2\) | v-component |

**Table 1:** Schema Mapping for Wind Vector Normalization.

Python

\# Conceptual Ibis Normalization Logic  
import ibis

def normalize\_wind(table, source\_type):  
    if source\_type \== 'met\_office':  
        return table.select(  
            time='forecast\_time',  
            u=table\['wind\_u\_10m'\],  
            v=table\['wind\_v\_10m'\],  
            geometry=ibis.geo.point(table.lon, table.lat)  
        )  
    elif source\_type \== 'met\_eireann':  
        \# Apply projection transform if needed via expression  
        return table.select(  
            time='validity\_time',  
            u=table\['u\_10m'\],  
            v=table\['v\_10m'\],  
            geometry=ibis.geo.transform(table.geom, 4326\)  
        )

## ---

**4\. Visualization Mechanics: Creating "Game-Like" Particle Effects**

The requirement for "game-like" effects implies a level of interactivity and visual smoothness (60 FPS) that static map tiles cannot provide. In fluid dynamics visualization, this is achieved through **Lagrangian Particle Tracking**.

### **4.1 The Physics of Flow**

There are two ways to represent fluid flow:

1. **Eulerian:** Inspecting the fluid properties (velocity, pressure) at fixed points in space (the Grid). This is what the GRIB2 file contains.  
2. **Lagrangian:** Following specific particles as they move through space and time. This is what the visualization renders.

The Simulation Loop:  
To visualize the Eulerian data (grid) in a Lagrangian way (particles), the rendering engine must perform Numerical Integration.

$$P\_{t+1} \= P\_t \+ \\vec{V}(P\_t) \\cdot \\Delta t$$

Where:

* $P\_t$ is the particle position at time $t$.  
* $\\vec{V}(P\_t)$ is the velocity vector sampled from the grid at position $P\_t$.  
* $\\Delta t$ is the time step.

### **4.2 WebGPU and Deck.gl Implementation**

Simulating 100,000+ particles using this equation on a CPU is too slow for JavaScript. The solution uses **WebGPU** (or WebGL2 Transform Feedback) to perform this integration on the Graphics Processing Unit.

#### **4.2.1 The Texture Strategy**

Instead of passing 100,000 velocity values to the GPU every frame, we pass the "Vector Field" as a **Texture** (an image).

* **Red Channel:** Encodes the U-component (scaled to 0-255).  
* **Green Channel:** Encodes the V-component.  
* **Blue Channel:** (Optional) Encodes temperature or magnitude.

DuckDB reads the GRIB2 data and exports it not as a list of points, but as a binary image buffer (PNG or raw bytes). This buffer is uploaded to the GPU memory once.

#### **4.2.2 The Compute Shader**

A WebGPU Compute Shader runs for every particle instance:

1. **Sample:** It reads the particle's current coordinate $(x, y)$.  
2. **Lookup:** It samples the Velocity Texture at $(x, y)$ to get $\\vec{V}$.  
3. **Integrate:** It calculates the new position.  
4. **Boundary Check:** If the particle moves off-screen or exceeds a "lifetime" counter, it resets to a random position.

### **4.3 Extending Lonboard with AnyWidget**

**Lonboard** natively supports ScatterplotLayer and PathLayer, which are insufficient for this simulation loop. We must extend it using **AnyWidget**.  
**AnyWidget** allows us to write a custom JavaScript module that wraps a specialized Deck.gl layer (like ParticleLayer from the weatherlayers or deck.gl-particle community packages) and expose it to Python.17

* **Python Side (WindWidget.py):** Defines a class inheriting from anywidget.AnyWidget. It has Traitlets for u\_texture, v\_texture, particle\_count, and speed\_factor.  
* **JavaScript Side (widget.js):** Listens for changes to these traits. When the u\_texture changes (because the user moved the time slider in Marimo), the JS updates the Deck.gl layer's texture uniform.

Synchronization:  
Because Marimo uses a reactive execution graph, connecting the Time Slider to the DuckDB query automatically triggers the chain:  
Slider Move \-\> DuckDB Query \-\> Ibis Processing \-\> GeoArrow/Image Output \-\> AnyWidget Update \-\> GPU Render.  
This creates a seamless, "game-like" experience where the wind field shifts smoothly as the user scrubs through time.

## ---

**5\. Comparative Architecture: SpacetimeDB**

To fully evaluate the proposed stack, we must compare it against **SpacetimeDB**, a technology that fundamentally rethinks the relationship between the database and the application.

### **5.1 SpacetimeDB: The Database IS the Server**

Traditional architectures separate the Database (Postgres) from the Backend Server (Node.js/Python). **SpacetimeDB** unifies them. It is a relational database that executes application logic (written in Rust or C\#) *inside* the database transaction loop.18

* **Reducers:** Instead of API endpoints, you define "Reducers"—functions that mutate the database state.  
* **Tick Rate:** The database has a concept of "time" and can run scheduled reducers (e.g., update\_physics()) every tick.  
* **Client Sync:** Clients subscribe to tables. When a reducer changes a row, the database automatically pushes the update to the client SDK.

### **5.2 The Particle Effect Challenge in SpacetimeDB**

How would one implement the "Wind Particle" simulation in SpacetimeDB?

#### **5.2.1 Approach A: Server-Authoritative Particles**

In this model, every particle is a row in a Particles table: (id, x, y, velocity).

* A server-side reducer iterates through the table 60 times a second, updating $x$ and $y$ based on the wind field.  
* **Failure Mode:** This requires broadcasting the position of 100,000 particles to every connected client 60 times a second. The bandwidth requirement (approx 100MB/s) is impossible for web clients. SpacetimeDB is optimized for *game state* (inventory, player health, position of 50 players), not *dense simulation data*.20

#### **5.2.2 Approach B: Client-Side Simulation (The Hybrid)**

In this model, SpacetimeDB stores only the **Wind Field** (the grid data).

* The client connects and downloads the Wind Field.  
* The client performs the particle simulation locally (using Unity/C\# or JS).  
* **Comparison:** In this scenario, SpacetimeDB acts merely as a data distribution API. However, it lacks the specialized compression of GeoParquet or the range-request capabilities of DuckDB. It would require parsing the GRIB2 file into SpacetimeDB tables (inserting millions of rows), which is far less efficient than DuckDB's zero-copy ST\_Read.

### **5.3 Comparison Matrix**

| Feature | OpenGEOS Stack (DuckDB/Lonboard) | SpacetimeDB |
| :---- | :---- | :---- |
| **Primary Philosophy** | **Data Gravity:** Move compute to the data (SQL/WebGPU). | **Unified State:** Logic lives with the data (Reducers). |
| **Data Ingestion** | **Native:** Reads GRIB2/Parquet directly. Zero-ETL. | **Custom:** Requires writing parsers to import data into DB tables. |
| **Particle Simulation** | **Client-Side (GPU):** Simulates 1M+ particles at 60 FPS. | **Server-Side (CPU):** Bandwidth limited. **Client-Side:** Lacks native geospatial compression. |
| **State Synchronization** | **Manual:** Re-query on change. Good for analytics. | **Automatic:** Real-time push. Good for multiplayer interactions. |
| **Geospatial Support** | **Mature:** GDAL, Proj4, GeoArrow ecosystem. | **Nascent:** Basic geometric types, no complex projection support. |
| **Network Overhead** | **Low:** Sends compressed vector field once. | **High:** If simulating on server. Medium if sending raw table data. |
| **Best Use Case** | Scientific Visualization, High-Fidelity Dashboards. | MMORPGs, Chat, Lobbies, Inventory Systems. |

**Key Insight:** SpacetimeDB excels at **Consistency** (ensuring all players see the *exact same* state at the same time), whereas the OpenGEOS stack excels at **Throughput** and **Visual Fidelity** (rendering massive datasets smoothly). For visualization, where "good enough" synchronization is acceptable but dropped frames are not, the OpenGEOS stack is superior.

## ---

**6\. Implementation Workflow: The "Storm Watch" Dashboard**

This section provides a narrative walkthrough of implementing the system to visualize a hypothetical storm moving across the UK and Ireland.

### **6.1 Phase 1: Ingestion and Normalization (DuckDB & Ibis)**

The workflow begins with DuckDB. Using the spatial extension, we mount the S3 buckets containing the Met Office UKV model and the Met Éireann HARMONIE model.  
We write an Ibis script to define the "virtual table." This script standardizes the column names (mapping u-component-of-wind to u) and performs a coordinate transformation on the Irish data, projecting it from ITM to WGS84 to match the UK data. Crucially, this step does not download the data yet; it simply defines the compute graph.

### **6.2 Phase 2: State Definition (PlanetScale)**

A user connects to the dashboard. PlanetScale retrieves their profile. The user selects "Storm Ciara \- Feb 2020." PlanetScale stores this state: view\_center: \[53.5, \-4.0\], zoom: 6, timestamp: 2020-02-09T12:00:00Z.  
Through the pg\_duckdb extension, PlanetScale can query the metadata table in MotherDuck to confirm that data for this timestamp is available and "warm" (cached).

### **6.3 Phase 3: The Reactive Loop (Marimo & GeoArrow)**

The user launches the **Marimo** notebook.

1. **Slider Interaction:** The user drags the time slider.  
2. **Reactive Trigger:** Marimo detects the variable change. It triggers the Ibis/DuckDB query.  
3. **Execution:** DuckDB executes the query. It reads the relevant "chunks" of the GRIB2/GeoParquet files for that specific hour.  
4. **Zero-Copy Transfer:** DuckDB outputs a **GeoArrow Table**. This binary object contains the U and V vectors for the viewport.  
5. **Data-to-Texture:** A Python helper converts this grid into a PNG or binary texture.

### **6.4 Phase 4: The Render (Lonboard & WebGPU)**

The texture is passed to the **AnyWidget** running in the browser.

1. The custom WindLayer (Deck.gl) receives the new texture.  
2. The **WebGPU Compute Shader** updates. It instantly applies the new wind vectors to the 100,000 particles currently swirling on the screen.  
3. **Result:** The user sees the wind patterns shift instantly as the storm moves across the Irish Sea. The particles accelerate where the gradient is steep (high wind speed) and spiral into low-pressure centers.

## ---

**7\. Strategic Recommendations and Future Outlook**

The convergence of cloud-native data formats and browser-based GPU compute has rendered the traditional "GIS Server" architecture obsolete for high-performance visualization. The **OpenGEOS/DuckDB/Lonboard** stack represents the optimal path for creating game-like meteorological visualizations.

### **7.1 Recommendations**

1. **Adopt GeoParquet:** Convert incoming GRIB2 data to GeoParquet immediately. While DuckDB *can* read GRIB2, Parquet is orders of magnitude faster for repeated querying and supports better compression.  
2. **Use SpacetimeDB for Collaboration, Not Simulation:** If the dashboard requires multiplayer features (e.g., users drawing annotation lines on the map that others must see instantly), use SpacetimeDB to handle *that specific layer*. Do not attempt to pipe the massive wind field data through it.  
3. **Leverage WebGPU:** Monitor the maturity of WebGPU in Deck.gl (v9.0+). Migrating from WebGL2 to WebGPU will allow for even more complex simulations, such as particles interacting with 3D terrain (mountains) or changing color based on real-time temperature probing.

### **7.2 Conclusion**

By decoupling the **Analytical Plane** (DuckDB/MotherDuck) from the **Transactional Plane** (PlanetScale) and the **Visual Plane** (Lonboard/WebGPU), this architecture achieves the best of all worlds: the query speed of an OLAP engine, the reliability of an ACID database, and the visual fidelity of a modern video game. This is the future of geospatial intelligence.

#### **Works cited**

1. Preface \- Introduction to GIS Programming \- Qiusheng Wu, accessed December 18, 2025, [https://gispro.gishub.org/book/preface.html](https://gispro.gishub.org/book/preface.html)  
2. Qiusheng Wu giswqs \- GitHub, accessed December 18, 2025, [https://github.com/giswqs](https://github.com/giswqs)  
3. Performance Guide \- DuckDB, accessed December 18, 2025, [https://duckdb.org/docs/stable/guides/performance/overview](https://duckdb.org/docs/stable/guides/performance/overview)  
4. How to use DuckDB's ST\_Read function to read and convert zipped shapefiles \- Flother, accessed December 18, 2025, [https://www.flother.is/til/duckdb-st-read/](https://www.flother.is/til/duckdb-st-read/)  
5. MotherDuck Integrates with PlanetScale Postgres \- MotherDuck Blog, accessed December 18, 2025, [https://motherduck.com/blog/motherduck-planetscale-integration/](https://motherduck.com/blog/motherduck-planetscale-integration/)  
6. DuckDB and MotherDuck support for PlanetScale Postgres, accessed December 18, 2025, [https://planetscale.com/changelog/postgres-extension-pg-duckdb-motherduck](https://planetscale.com/changelog/postgres-extension-pg-duckdb-motherduck)  
7. Using MotherDuck with PlanetScale, accessed December 18, 2025, [https://planetscale.com/blog/using-motherduck-with-planetscale](https://planetscale.com/blog/using-motherduck-with-planetscale)  
8. Integration with Ibis \- DuckDB, accessed December 18, 2025, [https://duckdb.org/docs/stable/guides/python/ibis](https://duckdb.org/docs/stable/guides/python/ibis)  
9. Ibis \+ DuckDB geospatial: a match made on Earth :: SciPy 2024 :: pretalx, accessed December 18, 2025, [https://cfp.scipy.org/2024/talk/PSR9BP/](https://cfp.scipy.org/2024/talk/PSR9BP/)  
10. Lonboard \- Overture Maps Documentation, accessed December 18, 2025, [https://docs.overturemaps.org/examples/lonboard/](https://docs.overturemaps.org/examples/lonboard/)  
11. What's New in Lonboard | Kyle Barron, accessed December 18, 2025, [https://kylebarron.dev/blog/new-in-lonboard/](https://kylebarron.dev/blog/new-in-lonboard/)  
12. How it works? \- lonboard \- Development Seed, accessed December 18, 2025, [https://developmentseed.org/lonboard/latest/how-it-works/](https://developmentseed.org/lonboard/latest/how-it-works/)  
13. Mixing code with widgets \- Marimo, accessed December 18, 2025, [https://marimo.io/features/feat-widgets](https://marimo.io/features/feat-widgets)  
14. Build plugins with anywidget\! \- Marimo, accessed December 18, 2025, [https://marimo.io/blog/anywidget](https://marimo.io/blog/anywidget)  
15. Met Office Weather DataHub \- Met Office, accessed December 18, 2025, [https://www.metoffice.gov.uk/services/data/met-office-weather-datahub](https://www.metoffice.gov.uk/services/data/met-office-weather-datahub)  
16. Meteorological improvements. \- Met Éireann, accessed December 18, 2025, [https://opendata2.met.ie/opendata2/docs/NWP\_explained.odt](https://opendata2.met.ie/opendata2/docs/NWP_explained.odt)  
17. AnyWidget \- marimo, accessed December 18, 2025, [https://docs.marimo.io/api/inputs/anywidget/](https://docs.marimo.io/api/inputs/anywidget/)  
18. Overview | SpacetimeDB docs, accessed December 18, 2025, [https://spacetimedb.com/docs/](https://spacetimedb.com/docs/)  
19. SpacetimeDB, accessed December 18, 2025, [https://spacetimedb.com/](https://spacetimedb.com/)  
20. SpacetimeDB \- Hacker News, accessed December 18, 2025, [https://news.ycombinator.com/item?id=43631822](https://news.ycombinator.com/item?id=43631822)  
21. SpacetimeDB: A new database written in Rust that replaces your server entirely \- Reddit, accessed December 18, 2025, [https://www.reddit.com/r/programming/comments/15mgp4i/spacetimedb\_a\_new\_database\_written\_in\_rust\_that/](https://www.reddit.com/r/programming/comments/15mgp4i/spacetimedb_a_new_database_written_in_rust_that/)

---

## Ibis, LanceDB, and Data Stack Integration

*Source: `docs/bunchloch/teanga/Ibis, LanceDB, and Data Stack Integration.md` (3596 words, 331 lines)*

# **The Converged Lakehouse: Architecting a Multimodal Data Environment with Lance Namespace and the Composable Stack**

## **1\. Executive Introduction: The Era of the Composable AI Stack**

The contemporary data infrastructure landscape is witnessing a fundamental dissolution of the historical barriers between Online Transactional Processing (OLTP), Online Analytical Processing (OLAP), and the burgeoning domain of Artificial Intelligence (AI) data management. We are moving beyond the monolithic paradigms of the single-vendor data warehouse and the unmanaged data lake into a third era: the **Composable AI Stack**. The environment proposed in this research—integrating **Ibis**, **DuckDB**, **MotherDuck**, **PlanetScale**, **Cloudflare R2**, **Iceberg**, **DuckLake**, and **Lance Namespace**—represents the vanguard of this architectural shift. It is a system designed not merely for "data processing" in the abstract, but specifically for the high-fidelity management of multimodal assets, such as PDF documents and their semantic vector embeddings, alongside rigorous transactional state management.  
The core challenge addressed by this architecture is the "impedance mismatch" between structured business data (users, subscriptions, access logs) and unstructured AI data (vectors, binary blobs, neural indices). Historically, these lived in separate silos: Postgres for the business, S3 for the files, and a specialized vector database for the embeddings. This fragmentation introduces latency, data drift, and governance nightmares. By unifying these layers through **Cloudflare R2** (as the universal storage substrate) and bridging them with **Lance Namespace** (as the metadata unifier), this architecture proposes a "Zero-Copy," "Zero-Egress" future where compute engines are brought to the data, rather than data being shipped to the compute.  
This report serves as an exhaustive architectural blueprint and implementation guide for this specific stack. It places a heavy emphasis on the role of **Lance Namespace**, dissecting its function as the integration layer that allows "AI-native" data (Lance format) to coexist and interoperate with "Analytics-native" data (Iceberg/DuckLake) and "Transaction-native" data (Postgres). We will explore the theoretical underpinnings of storage-compute separation, the mechanics of hybrid execution, and the practical implementation details of serving PDF files at the edge using this converged infrastructure.

## ---

**2\. The Architectural Foundation: Unbundling the Database**

To understand how best to utilize Lance Namespace within this stack, one must first rigorously define the role of each component. This ecosystem relies on the principle of "best-of-breed" specialization, where distinct tools solve specific classes of data engineering problems but are loosely coupled through open standards (Arrow, Parquet, Lance, SQL).

### **2.1. The Universal Interface: Ibis as the Control Plane**

In this heterogeneous environment, the developer experience is the primary risk factor. Managing connections to PlanetScale (MySQL/Postgres protocol), MotherDuck (DuckDB protocol), and LanceDB (Native/Arrow protocol) requires a unifying linguistic layer. **Ibis** fulfills this role as the portable Python DataFrame API.  
Unlike eager-execution libraries like pandas, which pull data into memory immediately, Ibis operates on a **lazy evaluation** model. It constructs an intermediate semantic representation of the query—a logical plan—and then compiles this plan into the native dialect of the target backend.1 This capability is indispensable in a stack where data resides in different physical locations (PlanetScale in AWS/GCP, MotherDuck in the cloud, Lance in R2).  
Ibis acts as the **federation coordinator**. While Ibis typically pushes a query to a single backend, the integration with **DuckDB** allows Ibis to act as a virtualization layer. Through DuckDB's ability to attach to external databases (Postgres via postgres\_scanner, S3 via httpfs), Ibis can express complex join logic across these systems in a single, fluent Python syntax.1 For the specific requirement of handling Lance datasets, Ibis serves as the orchestration tool that defines *what* data is needed, relying on DuckDB and Lance Namespace to handle the *how* of retrieval from R2.

### **2.2. The Compute Engine: DuckDB and MotherDuck**

**DuckDB** is the "engine room" of this architecture. As an in-process SQL OLAP database, it runs directly within the application container or the data processing worker. Its vectorized execution engine is optimized for analytical queries on columnar data, making it the ideal processor for the Parquet and Lance files stored in R2.2  
**MotherDuck** extends DuckDB into a serverless cloud data warehouse. It introduces the concept of **Hybrid Execution**, where a query plan can be split: purely local operations run on the developer's machine or worker node, while heavy aggregations or joins on large datasets are shipped to the MotherDuck cloud.4

* **Role in this Stack:** MotherDuck is the primary engine for heavy analytical lifting. It is responsible for joining the high-volume clickstream/access logs (stored in DuckLake format) with the dimensional user data (from PlanetScale).  
* **DuckLake:** This is MotherDuck’s optimized table format and catalog. Unlike generic data lakes, DuckLake brings ACID compliance and "time travel" to data stored in object storage.5 It is designed to work seamlessly with the DuckDB engine, offering features like **Data Inlining**, where small inserts are stored directly in the metadata to avoid the "small file problem" common in S3-based lakes.6

### **2.3. The Operational Store: PlanetScale PostgreSQL**

PlanetScale has historically been synonymous with Vitess and MySQL. However, the introduction of **PlanetScale for Postgres** fundamentally changes the integration dynamic of this stack.7

* **Role:** It serves as the immutable "System of Record" for transactional entities: User IDs, Billing, Authentication, and the mutable metadata of the PDF uploads (e.g., "is\_public", "owner\_id").  
* **The pg\_duckdb Bridge:** This is a critical synergy. PlanetScale Postgres supports the pg\_duckdb extension, which embeds the DuckDB engine *inside* the Postgres process.4 This allows the transactional database to query external data lakes (Parquet/Lance on R2) directly. It effectively blurs the line between OLTP and OLAP, allowing a developer to write a SQL query in PlanetScale that joins a local users table with a remote vector\_search\_logs table stored in MotherDuck.

### **2.4. The Storage Layer: Cloudflare R2**

**Cloudflare R2** is the physical foundation of the "Lake." Its S3-compatible API ensures compatibility with every tool in this stack (DuckDB, LanceDB, Iceberg).

* **Economic Strategic Advantage:** The "serving of PDF files" implies a high-read-volume workload. Traditional cloud object stores (AWS S3, Google GCS) charge significant egress fees for data moving out of their network. R2’s **zero-egress** model is the economic enabler of this architecture.9 It allows the PDFs to be served directly to users or retrieved by compute nodes for vectorization without incurring bandwidth penalties.  
* **Performance:** R2’s global distribution and tiering ensure low latency for retrieving large binary blobs (PDFs), effectively acting as a storage-backed CDN.

### **2.5. The Metadata Layer: Iceberg REST and Lance Namespace**

This layer provides the "governance and discovery" capabilities. Without a shared catalog, files in R2 are just "dark data," invisible to the query engines.

* **Iceberg REST Catalog:** This is the industry standard for tracking table metadata (schemas, snapshots, partitions) in a vendor-neutral way.10 It decouples the table state from the file system.  
* **Lance Namespace:** This is the specialized integration layer for the user’s vector data. It allows Lance-formatted tables (which are optimized for AI) to be registered and managed within the standard Iceberg REST catalog, making them discoverable alongside standard analytical tables.11

## ---

**3\. Deep Dive: Lance Namespace Integration Strategy**

The user's core inquiry revolves around "how best to use Lance Namespace integrating with the rest of this stack." This section serves as the definitive guide to that integration, moving from conceptual architecture to concrete implementation patterns.

### **3.1. The Problem Space: The "Split-Brain" Lakehouse**

In a standard data architecture, one often encounters a bifurcation:

1. **The Analytics Lake:** Tables stored in Parquet/Iceberg format, managed by a Hive Metastore or Iceberg Catalog, and queried by Spark, Trino, or DuckDB.  
2. **The AI Silo:** Vector embeddings stored in a specialized Vector Database (Pinecone, Milvus) or in raw files managed by a proprietary application logic.

This separation creates a "Split-Brain" problem. The data engineering team (using Iceberg) cannot see the vector data. The AI team (using vectors) cannot easily join their results with business dimensions in the analytics lake. **Lance Namespace** is the architectural solution to this schism. It is a specification and set of adapters that allow Lance datasets to "live inside" standard metadata catalogs.

### **3.2. Architecture of Lance Namespace with Iceberg REST**

When configuring Lance Namespace to use an **Iceberg REST Catalog**, the system employs a "Companion Table" mechanism. This is a sophisticated masquerade that allows the Lance data to be managed by Iceberg without forcing the data into the less-optimal Parquet format.

#### **3.2.1. The Physical vs. Logical Layout**

* **Physical Layer (R2):** The Lance data files (.lance), indices, and fragments are written to Cloudflare R2. For example: r2://my-data-lake/vectors/contracts/.  
* **Logical Layer (Iceberg REST):** The Lance Namespace implementation registers a table in the Iceberg catalog. However, this is not a standard Iceberg table.  
  * **Dummy Schema:** The registered Iceberg table often contains a placeholder schema (e.g., a single column dummy\_lance\_placeholder string). This satisfies the Iceberg requirement that a table must have a schema.  
  * **Table Properties as Pointers:** The integration relies heavily on **Iceberg Table Properties**. It sets specific keys that identify the table's true nature:  
    * table\_type: Set to lance.10  
    * lance\_location: Points to the R2 URI of the Lance dataset.  
    * lance\_schema: May cache the JSON representation of the actual Lance schema (vectors, blobs, metadata).

#### **3.2.2. The Resolution Workflow**

When a client application interacts with this setup:

1. **Discovery:** The client (e.g., Ibis or a Python script) asks the Iceberg Catalog for the table contracts.  
2. **Interception:** The Lance Namespace client (wrapping the connection) inspects the returned metadata. It sees table\_type=lance.  
3. **Redirection:** Instead of trying to read the table as an Iceberg/Parquet table, the client "mounts" the data found at lance\_location using the native Lance reader.

This architecture ensures that **Iceberg is the Single Source of Truth** for *existence, access control, and ownership*, while **Lance is the Storage Format** for *performance and vector capabilities*.

### **3.3. Strategic Implementation for "Serving PDFs and Embeddings"**

The user's specific requirement is to store and serve PDF files and their embeddings. The optimal strategy utilizes Lance's multimodal capabilities, specifically its efficiency with **Binary Large Objects (BLOBs)**.

#### **3.3.1. The "Fat Table" Schema Strategy**

Traditional architectures utilize a "Pointer Strategy": storing the PDF in S3, getting a URL, and storing the URL \+ Embedding in the database.

* **Drawback:** This creates an "N+1" query problem during retrieval. To serve the top 5 relevant documents, the application must (1) Query the vector DB (1 request), receive 5 URLs, and then (2) Make 5 separate HTTP requests to S3 to fetch the content.

**The Lance Recommendation:** Use a "Fat Table" schema where the PDF binary blob is stored *directly* in the Lance column.  
**Proposed Ibis/Lance Schema:**

Python

import pyarrow as pa

schema \= pa.schema()

Why this works on R2 with Lance:  
Lance is a fragment-based columnar format. Unlike Parquet, which must decompress and scan entire row groups, Lance supports O(1) random access to specific row IDs.

1. **Retrieval Efficiency:** When a vector search identifies the top K matches, Lance can perform a **Projection** to retrieve *only* the pdf\_blob column for those K rows.  
2. **Ranged Reads:** The Lance reader issues HTTP Range requests to R2. It does not download the whole file; it downloads only the bytes corresponding to the specific PDFs required.  
3. **Consolidated I/O:** This effectively reduces the "N+1" problem to a single (or very few) parallelized storage requests, drastically reducing latency for the user.

#### **3.3.2. Configuring the Lance Namespace with Iceberg REST and R2**

This section details the specific configuration required to wire these components together. The user must configure the Lance client to authenticate with both the Iceberg REST service (for metadata) and Cloudflare R2 (for data).  
**Python Configuration Pattern:**

Python

import lance  
from lance.namespace import connect

\# 1\. R2 Storage Configuration (S3-Compatible)  
\# These options tell Lance how to talk to Cloudflare R2  
storage\_options \= {  
    "s3\_endpoint\_override": "https://\<ACCOUNT\_ID\>.r2.cloudflarestorage.com",  
    "region": "auto",  
    "aws\_access\_key\_id": "\<R2\_ACCESS\_KEY\_ID\>",  
    "aws\_secret\_access\_key": "\<R2\_SECRET\_ACCESS\_KEY\>",  
    "allow\_http": "true", \# Required if bridging via certain proxies, otherwise false for R2  
    "timeout": "60s"  
}

\# 2\. Iceberg REST Catalog Configuration  
\# This tells Lance where to find the metadata  
catalog\_uri \= "https://\<ICEBERG\_REST\_URL\>/v1"  
warehouse\_path \= "r2://\<BUCKET\_NAME\>/lance-warehouse"

\# 3\. Connect to the Namespace  
\# This object 'ns' becomes the handle to create/manage tables  
ns \= connect(  
    "iceberg",   
    uri=catalog\_uri,   
    warehouse=warehouse\_path,   
    storage\_options=storage\_options  
)

\# 4\. Creating the Table (DDL)  
\# This registers the table in Iceberg AND creates the physical artifacts in R2  
tbl \= ns.create\_table(  
    "pdf\_documents",  
    schema=schema,  
    mode="create"   
)

### **3.4. Bridging Lance Namespace and Ibis/DuckDB**

The final piece of the integration puzzle is making these Lance tables accessible to **Ibis**. Ibis does not currently have a native "Lance Namespace" backend. Instead, we utilize the **Ibis DuckDB Backend**.  
The Integration Pattern: "Resolve and Register"  
Since DuckDB has a native lance extension (capable of reading .lance files) but may not yet automatically traverse the Iceberg/Lance-Namespace redirection link transparently, the application layer must bridge this gap.

1. **Resolve:** The application uses the lance.namespace client (as shown above) to look up the table pdf\_documents. The client returns the physical R2 URI (r2://.../data.lance).  
2. **Register:** The application registers this URI as a **View** or **Scanner** in the DuckDB connection used by Ibis.

Python

\#... assuming 'ns' is connected as above...

\# 1\. Resolve logical name to physical dataset  
lance\_table \= ns.open\_table("pdf\_documents")  
physical\_uri \= lance\_table.uri 

\# 2\. Setup Ibis with DuckDB  
import ibis  
con \= ibis.duckdb.connect()

\# 3\. Install Lance Extension in DuckDB  
con.raw\_sql("INSTALL lance; LOAD lance;")

\# 4\. Register the dataset as a View  
\# Note: We must pass the S3/R2 credentials to DuckDB as well  
con.raw\_sql(f"""  
    CREATE SECRET r2\_secret (  
        TYPE R2,  
        KEY\_ID '{r2\_key\_id}',  
        SECRET '{r2\_secret}',  
        ACCOUNT\_ID '{r2\_account\_id}'  
    );  
""")

\# Register the view using the lance\_scan function  
con.raw\_sql(f"CREATE VIEW pdf\_docs\_view AS SELECT \* FROM lance\_scan('{physical\_uri}');")

\# 5\. Ibis Object Creation  
\# Now Ibis treats it as a native table  
docs \= con.table("pdf\_docs\_view")

\# 6\. Usage: Ibis executes SQL, DuckDB scans Lance on R2  
result \= docs.filter(docs.file\_name.like("%.pdf")).execute()

This pattern provides the best of both worlds: the governance of the Namespace/Catalog and the fluid query API of Ibis.

## ---

**4\. Workflows: The Life of a PDF**

To further elucidate the stack's operation, we will trace the lifecycle of a PDF file through ingestion, storage, and serving.

### **4.1. Ingestion Workflow (Write Path)**

The write path is designed for **Concurrency** and **Atomicity**, leveraging the Iceberg REST catalog to manage state.

1. **Upload & Trigger:** A user uploads a file to the application.  
2. **Vectorization Worker:** A background worker (using Python/Ray) picks up the file. It extracts text and generates an embedding (e.g., using OpenAI or a local BERT model).  
3. **Constructing the Record:** The worker creates an Arrow RecordBatch containing:  
   * id: Generated UUID.  
   * pdf\_blob: The raw bytes of the file.  
   * vector: The computed embedding.  
   * metadata: JSON object with user\_id, timestamp, etc.  
4. **Lance Commit:** The worker calls ns.open\_table("documents").add(batch).  
   * **Phase 1 (Write):** The Lance writer writes new data fragments (files) to R2. These are invisible to readers.  
   * **Phase 2 (Commit):** The Lance client contacts the **Iceberg REST Catalog**. It attempts to swap the metadata pointer to include the new fragments.  
   * **Concurrency:** If multiple workers invoke this simultaneously, the Iceberg Catalog (backed by a database like Postgres) serializes the commits. One will succeed; the other will retry. This guarantees ACID compliance on object storage.12

### **4.2. Serving Workflow (Read Path)**

The read path optimizes for **Low Latency** using R2 and Lance’s random access capabilities.

1. **Request:** User asks "Show me contracts related to NDA."  
2. **Vector Search:** The application generates a query vector for "contracts related to NDA."  
3. **LanceDB Query:**  
   * The application connects to the Lance dataset.  
   * It executes a vector search: .search(query\_vector).limit(5).  
   * **Index Usage:** It utilizes the IVF-PQ index (stored in R2, cached locally on the compute node) to find the nearest neighbors.  
4. **Blob Retrieval:**  
   * The search returns 5 Row IDs.  
   * The query includes a request for the pdf\_blob column.  
   * **Ranged Read:** The Lance reader calculates the exact byte offsets of the blobs in the R2 files. It sends 5 parallel HTTP GET Range requests to R2.  
5. **Response:** The application receives the PDF bytes and streams them to the user.

## ---

**5\. Comparative Analysis: DuckLake vs. Iceberg REST**

The user's stack includes both **DuckLake** and **Iceberg REST**. A critical architectural decision is determining *when* to use which, as having two catalogs can lead to fragmentation.

| Feature | DuckLake | Iceberg REST (with Lance Namespace) | Recommendation for this Stack |
| :---- | :---- | :---- | :---- |
| **Primary Engine** | MotherDuck / DuckDB | Spark / Trino / LanceDB |  |
| **Metadata Storage** | SQL Database (MotherDuck managed) | JSON/Avro Files (standard spec) |  |
| **Write Latency** | **Low** (Data Inlining for small inserts) | **Higher** (File rotation required) | Use **DuckLake** for high-velocity logs (e.g., clickstream, access logs). |
| **Vector Support** | Limited (via Extensions) | **First-Class** (via Lance Namespace) | Use **Iceberg/Lance** for AI data (PDFs, Embeddings). |
| **Interoperability** | DuckDB Ecosystem primarily | Universal (Standard open format) | Use **Iceberg** for data shared with external teams/tools. |

Synthesis Strategy:  
The report recommends a Hybrid Catalog Strategy:

* **Operational Analytics:** Use **DuckLake** for tables that are primarily generated and queried by MotherDuck (e.g., aggregated usage metrics, session logs). DuckLake's "Data Inlining" feature 6 is superior for streaming small updates.  
* **AI Assets:** Use **Iceberg REST** hosting the **Lance Namespace** for the documents and embeddings tables. This adheres to the open standard for the AI assets, ensuring they are future-proof and accessible to other tools (like Spark for bulk training).  
* **Unified View:** Use Ibis \+ DuckDB to create a "Virtual Data Warehouse" that joins tables from both catalogs seamlessly.

## ---

**6\. Integrating PlanetScale and MotherDuck**

The relationship between PlanetScale (OLTP) and MotherDuck (OLAP) is the bridge between the application state and the data intelligence.

### **6.1. The pg\_duckdb Extension**

The inclusion of pg\_duckdb in the stack is pivotal. It allows the PlanetScale Postgres database to become an analytical query initiator.

* **Mechanism:** pg\_duckdb embeds a DuckDB instance inside the Postgres worker process.  
* **Capability:** It can read from MotherDuck.  
* **Workflow:**  
  1. Application writes a user subscription update to PlanetScale users table.  
  2. Analyst wants to see "Average PDF downloads per Premium User."  
  3. **Query:**  
     SQL  
     \-- Executed in PlanetScale  
     SELECT u.subscription\_tier, AVG(d.download\_count)  
     FROM public.users u  
     JOIN motherduck.analytics.daily\_downloads d ON u.id \= d.user\_id  
     GROUP BY u.subscription\_tier;

  4. **Execution:** Postgres handles the users scan. pg\_duckdb pushes the daily\_downloads aggregation to MotherDuck's cloud. The reduced result is returned to Postgres for the final join.  
  * **Performance:** Benchmarks indicate that offloading the analytical portion to MotherDuck via this extension can be **99% faster** than running the analysis in native Postgres, while avoiding resource contention on the transactional primary.4

## ---

**7\. Operationalizing the Stack on R2**

### **7.1. R2 Data Catalog vs. Self-Hosted Iceberg**

Cloudflare has recently introduced the **R2 Data Catalog** (in beta), which essentially provides a managed Iceberg REST endpoint for buckets.9

* **Recommendation:** For this stack, the user should prioritize using the **R2 Data Catalog** if available, as it removes the need to self-host an Iceberg REST service (e.g., Tabular or a Docker container).  
* **Configuration:** The Lance Namespace connection string would simply point to the R2 Data Catalog endpoint provided by Cloudflare, simplifying the infrastructure complexity significantly.

### **7.2. Caching Strategy**

Serving PDFs via Lance on R2 relies on network I/O.

* **Tiered Cache:** Enable **Smart Tiered Cache** on the R2 bucket. This helps adjacent requests for the same PDF fragments hit Cloudflare’s regional caches rather than the R2 origin, reducing latency.13  
* **Local NVMe:** For the compute nodes running LanceDB/DuckDB, ensure they have fast local NVMe storage. Lance leverages local disk to cache the **Vector Index**. A "cold" search (fetching index from R2) can take hundreds of milliseconds; a "warm" search (index on local NVMe) takes milliseconds.14

## ---

**8\. Conclusion and Future Outlook**

The proposed architecture represents a sophisticated, future-proof approach to the **AI Data Lakehouse**. By leveraging **Ibis** as the orchestrator, it achieves code portability. By utilizing **PlanetScale** and **MotherDuck**, it optimally segments transactional and analytical workloads while maintaining query interoperability.  
Most importantly, the strategic deployment of **Lance Namespace** transforms the handling of unstructured data. It elevates PDF documents and embeddings from "files in a bucket" to structured, governed, and queryable assets within the **Iceberg** catalog ecosystem. This allows for a system where a user's subscription status, their download history, and the semantic content of their documents can be queried and joined in a single, high-performance request—a capability that defines the next generation of intelligent applications.  
The successful implementation of this stack relies not on monolithic tooling, but on the disciplined integration of these composable parts, glued together by the open standards of Arrow, Lance, and the Iceberg REST protocol.

#### **Works cited**

1. Integration with Ibis \- DuckDB, accessed December 24, 2025, [https://duckdb.org/docs/stable/guides/python/ibis](https://duckdb.org/docs/stable/guides/python/ibis)  
2. DuckDB \- LanceDB, accessed December 24, 2025, [https://lancedb.com/docs/integrations/platforms/duckdb/](https://lancedb.com/docs/integrations/platforms/duckdb/)  
3. Reading and Writing Parquet Files \- DuckDB, accessed December 24, 2025, [https://duckdb.org/docs/stable/data/parquet/overview](https://duckdb.org/docs/stable/data/parquet/overview)  
4. MotherDuck Integrates with PlanetScale Postgres, accessed December 24, 2025, [https://motherduck.com/blog/motherduck-planetscale-integration/](https://motherduck.com/blog/motherduck-planetscale-integration/)  
5. accessed December 24, 2025, [https://motherduck.com/docs/integrations/file-formats/ducklake/\#:\~:text=1%20through%201.4.,files%20and%20a%20SQL%20database.](https://motherduck.com/docs/integrations/file-formats/ducklake/#:~:text=1%20through%201.4.,files%20and%20a%20SQL%20database.)  
6. DuckLake | MotherDuck Docs, accessed December 24, 2025, [https://motherduck.com/docs/integrations/file-formats/ducklake/](https://motherduck.com/docs/integrations/file-formats/ducklake/)  
7. PlanetScale Postgres, accessed December 24, 2025, [https://planetscale.com/docs/postgres](https://planetscale.com/docs/postgres)  
8. Using MotherDuck with PlanetScale, accessed December 24, 2025, [https://planetscale.com/blog/using-motherduck-with-planetscale](https://planetscale.com/blog/using-motherduck-with-planetscale)  
9. R2 Data Catalog: Managed Apache Iceberg tables with zero egress fees, accessed December 24, 2025, [https://blog.cloudflare.com/r2-data-catalog-public-beta/](https://blog.cloudflare.com/r2-data-catalog-public-beta/)  
10. Apache Iceberg REST Catalog \- Lance, accessed December 24, 2025, [https://lance.org/format/namespace/integrations/iceberg/](https://lance.org/format/namespace/integrations/iceberg/)  
11. lance-format/lance-namespace: Lance Namespace is an ... \- GitHub, accessed December 24, 2025, [https://github.com/lance-format/lance-namespace](https://github.com/lance-format/lance-namespace)  
12. Writing to LanceDB in cloud object storage while other processes are reading? \#1888, accessed December 24, 2025, [https://github.com/lancedb/lancedb/discussions/1888](https://github.com/lancedb/lancedb/discussions/1888)  
13. Public buckets · Cloudflare R2 docs, accessed December 24, 2025, [https://developers.cloudflare.com/r2/buckets/public-buckets/](https://developers.cloudflare.com/r2/buckets/public-buckets/)  
14. Storage Architecture in LanceDB, accessed December 24, 2025, [https://lancedb.com/docs/storage/](https://lancedb.com/docs/storage/)

---

## From BI to AI  A Modern Lakehouse Stack with Lance and Iceberg

*Source: `docs/bunchloch/teanga/From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md` (2766 words, 157 lines)*

---
title: "From BI to AI: A Modern Lakehouse Stack with Lance and Iceberg"
source: "https://lancedb.com/blog/from-bi-to-ai-lance-and-iceberg/"
author:
  - "[[[Jack Ye Prashanth Rao]]]"
published: 2025-11-24
created: 2025-12-26
description: "A comparison of where Iceberg and Lance sit in the modern lakehouse stack. We highlight emerging architectures that are bridging the worlds of analytics and …"
tags:
  - "clippings"
---
The modern, composable data stack has evolved around the idea of the *lakehouse* — a unified system that blends the flexibility of data lakes (i.e., object stores designed to hold data in open file formats) with the analytical performance and reliability of data warehouses. Projects like [Apache Iceberg](https://iceberg.apache.org/) have been pivotal in making this vision a reality, offering transactional guarantees and schema evolution at scale.

But as AI and machine learning workloads bring with them ever larger amounts of data from multiple modalities (e.g., text, images, audio, video, sensor data), newer formats like [Lance](https://lance.org/) are emerging to take the next leap forward. Lance is a high-performance columnar format that’s purpose-built for AI/ML workloads (training, feature engineering) and multimodal data at petabyte scale.

The goal of this post is to explain where Iceberg and Lance fit in the modern lakehouse stack, while discussing some of their key differences. We’ll highlight emerging data architectures that are bridging the worlds of analytics and AI/ML workloads using these two formats, all built on the same data foundation.

## Understanding the modern lakehouse stack

The modern lakehouse architecture consists of six distinct technological layers, each serving a specific purpose. Let’s dissect these layers (from the bottom up) to understand where Lance and Iceberg fit in, and how they can work together.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/lakehouse_stack.png)

### Object store

At the foundation of the lakehouse lies the **object store** — these are storage systems characterized by their simple, object-based hierarchy, typically providing high durability guarantees with HTTP-based communication for data transfer.

### File format

The **file format** describes how a single file should be stored on disk. This is where formats like Lance, Parquet, ORC, and Avro are present. The file format defines the internal structure, encoding, and compression of individual data files.

### Table format

The **table format** describes how multiple files work together to form a logical table. Table formats must include features like transactional commits and read isolation, so that multiple writers and readers can safely operate against the same table.

### Catalog spec

The **catalog spec** defines how any system can discover and manage a collection of tables within storage. It acts as the bridge between the storage layer and the compute layer of the stack (starting with the catalog *service*, more on this below).

### Catalog service

A **catalog service** offers easy connectivity to the compute engines on top, and implements one or more catalog specs to provide both table metadata and, optionally, continuous background maintenance (compaction, optimization, index updates) that table formats require to stay performant.

### Compute engine

The **compute engine** is the workhorse built on top of catalog services that leverage their awareness of catalog specs, table formats and file formats to perform complex data workflows. Compute engines are carefully designed to handle a variety of workloads, including SQL queries, analytics processing, vector search, full-text search, machine learning training.

## Differences between Lance and Iceberg

The key insight from the lakehouse architecture described above is that the file format, table format, and catalog spec layers are just **storage** specifications. **Compute power** resides only in the object store, catalog services, and compute engine layers. This clear separation of concerns is what allows lakehouse storage to be flexible, portable, and independently scalable, while opening up the same underlying data for discovery by any catalog service, and for processing by any compatible compute engine.

Iceberg operates at **two of the layers** in the stack: the table format and the catalog spec. It typically uses Parquet as the underlying file format.

Lance spans **three layers of the stack**, because it’s simultaneously a file format, table format *and* a catalog spec.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/lance_and_iceberg.png)

In the sections below, we’ll compare and contrast Lance and Iceberg at each of these layers.

### Table format

Iceberg employs a **three-level** metadata hierarchy in its table format: a table metadata file → manifest list → manifest files. The table metadata (a JSON file) rolls up a comprehensive history of past commits and schemas, and stores the partition specs, snapshot references and table properties. Each snapshot points to a manifest list (Avro) that contains metadata about manifest files and partition statistics (also Avro), and the manifests contain lists of data files that sit in the object store. Note that the Iceberg table format itself does not define how to atomically commit data — instead, it just describes the latest table metadata location, and it’s left to the catalog service to determine how to actually do the commit.

Lance employs a **single-level** metadata hierarchy, with one manifest file per table version. Lance tables use the notion of *fragments*, rather than partitions. Each commit to a Lance table produces a new manifest file that contains fragments (each with their own data and deletion files) and pointers to the index files (for FTS, vector and other scalar indexes).

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/table_format.png)

### File format

Iceberg supports multiple file formats under the hood. Parquet is the most prevalent and widely used, but Avro and ORC formats are also supported.

From a file format perspective, Lance does away with row groups (unlike Parquet, which heavily relies on them), achieving a high degree of parallelism, achieving 100x the random access performance of Parquet without sacrificing scan performance. There are several other differences between Lance and Parquet that won’t be discussed here, but you can read more about it in this VLDB 2025 paper: [Efficient Random Access in Columnar Storage through Adaptive Structural Encodings](https://arxiv.org/html/2504.15247v1).

### Catalog spec

Because of the way Iceberg delegates the actual atomic write guarantees to arbitrary catalog services, over the years there have been many protocols developed by the vendors building these catalog services. Iceberg’s “REST Catalog spec” was developed as a wrapper to standardize these different protocols, and any catalog service adopting the spec is required to guarantee the atomicity of the API operation.

Lance uses “namespaces”, rather than explicitly defining a catalog spec. In fact, Lance intentionally names it “Lance Namespace” rather than “Lance Catalog”, because it’s a thin wrapper to allow storing and managing a Lance table via any catalog service, and is not aimed to be a complete catalog spec. In the future, to provide a full catalog spec experience, Lance aims to use Arrow Flight gRPC as its main standard, to be compatible with Lance’s vision of being an “Arrow-native lakehouse format”.

## When Lance is beneficial

In this section, we’ll list the key benefits of using Lance over Iceberg, especially for AI/ML workloads.

Earlier generations of open table formats (Iceberg, Delta Lake and Hudi) were primarily designed as replacements for Hive. They focus mainly on data warehouse (OLAP) workloads, with tables that are typically “long but narrow”.

Lance, on the other hand, is designed from the ground up to support machine learning and AI workloads, with fundamentally different access patterns and support for tables that are “ [long and wide](https://lancedb.com/blog/lance-v2/#very-wide-schemas) ” (e.g., embeddings, blobs and deeply nested data in columns). Lance can index [billions of vectors in hours](https://lancedb.com/blog/case-study-netflix/), storing tens of petabytes of data. For vector search, it can support more than 10,000 QPS with [<50 ms latency](https://lancedb.com/docs/enterprise/benchmark/) over object storage. For ML training, Lance integrates with PyTorch and JAX data loaders, achieving (through a distributed cache fleet) more than 5 million IOPS from NVMe SSDs.

Combining fast random access with native indexes within the same format is what gives Lance a significant advantage in ML and AI use cases, compared to scan-based approaches that are common in traditional lakehouses relying on Iceberg.

### Multimodal data done right

Multimodal data (images, videos, audio, deeply nested point clouds and their associated embeddings) is becoming more and more common, especially in the age of AI, where it’s never been easier to generate and consume huge amounts of data.

In many Iceberg deployments today, multimodal data is modeled as columns in tables (like any other tabular data), with pointers to the actual data located in object storage. This isn’t ideal from a data governance perspective, because organizations would need separate access control layers and extra operational plumbing across various systems. It’s also not ideal from a performance perspective, because there is additional I/O and network overhead while fetching individual data items.

Lance’s file format makes it more convenient to maintain multimodal data natively as blobs inside the columns, with no external lookups (the multimodal data is co-located with metadata and embeddings), thus simplifying governance and management of data that’s multimodal in nature. It’s also significantly more performant, because at the table level, Lance can pack multiple smaller rows together while storing very large rows (e.g., image or audio blobs) in a dedicated file thanks to its fragment-based design, thus balancing performance with storage size.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/multimodal_lakehouse.png)

### Flexible, zero-cost data evolution

A common need as the dataset scales in size is **data evolution,** i.e., changes to the table schema and adding, updating or removing columns and their associated data. These types of operations are especially common in ML/AI applications, where multiple developers working in parallel frequently add features, predictions or embeddings as new columns to an existing table. In Iceberg, data evolution comes with a non-trivial cost — adding data to a new column requires a **full table rewrite** since Parquet stores entire row groups together. This means that for very large tables, it’s common to see multiple new feature columns being added in parallel by multiple teams in an organization – which would require a table lock as new columns are being added, bottlenecking the feature engineering process.

In Lance, adding a new column **is essentially a zero-copy operation**. Lance’s fragment design allows independent column files per fragment (though multiple columns can share a data file), meaning that adding or updating a column simply appends new column files without touching existing data. This avoids duplication on petabytes of data, as noted by [Netflix](https://lancedb.com/blog/case-study-netflix) as they built out their media data lake incorporating LanceDB.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/data_evolution.png)

The space savings can be tremendous – say you have an existing table that’s 100 GB in size. If you update the table schema and add a new column that’s only 1% this size (1 GB) – in Iceberg, performing a backfill operation on the new column would require a **full table copy** amounting to 101 GB of writes. In LanceDB, it would just be 1 GB of writes. The larger the dataset, the more this matters. The ability to continuously or incrementally add features, without duplicating or rewriting unaffected data, makes Lance a compelling choice for teams working with petabytes of data.

## When Iceberg is beneficial

Iceberg’s partition-based, catalog-centric approach can still be beneficial for traditional BI or analytics workloads, for the reasons listed below. In this section, we’ll highlight some of them, as well as how Lance aims to address them in future versions.

### Optimized for analytical workloads

Iceberg’s hidden partitioning logic and its three-level metadata hierarchy enable efficient partition pruning for compute engines that are optimized for analytics workloads, where queries are naturally filtered on partition keys. Lance, in contrast, uses fragments (rather than partitions) as the organizational unit for data, so at present, the way Lance organizes data doesn’t fit well with traditional OLAP-style compute engines that are heavily optimized for partition-based scans.

Newer methods like [liquid clustering](https://docs.databricks.com/aws/en/delta/clustering) (developed by Databricks) can, in the future, actively leverage Lance’s features, because they avoid hard-coded table layouts and adopt an adaptive clustering approach that’s optimized based on actual query patterns. However, partitioning is a concept that’s deeply baked into current-generation query engines, so until liquid clustering gains wider adoption in the ecosystem, Iceberg has several advantages for analytics workloads.

### Mature ecosystem integration

Iceberg has years of battle-hardening from production usage and is well-integrated with a mature ecosystem, including integrations with several compute engines and catalog services. In contrast, Lance’s compute engine integrations are still emerging (primarily Spark and Ray at present), with many more upcoming and in their nascent stages. There is strong community interest in adding Lance support to popular compute engines that are part of the Iceberg ecosystem, including Flink, StarRocks, and Trino. Expect this space to evolve over time.

### Centralized observability

Iceberg’s catalog-dependent design means the catalog is aware of *all* table operations, enabling centralized monitoring and powerful automated optimization triggers. It also enable an easy-to-maintain unified audit log across all tables, with coordinated data lineage tracking.

Lance tables, like Delta Lake, can be **modified directly in storage** without catalog awareness. This storage-first design gives Lance a portability advantage but complicates activity tracking — downstream operations must rely on pull-based polling or storage event notifications (S3 Events, GCS Pub/Sub) rather than semantic catalog events. Lance’s approach to address this is through its managed offering, LanceDB Enterprise (which has knowledge of all read/write traffic), but in the future, there could be ways to onboard all operations onto open observability frameworks like OpenTelemetry for easy tracking in any tool that supports it.

## Takeaways from the comparison

The following table summarizes the reasons Lance is emerging as a **new standard for multimodal data and AI** workloads in the lakehouse.

| Feature | Lance | Iceberg |
| --- | --- | --- |
| **Metadata Structure** | Single-level manifest per version | Three-level hierarchy (metadata → manifest list → manifest) |
| **Metadata Growth** | Independent versions, no rollup | Metadata files accumulate snapshot history |
| **Data Organization** | Fragments (horizontal slices), global clustering/sorting | Partition specs with hidden partitioning, clustering/sorting within partition |
| **Row Address** | 64-bit addresses (fragment\_id + offset) | file path + position tuple |
| **File Format** | Lance file format | Parquet/ORC/Avro |
| **Index Support** | Vector and full-text index, plus a standardized framework for new scalar index specifications | Puffin for simple NDV sketch, deletion vector |

Parquet and Iceberg, developed independently (in their own time frames), have led to an explosion of connectors, integrations and innovations up and down the layers of the lakehouse stack. However, a lot of these predate the age of AI, where the kinds of workloads and user requirements involved are changing at a blazing pace.

Lance is relatively new, and so it has had the opportunity to build and iterate rapidly from the ground up while learning from the successes and existing pain points of Iceberg/Parquet. The design features of Lance, as can be seen in the table above, incorporate several proven patterns while introducing new paradigms that aim to address the unique requirements of AI/ML workloads. Lance users can seamlessly interoperate across the various ML and data processing frameworks, from Pandas and Polars, to PyTorch and beyond.

## A unified data platform with Lance and Iceberg

Looking at the trade-offs involved when choosing between Lance and Iceberg, especially for analytics vs. ML/AI workloads, we’re seeing a dual-format strategy in which large organizations are beginning to adopt Lance. Companies like Netflix are now [adopting LanceDB](https://lancedb.com/blog/case-study-netflix/) for their AI and multimodal workloads alongside Iceberg, which has long been their primary table format for BI and analytics workloads.

The figure below envisions how a unified lakehouse platform built on top of Lance and Iceberg might look, as more organizations build out their lakehouses on top of modern infrastructure. The unification occurs at the compute layers both above (catalog services and compute engines) and below (i.e., the object stores) the storage formats.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/unified_lakehouse_platform.png)

Existing catalog specifications and metadata services like Glue, Hive metadata store (HMS), Unity REST catalog and Polaris are already integrated with Lance via [lance-namespace](https://lance.org/format/namespace/impls/), an open specification built on top of Lance that standardizes access to a collection of Lance tables. On the compute engine side, there are numerous integrations in the [Lance format](https://github.com/lance-format) ecosystem (such as `lance-ray`, `lance-spark`, etc.) that are gaining adoption in open source. The main takeaway from this section is that developers who do not want the burden of maintaining multiple catalog services can choose to build on top of Lance and leveraging its integration to the compute ecosystem, while developers who are already using Iceberg can interplay with Lance for use cases that benefit from the Lance format.

These emerging architectural patterns and open source projects reflect a broader trend: managing the separate needs of analytics and AI workloads with two distinct but interoperable formats — Iceberg for BI, and Lance for AI and multimodal data, bridging the best of both worlds.

---

## Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray

*Source: `docs/bunchloch/meaisínfhoghlaim/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray.md` (1369 words, 376 lines)*

---
title: "Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray"
source: "https://lancedb.com/blog/lance-namespace-lancedb-and-ray"
author:
  - "[[[Jack Ye]]]"
published: 2025-09-04
created: 2025-12-20
description: "Learn how to productionalize AI workloads with Lance Namespace's enterprise stack integration and the scalability of LanceDB and Ray for end-to-end ML …"
tags:
  - "clippings"
---
In our [previous post](https://lancedb.com/blog/introducing-lance-namespace-spark-integration), we introduced [Lance Namespace](https://lance.org/format/namespace/) and its integration with Apache Spark. Today, we’re excited to showcase how to **productionalize your AI workloads** by combining:

- **Lance Namespace** for seamless enterprise stack integration with your existing metadata services
- **Ray** for data ingestion and feature engineering at scale
- **LanceDB** for efficient [vector search](https://docs.lancedb.com/search/vector-search/) and [full‑text search](https://docs.lancedb.com/search/full-text-search/)

This powerful combination enables you to build production-ready AI applications that integrate with your existing infrastructure while maintaining the scalability needed for real-world deployments.

## What’s New

### Lance–Ray Integration

The [lance-ray](https://pypi.org/project/lance-ray/) package has now evolved into its own independent subproject, bringing seamless integration between Ray and Lance. It enables distributed read, write, and data evolution operations on Lance datasets using Ray’s parallel processing capabilities, making it simple to handle large-scale data transformations and feature engineering workloads across your compute cluster.

### Lance Namespace Python and Rust SDKs

Lance Namespace now provides native Python and Rust SDKs that enable seamless enterprise integration across languages. This is what enables integration with both `lance-ray` and LanceDB.

## Building an End-to-End AI Pipeline

Let’s walk through a complete example using real data from Hugging Face to build a question-answering system. We’ll use the [BeIR/quora](https://huggingface.co/datasets/BeIR/quora) dataset to demonstrate the entire workflow.

### Step 1: Setting Up the Environment

First, install the required packages:

code

```fallback
pip install lance-ray sentence-transformers datasets

pip install --no-deps lancedb==0.25.0

pip install --no-deps lance-namespace==0.0.14
```

Initialize your Ray cluster and import the necessary libraries:

python

```python
import ray

import pyarrow as pa

from lance_ray import write_lance, read_lance, add_columns

from datasets import load_dataset

from sentence_transformers import SentenceTransformer

import numpy as np

# Initialize Ray with sufficient resources for parallel processing

ray.init()

# Load the embedding model (we'll use it later)

model = SentenceTransformer('BAAI/bge-small-en-v1.5')
```

### Step 2: Initialize Lance Namespace

Lance Namespace provides a unified interface to store and manage your Lance tables across different metadata services. Depending on your enterprise environment requirements, you can choose from various supported catalog services:

python

```python
import lance_namespace as ln

# Example 1: Directory-based namespace (for development/testing)

namespace = ln.connect("dir", {"root": "./lance_tables"})

# Example 2: Hive Metastore (for Hadoop/Spark ecosystems)

# namespace = ln.connect("hive", {"uri": "thrift://hive-metastore:9083"})

# Example 3: AWS Glue Catalog (for AWS-based infrastructure)

# namespace = ln.connect("glue", {"region": "us-east-1"})

# Example 4: Unity Catalog (for Databricks environments)

# namespace = ln.connect("unity", {"url": "https://your-workspace.cloud.databricks.com"})
```

For this example, we’ll use a directory-based namespace for simplicity, but you can seamlessly switch to any of the above options based on your infrastructure. See the [namespace implementations documentation](https://lance.org/format/namespace/impls) for detailed configuration options of each integrated service.

### Step 3: Distributed Data Ingestion with Ray

Now let’s load the Quora dataset and ingest it into [Lance format](https://docs.lancedb.com/lance/) using Ray’s distributed processing:

python

```python
# Load Quora dataset from Hugging Face

print("Loading Quora dataset...")

dataset = load_dataset("BeIR/quora", "corpus", split="corpus[:10000]", trust_remote_code=True)

# Convert to Ray Dataset for distributed processing

ray_dataset = ray.data.from_huggingface(dataset)

# Define schema with proper types

schema = pa.schema([

    pa.field("_id", pa.string()),

    pa.field("title", pa.string()),

    pa.field("text", pa.string()),

])

# Write to Lance format using namespace

print("Writing data to Lance format via namespace...")

write_lance(

    ray_dataset,

    namespace=namespace,

    table_id=["quora_questions"],

    schema=schema,

    mode="create",

    max_rows_per_file=5000,

)

print(f"Ingested {ray_dataset.count()} documents into Lance format")
```

### Step 4: Feature Engineering with Lance–Ray

Now we’ll use Ray’s distributed processing to generate embeddings for all documents.

python

```python
def generate_embeddings(batch: pa.RecordBatch) -> pa.RecordBatch:

    """Generate embeddings for text using sentence-transformers."""

    from sentence_transformers import SentenceTransformer

    

    # Initialize model (will be cached per Ray worker)

    model = SentenceTransformer('BAAI/bge-small-en-v1.5')

    

    # Combine title and text for better semantic representation

    texts = []

    for i in range(len(batch)):

        title = batch["title"][i].as_py() or ""

        text = batch["text"][i].as_py() or ""

        combined = f"{title}. {text}".strip()

        texts.append(combined)

    

    # Generate embeddings

    embeddings = model.encode(texts, normalize_embeddings=True)

    

    # Return as RecordBatch with fixed-size list field

    return pa.RecordBatch.from_arrays(

        [pa.array(embeddings.tolist(), type=pa.list_(pa.float32(), 384))],

        names=["vector"]

    )

# Add embeddings column using distributed processing with namespace

print("Generating embeddings using Ray...")

add_columns(

    None, # no static URI

    namespace=namespace,

    table_id=["quora_questions"],

    transform=generate_embeddings,

    read_columns=["title", "text"],  # Only read necessary columns

    batch_size=100,  # Process in batches of 100

    concurrency=4,  # Use 4 parallel workers

    ray_remote_args={"num_gpus": 0.25} if ray.cluster_resources().get("GPU", 0) > 0 else {}

)

print("Embeddings generated successfully!")
```

The `add_columns` functionality in Ray allows ML/AI scientists to quickly start feature engineering with a local or remote Ray cluster. For more advanced feature engineering capabilities such as lazy materialization, partial backfill, fault-tolerant execution, check out [LanceDB’s Geneva](https://lancedb.com/docs/geneva/) - our feature engineering framework that provides schema enforcement, versioning, and complex transformations. You can also follow our [multimodal lakehouse tutorial](https://lancedb.com/docs/tutorials/mmlh/) for comprehensive examples.

Now let’s connect to our Lance dataset through [LanceDB](https://docs.lancedb.com/) using the same namespace and perform vector similarity search:

python

```python
import lancedb

from sentence_transformers import SentenceTransformer

# Connect to LanceDB using the same namespace

db = lancedb.connect_namespace("dir", {"root": "./lance_tables"})

table = db.open_table("quora_questions")

# Create [vector index](https://docs.lancedb.com/indexing/vector-index/) for fast similarity search

print("Creating vector index...")

table.create_index(

    metric="cosine",

    vector_column_name="vector",

    index_type="IVF_PQ",

    num_partitions=32,

    num_sub_vectors=48,

)

# Perform vector similarity search

query_text = "How do I learn machine learning?"

model = SentenceTransformer('BAAI/bge-small-en-v1.5')

query_embedding = model.encode([query_text], normalize_embeddings=True)[0]

vector_results = (

    table.search(query_embedding, vector_column_name="vector")

    .limit(5)

    .to_pandas()

)

print("\n=== Vector Search Results ===")

print(f"Query: {query_text}\n")

for idx, row in vector_results.iterrows():

    print(f"{idx + 1}. {row['title']}")

    print(f"   {row['text'][:150]}...")

    print()
```

Now let’s also do a full text search against the `text` column:

python

```python
print("Creating full-text search index...")

table.create_fts_index("text")

# Example 1: Full‑Text Search

keyword_results = (

    table.search("machine learning algorithms", query_type="fts")

    .limit(5)

    .to_pandas()

)

print("\n=== Full-Text Search Results ===")

print("Keywords: 'machine learning algorithms'\n")

for idx, row in keyword_results.iterrows():

    print(f"{idx + 1}. {row['title']}")

    print(f"   {row['text'][:150]}...")

    print()
```

### Step 7: Beyond the Examples

Now, you can continue playing around with the dataset. You can add more feature columns with python functions through Ray. LanceDB also allows [hybrid search](https://docs.lancedb.com/search/hybrid-search/) that combines the semantic understanding of [vector search](https://docs.lancedb.com/search/vector-search/) with the precision of [keyword matching](https://docs.lancedb.com/search/full-text-search/). You can also load data into tools like PyTorch and LangChain for other AI activities.

## Real-World Use Cases

This integration pattern is particularly powerful for:

1. **RAG Applications**: Ingest documents, generate embeddings, and serve semantic search
2. **Recommendation Systems**: Process user interactions and build vector indices at scale
3. **Multimodal Search**: Process images and text together using Ray’s distributed computing
4. **Feature Stores**: Transform and store ML features with versioning via Lance Namespace
5. **Real-time Analytics**: Combine batch processing with low-latency search

## Getting Started Today

Ready to scale your AI workloads? Here’s how to get started:

1. **Install the packages**: `pip install lance-ray lancedb`
2. **Read the documentation**: [Lance–Ray](https://lance.org/integrations/ray/), [LanceDB](https://docs.lancedb.com/), [Vector Search](https://docs.lancedb.com/search/vector-search/), [Full‑Text Search](https://docs.lancedb.com/search/full-text-search/), [Hybrid Search](https://docs.lancedb.com/search/hybrid-search/), [Vector Indexing](https://docs.lancedb.com/indexing/vector-index/), [FTS Indexing](https://docs.lancedb.com/indexing/fts-index/), [Filtering](https://docs.lancedb.com/search/filtering/), [Reranking](https://docs.lancedb.com/reranking/), [Quickstart](https://docs.lancedb.com/tables/), [LanceDB Geneva](https://docs.lancedb.com/geneva/)
3. **Join the community**: [Discord](https://discord.gg/zMM32dvNtd) and [GitHub Discussions](https://github.com/lancedb/lance/discussions)

## Thank You to Our Contributors

We’d like to extend our heartfelt thanks to the community members who have contributed to making this integration a reality, shoutout to:

- **Enwei Jiao** from Luma AI
- **Bryan Keller** from Netflix
- **Jay Narale** from Uber
- **Jay Ju** from ByteDance
- **Jiebao Xiao** from Xiaomi

Your contributions, feedback, and real-world use cases have been instrumental in shaping this integration to meet the needs of production AI workloads.

## Conclusion

The combination of [Lance Namespace](https://lance.org/format/namespace/), Ray, and [LanceDB](https://docs.lancedb.com/) provides a complete solution for productionalizing AI workloads. [Lance Namespace](https://lance.org/format/namespace/) ensures seamless integration with your existing enterprise metadata services, Ray delivers the distributed computing power needed for data ingestion and feature engineering at scale, and LanceDB provides efficient [vector search](https://docs.lancedb.com/search/vector-search/), [full‑text search](https://docs.lancedb.com/search/full-text-search/), and [hybrid search](https://docs.lancedb.com/search/hybrid-search/) capabilities for serving your AI applications.

This integrated approach bridges the gap between experimentation and production, enabling you to build AI systems that not only scale but also fit naturally into your existing infrastructure. Get started with the [Quickstart](https://docs.lancedb.com/quickstart/) or explore [indexing](https://docs.lancedb.com/indexing/vector-index/) options.

Whether you’re building a [RAG system](https://docs.lancedb.com/tutorials/agents/), recommendation engine, or [multimodal search](https://docs.lancedb.com/tutorials/agents/multimodal-agent) application, this powerful trio gives you the enterprise integration, scalability, and performance you need for production deployments.

Try it out today and let us know what you build! We’re excited to see how you use [Lance Namespace](https://lance.org/format/namespace/), Ray, and [LanceDB](https://docs.lancedb.com/) to productionalize your AI workloads.

---

## Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray(1)

*Source: `docs/bunchloch/teanga/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray(1).md` (1369 words, 376 lines)*

---
title: "Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray"
source: "https://lancedb.com/blog/lance-namespace-lancedb-and-ray/"
author:
  - "[[[Jack Ye]]]"
published: 2025-09-04
created: 2025-12-23
description: "Learn how to productionalize AI workloads with Lance Namespace's enterprise stack integration and the scalability of LanceDB and Ray for end-to-end ML …"
tags:
  - "clippings"
---
In our [previous post](https://lancedb.com/blog/introducing-lance-namespace-spark-integration), we introduced [Lance Namespace](https://lance.org/format/namespace/) and its integration with Apache Spark. Today, we’re excited to showcase how to **productionalize your AI workloads** by combining:

- **Lance Namespace** for seamless enterprise stack integration with your existing metadata services
- **Ray** for data ingestion and feature engineering at scale
- **LanceDB** for efficient [vector search](https://docs.lancedb.com/search/vector-search/) and [full‑text search](https://docs.lancedb.com/search/full-text-search/)

This powerful combination enables you to build production-ready AI applications that integrate with your existing infrastructure while maintaining the scalability needed for real-world deployments.

## What’s New

### Lance–Ray Integration

The [lance-ray](https://pypi.org/project/lance-ray/) package has now evolved into its own independent subproject, bringing seamless integration between Ray and Lance. It enables distributed read, write, and data evolution operations on Lance datasets using Ray’s parallel processing capabilities, making it simple to handle large-scale data transformations and feature engineering workloads across your compute cluster.

### Lance Namespace Python and Rust SDKs

Lance Namespace now provides native Python and Rust SDKs that enable seamless enterprise integration across languages. This is what enables integration with both `lance-ray` and LanceDB.

## Building an End-to-End AI Pipeline

Let’s walk through a complete example using real data from Hugging Face to build a question-answering system. We’ll use the [BeIR/quora](https://huggingface.co/datasets/BeIR/quora) dataset to demonstrate the entire workflow.

### Step 1: Setting Up the Environment

First, install the required packages:

code

```fallback
pip install lance-ray sentence-transformers datasets

pip install --no-deps lancedb==0.25.0

pip install --no-deps lance-namespace==0.0.14
```

Initialize your Ray cluster and import the necessary libraries:

python

```python
import ray

import pyarrow as pa

from lance_ray import write_lance, read_lance, add_columns

from datasets import load_dataset

from sentence_transformers import SentenceTransformer

import numpy as np

# Initialize Ray with sufficient resources for parallel processing

ray.init()

# Load the embedding model (we'll use it later)

model = SentenceTransformer('BAAI/bge-small-en-v1.5')
```

### Step 2: Initialize Lance Namespace

Lance Namespace provides a unified interface to store and manage your Lance tables across different metadata services. Depending on your enterprise environment requirements, you can choose from various supported catalog services:

python

```python
import lance_namespace as ln

# Example 1: Directory-based namespace (for development/testing)

namespace = ln.connect("dir", {"root": "./lance_tables"})

# Example 2: Hive Metastore (for Hadoop/Spark ecosystems)

# namespace = ln.connect("hive", {"uri": "thrift://hive-metastore:9083"})

# Example 3: AWS Glue Catalog (for AWS-based infrastructure)

# namespace = ln.connect("glue", {"region": "us-east-1"})

# Example 4: Unity Catalog (for Databricks environments)

# namespace = ln.connect("unity", {"url": "https://your-workspace.cloud.databricks.com"})
```

For this example, we’ll use a directory-based namespace for simplicity, but you can seamlessly switch to any of the above options based on your infrastructure. See the [namespace implementations documentation](https://lance.org/format/namespace/impls) for detailed configuration options of each integrated service.

### Step 3: Distributed Data Ingestion with Ray

Now let’s load the Quora dataset and ingest it into [Lance format](https://docs.lancedb.com/lance/) using Ray’s distributed processing:

python

```python
# Load Quora dataset from Hugging Face

print("Loading Quora dataset...")

dataset = load_dataset("BeIR/quora", "corpus", split="corpus[:10000]", trust_remote_code=True)

# Convert to Ray Dataset for distributed processing

ray_dataset = ray.data.from_huggingface(dataset)

# Define schema with proper types

schema = pa.schema([

    pa.field("_id", pa.string()),

    pa.field("title", pa.string()),

    pa.field("text", pa.string()),

])

# Write to Lance format using namespace

print("Writing data to Lance format via namespace...")

write_lance(

    ray_dataset,

    namespace=namespace,

    table_id=["quora_questions"],

    schema=schema,

    mode="create",

    max_rows_per_file=5000,

)

print(f"Ingested {ray_dataset.count()} documents into Lance format")
```

### Step 4: Feature Engineering with Lance–Ray

Now we’ll use Ray’s distributed processing to generate embeddings for all documents.

python

```python
def generate_embeddings(batch: pa.RecordBatch) -> pa.RecordBatch:

    """Generate embeddings for text using sentence-transformers."""

    from sentence_transformers import SentenceTransformer

    

    # Initialize model (will be cached per Ray worker)

    model = SentenceTransformer('BAAI/bge-small-en-v1.5')

    

    # Combine title and text for better semantic representation

    texts = []

    for i in range(len(batch)):

        title = batch["title"][i].as_py() or ""

        text = batch["text"][i].as_py() or ""

        combined = f"{title}. {text}".strip()

        texts.append(combined)

    

    # Generate embeddings

    embeddings = model.encode(texts, normalize_embeddings=True)

    

    # Return as RecordBatch with fixed-size list field

    return pa.RecordBatch.from_arrays(

        [pa.array(embeddings.tolist(), type=pa.list_(pa.float32(), 384))],

        names=["vector"]

    )

# Add embeddings column using distributed processing with namespace

print("Generating embeddings using Ray...")

add_columns(

    None, # no static URI

    namespace=namespace,

    table_id=["quora_questions"],

    transform=generate_embeddings,

    read_columns=["title", "text"],  # Only read necessary columns

    batch_size=100,  # Process in batches of 100

    concurrency=4,  # Use 4 parallel workers

    ray_remote_args={"num_gpus": 0.25} if ray.cluster_resources().get("GPU", 0) > 0 else {}

)

print("Embeddings generated successfully!")
```

The `add_columns` functionality in Ray allows ML/AI scientists to quickly start feature engineering with a local or remote Ray cluster. For more advanced feature engineering capabilities such as lazy materialization, partial backfill, fault-tolerant execution, check out [LanceDB’s Geneva](https://lancedb.com/docs/geneva/) - our feature engineering framework that provides schema enforcement, versioning, and complex transformations. You can also follow our [multimodal lakehouse tutorial](https://lancedb.com/docs/tutorials/mmlh/) for comprehensive examples.

Now let’s connect to our Lance dataset through [LanceDB](https://docs.lancedb.com/) using the same namespace and perform vector similarity search:

python

```python
import lancedb

from sentence_transformers import SentenceTransformer

# Connect to LanceDB using the same namespace

db = lancedb.connect_namespace("dir", {"root": "./lance_tables"})

table = db.open_table("quora_questions")

# Create [vector index](https://docs.lancedb.com/indexing/vector-index/) for fast similarity search

print("Creating vector index...")

table.create_index(

    metric="cosine",

    vector_column_name="vector",

    index_type="IVF_PQ",

    num_partitions=32,

    num_sub_vectors=48,

)

# Perform vector similarity search

query_text = "How do I learn machine learning?"

model = SentenceTransformer('BAAI/bge-small-en-v1.5')

query_embedding = model.encode([query_text], normalize_embeddings=True)[0]

vector_results = (

    table.search(query_embedding, vector_column_name="vector")

    .limit(5)

    .to_pandas()

)

print("\n=== Vector Search Results ===")

print(f"Query: {query_text}\n")

for idx, row in vector_results.iterrows():

    print(f"{idx + 1}. {row['title']}")

    print(f"   {row['text'][:150]}...")

    print()
```

Now let’s also do a full text search against the `text` column:

python

```python
print("Creating full-text search index...")

table.create_fts_index("text")

# Example 1: Full‑Text Search

keyword_results = (

    table.search("machine learning algorithms", query_type="fts")

    .limit(5)

    .to_pandas()

)

print("\n=== Full-Text Search Results ===")

print("Keywords: 'machine learning algorithms'\n")

for idx, row in keyword_results.iterrows():

    print(f"{idx + 1}. {row['title']}")

    print(f"   {row['text'][:150]}...")

    print()
```

### Step 7: Beyond the Examples

Now, you can continue playing around with the dataset. You can add more feature columns with python functions through Ray. LanceDB also allows [hybrid search](https://docs.lancedb.com/search/hybrid-search/) that combines the semantic understanding of [vector search](https://docs.lancedb.com/search/vector-search/) with the precision of [keyword matching](https://docs.lancedb.com/search/full-text-search/). You can also load data into tools like PyTorch and LangChain for other AI activities.

## Real-World Use Cases

This integration pattern is particularly powerful for:

1. **RAG Applications**: Ingest documents, generate embeddings, and serve semantic search
2. **Recommendation Systems**: Process user interactions and build vector indices at scale
3. **Multimodal Search**: Process images and text together using Ray’s distributed computing
4. **Feature Stores**: Transform and store ML features with versioning via Lance Namespace
5. **Real-time Analytics**: Combine batch processing with low-latency search

## Getting Started Today

Ready to scale your AI workloads? Here’s how to get started:

1. **Install the packages**: `pip install lance-ray lancedb`
2. **Read the documentation**: [Lance–Ray](https://lance.org/integrations/ray/), [LanceDB](https://docs.lancedb.com/), [Vector Search](https://docs.lancedb.com/search/vector-search/), [Full‑Text Search](https://docs.lancedb.com/search/full-text-search/), [Hybrid Search](https://docs.lancedb.com/search/hybrid-search/), [Vector Indexing](https://docs.lancedb.com/indexing/vector-index/), [FTS Indexing](https://docs.lancedb.com/indexing/fts-index/), [Filtering](https://docs.lancedb.com/search/filtering/), [Reranking](https://docs.lancedb.com/reranking/), [Quickstart](https://docs.lancedb.com/tables/), [LanceDB Geneva](https://docs.lancedb.com/geneva/)
3. **Join the community**: [Discord](https://discord.gg/zMM32dvNtd) and [GitHub Discussions](https://github.com/lancedb/lance/discussions)

## Thank You to Our Contributors

We’d like to extend our heartfelt thanks to the community members who have contributed to making this integration a reality, shoutout to:

- **Enwei Jiao** from Luma AI
- **Bryan Keller** from Netflix
- **Jay Narale** from Uber
- **Jay Ju** from ByteDance
- **Jiebao Xiao** from Xiaomi

Your contributions, feedback, and real-world use cases have been instrumental in shaping this integration to meet the needs of production AI workloads.

## Conclusion

The combination of [Lance Namespace](https://lance.org/format/namespace/), Ray, and [LanceDB](https://docs.lancedb.com/) provides a complete solution for productionalizing AI workloads. [Lance Namespace](https://lance.org/format/namespace/) ensures seamless integration with your existing enterprise metadata services, Ray delivers the distributed computing power needed for data ingestion and feature engineering at scale, and LanceDB provides efficient [vector search](https://docs.lancedb.com/search/vector-search/), [full‑text search](https://docs.lancedb.com/search/full-text-search/), and [hybrid search](https://docs.lancedb.com/search/hybrid-search/) capabilities for serving your AI applications.

This integrated approach bridges the gap between experimentation and production, enabling you to build AI systems that not only scale but also fit naturally into your existing infrastructure. Get started with the [Quickstart](https://docs.lancedb.com/quickstart/) or explore [indexing](https://docs.lancedb.com/indexing/vector-index/) options.

Whether you’re building a [RAG system](https://docs.lancedb.com/tutorials/agents/), recommendation engine, or [multimodal search](https://docs.lancedb.com/tutorials/agents/multimodal-agent) application, this powerful trio gives you the enterprise integration, scalability, and performance you need for production deployments.

Try it out today and let us know what you build! We’re excited to see how you use [Lance Namespace](https://lance.org/format/namespace/), Ray, and [LanceDB](https://docs.lancedb.com/) to productionalize your AI workloads.

---

## Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray

*Source: `docs/bunchloch/teanga/Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray.md` (1369 words, 376 lines)*

---
title: "Productionalize AI Workloads with Lance Namespace, LanceDB, and Ray"
source: "https://lancedb.com/blog/lance-namespace-lancedb-and-ray"
author:
  - "[[[Jack Ye]]]"
published: 2025-09-04
created: 2025-12-20
description: "Learn how to productionalize AI workloads with Lance Namespace's enterprise stack integration and the scalability of LanceDB and Ray for end-to-end ML …"
tags:
  - "clippings"
---
In our [previous post](https://lancedb.com/blog/introducing-lance-namespace-spark-integration), we introduced [Lance Namespace](https://lance.org/format/namespace/) and its integration with Apache Spark. Today, we’re excited to showcase how to **productionalize your AI workloads** by combining:

- **Lance Namespace** for seamless enterprise stack integration with your existing metadata services
- **Ray** for data ingestion and feature engineering at scale
- **LanceDB** for efficient [vector search](https://docs.lancedb.com/search/vector-search/) and [full‑text search](https://docs.lancedb.com/search/full-text-search/)

This powerful combination enables you to build production-ready AI applications that integrate with your existing infrastructure while maintaining the scalability needed for real-world deployments.

## What’s New

### Lance–Ray Integration

The [lance-ray](https://pypi.org/project/lance-ray/) package has now evolved into its own independent subproject, bringing seamless integration between Ray and Lance. It enables distributed read, write, and data evolution operations on Lance datasets using Ray’s parallel processing capabilities, making it simple to handle large-scale data transformations and feature engineering workloads across your compute cluster.

### Lance Namespace Python and Rust SDKs

Lance Namespace now provides native Python and Rust SDKs that enable seamless enterprise integration across languages. This is what enables integration with both `lance-ray` and LanceDB.

## Building an End-to-End AI Pipeline

Let’s walk through a complete example using real data from Hugging Face to build a question-answering system. We’ll use the [BeIR/quora](https://huggingface.co/datasets/BeIR/quora) dataset to demonstrate the entire workflow.

### Step 1: Setting Up the Environment

First, install the required packages:

code

```fallback
pip install lance-ray sentence-transformers datasets

pip install --no-deps lancedb==0.25.0

pip install --no-deps lance-namespace==0.0.14
```

Initialize your Ray cluster and import the necessary libraries:

python

```python
import ray

import pyarrow as pa

from lance_ray import write_lance, read_lance, add_columns

from datasets import load_dataset

from sentence_transformers import SentenceTransformer

import numpy as np

# Initialize Ray with sufficient resources for parallel processing

ray.init()

# Load the embedding model (we'll use it later)

model = SentenceTransformer('BAAI/bge-small-en-v1.5')
```

### Step 2: Initialize Lance Namespace

Lance Namespace provides a unified interface to store and manage your Lance tables across different metadata services. Depending on your enterprise environment requirements, you can choose from various supported catalog services:

python

```python
import lance_namespace as ln

# Example 1: Directory-based namespace (for development/testing)

namespace = ln.connect("dir", {"root": "./lance_tables"})

# Example 2: Hive Metastore (for Hadoop/Spark ecosystems)

# namespace = ln.connect("hive", {"uri": "thrift://hive-metastore:9083"})

# Example 3: AWS Glue Catalog (for AWS-based infrastructure)

# namespace = ln.connect("glue", {"region": "us-east-1"})

# Example 4: Unity Catalog (for Databricks environments)

# namespace = ln.connect("unity", {"url": "https://your-workspace.cloud.databricks.com"})
```

For this example, we’ll use a directory-based namespace for simplicity, but you can seamlessly switch to any of the above options based on your infrastructure. See the [namespace implementations documentation](https://lance.org/format/namespace/impls) for detailed configuration options of each integrated service.

### Step 3: Distributed Data Ingestion with Ray

Now let’s load the Quora dataset and ingest it into [Lance format](https://docs.lancedb.com/lance/) using Ray’s distributed processing:

python

```python
# Load Quora dataset from Hugging Face

print("Loading Quora dataset...")

dataset = load_dataset("BeIR/quora", "corpus", split="corpus[:10000]", trust_remote_code=True)

# Convert to Ray Dataset for distributed processing

ray_dataset = ray.data.from_huggingface(dataset)

# Define schema with proper types

schema = pa.schema([

    pa.field("_id", pa.string()),

    pa.field("title", pa.string()),

    pa.field("text", pa.string()),

])

# Write to Lance format using namespace

print("Writing data to Lance format via namespace...")

write_lance(

    ray_dataset,

    namespace=namespace,

    table_id=["quora_questions"],

    schema=schema,

    mode="create",

    max_rows_per_file=5000,

)

print(f"Ingested {ray_dataset.count()} documents into Lance format")
```

### Step 4: Feature Engineering with Lance–Ray

Now we’ll use Ray’s distributed processing to generate embeddings for all documents.

python

```python
def generate_embeddings(batch: pa.RecordBatch) -> pa.RecordBatch:

    """Generate embeddings for text using sentence-transformers."""

    from sentence_transformers import SentenceTransformer

    

    # Initialize model (will be cached per Ray worker)

    model = SentenceTransformer('BAAI/bge-small-en-v1.5')

    

    # Combine title and text for better semantic representation

    texts = []

    for i in range(len(batch)):

        title = batch["title"][i].as_py() or ""

        text = batch["text"][i].as_py() or ""

        combined = f"{title}. {text}".strip()

        texts.append(combined)

    

    # Generate embeddings

    embeddings = model.encode(texts, normalize_embeddings=True)

    

    # Return as RecordBatch with fixed-size list field

    return pa.RecordBatch.from_arrays(

        [pa.array(embeddings.tolist(), type=pa.list_(pa.float32(), 384))],

        names=["vector"]

    )

# Add embeddings column using distributed processing with namespace

print("Generating embeddings using Ray...")

add_columns(

    None, # no static URI

    namespace=namespace,

    table_id=["quora_questions"],

    transform=generate_embeddings,

    read_columns=["title", "text"],  # Only read necessary columns

    batch_size=100,  # Process in batches of 100

    concurrency=4,  # Use 4 parallel workers

    ray_remote_args={"num_gpus": 0.25} if ray.cluster_resources().get("GPU", 0) > 0 else {}

)

print("Embeddings generated successfully!")
```

The `add_columns` functionality in Ray allows ML/AI scientists to quickly start feature engineering with a local or remote Ray cluster. For more advanced feature engineering capabilities such as lazy materialization, partial backfill, fault-tolerant execution, check out [LanceDB’s Geneva](https://lancedb.com/docs/geneva/) - our feature engineering framework that provides schema enforcement, versioning, and complex transformations. You can also follow our [multimodal lakehouse tutorial](https://lancedb.com/docs/tutorials/mmlh/) for comprehensive examples.

Now let’s connect to our Lance dataset through [LanceDB](https://docs.lancedb.com/) using the same namespace and perform vector similarity search:

python

```python
import lancedb

from sentence_transformers import SentenceTransformer

# Connect to LanceDB using the same namespace

db = lancedb.connect_namespace("dir", {"root": "./lance_tables"})

table = db.open_table("quora_questions")

# Create [vector index](https://docs.lancedb.com/indexing/vector-index/) for fast similarity search

print("Creating vector index...")

table.create_index(

    metric="cosine",

    vector_column_name="vector",

    index_type="IVF_PQ",

    num_partitions=32,

    num_sub_vectors=48,

)

# Perform vector similarity search

query_text = "How do I learn machine learning?"

model = SentenceTransformer('BAAI/bge-small-en-v1.5')

query_embedding = model.encode([query_text], normalize_embeddings=True)[0]

vector_results = (

    table.search(query_embedding, vector_column_name="vector")

    .limit(5)

    .to_pandas()

)

print("\n=== Vector Search Results ===")

print(f"Query: {query_text}\n")

for idx, row in vector_results.iterrows():

    print(f"{idx + 1}. {row['title']}")

    print(f"   {row['text'][:150]}...")

    print()
```

Now let’s also do a full text search against the `text` column:

python

```python
print("Creating full-text search index...")

table.create_fts_index("text")

# Example 1: Full‑Text Search

keyword_results = (

    table.search("machine learning algorithms", query_type="fts")

    .limit(5)

    .to_pandas()

)

print("\n=== Full-Text Search Results ===")

print("Keywords: 'machine learning algorithms'\n")

for idx, row in keyword_results.iterrows():

    print(f"{idx + 1}. {row['title']}")

    print(f"   {row['text'][:150]}...")

    print()
```

### Step 7: Beyond the Examples

Now, you can continue playing around with the dataset. You can add more feature columns with python functions through Ray. LanceDB also allows [hybrid search](https://docs.lancedb.com/search/hybrid-search/) that combines the semantic understanding of [vector search](https://docs.lancedb.com/search/vector-search/) with the precision of [keyword matching](https://docs.lancedb.com/search/full-text-search/). You can also load data into tools like PyTorch and LangChain for other AI activities.

## Real-World Use Cases

This integration pattern is particularly powerful for:

1. **RAG Applications**: Ingest documents, generate embeddings, and serve semantic search
2. **Recommendation Systems**: Process user interactions and build vector indices at scale
3. **Multimodal Search**: Process images and text together using Ray’s distributed computing
4. **Feature Stores**: Transform and store ML features with versioning via Lance Namespace
5. **Real-time Analytics**: Combine batch processing with low-latency search

## Getting Started Today

Ready to scale your AI workloads? Here’s how to get started:

1. **Install the packages**: `pip install lance-ray lancedb`
2. **Read the documentation**: [Lance–Ray](https://lance.org/integrations/ray/), [LanceDB](https://docs.lancedb.com/), [Vector Search](https://docs.lancedb.com/search/vector-search/), [Full‑Text Search](https://docs.lancedb.com/search/full-text-search/), [Hybrid Search](https://docs.lancedb.com/search/hybrid-search/), [Vector Indexing](https://docs.lancedb.com/indexing/vector-index/), [FTS Indexing](https://docs.lancedb.com/indexing/fts-index/), [Filtering](https://docs.lancedb.com/search/filtering/), [Reranking](https://docs.lancedb.com/reranking/), [Quickstart](https://docs.lancedb.com/tables/), [LanceDB Geneva](https://docs.lancedb.com/geneva/)
3. **Join the community**: [Discord](https://discord.gg/zMM32dvNtd) and [GitHub Discussions](https://github.com/lancedb/lance/discussions)

## Thank You to Our Contributors

We’d like to extend our heartfelt thanks to the community members who have contributed to making this integration a reality, shoutout to:

- **Enwei Jiao** from Luma AI
- **Bryan Keller** from Netflix
- **Jay Narale** from Uber
- **Jay Ju** from ByteDance
- **Jiebao Xiao** from Xiaomi

Your contributions, feedback, and real-world use cases have been instrumental in shaping this integration to meet the needs of production AI workloads.

## Conclusion

The combination of [Lance Namespace](https://lance.org/format/namespace/), Ray, and [LanceDB](https://docs.lancedb.com/) provides a complete solution for productionalizing AI workloads. [Lance Namespace](https://lance.org/format/namespace/) ensures seamless integration with your existing enterprise metadata services, Ray delivers the distributed computing power needed for data ingestion and feature engineering at scale, and LanceDB provides efficient [vector search](https://docs.lancedb.com/search/vector-search/), [full‑text search](https://docs.lancedb.com/search/full-text-search/), and [hybrid search](https://docs.lancedb.com/search/hybrid-search/) capabilities for serving your AI applications.

This integrated approach bridges the gap between experimentation and production, enabling you to build AI systems that not only scale but also fit naturally into your existing infrastructure. Get started with the [Quickstart](https://docs.lancedb.com/quickstart/) or explore [indexing](https://docs.lancedb.com/indexing/vector-index/) options.

Whether you’re building a [RAG system](https://docs.lancedb.com/tutorials/agents/), recommendation engine, or [multimodal search](https://docs.lancedb.com/tutorials/agents/multimodal-agent) application, this powerful trio gives you the enterprise integration, scalability, and performance you need for production deployments.

Try it out today and let us know what you build! We’re excited to see how you use [Lance Namespace](https://lance.org/format/namespace/), Ray, and [LanceDB](https://docs.lancedb.com/) to productionalize your AI workloads.

---

## Using MotherDuck with PlanetScale — PlanetScale

*Source: `docs/bunchloch/teanga/Using MotherDuck with PlanetScale — PlanetScale.md` (405 words, 47 lines)*

---
title: "Using MotherDuck with PlanetScale — PlanetScale"
source: "https://planetscale.com/blog/using-motherduck-with-planetscale"
author:
published: 2025-12-16
created: 2025-12-16
description: "Using MotherDuck with PlanetScale"
tags:
  - "clippings"
---
$50 Metal Postgres databases are here.[Learn more](https://planetscale.com/blog/50-dollar-planetscale-metal-is-ga-for-postgres)

[Blog](https://planetscale.com/blog) |

## Using MotherDuck with PlanetScale

By Ben Dicken |

DuckDB has gained significant traction for OLAP workloads.It's powerful, flexible, and has a feature-rich SQL dialect, making it perfect to use for analytics alongside OLTP-oriented relational databases.

Today, we're excited to announce support for the `pg_duckdb` extension for Postgres databases on PlanetScale alongside our partnership with MotherDuck.

## DuckDB in Postgres

DuckDB can be run as a standalone OLAP database, but also alongside Postgres via the [`pg_duckdb` extension](https://github.com/duckdb/pg_duckdb).The extension integrates DuckDB's column-store analytics engine right inside of Postgres, allowing you to seamlessly combine OLTP and OLAP queries over Postgres connections.

When enabled, tables can be created either using the standard Postgres table format *or* temporary tables in the DuckDB vectorized column format.Queries can then be selectively executed either using the Postgres engine or DuckDB.`pg_duckdb` can also be used to work with and query external datasources in popular formats like Apache Parquet and Iceberg.

Having DuckDB as a built-in extension makes data movement between Postgres and DuckDB formats simpler, and unifies the experience of combining analytics results with the rest of your relational data.

## MotherDuck

Though DuckDB is extremely powerful, many prefer to separate analytical compute from OLTP compute.This is useful to ensure that heavy analytics queries don't negatively impact application performance, and vice-versa.

MotherDuck is a cloud data warehouse with deep integration and support for DuckDB, and is a perfect solution to this problem.The `pg_duckdb` extension supports offloading analytics queries to the MotherDuck cloud.Analytics queries can be executed from within your PlanetScale Postgres database, but the analytics query execution can be offloaded to your data sets stored in the MotherDuck cloud.The results can then be returned to Postgres for further processing.

To use DuckDB and MotherDuck together with your PlanetScale database:

- Enable `pg_duckdb` via the "Extensions" table on the "Clusters" page of your database.

![Enable pg_duckdb](https://planetscale-images.imgix.net/assets/enable-duckdb-extension-DHkLGkML.png?auto=compress%2Cformat)

- Connect to your Postgres database and run `GRANT CREATE ON SCHEMA public to pscale_superuser;` to allow the addition of the MotherDuck catalog in Postgres and `CREATE EXTENSION pg_duckdb;` to create the extension.
- Add your MotherDuck token with `CALL duckdb.enable_motherduck('YOUR_TOKEN');`
- Start running your analytics queries!

Check out [our docs](https://planetscale.com/docs/postgres/extensions/pg_duckdb) and the [MotherDuck docs](https://motherduck.com/docs/concepts/pgduckdb/) for more information on how to use `pg_duckdb` with MotherDuck.

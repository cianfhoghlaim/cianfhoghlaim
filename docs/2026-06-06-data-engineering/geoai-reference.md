# GeoAI Reference

> Merged from 35 source files in `geoai/` — PyPI package docs, API reference, QGIS plugin, research patterns, and JOSS paper.

---

## Introduction & Overview


> Source: `docs/data_engineering/geoai/README.md`

# GeoAI: Artificial Intelligence for Geospatial Data

[![image](https://img.shields.io/pypi/v/geoai-py.svg)](https://pypi.python.org/pypi/geoai-py)
[![image](https://static.pepy.tech/badge/geoai-py)](https://pepy.tech/project/geoai-py)
[![image](https://img.shields.io/conda/vn/conda-forge/geoai.svg)](https://anaconda.org/conda-forge/geoai)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/geoai.svg)](https://anaconda.org/conda-forge/geoai)
[![Conda Recipe](https://img.shields.io/badge/recipe-geoai-green.svg)](https://github.com/conda-forge/geoai-py-feedstock)
[![image](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![image](https://img.shields.io/badge/YouTube-Tutorials-red)](https://tinyurl.com/GeoAI-Tutorials)
[![QGIS](https://img.shields.io/badge/QGIS-plugin-orange.svg)](https://opengeoai.org/qgis_plugin)

[![logo](https://raw.githubusercontent.com/opengeos/geoai/master/docs/assets/logo_rect.png)](https://github.com/opengeos/geoai/blob/master/docs/assets/logo.png)

**A powerful Python package for integrating artificial intelligence with geospatial data analysis and visualization**

## 📖 Introduction

[GeoAI](https://opengeoai.org) is a comprehensive Python package designed to bridge artificial intelligence (AI) and geospatial data analysis, providing researchers and practitioners with intuitive tools for applying machine learning techniques to geographic data. The package offers a unified framework for processing satellite imagery, aerial photographs, and vector data using state-of-the-art deep learning models. GeoAI integrates popular AI frameworks including [PyTorch](https://pytorch.org), [Transformers](https://github.com/huggingface/transformers), [PyTorch Segmentation Models](https://github.com/qubvel-org/segmentation_models.pytorch), and specialized geospatial libraries like [torchange](https://github.com/Z-Zheng/pytorch-change-models), enabling users to perform complex geospatial analyses with minimal code.

The package provides five core capabilities:

1. Interactive and programmatic search and download of remote sensing imagery and geospatial data.
2. Automated dataset preparation with image chips and label generation.
3. Model training for tasks such as classification, detection, and segmentation.
4. Inference pipelines for applying models to new geospatial datasets.
5. Interactive visualization through integration with [Leafmap](https://github.com/opengeos/leafmap/) and [MapLibre](https://github.com/eoda-dev/py-maplibregl).

GeoAI addresses the growing demand for accessible AI tools in geospatial research by providing high-level APIs that abstract complex machine learning workflows while maintaining flexibility for advanced users. The package supports multiple data formats (GeoTIFF, JPEG2000,GeoJSON, Shapefile, GeoPackage) and includes automatic device management for GPU acceleration when available. With over 10 modules and extensive notebook examples, GeoAI serves as both a research tool and educational resource for the geospatial AI community.

## 📝 Statement of Need

The integration of artificial intelligence with geospatial data analysis has become increasingly critical across numerous scientific disciplines, from environmental monitoring and urban planning to disaster response and climate research. However, applying AI techniques to geospatial data presents unique challenges including data preprocessing complexities, specialized model architectures, and the need for domain-specific knowledge in both machine learning and geographic information systems.

Existing solutions often require researchers to navigate fragmented ecosystems of tools, combining general-purpose machine learning libraries with specialized geospatial packages, leading to steep learning curves and reproducibility challenges. While packages like TorchGeo and TerraTorch provide excellent foundational tools for geospatial deep learning, there remains a gap for comprehensive, high-level interfaces that can democratize access to advanced AI techniques for the broader geospatial community.

GeoAI addresses this need by providing a unified, user-friendly interface that abstracts the complexity of integrating multiple AI frameworks with geospatial data processing workflows. It lowers barriers for: (1) geospatial researchers who need accessible AI workflows without deep ML expertise; (2) AI practitioners who want streamlined geospatial preprocessing and domain-specific datasets; and (3) educators seeking reproducible examples and teaching-ready workflows.

The package's design philosophy emphasizes simplicity without sacrificing functionality, enabling users to perform sophisticated analyses such as building footprint extraction from satellite imagery, land cover classification, and change detection with just a few lines of code. By integrating cutting-edge AI models and providing seamless access to major geospatial data sources, GeoAI significantly lowers the barrier to entry for geospatial AI applications while maintaining the flexibility needed for advanced research applications.

## Citations

If you find GeoAI useful in your research, please consider citing the following paper to support my work. Thank you for your support.

-   Wu, Q. (2025). GeoAI: A Python package for integrating artificial intelligence with geospatial data analysis and visualization. _Journal of Open Source Software_, 9025. [https://doi.org/10.21105/joss.09025](https://github.com/openjournals/joss-papers/blob/joss.09605/joss.09605/10.21105.joss.09605.pdf) (Under Review)

## 🚀 Key Features

### 📊 Advanced Geospatial Data Visualization

-   Interactive multi-layer visualization of vector and raster data stored locally or in cloud storage
-   Customizable styling and symbology
-   Time-series data visualization capabilities

### 🛠️ Data Preparation & Processing

-   Streamlined access to satellite and aerial imagery from providers like Sentinel, Landsat, NAIP, and other open datasets
-   Tools for downloading, mosaicking, and preprocessing remote sensing data
-   Automated generation of training datasets with image chips and corresponding labels
-   Vector-to-raster and raster-to-vector conversion utilities optimized for AI workflows
-   Data augmentation techniques specific to geospatial data
-   Support for integrating Overture Maps data and other open datasets for training and validation

### 🖼️ Image Segmentation

-   Integration with [PyTorch Segmentation Models](https://github.com/qubvel-org/segmentation_models.pytorch) for automatic feature extraction
-   Specialized segmentation algorithms optimized for satellite and aerial imagery
-   Streamlined workflows for segmenting buildings, water bodies, wetlands,solar panels, etc.
-   Export capabilities to standard geospatial formats (GeoJSON, Shapefile, GeoPackage, GeoParquet)

### 🔍 Image Classification

-   Pre-trained models for land cover and land use classification
-   Transfer learning utilities for fine-tuning models with your own data
-   Multi-temporal classification support for change detection
-   Accuracy assessment and validation tools

### 🌍 Additional Capabilities

-   Change detection with AI-enhanced feature extraction
-   Object detection in aerial and satellite imagery
-   Georeferencing utilities for AI model outputs

## 📦 Installation

### Using pip

```bash
pip install geoai-py
```

### Using conda

```bash
conda install -c conda-forge geoai
```

### Using mamba

```bash
mamba install -c conda-forge geoai
```

## ⚙️ QGIS Plugin

Check out the [QGIS Plugin](https://opengeoai.org/qgis_plugin/) page if you are interested in using GeoAI with QGIS.

[![demo](https://github.com/user-attachments/assets/5aabc3d3-efd1-4011-ab31-2b3f11aab3ed)](https://youtu.be/8-OhlqeoyiY)

## 📋 Documentation

Comprehensive documentation is available at [https://opengeoai.org](https://opengeoai.org), including:

-   Detailed API reference
-   Tutorials and example notebooks
-   Contributing guide

## 📺 Video Tutorials

### GeoAI Made Easy: Learn the Python Package Step-by-Step (Beginner Friendly)

[![intro](https://github.com/user-attachments/assets/7e60ce05-573d-4d0d-9876-5289b87e5136)](https://youtu.be/VIl29Rca6zE&list=PLAxJ4-o7ZoPcvENqwaPa_QwbbkZ5sctZE)

### GeoAI Workshop: Unlocking the Power of GeoAI with Python

[![cover](https://github.com/user-attachments/assets/1c14e651-65b9-41ae-b42d-3ad028b3eeb8)](https://youtu.be/jdK-cleFUkc&list=PLAxJ4-o7ZoPcvENqwaPa_QwbbkZ5sctZE)

### GeoAI Tutorials Playlist

[![cover](https://github.com/user-attachments/assets/3cde9547-ab62-4d70-b23a-3e5ed27c7407)](https://www.youtube.com/playlist?list=PLAxJ4-o7ZoPcvENqwaPa_QwbbkZ5sctZE)

## 🤝 Contributing

We welcome contributions of all kinds! See our [contributing guide](https://opengeoai.org/contributing) for ways to get started.

## 📄 License

GeoAI is free and open source software, licensed under the MIT License.

## Acknowledgments

We gratefully acknowledge the support of the following organizations:

-   [NASA](https://www.nasa.gov): This research is partially supported by the National Aeronautics and Space Administration (NASA) through Grant No. 80NSSC22K1742, awarded under the [Open Source Tools, Frameworks, and Libraries Program](https://bit.ly/3RVBRcQ).
-   [AmericaView](https://americaview.org): This work is also partially supported by the U.S. Geological Survey through Grant/Cooperative Agreement No. G23AP00683 (GY23-GY27) in collaboration with AmericaView.


> Source: `docs/data_engineering/geoai/docs/index.md`

# GeoAI: Artificial Intelligence for Geospatial Data

[![image](https://img.shields.io/pypi/v/geoai-py.svg)](https://pypi.python.org/pypi/geoai-py)
[![image](https://static.pepy.tech/badge/geoai-py)](https://pepy.tech/project/geoai-py)
[![image](https://img.shields.io/conda/vn/conda-forge/geoai.svg)](https://anaconda.org/conda-forge/geoai)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/geoai.svg)](https://anaconda.org/conda-forge/geoai)
[![Conda Recipe](https://img.shields.io/badge/recipe-geoai-green.svg)](https://github.com/conda-forge/geoai-py-feedstock)
[![image](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![image](https://img.shields.io/badge/YouTube-Tutorials-red)](https://tinyurl.com/GeoAI-Tutorials)
[![QGIS](https://img.shields.io/badge/QGIS-plugin-orange.svg)](https://opengeoai.org/qgis_plugin)

[![logo](https://raw.githubusercontent.com/opengeos/geoai/master/docs/assets/logo_rect.png)](https://github.com/opengeos/geoai/blob/master/docs/assets/logo.png)

**A powerful Python package for integrating artificial intelligence with geospatial data analysis and visualization**

## 📖 Introduction

[GeoAI](https://opengeoai.org) is a comprehensive Python package designed to bridge artificial intelligence (AI) and geospatial data analysis, providing researchers and practitioners with intuitive tools for applying machine learning techniques to geographic data. The package offers a unified framework for processing satellite imagery, aerial photographs, and vector data using state-of-the-art deep learning models. GeoAI integrates popular AI frameworks including [PyTorch](https://pytorch.org), [Transformers](https://github.com/huggingface/transformers), [PyTorch Segmentation Models](https://github.com/qubvel-org/segmentation_models.pytorch), and specialized geospatial libraries like [torchange](https://github.com/Z-Zheng/pytorch-change-models), enabling users to perform complex geospatial analyses with minimal code.

The package provides five core capabilities:

1. Interactive and programmatic search and download of remote sensing imagery and geospatial data.
2. Automated dataset preparation with image chips and label generation.
3. Model training for tasks such as classification, detection, and segmentation.
4. Inference pipelines for applying models to new geospatial datasets.
5. Interactive visualization through integration with [Leafmap](https://github.com/opengeos/leafmap/) and [MapLibre](https://github.com/eoda-dev/py-maplibregl).

GeoAI addresses the growing demand for accessible AI tools in geospatial research by providing high-level APIs that abstract complex machine learning workflows while maintaining flexibility for advanced users. The package supports multiple data formats (GeoTIFF, JPEG2000,GeoJSON, Shapefile, GeoPackage) and includes automatic device management for GPU acceleration when available. With over 10 modules and extensive notebook examples, GeoAI serves as both a research tool and educational resource for the geospatial AI community.

## 📝 Statement of Need

The integration of artificial intelligence with geospatial data analysis has become increasingly critical across numerous scientific disciplines, from environmental monitoring and urban planning to disaster response and climate research. However, applying AI techniques to geospatial data presents unique challenges including data preprocessing complexities, specialized model architectures, and the need for domain-specific knowledge in both machine learning and geographic information systems.

Existing solutions often require researchers to navigate fragmented ecosystems of tools, combining general-purpose machine learning libraries with specialized geospatial packages, leading to steep learning curves and reproducibility challenges. While packages like TorchGeo and TerraTorch provide excellent foundational tools for geospatial deep learning, there remains a gap for comprehensive, high-level interfaces that can democratize access to advanced AI techniques for the broader geospatial community.

GeoAI addresses this need by providing a unified, user-friendly interface that abstracts the complexity of integrating multiple AI frameworks with geospatial data processing workflows. It lowers barriers for: (1) geospatial researchers who need accessible AI workflows without deep ML expertise; (2) AI practitioners who want streamlined geospatial preprocessing and domain-specific datasets; and (3) educators seeking reproducible examples and teaching-ready workflows.

The package's design philosophy emphasizes simplicity without sacrificing functionality, enabling users to perform sophisticated analyses such as building footprint extraction from satellite imagery, land cover classification, and change detection with just a few lines of code. By integrating cutting-edge AI models and providing seamless access to major geospatial data sources, GeoAI significantly lowers the barrier to entry for geospatial AI applications while maintaining the flexibility needed for advanced research applications.

## Citations

If you find GeoAI useful in your research, please consider citing the following paper to support my work. Thank you for your support.

-   Wu, Q. (2025). GeoAI: A Python package for integrating artificial intelligence with geospatial data analysis and visualization. _Journal of Open Source Software_, 9025. [https://doi.org/10.21105/joss.09025](https://github.com/openjournals/joss-papers/blob/joss.09605/joss.09605/10.21105.joss.09605.pdf) (Under Review)

## 🚀 Key Features

### 📊 Advanced Geospatial Data Visualization

-   Interactive multi-layer visualization of vector and raster data stored locally or in cloud storage
-   Customizable styling and symbology
-   Time-series data visualization capabilities

### 🛠️ Data Preparation & Processing

-   Streamlined access to satellite and aerial imagery from providers like Sentinel, Landsat, NAIP, and other open datasets
-   Tools for downloading, mosaicking, and preprocessing remote sensing data
-   Automated generation of training datasets with image chips and corresponding labels
-   Vector-to-raster and raster-to-vector conversion utilities optimized for AI workflows
-   Data augmentation techniques specific to geospatial data
-   Support for integrating Overture Maps data and other open datasets for training and validation

### 🖼️ Image Segmentation

-   Integration with [PyTorch Segmentation Models](https://github.com/qubvel-org/segmentation_models.pytorch) for automatic feature extraction
-   Specialized segmentation algorithms optimized for satellite and aerial imagery
-   Streamlined workflows for segmenting buildings, water bodies, wetlands,solar panels, etc.
-   Export capabilities to standard geospatial formats (GeoJSON, Shapefile, GeoPackage, GeoParquet)

### 🔍 Image Classification

-   Pre-trained models for land cover and land use classification
-   Transfer learning utilities for fine-tuning models with your own data
-   Multi-temporal classification support for change detection
-   Accuracy assessment and validation tools

### 🌍 Additional Capabilities

-   Change detection with AI-enhanced feature extraction
-   Object detection in aerial and satellite imagery
-   Georeferencing utilities for AI model outputs

## 📦 Installation

### Using pip

```bash
pip install geoai-py
```

### Using conda

```bash
conda install -c conda-forge geoai
```

### Using mamba

```bash
mamba install -c conda-forge geoai
```

## ⚙️ QGIS Plugin

Check out the [QGIS Plugin](https://opengeoai.org/qgis_plugin/) page if you are interested in using GeoAI with QGIS.

[![demo](https://github.com/user-attachments/assets/5aabc3d3-efd1-4011-ab31-2b3f11aab3ed)](https://youtu.be/8-OhlqeoyiY)

## 📋 Documentation

Comprehensive documentation is available at [https://opengeoai.org](https://opengeoai.org), including:

-   Detailed API reference
-   Tutorials and example notebooks
-   Contributing guide

## 📺 Video Tutorials

### GeoAI Made Easy: Learn the Python Package Step-by-Step (Beginner Friendly)

[![intro](https://github.com/user-attachments/assets/7e60ce05-573d-4d0d-9876-5289b87e5136)](https://youtu.be/VIl29Rca6zE&list=PLAxJ4-o7ZoPcvENqwaPa_QwbbkZ5sctZE)

### GeoAI Workshop: Unlocking the Power of GeoAI with Python

[![cover](https://github.com/user-attachments/assets/1c14e651-65b9-41ae-b42d-3ad028b3eeb8)](https://youtu.be/jdK-cleFUkc&list=PLAxJ4-o7ZoPcvENqwaPa_QwbbkZ5sctZE)

### GeoAI Tutorials Playlist

[![cover](https://github.com/user-attachments/assets/3cde9547-ab62-4d70-b23a-3e5ed27c7407)](https://www.youtube.com/playlist?list=PLAxJ4-o7ZoPcvENqwaPa_QwbbkZ5sctZE)

## 🤝 Contributing

We welcome contributions of all kinds! See our [contributing guide](https://opengeoai.org/contributing) for ways to get started.

## 📄 License

GeoAI is free and open source software, licensed under the MIT License.

## Acknowledgments

We gratefully acknowledge the support of the following organizations:

-   [NASA](https://www.nasa.gov): This research is partially supported by the National Aeronautics and Space Administration (NASA) through Grant No. 80NSSC22K1742, awarded under the [Open Source Tools, Frameworks, and Libraries Program](https://bit.ly/3RVBRcQ).
-   [AmericaView](https://americaview.org): This work is also partially supported by the U.S. Geological Survey through Grant/Cooperative Agreement No. G23AP00683 (GY23-GY27) in collaboration with AmericaView.


## KCG Summary


> Source: `docs/data_engineering/geoai/KCG_SUMMARY.md`

# GeoAI — KCG Summary

## What It Is
GeoAI is a Python package integrating AI with geospatial data analysis: satellite imagery classification, object detection, semantic segmentation (buildings, water bodies, solar panels), change detection, and interactive map visualization. Built on PyTorch, Transformers, and segmentation_models.pytorch, with QGIS plugin support and integration with Leafmap/MapLibre for interactive mapping. Includes 28 documentation pages and research on geospatial linguistics and Ibis integration.

## Why This Matters for Kings' College Galway
GeoAI's segmentation and classification patterns are directly applicable to Irish geography curriculum data — automated land cover analysis for Leaving Cert geography projects, historical map change detection for Celtic studies, and interactive map visualization for student-facing dashboards. The Ibis integration notes show how to bridge geospatial data with the oideachais Ibis analytics layer. The lightweight training patterns (fine-tuning on consumer hardware) align with the bunchloch MacBook M4 development environment.

## Key Patterns Preserved
34 .md files remain:
- `README.md` — Full GeoAI package overview with features, installation, and architecture
- `docs/*.md` (24 files) — Complete documentation: installation, segmentation, classification, change detection, model training (PyTorch, Detectron2, DINOv3, SAM, Moondream), map tools/widgets, QGIS plugin, GeoAgents, contributing, changelog
- `paper/paper.md` — JOSS paper on GeoAI
- `geospatial_book.md` — Geospatial data science reference
- `Geospatial Data Visualization with Ibis.md` — Ibis + geospatial integration
- `Geospatial Workflow & Particle Effects.md` — Advanced visualization patterns
- `geospatial-linguistics.md` — Linguistic geospatial analysis
- `qgis_plugin/README.md` — QGIS plugin overview
- `.github/ISSUE_TEMPLATE/` — Bug and feature request templates

## Source Files
Full source removed (2026-06-06). Available at https://github.com/opengeos/geoai

## What Was Removed
Python source (.py), Jupyter notebooks (.ipynb), YAML/TOML/JSON configs, SVG/PNG images, shell scripts, .gitignore, lock files, conda recipe, Docker files, QGIS plugin .xml


## Installation


> Source: `docs/data_engineering/geoai/docs/installation.md`

# Installation

This guide covers various methods for installing GeoAI on different platforms with different package managers.

## ✅ Prerequisites

GeoAI requires:

-   Python 3.10 or above
-   The required dependencies will be installed automatically

## 🚀 Recommended Installation Methods

### 🐍 Using pip

The simplest way to install the latest stable release of GeoAI is via pip:

```bash
pip install geoai-py
```

To install GeoAI with all optional dependencies for additional features:

```bash
pip install "geoai-py[all]"
```

### 🐍 Using uv

To install the latest stable release of GeoAI with [uv](https://docs.astral.sh/uv), a faster alternative to pip:

```bash
uv pip install geoai-py
```

### 🐼 Using conda

For Anaconda/Miniconda users, we recommend installing GeoAI via conda-forge, which handles dependencies like GDAL more elegantly:

```bash
conda install -c conda-forge geoai
```

### 🦡 Using mamba

Mamba provides faster dependency resolution compared to conda. This is especially useful for large packages like GeoAI:

```bash
conda create -n geo python=3.12
conda activate geo
conda install -c conda-forge mamba
mamba install -c conda-forge geoai
```

## 🔧 Advanced Installation Options

### 🖥️ GPU Support

To enable GPU acceleration for deep learning models (requires NVIDIA GPU):

```bash
mamba install -c conda-forge geoai "pytorch=*=cuda*"
```

This will install the appropriate PyTorch version with CUDA support.

If you run into issues with the ipympl package, you can install it using the following command:

```bash
mamba install -c conda-forge geoai "pytorch=*=cuda*" jupyterlab ipympl
```

If you encounter issues with the sqlite package, you can update it using the following command:

```bash
mamba update -c conda-forge sqlite
```

### Notes for Windows Users

If you use mamba to install geoai, you may not have the latest version of torchgeo, which may cause issues when importing geoai. To fix this, you can install the latest version of torchgeo using the following command:

```bash
pip install -U torchgeo
```

### 👩‍💻 Development Installation

For contributing to GeoAI development, install directly from the source repository:

```bash
git clone https://github.com/opengeos/geoai.git
cd geoai
pip install -e .
```

The `-e` flag installs the package in development mode, allowing you to modify the code and immediately see the effects.

### 📦 Installing from GitHub

To install the latest development version directly from GitHub:

```bash
pip install git+https://github.com/opengeos/geoai.git
```

For a specific branch:

```bash
pip install git+https://github.com/opengeos/geoai.git@branch-name
```

## ✓ Verifying Installation

To verify your installation, run:

```python
import geoai
print(geoai.__version__)
```

## ⚠️ Troubleshooting

If you encounter installation problems:

1. Search for similar issues in our [GitHub Issues](https://github.com/opengeos/geoai/issues)
2. Ask for help in our [GitHub Discussions](https://github.com/opengeos/geoai/discussions)

## 🔄 Upgrading

To upgrade GeoAI to the latest version:

```bash
pip install -U geoai-py
```

Or with conda:

```bash
conda update -c conda-forge geoai
```


## API Reference — Data Acquisition


> Source: `docs/data_engineering/geoai/docs/download.md`

# download module

::: geoai.download


> Source: `docs/data_engineering/geoai/docs/auto.md`

# auto module

::: geoai.auto


> Source: `docs/data_engineering/geoai/docs/hf.md`

# hf module

::: geoai.hf


## API Reference — Model Training


> Source: `docs/data_engineering/geoai/docs/train.md`

# train module

::: geoai.train


> Source: `docs/data_engineering/geoai/docs/timm_train.md`

# timm_train module

::: geoai.timm_train


> Source: `docs/data_engineering/geoai/docs/dinov3.md`

# DINOv3 module

::: geoai.dinov3


## API Reference — Inference & Segmentation


> Source: `docs/data_engineering/geoai/docs/classify.md`

# classify module

::: geoai.classify


> Source: `docs/data_engineering/geoai/docs/sam.md`

# sam module

::: geoai.sam


> Source: `docs/data_engineering/geoai/docs/segment.md`

# segment module

::: geoai.segment


> Source: `docs/data_engineering/geoai/docs/segmentation.md`

# segmentation module

::: geoai.segmentation


> Source: `docs/data_engineering/geoai/docs/timm_segment.md`

# timm_segment module

::: geoai.timm_segment


> Source: `docs/data_engineering/geoai/docs/detectron2.md`

# detectron2 module

::: geoai.detectron2


> Source: `docs/data_engineering/geoai/docs/moondream.md`

# moondream module

::: geoai.moondream


## API Reference — Change Detection & Extraction


> Source: `docs/data_engineering/geoai/docs/change_detection.md`

# change_detection module

::: geoai.change_detection


> Source: `docs/data_engineering/geoai/docs/extract.md`

# extract module

::: geoai.extract


## API Reference — Geo Agents & Utilities


> Source: `docs/data_engineering/geoai/docs/geo_agents.md`

# geo_agents module

::: geoai.agents.geo_agents


> Source: `docs/data_engineering/geoai/docs/geoai.md`


# geoai module

::: geoai.geoai

> Source: `docs/data_engineering/geoai/docs/utils.md`

# utils module

::: geoai.utils


## API Reference — Visualization & Tools


> Source: `docs/data_engineering/geoai/docs/map_tools.md`

# map_tools module

::: geoai.agents.map_tools


> Source: `docs/data_engineering/geoai/docs/map_widgets.md`

# map_widgets module

::: geoai.map_widgets


## QGIS Plugin


> Source: `docs/data_engineering/geoai/docs/qgis_plugin.md`

# QGIS Plugin for GeoAI

A QGIS plugin that brings the [geoai](https://github.com/opengeos/geoai) models into dockable panels (Moondream VLM, segmentation training/inference, SamGeo) so you can keep QGIS as your main workspace while experimenting with GeoAI.

## Quick Start

-   Create a fresh conda env (`conda create -n geo python=3.12`) and install QGIS + deps (see below).
-   Install the plugin (`python install.py`) from this repo.
-   Restart QGIS → `Plugins` → `Manage and Install Plugins...` → enable `GeoAI`.
-   Open a GeoAI toolbar panel and try the sample datasets below.

## Video Tutorials

Check out this [short video demo](https://youtu.be/Esr_e6_P1is) and [full video tutorial](https://youtu.be/8-OhlqeoyiY) on how to use the GeoAI plugin in QGIS.

[![demo](https://github.com/user-attachments/assets/5aabc3d3-efd1-4011-ab31-2b3f11aab3ed)](https://youtu.be/8-OhlqeoyiY)

## Requirements

-   QGIS 3.28 or later
-   Python 3.10+ (conda recommended)
-   PyTorch (CUDA if you want GPU acceleration)
-   `geoai` and `samgeo` packages

## Features

Each tool lives inside a dockable panel that can be attached to either side of the QGIS interface, so you can keep layers, maps, and models visible simultaneously.

### Moondream Vision-Language Model Panel

-   **Caption**: Generate descriptions of geospatial imagery (short, normal, or long)
-   **Query**: Ask questions about images using natural language
-   **Detect**: Detect and locate objects with bounding boxes
-   **Point**: Locate specific objects with point markers

### Segmentation Panel (Combined Training & Inference)

-   **Tab 1 - Create Training Data**: Export GeoTIFF tiles from raster and vector data
-   **Tab 2 - Train Models**: Train custom segmentation models (U-Net, DeepLabV3+, FPN, etc.)
-   **Tab 3 - Run Inference**: Apply trained models to new imagery and vectorize results. Vector outputs can optionally be smoothed or simplified for immediate use in GIS workflows.

### SamGeo Panel (Segment Anything Model)

-   **Model Tab**: Load SAM models (SAM1, SAM2, or SAM3) with configurable backend and device settings
-   **Text Tab**: Segment objects using text prompts (e.g., "tree", "building", "road")
-   **Interactive Tab**: Segment using point prompts (foreground/background) or box prompts drawn on the map
-   **Batch Tab**: Process multiple points interactively or from vector files/layers
-   **Output Tab**: Save results as raster (GeoTIFF) or vector (GeoPackage, Shapefile) with optional regularization (orthogonalize polygons, filter by minimum area)

### GPU Memory Management

-   **Clear GPU Memory**: Release GPU memory and clear CUDA cache for all loaded models

## Installation

### 1) Set up the environment

#### Installation on Linux/macOS

Use a clean conda env dedicated to QGIS—mixing with an existing QGIS install often breaks dependencies.

```bash
conda create -n geo python=3.12
conda activate geo
```

Install core geospatial deps first:

```bash
conda install -c conda-forge --strict-channel-priority gdal rasterio libnetcdf netcdf4
python -c "import rasterio; print('rasterio import successful')"
```

Install GeoAI:

```bash
conda install -c conda-forge geoai
python -c "import geoai; print('geoai import successful')"
```

Install QGIS:

```bash
conda install -c conda-forge qgis
```

Install SamGeo extras (PyPI is required for some parts):

```bash
pip install -U "segment-geospatial[samgeo3]" sam3
python -c "import samgeo; print('samgeo import successful')"
```

#### Installation on Windows

Windows installation requires some additional steps compared to Linux/macOS. Choose the appropriate section based on whether you have an NVIDIA GPU or want CPU-only installation.

**Prerequisites (Required for all Windows users):**

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download) if you haven't already.
2. Open **Anaconda Prompt** (not PowerShell or CMD) for all installation commands.
3. For GPU users: Ensure you have the latest [NVIDIA GPU drivers](https://www.nvidia.com/Download/index.aspx) installed.

##### Option A: Windows with NVIDIA GPU (CUDA)

This option provides the best performance using your NVIDIA GPU for model inference and training.

**Step 1: Create and activate the conda environment**

```bash
conda create -n geo python=3.12 -y
conda activate geo
```

**Step 2: Install PyTorch with CUDA support**

First, check your NVIDIA driver version to determine the compatible CUDA version:

```bash
nvidia-smi
```

Look for the "CUDA Version" in the output. Then install the appropriate PyTorch version:

For CUDA 12.4 (recommended for newer drivers):

```bash
conda install pytorch torchvision pytorch-cuda=12.4 -c pytorch -c nvidia -y
```

For CUDA 12.1 (for older drivers):

```bash
conda install pytorch torchvision pytorch-cuda=12.1 -c pytorch -c nvidia -y
```

**Step 3: Verify PyTorch GPU installation**

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

You should see `CUDA available: True` and your GPU name. If not, see the troubleshooting section below.

**Step 4: Install QGIS and core dependencies**

```bash
conda install -c conda-forge qgis -y
```

**Step 5: Install GeoAI**

```bash
conda install -c conda-forge geoai -y
python -c "import geoai; print('geoai import successful')"
```

**Step 6: Install SamGeo with SAM3 support**

```bash
pip install -U triton-windows
pip install -U "segment-geospatial[samgeo3]"
pip install -U sam3
python -c "import samgeo; print('samgeo import successful')"
```

##### Option B: Windows CPU-Only (No GPU)

Use this option if you don't have an NVIDIA GPU or want a simpler installation.

**Step 1: Create and activate the conda environment**

```bash
conda create -n geo python=3.12 -y
conda activate geo
```

**Step 2: Install PyTorch (CPU version)**

```bash
conda install pytorch torchvision cpuonly -c pytorch -y
```

**Step 3: Verify PyTorch installation**

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print('PyTorch CPU installation successful')"
```

**Step 4: Install QGIS and core dependencies**

```bash
conda install -c conda-forge qgis -y
```

**Step 5: Install GeoAI**

```bash
conda install -c conda-forge geoai -y
python -c "import geoai; print('geoai import successful')"
```

**Step 6: Install SamGeo (without SAM3)**

```bash
pip install segment-geospatial
python -c "import samgeo; print('samgeo import successful')"
```

##### Windows Troubleshooting

**Common Issue 1: CUDA not detected after PyTorch installation**

If `torch.cuda.is_available()` returns `False`:

1. Verify NVIDIA drivers are installed: Run `nvidia-smi` in command prompt
2. Ensure you installed the CUDA-enabled PyTorch (not CPU version)
3. Try reinstalling PyTorch:

```bash
conda uninstall pytorch torchvision -y
conda install pytorch torchvision pytorch-cuda=12.4 -c pytorch -c nvidia -y
```

**Common Issue 2: DLL load failed or missing dependencies**

If you see errors like `DLL load failed` or `ImportError`:

1. Install Microsoft Visual C++ Redistributable:
    - Download and install [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Restart your computer after installation

**Common Issue 3: Triton installation fails**

Triton is required for SAM3 on Windows. If `pip install triton-windows` fails:

1. Ensure you're using Python 3.12 (not 3.13+)
2. Try installing from conda-forge:

```bash
pip install triton-windows --no-cache-dir
```

If Triton still doesn't work, you can skip SAM3 and use SAM1/SAM2 instead.

**Common Issue 4: Permission errors during installation**

Run Anaconda Prompt as Administrator, or try:

```bash
pip install --user <package-name>
```

**Common Issue 5: QGIS fails to start or shows import errors**

Make sure you launch QGIS from the activated conda environment:

```bash
conda activate geo
qgis
```

Do NOT use the QGIS shortcut from the Start Menu—it won't have access to the conda packages.

**Common Issue 6: Out of memory errors**

If you run out of GPU memory:

1. Use the **GPU** button in the GeoAI toolbar to clear memory
2. Close other GPU-intensive applications
3. Use smaller batch sizes in training/inference settings
4. Switch to CPU mode in the plugin settings for smaller tasks

##### Video Tutorial

You can follow this [video tutorial](https://youtu.be/a-Ns9peiuu8) to install the GeoAI QGIS Plugin on Windows:

[![windows](https://github.com/user-attachments/assets/8d89d535-1d66-45d2-a6c0-171416c259c9)](https://youtu.be/a-Ns9peiuu8)

#### Request access to SAM 3

To use SAM 3, you will need to request access by filling out this form on Hugging Face at <https://huggingface.co/facebook/sam3>. Once your request has been approved, run the following command in the terminal to authenticate:

```bash
hf auth login
```

### 2) Install the QGIS plugin

Option A — use QGIS Plugin Manager (recommended):

GeoAI is available as an experimental plugin in the official [QGIS plugin repository](https://plugins.qgis.org/plugins/geoai). To install:

1. Launch QGIS: `conda run qgis`
2. Go to `Plugins` → `Manage and Install Plugins...`
3. Switch to the `All` tab, search for `GeoAI`, select it, and click `Install Plugin`

![](https://github.com/user-attachments/assets/b31d1d13-27ff-420a-84ab-9cc82ade9a8e)

Option B — use the helper script:

```bash
git clone https://github.com/opengeos/geoai.git
cd geoai/qgis_plugin
python install.py
```

This links/copies the plugin into your active QGIS profile. Re-run after pulling updates. Remove with:

```bash
python install.py --remove
```

Option C — manual copy:

-   Copy the `qgis_plugin` folder to your QGIS plugins directory:
    -   Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
    -   Windows: `C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
    -   macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

### 3) Enable in QGIS

Launch QGIS: `conda run qgis`

QGIS → `Plugins` → `Manage and Install Plugins...` → enable `GeoAI`. After updates, toggle the plugin off/on or restart QGIS to reload.

![](https://github.com/user-attachments/assets/1b6dab14-311d-4f62-85aa-1faed73ead5b)

## Usage

### Moondream Vision-Language Model

Sample dataset: [parking_lot.tif](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/parking_lot.tif)

Steps:

1. Click the **Moondream** button in the GeoAI toolbar (or `GeoAI` menu → `Moondream VLM`)
2. Load a Moondream model (default: vikhyatk/moondream2)
3. Select a raster layer or browse for an image file
4. Choose a mode:
    - **Caption**: Generate a description of the image
    - **Query**: Ask a question about the image
    - **Detect**: Detect objects by type (e.g., "building", "car")
    - **Point**: Locate specific objects
5. Click "Run"
6. Results are displayed and optionally added to the map. You can drag the panel to any side of QGIS to keep it out of the way while browsing results. Save the output table or vector layer if you want to reuse detections later.

    ![moondream](https://github.com/user-attachments/assets/bb800a04-b7c4-4fdd-a628-a48842d7eac5)

### Segmentation Panel (Create Data, Train, Inference)

Sample datasets:

-   [naip_rgb_train.tif](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/naip_rgb_train.tif)
-   [naip_test.tif](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/naip_test.tif)
-   [naip_train_buildings.geojson](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/naip_train_buildings.geojson)

Steps:

1. Download the sample datasets (links above) or prepare your own imagery/vector labels. Store them in a folder that is accessible to the conda environment.
2. Click the **Segmentation** button in the GeoAI toolbar (or `GeoAI` menu → `Segmentation`)
3. Use the tabs at the top of the panel to switch between:

    - **Create Training Data**: Select input raster and vector labels, configure tile size and stride, and export tiles to a directory.
    - **Train Model**: Select the images and labels directories, choose model architecture (U-Net, DeepLabV3+, etc.), configure training parameters, and start training.
    - **Run Inference**: Select input raster layer or file, specify the trained model path, configure inference parameters, run inference, and optionally vectorize the results.

    ![data](https://github.com/user-attachments/assets/121fcfa8-6f9b-4413-9419-af666698c053)

    ![train](https://github.com/user-attachments/assets/dfeefb86-ebf7-467c-a5ff-794cde80a7cb)

    ![inference](https://github.com/user-attachments/assets/f0945c01-0fcb-4607-9226-4a3b2bcb05e1)

### SamGeo Panel (Segment Anything Model)

Sample dataset:

-   [uc_berkeley.tif](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/uc_berkeley.tif)
-   [wa_building_image.tif](https://github.com/opengeos/datasets/releases/download/places/wa_building_image.tif)
-   [wa_building_centroids.geojson](https://github.com/opengeos/datasets/releases/download/places/wa_building_centroids.geojson)
-   [wa_building_bboxes.geojson](https://github.com/opengeos/datasets/releases/download/places/wa_building_bboxes.geojson)

Steps:

1. Click the **SamGeo** button in the GeoAI toolbar (or `GeoAI` menu → `SamGeo`)
2. In the **Model** tab:

    - Select the SAM model version (SamGeo3/SAM3, SamGeo2/SAM2, or SamGeo/SAM1)
    - Configure backend (meta or transformers) and device (auto, cuda, cpu)
    - Click "Load Model" to initialize the model
    - Select a raster layer or browse for an image file and click "Set Image"

    ![](https://github.com/user-attachments/assets/600b0879-f851-4423-b668-cb9e8df28425)

3. Choose a segmentation method:

    - **Text Tab**: Enter text prompts describing objects to segment (e.g., "tree, building")

        ![](https://github.com/user-attachments/assets/da2c17fc-4633-488d-ba44-00f1cd97555c)

    - **Interactive Tab**:

        - Click "Add Foreground Points" or "Add Background Points" and click on the map
        - Or click "Draw Box" and drag a rectangle on the map
        - Click "Segment by Points" or "Segment by Box"

        ![](https://github.com/user-attachments/assets/6730737d-62fc-438a-bff5-cffb685d391e)

    - **Batch Tab**: Add multiple points interactively or load from a vector file/layer

        ![](https://github.com/user-attachments/assets/104ec741-44cc-404a-9213-36cf78456171)

4. In the **Output** tab:

    - Select output format (Raster GeoTIFF, Vector GeoPackage, or Vector Shapefile)
    - For vector output, optionally enable regularization:
        - Check "Regularize polygons (orthogonalize)"
        - Set Epsilon (simplification tolerance) and Min Area (filter small polygons)
    - Click "Save Masks" to export results

    ![](https://github.com/user-attachments/assets/5c80cc57-3870-4a20-bb74-73e394ef22a6)

### Clear GPU Memory

Click the **GPU** button in the GeoAI toolbar to release GPU memory from all loaded models (Moondream, SamGeo, etc.) and clear CUDA cache. Use this frequently when switching between large models to prevent out-of-memory errors.

![](https://github.com/user-attachments/assets/76c9dd8a-581c-4975-9ecb-4bfe301447bd)

### Plugin Update Checker

Go to `GeoAI` menu → `Check for Updates...` to see if a newer version of the GeoAI plugin is available. Click on the `Check for Updates` button to fetch the latest version info from GitHub. If an update is found, click the `Download and Install Update` button to download and install the latest version automatically. Restart QGIS to apply the update.

![](https://github.com/user-attachments/assets/cc0dfd38-9b41-4735-9af0-c49b7aa71b72)

## Supported Model Architectures (Segmentation)

The QGIS plugin supports any models supported by [Pytorch Segmentation Models](https://smp.readthedocs.io/en/latest/models.html), including:

-   U-Net
-   U-Net++
-   DeepLabV3
-   DeepLabV3+
-   FPN (Feature Pyramid Network)
-   PSPNet
-   LinkNet
-   MANet
-   PAN
-   UperNet
-   SegFormer
-   DPT

## Supported Encoders (Segmentation)

-   ResNet (34, 50, 101, 152)
-   EfficientNet (b0-b4)
-   MobileNetV2
-   VGG (16, 19)

## Supported SAM Models (SamGeo)

-   **SamGeo3 (SAM3)**: Latest version with text prompts, point prompts, and box prompts
-   **SamGeo2 (SAM2)**: Improved version with better performance
-   **SamGeo (SAM1)**: Original Segment Anything Model

## Troubleshooting

-   Plugin missing after install: confirm the plugin folder exists in your QGIS profile path and that you restarted QGIS.
-   GDAL/rasterio errors: verify you launched QGIS from the conda env (`conda activate geo` then `qgis`) so it picks up the same Python libs.
-   CUDA OOM: use the **GPU** button to clear cache, lower batch sizes, or switch to CPU for smaller runs.
-   Model download failures: check network/firewall, then retry loading models from the panel.

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Links

-   [GeoAI Documentation](https://opengeoai.org)
-   [SamGeo Documentation](https://samgeo.gishub.org)
-   [GitHub Repository](https://github.com/opengeos/geoai)
-   [Report Issues](https://github.com/opengeos/geoai/issues)


> Source: `docs/data_engineering/geoai/qgis_plugin/README.md`

# QGIS Plugin for GeoAI

A QGIS plugin that brings the [geoai](https://github.com/opengeos/geoai) models into dockable panels (Moondream VLM, segmentation training/inference, SamGeo) so you can keep QGIS as your main workspace while experimenting with GeoAI.

## Quick Start

-   Create a fresh conda env (`conda create -n geo python=3.12`) and install QGIS + deps (see below).
-   Install the plugin (`python install.py`) from this repo.
-   Restart QGIS → `Plugins` → `Manage and Install Plugins...` → enable `GeoAI`.
-   Open a GeoAI toolbar panel and try the sample datasets below.

## Video Tutorials

Check out this [short video demo](https://youtu.be/Esr_e6_P1is) and [full video tutorial](https://youtu.be/8-OhlqeoyiY) on how to use the GeoAI plugin in QGIS.

[![demo](https://github.com/user-attachments/assets/5aabc3d3-efd1-4011-ab31-2b3f11aab3ed)](https://youtu.be/8-OhlqeoyiY)

## Requirements

-   QGIS 3.28 or later
-   Python 3.10+ (conda recommended)
-   PyTorch (CUDA if you want GPU acceleration)
-   `geoai` and `samgeo` packages

## Features

Each tool lives inside a dockable panel that can be attached to either side of the QGIS interface, so you can keep layers, maps, and models visible simultaneously.

### Moondream Vision-Language Model Panel

-   **Caption**: Generate descriptions of geospatial imagery (short, normal, or long)
-   **Query**: Ask questions about images using natural language
-   **Detect**: Detect and locate objects with bounding boxes
-   **Point**: Locate specific objects with point markers

### Segmentation Panel (Combined Training & Inference)

-   **Tab 1 - Create Training Data**: Export GeoTIFF tiles from raster and vector data
-   **Tab 2 - Train Models**: Train custom segmentation models (U-Net, DeepLabV3+, FPN, etc.)
-   **Tab 3 - Run Inference**: Apply trained models to new imagery and vectorize results. Vector outputs can optionally be smoothed or simplified for immediate use in GIS workflows.

### SamGeo Panel (Segment Anything Model)

-   **Model Tab**: Load SAM models (SAM1, SAM2, or SAM3) with configurable backend and device settings
-   **Text Tab**: Segment objects using text prompts (e.g., "tree", "building", "road")
-   **Interactive Tab**: Segment using point prompts (foreground/background) or box prompts drawn on the map
-   **Batch Tab**: Process multiple points interactively or from vector files/layers
-   **Output Tab**: Save results as raster (GeoTIFF) or vector (GeoPackage, Shapefile) with optional regularization (orthogonalize polygons, filter by minimum area)

### GPU Memory Management

-   **Clear GPU Memory**: Release GPU memory and clear CUDA cache for all loaded models

## Installation

### 1) Set up the environment

#### Installation on Linux/macOS

Use a clean conda env dedicated to QGIS—mixing with an existing QGIS install often breaks dependencies.

```bash
conda create -n geo python=3.12
conda activate geo
```

Install core geospatial deps first:

```bash
conda install -c conda-forge --strict-channel-priority gdal rasterio libnetcdf netcdf4
python -c "import rasterio; print('rasterio import successful')"
```

Install GeoAI:

```bash
conda install -c conda-forge geoai
python -c "import geoai; print('geoai import successful')"
```

Install QGIS:

```bash
conda install -c conda-forge qgis
```

Install SamGeo extras (PyPI is required for some parts):

```bash
pip install -U "segment-geospatial[samgeo3]" sam3
python -c "import samgeo; print('samgeo import successful')"
```

#### Installation on Windows

Windows installation requires some additional steps compared to Linux/macOS. Choose the appropriate section based on whether you have an NVIDIA GPU or want CPU-only installation.

**Prerequisites (Required for all Windows users):**

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/download) if you haven't already.
2. Open **Anaconda Prompt** (not PowerShell or CMD) for all installation commands.
3. For GPU users: Ensure you have the latest [NVIDIA GPU drivers](https://www.nvidia.com/Download/index.aspx) installed.

##### Option A: Windows with NVIDIA GPU (CUDA)

This option provides the best performance using your NVIDIA GPU for model inference and training.

**Step 1: Create and activate the conda environment**

```bash
conda create -n geo python=3.12 -y
conda activate geo
```

**Step 2: Install PyTorch with CUDA support**

First, check your NVIDIA driver version to determine the compatible CUDA version:

```bash
nvidia-smi
```

Look for the "CUDA Version" in the output. Then install the appropriate PyTorch version:

For CUDA 12.4 (recommended for newer drivers):

```bash
conda install pytorch torchvision pytorch-cuda=12.4 -c pytorch -c nvidia -y
```

For CUDA 12.1 (for older drivers):

```bash
conda install pytorch torchvision pytorch-cuda=12.1 -c pytorch -c nvidia -y
```

**Step 3: Verify PyTorch GPU installation**

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

You should see `CUDA available: True` and your GPU name. If not, see the troubleshooting section below.

**Step 4: Install QGIS and core dependencies**

```bash
conda install -c conda-forge qgis -y
```

**Step 5: Install GeoAI**

```bash
conda install -c conda-forge geoai -y
python -c "import geoai; print('geoai import successful')"
```

**Step 6: Install SamGeo with SAM3 support**

```bash
pip install -U triton-windows
pip install -U "segment-geospatial[samgeo3]"
pip install -U sam3
python -c "import samgeo; print('samgeo import successful')"
```

##### Option B: Windows CPU-Only (No GPU)

Use this option if you don't have an NVIDIA GPU or want a simpler installation.

**Step 1: Create and activate the conda environment**

```bash
conda create -n geo python=3.12 -y
conda activate geo
```

**Step 2: Install PyTorch (CPU version)**

```bash
conda install pytorch torchvision cpuonly -c pytorch -y
```

**Step 3: Verify PyTorch installation**

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print('PyTorch CPU installation successful')"
```

**Step 4: Install QGIS and core dependencies**

```bash
conda install -c conda-forge qgis -y
```

**Step 5: Install GeoAI**

```bash
conda install -c conda-forge geoai -y
python -c "import geoai; print('geoai import successful')"
```

**Step 6: Install SamGeo (without SAM3)**

```bash
pip install segment-geospatial
python -c "import samgeo; print('samgeo import successful')"
```

##### Windows Troubleshooting

**Common Issue 1: CUDA not detected after PyTorch installation**

If `torch.cuda.is_available()` returns `False`:

1. Verify NVIDIA drivers are installed: Run `nvidia-smi` in command prompt
2. Ensure you installed the CUDA-enabled PyTorch (not CPU version)
3. Try reinstalling PyTorch:

```bash
conda uninstall pytorch torchvision -y
conda install pytorch torchvision pytorch-cuda=12.4 -c pytorch -c nvidia -y
```

**Common Issue 2: DLL load failed or missing dependencies**

If you see errors like `DLL load failed` or `ImportError`:

1. Install Microsoft Visual C++ Redistributable:
    - Download and install [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Restart your computer after installation

**Common Issue 3: Triton installation fails**

Triton is required for SAM3 on Windows. If `pip install triton-windows` fails:

1. Ensure you're using Python 3.12 (not 3.13+)
2. Try installing from conda-forge:

```bash
pip install triton-windows --no-cache-dir
```

If Triton still doesn't work, you can skip SAM3 and use SAM1/SAM2 instead.

**Common Issue 4: Permission errors during installation**

Run Anaconda Prompt as Administrator, or try:

```bash
pip install --user <package-name>
```

**Common Issue 5: QGIS fails to start or shows import errors**

Make sure you launch QGIS from the activated conda environment:

```bash
conda activate geo
qgis
```

Do NOT use the QGIS shortcut from the Start Menu—it won't have access to the conda packages.

**Common Issue 6: Out of memory errors**

If you run out of GPU memory:

1. Use the **GPU** button in the GeoAI toolbar to clear memory
2. Close other GPU-intensive applications
3. Use smaller batch sizes in training/inference settings
4. Switch to CPU mode in the plugin settings for smaller tasks

##### Video Tutorial

You can follow this [video tutorial](https://youtu.be/a-Ns9peiuu8) to install the GeoAI QGIS Plugin on Windows:

[![windows](https://github.com/user-attachments/assets/8d89d535-1d66-45d2-a6c0-171416c259c9)](https://youtu.be/a-Ns9peiuu8)

#### Request access to SAM 3

To use SAM 3, you will need to request access by filling out this form on Hugging Face at <https://huggingface.co/facebook/sam3>. Once your request has been approved, run the following command in the terminal to authenticate:

```bash
hf auth login
```

### 2) Install the QGIS plugin

Option A — use QGIS Plugin Manager (recommended):

GeoAI is available as an experimental plugin in the official [QGIS plugin repository](https://plugins.qgis.org/plugins/geoai). To install:

1. Launch QGIS: `conda run qgis`
2. Go to `Plugins` → `Manage and Install Plugins...`
3. Switch to the `All` tab, search for `GeoAI`, select it, and click `Install Plugin`

![](https://github.com/user-attachments/assets/b31d1d13-27ff-420a-84ab-9cc82ade9a8e)

Option B — use the helper script:

```bash
git clone https://github.com/opengeos/geoai.git
cd geoai/qgis_plugin
python install.py
```

This links/copies the plugin into your active QGIS profile. Re-run after pulling updates. Remove with:

```bash
python install.py --remove
```

Option C — manual copy:

-   Copy the `qgis_plugin` folder to your QGIS plugins directory:
    -   Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
    -   Windows: `C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
    -   macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

### 3) Enable in QGIS

Launch QGIS: `conda run qgis`

QGIS → `Plugins` → `Manage and Install Plugins...` → enable `GeoAI`. After updates, toggle the plugin off/on or restart QGIS to reload.

![](https://github.com/user-attachments/assets/1b6dab14-311d-4f62-85aa-1faed73ead5b)

## Usage

### Moondream Vision-Language Model

Sample dataset: [parking_lot.tif](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/parking_lot.tif)

Steps:

1. Click the **Moondream** button in the GeoAI toolbar (or `GeoAI` menu → `Moondream VLM`)
2. Load a Moondream model (default: vikhyatk/moondream2)
3. Select a raster layer or browse for an image file
4. Choose a mode:
    - **Caption**: Generate a description of the image
    - **Query**: Ask a question about the image
    - **Detect**: Detect objects by type (e.g., "building", "car")
    - **Point**: Locate specific objects
5. Click "Run"
6. Results are displayed and optionally added to the map. You can drag the panel to any side of QGIS to keep it out of the way while browsing results. Save the output table or vector layer if you want to reuse detections later.

    ![moondream](https://github.com/user-attachments/assets/bb800a04-b7c4-4fdd-a628-a48842d7eac5)

### Segmentation Panel (Create Data, Train, Inference)

Sample datasets:

-   [naip_rgb_train.tif](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/naip_rgb_train.tif)
-   [naip_test.tif](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/naip_test.tif)
-   [naip_train_buildings.geojson](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/naip_train_buildings.geojson)

Steps:

1. Download the sample datasets (links above) or prepare your own imagery/vector labels. Store them in a folder that is accessible to the conda environment.
2. Click the **Segmentation** button in the GeoAI toolbar (or `GeoAI` menu → `Segmentation`)
3. Use the tabs at the top of the panel to switch between:

    - **Create Training Data**: Select input raster and vector labels, configure tile size and stride, and export tiles to a directory.
    - **Train Model**: Select the images and labels directories, choose model architecture (U-Net, DeepLabV3+, etc.), configure training parameters, and start training.
    - **Run Inference**: Select input raster layer or file, specify the trained model path, configure inference parameters, run inference, and optionally vectorize the results.

    ![data](https://github.com/user-attachments/assets/121fcfa8-6f9b-4413-9419-af666698c053)

    ![train](https://github.com/user-attachments/assets/dfeefb86-ebf7-467c-a5ff-794cde80a7cb)

    ![inference](https://github.com/user-attachments/assets/f0945c01-0fcb-4607-9226-4a3b2bcb05e1)

### SamGeo Panel (Segment Anything Model)

Sample dataset:

-   [uc_berkeley.tif](https://huggingface.co/datasets/giswqs/geospatial/resolve/main/uc_berkeley.tif)
-   [wa_building_image.tif](https://github.com/opengeos/datasets/releases/download/places/wa_building_image.tif)
-   [wa_building_centroids.geojson](https://github.com/opengeos/datasets/releases/download/places/wa_building_centroids.geojson)
-   [wa_building_bboxes.geojson](https://github.com/opengeos/datasets/releases/download/places/wa_building_bboxes.geojson)

Steps:

1. Click the **SamGeo** button in the GeoAI toolbar (or `GeoAI` menu → `SamGeo`)
2. In the **Model** tab:

    - Select the SAM model version (SamGeo3/SAM3, SamGeo2/SAM2, or SamGeo/SAM1)
    - Configure backend (meta or transformers) and device (auto, cuda, cpu)
    - Click "Load Model" to initialize the model
    - Select a raster layer or browse for an image file and click "Set Image"

    ![](https://github.com/user-attachments/assets/600b0879-f851-4423-b668-cb9e8df28425)

3. Choose a segmentation method:

    - **Text Tab**: Enter text prompts describing objects to segment (e.g., "tree, building")

        ![](https://github.com/user-attachments/assets/da2c17fc-4633-488d-ba44-00f1cd97555c)

    - **Interactive Tab**:

        - Click "Add Foreground Points" or "Add Background Points" and click on the map
        - Or click "Draw Box" and drag a rectangle on the map
        - Click "Segment by Points" or "Segment by Box"

        ![](https://github.com/user-attachments/assets/6730737d-62fc-438a-bff5-cffb685d391e)

    - **Batch Tab**: Add multiple points interactively or load from a vector file/layer

        ![](https://github.com/user-attachments/assets/104ec741-44cc-404a-9213-36cf78456171)

4. In the **Output** tab:

    - Select output format (Raster GeoTIFF, Vector GeoPackage, or Vector Shapefile)
    - For vector output, optionally enable regularization:
        - Check "Regularize polygons (orthogonalize)"
        - Set Epsilon (simplification tolerance) and Min Area (filter small polygons)
    - Click "Save Masks" to export results

    ![](https://github.com/user-attachments/assets/5c80cc57-3870-4a20-bb74-73e394ef22a6)

### Clear GPU Memory

Click the **GPU** button in the GeoAI toolbar to release GPU memory from all loaded models (Moondream, SamGeo, etc.) and clear CUDA cache. Use this frequently when switching between large models to prevent out-of-memory errors.

![](https://github.com/user-attachments/assets/76c9dd8a-581c-4975-9ecb-4bfe301447bd)

### Plugin Update Checker

Go to `GeoAI` menu → `Check for Updates...` to see if a newer version of the GeoAI plugin is available. Click on the `Check for Updates` button to fetch the latest version info from GitHub. If an update is found, click the `Download and Install Update` button to download and install the latest version automatically. Restart QGIS to apply the update.

![](https://github.com/user-attachments/assets/cc0dfd38-9b41-4735-9af0-c49b7aa71b72)

## Supported Model Architectures (Segmentation)

The QGIS plugin supports any models supported by [Pytorch Segmentation Models](https://smp.readthedocs.io/en/latest/models.html), including:

-   U-Net
-   U-Net++
-   DeepLabV3
-   DeepLabV3+
-   FPN (Feature Pyramid Network)
-   PSPNet
-   LinkNet
-   MANet
-   PAN
-   UperNet
-   SegFormer
-   DPT

## Supported Encoders (Segmentation)

-   ResNet (34, 50, 101, 152)
-   EfficientNet (b0-b4)
-   MobileNetV2
-   VGG (16, 19)

## Supported SAM Models (SamGeo)

-   **SamGeo3 (SAM3)**: Latest version with text prompts, point prompts, and box prompts
-   **SamGeo2 (SAM2)**: Improved version with better performance
-   **SamGeo (SAM1)**: Original Segment Anything Model

## Troubleshooting

-   Plugin missing after install: confirm the plugin folder exists in your QGIS profile path and that you restarted QGIS.
-   GDAL/rasterio errors: verify you launched QGIS from the conda env (`conda activate geo` then `qgis`) so it picks up the same Python libs.
-   CUDA OOM: use the **GPU** button to clear cache, lower batch sizes, or switch to CPU for smaller runs.
-   Model download failures: check network/firewall, then retry loading models from the panel.

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Links

-   [GeoAI Documentation](https://opengeoai.org)
-   [SamGeo Documentation](https://samgeo.gishub.org)
-   [GitHub Repository](https://github.com/opengeos/geoai)
-   [Report Issues](https://github.com/opengeos/geoai/issues)


## Research & Patterns


> Source: `docs/data_engineering/geoai/Geospatial Data Visualization with Ibis.md`

# **Modernizing Educational Geospatial Intelligence: A Comprehensive Architectural Analysis of Ibis, DuckDB, GeoParquet, and React**

## **1\. Executive Context: The Evolution of Spatial Analytics in Education**

The administration and strategic planning of educational systems are fundamentally spatial challenges. Every decision—from delineating school district boundaries and optimizing bus transportation routes to analyzing the equitable distribution of resources and projecting future enrollment based on demographic shifts—relies on the precise understanding of location. Historically, the management of this geospatial educational data has been bifurcated. On one hand, administrative data (enrollment, grades, funding) resided in structured Relational Database Management Systems (RDBMS) or simple spreadsheets. On the other hand, spatial data (boundaries, facility locations) was locked within specialized, desktop-bound Geographic Information Systems (GIS) accessible only to a few experts.  
This report details a paradigm shift towards a unified, cloud-native architecture that democratizes access to this critical intelligence. By integrating **DuckDB** as a high-performance in-process analytical engine, **Ibis** as a portable Pythonic interface, and **GeoParquet** as an optimized columnar storage format, educational organizations can achieve analytical speeds ranging from 3 to 25 times faster than traditional workflows.1 Furthermore, by coupling this backend with a modern frontend ecosystem built on **React**, **shadcn/ui**, and **Deck.gl**, it becomes possible to deliver interactive, web-based dashboards that empower stakeholders—superintendents, parents, and policy-makers—to explore complex spatial relationships in real-time.  
The analysis that follows is an exhaustive exploration of this stack. It moves beyond high-level abstractions to provide a granular engineering blueprint. We will examine the specific patterns for ingesting and transforming educational data, the mechanisms of vectorized spatial execution, and the precise composition of React components required to build professional-grade interfaces. The goal is to provide a definitive guide for displaying geospatial educational data that is not only robust and scalable but also capable of adapting to the exploding volume of data inherent in modern governance.

### **1.1 The Imperative for High-Performance Geospatial Systems**

In the context of education, "big data" is a reality. A state-level education department might manage thousands of schools, tens of thousands of bus routes, and millions of student records. Traditional analysis methods, often involving the serial processing of Shapefiles or the sluggish parsing of GeoJSON in a browser, are failing to meet the demand for rapid insight.  
Benchmarks presented in recent research illustrate the magnitude of the inefficiency in legacy systems. For instance, running aggregate summary statistics on large vector datasets, such as the 75 GB National Wetlands Inventory, historically took hours using file-based approaches. With the adoption of DuckDB and Parquet, these same operations are completed in seconds.1 For an educational planner, this difference is transformative. It changes a query like "How many students in the entire state live within a flood zone?" from an overnight batch job into an interactive question that can be refined and re-run during a meeting.

### **1.2 The Cloud-Native Geospatial Paradigm**

The architecture proposed in this report aligns with the Cloud-Native Geospatial (CNG) paradigm. This approach prioritizes formats and protocols that are optimized for the cloud environment—specifically object storage (like AWS S3) and HTTP range requests—rather than local file systems.  
**Key tenets of this paradigm as applied to educational data include:**

* **Separation of Compute and Storage:** Data resides in static, highly compressed GeoParquet files. Compute is ephemeral, spun up only when a query is run via DuckDB.  
* **Columnar Efficiency:** Unlike row-oriented formats (CSV, Shapefile) which force the engine to read entire records, columnar formats allow the engine to read only the specific attributes needed (e.g., just the "Geometry" and "Math\_Score" columns), drastically reducing I/O.  
* **Zero-Copy Transfer:** Technologies like **GeoArrow** allow data to move from the disk to the database memory and finally to the visualization layer without costly serialization and deserialization steps.1

By adopting these patterns, educational institutions can move away from maintaining expensive, always-on PostGIS servers and towards a serverless, scalable, and cost-effective infrastructure.

## **2\. The Analytical Engine: DuckDB and Ibis**

The core of this modern stack is the interaction between DuckDB, the execution engine, and Ibis, the expression language. Understanding the mechanics of this pairing is essential for engineering robust pipelines for educational data.

### **2.1 DuckDB: The Vectorized Powerhouse**

DuckDB is designed to be the "SQLite for Analytics." It runs in-process, meaning it has no external server dependency, yet it offers the power of a full OLAP (Online Analytical Processing) database. Its performance on geospatial workloads is driven by several architectural decisions.

#### **Vectorized Execution**

Traditional databases process data one row at a time. DuckDB uses vectorized execution, processing data in batches (vectors) that fit into the CPU's cache. This is particularly advantageous for geospatial calculations. When calculating the distance between student homes and schools (ST\_Distance), DuckDB can load the coordinates of thousands of students into the CPU registers and apply the distance formula in a single SIMD (Single Instruction, Multiple Data) operation. This architectural trait is responsible for the massive speedups—up to 25x faster analysis—observed in benchmarks over the last three years.1

#### **The Spatial Extension**

DuckDB does not implement geospatial logic from scratch. Instead, it bundles and binds to the industry-standard open-source libraries:

* **GEOS (Geometry Engine \- Open Source):** Handles the fundamental geometric predicates (Contains, Intersects, Touches) and operations (Buffer, Union, Intersection).  
* **GDAL (Geospatial Data Abstraction Library):** Provides the I/O capabilities to read over 50 geospatial formats.1 This is crucial for education departments that may have legacy data in obscure formats.  
* **PROJ:** Manages Coordinate Reference Systems (CRS) and transformations (ST\_Transform).

This integration means that DuckDB is not just a fast calculator; it is a full-fledged GIS that can perform complex spatial joins—such as associating millions of student addresses (points) with school attendance zones (polygons)—using optimized R-Tree indexes to prune the search space efficiently.1

### **2.2 Ibis: The Portable Interface**

While DuckDB provides the raw horsepower, Ibis provides the steering wheel. Ibis is a Python library that provides a dataframe API similar to pandas, but with a fundamentally different execution model.

#### **Deferred Execution**

When a data scientist writes code in pandas, every operation is executed immediately in memory. If the dataset is larger than the machine's RAM, the process crashes. Ibis uses **deferred execution**.

* **Mechanism:** When a user defines a transformation in Ibis (e.g., schools.filter(schools.type \== 'Public')), Ibis does not touch the data. Instead, it builds an internal expression graph representing that operation.  
* **Compilation:** Only when the user explicitly requests the result (e.g., .execute() or .to\_parquet()), Ibis compiles the expression graph into the native dialect of the backend—in this case, optimized DuckDB SQL—and sends it for execution.

#### **Why This Matters for Educational Data**

Educational datasets are often composed of multiple disparate sources that need to be joined:

1. **Facilities Database:** Physical attributes of school buildings (SQL database).  
2. **Student Information System (SIS):** Demographics and grades (CSV exports).  
3. **Geographic Boundaries:** District lines and hazard zones (Shapefiles).

With Ibis, a developer can write a coherent Python script that joins these sources logically. Ibis abstracts the complexity of the underlying SQL joins and spatial predicates. The snippet highlights that Ibis interfaces to 15+ query engines.1 This offers future-proofing: if the educational agency migrates from a local DuckDB instance to a cloud warehouse like BigQuery or Snowflake in the future, the Ibis analysis code remains largely unchanged.

## **3\. Data Engineering Patterns for Educational Intelligence**

To display the "attached type of data" (educational records) effectively, one must first master the data engineering patterns required to ingest, clean, and structure it. The following sections detail these patterns, integrating the specific techniques outlined in the research material.

### **3.1 Ingestion and Geometry Construction**

Educational data rarely arrives in a clean, geospatial format. It typically exists as flat files (CSVs) with separate columns for Latitude and Longitude.  
Pattern: Constructing Geometries  
The first step in any pipeline is converting these coordinates into true geometric objects that the spatial engine can reason about.

* **Raw Input:** A CSV file schools.csv with columns lat and lon.  
* **Ibis Operation:** Use the ST\_Point function.  
  Python  
  \# Conceptual Ibis implementation based on snippet patterns  
  schools \= ibis.read\_csv("schools.csv")  
  schools \= schools.mutate(  
      geometry \= ibis.geo.point(schools.lon, schools.lat)  
  )

  This seemingly simple operation transforms the data from "text" to "spatial features." As noted in the snippets, DuckDB leverages GDAL to support mixing and matching these newly created geometries with other data types.1

### **3.2 Coordinate Reference System (CRS) Normalization**

A critical and often overlooked aspect of geospatial data is the Coordinate Reference System.

* **The Problem:** Administrative data usually comes in "State Plane" coordinates (measured in feet or meters) because they offer high accuracy for local measurements. Web mapping libraries (like Deck.gl or Leaflet) require WGS84 (Latitude/Longitude, EPSG:4326).  
* **The Solution:** Implicit in the research is the use of ST\_Transform. A robust pipeline must standardize all inputs.  
  * **Snippet Reference:** ST\_Transform(pickup\_point, 'EPSG:4326', 'ESRI:102718').1  
  * **Educational Context:** To calculate the "walking distance" for bus eligibility, one might transform *to* a projected system (like ESRI:102718) to measure in feet. To display the schools on a map, one transforms *back* to EPSG:4326.  
  * **Implementation:**  
    Python  
    \# Transform for analysis (Feet)  
    schools\_projected \= schools.mutate(  
        geom\_feet \= schools.geometry.transform("ESRI:102718")  
    )  
    \# Transform for display (Lat/Lon)  
    schools\_display \= schools.mutate(  
        geom\_web \= schools.geometry.transform("EPSG:4326")  
    )

### **3.3 Spatial Joins and Catchment Analysis**

The most valuable insights in education planning come from the relationship between different layers.

* **The Query:** "Which school district is this student in?" or "How many students live within 1 mile of this bus stop?"  
* **The Mechanism:** This requires a **Spatial Join**.  
  * DuckDB uses an **R-Tree index** to optimize these joins.1 An R-Tree groups nearby objects into bounding boxes. When checking if a student is inside a district polygon, the engine first checks the bounding box. If the student is outside the box, the expensive "point-in-polygon" math is skipped.  
* **Performance Implication:** For a dataset of 1 million students and 500 districts, a brute-force approach would require 500 million checks. With R-Tree indexing, this is reduced to a fraction of the operations, enabling the sub-second performance noted in the benchmarks.1

### **3.4 Temporal Aggregation**

Educational data is longitudinal. We track attendance daily, test scores yearly, and enrollment continuously.

* **Snippet Insight:** The benchmarks explicitly track "Window Functions" and "Analysis Group By" performance over time.1  
* **Application:** We can analyze trends such as "Shifts in Student Center of Gravity over 10 Years."  
  * By grouping student locations by Year and calculating the ST\_Centroid of the population, administrators can visualize how the demand for schools is drifting geographically. DuckDB's columnar nature makes aggregating across the Year column exceptionally fast.

## **4\. The Persistence Layer: GeoParquet**

Once the data is processed, it must be stored efficiently. The research strongly advocates for **GeoParquet**.1

### **4.1 Comparison of Formats**

| Feature | Shapefile | GeoJSON | GeoParquet |
| :---- | :---- | :---- | :---- |
| **Type** | Binary (Multi-file) | Text (JSON) | Binary (Columnar) |
| **Parsing Speed** | Slow | Very Slow | **Fast (Parallel)** |
| **Compression** | Poor | None (Verbose) | **Excellent (Snappy/Zstd)** |
| **Cloud Native** | No | No | **Yes (Range Requests)** |
| **Metadata** | Sidecar (.prj) | No Standard | **Embedded (WKB/Proj)** |

### **4.2 Why GeoParquet for Education?**

1. **Compression:** Educational budgets are often tight. Storing historical GPS logs from bus fleets in CSV or JSON is prohibitively expensive. GeoParquet's compression can reduce storage footprints by 90% 1, resulting in direct cost savings.  
2. **Selective I/O:** If a dashboard only needs to show the "School Name" and "Location," GeoParquet allows the engine to read *only* those two columns. A Shapefile or GeoJSON would require reading the entire file, including heavy columns like "School\_Mission\_Statement" or "Funding\_History," wasting bandwidth and time.  
3. **Interoperability:** The snippet notes that GeoParquet is becoming the standard for geospatial data in the cloud.1 Using this format ensures that the data is not locked into a proprietary vendor ecosystem.

## **5\. Frontend Architecture: React and Shadcn/ui**

The user query specifically requests assistance finding relevant **shadcn/ui** and **React** components to display this data. This section translates the backend capabilities into a concrete frontend implementation plan.

### **5.1 The Shadcn/ui Philosophy**

Shadcn/ui is not a typical component library. It is a collection of re-usable components built on **Radix UI** (for headless, accessible functionality) and **Tailwind CSS** (for styling) that you copy and paste into your codebase.

* **Relevance:** Geospatial dashboards are complex applications that often require breaking out of standard "Bootstrap" or "Material Design" constraints. Shadcn allows for complete customization of the component logic and style, which is essential when overlaying UI on top of complex maps.

### **5.2 Component Selection and Composition**

To build a "School District Explorer," we require a specific set of components arranged in a coherent layout.

#### **A. Layout and Chrome: ResizablePanel**

The defining characteristic of a GIS application is the need to balance the Map View with the Data View.

* **Component:** shadcn/ui/resizable  
* **Implementation:** Use a ResizablePanelGroup with a horizontal direction.  
  * **Left Panel (Sidebar):** Contains filters, search, and details. Default width: 25%.  
  * **Right Panel (Map):** Contains the Deck.gl canvas. Default width: 75%.  
  * **Handle:** A ResizableHandle allows the user to drag the divider. If they are analyzing a spreadsheet of test scores, they can drag the sidebar to be wider. If they are exploring bus routes visually, they can minimize it.

#### **B. Search and Discovery: Command**

Users need to find specific entities quickly (e.g., "Find Lincoln High School").

* **Component:** shadcn/ui/command (wrapping cmdk).  
* **Integration:**  
  * This component provides a fuzzy-searchable modal or inline list.  
  * **Pattern:** Connect the onValueChange event to a debounced API call to the DuckDB backend. As the user types "Linc", the backend runs a SQL LIKE '%Linc%' query and returns matches instantly.  
  * **UX:** Use CommandGroup to separate results by type: "Schools", "Districts", "Bus Stops".

#### **C. Filtering Controls: Popover, Calendar, Slider**

* **Date Selection:** Educational data is time-sensitive.  
  * **Component:** shadcn/ui/calendar inside a shadcn/ui/popover.  
  * **Usage:** "View Attendance Rates for:."  
* **Metric Filtering:**  
  * **Component:** shadcn/ui/slider.  
  * **Usage:** "Student/Teacher Ratio: 10 \- 30". A dual-thumb slider allows users to define a min/max range. This triggers a backend update to filter the GeoParquet scan.  
* **Categorical Filtering:**  
  * **Component:** shadcn/ui/toggle-group.  
  * **Usage:** "School Level: \[Elem\]\[Middle\]\[High\]". Toggles allow for quick additive filtering.

#### **D. Data Display: Table and Sheet**

* **Tabular Data:**  
  * **Component:** shadcn/ui/table (integrated with TanStack Table).  
  * **Usage:** Display the attributes of the schools currently visible in the map viewport.  
  * **Pattern:** This table should be virtualized (using tanstack-virtual) if displaying thousands of rows to maintain 60fps performance.  
* **Detailed Inspection:**  
  * **Component:** shadcn/ui/sheet.  
  * **Usage:** When a user clicks a school on the map, a "Sheet" slides in from the right side of the screen.  
  * **Content:** This sheet contains the full dossier of the school: charts of historical performance, contact info, and lists of feeder neighborhoods. This keeps the user in the context of the map without navigating to a new page.

### **5.3 State Management**

To synchronize these components with the map, robust state management is required.

* **Zustand:** Recommended for global UI state.  
  * *Store:* useMapStore. Holds: viewState (lat/lon/zoom), selectedSchoolId, hoveredDistrictId, filters.  
* **React Query (TanStack Query):** Recommended for data fetching.  
  * *Query:* useSchools(filters). This hook calls the API. It handles caching, loading states, and refetching when the filters state in Zustand changes.

## **6\. Visualization Strategy: Deck.gl and GeoArrow**

The research snippet emphasizes the use of **Lonboard**, **Deck.gl**, and **Apache Arrow**.1 This is the "rendering engine" of the application.

### **6.1 The Performance Bottleneck of GeoJSON**

In a standard web map (Leaflet), the browser performs the following steps to render data:

1. Server sends JSON text.  
2. Browser parses JSON string into JavaScript Objects.  
3. Browser iterates over objects to extract coordinates.  
4. Browser creates internal arrays.  
5. Data is sent to the DOM (SVG) or Canvas.

This process is CPU-intensive. For 10,000 points, it causes the interface to freeze.

### **6.2 The GeoArrow Solution**

The snippet highlights **GeoArrow** as a way of representing geospatial vector data in memory.1

* **Mechanism:** DuckDB reads the GeoParquet file (which is binary). It outputs an **Arrow Table** (also binary). This binary blob is sent over the network.  
* **Zero-Copy:** The browser receives the Arrow binary. **Deck.gl** (via the @deck.gl/arrow-layers or lonboard loaders) can read this binary data *directly* into the GPU buffers without parsing it into JavaScript objects.  
* **Result:** The browser can render millions of points with 60fps performance because the main thread is bypassed. This is what enables the "visualize millions of geometries in one line of code" capability mentioned in the research.1

### **6.3 Layer Configuration for Education**

1. **ScatterplotLayer (Schools):**  
   * Renders circles at school coordinates.  
   * *Visual Encodings:*  
     * Radius: Proportional to Enrollment.  
     * Color: Diverging scale based on Academic Rating (Red \-\> Green).  
2. **GeoJsonLayer (Districts/Catchments):**  
   * Renders polygon boundaries.  
   * *Interactivity:* filled: false (transparent) normally, filled: true on hover to highlight the district.  
3. **PathLayer (Bus Routes):**  
   * Renders lines for transportation.  
   * *Optimization:* Use widthScale to represent capacity or ridership load.

## **7\. Deep Insights and Strategic Implications**

Analysis of the research materials reveals several second-order insights that extend beyond simple implementation details.

### **7.1 The Demise of the "GIS Department" Silo**

The toolchain described (SQL, Python, React) is the standard stack of a generalist Data Engineer or Full-Stack Developer. It does not require proprietary GIS languages (ArcObjects) or software (ArcGIS Desktop).

* **Implication:** Educational institutions can hire generalist software engineers to build these tools. The barrier to entry for spatial analysis has been lowered. The power to perform complex queries (e.g., ST\_Distance) is now available in standard libraries.1

### **7.2 The "Laptop as Data Center"**

The portability of Ibis and DuckDB means that the exact same code runs on a developer's laptop as on a massive server.

* **Insight:** The snippet notes that DuckDB allows analysis of \~10x larger datasets on the same hardware.1 This implies that a researcher with a decent laptop can now analyze an entire country's educational geospatial dataset (e.g., 50GB) without needing a cloud cluster. This decentralizes analysis and empowers local districts.

### **7.3 Interoperability as a Privacy Feature**

Educational data is highly sensitive (FERPA). The architecture described allows for **Privacy-Preserving Aggregation**.

* **Mechanism:** Because DuckDB is so fast, we don't need to send raw student locations to the frontend. The API can accept a request, calculate an aggregation on the fly (e.g., "Count students per Hexagon bin"), and send only the aggregate counts to the React app.  
* **Benefit:** The raw, sensitive point data never leaves the secure server environment (or the local DuckDB file), yet the user gets a high-fidelity map of the distribution.

### **7.4 Cost-Efficiency**

The "Benefits of compression" mentioned in the snippets 1 translate directly to taxpayer savings. Moving from uncompressed CSVs to GeoParquet reduces cloud storage bills. Moving from always-on RDS instances to on-demand DuckDB processes reduces compute bills. For public sector education, this efficiency is a major selling point.

## **8\. Performance Benchmarking Analysis**

The research material provides specific benchmarks that validate this architecture.1

* **Benchmark 1: Aggregation Speed:**  
  * *Task:* Summary statistics on 26 million features.  
  * *Old Stack:* Hours.  
  * *New Stack (DuckDB):* 37 Seconds.  
  * *Implication:* An interactive dashboard can allow a user to drag a selection box over a map of the entire US and get summary stats (Average GPA, Total Funding) in under a minute.  
* **Benchmark 2: Evolution of Speed:**  
  * *Insight:* DuckDB has become 3-25x faster over the last 3 years.1  
  * *Implication:* Adopting this stack is a bet on a technology curve that is accelerating. The software improves without the user changing their code.  
* **Benchmark 3: Scalability:**  
  * *Insight:* "Analyze \~10x larger datasets on the same hardware".1  
  * *Implication:* As educational data grows (e.g., tracking real-time bus telemetry), the system can absorb the load without requiring immediate hardware upgrades.

## **9\. Conclusion**

The integration of **Ibis**, **DuckDB**, and **GeoParquet** represents the state-of-the-art in geospatial data engineering. For the educational sector, this stack offers a solution to the perennial problems of data fragmentation, slow performance, and high costs. By decoupling the storage (GeoParquet) from the compute (DuckDB) and using a portable API (Ibis), institutions can build systems that are flexible and future-proof.  
On the frontend, the combination of **React**, **shadcn/ui**, and **Deck.gl** ensures that this backend power is translated into a user experience that is accessible, responsive, and professional. The days of waiting hours for a map to load or needing a PhD to query a spatial database are over. The tools to display and analyze geospatial educational data at scale are now available, open-source, and ready for deployment.

# ---

**Appendix: Detailed Component Reference Table**

| Component Purpose | Recommended Shadcn/ui Component | React Ecosystem Integration | Use Case in Education Dashboard |
| :---- | :---- | :---- | :---- |
| **Map/Data Split** | ResizablePanel | react-resizable-panels | Adjusting the ratio of Map vs. Student List. |
| **Global Search** | Command | cmdk | Fuzzy searching for Schools, Districts, or Routes. |
| **Date Filtering** | Calendar \+ Popover | date-fns | Selecting attendance windows or academic years. |
| **Metric Range** | Slider | radix-ui/react-slider | Filtering schools by "Student/Teacher Ratio". |
| **School Details** | Sheet | radix-ui/react-dialog | Sidebar overlay for detailed school profiles. |
| **Data Grid** | Table | tanstack-table | Sorting/Filtering tabular lists of schools. |
| **Tooltips** | Tooltip | radix-ui/react-tooltip | Hover information for map markers. |
| **Tabs** | Tabs | radix-ui/react-tabs | Switching between "Demographics" and "Academics" views. |
| **Map Rendering** | N/A | **Deck.gl** | Rendering millions of student points or boundaries. |
| **Base Map** | N/A | **React-Map-GL** | Underlying street/satellite tiles (MapLibre). |

This table serves as a quick-reference guide for the development team when scaffolding the application.

#### **Works cited**

1. naty-clementi-ibis-duckdb-and-geoparquet-making-geospatial-analytics-fast-simple-and-pythonic.pdf

> Source: `docs/data_engineering/geoai/geospatial-linguistics.md`

# Geospatial Linguistics: Celtic Language Mapping

A comprehensive guide to mapping Irish language areas, schools, and demographic data using DuckDB Spatial, MapLibre GL JS, and modern geospatial tools.

---

## Table of Contents

1. [Data Sources](#1-data-sources)
2. [DuckDB Spatial Queries](#2-duckdb-spatial-queries)
3. [MapLibre Visualization](#3-maplibre-visualization)
4. [Cross-border Harmonization](#4-cross-border-harmonization)

---

## 1. Data Sources

### Overview

This section provides detailed information on official data sources for Gaeltacht boundaries, census statistics, and school locations in the Republic of Ireland and Northern Ireland.

### 1.1 Republic of Ireland - Boundaries

#### 1.1.1 Gaeltacht Areas

Official Gaeltacht regions defined by the Gaeltacht Area Orders (1956, 1967, 1974, 1982).

| Property | Value |
|----------|-------|
| **Source** | Tailte Eireann |
| **Dataset** | Gaeltacht Areas - National Administrative Boundaries - Ungeneralised - 2024 |
| **Portal** | data.gov.ie |
| **Formats** | GeoJSON, Shapefile, CSV, KML |
| **Level** | Electoral Division (parts of) |
| **Coverage** | 155 Electoral Divisions (or parts) |
| **Counties** | Cork, Donegal, Galway, Kerry, Mayo, Meath, Waterford |

**Download URL:**
https://data-osi.opendata.arcgis.com/datasets/osi::gaeltacht-areas-national-administrative-boundaries-ungeneralised-2024

#### 1.1.2 Language Planning Areas (LPAs)

Areas designated under the Gaeltacht Act 2012 for language planning.

| Property | Value |
|----------|-------|
| **Source** | Tailte Eireann |
| **Dataset** | Gaeltacht Language Planning Areas - Ungeneralised - 2024 |
| **Portal** | data.gov.ie |
| **Formats** | GeoJSON, Shapefile, CSV, KML |
| **Count** | 26 LPAs |

**Download URL:**
https://data-osi.opendata.arcgis.com/datasets/osi::gaeltacht-language-planning-areas-national-administrative-boundaries-ungen-2024

#### 1.1.3 Small Area Boundaries

Census geography for detailed population analysis.

| Property | Value |
|----------|-------|
| **Source** | CSO / Tailte Eireann |
| **Count** | ~18,000 Small Areas |
| **Portal** | data.gov.ie / PxStat |
| **Formats** | GeoJSON, Shapefile |

### 1.2 Republic of Ireland - Census Data

#### Census 2022 - Irish Language

**Source:** Central Statistics Office (CSO)
**Portal:** https://data.cso.ie (PxStat)

**Key Statistics:**

| Metric | Value | Change from 2016 |
|--------|-------|------------------|
| Can speak Irish | 1,873,997 (40%) | +112,500 |
| Daily speakers (outside education) | 71,968 | -1,835 |
| Weekly speakers | 115,065 | - |
| Within education only | 553,965 | - |
| Never speak | ~473,000 | - |

**Proficiency Levels:**

| Level | Count | Percentage |
|-------|-------|------------|
| Very well | 195,029 | 10% |
| Well | 593,898 | 32% |
| Not well | 1,034,132 | 55% |

**Gaeltacht Specific:**

| Metric | Value |
|--------|-------|
| Total population | 106,220 |
| Irish speakers | 65,156 (66%) |
| Daily speakers | 20,000+ |

**Key Tables (PxStat):**

| Table ID | Content |
|----------|---------|
| F8014 | Irish speakers by frequency, Gaeltacht area |
| E8014 | Ability to speak Irish by area |
| F8015 | Irish speakers by proficiency |

### 1.3 Republic of Ireland - School Data

#### Department of Education

**Portal:** https://www.gov.ie/en/service/find-a-school/

**Data Available:**
- School Roll Number
- Address
- Eircode
- Phone/Email
- Enrollment figures

**Format:** Excel spreadsheets

#### Gaeloideachas

**Portal:** https://gaeloideachas.ie/directories/

**Lists Available (June 2023):**

| List | Content | Format |
|------|---------|--------|
| Primary Schools | Bunscoileanna 32 counties | Excel |
| Post-Primary Schools | Iar-bhunscoileanna 32 counties | Excel |
| Units (Aonaid) | Irish-medium units | Excel |

**Key Fields:**
- School name
- County
- Irish-medium status (explicit)

### 1.4 Northern Ireland - Boundaries

#### Data Zones (DZ2021)

Primary small-area geography for Census 2021.

| Property | Value |
|----------|-------|
| **Source** | NISRA |
| **Count** | 3,780 Data Zones |
| **Formats** | GeoJSON, Shapefile, Geodatabase |

**Download URLs:**

| Format | URL |
|--------|-----|
| **GeoJSON** | https://www.nisra.gov.uk/files/nisra/publications/geography-dz2021-geojson.zip |
| **Shapefile** | https://www.nisra.gov.uk/files/nisra/publications/geography-dz2021-esri-shapefile.zip |

#### Geographic Hierarchy

| Level | Count | Notes |
|-------|-------|-------|
| Data Zones | 3,780 | Primary census unit |
| Super Data Zones | 890 | Aggregation level |
| District Electoral Areas | 80 | Electoral boundaries |
| Local Government Districts | 11 | Council areas |

### 1.5 Northern Ireland - Census Data

#### Census 2021 - Irish Language

**Source:** NISRA
**Portal:** https://build.nisra.gov.uk (Flexible Table Builder)

**Key Statistics:**

| Metric | Value | Percentage |
|--------|-------|------------|
| Some ability in Irish | 228,617 | 12.45% |
| Irish as main language | 5,969 | 0.32% |
| Daily speakers | 43,557 | 2.43% |

**Detailed Abilities:**

| Ability | Count | % of those with ability |
|---------|-------|------------------------|
| Understand only | 90,800 | 39.7% |
| Understand, speak, read, write | 71,900 | 31.4% |

### 1.6 Northern Ireland - School Data

#### Department of Education NI

**Portal:** https://www.education-ni.gov.uk

**Irish-Medium Schools List:**
https://www.education-ni.gov.uk/articles/irish-medium-schools

**Content:**
- 30 standalone Irish-medium schools
- 10 Irish-medium units
- 46 nurseries (via CnaG)

#### Comhairle na Gaelscolaiochta (CnaG)

**Portal:** https://www.comhairle.org

Authoritative source for Irish-medium education in NI.

### 1.7 Master Data Source Summary

| Data Type | ROI Source | ROI Format | NI Source | NI Format |
|-----------|------------|------------|-----------|-----------|
| **Gaeltacht Boundaries** | Tailte Eireann | GeoJSON | N/A | Define from census |
| **Census - Language** | CSO PxStat | CSV | NISRA Builder | CSV |
| **Small Area Boundaries** | Tailte Eireann | GeoJSON | NISRA | GeoJSON |
| **Schools** | gov.ie + Gaeloideachas | Excel | DE NI + CnaG | Excel |

---

## 2. DuckDB Spatial Queries

### 2.1 Setup

#### Installation

```python
import duckdb

# Create connection and install spatial
conn = duckdb.connect("celtic_geo.duckdb")
conn.execute("INSTALL spatial; LOAD spatial;")
```

#### Verify Installation

```sql
-- Check spatial functions available
SELECT * FROM duckdb_functions() WHERE function_name LIKE 'ST_%' LIMIT 10;
```

### 2.2 Loading Geospatial Data

#### GeoJSON Files

```sql
-- Load Gaeltacht boundaries from GeoJSON
CREATE TABLE gaeltacht_areas AS
SELECT * FROM ST_Read('/path/to/gaeltacht_areas.geojson');

-- Load NI Data Zones
CREATE TABLE ni_data_zones AS
SELECT * FROM ST_Read('/path/to/dz2021.geojson');
```

#### Shapefiles

```sql
-- Load from Shapefile
CREATE TABLE language_planning_areas AS
SELECT * FROM ST_Read('/path/to/lpa_boundaries.shp');
```

#### CSV with Coordinates

```sql
-- Load schools with lat/lng columns
CREATE TABLE schools AS
SELECT
    school_name,
    roll_number,
    eircode,
    ST_Point(longitude, latitude) AS geom
FROM read_csv('/path/to/schools.csv');
```

### 2.3 Core Spatial Operations

#### Point in Polygon (Schools in Gaeltacht)

```sql
-- Find schools within Gaeltacht areas
SELECT
    s.school_name,
    s.roll_number,
    g.area_name AS gaeltacht_name
FROM schools s
JOIN gaeltacht_areas g
ON ST_Within(s.geom, g.geom);
```

#### Spatial Join (Census to Boundaries)

```sql
-- Join census data to Gaeltacht boundaries
SELECT
    g.area_name,
    SUM(c.irish_speakers) AS total_speakers,
    SUM(c.population) AS total_population,
    ROUND(100.0 * SUM(c.irish_speakers) / SUM(c.population), 2) AS speaker_pct
FROM gaeltacht_areas g
JOIN census_small_areas c
ON ST_Intersects(g.geom, c.geom)
GROUP BY g.area_name
ORDER BY speaker_pct DESC;
```

#### Buffer Analysis

```sql
-- Find schools within 5km of Gaeltacht boundaries
SELECT
    s.school_name,
    ST_Distance(s.geom, g.geom) / 1000 AS distance_km
FROM schools s, gaeltacht_areas g
WHERE ST_DWithin(s.geom, ST_Buffer(g.geom, 5000), 0)
ORDER BY distance_km;
```

#### Area Calculations

```sql
-- Calculate area of each Gaeltacht region
SELECT
    area_name,
    ROUND(ST_Area(geom) / 1000000, 2) AS area_km2
FROM gaeltacht_areas
ORDER BY area_km2 DESC;
```

### 2.4 Census Data Analysis

#### Speaker Concentration Mapping

```sql
-- Calculate speaker percentage by Small Area
CREATE TABLE speaker_choropleth AS
SELECT
    sa.sa_code,
    sa.geom,
    c.can_speak_irish,
    c.daily_speakers,
    c.population,
    ROUND(100.0 * c.can_speak_irish / NULLIF(c.population, 0), 2) AS ability_pct,
    ROUND(100.0 * c.daily_speakers / NULLIF(c.population, 0), 2) AS daily_pct
FROM small_area_boundaries sa
JOIN census_language c ON sa.sa_code = c.sa_code;
```

#### Gaeltacht vs Non-Gaeltacht Comparison

```sql
-- Compare speaker rates inside vs outside Gaeltacht
WITH classified AS (
    SELECT
        c.*,
        CASE WHEN g.area_name IS NOT NULL THEN 'Gaeltacht' ELSE 'Non-Gaeltacht' END AS area_type
    FROM census_small_areas c
    LEFT JOIN gaeltacht_areas g ON ST_Within(c.geom, g.geom)
)
SELECT
    area_type,
    SUM(population) AS total_pop,
    SUM(irish_speakers) AS total_speakers,
    ROUND(100.0 * SUM(irish_speakers) / SUM(population), 2) AS speaker_pct,
    SUM(daily_speakers) AS total_daily,
    ROUND(100.0 * SUM(daily_speakers) / SUM(population), 2) AS daily_pct
FROM classified
GROUP BY area_type;
```

#### County-Level Aggregation

```sql
-- Aggregate to county level
SELECT
    county,
    SUM(population) AS pop,
    SUM(irish_speakers) AS speakers,
    ROUND(100.0 * SUM(irish_speakers) / SUM(population), 2) AS pct,
    COUNT(*) AS num_areas
FROM census_small_areas
GROUP BY county
ORDER BY pct DESC;
```

### 2.5 School Analysis

#### School Density by Area

```sql
-- Count Irish-medium schools per county
SELECT
    county,
    COUNT(*) AS num_schools,
    SUM(enrollment) AS total_pupils
FROM irish_medium_schools
GROUP BY county
ORDER BY num_schools DESC;
```

#### Schools in Language Planning Areas

```sql
-- Identify schools in each LPA
SELECT
    lpa.lpa_name,
    COUNT(s.roll_number) AS num_schools,
    STRING_AGG(s.school_name, ', ') AS schools
FROM language_planning_areas lpa
LEFT JOIN irish_medium_schools s
ON ST_Within(s.geom, lpa.geom)
GROUP BY lpa.lpa_name
ORDER BY num_schools DESC;
```

#### Distance to Nearest School

```sql
-- Calculate distance to nearest Irish-medium school for each area
WITH nearest AS (
    SELECT
        sa.sa_code,
        MIN(ST_Distance(sa.geom, s.geom)) AS min_distance
    FROM small_area_boundaries sa
    CROSS JOIN irish_medium_schools s
    GROUP BY sa.sa_code
)
SELECT
    sa_code,
    min_distance / 1000 AS nearest_school_km
FROM nearest
ORDER BY min_distance DESC
LIMIT 20;
```

### 2.6 Cross-Border Analysis

#### Unified View

```sql
-- Create unified view of speaker data
CREATE VIEW all_ireland_speakers AS
SELECT
    'ROI' AS jurisdiction,
    sa_code AS area_code,
    geom,
    population,
    irish_speakers,
    daily_speakers
FROM roi_census_small_areas

UNION ALL

SELECT
    'NI' AS jurisdiction,
    dz_code AS area_code,
    geom,
    population,
    irish_ability AS irish_speakers,
    daily_speakers
FROM ni_census_data_zones;
```

#### Border Region Analysis

```sql
-- Define border counties
WITH border_counties AS (
    SELECT * FROM counties
    WHERE county_name IN (
        'Donegal', 'Leitrim', 'Cavan', 'Monaghan', 'Louth',  -- ROI
        'Derry', 'Tyrone', 'Fermanagh', 'Armagh', 'Down'     -- NI
    )
)
SELECT
    bc.county_name,
    bc.jurisdiction,
    SUM(c.irish_speakers) AS speakers,
    SUM(c.population) AS population,
    ROUND(100.0 * SUM(c.irish_speakers) / SUM(c.population), 2) AS pct
FROM border_counties bc
JOIN all_ireland_speakers c ON ST_Within(c.geom, bc.geom)
GROUP BY bc.county_name, bc.jurisdiction
ORDER BY pct DESC;
```

### 2.7 Export for MapLibre

#### GeoJSON Export

```sql
-- Export choropleth data as GeoJSON
COPY (
    SELECT
        sa_code,
        ability_pct,
        daily_pct,
        ST_AsGeoJSON(geom) AS geometry
    FROM speaker_choropleth
) TO '/output/speakers.geojson'
WITH (FORMAT JSON);
```

#### Prepare for Vector Tiles

```sql
-- Simplify geometries for web display
CREATE TABLE web_gaeltacht AS
SELECT
    area_name,
    speaker_pct,
    ST_Simplify(geom, 100) AS geom  -- 100m tolerance
FROM gaeltacht_areas;

-- Export for tippecanoe
COPY web_gaeltacht TO '/output/gaeltacht.geojson'
WITH (FORMAT JSON);
```

#### Centroid Export (For Labels)

```sql
-- Generate centroids for labeling
SELECT
    area_name,
    ST_X(ST_Centroid(geom)) AS lng,
    ST_Y(ST_Centroid(geom)) AS lat
FROM gaeltacht_areas;
```

### 2.8 Complete Pipeline Example

```python
#!/usr/bin/env python3
"""
DuckDB Spatial Pipeline for Celtic Language Mapping
"""

import duckdb
from pathlib import Path

class CelticGeoPipeline:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = duckdb.connect(db_path)
        self.conn.execute("INSTALL spatial; LOAD spatial;")

    def load_boundaries(self, geojson_path: str, table_name: str):
        """Load GeoJSON boundaries."""
        self.conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM ST_Read('{geojson_path}')
        """)

    def load_census_csv(self, csv_path: str, table_name: str):
        """Load census data from CSV."""
        self.conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_csv('{csv_path}')
        """)

    def join_census_to_boundaries(
        self,
        census_table: str,
        boundary_table: str,
        join_key: str
    ):
        """Spatial join census data to boundaries."""
        return self.conn.execute(f"""
            SELECT
                b.*,
                c.population,
                c.irish_speakers,
                c.daily_speakers,
                ROUND(100.0 * c.irish_speakers / NULLIF(c.population, 0), 2) AS pct
            FROM {boundary_table} b
            LEFT JOIN {census_table} c ON b.{join_key} = c.{join_key}
        """).fetchdf()

    def schools_in_areas(self, schools_table: str, areas_table: str):
        """Find schools within areas."""
        return self.conn.execute(f"""
            SELECT
                a.area_name,
                COUNT(s.*) AS num_schools
            FROM {areas_table} a
            LEFT JOIN {schools_table} s ON ST_Within(s.geom, a.geom)
            GROUP BY a.area_name
        """).fetchdf()

    def export_geojson(self, query: str, output_path: str):
        """Export query result as GeoJSON."""
        self.conn.execute(f"""
            COPY ({query}) TO '{output_path}'
            WITH (FORMAT JSON)
        """)

def main():
    pipeline = CelticGeoPipeline("celtic_geo.duckdb")

    # Load data
    pipeline.load_boundaries(
        "gaeltacht_areas.geojson",
        "gaeltacht"
    )

    # Analysis
    results = pipeline.schools_in_areas("schools", "gaeltacht")
    print(results)

    # Export
    pipeline.export_geojson(
        "SELECT * FROM gaeltacht",
        "output/gaeltacht.geojson"
    )

if __name__ == "__main__":
    main()
```

### 2.9 Performance Tips

| Operation | Tip |
|-----------|-----|
| **Large datasets** | Use `ST_Simplify()` for web export |
| **Spatial joins** | Create spatial index with `CREATE INDEX` |
| **Point-in-polygon** | Use `ST_DWithin()` for approximate queries |
| **Memory** | Use disk-based DB for >1GB data |

---

## 3. MapLibre Visualization

### 3.1 Basic Setup

#### HTML Template

```html
<!DOCTYPE html>
<html>
<head>
    <title>Celtic Language Map</title>
    <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
    <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
    <style>
        body { margin: 0; padding: 0; }
        #map { position: absolute; top: 0; bottom: 0; width: 100%; }
        .legend {
            position: absolute;
            bottom: 30px;
            left: 10px;
            background: white;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="legend" id="legend"></div>

    <script src="app.js"></script>
</body>
</html>
```

#### Initialize Map

```javascript
// app.js
const map = new maplibregl.Map({
    container: 'map',
    style: {
        version: 8,
        sources: {
            'osm': {
                type: 'raster',
                tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '(c) OpenStreetMap'
            }
        },
        layers: [{
            id: 'osm-tiles',
            type: 'raster',
            source: 'osm'
        }]
    },
    center: [-8.0, 53.5],  // Ireland center
    zoom: 6
});
```

### 3.2 Loading Data Sources

#### GeoJSON Source

```javascript
map.on('load', () => {
    // Add Gaeltacht boundaries
    map.addSource('gaeltacht', {
        type: 'geojson',
        data: '/data/gaeltacht_areas.geojson'
    });

    // Add schools
    map.addSource('schools', {
        type: 'geojson',
        data: '/data/irish_medium_schools.geojson'
    });

    // Add census choropleth
    map.addSource('census', {
        type: 'geojson',
        data: '/data/speaker_choropleth.geojson'
    });
});
```

#### Vector Tiles Source

```javascript
// For large datasets, use vector tiles
map.addSource('census-tiles', {
    type: 'vector',
    tiles: ['https://your-server.com/tiles/census/{z}/{x}/{y}.pbf'],
    minzoom: 0,
    maxzoom: 14
});
```

### 3.3 Layer Styling

#### Choropleth Layer (Speaker Percentage)

```javascript
map.addLayer({
    id: 'census-choropleth',
    type: 'fill',
    source: 'census',
    paint: {
        'fill-color': [
            'interpolate',
            ['linear'],
            ['get', 'speaker_pct'],
            0, '#f7fbff',
            10, '#c6dbef',
            20, '#9ecae1',
            40, '#6baed6',
            60, '#3182bd',
            80, '#08519c'
        ],
        'fill-opacity': 0.7
    }
});

// Add outline
map.addLayer({
    id: 'census-outline',
    type: 'line',
    source: 'census',
    paint: {
        'line-color': '#333',
        'line-width': 0.5
    }
});
```

#### Gaeltacht Boundaries

```javascript
map.addLayer({
    id: 'gaeltacht-fill',
    type: 'fill',
    source: 'gaeltacht',
    paint: {
        'fill-color': '#228B22',
        'fill-opacity': 0.3
    }
});

map.addLayer({
    id: 'gaeltacht-outline',
    type: 'line',
    source: 'gaeltacht',
    paint: {
        'line-color': '#228B22',
        'line-width': 2,
        'line-dasharray': [2, 2]
    }
});
```

#### School Points

```javascript
map.addLayer({
    id: 'schools-points',
    type: 'circle',
    source: 'schools',
    paint: {
        'circle-radius': [
            'interpolate',
            ['linear'],
            ['get', 'enrollment'],
            50, 4,
            200, 8,
            500, 12
        ],
        'circle-color': [
            'match',
            ['get', 'school_type'],
            'primary', '#4CAF50',
            'secondary', '#2196F3',
            '#9E9E9E'
        ],
        'circle-stroke-width': 1,
        'circle-stroke-color': '#fff'
    }
});
```

#### Labels

```javascript
map.addLayer({
    id: 'gaeltacht-labels',
    type: 'symbol',
    source: 'gaeltacht',
    layout: {
        'text-field': ['get', 'area_name'],
        'text-size': 12,
        'text-anchor': 'center'
    },
    paint: {
        'text-color': '#333',
        'text-halo-color': '#fff',
        'text-halo-width': 1
    }
});
```

### 3.4 Interactivity

#### Hover Effects

```javascript
// Highlight on hover
map.on('mousemove', 'census-choropleth', (e) => {
    map.getCanvas().style.cursor = 'pointer';

    if (e.features.length > 0) {
        const feature = e.features[0];

        // Update info panel
        document.getElementById('info').innerHTML = `
            <strong>${feature.properties.area_name}</strong><br>
            Population: ${feature.properties.population.toLocaleString()}<br>
            Speakers: ${feature.properties.speaker_pct}%<br>
            Daily: ${feature.properties.daily_pct}%
        `;
    }
});

map.on('mouseleave', 'census-choropleth', () => {
    map.getCanvas().style.cursor = '';
});
```

#### Click Popups

```javascript
map.on('click', 'schools-points', (e) => {
    const feature = e.features[0];
    const coordinates = feature.geometry.coordinates.slice();

    new maplibregl.Popup()
        .setLngLat(coordinates)
        .setHTML(`
            <h3>${feature.properties.school_name}</h3>
            <p>
                <strong>Type:</strong> ${feature.properties.school_type}<br>
                <strong>Enrollment:</strong> ${feature.properties.enrollment}<br>
                <strong>Address:</strong> ${feature.properties.address}
            </p>
        `)
        .addTo(map);
});
```

#### Layer Toggle

```javascript
function toggleLayer(layerId, visible) {
    const visibility = visible ? 'visible' : 'none';
    map.setLayoutProperty(layerId, 'visibility', visibility);
}

// Usage
document.getElementById('toggle-gaeltacht').addEventListener('change', (e) => {
    toggleLayer('gaeltacht-fill', e.target.checked);
    toggleLayer('gaeltacht-outline', e.target.checked);
});
```

### 3.5 Legend

#### Choropleth Legend

```javascript
function createLegend() {
    const legend = document.getElementById('legend');

    const grades = [0, 10, 20, 40, 60, 80];
    const colors = ['#f7fbff', '#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c'];

    legend.innerHTML = '<h4>Irish Speakers (%)</h4>';

    grades.forEach((grade, i) => {
        const next = grades[i + 1] || '+';
        legend.innerHTML += `
            <div>
                <span style="background:${colors[i]}; width:20px; height:20px; display:inline-block;"></span>
                ${grade}${next !== '+' ? ' - ' + next : next}
            </div>
        `;
    });
}

map.on('load', createLegend);
```

#### School Legend

```javascript
function createSchoolLegend() {
    const legend = document.getElementById('school-legend');

    legend.innerHTML = `
        <h4>Schools</h4>
        <div>
            <span style="background:#4CAF50; width:12px; height:12px; display:inline-block; border-radius:50%;"></span>
            Primary
        </div>
        <div>
            <span style="background:#2196F3; width:12px; height:12px; display:inline-block; border-radius:50%;"></span>
            Secondary
        </div>
    `;
}
```

### 3.6 Vector Tile Generation

#### Using tippecanoe

```bash
#!/bin/bash
# Generate vector tiles from GeoJSON

# Census choropleth tiles
tippecanoe \
    -o census.mbtiles \
    -z 14 \
    -l census \
    --coalesce-densest-as-needed \
    --extend-zooms-if-still-dropping \
    speaker_choropleth.geojson

# Gaeltacht boundaries
tippecanoe \
    -o gaeltacht.mbtiles \
    -z 14 \
    -l gaeltacht \
    --simplify-only-low-zooms \
    gaeltacht_areas.geojson

# Schools (preserve all features)
tippecanoe \
    -o schools.mbtiles \
    -z 14 \
    -l schools \
    --drop-smallest-as-needed \
    -r1 \
    irish_medium_schools.geojson
```

#### Serving Tiles

```bash
# Using tileserver-gl
docker run --rm -it \
    -v $(pwd)/tiles:/data \
    -p 8080:8080 \
    maptiler/tileserver-gl
```

### 3.7 Complete Application

```javascript
// Full application with all features
class CelticLanguageMap {
    constructor(containerId) {
        this.map = new maplibregl.Map({
            container: containerId,
            style: this.getBaseStyle(),
            center: [-8.0, 53.5],
            zoom: 6
        });

        this.map.on('load', () => this.initLayers());
    }

    getBaseStyle() {
        return {
            version: 8,
            sources: {
                'carto': {
                    type: 'raster',
                    tiles: ['https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'],
                    tileSize: 256,
                    attribution: '(c) CartoDB (c) OSM'
                }
            },
            layers: [{
                id: 'base',
                type: 'raster',
                source: 'carto'
            }]
        };
    }

    async initLayers() {
        // Load data sources
        await this.loadSource('gaeltacht', '/data/gaeltacht.geojson');
        await this.loadSource('census', '/data/census.geojson');
        await this.loadSource('schools', '/data/schools.geojson');

        // Add layers
        this.addChoroplethLayer();
        this.addGaeltachtLayer();
        this.addSchoolsLayer();

        // Setup interactivity
        this.setupPopups();
        this.createLegend();
    }

    async loadSource(id, url) {
        const response = await fetch(url);
        const data = await response.json();

        this.map.addSource(id, {
            type: 'geojson',
            data: data
        });
    }

    addChoroplethLayer() {
        this.map.addLayer({
            id: 'census-fill',
            type: 'fill',
            source: 'census',
            paint: {
                'fill-color': [
                    'interpolate', ['linear'], ['get', 'speaker_pct'],
                    0, '#f7fbff',
                    10, '#c6dbef',
                    20, '#9ecae1',
                    40, '#6baed6',
                    60, '#3182bd',
                    80, '#08519c'
                ],
                'fill-opacity': 0.6
            }
        });
    }

    addGaeltachtLayer() {
        this.map.addLayer({
            id: 'gaeltacht-boundary',
            type: 'line',
            source: 'gaeltacht',
            paint: {
                'line-color': '#228B22',
                'line-width': 3
            }
        });
    }

    addSchoolsLayer() {
        this.map.addLayer({
            id: 'schools',
            type: 'circle',
            source: 'schools',
            paint: {
                'circle-radius': 6,
                'circle-color': '#E91E63',
                'circle-stroke-width': 2,
                'circle-stroke-color': '#fff'
            }
        });
    }

    setupPopups() {
        // School popups
        this.map.on('click', 'schools', (e) => {
            const props = e.features[0].properties;
            new maplibregl.Popup()
                .setLngLat(e.lngLat)
                .setHTML(`<h3>${props.school_name}</h3><p>Enrollment: ${props.enrollment}</p>`)
                .addTo(this.map);
        });

        // Cursor changes
        ['census-fill', 'schools'].forEach(layer => {
            this.map.on('mouseenter', layer, () => {
                this.map.getCanvas().style.cursor = 'pointer';
            });
            this.map.on('mouseleave', layer, () => {
                this.map.getCanvas().style.cursor = '';
            });
        });
    }

    createLegend() {
        // Implementation from section 3.5
    }
}

// Initialize
const celticMap = new CelticLanguageMap('map');
```

### 3.8 Data-Driven Styling Examples

#### Gradient by Daily Speakers

```javascript
'fill-color': [
    'case',
    ['<', ['get', 'daily_pct'], 1], '#fee5d9',
    ['<', ['get', 'daily_pct'], 5], '#fcae91',
    ['<', ['get', 'daily_pct'], 10], '#fb6a4a',
    ['<', ['get', 'daily_pct'], 20], '#de2d26',
    '#a50f15'
]
```

#### School Size by Enrollment

```javascript
'circle-radius': [
    'step',
    ['get', 'enrollment'],
    4,   // Default
    100, 6,
    200, 8,
    500, 12
]
```

---

## 4. Cross-border Harmonization

### 4.1 Geographic Comparability

The challenge of comparing Irish language data across the Republic of Ireland and Northern Ireland involves reconciling fundamentally different statistical geographies and census methodologies.

#### ROI vs NI Geographic Units

| Feature | Republic of Ireland | Northern Ireland |
|---------|---------------------|------------------|
| **Primary Unit** | Small Area (SA) | Data Zone (DZ2021) |
| **Count** | ~18,000 | 3,780 |
| **Average Population** | ~250 | ~500 |
| **Parent Unit** | Electoral Division (ED) | Super Data Zone (SDZ) |
| **Regional Level** | County (31) | Local Government District (11) |

#### Coordinate Reference Systems

| Jurisdiction | Native CRS | Web Map CRS |
|--------------|------------|-------------|
| ROI | Irish Transverse Mercator (ITM) EPSG:2157 | WGS84 (EPSG:4326) |
| NI | Irish Grid (IG) EPSG:29902 | WGS84 (EPSG:4326) |

**Transform in DuckDB:**
```sql
SELECT ST_Transform(geom, 'EPSG:4326') AS geom_wgs84 FROM boundaries;
```

### 4.2 Temporal Alignment

| Data Type | ROI Date | NI Date |
|-----------|----------|---------|
| Census | 2022 | 2021 |
| Boundaries | 2024 | 2021 |
| Schools | 2023/24 | 2022/23 |

### 4.3 Census Question Comparability

#### ROI Census 2022 Questions

1. **Can you speak Irish?** (Yes/No)
2. **How often do you speak Irish?**
   - Daily (within education)
   - Daily (outside education)
   - Weekly
   - Less often
   - Never
3. **How well do you speak Irish?** (New in 2022)
   - Very well
   - Well
   - Not well

#### NI Census 2021 Questions

1. **Can you understand, speak, read or write Irish?** (Multiple choice)
   - Understand spoken Irish
   - Speak Irish
   - Read Irish
   - Write Irish
   - None
2. **How often do you speak Irish?** (New in 2021)
   - Daily
   - Weekly
   - Less often
   - Never

#### Mapping Common Metrics

| Metric | ROI Variable | NI Variable | Comparable? |
|--------|-------------|-------------|-------------|
| **Some ability** | "Can speak Irish" = Yes | Any of understand/speak/read/write | Approximate |
| **Daily speakers** | "Daily outside education" | "Daily" | Good |
| **Fluency** | "Very well" + "Well" | "Speak" + "Read" + "Write" | Approximate |

### 4.4 Harmonization Strategies

#### Strategy 1: Aggregate to Comparable Levels

When direct comparison of small areas is problematic, aggregate to county/council level where populations are large enough for meaningful comparison.

```sql
-- Compare at county/council level
SELECT
    'ROI' AS jurisdiction,
    county_name AS region,
    SUM(daily_speakers) AS daily,
    SUM(population) AS pop,
    ROUND(100.0 * SUM(daily_speakers) / SUM(population), 2) AS daily_pct
FROM roi_census
GROUP BY county_name

UNION ALL

SELECT
    'NI' AS jurisdiction,
    lgd_name AS region,
    SUM(daily_speakers) AS daily,
    SUM(population) AS pop,
    ROUND(100.0 * SUM(daily_speakers) / SUM(population), 2) AS daily_pct
FROM ni_census
GROUP BY lgd_name
ORDER BY daily_pct DESC;
```

#### Strategy 2: Define NI "Gaeltacht-Equivalent" Areas

Since NI has no official Gaeltacht designation, define areas with high speaker concentration:

```sql
-- Identify NI Data Zones with >10% daily Irish speakers
CREATE TABLE ni_irish_concentration AS
SELECT
    dz_code,
    geom,
    daily_speakers,
    population,
    ROUND(100.0 * daily_speakers / NULLIF(population, 0), 2) AS daily_pct
FROM ni_census_data_zones
WHERE (100.0 * daily_speakers / NULLIF(population, 0)) > 10;
```

#### Strategy 3: Focus on Common Metrics

Use "daily speakers" as the primary comparison metric, as both censuses now collect this data with similar methodology.

### 4.5 Border Region Analysis

The border region offers unique analytical opportunities due to geographic proximity.

#### Border Counties

| ROI Counties | NI Counties |
|--------------|-------------|
| Donegal | Derry |
| Leitrim | Tyrone |
| Cavan | Fermanagh |
| Monaghan | Armagh |
| Louth | Down |

#### Cross-Border Query

```sql
-- Analyze Irish language use in border region
WITH border_areas AS (
    -- ROI border Small Areas
    SELECT
        'ROI' AS jurisdiction,
        sa_code AS area_code,
        geom,
        daily_speakers,
        population
    FROM roi_small_areas
    WHERE county IN ('Donegal', 'Leitrim', 'Cavan', 'Monaghan', 'Louth')

    UNION ALL

    -- NI border Data Zones
    SELECT
        'NI' AS jurisdiction,
        dz_code AS area_code,
        geom,
        daily_speakers,
        population
    FROM ni_data_zones
    WHERE lgd IN ('Derry City and Strabane', 'Fermanagh and Omagh',
                  'Mid Ulster', 'Armagh City, Banbridge and Craigavon',
                  'Newry, Mourne and Down')
)
SELECT
    jurisdiction,
    COUNT(*) AS num_areas,
    SUM(population) AS total_pop,
    SUM(daily_speakers) AS total_daily,
    ROUND(100.0 * SUM(daily_speakers) / SUM(population), 2) AS daily_pct
FROM border_areas
GROUP BY jurisdiction;
```

### 4.6 Key Metrics Comparison

| Metric | ROI (Census 2022) | NI (Census 2021) |
|--------|-------------------|------------------|
| **Total Population** | 5,149,139 | 1,903,175 |
| **Can Speak/Some Ability** | 1,873,997 (40%) | 228,617 (12.45%) |
| **Daily Speakers** | 71,968 (1.5%) | 43,557 (2.43%) |
| **Main Language** | N/A | 5,969 (0.32%) |

### 4.7 Gaeltacht vs Belfast Gaeltacht Quarter

A unique comparison can be made between traditional Gaeltacht areas and the urban "neo-Gaeltacht" in Belfast.

| Feature | Traditional Gaeltacht (ROI) | Belfast Gaeltacht Quarter |
|---------|---------------------------|---------------------------|
| **Origin** | Historical continuity | Community revival |
| **Legal Status** | Statutory (Gaeltacht Acts) | None |
| **Population** | 106,220 | ~5,000 |
| **Speaker %** | 66% can speak | ~50% can speak |
| **Daily Use** | Declining | Growing |

### 4.8 Visualization Considerations

When displaying cross-border data:

1. **Use consistent color scales** - Apply the same choropleth breaks to both jurisdictions
2. **Clearly mark the border** - Use a distinct line style for the international border
3. **Provide context** - Include notes about data comparability in legends
4. **Offer both views** - Provide options to view ROI-only, NI-only, or all-island

#### Example MapLibre Layer for Border

```javascript
map.addLayer({
    id: 'border-line',
    type: 'line',
    source: 'border',
    paint: {
        'line-color': '#000',
        'line-width': 2,
        'line-dasharray': [4, 2]
    }
});
```

---

## References

### Data Sources

- Tailte Eireann Open Data: https://data-osi.opendata.arcgis.com
- CSO PxStat: https://data.cso.ie
- NISRA: https://www.nisra.gov.uk
- data.gov.ie: https://data.gov.ie
- OpenDataNI: https://www.opendatani.gov.uk

### Technical Documentation

- DuckDB Spatial: https://duckdb.org/docs/extensions/spatial
- PostGIS (compatible functions): https://postgis.net/docs/
- MapLibre GL JS: https://maplibre.org/maplibre-gl-js/docs/
- tippecanoe: https://github.com/felt/tippecanoe
- GeoParquet: https://geoparquet.org/

### Organizations

- Gaeloideachas: https://gaeloideachas.ie
- Comhairle na Gaelscolaiochta: https://www.comhairle.org
- Gaois Research Group (DCU): https://www.gaois.ie


> Source: `docs/data_engineering/geoai/Geospatial Workflow & Particle Effects.md`

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

> Source: `docs/data_engineering/geoai/geospatial_book.md`

# Spatial Data Management with DuckDB

[![image](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/giswqs/duckdb-spatial/HEAD)
[![image](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/giswqs/duckdb-spatial/blob/main)

<!-- [![Docker Image](https://img.shields.io/badge/docker-giswqs%2Fpygis%3Abook-blue?logo=docker)](https://hub.docker.com/r/giswqs/pygis/tags) -->

<!-- [![Amazon](https://img.shields.io/badge/Buy%20on-Amazon-orange?logo=amazon&logoColor=white)](https://amazon.com/dp/B0FFW34LL3) -->

## Introduction

Welcome to the official website for **_Spatial Data Management with DuckDB: From SQL Basics to Advanced Geospatial Analytics_**. This website contains all the code examples featured in the book, designed to help you learn and apply DuckDB for geospatial analysis.

## Get the Book

- 🇺🇸 **English Full-Color Print Edition (446 pages):** Available on Amazon ([link](https://www.amazon.com/dp/B0G2JFMFFC))

- 🇺🇸 **English PDF Edition (441 pages):** Available on Leanpub ([link](https://leanpub.com/duckdb))

<!-- - 🇨🇳 **Chinese PDF Edition (430 pages):** 中文电子版可在 Leanpub 购买 ([link](https://leanpub.com/duckdb-zh))

- 🇲🇽 **Spanish PDF Edition (430 pages):** Edición en español disponible en Leanpub ([link](https://leanpub.com/duckdb-es))
 -->

## Cite the Book

If you use this book in your research or teaching, please consider citing it as follows:

> Wu, Q. (2025). _Spatial Data Management with DuckDB: From SQL Basics to Advanced Geospatial Analytics_. Independently published. PDF edition ISBN 979-8993859705; Print edition ISBN 979-8274710572. [https://duckdb.gishub.org](https://duckdb.gishub.org)

![book cover](https://assets.gishub.org/images/duckdb-book-cover.webp)

## Table of Contents

<!-- To download a PDF version of the Table of Contents, please visit <https://duckdb.gishub.org/book-toc.pdf>. -->

- **Preface**

  - Introduction
  - Who This Book Is For
  - What This Book Covers
  - Getting the Most Out of This Book
  - Conventions Used in This Book
  - Downloading the Code Examples
  - Video Tutorials and Supplementary Resources
  - Community and Feedback
  - Acknowledgments
  - About the Author
  - Licensing and Copyright

- **DuckDB Foundations**

  - Getting Started with DuckDB
  - Essential SQL for Spatial Analysis
  - DuckDB Python Integration

- **Spatial Data Operations**

  - Loading Spatial Data Formats
  - Exporting and Converting Spatial Data
  - Geometry Operations and Functions
  - Spatial Queries and Relationships
  - Advanced Spatial Joins
  - Interactive Data Visualization
  - Working with Vector Tiles and PMTiles

- **Real-World Geospatial Analytics**

  - Analyzing the US National Wetlands Inventory
  - Analyzing Global Building Footprints
  - Analyzing NYC Taxi Data
  - Developing Interactive Dashboards with Voilà and Solara

## How to Run Code Examples

The code examples are organized into folders, each corresponding to a chapter in the book. The code examples are written in Python and can be run using MyBinder, Google Colab, or Docker.

<!-- Follow this [video tutorial](https://www.youtube.com/embed/6GwMoV4LOiU) to learn how to run the code examples. -->

### Using MyBinder

The code examples can be run using MyBinder.

[![image](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/giswqs/duckdb-spatial/HEAD)

### Using Google Colab

The code examples can be run using Google Colab.

[![image](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/giswqs/duckdb-spatial/blob/main)

<!-- ### Using Docker

The code examples can be run using Docker. There are two Docker [images](https://hub.docker.com/r/giswqs/pygis/tags) available:

A lightweight docker image without Apache Sedona:

```bash
docker pull giswqs/pygis:book
docker run -it -p 8888:8888 -v $(pwd):/app/workspace giswqs/pygis:book
```

A docker image with Apache Sedona:

```bash
docker pull giswqs/pygis:sedona
docker run -it -p 8888:8888 -p 4040:4040 -p 8080:8080 -p 8081:8081 -p 7077:7077 -p 8085:8085 -v $(pwd):/app/workspace giswqs/pygis:sedona
``` -->

## Video Tutorials

Complementing the written content, this book is supported by a comprehensive series of video tutorials that walk through key concepts and provide additional examples: <https://tinyurl.com/duckdb-spatial-videos>.

The videos are designed to complement, not replace, the written material. They're particularly helpful for:

- Visual learners who benefit from seeing code being written and executed
- Understanding complex concepts through multiple explanations
- Learning about the development workflow and best practices
- Seeing how to approach problems and debug issues

The playlist is organized to follow the book's structure. You can watch them in order as you progress through the book, or jump to specific topics as needed.

The videos were created in Fall 2023 when I was teaching the [**Spatial Data Management**](https://geog-414.gishub.org) course at the University of Tennessee. Although the course has concluded, the videos remain relevant and can be used as a reference for the book. Additional videos will be added in the future.

## About the Author

Dr. Qiusheng Wu is an Associate Professor in the Department of Geography & Sustainability at the University of Tennessee, Knoxville. He is also an Amazon Scholar. Dr. Wu’s research focuses on advancing open-source geospatial analytics through cloud computing and GeoAI. He is the creator and maintainer of several widely used open-source Python packages, including [Geemap](https://geemap.org), [Leafmap](https://leafmap.org), [SAMGeo](https://samgeo.gishub.org), and [GeoAI](https://opengeoai.org), which integrate cloud-based geospatial platforms with AI-powered analysis and visualization. Dr. Wu’s work bridges remote sensing, Earth observation, and artificial intelligence to make large-scale geospatial data more accessible, reproducible, and intelligent for researchers, educators, and practitioners worldwide. His open-source projects can be found on GitHub at <https://github.com/opengeos>.

## Licensing and Copyright

This book embraces the principles of open science and open education. To support transparency, learning, and reuse, the **code examples** in this book are released under a [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license. This means you are free to copy, modify, and distribute the code, even for commercial purposes, as long as appropriate credit is given.

Please attribute code usage by citing the book or linking to the GitHub repository:

> Wu, Q. (2025). _Spatial Data Management with DuckDB: From SQL Basics to Advanced Geospatial Analytics_. Independently published. PDF edition ISBN 979-8993859705; Print edition ISBN 979-8274710572. [https://duckdb.gishub.org](https://duckdb.gishub.org)

While the code is freely available, the **text, figures, and images** in this book are **copyrighted** by the author and may not be reproduced, redistributed, or modified without explicit permission. This includes all written content, custom diagrams, and embedded visualizations unless otherwise noted.

If you wish to reuse or adapt any non-code material from the book (for example, for teaching, presentations, or publications), please contact the author to request permission.

This dual licensing approach helps balance open access to learning materials with the protection of original creative work. Thank you for respecting these terms and supporting the open-source geospatial community.


## JOSS Paper


> Source: `docs/data_engineering/geoai/paper/paper.md`

---
title: "GeoAI: A Python package for integrating artificial intelligence with geospatial data analysis and visualization"
tags:
    - Python
    - geospatial
    - artificial intelligence
    - deep learning
    - Jupyter
    - visualization

authors:
    - name: Qiusheng Wu
      orcid: 0000-0001-5437-4073
      affiliation: "1"
affiliations:
    - name: Department of Geography & Sustainability, University of Tennessee, Knoxville, TN 37996, United States
      index: 1
date: 12 September 2025
bibliography: paper.bib
---

# Summary

GeoAI is a comprehensive Python package designed to bridge artificial intelligence (AI) and geospatial data analysis, providing researchers and practitioners with intuitive tools for applying machine learning techniques to geographic data. The package offers a unified framework for processing satellite imagery, aerial photographs, and vector data using state-of-the-art deep learning models. GeoAI integrates popular AI frameworks including PyTorch [@Paszke2019], Transformers [@Wolf2019], PyTorch Segmentation Models [@Iakubovskii2019], and specialized geospatial libraries like torchange [@Zheng2024], enabling users to perform complex geospatial analyses with minimal code.

The package provides five core capabilities:

1. Interactive and programmatic search and download of remote sensing imagery and geospatial data.
2. Automated dataset preparation with image chips and label generation.
3. Model training for tasks such as classification, detection, and segmentation.
4. Inference pipelines for applying models to new geospatial datasets.
5. Interactive visualization through integration with Leafmap [@Wu2021] and MapLibre.

GeoAI addresses the growing demand for accessible AI tools in geospatial research by providing high-level APIs that abstract complex machine learning workflows while maintaining flexibility for advanced users. The package supports multiple data formats (GeoTIFF, JPEG2000,GeoJSON, Shapefile, GeoPackage) and includes automatic device management for GPU acceleration when available. With over 10 modules and extensive notebook examples, GeoAI serves as both a research tool and educational resource for the geospatial AI community.

# Statement of Need

The integration of artificial intelligence with geospatial data analysis has become increasingly critical across numerous scientific disciplines, from environmental monitoring and urban planning to disaster response and climate research [@Li2022; @Mai2024]. However, applying AI techniques to geospatial data presents unique challenges including data preprocessing complexities, specialized model architectures, and the need for domain-specific knowledge in both machine learning and geographic information systems [@Zhu2017; @Ma2019].

Existing solutions often require researchers to navigate fragmented ecosystems of tools, combining general-purpose machine learning libraries with specialized geospatial packages, leading to steep learning curves and reproducibility challenges. While packages like TorchGeo [@Stewart2022] and TerraTorch [@Gomes2025] provide excellent foundational tools for geospatial deep learning, there remains a gap for comprehensive, high-level interfaces that can democratize access to advanced AI techniques for the broader geospatial community.

GeoAI addresses this need by providing a unified, user-friendly interface that abstracts the complexity of integrating multiple AI frameworks with geospatial data processing workflows. It lowers barriers for: (1) geospatial researchers who need accessible AI workflows without deep ML expertise; (2) AI practitioners who want streamlined geospatial preprocessing and domain-specific datasets; and (3) educators seeking reproducible examples and teaching-ready workflows.

The package's design philosophy emphasizes simplicity without sacrificing functionality, enabling users to perform sophisticated analyses such as building footprint extraction from satellite imagery, land cover classification, and change detection with just a few lines of code. By integrating cutting-edge AI models and providing seamless access to major geospatial data sources, GeoAI significantly lowers the barrier to entry for geospatial AI applications while maintaining the flexibility needed for advanced research applications.

# Acknowledgements

We gratefully acknowledge the support of the National Aeronautics and Space Administration (NASA) through Grant No. 80NSSC22K1742, awarded under the Open Source Tools, Frameworks, and Libraries Program. Additional support was provided by the U.S. Geological Survey through Grant/Cooperative Agreement No. G23AP00683 (GY23-GY27) in collaboration with AmericaView. We also thank the broader open-source geospatial community for their contributions and feedback during the development of this package.

# References


## Original Sources

- `docs/data_engineering/geoai/.github/ISSUE_TEMPLATE/bug_report.md`
- `docs/data_engineering/geoai/.github/ISSUE_TEMPLATE/feature_request.md`
- `docs/data_engineering/geoai/docs/auto.md`
- `docs/data_engineering/geoai/docs/change_detection.md`
- `docs/data_engineering/geoai/docs/changelog.md`
- `docs/data_engineering/geoai/docs/classify.md`
- `docs/data_engineering/geoai/docs/contributing.md`
- `docs/data_engineering/geoai/docs/detectron2.md`
- `docs/data_engineering/geoai/docs/dinov3.md`
- `docs/data_engineering/geoai/docs/download.md`
- `docs/data_engineering/geoai/docs/extract.md`
- `docs/data_engineering/geoai/docs/geo_agents.md`
- `docs/data_engineering/geoai/docs/geoai.md`
- `docs/data_engineering/geoai/docs/hf.md`
- `docs/data_engineering/geoai/docs/index.md`
- `docs/data_engineering/geoai/docs/installation.md`
- `docs/data_engineering/geoai/docs/map_tools.md`
- `docs/data_engineering/geoai/docs/map_widgets.md`
- `docs/data_engineering/geoai/docs/moondream.md`
- `docs/data_engineering/geoai/docs/qgis_plugin.md`
- `docs/data_engineering/geoai/docs/sam.md`
- `docs/data_engineering/geoai/docs/segment.md`
- `docs/data_engineering/geoai/docs/segmentation.md`
- `docs/data_engineering/geoai/docs/timm_segment.md`
- `docs/data_engineering/geoai/docs/timm_train.md`
- `docs/data_engineering/geoai/docs/train.md`
- `docs/data_engineering/geoai/docs/utils.md`
- `docs/data_engineering/geoai/Geospatial Data Visualization with Ibis.md`
- `docs/data_engineering/geoai/Geospatial Workflow & Particle Effects.md`
- `docs/data_engineering/geoai/geospatial_book.md`
- `docs/data_engineering/geoai/geospatial-linguistics.md`
- `docs/data_engineering/geoai/KCG_SUMMARY.md`
- `docs/data_engineering/geoai/paper/paper.md`
- `docs/data_engineering/geoai/qgis_plugin/README.md`
- `docs/data_engineering/geoai/README.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*

# Multi-Modal Deep Learning for Historical Document Analysis
This code contains the repository for analyzing historical documents and parsing historical manuscripts into usable JSON formatting.
It goes in conjunction with the Medium article series on the Cairo Genizah Analysis but should work with other document
collections as well.

## Setup/Use

### Initial installation
This code was primarily run and tested on py.313 venv on Mac OS Silicon with 48gb of RAM. We are working on setting up a CI/CD pipeline but in the interim
we cannot guarantee its ability to run on other environments.

1. Run `git clone https://github.com/AIStream-Peelout/historical-document-analysis.git`
2. `cd historical-document-analysis`
3. Run `pip install -r requirements.txt`

### .env file

This repository is heavily dependent on GCP, Elasticsearch , and optionally Weights and Biases. In order for these 
tools work properly you will have to create .env in the root of the repo and supply the following. 
```
GEMINI_API_KEY = "your_key_here"
OPEN_AI_API_KEY = SOME_KEY_HERE
WANDB_API_KEY = WANDB_API_KEY
ELASTIC_SEARCH_HOST = es_endpoint.your_domain.com
ELASTIC_USER = YOUR_USERNAME
ELASTIC_PASSWORD = YOUR_PASSWORD
GOOGLE_APPLICATION_CREDENTIALS=/path_to_your_gcp_creds

```

## Cairo Genizah AI Assistant (GenizahAI)
For Cairo Genizah research we have organized the code in the following ways. We have also supplied most of the data we have collected from various sites (subject to licensing constraints). 

This code primarily builds the elastic search indices, SQL database, and graph database for the project. A separate repository contains the code for the  frontend and backend APIs. 

### Datasets
The core Cario Genizah documents are stored under `src/raw_data/cairo_genizah`. This file is not commited to the repository 
as it is way too large. We regularly back this file up to GCP as it is very large. It can be accessed at GCP
`gs://`. By accessing the data you agree not to re-distribute the data and to cite all on the original authors/institutions from where the data was derived. 

Code assumes all files are in this directory. Additionally, we will be posting this to HuggingFace datasets for added redundancy.

Data is then further divided based on where it was CLONE or SCRAPED from. This can cause some confusion because it is not necessarily 
organized by collection. However, sub folders are organized by collection
```
src
  |
  datasets
    |
    raw_data
        |
        cairo_genizah
            |
            cambridge_university
            |
            other_sources
            |
            princeton
            |
            academic_literature
                |
                cairo_to_manchester
        
        talmud_complete
            
    document_models
        |
        genizah_document.py
        |
        gemara_document.py
        |
        bilbliography_document.py
        
    indexing
        |
        bulk_insert_all_documents.py
        |
        elastic_index_genizah.py 
        

     
    
```
Under other_sources there are further subfolders for specific institutions such as Manchester, Paris, UPenn, etc. Due to 
copyright and respect for the authors reasons we cannot share the raw data in `academic_literature` with external parties.
Normally this data is the full length scanned material of the books or the downloaded articles from websites.

For purposes of training the transcription model we have also scraped the complete Talmud Bavli. This can be found on under the Talmud 
directory. 

Furthermore, we have added tons of newspapers from the NLI to help improve the transcription (RTL base model),

### Databases/Indexing 

We currently index to two primary places `elasticsearch` and `postgresql`. GenizahDocument under `genizah_document.py` does much of the heavy 
lifting when preparing data for elasticsearch indexing. The main indexing can be found under:

```
src
    |
    datasets
        |
        cairo_genizah
            |
            indexing
                |
                 elastic_index_genizah.py
                 |
                 image_url_helpers.py
                 |
                 sql
                    |
                    
                    
                 
            
```
We regularly generate new indices as we improve our scraping results and embedding models. However, for historical and reproducibility practices we will be backing up production ElasticSearch indices and making them publically accessible.



### Embeddings 

For embeddings we currently use NOMICs and CLIP primarily. See `[embedding_models.py](src/multimodal_embeddings/embedding_models.py)` for more specific usage information.  

As we continue to fine-tune embeddings we will publicly release the weights here. 

### Model Finetuning

### Secondary Source  Processing 

For secondary sources (e.g. journal articles, books, blog posts, etc) we apply a multi-step process to extract the data into a useful format for creating a searchable secondary source index. We believe this process can be reusable for a number of historical
documents beyond the Cairo Genizah. 


#### OCR 
Raw OCR can either be done with the:

 - Google Cloud Vision API 
 - Doctr 
 - Unstructured

For Hebrew and non-latin languages (especially Hebrew) we highly recommend the Google Cloud Vision API. It is one of the only ones where we have had reliable results.
`[book_ocr_service.py](src/models/ocr/book_ocr_service.py)`

###

### Further Documentation
We are currently in the process of building out Sphinx and ReadTheDocs. You can find information on specific APIs and services
located [here](multimodal-document-analysis.read-thedocs.com].


### Acknowledgements 

We thank the following for providing much of the meta-data, transcriptions,
```
Princeton Geniza Project, version [#]. Center for Digital Humanities at Princeton, [2025]. http://geniza.princeton.edu. Accessed 11/3/2025
```
[Princeton Cairo Genizah Project on GitHub](https://geniza.princeton.edu/en/)

Additionally, we thank the following institutions:

[University Manchester Rylands](https://luna.manchester.ac.uk/luna/servlet/ManchesterDev~95~2)

[Cambridge University](https://cudl.lib.cam.ac.uk/collections/genizah/1)

[Oxford University](https://genizah.bodleian.ox.ac.uk)


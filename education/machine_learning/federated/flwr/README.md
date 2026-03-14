# fantastic-enigma
Federated LLM Finetuning Playground

This GitHub repository is a companion resource to the following Medium article on Federated LLM finetuning: [Upcoming!](https://google.com)

<p align="center">
    <img src="./images/federated_learning.png">
</p>

## Content
In our notebooks folder, we demonstrate federated supervised finetuning of an LLM using the Flower AI framework.
```
.
|- notebooks
    |- llama32_1b_fed_finetuning.ipynb     <- Federated finetuning of a Llama 3.2 1B LLM. This is the main notebook discussed in the companion medium article
    |- pythia_70m_fed_finetuning.ipynb     <- Federated finetuning experiment on Pythia 70m LLM.  
```

## Getting started
```
uv sync
```
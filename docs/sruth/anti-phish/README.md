# anti-phish

*** 2026 reflection: My lecturer gave me positive feedbadck for this project in 2022. I no longer understand Dr Enda Barrett because he gave me an 85% for this project rather than capping it at 40% due to granting accomodations for my validated disability of Anxiety (Complex Post-Traumatic Stress Disorder) that many others since have gaslit me about falsely claiming stigmatising diagnoses and I'd rather be invisible and no longer understand why accomodations were granted (due to severe conditioning by others) and amn't allowed get trauma-informed care until my MSc in AI in September or Assisted Dying yet until my grandmother dies***


This project intends to highlight how the latest machine learning techniques can be used to train a model that will detect phishing emails.

Phishing has been described as "the most prevalent method of cybercrime that convinces people to provide sensitive information" (Salloum et al., 2021). Applications of social engineering, targeted research, and technological improvements have allowed for sophisticated phishing techniques to develop alongside improving attempts at their detection. There are many ways in which phishing attempts can be made, whether through SMS, phone calls, websites or emails. These attempts all tend to share the fact that they imitate a third party in an attempt to confuse the victim and convince them to share sensitive information.

The use of phishing emails has been on the rise, especially during/after the COVID-19 pandemic, with the Anti-Phishing Working Group reporting the detection of 128,926 phishing emails during Q3 of 2020 in comparison with 44,497 and 44,008 detected in Q2 and Q1 of 2020, respectively.

There has been extensive research into the application of artificial intelligence / machine learning techniques towards the improvement of phishing email detection: (Vazhayil and Nb, 2018), (Egozi and Verma, 2018), (Alhogail and Alsabih, 2021), (Divakaran and Oest, 2022)

Machine learning is described as "a scientific field that focuses on the design of computer models and algorithms that can perform specific tasks, often involving pattern recognition, without the need to be explicitly programmed"(Raschka, Patterson and Nolet, 2020). Within the last decade, the general-purpose Python language has seen a tremendous growth of popularity with the scientific computing community. The most recent machine learning and deep learning libraries are now Python-based.

Open-source, community-contributed libraries such as Pandas, NumPy, Scikit-learn, and PyTorch provide a relatively easy to learn ecosystem for the machine learning community to develop within.

The task of phishing email detection can be described as a Natural Language Processing problem of text classification. By learning from pre-defined classes of phishing or legitimate emails, models can be trained on previously collected emails and through reinforcement learning or deep learning be able to identify new previously unseen email samples.

This project will walkthrough the required steps and different methods of creating a phishing email detector over the course of 6 different Colab Notebooks:

1. Data Extraction
2. [Classical Machine Learning Classification Methods  (Sci-kit Learn)](https://colab.research.google.com/drive/1uAGq5z3_AOcMHMNHxmCWT9Hj8RNZQZRR?usp=sharing)
3. [Deep Learning with PyTorch](https://colab.research.google.com/drive/10Q7_gMq9MxxY9vpBwHDO_uokGEVNCoKw?usp=sharing)
4. [Deep Learning with HuggingFace Transformers](https://colab.research.google.com/drive/1zmokI_UWsUMJ-cumXlaxaEXHWX6_Vlrs?usp=sharing)
5. [A look into Federated Learning with Flower](https://colab.research.google.com/drive/1-CcQWBGSY6U1FHZ7j_m4_z9D8DwW43eL?usp=sharing)
6. [Finished phishing detector hosted via Gradio](https://colab.research.google.com/drive/13arA1h6_yBiPJkxHCIrmiRo5IT8YjaBO?usp=sharing)


![example features](https://github.com/foghlaimeoir/anti-phish/blob/main/docs/img/Example%20Features.png)
![example scikit-learn](https://github.com/foghlaimeoir/anti-phish/blob/main/docs/img/Example%20scikit-learn.png)
![example Gradio UI](https://github.com/foghlaimeoir/anti-phish/blob/main/docs/img/Gradio%20UI.png)

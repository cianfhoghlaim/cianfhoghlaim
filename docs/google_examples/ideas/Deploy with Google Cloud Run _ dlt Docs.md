---
title: "Deploy with Google Cloud Run | dlt Docs"
source: "https://dlthub.com/docs/walkthroughs/deploy-a-pipeline/deploy-with-google-cloud-run"
author:
published:
created: 2025-12-29
description: "Step-by-step guide on deploying a pipeline with Google Cloud Run."
tags:
  - "clippings"
---
Version: 1.20.0 (latest)

This guide explains how to deploy a pipeline using the gcloud shell and dlt CLI commands. To deploy a pipeline using this method, you must have a working knowledge of GCP and its associated services, such as Cloud Run jobs, IAM and permissions, and GCP service accounts.

Deploy the pipeline using Google Cloud Run jobs. First, navigate to the directory on your local machine or cloud repository (e.g., GitHub, Bitbucket) where you want to create the function code for deployment.

## 1\. Setup pipeline

1. In this guide, we set up the dlt [Notion verified source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/notion). However, you can use any verified source or create a custom one.
2. Run the following command to initialize the verified source with Notion and create a pipeline example with BigQuery as the target.
	```sh
	dlt init notion bigquery
	```
	- After the command executes, new files and folders with the necessary configurations are created in the main directory.
	- Detailed information about initializing a verified source and a pipeline example is available in the dlthub [documentation](https://dlthub.com/docs/dlt-ecosystem/verified-sources/notion).
3. Create a new file named "Procfile" in the main directory and configure it as follows:
	```sh
	web: python3 notion_pipeline.py
	```
	This instructs the Cloud Run job to run "notion\_pipeline.py", using python3.
4. If you need any additional dependencies, add them to the "requirements.txt" that was created.

## 2\. Deploying GCP Cloud Run Jobs

In the terminal, navigate to the directory where the "notion\_pipeline.py" file is located and run the following command in the terminal:

```sh
gcloud run jobs deploy notion-pipeline-job \    --source . \    --tasks 1 \    --max-retries 5 \    --cpu 4 \    --memory 4Gi \    --region us-central1 \    --project dlthub-sandbox
```
- This command creates a Cloud Run job. The source "." refers to all files in the directory. The number of vCPUs is set to 4 and memory 4GiB. You can tweak the parameters as per your requirement. To learn more about deploying the Cloud Run job, read the [documentation here.](https://cloud.google.com/run/docs/create-jobs#gcloud)
- By default, Cloud Run jobs have a 10-minute timeout, you can increase this up to 1440 minutes (24 hours). To learn more about the function timeout, see the [documentation here](https://cloud.google.com/run/docs/configuring/task-timeout).

> Your project has a default service account associated with the project ID. Please assign the `roles/run.invoker` role to the associated service account.

## 3\. Setting up environment variables in Cloud Run

Do not add secrets directly to the "secrets.toml" file, as it will be included in the deployed container for executing the job. Instead, use environment variables or Google Secrets Manager, as described below. Environment variables can be set in Cloud Run in two ways:

#### 3a. Directly in the function:

- Go to the Google Cloud Run job and select the deployed function. Click "VIEW AND EDIT JOB CONFIGURATION".
- In the "CONTAINERS" > "VARIABLE AND SECRETS" > "ADD VARIABLE".
- Enter a name for the variable according to the pipeline's requirements. Make sure to capitalize the variable name if it is specified in "secrets.toml". For example, if the variable name is `sources.notion.api_key`, set the variable name to `SOURCES__NOTION__API_KEY`.
- Enter the value for the Notion API key.
- Click "Done" and update the function.

#### 3b. Use GCP Secret Manager:

- Go to the Google Cloud Run job and select the deployed function. Click "VIEW AND EDIT JOB CONFIGURATION".
- In the "Containers" > "VARIABLE AND SECRETS" > "ADD VARIABLE".
- Click "Add a secret reference" and select the secret you created, for example, "notion\_secret".
- Set the "REFERENCE A SECRET" to mounted as an environment variable.
- In the "Environment Variable" field, enter the environment variable's name that corresponds to the argument required by the pipeline. Remember to capitalize the variable name if it is required by the pipeline and specified in secrets.toml. For example, if the variable name is `sources.notion.api_key`, you would declare the environment variable as `SOURCES__NOTION__API_KEY`.
- Select the secret to reference.
- Click "Done" and update the function.
- “Assign the Secret Manager Secret Accessor role to the Cloud Run service account. Typically, this is the default service account associated with the Google Project in which the function is being created.

## 4\. Monitor (and manually trigger) the Cloud Run

To manually trigger the job, click "EXECUTE". You can also set up a scheduled trigger to automate runs.

That's it! Have fun using dlt in Google Cloud Run!

This demo works on codespaces. Codespaces is a development environment available for free to anyone with a Github account. You'll be asked to fork the demo repository and from there the README guides you with further steps.

The demo uses the Continue VSCode extension.

  
[Off to codespaces!](https://github.com/codespaces/new/dlt-hub/dlt-llm-code-playground?ref=create-pipeline)

## DHelp

## Ask a question

Welcome to "Codex Central", your next-gen help center, driven by OpenAI's GPT-4 model. It's more than just a forum or a FAQ hub – it's a dynamic knowledge base where coders can find AI-assisted solutions to their pressing problems. With GPT-4's powerful comprehension and predictive abilities, Codex Central provides instantaneous issue resolution, insightful debugging, and personalized guidance. Get your code running smoothly with the unparalleled support at Codex Central - coding help reimagined with AI prowess.
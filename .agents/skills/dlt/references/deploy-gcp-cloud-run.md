# Deploy: GCP Cloud Run (long-running)

Deploy a dlt pipeline as a **long-running** GCP Cloud Run job.
Useful for pipelines that take > 9 minutes (the Cloud Functions
limit).

## Pattern (Job)

```yaml
# job.yaml
apiVersion: run.googleapis.com/v1
kind: Job
metadata:
  name: dlt-pipeline-job
spec:
  template:
    spec:
      template:
        spec:
          containers:
            - image: gcr.io/PROJECT/dlt-pipeline:latest
              resources:
                limits:
                  memory: 4Gi
                  cpu: 2
              env:
                - name: DLT_DISABLE_PLUGINS
                  value: "true"
                - name: DESTINATION__BIGQUERY__CREDENTIALS
                  valueFrom:
                    secretKeyRef:
                      name: gcp-sa-key
                      key: latest
          restartPolicy: Never
          maxRetries: 5
          completionMode: Indexed
```

## Deploy

```bash
# Build and push the image
gcloud builds submit --tag gcr.io/PROJECT/dlt-pipeline:latest

# Run the job
gcloud run jobs execute dlt-pipeline-job --region europe-west1
```

## Schedule with Cloud Scheduler

```bash
gcloud scheduler jobs create http dlt-pipeline-schedule \
  --schedule "0 2 * * *" \
  --time-zone "Europe/Dublin" \
  --http-method POST \
  --uri https://europe-west1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT/jobs/dlt-pipeline-job:run \
  --oauth-service-account-email your-sa@PROJECT.iam.gserviceaccount.com
```

## Pattern (Service)

For a long-running service that polls a queue or watches a file
system, use a Cloud Run service (not a job):

```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: dlt-pipeline-service
spec:
  template:
    spec:
      containers:
        - image: gcr.io/PROJECT/dlt-pipeline:latest
          ports:
            - containerPort: 8080
          env:
            - name: DLT_DISABLE_PLUGINS
              value: "true"
```

## KCG usage

The KCG stack uses **Dagster on `bunchloch` (M4 Mac) + `arm1-oci`
(ARM)** for orchestration. GCP Cloud Run is a valid alternative
for cloud-only deployments.

## Reference

- The `Deploy with Google Cloud Run _ dlt Docs.md` (6.0K) was in
  `docs/dlt/` (deleted with the `sync-skills-from-docs` change)
- The GCP Cloud Run docs: <https://cloud.google.com/run/docs>
- The dltHub BigQuery destination: <https://dlthub.com/docs/dlt-ecosystem/destinations/bigquery>

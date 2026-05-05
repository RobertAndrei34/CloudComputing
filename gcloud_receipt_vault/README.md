# Receipt Vault on Google Cloud

A small but complete Google Cloud application that satisfies the assignment constraints:

- **Hosted on App Engine**, so it is available on the `*.appspot.com` domain.
- Uses **at least three Google Cloud services**:
  1. **App Engine** for hosting the web application.
  2. **Cloud Firestore** as the **stateful** service for metadata persistence.
  3. **Cloud Storage** for uploaded file storage.
- Uses **one Google Cloud API optionally**:
  4. **Cloud Vision API** for OCR and automatic image labeling.

## What the app does

Users can upload a receipt or invoice image/PDF, assign a title/category/amount, and then:

- the file is saved in **Cloud Storage**;
- the metadata is saved in **Firestore**;
- the text and labels are extracted through **Vision API** (optional);
- the UI runs on **App Engine**.

This creates a realistic cloud-native document processing application rather than a trivial demo.

## Why these services

### 1) App Engine
Chosen because the assignment explicitly requires an application reachable through the **`appspot.com`** domain.
App Engine is the most direct fit:

- automatic deployment with `gcloud app deploy`
- built-in scaling
- no VM management
- standard web application workflow

Why not Cloud Run?
Cloud Run is excellent, but the assignment explicitly mentions the `appspot.com` domain, which naturally points to **App Engine**.

### 2) Cloud Firestore (stateful service)
Chosen as the stateful component because the app stores structured metadata:

- receipt title
- category
- amount
- upload timestamp
- OCR text
- labels
- file reference in Cloud Storage

Why Firestore instead of Cloud SQL?
Firestore fits better because the data model is document-oriented, the schema is flexible, and the application needs simple CRUD with low operational overhead.

### 3) Cloud Storage
Chosen because uploaded receipts are binary files, which are a natural fit for object storage.

Why not store the files inside Firestore?
Firestore is not meant for large binary file storage. Cloud Storage is cheaper, more scalable, and designed for durable object storage.

### 4) Vision API (optional API substitution)
This is the single allowed API-based substitution mentioned in the assignment.
It adds meaningful complexity:

- OCR for text extraction
- label detection for automatic classification

That makes the project stronger than a plain upload app.

## Architecture

```text
Browser
  |
  v
App Engine (Flask)
  |----> Cloud Storage  (stores receipt files)
  |----> Firestore      (stores metadata)
  |----> Vision API     (extracts OCR and labels)
```

## Project structure

```text
gcloud_receipt_vault/
├── app.py
├── app.yaml
├── requirements.txt
├── README.md
├── static/
│   └── styles.css
└── templates/
    ├── base.html
    ├── detail.html
    └── index.html
```

## Prerequisites

- Google Cloud project
- billing enabled
- Python 3.11+
- `gcloud` CLI installed

## Enable services

```bash
gcloud services enable appengine.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  vision.googleapis.com
```

## One-time setup

### 1. Create the App Engine application

```bash
gcloud app create --region=europe-west1
```

### 2. Create Firestore database

Use Native mode in the Google Cloud console.

### 3. Create a Cloud Storage bucket

```bash
gsutil mb -l europe-west1 gs://YOUR_BUCKET_NAME
```

### 4. Update `app.yaml`

Replace:

```yaml
RECEIPT_BUCKET: "YOUR_BUCKET_NAME"
```

with your actual bucket name.

## Run locally

Set environment variables first:

```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export RECEIPT_BUCKET="YOUR_BUCKET_NAME"
export ENABLE_VISION="true"
export FLASK_SECRET_KEY="local-dev-secret"
```

Install dependencies and start the app:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8080`.

## Deploy to App Engine

```bash
gcloud app deploy
```

After deployment, the app will be available at:

```text
https://YOUR_PROJECT_ID.appspot.com
```

That satisfies the assignment rule that the application must be located in the `appspot.com` domain.

## Security / production notes

For a classroom project, the current version is enough. For a production-grade version, you could add:

- authentication with Identity Platform or Firebase Authentication
- signed URLs instead of public Cloud Storage links
- background OCR with Pub/Sub + Cloud Functions or Cloud Run jobs
- validation and quotas
- IAM hardening

## Assignment checklist

- [x] Uses **at least three Google Cloud services**
- [x] Includes **one stateful service**: Firestore
- [x] Is deployable on **`appspot.com`** via App Engine
- [x] Uses a framework: **Flask**
- [x] Uses **only one API substitution**: Vision API
- [x] Includes motivation for service choices

## Suggested presentation pitch

> I built a cloud-native receipt management application on Google Cloud. The application is hosted on App Engine, which ensures deployment on the appspot.com domain required by the assignment. It uses Firestore as the stateful service for storing document metadata, Cloud Storage for storing uploaded receipt files, and Vision API for OCR and label extraction. I chose Firestore over Cloud SQL because the receipt metadata is document-shaped and benefits from flexible schema and low operational overhead. I chose Cloud Storage because binary uploads are a natural fit for object storage. This architecture is simple, scalable, and clearly demonstrates service separation inside the Google Cloud ecosystem.

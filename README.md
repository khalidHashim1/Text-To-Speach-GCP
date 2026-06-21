# Architecture Overview: Serverless Text-to-Speech (TTS) Converter

This project implements a fully serverless, asynchronous microservice backend built on **Google Cloud Platform (GCP)**. It exposes a secure, CORS-enabled REST API endpoint that accepts raw text input, converts it into high-fidelity synthetic audio, saves the output persistently, and returns a secure, time-limited download URL to the client.

---

## 🏗️ Architectural Components

The system is decoupled into four primary infrastructure pillars:

### 1. Compute Layer: Cloud Run (Functions V2)
* **Role:** Event-driven backend API execution framework.
* **How it works:** The Python runtime handles incoming HTTPS requests. It operates on a **scale-to-zero** configuration, meaning infrastructure resources are only consumed and billed during active request processing, minimizing operational overhead.
* **Runtime Framework:** Wrapped natively via the Google Functions Framework, exposed as a serverless web container listening internally on `PORT 8080`.

### 2. Processing Layer: Google Cloud Text-to-Speech API
* **Role:** Neural audio synthesis engine.
* **How it works:** The compute layer passes raw string data to the TTS API. The engine applies advanced WaveNet neural networks (DeepMind) to generate human-like speech patterns, returning raw, synthesized binary audio content (`MP3` format) back to the application.

### 3. Storage Layer: Google Cloud Storage (GCS)
* **Role:** Immutable object storage.
* **How it works:** The synthesized audio byte stream is not stored locally on the volatile serverless container. Instead, it is instantly streamed to a globally unique storage bucket (`bootcamp.khalidhashim.com`) as an isolated blob named with a unique UUID string (`tts-[UUID].mp3`).

### 4. Security & Access Layer (IAM & Signed URLs)
* **Role:** Multi-layered security and data protection.
* **Service Accounts:** Cloud Run executes under a restricted **IAM (Identity and Access Management)** service account bound explicitly to the `roles/storage.objectAdmin` role, adhering strictly to the principle of least privilege.


---

## ⚡ Key Technical Strengths to Highlight in Interviews

* **Zero Infrastructure Management:** The entire application code relies on abstraction layers. There are zero Linux VMs to patch, no OS instances to secure, and no web servers to maintain manually.
* **Absolute Cost Optimization:** Because every service is strictly on-demand, this architecture runs entirely within GCP's free tier for low volumes. Storage is billed per gigabyte-month, and compute scales down to zero when idle.
* **Decoupled Architecture:** The system separates computing (`Cloud Run`) from storage (`GCS`). If thousands of users pull files simultaneously, it puts zero memory or CPU strain on your application workers because the client downloads directly from Google's global storage network edge.

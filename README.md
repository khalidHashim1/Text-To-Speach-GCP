Architecture Overview: Serverless Text-to-Speech (TTS) Converter
This project implements a fully serverless, asynchronous microservice backend built on Google Cloud Platform (GCP). It exposes a secure, CORS-enabled REST API endpoint that accepts raw text input, converts it into high-fidelity synthetic audio, saves the output persistently, and returns a secure, time-limited download URL to the client.

🏗️ Architectural Components
The system is decoupled into four primary infrastructure pillars:

1. Compute Layer: Cloud Run (Functions V2)
Role: Event-driven backend API execution framework.

How it works: The Python runtime handles incoming HTTPS requests. It operates on a scale-to-zero configuration, meaning infrastructure resources are only consumed and billed during active request processing, minimizing operational overhead.

Runtime Framework: Wrapped natively via the Google Functions Framework, exposed as a serverless web container listening internally on PORT 8080.

2. Processing Layer: Google Cloud Text-to-Speech API
Role: Neural audio synthesis engine.

How it works: The compute layer passes raw string data to the TTS API. The engine applies advanced WaveNet neural networks (DeepMind) to generate human-like speech patterns, returning raw, synthesized binary audio content (MP3 format) back to the application.

3. Storage Layer: Google Cloud Storage (GCS)
Role: Immutable object storage.

How it works: The synthesized audio byte stream is not stored locally on the volatile serverless container. Instead, it is instantly streamed to a globally unique storage bucket (bootcamp.khalidhashim.com) as an isolated blob named with a unique UUID string (tts-[UUID].mp3).

4. Security & Access Layer (IAM & Signed URLs)
Role: Multi-layered security and data protection.

Service Accounts: Cloud Run executes under a restricted IAM (Identity and Access Management) service account bound explicitly to the roles/storage.objectAdmin role, adhering strictly to the principle of least privilege.

🔄 End-to-End Data Flow
[ Client Frontend ]
       │
       │ 1. POST /tts-converter { text: "Hello World" }
       ▼
[ Cloud Run Service ] ──( 2. Validates & forwards text )──► [ GCP Text-to-Speech ]
       │                                                             │
       │ 4. Streams raw MP3 bytes                                    │ 3. Generates audio bytes
       ▼                                                             ▼
[ Cloud Storage Bucket ] ◄───────────────────────────────────────────┘
       │
       │ 5. Generates cryptographic V4 Signed URL
       ▼
[ Cloud Run Service ] ──( 6. Returns JSON { audio_url: "..." } )──► [ Client Frontend ]

Ingress: The client application initiates an asymmetric HTTPS POST request carrying a JSON payload containing the target string.

Pre-flight (CORS): The function handles HTTP OPTIONS requests natively, returning appropriate Access-Control headers (*) to eliminate browser cross-origin blocking.

Synthesis: The function instantiates the TextToSpeechClient(), authenticates implicitly via metadata credentials, and requests audio translation using the premium neural voice profile (en-US-Wavenet-F).

Persistence: The resulting binary payload is transferred to Google Cloud Storage under a randomly generated, unguessable uuid4 namespace.

Token Generation: The application calls GCS signing libraries to append an authentication token directly onto the target object URI path.

Egress: The function formats a clean 200 OK JSON response containing the temporary download URL back to the frontend listener.

⚡ Key Technical Strengths to Highlight in Interviews
If a technical recruiter asks you about this design, emphasize these three cloud concepts:

Zero Infrastructure Management: The entire application code relies on abstraction layers. There are zero Linux VMs to patch, no OS instances to secure, and no web servers (like Nginx) to maintain manually.

Absolute Cost Optimization: Because every service is strictly on-demand, this architecture runs entirely within GCP's free tier for low volumes. Storage is billed per gigabyte-month, and compute scales down to zero when idle.

Decoupled Architecture: The system separates computing (Cloud Run) from storage (GCS). If thousands of users pull files simultaneously, it puts zero memory or CPU strain on your application workers because the client downloads directly from Google's global storage network edge.
Presigned Assets: To prevent exposing the storage bucket completely to the public internet, the application generates a cryptographic V4 Signed URL with a strict 64-bit signature and an automated expiration window (1 hour). The frontend can stream or download the audio asset directly through this link without needing a GCP login.

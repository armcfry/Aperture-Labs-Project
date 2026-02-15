# Aperture Labs - FOD Detection

CSCI 577A Spring 2026 Group Project

Foreign Object Debris (FOD) detection using Vision Language Models.

## Setup

### 1. Install Ollama

Download from https://ollama.com

### 2. Pull the model and start server

```bash
ollama pull qwen2.5vl:7b
ollama serve
```

### 3. Setup backend (first time only)

```bash
cd backend
setup.bat
```

### 4. Run the server

```bash
cd backend
run.bat
```

## API

Swagger UI: http://localhost:8000/docs

### POST /api/detect

Upload an image to detect FOD. Returns location and description of any FOD found.

**Test with curl (Windows):**
```bash
curl.exe -X POST http://localhost:8000/api/detect -F "file=@data/FOD_pictures/bolt_in_front_of_plane.png"
```

**Response:**
Raw response
{"response":"In the image, there is a visible Foreign Object Debris (FOD) item in the foreground. Here is the description:\n\n- **Item**: The item appears to be a cylindrical object with markings that read \"48 FW - GOLDEN BOLT.\" It looks like a spent cartridge or a similar type of ammunition casing.\n- **Location**: It is lying on the ground in the foreground, closer to the bottom left corner of the image.\n\nThis item is likely FOD and should be removed to ensure safety and operational readiness."}


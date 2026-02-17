# Aperture Labs - FOD Detection

CSCI 577A Spring 2026 Group Project

Foreign Object Debris (FOD) detection using Vision Language Models.

## Getting Started

### Backend Setup  

#### 1. Install Ollama

Download from https://ollama.com

#### 2. Pull the model and start server

```bash
ollama pull qwen2.5vl:7b
ollama serve
```

#### 3. Setup backend (first time only)

```bash
cd backend
setup.bat
```

#### 4. Run the server

```bash
cd backend
run.bat
```

### Frontend Setup

#### 1. Install Node.js

Ensure you have node 22.13+ and npm v10+ installed. Use nvm to install or update your node version if necessary.

#### 2. Install packages

```bash
cd frontend
npm install
```

#### 3. Run the development server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

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

## Using docker to spin up the database containers

#### 1. Make sure you have docker desktop installed.
#### 2. Install docker cli.
#### 3. Spin up containers

    docker compose up -d

This will create two containers. One contains the postgres database, the other holds the minio storage. In the /backend/db/init.sql, two tables are created in the postgres db. One for `users` and the other for `fod_detection` (subject to change.) Database information will persist unless the volumes are deleted.

#### 4. To stop running containers (not remove volume)
    docker compose stop

#### 5. To remove the containers and remove the volumes:
    docker compose down -v
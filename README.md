# Aperture Labs - FOD Detection

CSCI 577A Spring 2026 Group Project

Foreign Object Debris (FOD) detection using Vision Language Models.

## Getting Started

### For Code Quality Metrics

SonarQube: https://sonarcloud.io/project/overview?id=Aperture-Labs-SP-26_Aperture-Labs-Project

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

Ensure you have Node.js 22.13.0 (LTS). Use nvm to install or switch versions; run `nvm use` from the frontend directory.

#### 2. Install packages

```bash
cd frontend
npm install
```

#### 3. Run the development server
```bash
npm run dev
```

Open [http://localhost:3998](http://localhost:3998) with your browser to see the result.

See [frontend/README.md](frontend/README.md) for more details.

## API

Can use Swagger UI: http://localhost:8000/docs or commands below

### `POST /api/login`

Authenticate a user with username and password.

**Test with curl (Windows):**
```powershell
curl.exe --% -X POST http://localhost:8000/api/login -H "Content-Type: application/json" -d "{\"username\":\"test\",\"password\":\"test\"}"
```

**Response:**
```json
{"success":true,"user":{"username":"test"},"message":"Login successful"}
```

### `POST /api/detect`

Upload an image to detect FOD. Returns location and description of any FOD found.

**Test with curl (Windows):**
```powershell
curl.exe -X POST "http://localhost:8000/api/detect" -F "file=@data/FOD_pictures/bolt_in_front_of_plane.png"
```

**Response:**
`{"response":"In the image, there is a visible Foreign Object Debris (FOD) item in the foreground. Here is the description:\n\n- **Item**: The item appears to be a cylindrical object with markings that read \"48 FW - GOLDEN BOLT.\" It looks like a spent cartridge or a similar type of ammunition casing.\n- **Location**: It is lying on the ground in the foreground, closer to the bottom left corner of the image.\n\nThis item is likely FOD and should be removed to ensure safety and operational readiness."}`

### `POST /api/projects/create`

Create a new project. Required before uploading images.

**Test with curl (Windows):**
```powershell
curl.exe --% -X POST http://localhost:8000/api/projects/create -H "Content-Type: application/json" -d "{\"name\":\"TestProject\"}"
```

**Response:**
```json
{"id":"a1b2c3d4-e5f6-7890-abcd-ef1234567890","name":"TestProject","created_at":"2026-02-21T12:00:00","design_specs":[]}
```

### `GET /api/projects/list`

List all projects.

**Test with curl (Windows):**
```powershell
curl.exe -X GET "http://localhost:8000/api/projects/list"
```

### `POST /api/upload/image`

Upload an image to MinIO storage. Requires a valid project ID.

**Step 1: Create a project (see above) and copy the `id` from the response.**

**Step 2: Upload image using the project ID:**
```powershell
curl.exe -X POST "http://localhost:8000/api/upload/image?project_id=YOUR_PROJECT_ID" -F "file=@data/FOD_pictures/bolt_in_front_of_plane.png"
```

**Response:**
```json
{"filename":"bolt_in_front_of_plane.png","project_id":"a1b2c3d4-e5f6-7890-abcd-ef1234567890","object_key":"a1b2c3d4-e5f6-7890-abcd-ef1234567890/bolt_in_front_of_plane.png"}
```

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
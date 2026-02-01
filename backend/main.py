from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Aperture Labs API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # next.js default dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World. TODO: Pass chatmessages via api"}

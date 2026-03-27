from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.transcribe import router as transcribe_router
from routes.translate import router as translate_router
from routes.dub import router as dub_router
from routes.projects import router as projects_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://subdub-api.vapai.studio",
        "https://sub-dub-psi.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(transcribe_router)
app.include_router(translate_router)
app.include_router(dub_router)

@app.get("/")
def root():
    return {"message": "SUB-DUB Backend corriendo ✓"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.performance_routes import router as performance_router
from app.routes.training_routes import router as training_router
from app.routes.predict_router import router as predict_router
from app.routes.volume_routes import router as volume_router

app = FastAPI()

app.include_router(performance_router)
app.include_router(training_router)
app.include_router(volume_router)
app.include_router(predict_router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)
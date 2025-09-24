from fastapi import FastAPI
from routes.pieceRoutes import router as pieceRouter
from routes.combinedPiecesRoutes import router as combinedPieceRouter
from dataBase.DBConfing import connect_to_db, close_db
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",             # tu frontend en dev
        "https://setsunai-front.vercel.app"  # frontend en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(pieceRouter, prefix="/authPiece", tags=["Piece"])
app.include_router(combinedPieceRouter, prefix="/authCombinedPieces", tags=["CombinedPieces"])


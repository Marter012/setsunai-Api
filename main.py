from fastapi import FastAPI
from routes.pieceRoutes import router as pieceRouter
from routes.combinedPiecesRoutes import router as combinedPieceRouter
from dataBase.DBConfing import connect_to_db, close_db
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)

# Rutas
app.include_router(pieceRouter, prefix="/authPiece", tags=["Piece"])
app.include_router(combinedPieceRouter, prefix="/authCombinedPieces", tags=["CombinedPieces"])


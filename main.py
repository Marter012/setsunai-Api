from fastapi import FastAPI
from routes.pieceRoutes import router as pieceRouter
from routes.combinedPiecesRoutes import router as combinedPieceRouter
from routes.bonusProduct import router as bonusProduct
from dataBase.DBConfing import connect_to_db, close_db,init_indexes
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
   # 🔹 Startup
    await connect_to_db()
    await init_indexes()   # 👈 ACÁ se crea el índice único
    yield
    # 🔹 Shutdown
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
app.include_router(bonusProduct, prefix="/authBonusProduct", tags=["BonusProduct"])


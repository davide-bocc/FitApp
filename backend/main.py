from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect, create_engine
from pathlib import Path
import logging

from backend.core.config import settings
from backend.core.dependencies import get_current_active_user
from backend.core.database import async_engine, AsyncSessionLocal, get_db_session
from backend.routers.auth import router as auth_router
from backend.routers.coach import router as coach_router
from backend.routers.trainee import router as trainee_router
from backend.routers.workout_router import router as workout_router
from backend.routers.exercise_router import router as exercise_router
from backend.core.auth_dependencies import get_db
from backend.db_models.base import Base
from backend.schemas.workout_schemas import resolve_forward_refs
resolve_forward_refs()
from backend.core.token_middleware import token_validator_middleware

# Motore sincrono per inspect in health check
sync_engine = create_engine(settings.SYNC_DATABASE_URL)

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from backend.db_models.user_models import User as UserModel
        from backend.db_models.workout import Workout as WorkoutModel
        from backend.db_models.workout import WorkoutAssignment as WorkoutAssignmentModel
        from backend.db_models.exercise import Exercise as ExerciseModel

        logger.info("\n🔧 Configurazione ambiente:")
        logger.info(f"- DEV_MODE: {settings.DEV_MODE}")
        logger.info(f"- DB URL: {settings.SYNC_DATABASE_URL}")
        logger.info(f"- CORS Origins: {settings.CORS_ALLOWED_ORIGINS}")

        logger.info("\n🔎 Modelli importati:")
        logger.info(f"- User: {UserModel.__tablename__}")
        logger.info(f"- Workout: {WorkoutModel.__tablename__}")
        logger.info(f"- Exercise: {ExerciseModel.__tablename__}")
        logger.info(f"- WorkoutAssignment: {WorkoutAssignmentModel.__tablename__}")

        if settings.DEV_MODE:
            logger.info("\n⚙️ Modalità sviluppo attiva")
            db_path = settings.SYNC_DATABASE_URL.replace("sqlite:///", "")
            logger.info(f"📂 Percorso database: {Path(db_path).absolute()}")

        # Creazione tabelle e indici
        async with async_engine.begin() as conn:
            inspector = await conn.run_sync(lambda sync_conn: inspect(sync_conn))

            existing_tables = set(await conn.run_sync(lambda sync_conn: inspector.get_table_names()))
            required_tables = set(Base.metadata.tables.keys())

            tables_to_create = [Base.metadata.tables[table] for table in (required_tables - existing_tables)]
            if tables_to_create:
                await conn.run_sync(
                    lambda sync_conn: Base.metadata.create_all(
                        sync_conn,
                        tables=tables_to_create,
                        checkfirst=True
                    )
                )
                logger.info("\n✅ Tabelle create:")
                for table in tables_to_create:
                    logger.info(f"- {table.name}")
            else:
                logger.info("\nℹ️ Tutte le tabelle esistono già")

            logger.info("\n🔍 Verifica indici:")
            for table_name, table in Base.metadata.tables.items():
                if table_name not in existing_tables:
                    continue

                existing_indexes = await conn.run_sync(
                    lambda sync_conn, tn=table_name: inspector.get_indexes(tn)
                )
                existing_index_names = {idx['name'] for idx in existing_indexes}

                for index in table.indexes:
                    if index.name not in existing_index_names:
                        try:
                            await conn.run_sync(
                                lambda sync_conn, idx=index: idx.create(sync_conn)
                            )
                            logger.info(f"  ✅ Creato indice {index.name} su {table_name}")
                        except Exception as e:
                            logger.warning(f"  ⚠️ Errore creazione indice {index.name}: {str(e)}")
                    else:
                        logger.debug(f"  ✔️ Indice {index.name} esiste già su {table_name}")

            # Indici aggiuntivi richiesti
            required_indexes = {
                'users': [
                    {'name': 'uidx_users_email', 'columns': ['email'], 'unique': True},
                ],
                'workout_assignments': [
                    {'name': 'uidx_assignments_user_workout',
                     'columns': ['user_id', 'workout_id'], 'unique': True}
                ]
            }

            for table, indexes in required_indexes.items():
                existing_indexes = await conn.run_sync(
                    lambda sync_conn, t=table: inspector.get_indexes(t))

                existing_index_names = {idx['name'] for idx in existing_indexes}

                for index in indexes:
                    if index['name'] not in existing_index_names:
                        try:
                            columns = ", ".join(index['columns'])
                            unique = "UNIQUE" if index['unique'] else ""
                            await conn.execute(text(
                                f"CREATE {unique} INDEX IF NOT EXISTS {index['name']} "
                                f"ON {table} ({columns})"
                            ))
                            logger.info(f"  ✅ Creato indice aggiuntivo {index['name']} su {table}")
                        except Exception as e:
                            logger.error(f"  ❌ Errore creazione indice aggiuntivo {index['name']}: {str(e)}")

        if settings.POPULATE_TEST_DATA:
            logger.info("\n🌱 Popolamento dati di test...")
            try:
                from backend.tests.populate_test_data import populate_test_data
                async with AsyncSessionLocal() as db:
                    await populate_test_data(db)
                logger.info("✅ Dati di test inseriti con successo")
            except Exception as e:
                logger.error(f"❌ Errore durante il popolamento: {str(e)}")
                if settings.DEV_MODE:
                    raise

        yield

    except Exception as e:
        logger.critical(f"⛔ Errore critico durante l'avvio: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("\n🔌 Pulizia risorse...")
        await async_engine.dispose()


app = FastAPI(
    title="FitApp API",
    description="API completa per la gestione di palestre e allenamenti",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEV_MODE else None,
    redoc_url="/redoc" if settings.DEV_MODE else None,
    openapi_url="/openapi.json" if settings.DEV_MODE else None,
    swagger_ui_parameters={
        "syntaxHighlight": False,
        "tryItOutEnabled": True,
        "displayRequestDuration": True,
        "filter": True,
        "showExtensions": True,
    },
    responses={
        401: {"description": "Non autorizzato"},
        403: {"description": "Operazione non permessa"},
        404: {"description": "Risorsa non trovata"},
        500: {"description": "Errore interno del server"}
    }
)

# CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

# Middleware personalizzato per validazione token
app.middleware("http")(token_validator_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Middleware logging richieste in DEV_MODE
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    if settings.DEV_MODE:
        response.headers["Access-Control-Expose-Headers"] = "*"
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


# Endpoint principale (home page)
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>FitApp API</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 2rem; }}
                a {{ color: #2563eb; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>FitApp API</h1>
                <p>Versione: {app.version}</p>
                <p>Ambiente: {'Sviluppo' if settings.DEV_MODE else 'Produzione'}</p>

                <h2>Documentazione</h2>
                <ul>
                    <li><a href="/docs">Swagger UI</a></li>
                    <li><a href="/redoc">ReDoc</a></li>
                </ul>

                <h2>Endpoint Utili</h2>
                <ul>
                    <li><a href="/health">Health Check</a></li>
                    <li><a href="/auth/login">Login</a></li>
                </ul>
            </div>
        </body>
    </html>
    """


# Health check
@app.get("/health", include_in_schema=False)
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Verifica connessione DB
        await db.execute(text("SELECT 1"))

        # Controllo presenza tabelle (usando motore sync per inspect)
        required_tables = {"users", "workouts", "exercises", "workout_assignments"}
        inspector = inspect(sync_engine)
        existing_tables = set(inspector.get_table_names())

        status = {
            "status": "healthy",
            "database": "connected",
            "missing_tables": list(required_tables - existing_tables),
            "environment": "development" if settings.DEV_MODE else "production",
            "version": app.version
        }

        if status["missing_tables"]:
            logger.warning(f"Tabelle mancanti: {status['missing_tables']}")
            status["status"] = "degraded"

        return status

    except Exception as e:
        logger.error(f"Health check fallito: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "environment": "development" if settings.DEV_MODE else "production"
            }
        )


# Registrazione router con gestione errori e dipendenze
routers = [
    (auth_router, "/auth", "Authentication"),
    (coach_router, "/coaches", "Coaches"),
    (trainee_router, "/trainees", "Trainees"),
    (workout_router, "/workouts", "Workouts"),
    (exercise_router, "/exercises", "Exercises")
]

for router, prefix, tags in routers:
    try:
        app.include_router(
            router,
            prefix=prefix,
            tags=[tags],
            dependencies=[Depends(get_current_active_user)] if prefix != "/auth" else None
        )
        logger.info(f"✅ Router registrato: {prefix}")
    except Exception as e:
        logger.error(f"❌ Errore registrazione router {prefix}: {str(e)}")
        if settings.DEV_MODE:
            raise


# Endpoint favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEV_MODE,
        log_level="info"
    )

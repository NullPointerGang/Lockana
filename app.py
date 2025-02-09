import logging
import uvicorn
from fastapi import FastAPI
from lockana.api.v1 import api_router
from lockana.database.database_setup import create_tables
from lockana import logging_config  


logger = logging.getLogger(__name__)

if __name__ == '__main__':
    create_tables()

    app = FastAPI()
    app.include_router(api_router)
    
    logger.info("Loading Lockana...")
    uvicorn.run(app)

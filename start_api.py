#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.main import app
import uvicorn
from api.config.settings import settings

if __name__ == "__main__":
    print("Starting Microshare ERP Integration v3.0...")
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, reload=settings.debug)

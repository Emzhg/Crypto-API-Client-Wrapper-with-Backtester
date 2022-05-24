from fastapi import FastAPI
import uvicorn
from routers import router

app = FastAPI(title="CoinGecko API Wrapper")
app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app)
    """
    open in browser for swagger: http://127.0.0.1:8000/docs#/
    """

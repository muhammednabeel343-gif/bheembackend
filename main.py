import asyncio
import sys
from app.main import app

if __name__ == "__main__":
    import uvicorn
    
    # Set event loop policy for Windows and Railway compatibility
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        try:
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        except RuntimeError:
            pass
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

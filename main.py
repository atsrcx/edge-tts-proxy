import asyncio
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import edge_tts

app = FastAPI(title="Edge TTS Fast Proxy")

async def tts_streaming_generator(text: str, voice: str):
    """
    Yeh function Microsoft Edge se audio chunks lata hai aur 
    bina save kiye turant Android app ko stream (pipe) kar deta hai.
    """
    try:
        communicate = edge_tts.Communicate(text, voice)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    except Exception as e:
        # Logging error if something goes wrong
        print(f"Error in streaming: {e}")

@app.get("/v1/tts")
async def text_to_speech(
    text: str = Query(..., description="Jo text bolna hai"),
    voice: str = Query("hi-IN-MadhurNeural", description="Voice name (e.g., hi-IN-MadhurNeural, hi-IN-SwaraNeural, en-US-AriaNeural)")
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    # Chunked streaming response return karega (Zero buffering latency)
    return StreamingResponse(
        tts_streaming_generator(text, voice), 
        media_type="audio/mpeg"
    )

@app.get("/")
def home():
    return {"status": "Edge TTS Proxy is Running Successfully!"}
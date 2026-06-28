import asyncio
import httpx
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI(title="Ultimate Patched TTS Proxy")

# Stable Open-Source Production Deployment Mirror for Edge TTS
TTS_STABLE_API = "https://tts.cyg.sh/api/tts"

@app.get("/v1/tts")
async def text_to_speech(
    text: str = Query(..., description="Jo text bolna hai"),
    voice: str = Query("hi-IN-SwaraNeural", description="Ladki ki Premium Natural Voice")
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Swara aur Madhur ko format handle karna
    if "swara" in voice.lower():
        voice = "hi-IN-SwaraNeural"
    elif "madhur" in voice.lower():
        voice = "hi-IN-MadhurNeural"

    # Direct query parameters bypass standard format
    params = {
        "text": text,
        "voice": voice,
        "rate": "0%",
        "pitch": "0%"
    }

    async def stream_audio():
        # Stream response chunks instantly for zero-latency playback
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream("GET", TTS_STABLE_API, params=params) as r:
                    if r.status_code != 200:
                        yield b""
                        return
                    async for chunk in r.aiter_bytes():
                        yield chunk
            except Exception as e:
                print(f"Streaming error: {e}")
                yield b""

    return StreamingResponse(stream_audio(), media_type="audio/mpeg")

@app.get("/")
def home():
    return {"status": "Proxy Server is Active and Running Fine!"}

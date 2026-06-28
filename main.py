import asyncio
import httpx
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI(title="Ultimate Free Cloud TTS Proxy")

# Deep Internet Research Hidden Endpoint (Gradio Free Cloud Mirror)
# Yeh serverless mirror Microsoft Edge ki original voices stream karta hai bina block hue
TTS_MIRROR_URL = "https://yy0931-edge-tts.hf.space/run/predict"

@app.get("/v1/tts")
async def text_to_speech(
    text: str = Query(..., description="Jo text bolna hai"),
    voice: str = Query("hi-IN-SwaraNeural", description="Voice name")
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Gradio format me payload bhej rahe hain real-time audio ke liye
    payload = {
        "data": [
            text,
            voice,
            "+0Hz",  # Pitch standard
            "+0%"   # Speed standard
        ]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(TTS_MIRROR_URL, json=payload)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Cloud Mirror Error")
            
            data = response.json()
            # Gradio response se audio file ka temporary cloud link nikalna
            audio_url = data["data"][1]["name"]
            
            # Us audio file ko direct client (Android) ke liye stream (pipe) karna
            async def stream_audio():
                async with client.stream("GET", audio_url) as r:
                    async for chunk in r.aiter_bytes():
                        yield chunk

            return StreamingResponse(stream_audio(), media_type="audio/mpeg")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Proxy Error: {str(e)}")

@app.get("/")
def home():
    return {"status": "Ultimate Free Cloud TTS Proxy is Live!"}

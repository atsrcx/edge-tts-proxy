import asyncio
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import edge_tts

app = FastAPI(title="Edge TTS Fast Proxy")

async def tts_streaming_generator(text: str, voice: str):
    try:
        # Microsoft ko bypass karne ke liye exact Edge Browser ka setup aur headers
        communicate = edge_tts.Communicate(text, voice)
        
        # Isme rate limits aur robotic fallback se bachne ke liye streaming options hain
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
                
    except Exception as e:
        print(f"Error in streaming: {e}")

@app.get("/v1/tts")
async def text_to_speech(
    text: str = Query(..., description="Jo text bolna hai"),
    voice: str = Query("hi-IN-SwaraNeural", description="Default Ladki ki Natural Voice")
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    # Agar tum galti se sirf 'Swara' ya 'Madhur' pass karo toh ye auto-correct kar dega
    if "swara" in voice.lower():
        voice = "hi-IN-SwaraNeural"
    elif "madhur" in voice.lower():
        voice = "hi-IN-MadhurNeural"
        
    return StreamingResponse(
        tts_streaming_generator(text, voice), 
        media_type="audio/mpeg"
    )

@app.get("/")
def home():
    return {"status": "Edge TTS Proxy is Running Successfully!"}

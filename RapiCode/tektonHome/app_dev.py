from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import scripts.ESP32Control as strip
import shlex

app = FastAPI()

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.0.234:3001"],  # Adjust this to your Next.js app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run-script/")
async def run_script(button: str = Form(...), RGBvalues: str = Form(None)):
    args = []
    if button == "turnOn":
        strip.turn_led_on()
        message = 'LED Turn on executed successfully!'
    elif button == "turnOff":
        strip.turn_led_off()
        message = 'LED Turn off executed successfully!'
    elif button == "changeColor" and RGBvalues:
        RGBval_list = shlex.split(RGBvalues)
        strip.change_color(RGBval_list[0], RGBval_list[1], RGBval_list[2] )
        message = 'Color Changed to: ' + RGBvalues + ' in RGB '

    return JSONResponse(content={"message": message})

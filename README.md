# tektonHome

> A self-hosted home automation dashboard that turns Python functions on any Raspberry Pi into live UI controls — automatically.

<!-- Replace with your actual demo GIF once exported -->
<!-- Demo: two boards loaded, then registering a new board -->
![tektonHome Demo](resources/demo2.gif)

---

## What is this?

tektonHome is a lightweight system for controlling multiple Raspberry Pis (or any networked computer) from a single web dashboard. The idea is simple: you write Python functions on each device, annotate them with a type (`Button` or `Input`), and the system automatically discovers them and renders the right UI component in the browser — no manual frontend changes needed.

Each device is called a **Board**. The central Next.js dashboard fetches all registered boards and displays a card per board, with buttons and input fields that map 1:1 to the Python functions running on that device.

The included example boards control an **ESP32 LED strip** and a **Raspberry Pi camera** with real-time ambient lighting using OpenCV — but the system is generic enough to wrap anything.

---

## How it works

```
┌──────────────────────────────────────────────────────────────────┐
│                         Your Home Network                        │
│                                                                  │
│   ┌─────────────────────┐         ┌──────────────────────────┐   │
│   │   Central Server    │◄────────│   Raspberry Pi (Board)   │   │
│   │                     │  REST   │                          │   │
│   │  ┌───────────────┐  │  API    │  ┌────────────────────┐  │   │
│   │  │  Next.js UI   │  │         │  │   FastAPI (app.py) │  │   │
│   │  │  :3000        │  │         │  │   :8000            │  │   │
│   │  └───────┬───────┘  │         │  └────────┬───────────┘  │   │
│   │          │          │         │           │              │   │
│   │  ┌───────▼───────┐  │         │  ┌────────▼───────────┐  │   │
│   │  │  FastAPI API  │  │         │  │  scripts/          │  │   │
│   │  │  :8000        │  │         │  │  ├── ESP32Control  │  │   │
│   │  │  /Boards/     │  │         │  │  ├── camSetup.py   │  │   │
│   │  └───────────────┘  │         │  │  └── OPCV.py       │  │   │
│   └─────────────────────┘         └──────────────────────────┘   │
│                                                                  │
│              ┌──────────────────────────────┐                    │
│              │   Another Pi (Board 2)       │                    │
│              │   FastAPI :8000              │                    │
│              │   scripts/ (other .py files) │                    │
│              └──────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────────┘
```

**The flow:**

1. Each Pi runs `app.py` (FastAPI). On startup it scans its `scripts/` folder using `load_scripts.py`.
2. `load_scripts.py` introspects every Python file: it finds all functions and reads their type annotations (`Button` or `Input`).
3. The Pi registers itself with the central server by POSTing its board name and function map to `/Boards/`.
4. The Next.js dashboard fetches all boards from the central server and renders a card per board. Each `Button`-annotated function becomes a button; each `Input`-annotated function becomes a text input + submit button.
5. When you click a button in the UI, the Next.js frontend calls back to the Pi's own FastAPI (`/run-function/` or `/run-function-params/`) and the Python function executes on the device.

---

## Repository Structure

```
tektonHome/
├── ESP32_LEDCode/              # Arduino/ESP32 firmware for the LED strip
│
└── RapiCode/
    ├── tektonHomeServer/       # Central server
    │   ├── tektonhome/         # Next.js frontend (the dashboard)
    │   │   ├── pages/
    │   │   ├── components/
    │   │   └── package.json
    │   └── main.py             # FastAPI backend — stores board registrations
    │
    └── tektonHomeClient/       # Runs on each Raspberry Pi
        ├── app.py              # FastAPI app — exposes functions over HTTP
        ├── load_scripts.py     # Script introspection & board registration
        ├── func_types.py       # Button / Input type definitions
        ├── requirements.txt
        └── scripts/            # ← Your Python scripts go here
            ├── ESP32Control.py # Example: LED strip control via ESP32
            ├── OPCV.py         # Example: OpenCV ambient lighting
            └── camSetup.py     # Example: Picamera2 MJPEG stream
```

---

## The Type Annotation System

The entire auto-discovery mechanism is built on Python type annotations. Two types are defined in `func_types.py`:

```python
class Button:
    """Renders a button in the UI. Function is called with no user input."""
    pass

class Input:
    """Renders a text input + submit in the UI. User input is passed as a string."""
    pass
```

To expose a function, simply annotate its first parameter with one of these types:

```python
from func_types import Button, Input

# → Renders as a button labelled "turn_led_on"
def turn_led_on(type: Button = None):
    requests.get('http://192.168.0.163/on')
    return 'LED turned on!'

# → Renders as a text input labelled "change_color"
def change_color(type: Input = None, param_vals: str = ""):
    r, g, b = param_vals.split()
    requests.get('http://192.168.0.163/change-color', params={'r': r, 'g': g, 'b': b})
    return f'Color changed to {param_vals}'
```

Functions **without** a `Button` or `Input` annotation are ignored by the introspection system — they're treated as internal helpers.

---

## Setup

### Prerequisites

- Python 3.10+ on all devices
- Node.js 18+ on the central server machine
- All devices on the same local network

---

### 1. Central Server

The central server stores board registrations and serves the Next.js dashboard.

```bash
cd RapiCode/tektonHomeServer

# Start the FastAPI backend (stores board info)
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# In a separate terminal — start the Next.js dashboard
cd tektonhome
npm install
npm run dev        # development
# or
npm run build && npm start   # production (port 3000)
```

Note the machine's local IP (e.g. `192.168.0.234`). You'll need it for client configuration.

---

### 2. Client (each Raspberry Pi)

```bash
cd RapiCode/tektonHomeClient

pip install -r requirements.txt
```

Edit the two configuration values at the top of `load_scripts.py`:

```python
# URL of the central server's FastAPI backend
tekton_url = "http://192.168.0.234:8000/Boards/"
```

And in `app.py`, set your board's identity:

```python
glob_board_id   = 1          # unique integer per board
glob_board_name = "MyPi_1"   # display name in the dashboard
```

Then start the client API:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

### 3. Register the Board

Once the client is running, open its local dashboard at `http://<pi-ip>:8000/` and click **Create Board**. This POSTs the board's identity and its full function map to the central server. The board card will immediately appear in the Next.js dashboard at `http://<server-ip>:3000`.

![tektonHome Demo](resources/demo1.gif)

You can also register/update via the API directly:

```bash
# Register (or re-register after adding new scripts)
curl -X POST http://<pi-ip>:8000/run-script/ \
  -F "button=createBoard"

# Push updated function list after adding/editing scripts
curl -X POST http://<pi-ip>:8000/run-script/ \
  -F "button=updateBoard"

# Remove the board from the dashboard
curl -X POST http://<pi-ip>:8000/run-script/ \
  -F "button=deleteBoard"
```

---

## Adding Your Own Scripts

1. Create a new `.py` file inside `RapiCode/tektonHomeClient/scripts/`.
2. Import the types and annotate your functions:

```python
# scripts/my_device.py
import requests
from func_types import Button, Input

DEVICE_IP = "http://192.168.0.XXX/"

def reboot_device(type: Button = None):
    requests.post(DEVICE_IP + "reboot")
    return "Reboot command sent"

def set_brightness(type: Input = None, param_vals: str = ""):
    level = int(param_vals.strip())
    requests.get(DEVICE_IP + "brightness", params={"level": level})
    return f"Brightness set to {level}"

# This function has no type annotation → NOT shown in the UI
def _internal_helper():
    pass
```

3. Click **Update Board** in the local dashboard (or hit the `updateBoard` endpoint). The new functions appear in the Next.js card automatically — no frontend changes needed.

---

## Included Example Scripts

### `scripts/ESP32Control.py` — LED Strip

Controls an ESP32 connected to an RGB LED strip over WiFi. Demonstrates both `Button` and `Input` function types.

| Function | Type | Description |
|---|---|---|
| `turn_led_on` | Button | Sends GET `/on` to the ESP32 |
| `turn_led_off` | Button | Sends GET `/off` to the ESP32 |
| `change_color` | Input | Accepts `"R G B"` string, applies color |

The ESP32 firmware lives in `ESP32_LEDCode/`. Flash it to your board and update `esp_ip` in the script to match your ESP32's IP.

---

### `scripts/OPCV.py` — Ambient Lighting (Camera → LED)

Implements an Ambilight-style effect using the Pi Camera and OpenCV. Splits the camera frame into 6 tiles (3 top, 3 bottom), computes the dominant color of each tile via k-means clustering, then streams those RGB values live to the ESP32 LED strip.

| Function | Type | Description |
|---|---|---|
| `initCam` | Button | Initialises Picamera2 |
| `sendData` | Button | Starts the ambient lighting loop in a background thread |
| `stop_sendData` | Button | Stops the loop |

The camera streams at ~60fps. The tile layout (`Tile_dict`) covers a 640×480 frame and can be adjusted in the script to match your setup.

---

### `scripts/camSetup.py` — MJPEG Camera Stream

Starts an MJPEG HTTP server on port **7123** so you can preview what the Pi Camera sees in any browser before or during ambient mode.

| Function | Type | Description |
|---|---|---|
| `startSetup` | Button | Launches the MJPEG stream server |

Navigate to `http://<pi-ip>:7123` to see the live preview. A **Stop Server** button in the page shuts it down cleanly.

> **Note:** `initCam` in `OPCV.py` must be called first. The camera instance is shared between `OPCV.py` and `camSetup.py` — they both reference the same global `picam2` object.

---

## API Reference (Client — `app.py`)

Each Pi exposes the following endpoints on port `8000`:

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Simple HTML control panel (create/update/delete board) |
| `POST` | `/run-function/` | Call a `Button` function by module + function name |
| `POST` | `/run-function-params/` | Call an `Input` function, passing user string |
| `POST` | `/run-script/` | Board management (createBoard / updateBoard / deleteBoard) |
| `GET` | `/deleteBoard/` | Delete this board from the central server |

### `/run-function/`

```bash
curl -X POST http://<pi-ip>:8000/run-function/ \
  -F "moduleName=ESP32Control" \
  -F "functionName=turn_led_on"
# → {"message": "Turn on executed successfully!"}
```

### `/run-function-params/`

```bash
curl -X POST http://<pi-ip>:8000/run-function-params/ \
  -F "moduleName=ESP32Control" \
  -F "functionName=change_color" \
  -F "functionParams=255 80 10"
# → {"message": "Changed Color Succesfully to: 255 80 10"}
```

---

## API Reference (Central Server — `main.py`)

| Method | Path | Description |
|---|---|---|
| `POST` | `/Boards/` | Register a new board |
| `GET` | `/Boards/{id}/description` | Get a board's function map |
| `PUT` | `/Boards/{id}` | Update board name + function map |
| `DELETE` | `/Boards/{id}` | Remove a board |

---

## Hardware Used in the Examples

| Component | Role |
|---|---|
| Raspberry Pi (any model with camera support) | Runs `tektonHomeClient` |
| Raspberry Pi Camera Module | Picamera2 / MJPEG stream / ambient capture |
| ESP32 (any Wi-Fi capable variant) | LED strip controller, flashed with `ESP32_LEDCode/` |
| RGB LED Strip (WS2812B or similar) | Ambient lighting output |

---

## Troubleshooting

**Board doesn't appear in the dashboard after Create Board**
- Check that the central server's FastAPI is running (`http://<server-ip>:8000/Boards/` should return JSON)
- Verify `tekton_url` in `load_scripts.py` points to the correct IP
- Check CORS — `app.py` allows only `http://192.168.0.234:3000` by default; update `allow_origins` if your server IP differs

**Functions don't show up after adding a new script**
- Make sure the function has a `Button` or `Input` annotation on its first parameter
- Hit **Update Board** to re-scan and re-register
- Check for import errors in your script — a broken import silently skips the whole file

**Camera already initiated error**
- `picam2` is a process-level singleton; call `initCam` only once per session. Restart `app.py` to fully reset camera state.

---

## License

MIT
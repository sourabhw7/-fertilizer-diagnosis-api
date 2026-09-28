import hashlib
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Fertilizer Advisory API (TEMP MOCK)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLASSES = ['ALL Present', 'ALLAB', 'KAB', 'NAB', 'PAB', 'ZNAB']

ADVISORY = {
    'ALL Present': {
        'condition': 'Healthy Crop (All Nutrients Present)',
        'fertilizer': 'No Extra Fertilizer Needed',
        'symptoms': 'Leaves exhibit healthy green color and balanced cellular structure.',
        'action': 'Maintain standard irrigation and micro-nutrient maintenance schedule.',
        'stock': 100, 'price': 'N/A'
    },
    'NAB': {
        'condition': 'Nitrogen Deficiency',
        'fertilizer': 'Urea / Ammonium Sulphate',
        'symptoms': 'General pale green to yellow leaves starting from older bottom leaves.',
        'action': 'Apply top dressing of Urea in split applications.',
        'stock': 45, 'price': '₹266.50 / 45kg'
    },
    'PAB': {
        'condition': 'Phosphorus Deficiency',
        'fertilizer': 'DAP (Diammonium Phosphate) / SSP',
        'symptoms': 'Purplish tint along leaf edges and stunted root development.',
        'action': 'Apply DAP as a basal placement directly into root zone.',
        'stock': 25, 'price': '₹1,350.00 / 50kg'
    },
    'KAB': {
        'condition': 'Potassium Deficiency',
        'fertilizer': 'MOP (Muriate of Potash)',
        'symptoms': 'Marginal leaf scorch, browning edges, and weak stem strength.',
        'action': 'Apply MOP to restore water regulation and plant immunity.',
        'stock': 12, 'price': '₹1,700.00 / 50kg'
    },
    'ZNAB': {
        'condition': 'Zinc Deficiency',
        'fertilizer': 'Zinc Sulphate (ZnSO4)',
        'symptoms': 'Broad white/bleached bands on leaf tissues beside the midrib.',
        'action': 'Foliar spray with 0.5% Zinc Sulphate solution mixed with slaked lime.',
        'stock': 30, 'price': '₹550.00 / 25kg'
    },
    'ALLAB': {
        'condition': 'Severe Multiple Deficiencies',
        'fertilizer': 'NPK Complex (19:19:19) + Micronutrient Mix',
        'symptoms': 'Multi-pattern chlorosis, severe necrosis, and severely stunted growth.',
        'action': 'Apply balanced water-soluble NPK foliar spray.',
        'stock': 20, 'price': '₹1,200.00 / 25kg'
    }
}

@app.get("/")
def home():
    return {"status": "ok", "mode": "mock"}

@app.post("/api/diagnose")
async def diagnose(file: UploadFile = File(...)):
    contents = await file.read()
    # Same image always gives the same fake result
    h = int(hashlib.md5(contents).hexdigest(), 16)
    label = CLASSES[h % len(CLASSES)]
    confidence = round(80 + (h % 190) / 10, 1)  # 80.0 to 98.9

    info = ADVISORY[label]
    return {
        "detected_condition": info["condition"],
        "confidence": confidence,
        "recommended_fertilizer": info["fertilizer"],
        "symptoms": info["symptoms"],
        "action": info["action"],
        "stock": {
            "in_stock": info["stock"] > 0,
            "quantity_bags": info["stock"],
            "unit_price": info["price"]
        },
        "mock": True
    }

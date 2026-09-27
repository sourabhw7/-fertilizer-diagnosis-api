import cv2
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Fertilizer Advisory API")

# Enable Cross-Origin Requests for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model
MODEL = tf.keras.models.load_model("fertilizer_model.keras")

CLASSES = ['ALL Present', 'ALLAB', 'KAB', 'NAB', 'PAB', 'ZNAB']

ADVISORY = {
    'ALL Present': {
        'condition': 'Healthy Crop (All Nutrients Present)',
        'fertilizer': 'No Extra Fertilizer Needed',
        'symptoms': 'Leaves exhibit healthy green color and balanced cellular structure.',
        'action': 'Maintain standard irrigation and micro-nutrient maintenance schedule.',
        'stock': 100,
        'price': 'N/A'
    },
    'NAB': {
        'condition': 'Nitrogen Deficiency',
        'fertilizer': 'Urea / Ammonium Sulphate',
        'symptoms': 'General pale green to yellow leaves starting from older bottom leaves.',
        'action': 'Apply top dressing of Urea in split applications.',
        'stock': 45,
        'price': '₹266.50 / 45kg'
    },
    'PAB': {
        'condition': 'Phosphorus Deficiency',
        'fertilizer': 'DAP (Diammonium Phosphate) / SSP',
        'symptoms': 'Purplish tint along leaf edges and stunted root development.',
        'action': 'Apply DAP as a basal placement directly into root zone.',
        'stock': 25,
        'price': '₹1,350.00 / 50kg'
    },
    'KAB': {
        'condition': 'Potassium Deficiency',
        'fertilizer': 'MOP (Muriate of Potash)',
        'symptoms': 'Marginal leaf scorch, browning edges, and weak stem strength.',
        'action': 'Apply MOP to restore water regulation and plant immunity.',
        'stock': 12,
        'price': '₹1,700.00 / 50kg'
    },
    'ZNAB': {
        'condition': 'Zinc Deficiency',
        'fertilizer': 'Zinc Sulphate (ZnSO4)',
        'symptoms': 'Broad white/bleached bands on leaf tissues beside the midrib.',
        'action': 'Foliar spray with 0.5% Zinc Sulphate solution mixed with slaked lime.',
        'stock': 30,
        'price': '₹550.00 / 25kg'
    },
    'ALLAB': {
        'condition': 'Severe Multiple Deficiencies',
        'fertilizer': 'NPK Complex (19:19:19) + Micronutrient Mix',
        'symptoms': 'Multi-pattern chlorosis, severe necrosis, and severely stunted growth.',
        'action': 'Apply balanced water-soluble NPK foliar spray.',
        'stock': 20,
        'price': '₹1,200.00 / 25kg'
    }
}

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return np.expand_dims(img.astype(np.float32), axis=0)

@app.post("/api/diagnose")
async def diagnose(file: UploadFile = File(...)):
    contents = await file.read()
    tensor = preprocess_image(contents)
    
    preds = MODEL.predict(tensor)[0]
    best_idx = int(np.argmax(preds))
    label = CLASSES[best_idx]
    
    info = ADVISORY[label]
    return {
        "detected_condition": info["condition"],
        "confidence": round(float(preds[best_idx]) * 100, 1),
        "recommended_fertilizer": info["fertilizer"],
        "symptoms": info["symptoms"],
        "action": info["action"],
        "stock": {
            "in_stock": info["stock"] > 0,
            "quantity_bags": info["stock"],
            "unit_price": info["price"]
        }
    }

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

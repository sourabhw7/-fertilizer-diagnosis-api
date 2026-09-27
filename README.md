# Fertilizer Leaf Diagnosis API

FastAPI service that predicts nutrient deficiency from a leaf photo using a MobileNetV2-based Keras model.

## Endpoint
POST /api/diagnose - multipart/form-data with a "file" field containing the image.

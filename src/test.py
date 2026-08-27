import io
import torch
import torch.nn.functional as F
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
from model import get_model
from dataset import get_transforms

app = FastAPI(title="CIFAR-10 Serving")
device = torch.device("cpu")
model = None
transform = get_transforms(train=False)

@app.on_event("startup")
def load_serving_model():
    global model
    checkpoint_path = "/app/checkpoints/classifier_v1.pt"
    model = get_model("resnet18", 10)
    try:
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        model.eval()
    except Exception as e:
        model = None

@app.get("/health")
def health_check():
    if model is None:
        raise HTTPException(status_code=503, detail="Model checkpoint not loaded")
    return {"status": "healthy"}

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model unavailable")
    img_bytes = await image.read()
    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    tensor_img = transform(pil_img).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(tensor_img)
        probs = F.softmax(logits, dim=1).squeeze().tolist()
    return {"probabilities": probs, "predicted_class": int(torch.argmax(logits, dim=1).item())}
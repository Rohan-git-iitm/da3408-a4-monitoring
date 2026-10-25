import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

MODEL_ID = "Salesforce/blip-image-captioning-base"
torch.set_num_threads(4)

processor = BlipProcessor.from_pretrained(MODEL_ID)
model = BlipForConditionalGeneration.from_pretrained(MODEL_ID).eval()


def caption(img: Image.Image) -> str:
    inputs = processor(img.convert("RGB"), return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=30)
    return processor.decode(out[0], skip_special_tokens=True)


if __name__ == "__main__":
    import sys, time
    t = time.time()
    print(caption(Image.open(sys.argv[1])), f"({time.time() - t:.2f}s)")
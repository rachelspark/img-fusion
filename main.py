import io
from fastapi import File, UploadFile, Response, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import modal

app = FastAPI()
stub = modal.Stub("img-fusion")


image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install(["git"])
    .pip_install(
        "opencv-python-headless",
        "git+https://github.com/ai-forever/Kandinsky-2.git",
        "git+https://github.com/openai/CLIP.git",
    )
)
stub.image = image

origins = [
    "http://localhost:3000",
    "http://localhost:*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@stub.cls(gpu=modal.gpu.A100())
class Kandinsky:
    def __enter__(self):
        from kandinsky2 import get_kandinsky2
        self.model = get_kandinsky2('cuda', task_type='text2img', model_version='2.1', use_flash_attention=False)

    @modal.method()
    def run_model(self, file1: UploadFile = File(...), file2: UploadFile = File(...)):
        """Runs Kandinsky 2 image fuse on two uploaded image files
        Returns another file
        """
        import base64
        from io import BytesIO
        from PIL import Image

        img1_content = file1.file.read()
        img2_content = file2.file.read()
        img1 = Image.open(io.BytesIO(img1_content))
        img2 = Image.open(io.BytesIO(img2_content))

        image_mixed = self.model.mix_images(
        [img1, img2], [0.5, 0.5], 
        num_steps=100, 
        batch_size=1, 
        guidance_scale=4, 
        h=500, 
        w=500, 
        sampler='p_sampler', 
        prior_cf_scale=4, 
        prior_steps="5",
        )[0]

        buf = BytesIO()
        image_mixed.save(buf, format="PNG")
        encoded = base64.b64encode(buf.getvalue())
        return encoded

@app.post("/generate-image")
def generate_image(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    try:
        k = Kandinsky()
        generated_image = k.run_model.call(file1, file2)
        return {"image": generated_image}
    except Exception as e:
        print(e)
        raise e
    finally:
        file1.file.close()
        file2.file.close()

@stub.function()
@modal.asgi_app()
def fastapi_app():
    return app

@stub.local_entrypoint()
def main():
    k = Kandinsky()
    png_data = k.run_model.call()
    with open("output.png", "wb") as f:
        f.write(png_data)
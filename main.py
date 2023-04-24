import io
from fastapi import File, UploadFile
from modal import method, Image, Stub, asgi_app

stub = Stub("img-fusion")

def download_model():
    from kandinsky2 import get_kandinsky2
    get_kandinsky2('cuda', task_type='text2img', model_version='2.1', use_flash_attention=False)

image = (
    Image.debian_slim()
    .apt_install("git")
    .pip_install(
        "opencv-python-headless",
        "git+https://github.com/ai-forever/Kandinsky-2.git",
        "git+https://github.com/openai/CLIP.git",
    )
    .run_function(download_model, gpu="any")
)
stub.image = image

@stub.cls(gpu="A10G")
class Kandinsky:
    def __enter__(self):
        from kandinsky2 import get_kandinsky2
        self.model = get_kandinsky2('cuda', task_type='text2img', model_version='2.1', use_flash_attention=False)

    @method()
    def run_model(self, file1: UploadFile = File(...), file2: UploadFile = File(...)):
        """Runs Kandinsky 2 image fuse on two uploaded image files
        Returns output image as base-64 encoded value
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

@stub.function()
@asgi_app()
def fastapi_app():
    from fastapi import FastAPI, Response

    app = FastAPI()
    k = Kandinsky()

    @app.post("/generate-image")
    def generate_image(response: Response, file1: UploadFile = File(...), file2: UploadFile = File(...)):
        try:
            response.headers["Access-Control-Allow-Origin"] = "*"
            generated_image = k.run_model.call(file1, file2)
            return [{"image": generated_image}]
        except Exception as e:
            print(e)
            raise e
        finally:
            file1.file.close()
            file2.file.close()

    return app
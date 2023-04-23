import modal

stub = modal.Stub("image-fusion")

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

@stub.function(gpu=modal.gpu.A100())
def run_model():
    import sys
    from io import BytesIO
    from PIL import Image
    from kandinsky2 import get_kandinsky2

    model = get_kandinsky2('cuda', task_type='text2img', model_version='2.1', use_flash_attention=False)

    img1 = Image.open(sys.path.append("data/arthur.png"))
    img2 = Image.open(sys.path.append("data/bluesclues.png"))

    image_mixed = model.mix_images(
    [img1, img2], [0.5, 0.5], 
    num_steps=100, 
    batch_size=1, 
    guidance_scale=4, 
    h=768, 
    w=768, 
    sampler='p_sampler', 
    prior_cf_scale=4, 
    prior_steps="5",
)[0]

    buf = BytesIO()
    image_mixed.save(buf, format="PNG")
    return buf.getvalue()

@stub.local_entrypoint()
def main():
    png_data = run_model.call()
    with open("output.png", "wb") as f:
        f.write(png_data)
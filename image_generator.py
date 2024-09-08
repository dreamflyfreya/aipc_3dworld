import torch
from diffusers import StableDiffusion3Pipeline
def generate_image(prompt: str):
    pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3-medium-diffusers", torch_dtype=torch.float16)
    pipe = pipe.to("cuda")

    image = pipe(
        prompt,
        negative_prompt="",
        num_inference_steps=28,
        guidance_scale=7.0,
    ).images[0]
    # Save the image
    image.save("generated_image.png")

    # Display the image (if you're running this in a Jupyter notebook or similar environment)
    image.show()
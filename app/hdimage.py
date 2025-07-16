import asyncio
import os
import io
import base64
from PIL import Image
from appPublic.hf import hf_socks5proxy
from appPublic.log import debug
from appPublic.worker import awaitify
from appPublic.folderUtils import _mkdir, temp_file
from appPublic.jsonConfig import getConfig
from ahserver.filestorage import FileStorage
from ahserver.webapp import webapp
from ahserver.serverenv import ServerEnv
from ahserver.filestorage import FileStorage

import torch
import transformers
from transformers import PreTrainedTokenizerFast, LlamaForCausalLM
from diffusers import HiDreamImagePipeline

hf_socks5proxy()

def pil_image_to_base64_str(img: Image.Image, format="PNG") -> str:
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    img_bytes = buffer.getvalue()
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    return base64_str

class HDImage:
	def __init__(self):
		config = getConfig()
		tokenizer_4 = PreTrainedTokenizerFast.from_pretrained(f"{config.llama_model_path}/Llama-3.1-8B-Instruct",
			device_map="balanced"
		)
		text_encoder_4 = LlamaForCausalLM.from_pretrained(
			f"{config.llama_model_path}/Llama-3.1-8B-Instruct",
			output_hidden_states=True,
			device_map="balanced",
			output_attentions=True,
			torch_dtype=torch.bfloat16,
		)

		pipe = HiDreamImagePipeline.from_pretrained(
			f"{config.hidream_model_path}/HiDream-I1-Full",  # "HiDream-ai/HiDream-I1-Dev" | "HiDream-ai/HiDream-I1-Fast"
			device_map="balanced",
			tokenizer_4=tokenizer_4,
			text_encoder_4=text_encoder_4,
			torch_dtype=torch.bfloat16,
		)

		# pipe = pipe.to('cuda')
		self.pipe = pipe
		self.fs = FileStorage()
		self.defaultv = {
			"width":1024,
			"height":1024,
			"guidance_scale":5.0,
			"num_inference_steps":50
		}
		self.lock = asyncio.Lock()

	
	def _generate(self, prompt, kw):
		image = self.pipe(
			prompt,
			generator=torch.Generator("cuda").manual_seed(0),
			**kw
		).images[0]
		return pil_image_to_base64_str(image)
		fn=self.fs._name2path('generated.png')
		pth = self.fs.webpath(fn)
		debug(f'{fn=}, {pth=}, {dir(image)},{type(image)}')
		_mkdir(os.path.dirname(fn))
		image.save(fn)
		return pth

	async def generate(self, prompt, width=None, height=None, 
						guidance_scale=None,
						num_inference_steps=None):
		kw = {
			"width" : self.defaultv['width'] if width is None else width,
			"height" : self.defaultv['height'] if height is None else height,
			"guidance_scale" : self.defaultv['guidance_scale'] if guidance_scale is None else guidance_scale,
			"num_inference_steps" : self.defaultv['num_inference_steps'] if num_inference_steps is None else num_inference_steps
		}
		async with self.lock:
			f = awaitify(self._generate)
			return await f(prompt, kw)

def init():
	hd_image = HDImage()
	g = ServerEnv()
	g.hd_image = hd_image

if __name__ == '__main__':
	webapp(init)


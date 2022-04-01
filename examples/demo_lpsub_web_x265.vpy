from typing import NamedTuple, List
import mvsfunc as mvf
import kagefunc as kgf
import havsfunc as haf
import vapoursynth as vs
import nnedi3_resample as nnrs
import fvsfunc as fvf
import vsTAAmbk as taa
import adptvgrnMod as adp
import atomchtools
core = vs.core
#OKE:MEMORY
core.max_cache_size = 50000

#OKE:INPUTFILE
a =r"F:\output\Downloads\Script\48.mp4"
src = core.lsmas.LWLibavSource(a)
src = core.std.Trim(src,last=1000)
src16 = mvf.Depth(src,16)
out16 = adp.adptvgrnMod(src16, strength=1, size=1.2, sharp=20, static=False, luma_scaling=5, grain_chroma=False)
res = mvf.Depth(out16,10)

#OKE:DEBUG
debug = 0
if debug:
	denoise = mvf.ToRGB(denoise,full=False,depth=8) 
	src = mvf.ToRGB(src,full=False,depth=8) 
	compare = core.std.Interleave([denoise,src])
	compare.set_output()
else:
	res.set_output(0)
	src16.set_output(1)
	
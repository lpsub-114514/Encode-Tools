import vapoursynth as vs
import sys
import havsfunc as haf
import mvsfunc as mvf
core = vs.core
core.num_threads = 12

#OKE:MEMORY
core.max_cache_size = 1000

#OKE:INPUTFILE
a = "src.mkv"
src8 = core.lsmas.LWLibavSource(a)
ass = input_ass #修改成字幕名称
res = core.vsfm.TextSubMod(src8,ass)
res = mvf.Depth(res)
res.set_output(0)

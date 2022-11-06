import vapoursynth as vs
import mvsfunc as mvf
import adptvgrnMod as adp

# 字幕组新番 web源 x264 通用脚本

core = vs.core
#OKE:MEMORY
core.max_cache_size = 8000
#OKE:INPUTFILE
source = r"E:\Animations\4个人各自有着自己的秘密\[SubsPlease] 4-nin wa Sorezore Uso wo Tsuku - 02 (1080p) [A5D310BC].mkv" # 片源
ass = source[:-4]+'.sc.ass'
src8 = core.lsmas.LWLibavSource(source)
src16 = mvf.Depth(src8, depth=16)
#Denoise
down444 = core.fmtc.resample(src16,960,540, sx=[-0.5,0,0], css="444", planes=[3,2,2], cplace="MPEG2")
nr16y = core.knlm.KNLMeansCL(src16, d=2, a=2, s=3,  h=0.8, wmode=2, device_type="GPU")
nr16uv = core.knlm.KNLMeansCL(down444, d=2, a=1, s=3,  h=0.4, wmode=2, device_type="GPU")
nr16 = core.std.ShufflePlanes([nr16y,nr16uv], [0,1,2], vs.YUV)
#Deband
nr8    = mvf.Depth(nr16, depth=8)
luma   = core.std.ShufflePlanes(nr8, 0, vs.YUV).resize.Bilinear(format=vs.YUV420P8)
nrmasks = core.tcanny.TCanny(nr8,sigma=0.8,op=2,gmmax=255,mode=1,planes=[0,1,2]).std.Expr(["x 7 < 0 65535 ?",""],vs.YUV420P16)
nrmaskb = core.tcanny.TCanny(nr8,sigma=1.3,t_h=6.5,op=2,planes=0)
nrmaskg = core.tcanny.TCanny(nr8,sigma=1.1,t_h=5.0,op=2,planes=0)
nrmask  = core.std.Expr([nrmaskg,nrmaskb,nrmasks, nr8],["a 20 < 65535 a 48 < x 256 * a 96 < y 256 * z ? ? ?",""],vs.YUV420P16)
nrmask  = core.std.Maximum(nrmask,0).std.Maximum(0).std.Minimum(0)
nrmask  = core.rgvs.RemoveGrain(nrmask,[20,0])
debd  = core.f3kdb.Deband(nr16,12,24,16,16,0,0,output_depth=16)
debd  = core.f3kdb.Deband(debd,20,56,32,32,0,0,output_depth=16)
debd  = mvf.LimitFilter(debd,nr16,thr=0.6,thrc=0.5,elast=2.0)
debd  = core.std.MaskedMerge(debd,nr16,nrmask,first_plane=True)
#Addnoise
adn = adp.adptvgrnMod(debd, strength=0.50, size=1.5, sharp=30, static=False, luma_scaling=12, grain_chroma=False)
out16 = core.std.MaskedMerge(adn,debd,nrmask,first_plane=True)
#OKE:DEBUG
debug = 0
if debug:
	src1 = mvf.ToRGB(src16,depth=8)
	src2 = mvf.ToRGB(out16,depth=8)
	compare = core.butteraugli.butteraugli(src1, src2)
	res = core.std.Interleave([src1,src2,compare])
else: 
	res = core.sub.TextFile(out16,ass)
	res = mvf.Depth(res,8)
res.set_output()
src8.set_output(1)

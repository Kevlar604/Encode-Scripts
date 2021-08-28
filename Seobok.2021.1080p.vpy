import vapoursynth as vs
import solar as sl
from adptvgrnMod import *
from vsutil import depth,get_y
import kagefunc as kgf
import awsmfunc as awf
import fvsfunc as fvf

core = vs.get_core()
core.num_threads = 4
core.max_cache_size = 2048

#Source
src=core.lsmas.LWLibavSource(r'D:\Test\Seobok.2021.Hybrid.1080p.BluRay.REMUX.AVC.TrueHD.5.1-TayTO.mkv')

#Cropping
src=core.std.Crop(src,top=138,bottom=138)

#Dither to 16 bit depth for filtering
src=depth(src,16)

#Fixing dirty lines
fix=awf.fb(src,right=2,planes=[1,2])
#t=core.lsmas.LWLibavSource(r'D:\Test\encoded5.mkv')
src=awf.fb(fix,left=1,top=2,planes=[0])

#Debanding/deblocking
luma=get_y(src)
mask=core.std.Convolution(luma,matrix=[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 24, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
grain=adptvgrnMod(src,strength=2,size=0.5)
src=core.std.MaskedMerge(grain,src,mask)
mask2=kgf.retinex_edgemask(luma).std.Binarize(55000)
deband=core.neo_f3kdb.Deband(src,range=30,y=250,cb=250,cr=250,grainy=50,grainc=50,blur_first=True,dynamic_grain=True,output_depth=16,keep_tv_range=True)
deband=adptvgrnMod(deband,strength=1.2,cstrength=1.2,sharp=70,size=1.15,static=False,luma_scaling=6,grain_chroma=True,grainer=None,fade_edges=True,tv_range=True)
deband=core.std.MaskedMerge(deband,src,mask2)
src=src[0:384]+deband[384:945]+src[945:]

#Dithering down to 8 bit depth
src=depth(src,8,dither_type='error_diffusion')

#For test encodes
#src=awf.SelectRangeEvery(src, every=3000, length=50, offset=1000)

src.set_output()

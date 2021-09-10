import vapoursynth as vs
from adptvgrnMod import adptvgrnMod
from vsutil import depth
import fvsfunc as fvf
import kagefunc as kgf
core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

#Importing source
src=core.lsmas.LWLibavSource("D:\Test\cat.hevc")

#Cropping black bars
src=core.std.Crop(src,top=264,bottom=264)

#Finding new height
nh=round(1920 /src.width / 2 * src.height) * 2

#Resizing
src=core.resize.Spline36(src,1920,nh,dither_type="error_diffusion")

#Dithering to 16 bit depth for filtering
src=depth(src,16)

#Debanding
db=core.f3kdb.Deband(src, range=15, y=58, cb=40, cr=40, grainy=0, grainc=0, output_depth=16)
mask=kgf.retinex_edgemask(src).std.Binarize(50000).std.Inflate().std.Inflate()
db=core.std.MaskedMerge(db,src,mask)
#Adding grain
db=adptvgrnMod(db,size=1.1,strength=0.8,sharp=60,cstrength=.6,luma_scaling=95,seed=3)

#Dithering down to native 10 bit depth
src,db=[depth(s,10,dither_type="error_diffusion") for s in (src,db)]

#Replacing source frames with debanded frames for frames 380:1788
src=fvf.rfs(src,db,"[380 1788]")

#Final output
src.set_output()

import vapoursynth as vs
import awsmfunc as awf
from vsutil import depth,get_y
from muvsfunc import SSIM_downsample
import fvsfunc as fvf
core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

src=core.lsmas.LWLibavSource(r'D:\Test\BLONDE VENUS\BDMV\STREAM\00003.m2ts')
src=core.std.CropRel(src, left=220, right=220)


nw=round(720/src.height / 2 * src.width) * 2

src=SSIM_downsample(src,w=nw,h=720,kernel='Spline36',use_fmtc=False,sigmoid=True)

src=depth(src,8,dither_type="error_diffusion")

#Fixing dirty lines after resizing since it involved adding black borders hence doing this before resizing and adding black borders was making dirty line reappear on the universal logo scenes
u=depth(src,16)
u=core.std.Crop(u,left=20,right=20)
u=awf.fb(u,left=2,right=2)
u=core.std.AddBorders(u,left=20,right=20)
u=depth(u,8,dither_type="error_diffusion")
src=fvf.rfs(src,u,"[0 578]")

src.set_output()



import vapoursynth as vs
import lostfunc as lot
import fvsfunc as fvf
import mvsfunc as mvf
import adptvgrnMod as adp
import awsmfunc as awf
import kagefunc as kgf
from pathlib import Path
from vsutil import get_y,depth
core = vs.get_core()

path=Path('E:\\Michael.1924.1080p.GBR.Blu-ray.AVC.LPCM.2.0\\00004 - 2 - h264, 1080p24.h264')
src=core.lsmas.LWLibavSource(path)
src=video=core.std.Crop(clip=src, left=248, right=248, top=0, bottom=0)
nw=round(720 / src.height / 2 * src.width) * 2
src=core.resize.Spline36(src,nw,720,dither_type='error_diffusion')
video=src
src=depth(src,16)
#Fixing dirty lines
src=core.cf.ContinuityFixer(src,left=[4,4,4],right=[4,4,4],top=[4,4,4],bottom=[4,4,4])

#Denoising removing random white and black dots ,moderate fixing of randi=om white lines
lmask=kgf.retinex_edgemask(get_y(src)).std.Binarize(5140).std.Minimum(coordinates=[1, 0, 1, 0, 0, 1, 0, 1])
ds=lot.DeSpot(src)
ds=core.std.MaskedMerge(src,ds,lmask)
noise=core.std.MakeDiff(src,ds)
src=core.std.MakeDiff(src,noise)

#Deblocking and debanding
mask=kgf.retinex_edgemask(get_y(src))
deband=core.neo_f3kdb.Deband(src,y=128,cb=128,cr=120,grainy=100,grainc=100,dynamic_grain=True)
deband=adp.adptvgrnMod(deband, strength=0.8,size=2,static=False,luma_scaling=6)
src=core.std.MaskedMerge(deband,src,mask)

#Adding some grain
src=core.grain.Add(src,var=10)
src=depth(src,8,dither_type='error_diffusion')
src.set_output()

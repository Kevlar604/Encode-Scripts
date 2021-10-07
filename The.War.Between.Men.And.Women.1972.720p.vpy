import vapoursynth as vs
import awsmfunc as awf
from adptvgrnMod import *
import fvsfunc as fvf
import lvsfunc as lvf
from vsutil import depth

core = vs.get_core()

src=core.lsmas.LWLibavSource(r'D:\Test\The War Between Men and Women\video.h264')

#Resizing 
src=core.resize.Spline36(src,1280,720,dither_type="error_diffusion")

src=depth(src,16)
#Generating mask for the purpose of debanding
mask=lvf.mask.detail_mask(src,sigma=2,brz_a=0.0250, brz_b=0.250).std.Binarize(20000)

#Debanding and adding some static grain
db=core.neo_f3kdb.Deband(src,range=25,y=200,cb=128,cr=128,grainy=50,grainc=50,dynamic_grain=False,keep_tv_range=True,output_depth=16)
db=core.std.MaskedMerge(db,src,mask)

#Adding some dynamic grains to the debanded scenes adaptively based on scene changes
db=adptvgrnMod(db, strength=1.5, cstrength=1.5, size=1.25, sharp=50,grain_chroma=True,static=False,luma_scaling=100,seed=3)
src=lvf.rfs(src,db,[(288,605)])

src=depth(src,8,dither_type='error_diffusion')

src.set_output()

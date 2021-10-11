import vapoursynth as vs
from vsutil import depth
import awsmfunc as awf
import lvsfunc as lvf
from adptvgrnMod import *
core = vs.get_core()

src=core.lsmas.LWLibavSource(r'D:\Test\The.Man.from.Colorado.1948.1080p.BluRay.REMUX.AVC.FLAC.2.0-EPSiLON.mkv')
src=core.std.Crop(src,left=240,right=240)
vid=core.resize.Spline36(src,960,720,dither_type='error_diffusion')
src=depth(src,16)
w=round(720 / src.height / 2 * src.width) * 2
src=awf.bbmod(src,top=3,bottom=3,blur=15,thresh=2000)
src=core.resize.Spline36(src,w,720,dither_type='error_diffusion')
mask=lvf.mask.detail_mask(src,sigma=1,brz_a=0.0250, brz_b=0.0250)
db=core.neo_f3kdb.Deband(src,range=25,y=64,cb=48,cr=48,grainy=0,grainc=0,keep_tv_range=True,output_depth=16)
db=core.std.MaskedMerge(db,src,mask)
db=adptvgrnMod(db,strength=2,cstrength=2,size=1,sharp=80,grain_chroma=True,static=False,luma_scaling=10,seed=3)

src=lvf.rfs(src,db,[(64,501),(140959,141164)])
src=depth(src,8,dither_type='error_diffusion')
src.set_output()

import vapoursynth as vs
import rekt
import awsmfunc as awf
import fvsfunc as fvf
import muvsfunc as muv
import mvsfunc as mvf
import kagefunc as kgf
import adptvgrnMod
import functools
import vsutil
 
core = vs.get_core()
video = core.lsmas.LWLibavSource(r'H:\Caramel.2007.1080p.BluRay.REMUX.AVC.DD.5.1-VaMPiRO.mkv')
video1 = core.std.CropRel(video, left=0, top=20, right=0, bottom=22)
video1 = awf.fb(video1,bottom=1 )
bb = awf.bbmod(video1,left=6, top=6 ,right=6, bottom=8, thresh=90, blur=60)
video2=fvf.AutoDeblock(bb.deblock.Deblock(quant=28, aoffset=0, boffset=0))
video2 = vsutil.depth(video2, 16)
mask = awf.bandmask(video2 , thr=250)
deband = core.neo_f3kdb.Deband(video2, y=45, cb=45, cr=45, grainy=20, grainc=56, dynamic_grain=True, range=30, output_depth=16)
deband = adptvgrnMod.adptvgrnMod(deband, strength=1, size=1.25, sharp=55, static=False, luma_scaling=25,grain_chroma=True, grainer=None, show_mask=False)
src = core.std.MaskedMerge(video2, deband, mask)
src = vsutil.depth(src, 8, dither_type='error_diffusion')
src.set_output()



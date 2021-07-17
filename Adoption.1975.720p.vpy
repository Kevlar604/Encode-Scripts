import vapoursynth as vs
import awsmfunc as awf
import btpfunc
from vsutil import depth
core = vs.get_core()

src=core.ffms2.Source(r'D:\Test\Adoption.1975.1080p.BluRay.REMUX.AVC.FLAC.1.0-MM.mkv')
src=core.std.CropRel(src, left=0, top=14, right=0, bottom=14)
src=depth(src,16)
h=round(1280 / src.width / 2 * src.height) * 2
src=core.resize.Spline36(src,1280,h,dither_type='error_diffusion')
src=core.fb.FillBorders(src,left=0,right=0,top=0,bottom=1,mode="fillmargins")
src=depth(src,8,dither_type='ordered')
src.set_output()

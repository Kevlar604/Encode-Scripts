import vapoursynth as vs
import awsmfunc as awf
from vsutil import depth
core = vs.get_core()

src=core.lsmas.LWLibavSource(r'D:\Test\Breathless.1960.FRENCH.2160p.UHD.BluRay.REMUX.DV.HEVC.FLAC.2.0-WhiteRose_track1_[eng].hevc')
src=core.std.Crop(src,left=440,right=440)
src=depth(src,16)
nw=round(1080/src.height / 2 * src.width) * 2
src=core.resize.Spline36(src,nw,1080)
src=depth(src,10,dither_type='error_diffusion')
#src=awf.SelectRangeEvery(clip=src, every=3000, length=50, offset=10000)
src.set_output()

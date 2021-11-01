import vapoursynth as vs
from vsutil import depth
import awsmfunc as awf
core = vs.get_core()

src=core.lsmas.LWLibavSource(r'D:\Test\High.Sierra.1941.1080p.BluRay.REMUX.AVC.FLAC.1.0-EPSiLON.mkv')
src=depth(src,16)
src=core.std.Crop(src,left=220,right=220)
src=depth(src,8,dither_type='error_diffusion')
src.set_output()

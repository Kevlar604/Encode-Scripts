import vapoursynth as vs
from vapoursynth import core
from vsutil import depth
import btpfunc as btp


src=core.lsmas.LWLibavSource(r'D:\Test\Mad.Max.1979.UHD.BluRay.2160p.DTS-HD.MA.5.1.DV.HEVC.REMUX-FraMeSToR_track1_[und].hevc')
src=depth(src,16)
src=core.std.Crop(src,top=264,bottom=264)
nh=round(1920 /src.width / 2 * src.height)* 2
src=core.resize.Spline36(src,1920,nh,dither_type='error_diffusion')

src=depth(src,10,dither_type='error_diffusion')

src.set_output()

import vapoursynth as vs
from vsutil import depth
core = vs.get_core()

src=core.lsmas.LWLibavSource(r'D:\Test\Maddalena 1971 1080p Blu-ray AVC DTS-HD MA 2.0-DAMN\00000 - 2 - h264, 1080p24.h264')

src=core.std.Crop(src,top=20,bottom=20)

src=depth(src,16)
#Fixing dirty lines
src=core.fb.FillBorders(src,top=1,bottom=1,mode="repeat")

h=round(1280 / src.width / 2 * src.height) * 2
#Resizing
src=core.resize.Spline36(src,1280,h,dither_type='error_diffusion')

src=depth(src,8,dither_type='error_diffusion')

src.set_output()

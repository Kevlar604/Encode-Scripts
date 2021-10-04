import vapoursynth as vs
import awsmfunc as awf
from vsutil import depth

core = vs.get_core()


gbr=core.lsmas.LWLibavSource(r'D:\MovieUK.mkv')

#Cropping
gbr=core.std.Crop(gbr,top=20,bottom=20)

#Dithering to 16 bit depth for filtering
gbr=depth(gbr,16)

#Fixing dirty lines
gbr=awf.bbmod(gbr,left=3,right=3,blur=12,thresh=32000)

#Dithering down to 8 bit depth
gbr=depth(gbr,8,dither_type='error_diffusion')

#gbr=awf.SelectRangeEvery(gbr, every=3000, length=50, offset=10000)

gbr.set_output()

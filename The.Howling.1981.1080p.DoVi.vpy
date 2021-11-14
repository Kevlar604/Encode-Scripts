import vapoursynth as vs
from vapoursynth import core
from vsutil import depth


#Source
src=core.lsmas.LWLibavSource(r'D:\Test\The.Howling.1981.2160p.UHD.BluRay.REMUX.DV.HDR.HEVC.DTS-HD.MA.5.1-iNTERZØNE_track1_[eng].hevc')

#Cropping and resizing at 16 bit depth
src=depth(src,16)

#Cropping blackbars
src=core.std.Crop(src,top=40,bottom=40)

#Finding new height
nh=round(1920 /src.width / 2 * src.height)* 2

#Resizing
src=core.resize.Spline36(src,1920,nh)

#Dithering down to native 10 bit depth
src=depth(src,10,dither_type="error_diffusion")

src.set_output()

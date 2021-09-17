import vapoursynth as vs
from muvsfunc import SSIM_downsample
from vsutil import depth 




core = vs.get_core()



src=core.ffms2.Source(r'D:\Test\The.Thing.1982.UHD.BluRay.2160p.DTS-X.7.1.HEVC.REMUX-FraMeSToR.mkv')
src=core.std.Crop(src,top=264,bottom=264)
nh=round(1920 /src.width / 2 * src.height)* 2
#Resizing at 32 bit float
src=SSIM_downsample(src,w=1920,h=nh,kernel='Spline36',use_fmtc=False,sigmoid=False,curve='2020')
src=depth(src,10,dither_type="error_diffusion")



src.set_output()



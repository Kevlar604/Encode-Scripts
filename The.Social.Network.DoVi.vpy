import vapoursynth as vs
from vsutil import depth
core = vs.get_core()

src=core.lsmas.LWLibavSource(r'D:\Test\The.Social.Network.2010.2160p.UHD.BluRay.REMUX.DV.HDR.HEVC.Atmos-TRiToN_track1_[eng].hevc')
src=depth(src,16)
src=core.std.Crop(src,top=280,bottom=280)
nh=round(1920 / src.width / 2 * src.height) * 2
src=core.fb.FillBorders(src,left=1,right=1,mode="repeat")
src=core.resize.Spline36(src,1920,nh,dither_type="error_diffusion")
src=depth(src,10,dither_type="error_diffusion")
src.set_output()

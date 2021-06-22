import vapoursynth as vs
import rekt
import awsmfunc as awf
import havsfunc as haf
import vsutil
import urllib.request
core = vs.get_core()


path=r'D:\Test\Dawn.of.the.Dead.1978.Extended.Cannes.Cut.2160p.UHD.Blu-ray.Remux.HEVC.HDR10P.DTS-HD.MA.5.1-SECONDSIGHT.mkv'
src=core.ffms2.Source(path)
src=vsutil.depth(src,16)
src=core.std.CropRel(src, left=0, top=44, right=0, bottom=44)
h = round((1920*src.height/src.width) / 2) * 2
src=core.resize.Spline36(src,width=1920,height=h,dither_type='error_diffusion')
src=vsutil.depth(src,10,dither_type='error_diffusion')
src=src.set_output()

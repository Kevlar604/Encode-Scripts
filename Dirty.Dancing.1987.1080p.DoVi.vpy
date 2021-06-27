import vapoursynth as vs
import awsmfunc as awf
import vsutil
core = vs.get_core()

path=r'D:\Test\Dirty.Dancing.1987.2160p.UHD.BluRay.REMUX.DV.HDR.HEVC.Atmos-TRiToN_track1_[eng].hevc'
src=core.lsmas.LWLibavSource(path)
src=vsutil.depth(src,16)
src=core.std.Crop(src, left=0, right=0, top=42, bottom=42)
nh=round(1920 / src.width / 2 * src.height) * 2
src=core.resize.Spline36(src,1920,nh,dither_type='error_diffusion')
src=vsutil.depth(src,10,dither_type='error_diffusion')
src.set_output()

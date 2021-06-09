import vapoursynth as vs
import awsmfunc as awf
import vsutil
core = vs.get_core()

path=r'D:\Sync\Django.1966.UHD.BluRay.2160p.FLAC.1.0.DV.HEVC.REMUX-FraMeSToR.mkv'
src=core.ffms2.Source(path)
src=vsutil.depth(src,16)
src=core.std.CropRel(src,120,120,0,0)
nw=round(1080 / src.height / 2 * src.width) * 2
src=core.resize.Spline36(src,nw,1080)
src=vsutil.depth(src,10,dither_type='error_diffusion')
src.set_output()

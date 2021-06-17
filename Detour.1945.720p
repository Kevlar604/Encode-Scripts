import vapoursynth as vs
import awsmfunc as awf
core = vs.get_core()

path=r'D:\DETOUR_dgHD\00274 - 2 - h264, 1080p24.h264'
src=core.lsmas.LWLibavSource(path)
src=core.std.CropRel(src, left=220, top=0, right=220, bottom=0)
nw=round(720 / src.height / 2 * src.width) * 2
src=core.resize.Spline36(src,nw,720)
src.set_output()

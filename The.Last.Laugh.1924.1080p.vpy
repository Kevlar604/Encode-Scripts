import vapoursynth as vs
import vsutil
from rekt import rektlvls
import awsmfunc as awf
import havsfunc as haf
import fvsfunc as fvf
core = vs.get_core()

video=core.lsmas.LWLibavSource(r'D:\Test\Der.Letzte.Mann.aka.The.Last.Laugh.1924.Bluray.REMUX-Machine.mkv')
video=core.std.CropRel(video,left=242,top=0,right=242,bottom=0)
video4=video
video=video.fb.FillBorders(left=1, right=1, bottom=0, top=0, mode="fillmargins")#fixing 1 px dirty line on left and right
video2=vsutil.depth(video, 16)
mask = core.std.Sobel(video2, 0)
luma = core.std.ShufflePlanes(mask, 0, colorfamily=vs.GRAY)
mask_outer=luma.std.Maximum().std.Maximum().std.Inflate()
mask_inner=mask_outer.std.Minimum().std.Minimum().std.Minimum().std.Deflate()
halos = core.std.Expr([mask_outer, mask_inner], 'x y -')
dehalo = haf.DeHalo_alpha(video2)
src = core.std.MaskedMerge(video2, dehalo, halos)
src = vsutil.depth(src, 8, dither_type='error_diffusion')
final=fvf.rfs(video,src,"[22484 23399]")
final.set_output()

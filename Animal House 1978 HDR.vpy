import awsmfunc as awf
import vapoursynth as vs
import Debandmask as db
import vsutil
core = vs.get_core()
 
path=r'D:\Sync\National.Lampoons.Animal.House.1978.UHD.BluRay.2160p.DTS-X.7.1.HEVC.REMUX-FraMeSToR.mkv'
video=core.ffms2.Source(path)
video = core.std.CropRel(video, left=0, top=40, right=0, bottom=40)
nh=round(1920 / video.width / 2 * video.height) * 2
video=core.resize.Spline36(video,1920,nh)
video=vsutil.depth(video,16)
mask=db.debandmask(video)
deband=core.neo_f3kdb.Deband(video, y=48, cb=45, cr=45, range=20, grainy=10,grainc=5, output_depth=16, keep_tv_range=True)
video=core.std.MaskedMerge(deband,video,mask)
video=vsutil.depth(video,10,dither_type='error_diffusion')
video.set_output()

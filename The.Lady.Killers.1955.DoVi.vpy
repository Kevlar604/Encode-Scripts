import vapoursynth as vs
from vapoursynth import core

src=core.lsmas.LWLibavSource(r'D:\Test\The.Ladykillers.1955.2160p.UHD.BluRay.Remux.HDR.DV.HEVC.FLAC.1.0-PmP_track1_[eng].hevc')
src=core.std.Crop(src,left=440,right=440)
src=core.resize.Spline36(src,round(1080/src.height / 2 * src.width) * 2,1080)
src.set_output()

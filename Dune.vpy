import vapoursynth as vs
from vsutil import depth
import awsmfunc as awf
from adptvgrnMod import adptvgrnMod
from muvsfunc import SSIM_downsample
import kagefunc as kgf
core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

src=core.lsmas.LWLibavSource(r'D:\Test\Dune.1984.2160p.UHD.Blu-ray.Remux.HEVC.HDR.DoVi.DTS-HD.MA.5.1-ARROW4K_track1_[eng].hevc')
src=core.std.Crop(src,top=264,bottom=264)
nh=round(1920 / src.width / 2 * src.height) * 2
src=awf.fb(src,left=1,right=1)
src=core.resize.Spline36(src,1920,nh)
src.set_output()
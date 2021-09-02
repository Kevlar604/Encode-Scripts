import vapoursynth as vs
from vsutil import depth
import awsmfunc as awf

core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

#Importing source
src=core.lsmas.LWLibavSource(r'D:\Test\Dune.1984.2160p.UHD.Blu-ray.Remux.HEVC.HDR.DoVi.DTS-HD.MA.5.1-ARROW4K_track1_[eng].hevc')

#Cropping black bars
src=core.std.Crop(src,top=264,bottom=264)

#Finding new height
nh=round(1920 / src.width / 2 * src.height) * 2

#Cleaning the edges
src=awf.fb(src,left=1,right=1)

#Resizing
src=core.resize.Spline36(src,1920,nh)

#Final output
src.set_output()

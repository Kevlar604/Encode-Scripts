import vapoursynth as vs
core = vs.get_core()
 
path=r'D:\Sync\Deadlock.1970.2160p.UHD.BluRay.Remux.HDR.HEVC.FLAC.1.0-PmP.mkv'
video=core.ffms2.Source(path)
video=core.std.CropRel(video,128,128,0,0)
video =core.resize.Spline36(video,1792,1080)
video.set_output()

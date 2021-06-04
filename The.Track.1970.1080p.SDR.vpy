a1=FFVideoSource("D:\Sync\The.Track.1975.2160p.UHD.BluRay.Remux.HEVC.FLAC.1.0-PmP.mkv")
a1=a1.z_ConvertFormat(width=1920,height=1080,pixel_type="YV12",resample_filter="spline36", dither_type="error_diffusion",approximate_gamma = false)
a1=a1.ConvertToYUV420(matrix="Rec709")
a1=a1.Crop(58,0,-58,0).FillBorders(3,1,2,1,mode=0).FixCbr(2,2).FixCBr(1800,-6).FixCBr(1796,-2)
a=f3kdb(a1,range=20,Y=48,cb=32,cr=32,keep_tv_range=True)
b=ReplaceFramesSimple(a1,a,mappings="[0 3638]")
b

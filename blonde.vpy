import vapoursynth as vs
import awsmfunc as awf
from vsutil import depth,get_y
from muvsfunc import SSIM_downsample
import fvsfunc as fvf
core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

src=core.lsmas.LWLibavSource(r'D:\Test\BLONDE VENUS\BDMV\STREAM\00003.m2ts')
src=core.std.CropRel(src, left=220, right=220)

#s=core.lsmas.LWLibavSource(r'D:\Test\BLONDE_VENUS_rmHD\BDMV\STREAM\00274.m2ts')
#s=core.std.CropRel(s,left=220, right=220)

#b=core.std.BlankClip(width=986,height=720,format=vs.YUV420P8,length=40,fpsnum=24000,fpsden=1001,color=[0,127,127])
#e=core.lsmas.LWLibavSource(r'D:\Test\encoded8.mkv')
#src=b+src #1144
#src=src[1144:]
#s=s[1096:]
#dif=core.std.MakeDiff(s,src)
#s1=core.std.MergeDiff(s,dif)
#s=awf.FrameInfo(s,"Criterion")
#src=awf.FrameInfo(src,"Indicator")
#core.std.Interleave([src,s]).set_output()


nw=round(720/src.height / 2 * src.width) * 2

#s=SSIM_downsample(s,w=nw,h=720,kernel='Spline36',use_fmtc=False,sigmoid=True)

src=SSIM_downsample(src,w=nw,h=720,kernel='Spline36',use_fmtc=False,sigmoid=True)

src=depth(src,8,dither_type="error_diffusion")
#s=depth(s,8,dither_type="error_diffusion")
u=depth(src,16)
u=core.std.Crop(u,left=20,right=20)
u=awf.fb(u,left=2,right=2)
u=core.std.AddBorders(u,left=20,right=20)
u=depth(u,8,dither_type="error_diffusion")
src=fvf.rfs(src,u,"[0 578]")
#src=src[5000:6000]
src.set_output()


#src=awf.FrameInfo(src,"Source")
#e=awf.FrameInfo(e,"JKP")
#core.std.Interleave([src,e]).set_output()
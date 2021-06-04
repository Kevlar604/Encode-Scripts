import vapoursynth as vs
import fvsfunc as fvf
import vsutil
import functools
import adptvgrnMod as adp
import rekt as rk
import kagefunc as kgf
import awsmfunc as awf
core = vs.get_core()

path=r'D:\Sync\A_WOMAN_LIKE_EVE_BD\BDMV\STREAM\00000.m2ts'
video=core.lsmas.LWLibavSource(path)
video=core.std.CropRel(video,left=60,top=0,right=60,bottom=0)
video=core.resize.Spline36(video, width=1200, height=720,dither_type='error_diffusion')
v1=v3=video
video=core.bilateral.Bilateral(video,sigmaS=3.0,sigmaR=0.02,algorithm=0)
video=core.std.ShufflePlanes(video, planes=[0], colorfamily=vs.GRAY)
video=vsutil.depth(video,16)
v2=vsutil.depth(v1,16)
#Fixing dirty lines
cf=core.edgefixer.ContinuityFixer(v2, left=4, top=0, right=6, bottom=0, radius=15)
v2=core.std.Merge(v2,cf,[0,1])
v2=rk.rektlvls(v2,rownum=None, rowval=None, colnum=[3,1195,1196],colval=[-5,2,2], prot_val=20).fb.FillBorders(2,1,2,1,mode="fillmargins")
video=core.bilateral.Bilateral(video,sigmaS=3.0,sigmaR=0.02,algorithm=0)#Getting rid of noise at the same time preserving details because of uneven noise hence chose bilateral before preparing our edgemask.
#5*5 Sobel in horizontal and vertical direction respectively. This is the most accurate approximation of Sobel edgemask. More on here https://stackoverflow.com/questions/9567882/sobel-filter-kernel-of-large-size/41065243#41065243
sobelx=core.std.Convolution(video,[-5,-4,0,4,5,-8,-10,0,10,8,-10,-20,0,20,10,-8,-10,0,10,8,-5,-4,0,4,5])
sobely=core.std.Convolution(video,[-5,-8,-10,-8,-5,-4,-10,-20,-10,-4,0,0,0,0,0,4,10,20,10,4,5,8,10,8,5])
src=core.std.Expr([sobelx,sobely],'x dup * y dup * + sqrt')
ret=core.retinex.MSRCP(video, sigma=[50, 200, 350], upper_thr=0.005)
canny=core.tcanny.TCanny(ret,mode=1,sigma=1).std.Minimum(coordinates=[1, 0, 1, 0, 0, 1, 0, 1])
max_value=(1 << video.format.bits_per_sample) - 1
mask=core.std.Expr([src,canny],f'x y + {max_value} min').std.Expr('x 32767 >= 65535 0 ?')
deband=core.neo_f3kdb.Deband(v2, y=120, cb=32, cr=32, range=31, grainy=32,grainc=0, output_depth=16, keep_tv_range=True)
grain=adp.adptvgrnMod(deband, strength=2.5, size=1.25, sharp=35, static=False,luma_scaling=3, grain_chroma=False)
v2=core.std.MaskedMerge(grain,v2,mask)
v2=vsutil.depth(v2,8,dither_type='error_diffusion')
#0-1330 44365-45192 77587-82046 89196-89865 112289 133569-133738
v1=fvf.rfs(v1,v2,"[0 9949][67752 71379][44365 45192][55492 62573][77587 82046][89196 89865][133569 133738]")
#v1= awf.SelectRangeEvery(v1, every=15000, length=250, offset=[1000, 5000])
v1.set_output()

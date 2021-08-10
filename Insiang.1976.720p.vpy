import vapoursynth as vs
import awsmfunc as awf
import kagefunc as kgf
from rekt import rektlvls
import fvsfunc as fvf
from vsutil import *
from adptvgrnMod import adptvgrnMod
from mt_lutspa import *
from functools import partial
import awsmfunc as awf
core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

path=r'D:\Test\Insiang.1976.GBR.BluRay.Remux.1080p.AVC.FLAC.1.0-ZQ.mkv'
src=core.ffms2.Source(path)

#Fixing dirty lines 
src=depth(src,16)
src=core.std.Crop(src, left=220, right=220, top=0, bottom=0)
src=awf.bbmod(src,left=2,top=0,right=2,bottom=0,blur=20,planes=[0,1,2],thresh=32800)
src=rektlvls(src,rownum=[0,1079],rowval=[5]*2)

#Resizing
w=round(720 / src.height / 2 * src.width) * 2
src=core.resize.Spline36(src,w,720,dither_type='error_diffusion')

#Storing the sorce video videonode into a new variable for future reference 
s=src

#defining Sobel edgemask
Sobel_x = lambda clip: clip.std.Convolution([-1, 0, 1, -2, 0, 2, -1, 0, 1])
Sobel_y = lambda clip: clip.std.Convolution([-1, -2, -1, 0, 0, 0, 1, 2, 1])

#Extracting luma
y=get_y(src)

#Building a ridge detection mask
sbx = Sobel_x(y)
sby = Sobel_y(y)
sbxx = Sobel_x(sbx)
sbyy = Sobel_y(sby)
sbxy = Sobel_y(sbx)
m=core.std.Expr([sbxx,sbyy],'x dup * y dup * +')
n=core.std.Expr([sbxy],'x dup * 4 *')
o=core.std.Expr([sbxx,sbyy],'x y * 2 *')
res=core.std.Expr([m,n,o],'x y + z - sqrt')
ridge=core.std.Expr([sbxx,sbyy,res],'x y + z + 0.5 * ')
ridge=depth(ridge,16,dither_type='error_diffusion').std.Binarize(25000).std.Maximum()

#Building a gradient mask to deband chroma at darker scenes
grad=lutspa(src, mode="relative",relative=True,biased=True,expr="y x 0.00000001 + / atan",chroma=None)
#Brightening the mask
grad=awf.fixlvls(grad, gamma=1.1)

#Conditional filtering(deband) based on content light
def conditionalfilter(n, f, clip,filter1,filter2):
    if f[0].props.PlaneStatsAverage < 0.23 :
        return filter1
    elif f[0].props.PlaneStatsAverage >= 0.23  and f[0].props.PlaneStatsAverage < 0.30 :    
        return filter2	    
    else:
        return clip

#For debanding relatively darker reddish scenes and adding static grain to them
deband1=src.f3kdb.Deband(y=50,cr=64,cb=56,grainy=60,grainc=64,dynamic_grain=False, keep_tv_range=True, output_depth=16)
deband1=adptvgrnMod(deband1, strength=.9, cstrength=1, size=1.15, sharp=60,grain_chroma=True,luma_scaling=8,fade_edges=True)

#debanding chroma
debandchroma=core.std.MaskedMerge(src,deband1,grad,planes=[1,2],first_plane=False)

#Building a strong retinex edgemask for debanding luma
ret=core.retinex.MSRCP(y, sigma=[50, 200, 350], upper_thr=0.005)
mask=[[-7, 0, 7, -10, 0, 10, -7, 0, 7],
     [-7, -10, -7, 0, 0, 0, 7, 10, 7]]
conv=[core.std.Convolution(ret,matrix=m[0:10],divisor=7)for m in mask]
mag=core.std.Expr(conv,'x x * y y * + sqrt').std.Binarize(25000).std.Maximum().std.Maximum().std.Inflate()

#Debanding luma for relatively darker scenes
deband1=core.std.MaskedMerge(deband1,src,mag,planes=0)

#Merging debanded luma with debanded chroma
deband1=core.std.ShufflePlanes([deband1,debandchroma],planes=[0,1,2],colorfamily=vs.YUV)

#For debanding relatively brighter scene and adding dynamic grain
graindynamic=lambda x: x.f3kdb.Deband(y=48,cr=48,cb=48,grainy=20,grainc=30,dynamic_grain=True, keep_tv_range=True, output_depth=16)
deband2=adptvgrnMod(src, strength=1.2, cstrength=1.25, size=0.8, sharp=60,grain_chroma=True,grainer=graindynamic,luma_scaling=6)
deband2=core.std.MaskedMerge(deband2,src,ridge)

mask2=kgf.retinex_edgemask(src).std.PlaneStats()
mask3=kgf.retinex_edgemask(deband1).std.PlaneStats()
mask4=kgf.retinex_edgemask(deband2).std.PlaneStats()

#conditonal filtering
src=src.std.FrameEval(partial(conditionalfilter,clip=src,filter1=deband1,filter2=deband2),[mask2,mask3,mask4])
s=depth(s,8,dither_type='error_diffusion')
src=depth(src,8,dither_type='error_diffusion')

#Excluding the intro and end credit scenes from conditional filtering
s=depth(s,8,dither_type='error_diffusion')
src=fvf.rfs(s,src,"[1345 135307]")

src.set_output()

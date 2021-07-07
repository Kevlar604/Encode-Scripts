import vapoursynth as vs
import mvsfunc as mvf 
import insaneAA 
import muvsfunc as muvf
import havsfunc as hvf
import kagefunc as kgf
import awsmfunc as awf
import vsutil
import fvsfunc as fvf
import lvsfunc as lvf 
import adptvgrnMod
from nnedi3_rpow2 import *
core = vs.get_core()

#Some of the parts of the script are commented because initially I thought of doing 1080p which failed miserably hence switched to 720p later also the movie is upscaled from 855p so doing 720p makes more sense

path=r'D:\Sync\Demon Slayer -Kimetsu no Yaiba- Mugen Train Movie v3 2020 1080p BluRay REMUX AVC AC3 5.1 Dual Audio -ZR-.mkv'
src=core.ffms2.Source(path)
credits=core.std.Trim(src,first=161091,last=168023)
src=core.std.Trim(src,first=0,last=161090)
src=fvf.Depth(src, 32)
planes=vsutil.split(src)
h = 855
w=vsutil.get_w(h)
b, c =  1/3, 1/3
#Rescaling from 855p(directly resizing to 720p is causing ringing artifacts)
descaled=core.descale.Debicubic(planes[0],w,h,b,c)
upscaled=nnedi3_rpow2(descaled, 2).resize.Spline36(1920,1080)
planes=[upscaled,planes[1],planes[2]]
src=vsutil.join(planes)
src=vsutil.depth(src,16,dither_type='error_diffusion')
#resizing
src=core.resize.Spline36(src,width=1280,height=720)
#Fixing minor dirty lines
src=core.cf.ContinuityFixer(src, [2,1,1], [2,1,1], [1,0,0], [1,0,0], [10,5,5])
src=core.fb.FillBorders(src,left=1,top=2,right=0,bottom=0)
src=vsutil.depth(src,8,dither_type='error_diffusion')
#Denoising at 8 bit depth because at 16 bit it's slow af!
src=core.knlm.KNLMeansCL(src, a=2, h=1.5, d=3, s=0, channels="Y",device_type="gpu", device_id=0)
src=vsutil.depth(src,16)
y=vsutil.get_y(src)
#Selectively dehaloing some scenes
dehalomask=hvf.FineDehalo(y,showmask=4)
mask_outer=vsutil.iterate(dehalomask, core.std.Maximum, 2)
mask_inner=vsutil.iterate(mask_outer, core.std.Minimum, 3)
halos=core.std.Expr([mask_outer, mask_inner], 'x y -')
dh=hvf.DeHalo_alpha(src,rx=2.5,ry=2.5)
dh=core.std.MaskedMerge(src,dh,halos)
src=fvf.rfs(src,dh,"[59746 69283][75443 75677]")
#Creating antialiasing mask 
l_mask=lvf.util.quick_resample(src, kgf.retinex_edgemask)
#Moderate antialiaser to fix jaggies and broken lineart
aa=lvf.aa.nneedi3_clamp(src, strength=1.25)
src=core.std.MaskedMerge(src, aa, l_mask)
#Debanding using two different masks , a custom defined retinex edgemask and a 5*5 Sobel mask
t=core.tcanny.TCanny(y,planes=0)
maxvalue=(1 << vsutil.get_depth(y)) - 1
w = [5]*3 + [-3]*5
weights = [w[-i:] + w[:-i] for i in range(4)]
c = [core.std.Convolution(y, (w[:4]+[0]+w[4:]), saturate=False) for w in weights]
c=core.std.Expr(c, 'x y max z max a max')
t=core.std.Minimum(t,coordinates=[1, 0, 1, 0, 0, 1, 0, 1])
ret=core.retinex.MSRCP(y, sigma=[50, 200, 350], upper_thr=0.005)
sobelx=core.std.Convolution(y,[-5,-4,0,4,5,-8,-10,0,10,8,-10,-20,0,20,10,-8,-10,0,10,8,-5,-4,0,4,5])
sobely=core.std.Convolution(y,[-5,-8,-10,-8,-5,-4,-10,-20,-10,-4,0,0,0,0,0,4,10,20,10,4,5,8,10,8,5])
smask=core.std.Expr([sobelx,sobely],'x dup * y dup * + sqrt')
smask=core.std.Binarize(smask,32000).std.Maximum().std.Maximum().std.Inflate()
mask=core.std.Expr([c,t],f'x y + {maxvalue} min')
deband1=core.neo_f3kdb.Deband(src,range=20,y=64,cb=48,cr=48)
deband2=core.neo_f3kdb.Deband(src,range=18,y=48,cb=45,cr=45)
deband1=core.std.MaskedMerge(deband1,src,mask)
deband2=core.std.MaskedMerge(deband2,src,smask)
#dehalo 59746-61283,75443-75677
#14350-26106,29819-30740,30741-42212,59742-137970
#4179-10151,10152-14379,26107-29818,42212-59741,13791-161090
#Modifying grains
deband2=adptvgrnMod.adptvgrnMod(deband2,strength=0.25, size=1.15, sharp=75, static=True)
src=adptvgrnMod.adptvgrnMod(deband1,strength=0.25, size=1.15, sharp=75, static=True)
src=fvf.rfs(src,deband2,"[4179 10151][26107 29818][42212 59741][13791 161090]")
src=vsutil.depth(src,8,dither_type='error_diffusion')

#Fixing credits
c=credits
credits=vsutil.depth(credits,16)
src16 = vsutil.get_y(credits)
src32 = fvf.Depth(src16, 32)

standard_scale = core.resize.Spline36(credits, 1280, 720, format=vs.YUV444P16, resample_filter_uv='spline16')

inverse_scale = core.descale.Debicubic(src32, 1280, 720)
inverse_scale = fvf.Depth(inverse_scale, 16)

#absolute error of descaling
error = core.resize.Bicubic(inverse_scale, 1920, 1080)
error = core.std.Expr([src16, error], 'x y - abs')

#A light error mask to protect smaller spots against halos aliasing and rings
error_light = core.std.Maximum(error, coordinates=[0,1,0,1,1,0,1,0])
error_light = core.std.Expr(error_light, '65535 x 1000 / /')
error_light = core.resize.Spline36(error_light, 1280, 720)

#Adaptive luma rescaling and risizing stolen from guide.encode.moe
#masks are always full-range, so manually set fulls/fulld to True or range_in/range to 1 when changing bitdepth
credits = core.std.Expr([src16, error], 'x 55800 > y 2500 > and 255 0 ?', vs.GRAY8)
credits = core.resize.Bilinear(credits, 1280, 720)
credits = core.std.Maximum(credits).std.Inflate().std.Inflate()
credits = fvf.Depth(credits, 16, range_in=1, range=1)

descale_mask = core.std.Expr([error_light, credits], 'x y -')

output = vsutil.get_y(standard_scale).std.MaskedMerge(inverse_scale, descale_mask)
credits = muvf.MergeChroma(output, standard_scale)
credits=vsutil.depth(credits,8,dither_type='error_diffusion')
#Denoising credits
credits=core.knlm.KNLMeansCL(credits, a=3, h=2, d=3, s=0, channels="Y",device_type="gpu", device_id=0)
credits=vsutil.depth(credits,16)
cmask=core.std.ShufflePlanes(credits,planes=0,colorfamily=vs.GRAY)
#Antialiasing mask for credits
cmask=core.std.Prewitt(cmask).std.Expr('x 65000 < x 0 ?').std.Minimum(coordinates=[0,1,0,1,1,0,1,0]).std.Invert()
#cmask=core.jinc.JincResize(cmask,width=1920,height=1080)
l,u,v=vsutil.split(credits)
#l=nnedi3_rpow2(l, 2).resize.Spline36(1920,1080)
u=core.resize.Spline16(u,640,360)
v=core.resize.Spline16(v,640,360)
credits=vsutil.join([l,u,v])
#Employing strong antialiaser
aa1=insaneAA.insaneAA(credits)
credits=core.std.MaskedMerge(aa1,credits,cmask)
#Debanding mask for credits
cmask2=kgf.retinex_edgemask(credits)
#Debanding and adding grains to hide white patches on black background credits
debandcredits=core.neo_f3kdb.Deband(credits,range=25,y=64,cb=64,cr=64,grainy=200,grainc=150)
debandcredits=adptvgrnMod.adptvgrnMod(debandcredits, strength=0.25, size=1.15, sharp=75, static=True)
credits=core.std.MaskedMerge(debandcredits,credits,cmask2)
credits=vsutil.depth(credits,8,dither_type='error_diffusion')
src=core.std.Splice([src,credits])
src.set_output()

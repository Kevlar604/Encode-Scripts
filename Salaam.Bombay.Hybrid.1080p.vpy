
import vapoursynth as vs
import vsutil
from rekt import *
import havsfunc as hvf
import fvsfunc as fvf
from muvsfunc import SSIM_downsample
from nnedi3_rpow2 import*
import kagefunc as kgf
import awsmfunc as awf
from adptvgrnMod import *

core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

#BFI
src=core.lsmas.LWLibavSource(r'D:\Sync\Salaam Bombay! (1988) UK BD\00004 - 2 - h264, 1080p24.h264')

#Kino Lorber
src1=core.lsmas.LWLibavSource(r'D:\Sync\Salaam.Bombay.1988.COMPLETE.BLURAY-watchHD\00000 - 2 - h264, 1080p24.h264')

#Cropping the Kino Lorber source
src1=core.std.Crop(src1,top=20,bottom=20)

#Changing fps of BFI
src=core.std.AssumeFPS(src,fpsnum=24000,fpsden=1001)

blk=core.std.BlankClip(width=1920,height=1080, format=vs.YUV420P8, length=204, fpsnum=24000, fpsden=1001, color=[0, 128, 128])
#Trimming BFI intros and adding blank screen to BFI they will be later replaced by the Kino end credit scenes
src=src[830:]+blk

#Fixing 1px dirty line of Kino
src1=awf.fb(src1,left=1)
#Dithering to 32 bit depth
src,src1=[vsutil.depth(s,32) for s in (src,src1)]

#Supersampling kno twice it's resolution
src1=nnedi3_rpow2(src1,2)
#downsampling Kino to 1080p
src1= SSIM_downsample(src1,w=1920,h=1080,kernel='Spline36',use_fmtc=True,sigmoid=True)
#Adding intro from kino to BFI
src=src1[0:909]+src
src=fvf.rfs(src,src1,"[159882 164615]")

#Dithering down to 16 bit
src=vsutil.depth(src,16,dither_type='error_diffusion')

#Fixing BFI dirty lines
fix=awf.bbmod(src,left=2,top=2,right=1,bottom=1,blur=12,planes=[0,1,2],thresh=10000)

#Replacing BFI end credits and blank scenes with Kino end credits 
src=fvf.rfs(src,fix,"[159882 164615]")

#Performing bunch of deblocking and debanding techniques based on scenes. Added grains to hide blocky artefacts and to brighten the BFI source as the BFI source has bit of an incorrect levels for dark scenes. Black is almost outside of tv range instead of tinkering the std.levels used grains to brighten them up.
planes=[core.std.ShufflePlanes(src, planes=x, colorfamily=vs.GRAY) for x in range(3)]
mask=kgf.retinex_edgemask(planes[0]).std.Binarize(40000).std.Maximum().std.Inflate()
planes[0]=core.placebo.Deband(planes[0],threshold=6, radius=36.0, grain=50)
planes[1]=core.placebo.Deband(planes[1],threshold=3, radius=26.0, grain=55)
planes[2]=core.placebo.Deband(planes[2],threshold=3, radius=26.0, grain=60)
dbn=vsutil.join(planes)
dbn1=adptvgrnMod(dbn,strength=0.9,cstrength=0.95,size=0.85, sharp=50, static=False, luma_scaling=5)
dbn=core.std.MaskedMerge(dbn,src,mask)
dbn=fvf.rfs(dbn,dbn1,"[909 3810]")
dbn2=sizedgrn(dbn, strength=.1, size=0.65, sharp=40,static=False)
dbn=fvf.rfs(dbn,dbn2,"[4745 5763]")
db3=fvf.gf3(src,thr=1, elast=3, mask=0)#For some fading scenes
dbn=fvf.rfs(dbn,db3,"[7624 7675]")
db4=core.neo_f3kdb.Deband(src,range=25, y=64, cb=64, cr=64, grainy=10, grainc=10, sample_mode=4, output_depth=16)
db4=adptvgrnMod(db4,strength=.6,cstrength=.5,size=1.15,sharp=60,static=False, luma_scaling=8)
db4=core.std.MaskedMerge(db4,src,mask)
dbn=fvf.rfs(dbn,db4,"[28661 30021]")
db5=core.neo_f3kdb.Deband(src,range=25, y=48, cb=56, cr=56, grainy=20, grainc=40,dynamic_grain=False)
db5=adptvgrnMod(db5,strength=1,cstrength=1.1,size=1.5,sharp=60,static=True, luma_scaling=4)
db5=core.std.MaskedMerge(db5,src,mask)
dbn=fvf.rfs(dbn,db5,"[32803 42948],[75574 84708]") 
src=fvf.rfs(src,dbn,"[909 159881]")

#Finally dithering down to 8 bit
src=vsutil.depth(src,8,dither_type='error_diffusion')

#Final output
src.set_output()

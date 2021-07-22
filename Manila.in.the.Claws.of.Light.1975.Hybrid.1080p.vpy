import vapoursynth as vs
import awsmfunc as awf
from adptvgrnMod import *
from rekt import *
import fvsfunc as fvf
from math import sqrt
from vsutil import depth,get_y
core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

#Importing the sources,croping black borders and matching fps of two sources 
src=core.lsmas.LWLibavSource(r'D:\Test\Manila.in.the.Claws.of.Light.1975.1080p.BluRay.REMUX.AVC.FLAC.1.0-C0M3T.mkv')
s2=core.lsmas.LWLibavSource(r'D:\Test\video.h264')
src=core.std.Crop(src,left=0,top=22,right=0,bottom=22)
s2=core.std.Crop(s2,left=0,top=22,right=0,bottom=22)
s2=core.std.AssumeFPS(s2,fpsnum=24000,fpsden=1000)

#Merging the BFI luma plane with the Criterion chroma planes
blank=core.std.BlankClip(width=1920,height=1036,format=vs.YUV420P8,length=504,fpsnum=24000,fpsden=1000,color=[0,127,127])
b2=core.std.BlankClip(width=1920,height=1036,format=vs.YUV420P8,length=98,fpsnum=24000,fpsden=1000,color=[0,127,127])
src=blank+src
s=s2
s2=s2+b2
s3=core.std.ShufflePlanes([src,s2],planes=[0, 1, 2], colorfamily=vs.YUV)
s3=fvf.rfs(s3,s2,"[0 2300]")

#Replacing the merged end credit scenes with only the criterion source
s3=s3[0:182083]+s[182083: ] 

#dither
s3=depth(s3,16)
#Extracting 2px top and bottom edges and stacking them to the hybrid source
l1=core.std.Crop(s,left=0,top=0,right=0,bottom=s.height-2)
l2=core.std.Crop(s,left=0,top=s.height-2,right=0,bottom=0)
s3=core.std.Crop(s,left=0,top=2,right=0,bottom=2)
s3=core.std.StackVertical([l1,s3,l2])

#Fixing dirty lines
s3=awf.bbmod(s3,left=0,top=4,right=0,bottom=4,blur=999,planes=[0,1,2],thresh=1500)
s3=rekt_fast(s3,lambda x:core.fb.FillBorders(x,left=0,top=2,right=0,bottom=0), left=0, right=0, top=0, bottom=s3.height-6)
s3=rekt_fast(s3,lambda x:core.fb.FillBorders(x,left=0,top=0,right=0,bottom=2), left=0, right=0, top=s3.height-6, bottom=0)
s3=rektlvls(s3, colnum=[0], colval=[-1])

#Defining Chen Frei 3*3 mask
sqrt2=sqrt(2)
m=[[1, sqrt2, 1, 0, 0, 0, -1, -sqrt2, -1],
                [1, 0, -1, sqrt2, 0, -sqrt2, 1, 0, -1],
                [0, -1, sqrt2, 1, 0, -1, -sqrt2, 1, 0],
                [sqrt2, -1, 0, -1, 0, 1, 0, 1, -sqrt2],
                [0, 1, 0, -1, 0, -1, 0, 1, 0],
                [-1, 0, 1, 0, 0, 0, 1, 0, -1],
                [1, -2, 1, -2, 4, -2, 1, -2, 1],
                [-2, 1, -2, 1, 4, 1, -2, 1, -2],
                [1, 1, 1, 1, 1, 1, 1, 1, 1]]

M='x x * y y * + z z * + a a * +'
S=f'b b * c c * + d d * + e e * + f f * + {M} +'
exp=f'{M} {S} / sqrt'
div=[2 * sqrt2, 2 * sqrt2, 2 * sqrt2, 2 * sqrt2, 2, 2, 6, 6, 3]
#performing convolution at 32 bit depth
s3=depth(s3,32)
luma=get_y(s3)
conv=[core.std.Convolution(luma,mask[:9],divisor=i,saturate=False)for mask,i in zip(m,div)]
conv=core.std.Expr(conv,exp)

Dithering down to 16 bit
s3=depth(s3,16,dither_type='error_diffusion')

#defining Kirsch based retinex edge mask at 16 bit depth
w = [5]*3 + [-3]*5
weights = [w[-i:] + w[:-i] for i in range(4)]
c = [core.std.Convolution(luma, (w[:4]+[0]+w[4:]), saturate=False) for w in weights]
c=core.std.Expr(c, 'x y max z max a max')
conv=depth(conv,16,dither_type='ordered')
c=depth(c,16,dither_type='ordered')
#Adding the two masks clamped to 16 bit depth
mask=core.std.Expr([c,conv],'x y + 65535 min').std.Binarize(25000)

#Performing deblocking and debanding
deband=core.neo_f3kdb.Deband(s3,range=25,y=64,cb=48,cr=48,grainy=20,grainc=50,dynamic_grain=True)
deband=adptvgrnMod(deband,strength=1.15,cstrength=1.5,size=0.65,sharp=60,static=False,luma_scaling=4,grain_chroma=True,grainer=None,fade_edges=True,tv_range=True)
deband=core.std.MaskedMerge(deband,s3,mask)
s3=fvf.rfs(s3,deband,"[5904 179516]")

#dithering down to 8 bit depth
s3=depth(s3,8,dither_type='error_diffusion')

#Changing the fps to 23.976
s3=core.std.AssumeFPS(s3,fpsnum=24000,fpsden=1001)

#for test encodes
#s3=awf.SelectRangeEvery(clip=s3, every=3000, length=50, offset=10000)

#Final output
s3.set_output()



import vapoursynth as vs
import awsmfunc as awf
from vsutil import depth
from adptvgrnMod import adptvgrnMod
import kagefunc as kgf
from havsfunc import Deblock_QED
core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

#JPN Source
src=core.lsmas.LWLibavSource(r'D:\Test\Hana-bi 1997 1080p Blu-ray AVC LPCM 2.0-MM\video.h264')
#src=awf.FrameInfo(src,"JPN")

#FRE Source
src1=core.lsmas.LWLibavSource(r'D:\Test\Fireworks.1997.1080p.BluRay.REMUX.AVC.FLAC.2.0-C0M3T.mkv')
b=core.std.BlankClip(width=1920, height=1080,format=vs.YUV420P8,length=96,fpsnum=24000,fpsden=1001,color=[0,128,128])
src=b+src
#src1=awf.FrameInfo(src1,"FRE")

#Cropping both the sources
src=core.std.Crop(src,left=0,right=0, top=22, bottom=22)
src1=core.std.Crop(src1,left=0,right=0, top=22, bottom=22)

#Adding frames 0-96 to JPN from FRE and replacing 66209:67357 and 67357:148406 from JPN with FRE and trimming the logo scenes at the end of JPN
src=src1[0:97]+src[97:66209]+src1[66209:67357]+src[67357:148406]

#Dithering to 16 bit depth for the purpose of filtering
src,src1=[depth(s,16) for s in (src,src1)]

#Fixing dirty lines of both the sources
src=awf.fb(src,right=1,top=2)
src1=awf.fb(src1,left=1,right=1)

#Debanding JPN source
db=core.neo_f3kdb.Deband(src,range=25,y=128,cb=100,cr=100,grainy=100,grainc=100,dynamic_grain=True,keep_tv_range=True, output_depth=16)
db=adptvgrnMod(db,strength=3,cstrength=2.5,size=.5,sharp=80,static=False,luma_scaling=6,grain_chroma=True,grainer=None,fade_edges=False,tv_range=True)

#Getting rid of noise to generate noise free mask
denoise=core.bilateral.Bilateral(src,sigmaS=3.0,sigmaR=0.02)

#Generating first mask
mask=kgf.retinex_edgemask(denoise).std.Binarize(60000).std.Maximum().std.Maximum().std.Inflate()
db=core.std.MaskedMerge(db,src,mask)

#Including debanded frames 2154:2328 to the source
src=src[0:2154]+db[2154:2329]+src[2329:]

#Generating second mask
mask2=kgf.retinex_edgemask(src1).std.Binarize(40000).std.Maximum().std.Maximum().std.Inflate()

#Second deband of the FRE source
db2=core.neo_f3kdb.Deband(src1,range=20,y=64,cb=48,cr=48,grainy=30,grainc=30,dynamic_grain=True,keep_tv_range=True, output_depth=16)
db2=adptvgrnMod(db2,strength=.5,cstrength=.5,size=.5,static=False,luma_scaling=12)
db2=core.std.MaskedMerge(db2,src1,mask2)

#Including debanded frames 96148:96760 FRE to the JPN source
src=src[0:96148]+db2[96148:96761]+src[96761:]
#96148 96760

#Dithering down to native 8 bit depth
src=depth(src,8,dither_type="error_diffusion")
#src=awf.SelectRangeEvery(clip=src, every=3000, length=50, offset=10000)
src.set_output()

#2154 #2328 #2058 #2154 #66209 67356


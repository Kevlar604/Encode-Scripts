import vapoursynth as vs
from muvsfunc import SSIM_downsample
from vsutil import get_y
from adptvgrnMod import adptvgrnMod
import kagefunc as kgf
import awsmfunc as awf
import fvsfunc as fvf
core = vs.get_core()

core.num_threads = 4
core.max_cache_size = 2048

path=r'D:\Test\Black.Sabbath.1963.European.Cut.UHD.BluRay.2160p.DTS.2.0.SDR.HEVC.REMUX-FraMeSToR.mkv'
src=core.lsmas.LWLibavSource(path)

#Cropping black bars
src=core.std.Crop(src,top=42, bottom=42)

#Finding new height
nh=round(1920 / src.width / 2 * src.height) * 2

#Resizing at 32 bit depth
src=SSIM_downsample(src,w=1920,h=nh,kernel='Spline36',use_fmtc=False,sigmoid=True)

#Dithering to 16 bit depth
src=core.fmtc.bitdepth(src,bits=16,dmode=7)

#Extracting luma plane
luma=get_y(src)

#Deblocking/debanding
db2=core.neo_f3kdb.Deband(src,range=25,y=64,cb=45,cr=45,grainy=30,grainc=20,blur_first=True,dynamic_grain=True, keep_tv_range=True, output_depth=16)
db2=adptvgrnMod(db2,strength=.6,cstrength=.4,size=0.6,sharp=70,static=False,luma_scaling=5,grain_chroma=True,grainer=None,fade_edges=True,tv_range=True)
mask2=kgf.retinex_edgemask(luma).std.Expr('x 10000 <= 0 x ?')
db2=core.std.MaskedMerge(db2,src,mask2)
src=fvf.rfs(src,db2,"{23321,23461][63350 63940]")

#Dithering down to 8 bit depth
src=core.fmtc.bitdepth(src,bits=8,dmode=7)
#src=awf.SelectRangeEvery(src, every=3000, length=50, offset=1000

src.set_output()

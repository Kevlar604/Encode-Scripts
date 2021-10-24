import vapoursynth as vs
from vapoursynth import core
import awsmfunc as awf
import kagefunc as kgf
from vsutil import depth
import kagefunc as kgf
import lvsfunc as lvf
from adptvgrnMod import *
core.num_threads = 4
core.max_cache_size = 2048

#Importing source
src=core.lsmas.LWLibavSource(r'D:\Test\Il était une fois, une fois.2012.FRA.Complete.Blu-ray.AVC.HDMA\BDMV\STREAM\00002.m2ts')

#Changing fps to sync the subtitles
src=core.std.AssumeFPS(src,fpsnum=24000, fpsden=1000)

#Crop
src=core.std.Crop(src,top=22,bottom=20)

src=depth(src,16)

#Fixing dirty line, not all frames have them the ones at the starting frames(logo scenes) gives the perception of dirty lines but they are not they are just how the frames supposed to be mastered.
fix=awf.bbmod(src,left=1,blur=15,thresh=32000)
src=lvf.rfs(src,fix,(5000,128000))


#Debanding/deblocking 
mask=kgf.retinex_edgemask(src).std.Binarize(20000).std.Maximum().std.Maximum().std.Deflate()
mask2=kgf.retinex_edgemask(src).std.Binarize(30000).std.Maximum().std.Inflate()
db=core.neo_f3kdb.Deband(src)#Moderate deband, the default values are good enough
db2=core.neo_f3kdb.Deband(src,y=200,cb=128,cr=128,range=25)#Strong deband 
db=core.std.MaskedMerge(db,src,mask)
db2=core.std.MaskedMerge(db2,src,mask2)
db2=adptvgrnMod(db2,strength=2,cstrength=1,grain_chroma=True,size=1.25,sharp=50,static=False,luma_scaling=10,seed=3)
src=lvf.rfs(src,db,(0,130211))
src=lvf.rfs(src,db2,(14014,15707))
src=depth(src,8,dither_type='error_diffusion')
src.set_output()

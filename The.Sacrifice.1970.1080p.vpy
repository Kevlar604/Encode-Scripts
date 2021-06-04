import vapoursynth as vs
import havsfunc as hvf
import fvsfunc as fvf
import fag3kdb #Modified it a bit to use newer neo_f3kdb instead of old f3kdb
import vsutil
import kagefunc as kgf 
core = vs.get_core()
 

path=r'D:\Sync\The.Sacrifice.aka.Offret.1986.1080p.JPN.Bluray.Remux.AVC.LPCM.2.0-NTL.mkv'
path1=r'D:\Sync\Offret AKA The Sacrifice 1986 1080p 4K Remastered Blu-ray Remux AVC FLAC 2.0-KINOLORBER2018.mkv'
src=core.lsmas.LWLibavSource(path)
src1=core.lsmas.LWLibavSource(path1)
src=core.std.CropRel(src, left=64,top=0,right=64,bottom=0)
src1=core.std.CropRel(src1, left=64,top=0,right=64,bottom=0)
src=core.std.Trim(src,8138,src.num_frames-1)
src1=core.std.Trim(src1,0,5091)
src=core.fb.FillBorders(src,2,0,1,0,'fillmargins')
src1=core.fb.FillBorders(src1,2,1,1,1,'fillmargins')
video=core.std.Splice([src1,src])
video=core.std.Trim(video,0,210854)
video1=video
v1=video
v2=core.std.ShufflePlanes(video, planes=0, colorfamily=vs.GRAY)
v1=vsutil.depth(v1,16)
v2=vsutil.depth(v2,16)
thresh=(32 * (1 << v2.format.bits_per_sample) - 1) / 255 #this could be written more efficiently 
thresh=32*(1<<(v1.format.bits_per_sample/2)+1). What this does it scales 8 bit clip threshold for 16 bit clip.Here 32 is the 8 bit threshold and we are scaling it to 16bit.
#Laplacian mask which proves more useful for regions in scenes which does not show very high change in gradient especially helpful in debanding skies since it's a partial double derivative instead of finding the slope as in edge masks it computes rate of change of slope.
mask1=core.std.Convolution(v2,[1,1,1,1,-8,1,1,1,1]).std.Binarize(thresh).std.Maximum().std.Inflate().std.Maximum().std.Inflate()
mask2=kgf.retinex_edgemask(v2).std.Maximum().std.Inflate().std.Maximum().std.Inflate()
deband=fag3kdb.Fag3kdb(v1,radiusy=12, radiusc=8, thry=60, thrc=40, grainy=15,grainc=10,keep_tv_range=True)#Deblocking and hard debanding
deband1 = core.neo_f3kdb.Deband(v1, y=45, cb=45, cr=45, range=18, grainy=0,grainc=0, output_depth=16, keep_tv_range=True) #soft deband
deband2= core.neo_f3kdb.Deband(v1, y=48, cb=48, cr=48, range=16, grainy=10,grainc=0, output_depth=16, keep_tv_range=True)#Medium deband
deband1=core.std.MaskedMerge(deband1,v1, mask1)
deband2=core.std.MaskedMerge(deband2,v1, mask2)
deband=vsutil.depth(deband,8,dither_type='error_diffusion')
deband1=vsutil.depth(deband1,8,dither_type='error_diffusion')
deband2=vsutil.depth(deband2,8,dither_type='error_diffusion')
video=fvf.rfs(video,deband1,"[5192 19734][63221 72018][115077 115470][115942 117312][130454 130816][172147 175669][181894 204701][210449 210854]")
video=fvf.rfs(video,deband2,"[72426 115076][115797 115940][117336 128812]")
video=fvf.rfs(video,deband,"[44338 44366][45546 46391][131540 164243]")


video.set_output()

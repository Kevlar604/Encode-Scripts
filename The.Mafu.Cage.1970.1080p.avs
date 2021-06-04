a=FFVideoSource("D:\Sync\The Mafu Cage 1978 1080p BluRay REMUX AVC DTS-HD MA 2.0-Eli7s.mkv")
b=mt_merge(a,a.f3kdb(dither_algo=3,y=32,cb=35,cr=35,grainy=90,grainc=70),a.mt_binarize(36,true),u=3,v=4)
d=ReplaceFramesSimple(a,b,mappings="[17682 18665][31554 31685] [70861 72327]")
e=mt_merge(a,a.f3kdb(dither_algo=3,y=32,cb=35,cr=35,grainy=100,grainc=85),a.mt_binarize(36,true),u=3,v=4)
f= ReplaceFramesSimple(d,e,mappings="[126578 126896] [127545 128582]")
f

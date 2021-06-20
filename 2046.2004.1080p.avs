FFVideoSource("D:\Sync\2046.2004.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-MM.mkv")
crop(0,132,0,-132)
FillBorders(1,0,1,0).BalanceBorders(0,1,1,0)
FixRBr(1,2).FillBorders(0,1,0,0)
FixRBr(814,2)
#FixRBr(815,2)
fix1=last.f3kdb(grainY=10, dynamic_grain=true)                                                 # 1. Light banding
fix2=last.f3kdb(range=25,grainY=10,Y=100)                                                        # 2. Hard banding
fix3=last.f3kdb(Y=45,grainY=0,grainC=0)                                                            # 3. Deblocking
fix4=last.f3kdb(range=10,Y=40,grainY=0,grainC=0,dynamic_grain=True)             # 4. Deblocking faces
ConditionalFilter(last, fix1, "SceneType", "<", "1")
ConditionalFilter(last, fix2, "SceneType", "<", "2")
ConditionalFilter(last, fix3, "SceneType", "<", "3")
ConditionalFilter(last, fix4, "SceneType", "<", "4")
a=ConditionalReader("D:\Sync\fix.txt", "SceneType")

Fix.txt
type int
default 0

R 0 1679 2
R 7944 8040 1
R 9120 9460 1

# ---------------------------------------------------------------- Shanhai scenery: trees, herbs and landmarks of the five mountain classics
M["Jade"] = mat("Jade", "#8fc9b0"); M["JadeDark"] = mat("JadeDark", "#5f9a84"); M["ZheLeaf"] = mat("ZheLeaf", "#3b5a3a"); M["ZheBark"] = mat("ZheBark", "#3a2e28")
M["CassiaLeaf"] = mat("CassiaLeaf", "#4f7f4a"); M["CassiaGold"] = mat("CassiaGold", "#e8b83a"); M["ZhenLeaf"] = mat("ZhenLeaf", "#7fae62"); M["MiguBark"] = mat("MiguBark", "#2a2326")
M["MiguLeaf"] = mat("MiguLeaf", "#c9d8b0"); M["Zhuyu"] = mat("Zhuyu", "#6fa86a"); M["ZhuyuFlower"] = mat("ZhuyuFlower", "#5aa0d8"); M["BlackWater"] = mat("BlackWater", "#1c2230", rough=0.15)
M["Cinnabar"] = mat("Cinnabar", "#b8402a"); M["Twig"] = mat("Twig", "#5a4632"); M["SunGold"] = mat("SunGold", "#ffd36a", rough=0.3, emit="#ffb340", strength=5.0)

P = kit("LanggTree")   # 琅玕树 (槐江之山藏琅玕; 海内西经 琅玕树): a jade tree, branches tipped with glowing jade
cyl("LgTrunk", (0, 0, 0.9), 0.16, 1.8, M["StoneLight"], P, verts=7, r2=0.1, rot=(0.06, 0.04, 0))
for i in range(5):
    a = i * 1.26; rz = a
    cyl(f"LgBranch{i}", (math.cos(a) * 0.35, math.sin(a) * 0.35, 1.9 + i * 0.12), 0.05, 0.9, M["StoneLight"], P, rot=(math.sin(a) * 0.9, -math.cos(a) * 0.9, 0), verts=5, r2=0.03)
    x, y, z = math.cos(a) * 0.85, math.sin(a) * 0.85, 2.3 + i * 0.12
    cone(f"Crystal_Lg{i}T", (x, y, z + 0.14), 0.13, 0.28, M["Crystal"], P, verts=4)
    cone(f"Crystal_Lg{i}B", (x, y, z - 0.14), 0.13, 0.28, M["Crystal"], P, verts=4, rot=(math.pi, 0, 0))
ball("LgCrown", (0, 0, 2.75), 0.32, M["JadeDark"], P, sub=1)
cone("Crystal_LgTop", (0, 0, 3.25), 0.16, 0.36, M["Crystal"], P, verts=4)
ball("Snow_Lg", (0, 0, 2.95), 0.34, M["Snow"], P, scale=(1, 1, 0.35), sub=1)

P = kit("Shatang")   # 沙棠 (昆仑之丘): like a pear tree, yellow flowers, red fruit
cyl("StTrunk", (0, 0, 0.6), 0.13, 1.2, M["PeachTrunk"], P, verts=7, r2=0.09)
for i, (dx, dy, dz, r) in enumerate(((0, 0, 1.55, 0.6), (-0.4, 0.2, 1.8, 0.42), (0.4, -0.2, 1.85, 0.4), (0.05, 0.1, 2.15, 0.36))):
    ball(f"StLeaves{i}", (dx, dy, dz), r, M["Leaves"] if i % 2 == 0 else M["LeavesDark"], P, sub=1)
    ball(f"Snow_St{i}", (dx, dy, dz + r * 0.55), r * 0.9, M["Snow"], P, scale=(1, 1, 0.35), sub=1)
for i in range(6):
    a = i * 1.05
    ball(f"StFlower{i}", (math.cos(a) * 0.55, math.sin(a) * 0.55, 1.65 + (i % 3) * 0.2), 0.07, M["Hay"], P, sub=0)
    ball(f"StFruit{i}", (math.cos(a + 0.5) * 0.45, math.sin(a + 0.5) * 0.45, 1.45 + (i % 2) * 0.25), 0.06, M["Flag"], P, sub=0)

P = kit("ZheTree")   # 柘木 (发鸠之山多柘木): a dark, thorny mulberry
cyl("ZhTrunk", (0, 0, 0.8), 0.17, 1.6, M["ZheBark"], P, verts=7, r2=0.11, rot=(0.1, -0.05, 0))
cyl("ZhBranch", (0.3, -0.1, 1.4), 0.07, 0.8, M["ZheBark"], P, rot=(0.2, 1.1, 0), verts=5)
for i, (dx, dy, dz, r) in enumerate(((0, 0, 1.9, 0.7), (0.6, -0.2, 1.75, 0.45), (-0.45, 0.35, 2.1, 0.45), (0.1, 0.05, 2.4, 0.5))):
    ball(f"ZhLeaves{i}", (dx, dy, dz), r, M["ZheLeaf"], P, scale=(1.2, 1.1, 0.6), sub=1)
    ball(f"Snow_Zh{i}", (dx, dy, dz + r * 0.32), r * 0.95, M["Snow"], P, scale=(1.15, 1.05, 0.25), sub=1)
for i in range(6):
    a = i * 1.05
    cone(f"ZhThorn{i}", (math.cos(a) * 0.16, math.sin(a) * 0.16, 0.5 + i * 0.18), 0.03, 0.18, M["Twig"], P, verts=4, rot=(math.sin(a) * 1.3, -math.cos(a) * 1.3, 0))

P = kit("ZhenTree")   # 桢木 (太山上多桢木): tall privet with an oval crown
cyl("ZnTrunk", (0, 0, 1.1), 0.13, 2.2, M["Trunk"], P, verts=7, r2=0.09)
ball("ZnCrown", (0, 0, 2.9), 0.75, M["ZhenLeaf"], P, scale=(0.9, 0.9, 1.25), sub=1)
ball("ZnCrown2", (0.25, -0.15, 2.5), 0.5, M["Leaves"], P, scale=(1, 1, 0.9), sub=1)
ball("Snow_Zn", (0, 0, 3.55), 0.62, M["Snow"], P, scale=(1, 1, 0.3), sub=1)

P = kit("Cassia")   # 桂 (招摇之山多桂): osmanthus, round crown dotted with gold blossom
cyl("CsTrunk", (0, 0, 0.6), 0.15, 1.2, M["PeachTrunk"], P, verts=7, r2=0.1)
cyl("CsBranch", (-0.25, 0.1, 1.2), 0.06, 0.6, M["PeachTrunk"], P, rot=(-0.3, -0.9, 0), verts=5)
for i, (dx, dy, dz, r) in enumerate(((0, 0, 1.7, 0.72), (-0.5, 0.25, 1.95, 0.5), (0.5, -0.2, 2.0, 0.48), (0.05, 0.1, 2.35, 0.45))):
    ball(f"CsLeaves{i}", (dx, dy, dz), r, M["CassiaLeaf"] if i % 2 == 0 else M["LeavesDark"], P, sub=1)
    ball(f"Snow_Cs{i}", (dx, dy, dz + r * 0.5), r * 0.9, M["Snow"], P, scale=(1, 1, 0.35), sub=1)
for i in range(8):
    a = i * 0.8
    ball(f"CsBloom{i}", (math.cos(a) * (0.55 + (i % 2) * 0.2), math.sin(a) * (0.55 + (i % 2) * 0.2), 1.6 + (i % 4) * 0.22), 0.07, M["CassiaGold"], P, sub=0)

P = kit("Migu")   # 迷榖 (招摇之山): black-veined bark, its flowers shine on all four sides
cyl("MgTrunk", (0, 0, 0.7), 0.14, 1.4, M["MiguBark"], P, verts=7, r2=0.1)
for i in range(4):
    a = i * 1.57 + 0.3
    box(f"MgVein{i}", (math.cos(a) * 0.13, math.sin(a) * 0.13, 0.7), (0.03, 0.03, 1.2), M["Hair"], P, rot=(0, 0, a), bevel=0.0)
for i, (dx, dy, dz, r) in enumerate(((0, 0, 1.8, 0.62), (-0.45, 0.2, 2.0, 0.42), (0.45, -0.2, 2.05, 0.4))):
    ball(f"MgLeaves{i}", (dx, dy, dz), r, M["MiguLeaf"], P, sub=1)
    ball(f"Snow_Mg{i}", (dx, dy, dz + r * 0.55), r * 0.9, M["Snow"], P, scale=(1, 1, 0.35), sub=1)
for i in range(4):
    a = i / 4 * math.tau + 0.4
    ball(f"Lantern_MgFlower{i}", (math.cos(a) * 0.62, math.sin(a) * 0.62, 1.85 + (i % 2) * 0.2), 0.1, M["Lantern"], P, sub=0)   # "其花四照": lit like lanterns at night

P = kit("Zhuyu")   # 祝馀 (招摇之山): leek-like grass with blue flowers, eating it stills hunger
for i in range(6):
    a = i / 6 * math.tau
    cone(f"ZyLeaf{i}", (math.cos(a) * 0.08, math.sin(a) * 0.08, 0.24), 0.04, 0.5, M["Zhuyu"], P, rot=(math.sin(a) * 0.4, -math.cos(a) * 0.4, 0), verts=4)
for i in range(3):
    a = i * 2.1 + 0.5
    cyl(f"ZyStem{i}", (math.cos(a) * 0.05, math.sin(a) * 0.05, 0.35), 0.012, 0.5, M["Zhuyu"], P, verts=4)
    ball(f"ZyFlower{i}", (math.cos(a) * 0.05, math.sin(a) * 0.05, 0.62), 0.05, M["ZhuyuFlower"], P, sub=0)

P = kit("WuluoStatue")   # 武罗 (青要之山): human face, leopard spots, slim waist, white teeth, ear rings; carved in stone
box("WlBase", (0, 0, 0.2), (1.2, 1.2, 0.4), M["Stone"], P)
cone("WlRobe", (0, 0, 1.0), 0.42, 1.2, M["StoneLight"], P, verts=10, r2=0.2)
cyl("WlWaist", (0, 0, 1.6), 0.18, 0.3, M["StoneLight"], P, verts=10)
ball("WlChest", (0, 0, 1.95), 0.3, M["StoneLight"], P, scale=(1.1, 0.8, 0.9), sub=1)
ball("WlHead", (0, 0, 2.45), 0.26, M["StoneLight"], P, sub=1)
box("WlTeeth", (0, -0.22, 2.35), (0.16, 0.06, 0.05), M["Bone"], P, bevel=0.0)
for sx in (-1, 1):
    torus(f"WlEarring{sx}", (sx * 0.28, 0, 2.4), 0.08, 0.02, M["Bronze"], P, rot=(0, math.pi / 2, 0), segs=(10, 4))
for i in range(7):
    a = i * 0.9
    ball(f"WlSpot{i}", (math.cos(a) * 0.32, math.sin(a) * 0.32, 0.8 + (i % 4) * 0.28), 0.06, M["StoneDark"], P, scale=(1, 1, 0.5), sub=0)
box("WlPlaque", (0, -0.62, 0.5), (0.5, 0.06, 0.3), M["Bronze"], P, bevel=0.0)

P = kit("DitaiStone")   # 帝台之棋 (休与之山): five-coloured patterned stones like quail eggs, for praying to the hundred spirits
cyl("DtAltar", (0, 0, 0.2), 0.7, 0.4, M["Stone"], P, verts=8)
cyl("DtAltarTop", (0, 0, 0.44), 0.62, 0.08, M["StoneDark"], P, verts=8)
for i, col in enumerate(("Flag", "CassiaGold", "Jade", "CloakDark", "Bone")):
    a = i / 5 * math.tau
    ball(f"DtEgg{i}", (math.cos(a) * 0.32, math.sin(a) * 0.32, 0.58), 0.12, M[col], P, scale=(0.9, 0.9, 1.25), sub=1)
    ball(f"DtEggSpot{i}", (math.cos(a) * 0.32 + 0.05, math.sin(a) * 0.32 - 0.05, 0.66), 0.045, M["StoneDark"], P, sub=0)
ball("EmberCore_DtCenter", (0, 0, 0.6), 0.1, M["EmberCore"], P, sub=0)

P = kit("KunlunGate")   # 昆仑九门 (海内西经): a gate kept by the Kaiming beast, nine human faces on a tiger's body
for sx in (-1, 1):
    box(f"KgPillar{sx}", (sx * 1.6, 0, 1.9), (0.7, 0.7, 3.8), M["StoneLight"], P)
    box(f"KgCap{sx}", (sx * 1.6, 0, 3.9), (0.9, 0.9, 0.24), M["Jade"], P, bevel=0.02)
box("KgBeam", (0, 0, 4.1), (4.2, 0.6, 0.45), M["StoneLight"], P)
box("KgBeamTrim", (0, 0, 4.4), (4.4, 0.7, 0.14), M["Jade"], P, bevel=0.0)
# the Kaiming beast crouches on the beam: a tiger body with nine faces
ball("KgBeast", (0, 0, 4.85), 0.55, M["Feather"], P, scale=(1.9, 0.8, 0.7), sub=1)
for i in range(9):
    x = -1.2 + i * 0.3
    ball(f"KgFace{i}", (x, -0.42, 4.95 + (i % 2) * 0.1), 0.11, M["Skin"], P, sub=0)
    ball(f"EnemyEye_Kg{i}", (x, -0.52, 4.98 + (i % 2) * 0.1), 0.03, M["EnemyEye"], P, sub=0)
for sx in (-1, 1):
    cyl(f"KgLeg{sx}", (sx * 0.8, -0.2, 4.55), 0.09, 0.4, M["Feather"], P, verts=6)
for i in range(3):
    box(f"KgStep{i}", (0, 0, 0.1 + i * 0.12), (4.4 - i * 0.5, 2.0 - i * 0.4, 0.12), M["Stone"], P, bevel=0.0)

P = kit("Ruoshui")   # 弱水 (昆仑之丘,弱水之渊环之): a black pool ringed with pale stone
cyl("RsWater", (0, 0, 0.05), 2.4, 0.1, M["BlackWater"], P, verts=16)
for i in range(14):
    a = i / 14 * math.tau
    box(f"RsRim{i}", (math.cos(a) * 2.5, math.sin(a) * 2.5, 0.16), (1.15, 0.3, 0.32), M["StoneLight"], P, rot=(0, 0, a + math.pi / 2), bevel=0.0)
for i in range(4):
    a = i * 1.7 + 0.4
    cone(f"Crystal_RsJade{i}", (math.cos(a) * 1.4, math.sin(a) * 1.4, 0.3), 0.1, 0.4, M["Crystal"], P, verts=4)

P = kit("YanhuoCliff")   # 炎火之山 (昆仑之外): a burning cliff, anything thrown in catches fire
for i in range(4):
    x = -1.5 + i * 1.0
    box(f"YhRock{i}", (x, 0, 0.9 + (i % 2) * 0.4), (1.1, 1.2, 1.8 + (i % 2) * 0.8), M["Ash"], P, rot=(0.1 * (i % 2), 0, 0.2 * (i % 3 - 1)), bevel=0.05)
for i in range(6):
    x = -1.6 + i * 0.64
    box(f"Fire_YhCrack{i}", (x, -0.62, 0.5 + (i % 3) * 0.5), (0.12, 0.05, 0.8), M["Fire"], P, rot=(0, 0.3 * (i % 2 - 0.5), 0), bevel=0.0)
    ball(f"Fire_YhFlame{i}", (x, -0.3, 2.0 + (i % 2) * 0.5), 0.16, M["Fire"], P, scale=(1, 0.8, 1.6), sub=0)

P = kit("JingweiPile")   # 精卫填海 (发鸠之山): the heap of twigs and stones the bird drops into the eastern sea
ball("JwMound", (0, 0, 0.25), 1.2, M["StoneDark"], P, scale=(1.4, 1.1, 0.4), sub=1)
for i in range(10):
    a = i * 0.63
    cyl(f"JwTwig{i}", (math.cos(a) * 0.7, math.sin(a) * 0.55, 0.45 + (i % 3) * 0.12), 0.03, 0.9, M["Twig"], P, rot=(0.2 * (i % 2), 1.2, a), verts=4)
    ball(f"JwStone{i}", (math.cos(a + 0.3) * 0.9, math.sin(a + 0.3) * 0.7, 0.35 + (i % 2) * 0.15), 0.14, M["StoneLight"], P, sub=0)

P = kit("XuanFox")   # 玄狐 (幽都之山): a black fox with a bushy tail, one of the black beasts of Youdu
ball("XfBody", (0, 0.05, 0.35), 0.24, M["Hair"], P, scale=(0.8, 1.5, 0.7), sub=1)
ball("XfHead", (0, -0.4, 0.42), 0.14, M["Hair"], P, sub=1)
cone("XfSnout", (0, -0.56, 0.38), 0.07, 0.2, M["Ape"], P, verts=5, rot=(math.pi / 2, 0, 0))
for sx in (-1, 1):
    cone(f"XfEar{sx}", (sx * 0.08, -0.36, 0.58), 0.05, 0.16, M["Hair"], P, verts=4)
    ball(f"EnemyEye_Xf{sx}", (sx * 0.06, -0.5, 0.45), 0.025, M["EnemyEye"], P, sub=0)
    for i, y in enumerate((-0.2, 0.25)):
        cyl(f"XfLeg{sx}{i}", (sx * 0.12, y, 0.12), 0.03, 0.24, M["Hair"], P, verts=4)
ball("XfTail", (0, 0.5, 0.42), 0.16, M["Hair"], P, scale=(0.8, 1.6, 0.8), sub=1)
ball("XfTailTip", (0, 0.75, 0.5), 0.07, M["Bone"], P, sub=0)

P = kit("FusangTree")   # 扶桑 (汤谷上有扶桑,十日所浴): nine suns on the lower branches, one on the top
cyl("FsTrunk", (0, 0, 2.5), 0.45, 5.0, M["Trunk"], P, verts=9, r2=0.25)
cyl("FsTrunk2", (0.2, 0.1, 5.5), 0.22, 2.0, M["Trunk"], P, verts=8, r2=0.12, rot=(-0.1, 0.15, 0))
for i in range(9):
    a = i / 9 * math.tau; r = 1.9 + (i % 2) * 0.5; z = 2.4 + (i % 3) * 0.9
    cyl(f"FsBranch{i}", (math.cos(a) * r * 0.5, math.sin(a) * r * 0.5, z), 0.08, r, M["Trunk"], P, rot=(math.sin(a) * 1.25, -math.cos(a) * 1.25, 0), verts=5, r2=0.04)
    ball(f"FsLeaves{i}", (math.cos(a) * r * 0.85, math.sin(a) * r * 0.85, z + 0.35), 0.5, M["Leaves"] if i % 2 else M["LeavesDark"], P, scale=(1.2, 1.2, 0.6), sub=1)
    ball(f"Fire_FsSun{i}", (math.cos(a) * r, math.sin(a) * r, z + 0.25), 0.26, M["SunGold"], P, sub=1)   # nine suns resting on the lower branches
ball("FsCrown", (0.2, 0.1, 6.6), 0.9, M["LeavesDark"], P, scale=(1.3, 1.3, 0.7), sub=1)
ball("Fire_FsSunTop", (0.2, 0.1, 7.4), 0.42, M["SunGold"], P, sub=1)                              # one sun on the top branch
for i in range(3):
    a = i * 2.1
    box(f"FsRoot{i}", (math.cos(a) * 0.55, math.sin(a) * 0.55, 0.12), (0.7, 0.3, 0.24), M["Trunk"], P, rot=(0, 0, a), bevel=0.0)

P = kit("Tanggu")   # 汤谷 (海外东经): the hot valley where the suns bathe; a steaming spring
cyl("TgWater", (0, 0, 0.08), 2.0, 0.16, M["Water"], P, verts=14)
for i in range(12):
    a = i / 12 * math.tau
    ball(f"TgRock{i}", (math.cos(a) * 2.1, math.sin(a) * 2.1, 0.2), 0.36, M["StoneLight"], P, scale=(1.2, 1, 0.7), sub=0)
for i in range(3):
    a = i * 2.1 + 0.8
    ball(f"Fire_TgGlow{i}", (math.cos(a) * 0.7, math.sin(a) * 0.7, 0.14), 0.2, M["SunGold"], P, scale=(1, 1, 0.3), sub=0)

P = kit("Danxue")   # 丹穴之山 (南山经): red cliff with the phoenix nest on top
for i in range(3):
    ball(f"DxRock{i}", (0.3 * (i - 1), 0.2 * (i % 2), 0.6 + i * 0.45), 0.9 - i * 0.15, M["Cinnabar"], P, scale=(1.3, 1.0, 0.8), sub=1)
cyl("DxNest", (0, 0, 1.95), 0.7, 0.2, M["Twig"], P, verts=10, r2=0.5)
cyl("DxNestHole", (0, 0, 2.08), 0.42, 0.06, M["ZheBark"], P, verts=10)
for i, col in enumerate(("Flag", "CassiaGold", "Jade", "CloakDark", "Blossom")):
    a = i / 5 * math.tau
    ball(f"DxEgg{i}", (math.cos(a) * 0.22, math.sin(a) * 0.22, 2.16), 0.08, M[col], P, scale=(0.9, 0.9, 1.2), sub=0)
for i in range(4):
    a = i * 1.6
    box(f"DxFeather{i}", (math.cos(a) * 0.6, math.sin(a) * 0.6, 2.0), (0.3, 0.06, 0.02), M["Flag" if i % 2 else "CassiaGold"], P, rot=(0, 0, a), bevel=0.0)

P = kit("QingqiuMound")   # 青丘 (南山经): a green-earth mound where the nine-tailed fox dens
ball("QmMound", (0, 0, 0.3), 1.6, M["Jade"], P, scale=(1.5, 1.2, 0.45), sub=1)
ball("QmMound2", (0.6, 0.4, 0.55), 0.8, M["JadeDark"], P, scale=(1.2, 1.0, 0.6), sub=1)
cyl("QmDen", (-0.6, -1.0, 0.35), 0.4, 0.5, M["ZheBark"], P, rot=(math.pi / 2, 0, 0.5), verts=10)
for i in range(3):
    a = i * 2.1
    cone(f"QmBone{i}", (math.cos(a) * 1.1, math.sin(a) * 0.9, 0.3), 0.04, 0.4, M["Bone"], P, verts=4, rot=(0.4, 0.2, a))
for i in range(5):
    a = i * 1.3
    cone(f"QmGrass{i}", (math.cos(a) * 1.3, math.sin(a) * 1.1, 0.5), 0.05, 0.4, M["Zhuyu"], P, verts=4, rot=(math.sin(a) * 0.3, -math.cos(a) * 0.3, 0))

P = kit("Jingwei")   # 精卫: crow-shaped, patterned head, white beak, red feet, carrying a twig to the sea
ball("JwBody", (0, 0, 0), 0.18, M["Hair"], P, scale=(0.75, 1.5, 0.7), sub=1)
ball("JwHead", (0, -0.3, 0.1), 0.11, M["Hair"], P, sub=0)
box("JwHeadMark", (0, -0.3, 0.2), (0.08, 0.14, 0.03), M["Bone"], P, bevel=0.0)
cone("JwBeak", (0, -0.46, 0.08), 0.03, 0.16, M["Bone"], P, verts=4, rot=(math.pi / 2, 0, 0))
for sx in (-1, 1):
    box(f"JwWing{sx}", (sx * 0.42, 0.0, 0.04), (0.7, 0.34, 0.03), M["Hair"], P, rot=(0, sx * 0.15, 0), bevel=0.0)
    cyl(f"JwLeg{sx}", (sx * 0.05, 0.1, -0.16), 0.012, 0.22, M["Flag"], P, verts=4, rot=(-0.3, 0, 0))
cyl("JwTwig", (0, -0.4, -0.12), 0.02, 0.6, M["Twig"], P, rot=(0, math.pi / 2, 0), verts=4)
box("JwTail", (0, 0.32, 0.02), (0.16, 0.24, 0.03), M["Hair"], P, bevel=0.0)


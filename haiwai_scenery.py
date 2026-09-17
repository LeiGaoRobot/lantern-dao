# ---------------------------------------------------------------- Haiwai scenery: the lands beyond the seas (海外四經)
M["TigerStone"] = mat("TigerStone", "#c9a05a"); M["TigerStripe"] = mat("TigerStripe", "#3a2a1e"); M["Cypress"] = mat("Cypress", "#2f5f4a"); M["CypressDark"] = mat("CypressDark", "#224638")
M["XunhuaPetal"] = mat("XunhuaPetal", "#f3d9e6"); M["XunhuaStem"] = mat("XunhuaStem", "#6f9a5a"); M["MarshWater"] = mat("MarshWater", "#3a4a36", rough=0.2); M["BloodEarth"] = mat("BloodEarth", "#5a2a26")
M["SnakeGreen"] = mat("SnakeGreen", "#3f9a5a"); M["SnakeYellow"] = mat("SnakeYellow", "#d8b23a"); M["GiantSkin"] = mat("GiantSkin", "#c49a72")
M["TombEarth"] = mat("TombEarth", "#9a8a62"); M["HullWood"] = mat("HullWood", "#a8794a"); M["Mulberry"] = mat("Mulberry", "#4f7a3f"); M["Peach"] = mat("Peach", "#f0a8a0"); M["FruitGold"] = mat("FruitGold", "#e8a23a")

P = kit("TigerStatue")   # 君子國: 使二文虎在旁 — a striped tiger seated on a plinth
box("TsPlinth", (0, 0, 0.15), (1.1, 1.5, 0.3), M["StoneLight"], P, bevel=0.03)
ball("TsHaunch", (0, 0.3, 0.75), 0.45, M["TigerStone"], P, scale=(1.0, 1.15, 1.0), sub=1)
ball("TsChest", (0, -0.2, 1.05), 0.38, M["TigerStone"], P, scale=(0.95, 0.9, 1.2), sub=1)
ball("TsHead", (0, -0.4, 1.6), 0.3, M["TigerStone"], P, sub=1)
box("TsMuzzle", (0, -0.64, 1.52), (0.26, 0.2, 0.18), M["Bone"], P, bevel=0.03)
for sx in (-1, 1):
    cone(f"TsEar{sx}", (sx * 0.2, -0.32, 1.88), 0.08, 0.14, M["TigerStone"], P, verts=4)
    cyl(f"TsForeleg{sx}", (sx * 0.22, -0.4, 0.62), 0.1, 0.7, M["TigerStone"], P, verts=6)
    ball(f"Lantern_TsEye{sx}", (sx * 0.11, -0.66, 1.66), 0.035, M["Lantern"], P, sub=0)
for i in range(5):
    box(f"TsStripe{i}", (0, 0.05 + i * 0.13, 1.18 - i * 0.09), (0.8, 0.05, 0.06), M["TigerStripe"], P, rot=(0.5, 0, 0), bevel=0.0)
cyl("TsTail", (0.3, 0.75, 0.5), 0.05, 0.8, M["TigerStone"], P, rot=(-1.1, 0, 0.5), verts=5)

P = kit("Xunhua")   # 薰華草: 朝生夕死 — it lives only by day (the web hides the whole Xunhua set at night)
for i in range(5):
    a = i / 5 * math.tau
    cyl(f"XhStem{i}", (math.cos(a) * 0.12, math.sin(a) * 0.12, 0.2), 0.015, 0.4, M["XunhuaStem"], P, verts=4, rot=(math.sin(a) * 0.3, -math.cos(a) * 0.3, 0))
    ball(f"XhBloom{i}", (math.cos(a) * 0.2, math.sin(a) * 0.2, 0.42), 0.07, M["XunhuaPetal"], P, scale=(1, 1, 0.6), sub=0)
ball("XhBloomTop", (0, 0, 0.5), 0.09, M["XunhuaPetal"], P, scale=(1, 1, 0.6), sub=0)

P = kit("SanzhuTree")   # 三株樹: 其為樹如柏,葉皆為珠 — a cypress whose leaves are all pearls
cyl("SzTrunk", (0, 0, 0.9), 0.16, 1.8, M["Trunk"], P, verts=7, r2=0.09)
for i, (z, r) in enumerate(((1.3, 0.8), (2.0, 0.62), (2.7, 0.44), (3.3, 0.26))):
    cone(f"SzTier{i}", (0, 0, z), r, 0.95, M["Cypress"] if i % 2 == 0 else M["CypressDark"], P, verts=7)
    for k in range(6 - i):
        a = k / (6 - i) * math.tau + i * 0.5
        ball(f"Crystal_SzPearl{i}{k}", (math.cos(a) * r * 0.85, math.sin(a) * r * 0.85, z - 0.3), 0.07, M["Crystal"], P, sub=0)

P = kit("DishanMound")   # 狄山: 帝堯葬于陽,帝嚳葬于陰 — a twin burial mound with a stele on each side
ball("DsMoundA", (-0.9, 0, 0.0), 1.5, M["TombEarth"], P, scale=(1, 1, 0.6), sub=2)
ball("DsMoundB", (1.1, 0.3, 0.0), 1.2, M["TombEarth"], P, scale=(1, 1, 0.55), sub=2)
for sx, y in ((-1, -1.7), (1, 1.7)):
    box(f"DsStele{sx}", (sx * 0.2, y, 0.55), (0.5, 0.14, 1.1), M["Stone"], P, bevel=0.02)
    box(f"DsSteleCap{sx}", (sx * 0.2, y, 1.15), (0.62, 0.2, 0.12), M["StoneDark"], P, bevel=0.02)
for i in range(4):
    a = i / 4 * math.tau + 0.5
    ball(f"DsGrass{i}", (math.cos(a) * 1.0 - 0.3, math.sin(a) * 0.8, 0.8), 0.22, M["Grass"], P, scale=(1, 1, 0.5), sub=0)

P = kit("ShouhuaField")   # 壽華之野: 羿與鑿齒戰,羿射殺之 — spent arrows and a split shield left on the field
cyl("ShShield", (0.2, 0, 0.12), 0.7, 0.08, M["Timber"], P, verts=12, rot=(0.15, 0.1, 0))
box("ShSplit", (0.2, 0, 0.18), (0.06, 1.3, 0.04), M["StoneDark"], P, rot=(0, 0, 0.4), bevel=0.0)
for i, (x, y, tilt) in enumerate(((-0.6, 0.3, 0.35), (0.5, -0.5, -0.3), (0.2, 0.1, 0.15), (-0.2, -0.7, 0.5), (0.9, 0.5, -0.45))):
    cyl(f"ShArrow{i}", (x, y, 0.45), 0.02, 0.9, M["Timber"], P, verts=4, rot=(tilt, tilt * 0.5, 0))
    box(f"ShFletch{i}", (x - tilt * 0.12, y + tilt * 0.35, 0.86), (0.1, 0.02, 0.14), M["Flag"], P, rot=(tilt, 0, 0), bevel=0.0)

P = kit("DengbaoPeak")   # 登葆山: 群巫所從上下也 — a steep peak with the shamans' ladder
cone("DbPeak", (0, 0, 2.2), 1.8, 4.4, M["Stone"], P, verts=7)
cone("DbShoulder", (0.9, 0.5, 1.0), 1.2, 2.0, M["StoneDark"], P, verts=6)
ball("DbCloud", (-0.3, 0.2, 3.2), 0.8, M["Mist"], P, scale=(1.6, 1.2, 0.35), sub=1)
for i in range(9):
    box(f"DbRung{i}", (-0.55 + i * 0.05, -1.05 + i * 0.1, 0.4 + i * 0.42), (0.5, 0.06, 0.05), M["Timber"], P, rot=(0.2, 0, 0.1), bevel=0.0)
for sx in (-1, 1):
    cyl(f"DbRail{sx}", (-0.35 + sx * 0.25, -0.62, 2.1), 0.03, 4.0, M["Timber"], P, verts=4, rot=(0.24, 0.1, 0))
box("Crystal_DbAltar", (0, 0, 4.45), (0.3, 0.3, 0.1), M["Crystal"], P, bevel=0.0)

P = kit("NvchouCorpse")   # 女丑之屍: 十日炙殺之,以右手鄣其面,十日居上 — a figure on a hill, a hand over the face, ten suns above
ball("NcHill", (0, 0, 0.0), 1.6, M["TombEarth"], P, scale=(1, 1, 0.5), sub=2)
cone("NcRobe", (0, 0, 1.2), 0.4, 1.1, M["Cloak"], P, verts=8, r2=0.2)
ball("NcHead", (0, -0.02, 1.95), 0.18, M["Skin"], P, sub=1)
cyl("NcArm", (-0.15, -0.16, 1.85), 0.05, 0.5, M["Cloak"], P, verts=5, rot=(0.9, 0.5, 0))   # the right hand raised to shield the face
box("NcHair", (0, 0.08, 2.0), (0.3, 0.26, 0.4), M["Hair"], P, bevel=0.02)
for i in range(10):
    a = i / 10 * math.tau
    ball(f"Fire_NcSun{i}", (math.cos(a) * 1.3, math.sin(a) * 1.3, 3.4 + (i % 2) * 0.25), 0.16, M["SunGold"], P, sub=0)

P = kit("XuanyuanMound")   # 軒轅之丘: 其丘方,四蛇相繞 — a square mound with four snakes coiled about it
box("XyBase", (0, 0, 0.4), (3.2, 3.2, 0.8), M["TombEarth"], P, bevel=0.1)
box("XyTop", (0, 0, 1.0), (2.2, 2.2, 0.5), M["StoneLight"], P, bevel=0.08)
box("Crystal_XySeal", (0, 0, 1.28), (0.6, 0.6, 0.06), M["Crystal"], P, bevel=0.0)
for k in range(4):
    a0 = k / 4 * math.tau
    for i in range(9):
        a = a0 + i * 0.17
        ball(f"XySnake{k}{i}", (math.cos(a) * 2.0, math.sin(a) * 2.0, 0.22 + i * 0.05), 0.16 - i * 0.008, M["SnakeGreen" if k % 2 == 0 else "SnakeYellow"], P, sub=0)
    ah = a0 + 9 * 0.17
    ball(f"XySnakeHead{k}", (math.cos(ah) * 1.95, math.sin(ah) * 1.95, 0.72), 0.17, M["SnakeGreen" if k % 2 == 0 else "SnakeYellow"], P, scale=(1, 1.4, 0.8), sub=0)

P = kit("GonggongTerrace")   # 共工之臺: 臺四方,隅有一蛇,虎色,首衝南方 — a square terrace, a tiger-coloured snake at each corner, heads to the south
box("GgBase", (0, 0, 0.5), (3.6, 3.6, 1.0), M["StoneDark"], P, bevel=0.06)
box("GgMid", (0, 0, 1.3), (2.8, 2.8, 0.7), M["Stone"], P, bevel=0.05)
box("GgTop", (0, 0, 1.85), (2.0, 2.0, 0.4), M["StoneLight"], P, bevel=0.04)
for i in range(5):
    box(f"GgStep{i}", (0, -1.95 - i * 0.22, 0.85 - i * 0.18), (1.2, 0.24, 0.16), M["Stone"], P, bevel=0.0)
for sx in (-1, 1):
    for sy in (-1, 1):
        for i in range(5):
            ball(f"GgSnake{sx}{sy}{i}", (sx * 1.7, sy * 1.7 - i * 0.16, 1.05 + i * 0.02), 0.13, M["TigerStone" if i % 2 == 0 else "TigerStripe"], P, sub=0)
        ball(f"GgSnakeHead{sx}{sy}", (sx * 1.7, sy * 1.7 - 0.9, 1.2), 0.15, M["TigerStone"], P, scale=(1, 1.5, 0.8), sub=0)   # -Y is south on the island map
box("EmberCore_GgFire", (0, 0, 2.1), (0.5, 0.5, 0.12), M["EmberCore"], P, bevel=0.0)

P = kit("DenglinTree")   # 鄧林: 夸父棄其杖,化為鄧林 — a grove that grew from a staff
cyl("DlTrunk", (0, 0, 0.8), 0.13, 1.6, M["PeachTrunk"], P, verts=6, r2=0.08, rot=(0, 0.08, 0))
for i, (dx, dy, dz, r) in enumerate(((0, 0, 1.9, 0.62), (0.45, 0.1, 1.6, 0.42), (-0.4, -0.2, 1.65, 0.4), (0.1, 0.4, 2.3, 0.36))):
    ball(f"DlLeaves{i}", (dx, dy, dz), r, M["Leaves"] if i % 2 == 0 else M["LeavesDark"], P, sub=1)
for i in range(6):
    a = i / 6 * math.tau
    ball(f"DlPeach{i}", (math.cos(a) * 0.55, math.sin(a) * 0.55, 1.75 + (i % 3) * 0.2), 0.07, M["Peach"], P, sub=0)

P = kit("Xunmu")   # 尋木: 長千里 — a tree far taller than the rest
cyl("XmTrunk", (0, 0, 3.0), 0.3, 6.0, M["Trunk"], P, verts=8, r2=0.14)
for i in range(5):
    a = i * 1.3
    cyl(f"XmBranch{i}", (math.cos(a) * 0.6, math.sin(a) * 0.6, 3.2 + i * 0.6), 0.06, 1.4, M["Trunk"], P, verts=5, rot=(math.sin(a) * 1.0, -math.cos(a) * 1.0, 0))
    ball(f"XmLeaves{i}", (math.cos(a) * 1.2, math.sin(a) * 1.2, 3.6 + i * 0.6), 0.6, M["Pine"] if i % 2 else M["Leaves"], P, scale=(1.2, 1.2, 0.7), sub=1)
ball("XmCrown", (0, 0, 6.3), 0.9, M["Leaves"], P, scale=(1.2, 1.2, 0.8), sub=1)

P = kit("Sansang")   # 三桑無枝: 其木長百仞,無枝 — three tall mulberries with no branches, only a tuft at the top
for k, (x, y, h) in enumerate(((0, 0, 4.6), (0.7, 0.3, 4.0), (-0.5, 0.6, 4.3))):
    cyl(f"SsTrunk{k}", (x, y, h / 2), 0.13, h, M["ZheBark"], P, verts=6, r2=0.08)
    ball(f"SsTuft{k}", (x, y, h + 0.15), 0.4, M["Mulberry"], P, scale=(1.2, 1.2, 0.7), sub=1)

P = kit("MarshPool")   # 相柳之所抵,厥為澤谿 — a fouled marsh pool
cyl("MpWater", (0, 0, 0.03), 2.6, 0.06, M["MarshWater"], P, verts=14)
for i in range(9):
    a = i / 9 * math.tau
    ball(f"MpBank{i}", (math.cos(a) * 2.6, math.sin(a) * 2.6, 0.08), 0.42, M["Mud"], P, scale=(1.2, 1.0, 0.45), sub=0)
for i in range(4):
    a = i / 4 * math.tau + 0.6
    box(f"EmberCore_MpReek{i}", (math.cos(a) * 1.2, math.sin(a) * 1.2, 0.08), (0.5, 0.18, 0.03), M["EmberCore"], P, rot=(0, 0, a), bevel=0.0)
    cyl(f"MpReed{i}", (math.cos(a + 0.7) * 2.1, math.sin(a + 0.7) * 2.1, 0.5), 0.02, 1.0, M["Reed"], P, verts=4)

P = kit("DarenBoat")   # 大人國: 為人大,坐而削船 — a giant seated, whittling the hull of a boat
ball("DrTorso", (0, 0.6, 1.3), 0.8, M["GiantSkin"], P, scale=(1.1, 0.9, 1.2), sub=2)
ball("DrHead", (0, 0.35, 2.55), 0.45, M["GiantSkin"], P, sub=1)
box("DrHair", (0, 0.5, 2.85), (0.8, 0.7, 0.3), M["Hair"], P, bevel=0.05)
for sx in (-1, 1):
    cyl(f"DrThigh{sx}", (sx * 0.5, -0.3, 0.45), 0.28, 1.5, M["GiantSkin"], P, verts=7, rot=(math.pi / 2 - 0.15, 0, 0))
    cyl(f"DrArm{sx}", (sx * 0.85, -0.1, 1.35), 0.17, 1.2, M["GiantSkin"], P, verts=6, rot=(0.9, 0, 0))
box("DrHull", (0, -1.5, 0.45), (1.0, 2.8, 0.5), M["HullWood"], P, bevel=0.12)
box("DrHullHollow", (0, -1.5, 0.66), (0.7, 2.3, 0.12), M["Timber"], P, bevel=0.0)
box("DrAdze", (0.85, -0.85, 0.95), (0.08, 0.5, 0.08), M["Steel"], P, rot=(0.6, 0, 0), bevel=0.0)
for i in range(5):
    box(f"DrChip{i}", (-0.9 + i * 0.4, -2.2 + (i % 2) * 0.5, 0.04), (0.2, 0.08, 0.03), M["WoodLight"], P, rot=(0, 0, i * 0.7), bevel=0.0)

P = kit("ChaoyangValley")   # 朝陽之谷: 在兩水間 — two streams, the valley of the water lord between them
for sx in (-1, 1):
    box(f"CyStream{sx}", (sx * 1.6, 0, 0.03), (0.9, 5.0, 0.06), M["Water"], P, bevel=0.0, rot=(0, 0, sx * 0.12))
    for i in range(4):
        ball(f"CyStone{sx}{i}", (sx * (1.0 + (i % 2) * 1.2), -2.0 + i * 1.3, 0.12), 0.3, M["Stone"], P, scale=(1.2, 1, 0.6), sub=0)
ball("CyKnoll", (0, 0, 0.0), 1.0, M["Moss"], P, scale=(1, 1.8, 0.4), sub=1)
box("Crystal_CyShrine", (0, 0, 0.55), (0.3, 0.3, 0.5), M["Crystal"], P, bevel=0.03)

P = kit("FruitTree")   # 甘柤、甘華,百果所生
cyl("FtTrunk", (0, 0, 0.7), 0.12, 1.4, M["Trunk"], P, verts=6, r2=0.08)
for i, (dx, dy, dz, r) in enumerate(((0, 0, 1.7, 0.6), (0.4, 0.15, 1.45, 0.4), (-0.35, -0.2, 1.5, 0.42))):
    ball(f"FtLeaves{i}", (dx, dy, dz), r, M["Mulberry"] if i % 2 == 0 else M["Leaves"], P, sub=1)
for i in range(7):
    a = i / 7 * math.tau
    ball(f"FtFruit{i}", (math.cos(a) * 0.52, math.sin(a) * 0.52, 1.5 + (i % 3) * 0.18), 0.075, M["FruitGold"], P, sub=0)


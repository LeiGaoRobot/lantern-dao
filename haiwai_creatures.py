# ---------------------------------------------------------------- enemies (Z up; front = -Y) — Beyond the Seas (海外四經), same rig contract as the mountain kit
M["BirdBlue"] = mat("BirdBlue", "#3f7f8f"); M["BirdRed"] = mat("BirdRed", "#c8452e"); M["PigBlack"] = mat("PigBlack", "#26242a"); M["PigSnout"] = mat("PigSnout", "#4a4048")
M["HorseWhite"] = mat("HorseWhite", "#ece8de"); M["HorseMane"] = mat("HorseMane", "#b9b2a4"); M["XlBody"] = mat("XlBody", "#3f8a7a"); M["XlBelly"] = mat("XlBelly", "#a9c9a8")
M["SnakeRed"] = mat("SnakeRed", "#c8402e"); M["WuRobe"] = mat("WuRobe", "#5a3f6a")
M["TwBlue"] = mat("TwBlue", "#3f6f8a"); M["TwYellow"] = mat("TwYellow", "#d2b04a"); M["BlackBeast"] = mat("BlackBeast", "#1f1d22")


def eyes(P, y, z, sep=0.12, r=0.05):
    for sx in (-1, 1):
        ball(f"EnemyEye_{sx}", (sx * sep, y, z), r, M["EnemyEye"], P, sub=0)


def snake(prefix, parent, start, material, n=5, step=(0, -0.16, 0.06), r=0.06, wave=0.08):
    """a little snake held in a hand: a chain of overlapping balls that ends in a head"""
    x, y, z = start
    for i in range(n):
        ball(f"{prefix}{i}", (x + math.sin(i * 1.3) * wave, y + step[1] * i, z + step[2] * i), r * (1.0 - i * 0.06), material, parent, sub=0)
    ball(f"{prefix}Head", (x + math.sin(n * 1.3) * wave, y + step[1] * n, z + step[2] * n), r * 1.25, material, parent, scale=(1, 1.4, 0.8), sub=0)


def face(prefix, parent, loc, r=0.2, skin="Skin"):
    """a small human face: head ball, brow, glowing eyes"""
    x, y, z = loc
    ball(f"{prefix}Face", (x, y, z), r, M[skin], parent, scale=(0.9, 1.0, 1.05), sub=1)
    box(f"{prefix}Hair", (x, y + r * 0.35, z + r * 0.55), (r * 1.6, r * 1.4, r * 0.7), M["Hair"], parent, bevel=0.0)
    for sx in (-1, 1):
        ball(f"EnemyEye_{prefix}{sx}", (x + sx * r * 0.38, y - r * 0.82, z + r * 0.12), r * 0.2, M["EnemyEye"], parent, sub=0)


P = kit("Wisp")   # 比翼鳥: one green-blue, one red, flying wing to wing (海外南經)
for sx, col, dark in ((-1, "BirdBlue", "FeatherDark"), (1, "BirdRed", "Flag")):
    ball(f"ByBody{sx}", (sx * 0.17, 0.05, 0.5), 0.17, M[col], P, scale=(0.85, 1.3, 0.85), sub=1)
    ball(f"ByHead{sx}", (sx * 0.17, -0.24, 0.6), 0.1, M[col], P, sub=1)
    cone(f"ByBeak{sx}", (sx * 0.17, -0.37, 0.59), 0.03, 0.12, M["Belt"], P, verts=4, rot=(math.pi / 2, 0, 0))
    ball(f"EnemyEye_By{sx}", (sx * 0.23, -0.3, 0.63), 0.03, M["EnemyEye"], P, sub=0)
    box(f"ByWing{sx}", (sx * 0.5, 0.05, 0.56), (0.5, 0.3, 0.04), M[dark], P, rot=(0, sx * 0.4, 0), bevel=0.0)     # each bird keeps only its outer wing
    box(f"ByTail{sx}", (sx * 0.17, 0.4, 0.5), (0.08, 0.3, 0.03), M[dark], P, rot=(-0.4, 0, sx * 0.2), bevel=0.0)
box("ByJoin", (0, 0.05, 0.54), (0.12, 0.22, 0.04), M["Bone"], P, bevel=0.0)                                       # the wings that meet in the middle

P = kit("Cinder")   # 并封: shaped like a pig, a head at the front and a head at the back, black (海外西經)
ball("BfBody", (0, 0, 0.5), 0.42, M["PigBlack"], P, scale=(0.95, 1.35, 0.85), sub=1)
for sy in (-1, 1):
    ball(f"BfHead{sy}", (0, sy * 0.56, 0.5), 0.25, M["PigBlack"], P, scale=(0.9, 1.0, 0.85), sub=1)
    box(f"BfSnout{sy}", (0, sy * 0.82, 0.42), (0.2, 0.16, 0.16), M["PigSnout"], P, bevel=0.03)
    for sx in (-1, 1):
        cone(f"BfTusk{sy}{sx}", (sx * 0.1, sy * 0.84, 0.36), 0.03, 0.14, M["Fang"], P, verts=4, rot=(-0.6 * sy, 0, 0))
        cone(f"BfEar{sy}{sx}", (sx * 0.2, sy * 0.46, 0.72), 0.07, 0.16, M["PigBlack"], P, verts=4, rot=(-0.3 * sy, sx * 0.5, 0))
        ball(f"EnemyEye_Bf{sy}{sx}", (sx * 0.11, sy * 0.72, 0.6), 0.045, M["EnemyEye"], P, sub=0)
for sx in (-1, 1):
    for i, y in enumerate((-0.28, 0.28)):
        box(f"BfLeg{sx}{i}", (sx * 0.24, y, 0.12), (0.14, 0.16, 0.24), M["PigSnout"], P, bevel=0.0)
for i in range(5):
    cone(f"BfBristle{i}", (0, -0.4 + i * 0.2, 0.86), 0.05, 0.2, M["Bristle"], P, verts=4)

P = kit("Crawler")   # 讙頭國: a human face, wings, a bird's beak, catching fish (海外南經) — the Leg buckets are its wings
ball("HtBody", (0, 0.05, 0.42), 0.24, M["FeatherDark"], P, scale=(0.9, 1.2, 1.0), sub=1)
ball("HtHead", (0, -0.3, 0.62), 0.17, M["Skin"], P, scale=(0.9, 1.0, 1.05), sub=1)
box("HtHair", (0, -0.24, 0.76), (0.28, 0.24, 0.08), M["Hair"], P, bevel=0.0)
cone("HtBeak", (0, -0.5, 0.58), 0.05, 0.2, M["Belt"], P, verts=4, rot=(math.pi / 2, 0, 0))
eyes(P, -0.43, 0.67, sep=0.07, r=0.035)
for sx in (-1, 1):
    box(f"Leg{sx}0", (sx * 0.42, -0.1, 0.5), (0.6, 0.3, 0.03), M["Feather"], P, rot=(0, sx * 0.35, 0.15), bevel=0.0)
    box(f"Leg{sx}1", (sx * 0.4, 0.22, 0.47), (0.5, 0.26, 0.03), M["FeatherDark"], P, rot=(0, sx * 0.35, -0.15), bevel=0.0)
    box(f"Leg2{sx}0", (sx * 0.72, -0.1, 0.56), (0.28, 0.14, 0.02), M["Feather"], P, rot=(0, sx * 0.6, 0.15), bevel=0.0)
    box(f"Leg2{sx}1", (sx * 0.66, 0.22, 0.52), (0.24, 0.12, 0.02), M["FeatherDark"], P, rot=(0, sx * 0.6, -0.15), bevel=0.0)
    cyl(f"HtFoot{sx}", (sx * 0.09, 0.05, 0.12), 0.025, 0.24, M["Belt"], P, verts=4)
ball("HtFish", (0, -0.36, 0.3), 0.09, M["Steel"], P, scale=(0.6, 1.6, 0.8), sub=0)                               # 方捕魚: the fish it has just caught
box("EmberCore_HtFish", (0, -0.36, 0.34), (0.03, 0.2, 0.02), M["EmberCore"], P, bevel=0.0)

P = kit("Spitter")   # 厭火國: a beast's body, black, fire coming out of its mouth (海外南經)
ball("YhBody", (0, 0.1, 0.6), 0.4, M["BlackBeast"], P, scale=(0.9, 1.2, 0.95), sub=1)
ball("YhChest", (0, -0.25, 0.85), 0.32, M["BlackBeast"], P, sub=1)
ball("YhHead", (0, -0.5, 1.15), 0.24, M["BlackBeast"], P, scale=(0.95, 1.05, 0.95), sub=1)
box("YhJaw", (0, -0.7, 1.05), (0.26, 0.2, 0.1), M["PigSnout"], P, bevel=0.02)
ball("Fire_Maw", (0, -0.8, 1.1), 0.1, M["Fire"], P, sub=0)                                                     # 生火出其口中
cone("Fire_YhTongue", (0, -0.98, 1.1), 0.06, 0.3, M["Fire"], P, verts=5, rot=(math.pi / 2, 0, 0))
eyes(P, -0.68, 1.24, sep=0.1, r=0.045)
for sx in (-1, 1):
    cyl(f"YhArm{sx}", (sx * 0.36, -0.3, 0.45), 0.09, 0.9, M["BlackBeast"], P, verts=6, rot=(0.25, 0, 0))
    ball(f"YhFist{sx}", (sx * 0.36, -0.42, 0.06), 0.12, M["PigSnout"], P, sub=0)
    cyl(f"YhLeg{sx}", (sx * 0.26, 0.4, 0.3), 0.11, 0.6, M["BlackBeast"], P, verts=6)
    cone(f"YhEar{sx}", (sx * 0.2, -0.42, 1.38), 0.06, 0.16, M["BlackBeast"], P, verts=4)
cyl("YhTail", (0, 0.7, 0.75), 0.05, 0.7, M["BlackBeast"], P, rot=(-0.9, 0, 0), verts=5, r2=0.02)

P = kit("Brute")   # 駮: shaped like a white horse, saw teeth, eats tigers and leopards (海外北經)
ball("BoBody", (0, 0.15, 1.15), 0.62, M["HorseWhite"], P, scale=(0.8, 1.6, 0.85), sub=2)
cyl("BoNeck", (0, -0.85, 1.6), 0.24, 0.9, M["HorseWhite"], P, rot=(0.75, 0, 0), verts=8, r2=0.18)
ball("BoHead", (0, -1.3, 2.0), 0.26, M["HorseWhite"], P, scale=(0.8, 1.5, 0.85), sub=1)
box("BoMuzzle", (0, -1.62, 1.88), (0.26, 0.34, 0.24), M["HorseMane"], P, bevel=0.03)
for i in range(6):
    cone(f"BoTooth{i}", (-0.1 + i * 0.04, -1.78, 1.8 - (i % 2) * 0.02), 0.025, 0.12, M["Fang"], P, verts=4, rot=(math.pi if i % 2 else 0, 0, 0))   # 鋸牙
box("EmberCore_BoMouth", (0, -1.76, 1.82), (0.2, 0.04, 0.05), M["EmberCore"], P, bevel=0.0)
eyes(P, -1.42, 2.1, sep=0.17, r=0.05)
for i in range(6):
    box(f"BoMane{i}", (0, -1.15 + i * 0.22, 2.05 - i * 0.12), (0.06, 0.22, 0.3), M["HorseMane"], P, rot=(0.75, 0, 0), bevel=0.0)
for sx in (-1, 1):
    cone(f"BoEar{sx}", (sx * 0.14, -1.16, 2.28), 0.05, 0.18, M["HorseWhite"], P, verts=4)
    for i, y in enumerate((-0.6, 0.85)):
        cyl(f"BoLeg{sx}{i}", (sx * 0.3, y, 0.5), 0.1, 1.0, M["HorseWhite"], P, verts=6, r2=0.07)
        box(f"BoHoof{sx}{i}", (sx * 0.3, y, 0.06), (0.2, 0.24, 0.12), M["Horn"], P, bevel=0.0)
for k in range(3):
    box(f"BoTail{k}", ((k - 1) * 0.06, 1.25, 1.0 - k * 0.05), (0.06, 0.12, 0.9), M["HorseMane"], P, rot=(-0.35, 0, (k - 1) * 0.12), bevel=0.0)

# Boss: 相柳 — nine human-faced heads on a blue-green serpent body; where it goes the ground turns to marsh (海外北經)
P = kit("Warden")
wb = empty("W_Body"); wb.parent = P
for i in range(7):                                   # the coiled body, a spiral of overlapping segments rising to the necks
    a = i * 0.9
    r = 1.15 - i * 0.1
    ball(f"XlCoil{i}", (math.cos(a) * r * 0.8, 0.35 + math.sin(a) * r * 0.8, 0.45 + i * 0.3), 0.62 - i * 0.03, M["XlBody"] if i % 2 == 0 else M["XlBelly"], wb, scale=(1, 1, 0.75), sub=1)
cyl("XlTrunk", (0, 0, 2.2), 0.62, 1.4, M["XlBody"], wb, verts=12, r2=0.5)
cyl("XlBellyPlate", (0, -0.42, 2.2), 0.34, 1.3, M["XlBelly"], wb, verts=8, r2=0.28)
cone("XlTailTip", (-1.2, 1.4, 0.35), 0.3, 1.2, M["XlBody"], wb, verts=6, rot=(-math.pi / 2, 0, 0.9))
for i in range(5):
    a = i / 5 * math.tau
    box(f"EmberCore_WVein{i}", (math.cos(a) * 0.6, math.sin(a) * 0.6, 1.7 + (i % 2) * 0.5), (0.24, 0.05, 0.12), M["EmberCore"], wb, rot=(0, 0, a + 0.3), bevel=0.0)   # the reeking blood under the scales
wh = empty("W_Head"); wh.parent = wb; wh.location = (0, 0, 2.9)
for k, (dx, dz, lean) in enumerate(((0, 0.95, 0.0), (-0.5, 0.7, -0.35), (0.5, 0.7, 0.35))):     # three middle heads
    cyl(f"XlNeckC{k}", (dx * 0.5, -0.15, dz * 0.5), 0.17, 1.0, M["XlBody"], wh, verts=7, rot=(0.25, lean, 0))
    face(f"WC{k}", wh, (dx, -0.35, dz + 0.1), r=0.27)
wl = empty("W_ArmL"); wl.parent = wb; wl.location = (-0.75, 0, 2.6)
wr = empty("W_ArmR"); wr.parent = wb; wr.location = (0.75, 0, 2.6)
for emp, sx, tag in ((wl, -1, "L"), (wr, 1, "R")):                                               # three heads a side on long necks: they strike like arms
    for k, (out, up, fwd) in enumerate(((0.75, 0.45, -0.3), (1.15, -0.1, -0.55), (0.55, -0.55, -0.75))):
        cyl(f"XlNeck{tag}{k}", (sx * out * 0.5, fwd * 0.5, up * 0.5), 0.14, 1.0 + k * 0.1, M["XlBody"], emp, verts=6, rot=(-0.5 - k * 0.2, sx * (1.0 - k * 0.15), 0))
        face(f"W{tag}{k}", emp, (sx * out, fwd - 0.2, up), r=0.23)
wbl = empty("W_Blade"); wbl.parent = wr; wbl.location = (0.55, -0.95, -0.55)
cone("XlFangA", (-0.06, -0.3, 0), 0.04, 0.3, M["Fang"], wbl, verts=4, rot=(math.pi / 2, 0, 0))
cone("XlFangB", (0.06, -0.3, 0), 0.04, 0.3, M["Fang"], wbl, verts=4, rot=(math.pi / 2, 0, 0))
box("EmberCore_WBlade", (0, -0.5, 0), (0.06, 0.5, 0.06), M["EmberCore"], wbl, bevel=0.0)       # the venom it spits where it strikes

# ---------------------------------------------------------------- district elites (mini-bosses), rig: M<n>_Body / M<n>_Head / M<n>_ArmL / M<n>_ArmR
MINI = {}
def mini_rig(n, name):
    P = kit(name)
    body = empty(f"M{n}_Body"); body.parent = P
    head = empty(f"M{n}_Head"); head.parent = body
    al = empty(f"M{n}_ArmL"); al.parent = body
    ar = empty(f"M{n}_ArmR"); ar.parent = body
    MINI[n] = {"body": body, "head": head, "armL": al, "armR": ar}
    return P, body, head, al, ar

# 1. 巫咸 (海外西經 登葆山): a green snake in the right hand, a red snake in the left — humanoid rig
P, body, head, al, ar = mini_rig(1, "WolfKing")
cone("WxRobe", (0, 0, 0.85), 0.75, 1.7, M["WuRobe"], body, verts=10, r2=0.4)
cyl("WxSash", (0, 0, 1.45), 0.46, 0.14, M["Flag"], body, verts=10)
ball("WxChest", (0, 0, 1.85), 0.45, M["WuRobe"], body, scale=(1.1, 0.8, 0.9), sub=1)
for i in range(6):
    a = i / 6 * math.tau
    box(f"WxTassel{i}", (math.cos(a) * 0.62, math.sin(a) * 0.62, 0.25), (0.08, 0.08, 0.4), M["CassiaGold"], body, bevel=0.0)
head.location = (0, -0.05, 2.35)
ball("WxHead", (0, 0, 0), 0.3, M["Skin"], head, scale=(0.9, 1.0, 1.05), sub=1)
box("WxMask", (0, -0.27, 0.02), (0.4, 0.06, 0.34), M["Bone"], head, bevel=0.02)                  # a shaman's mask
for sx in (-1, 1):
    ball(f"EnemyEye_Wx{sx}", (sx * 0.1, -0.31, 0.06), 0.05, M["EnemyEye"], head, sub=0)
    cone(f"WxPlume{sx}", (sx * 0.2, 0.05, 0.45), 0.06, 0.7, M["Flag" if sx < 0 else "BirdBlue"], head, verts=4, rot=(0, sx * 0.35, 0))
cone("WxCrown", (0, 0, 0.42), 0.2, 0.55, M["CassiaGold"], head, verts=6)
for emp, sx, col in ((al, -1, "SnakeGreen"), (ar, 1, "SnakeRed")):                                  # -X is its own right hand (front = -Y)
    emp.location = (sx * 0.55, 0, 2.0)
    cyl("WxArm", (sx * 0.12, -0.25, -0.2), 0.1, 0.8, M["WuRobe"], emp, verts=6, rot=(-0.9, sx * 0.3, 0))
    ball("WxHand", (sx * 0.2, -0.6, -0.05), 0.11, M["Skin"], emp, sub=0)
    snake("WxSnake", emp, (sx * 0.2, -0.62, 0.0), M[col], n=6, step=(0, -0.13, 0.11), r=0.07)

# 2. 夸父 (海外北經): a giant, a green snake in the right hand, a yellow snake in the left; the staff he dropped became Denglin — giant rig
P, body, head, al, ar = mini_rig(2, "Sentinel")
for sx in (-1, 1):
    cyl(f"KfLeg{sx}", (sx * 0.4, 0, 0.75), 0.26, 1.5, M["GiantSkin"], body, verts=8, r2=0.2)
    box(f"KfFoot{sx}", (sx * 0.4, -0.15, 0.08), (0.42, 0.7, 0.16), M["GiantSkin"], body, bevel=0.03)
cone("KfKilt", (0, 0, 1.55), 0.85, 0.8, M["Hay"], body, verts=10, r2=0.6)
ball("KfTorso", (0, 0, 2.35), 0.85, M["GiantSkin"], body, scale=(1.1, 0.8, 1.0), sub=2)
cyl("KfBelt", (0, 0, 1.9), 0.7, 0.16, M["Rope"], body, verts=10)
head.location = (0, -0.1, 3.3)
ball("KfHead", (0, 0, 0), 0.45, M["GiantSkin"], head, scale=(0.95, 1.0, 1.05), sub=1)
box("KfHair", (0, 0.12, 0.3), (0.8, 0.7, 0.3), M["Hair"], head, bevel=0.05)
box("KfBeard", (0, -0.32, -0.3), (0.5, 0.2, 0.4), M["Hair"], head, bevel=0.03)
for sx in (-1, 1):
    ball(f"EnemyEye_Kf{sx}", (sx * 0.16, -0.4, 0.06), 0.07, M["EnemyEye"], head, sub=0)
for emp, sx, col in ((al, -1, "SnakeGreen"), (ar, 1, "SnakeYellow")):
    emp.location = (sx * 1.05, 0, 2.75)
    cyl("KfArm", (sx * 0.1, -0.2, -0.6), 0.22, 1.3, M["GiantSkin"], emp, verts=8, rot=(-0.35, sx * 0.15, 0))
    ball("KfFist", (sx * 0.15, -0.45, -1.25), 0.28, M["GiantSkin"], emp, sub=1)
    snake("KfSnake", emp, (sx * 0.15, -0.5, -1.2), M[col], n=7, step=(0, -0.16, 0.14), r=0.1, wave=0.12)
cyl("KfStaff", (0.55, -0.75, 1.6), 0.07, 3.2, M["Timber"], MINI[2]["armR"], verts=6, rot=(0.1, 0, 0))   # 棄其杖,化為鄧林
ball("KfStaffBud", (0.55, -0.9, 3.2), 0.16, M["Blossom"], MINI[2]["armR"], sub=0)

# 3. 天吳 (海外東經 朝陽之谷): the water lord, eight human-faced heads, eight legs, eight tails, blue-green and yellow — quadruped rig
P, body, head, al, ar = mini_rig(3, "Salamander")
ball("TwBody", (0, 0.2, 1.0), 0.72, M["TwBlue"], body, scale=(0.95, 1.8, 0.8), sub=2)
box("TwBack", (0, 0.2, 1.52), (0.7, 2.0, 0.12), M["TwYellow"], body, bevel=0.04)                   # 背青黃
for i in range(3):                                                                                  # six of the eight legs sit on the body, the front pair on the arm empties
    for sx in (-1, 1):
        cyl(f"TwLeg{i}{sx}", (sx * 0.55, -0.1 + i * 0.6, 0.45), 0.11, 0.9, M["TwBlue"], body, verts=6, r2=0.08)
        ball(f"TwPaw{i}{sx}", (sx * 0.55, -0.18 + i * 0.6, 0.07), 0.13, M["TwYellow"], body, scale=(1, 1.3, 0.6), sub=0)
for i in range(8):
    a = (i - 3.5) * 0.2
    cyl(f"TwTail{i}", (math.sin(a) * 0.8, 1.6 + math.cos(a) * 0.35, 1.2 + abs(i - 3.5) * 0.04), 0.06, 1.1, M["TwYellow" if i % 2 else "TwBlue"], body, rot=(-1.0, 0, -a), verts=5, r2=0.02)
head.location = (0, -1.25, 1.35)
for k in range(8):                                                                                  # eight faces in two fanned rows
    row = k // 4; col = k % 4
    face(f"Tw{k}", head, ((col - 1.5) * 0.36, -0.12 - row * 0.05, 0.12 + row * 0.42 - abs(col - 1.5) * 0.06), r=0.19)
ball("TwMane", (0, 0.2, 0.3), 0.55, M["TwBlue"], head, scale=(1.4, 0.7, 1.1), sub=1)
for emp, sx in ((al, -1), (ar, 1)):
    emp.location = (sx * 0.6, -0.75, 0.95)
    cyl("TwForeleg", (sx * 0.05, 0, -0.45), 0.13, 0.95, M["TwBlue"], emp, verts=6, r2=0.09)
    ball("TwForepaw", (sx * 0.05, -0.08, -0.9), 0.15, M["TwYellow"], emp, scale=(1, 1.3, 0.6), sub=0)

# 4. 鑿齒 (海外南經 壽華之野): fought Yi and was shot; holds a shield (some say a dagger-axe), a tooth like a chisel — blob rig slot
P, body, head, al, ar = mini_rig(4, "Maw")
for sx in (-1, 1):
    cyl(f"CcLeg{sx}", (sx * 0.32, 0, 0.5), 0.2, 1.0, M["Ape"], body, verts=7, r2=0.16)
ball("CcTorso", (0, 0, 1.45), 0.75, M["Ape"], body, scale=(1.1, 0.85, 1.0), sub=2)
cyl("CcBelt", (0, 0, 1.0), 0.62, 0.16, M["Rope"], body, verts=10)
for i in range(5):
    box(f"CcHide{i}", ((i - 2) * 0.26, -0.5, 0.8), (0.2, 0.06, 0.45), M["Hay"], body, bevel=0.0)
head.location = (0, -0.25, 2.15)
ball("CcHead", (0, 0, 0), 0.42, M["ApeFace"], head, scale=(1.0, 1.0, 0.95), sub=1)
box("CcBrow", (0, -0.32, 0.16), (0.6, 0.12, 0.12), M["Ape"], head, bevel=0.02)
for sx in (-1, 1):
    ball(f"EnemyEye_Cc{sx}", (sx * 0.15, -0.38, 0.05), 0.06, M["EnemyEye"], head, sub=0)
box("CcTooth", (0.06, -0.5, -0.42), (0.1, 0.1, 0.7), M["Fang"], head, rot=(0.25, 0, 0), bevel=0.0)  # the chisel tooth, long past the chin
box("EmberCore_CcTooth", (0.06, -0.56, -0.74), (0.1, 0.06, 0.08), M["EmberCore"], head, bevel=0.0)
box("CcHair", (0, 0.1, 0.3), (0.7, 0.6, 0.25), M["Hair"], head, bevel=0.04)
al.location = (-0.85, 0, 1.75); ar.location = (0.85, 0, 1.75)
cyl("CcArmL", (-0.05, -0.2, -0.45), 0.18, 1.0, M["Ape"], al, verts=7, rot=(-0.4, 0, 0))
cyl("CcShield", (-0.1, -0.7, -0.6), 0.8, 0.1, M["Timber"], al, rot=(math.pi / 2, 0, 0), verts=14)  # 鑿齒持盾
cyl("CcShieldBoss", (-0.1, -0.77, -0.6), 0.22, 0.08, M["Bronze"], al, rot=(math.pi / 2, 0, 0), verts=8)
cyl("CcArmR", (0.05, -0.2, -0.45), 0.18, 1.0, M["Ape"], ar, verts=7, rot=(-0.4, 0, 0))
cyl("CcGeHaft", (0.1, -0.6, -0.1), 0.05, 2.4, M["Timber"], ar, verts=6, rot=(0.5, 0, 0))            # 一曰戈
box("CcGeBlade", (0.1, -1.15, 0.85), (0.08, 0.7, 0.16), M["Bronze"], ar, rot=(0.5, 0, 0), bevel=0.0)


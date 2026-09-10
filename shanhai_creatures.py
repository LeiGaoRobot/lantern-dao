# ---------------------------------------------------------------- enemies (Z up; front = -Y) — Classic of Mountains and Seas
def eyes(P, y, z, sep=0.12, r=0.05):
    for sx in (-1, 1):
        ball(f"EnemyEye_{sx}", (sx * sep, y, z), r, M["EnemyEye"], P, sub=0)

M["Feather"] = mat("Feather", "#6e4436"); M["FeatherDark"] = mat("FeatherDark", "#3f2a24"); M["Sack"] = mat("Sack", "#d9a441"); M["FoxFur"] = mat("FoxFur", "#e8d9b8"); M["FoxDark"] = mat("FoxDark", "#c9a56a")
M["Ox"] = mat("Ox", "#2e2a2c"); M["Wool"] = mat("Wool", "#cfc6b4"); M["Bristle"] = mat("Bristle", "#5a4a3c")

P = kit("Wisp")   # 鬿雀: fowl-shaped, white head, rat feet, tiger claws (東次四經 北號之山)
ball("QqBody", (0, 0.05, 0.42), 0.26, M["Feather"], P, scale=(0.85, 1.15, 0.9), sub=1)
ball("QqHead", (0, -0.3, 0.62), 0.15, M["Bone"], P, sub=1)
cone("QqBeak", (0, -0.47, 0.6), 0.04, 0.16, M["Belt"], P, verts=4, rot=(math.pi / 2, 0, 0))
box("QqComb", (0, -0.28, 0.78), (0.03, 0.14, 0.08), M["Flag"], P, bevel=0.0)
eyes(P, -0.4, 0.66, sep=0.07, r=0.035)
for sx in (-1, 1):
    box(f"QqWing{sx}", (sx * 0.28, 0.05, 0.5), (0.22, 0.4, 0.05), M["FeatherDark"], P, rot=(0, sx * 0.5, 0), bevel=0.0)
    cyl(f"QqLeg{sx}", (sx * 0.1, 0.05, 0.16), 0.02, 0.3, M["Skin"], P, verts=4)
    for k in range(3):
        cone(f"QqClaw{sx}{k}", (sx * 0.1 + (k - 1) * 0.05, -0.06, 0.02), 0.02, 0.1, M["Fang"], P, verts=4, rot=(math.pi / 2, 0, 0))
for k in range(3):
    box(f"QqTail{k}", (0, 0.38, 0.5 + k * 0.05), (0.05, 0.3, 0.03), M["FeatherDark"], P, rot=(-0.6 - k * 0.2, 0, (k - 1) * 0.35), bevel=0.0)

P = kit("Cinder")   # 山膏: pig, red as cinnabar fire, fond of cursing (中次七經 苦山)
ball("SgBody", (0, 0.05, 0.5), 0.42, M["Scale"], P, scale=(0.95, 1.3, 0.85), sub=1)
ball("SgHead", (0, -0.5, 0.5), 0.26, M["Scale"], P, scale=(0.9, 1.0, 0.85), sub=1)
box("SgSnout", (0, -0.78, 0.42), (0.2, 0.18, 0.16), M["ScaleBelly"], P, bevel=0.03)
box("Fire_SgMouth", (0, -0.84, 0.34), (0.16, 0.06, 0.05), M["Fire"], P, bevel=0.0)   # the open, cursing mouth glows like an ember
for sx in (-1, 1):
    cone(f"SgTusk{sx}", (sx * 0.1, -0.8, 0.36), 0.03, 0.14, M["Fang"], P, verts=4, rot=(-0.6, 0, 0))
    cone(f"SgEar{sx}", (sx * 0.2, -0.42, 0.72), 0.07, 0.18, M["Scale"], P, verts=4, rot=(-0.3, sx * 0.5, 0))
    for i, y in enumerate((-0.25, 0.3)):
        box(f"SgLeg{sx}{i}", (sx * 0.24, y, 0.12), (0.14, 0.16, 0.24), M["ScaleBelly"], P, bevel=0.0)
eyes(P, -0.68, 0.6, sep=0.11, r=0.045)
for i in range(5):
    cone(f"SgBristle{i}", (0, -0.35 + i * 0.2, 0.85), 0.05, 0.22, M["Bristle"], P, verts=4, rot=(0.25, 0, 0))
for i in range(4):
    a = i / 4 * math.tau
    box(f"Fire_SgFlame{i}", (math.cos(a) * 0.38, 0.05 + math.sin(a) * 0.45, 0.5 + (i % 2) * 0.12), (0.16, 0.05, 0.08), M["Fire"], P, rot=(0, 0, a + 0.4), bevel=0.0)

P = kit("Crawler")   # 鳴蛇: a serpent with four wings, sounding like a chime (中次二經 鮮山) — the Leg buckets become the wings
for i in range(6):
    y = -0.5 + i * 0.2
    ball(f"MsSeg{i}", (0, y, 0.26), 0.2 if i % 2 == 0 else 0.17, M["Mud"] if i % 2 == 0 else M["MudLight"], P, scale=(1.0, 0.9, 0.8), sub=1)
ball("MsHead", (0, -0.72, 0.3), 0.2, M["Mud"], P, scale=(1, 1.15, 0.8), sub=1)
eyes(P, -0.88, 0.36, sep=0.08, r=0.045)
for sx in (-1, 1):
    cone(f"MsFang{sx}", (sx * 0.06, -0.92, 0.24), 0.02, 0.1, M["Fang"], P, verts=4, rot=(math.pi / 2, 0, 0))
    # two wings a side: the web treats Leg-1* as the left bucket and Leg1* as the right bucket and swings them
    box(f"Leg{sx}0", (sx * 0.42, -0.25, 0.38), (0.6, 0.3, 0.03), M["Feather"], P, rot=(0, sx * 0.35, 0.15), bevel=0.0)
    box(f"Leg{sx}1", (sx * 0.4, 0.2, 0.36), (0.55, 0.28, 0.03), M["FeatherDark"], P, rot=(0, sx * 0.35, -0.15), bevel=0.0)
    box(f"Leg2{sx}0", (sx * 0.7, -0.25, 0.42), (0.28, 0.14, 0.02), M["Feather"], P, rot=(0, sx * 0.6, 0.15), bevel=0.0)
    box(f"Leg2{sx}1", (sx * 0.66, 0.2, 0.4), (0.26, 0.13, 0.02), M["FeatherDark"], P, rot=(0, sx * 0.6, -0.15), bevel=0.0)
cone("MsTail", (0, 0.78, 0.24), 0.12, 0.4, M["Mud"], P, verts=5, rot=(-math.pi / 2, 0, 0))
box("EmberCore_MsChime", (0, -0.2, 0.44), (0.08, 0.5, 0.03), M["EmberCore"], P, bevel=0.0)   # the chime-like glow along the spine

P = kit("Spitter")   # 畢方: a one-legged crane, red markings on green, white beak, brings strange fire (西次三經 章莪之山)
ball("BfBody", (0, 0.05, 0.75), 0.36, M["Bamboo"], P, scale=(0.85, 1.2, 0.8), sub=1)
cyl("BfNeck", (0, -0.35, 1.02), 0.07, 0.55, M["Bamboo"], P, rot=(0.9, 0, 0), verts=6)
ball("BfHead", (0, -0.55, 1.3), 0.14, M["Bamboo"], P, scale=(0.9, 1.2, 0.9), sub=1)
cone("BfBeak", (0, -0.8, 1.28), 0.04, 0.3, M["Bone"], P, verts=4, rot=(math.pi / 2, 0, 0))
ball("Fire_Maw", (0, -0.94, 1.26), 0.06, M["Fire"], P, sub=0)   # the fire it spits gathers at the beak
box("BfCrest", (0, -0.5, 1.45), (0.04, 0.16, 0.1), M["Flag"], P, bevel=0.0)
eyes(P, -0.64, 1.36, sep=0.07, r=0.035)
for sx in (-1, 1):
    box(f"BfWing{sx}", (sx * 0.4, 0.05, 0.85), (0.5, 0.55, 0.04), M["Bamboo"], P, rot=(0, sx * 0.25, 0), bevel=0.0)
    box(f"BfWingMark{sx}", (sx * 0.45, 0.0, 0.88), (0.3, 0.12, 0.05), M["Flag"], P, rot=(0, sx * 0.25, 0.3), bevel=0.0)
for i in range(4):
    box(f"BfMark{i}", (0.12 * (i % 2 - 0.5), -0.1 + i * 0.12, 0.98), (0.22, 0.06, 0.05), M["Flag"], P, rot=(0, 0, 0.5 * (i % 2 - 0.5)), bevel=0.0)
cyl("BfLeg", (0, 0.05, 0.28), 0.03, 0.55, M["Belt"], P, verts=5)   # one leg
for k in range(3):
    cone(f"BfToe{k}", (math.sin(k * 2.1) * 0.06, 0.05 + math.cos(k * 2.1) * 0.06, 0.02), 0.02, 0.16, M["Belt"], P, verts=4, rot=(math.pi / 2 - 0.2, 0, k * 2.1))
for k in range(3):
    box(f"BfTail{k}", (0, 0.5, 0.78 + k * 0.05), (0.06, 0.32, 0.03), M["Bamboo"] if k % 2 else M["Flag"], P, rot=(-0.5, 0, (k - 1) * 0.3), bevel=0.0)

P = kit("Brute")   # 窮奇: ox-shaped with hedgehog bristles, howls like a dog, eats men (西次四經 邽山)
ball("QoBody", (0, 0.1, 0.95), 0.82, M["Ox"], P, scale=(1.05, 1.35, 0.9), sub=1)
ball("QoHead", (0, -0.95, 1.1), 0.4, M["Ox"], P, scale=(0.9, 1.1, 0.85), sub=1)
box("QoSnout", (0, -1.32, 0.98), (0.34, 0.3, 0.26), M["Bristle"], P, bevel=0.03)
eyes(P, -1.25, 1.2, sep=0.16, r=0.07)
for sx in (-1, 1):
    cone(f"QoHorn{sx}", (sx * 0.32, -0.85, 1.42), 0.08, 0.5, M["Horn"], P, verts=6, rot=(-0.3, sx * 0.8, 0))
    cone(f"QoFang{sx}", (sx * 0.12, -1.45, 0.86), 0.04, 0.2, M["Fang"], P, verts=4, rot=(-0.4, 0, 0))
    for i, y in enumerate((-0.45, 0.55)):
        box(f"QoLeg{sx}{i}", (sx * 0.45, y, 0.25), (0.3, 0.34, 0.5), M["Ox"], P, bevel=0.0)
        box(f"QoHoof{sx}{i}", (sx * 0.45, y, 0.04), (0.32, 0.36, 0.08), M["Horn"], P, bevel=0.0)
for i in range(18):
    a = (i % 6) / 6 * math.pi - math.pi / 2; row = i // 6
    cone(f"QoBristle{i}", (math.sin(a) * 0.7, -0.4 + row * 0.5, 1.15 + math.cos(a) * 0.55), 0.05, 0.4, M["Bristle"], P, verts=4, rot=(0, a * 0.9, 0))
cyl("QoTail", (0, 1.2, 1.0), 0.05, 0.6, M["Ox"], P, rot=(-0.9, 0, 0), verts=5, r2=0.02)

# Boss: 刑天 — headless, nipples for eyes, navel for a mouth, dancing with shield and axe (海外西經)
P = kit("Warden")
wb = empty("W_Body"); wb.parent = P
cone("XtKilt", (0, 0, 0.9), 0.95, 1.8, M["Warden"], wb, verts=14, r2=0.7)
cyl("XtBelt", (0, 0, 1.75), 0.72, 0.18, M["Bronze"], wb, verts=14)
ball("XtTorso", (0, 0, 2.35), 0.78, M["Skin"], wb, scale=(1.15, 0.85, 0.95), sub=2)
cyl("XtShoulders", (0, 0, 2.95), 0.85, 0.3, M["Skin"], wb, verts=14, r2=0.55)
for sx in (-1, 1):
    ball(f"EnemyEye_W{sx}", (sx * 0.34, -0.66, 2.45), 0.12, M["EnemyEye"], wb, sub=0)          # the nipples are its eyes
box("EmberCore_WMouth", (0, -0.7, 1.95), (0.34, 0.08, 0.12), M["EmberCore"], wb, bevel=0.0)      # the navel is its mouth
for sx in (-1, 1):
    cone(f"XtTooth{sx}", (sx * 0.1, -0.74, 1.9), 0.03, 0.1, M["Fang"], wb, verts=4, rot=(math.pi, 0, 0))
for i in range(4):
    a = i / 4 * math.tau + 0.4
    box(f"EmberCore_WVein{i}", (math.cos(a) * 0.7, math.sin(a) * 0.5, 1.2 + (i % 2) * 0.35), (0.26, 0.05, 0.12), M["EmberCore"], wb, rot=(0, 0, a + 0.3), bevel=0.0)
wh = empty("W_Head"); wh.parent = wb; wh.location = (0, 0, 2.95)
cyl("XtNeckStump", (0, 0, 0.18), 0.22, 0.3, M["Skin"], wh, verts=10)                                   # no head: only the severed neck
cyl("XtNeckCut", (0, 0, 0.34), 0.2, 0.04, M["Flag"], wh, verts=10)
wl = empty("W_ArmL"); wl.parent = wb; wl.location = (-0.9, 0, 2.55)
cyl("XtArmL", (0, -0.1, -0.55), 0.19, 1.1, M["Skin"], wl, verts=8, rot=(-0.3, 0, 0))
ball("XtFistL", (0, -0.3, -1.1), 0.22, M["Skin"], wl, sub=1)
cyl("XtShield", (0, -0.55, -0.9), 0.75, 0.1, M["Bronze"], wl, rot=(math.pi / 2, 0, 0), verts=16)     # 干: the shield
cyl("XtShieldBoss", (0, -0.62, -0.9), 0.2, 0.08, M["Steel"], wl, rot=(math.pi / 2, 0, 0), verts=10)
torus("XtShieldRing", (0, -0.6, -0.9), 0.5, 0.04, M["Steel"], wl, rot=(math.pi / 2, 0, 0), segs=(16, 5))
wr = empty("W_ArmR"); wr.parent = wb; wr.location = (0.9, 0, 2.55)
cyl("XtArmR", (0, -0.1, -0.55), 0.19, 1.1, M["Skin"], wr, verts=8, rot=(-0.3, 0, 0))
ball("XtFistR", (0, -0.3, -1.1), 0.22, M["Skin"], wr, sub=1)
wbl = empty("W_Blade"); wbl.parent = wr; wbl.location = (0, -0.4, -1.2)
cyl("XtHaft", (0, -0.5, 0), 0.06, 2.2, M["Timber"], wbl, verts=6, rot=(math.pi / 2, 0, 0))          # 戚: the great axe
box("XtAxeHead", (0.35, -1.35, 0), (0.7, 0.9, 0.08), M["Steel"], wbl, bevel=0.02)
box("EmberCore_WBlade", (0.72, -1.35, 0), (0.08, 0.95, 0.1), M["EmberCore"], wbl, bevel=0.0)
box("XtAxeBack", (-0.25, -1.35, 0), (0.2, 0.3, 0.1), M["Bronze"], wbl, bevel=0.0)
ball("XtHaftEnd", (0, 0.6, 0), 0.08, M["Bronze"], wbl, sub=0)

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

# 1. 九尾狐 (南山經 青丘之山): fox with nine tails, cries like an infant — quadruped rig
P, body, head, al, ar = mini_rig(1, "WolfKing")
ball("NfBody", (0, 0.1, 0.95), 0.62, M["FoxFur"], body, scale=(0.85, 1.55, 0.75), sub=1)
ball("NfChest", (0, -0.65, 0.98), 0.48, M["Bone"], body, scale=(0.9, 0.9, 0.85), sub=1)
for i in range(9):
    a = (i - 4) * 0.28
    cyl(f"NfTail{i}", (math.sin(a) * 0.9, 1.15 + math.cos(a) * 0.5, 1.15 + abs(i - 4) * 0.06), 0.09, 1.3, M["FoxFur"] if i % 2 else M["FoxDark"], body, rot=(-0.9, 0, -a), verts=6, r2=0.03)
    ball(f"NfTailTip{i}", (math.sin(a) * 1.35, 1.35 + math.cos(a) * 0.95, 1.75 + abs(i - 4) * 0.06), 0.09, M["Bone"], body, sub=0)
for sx in (-1, 1):
    cyl(f"NfHind{sx}", (sx * 0.36, 0.7, 0.45), 0.11, 0.9, M["FoxFur"], body, verts=7, r2=0.07)
    ball(f"NfPawH{sx}", (sx * 0.36, 0.62, 0.08), 0.13, M["FoxDark"], body, scale=(1, 1.3, 0.6), sub=0)
head.location = (0, -1.15, 1.25)
ball("NfHead", (0, -0.1, 0), 0.34, M["FoxFur"], head, scale=(0.9, 1.1, 0.85), sub=1)
cone("NfSnout", (0, -0.5, -0.08), 0.16, 0.45, M["Bone"], head, verts=6, rot=(math.pi / 2, 0, 0))
ball("NfNose", (0, -0.7, -0.06), 0.05, M["Hair"], head, sub=0)
for sx in (-1, 1):
    cone(f"NfEar{sx}", (sx * 0.2, 0.05, 0.36), 0.11, 0.38, M["FoxFur"], head, verts=5, rot=(0.2, sx * 0.25, 0))
    ball(f"EnemyEye_WK{sx}", (sx * 0.15, -0.3, 0.1), 0.06, M["EnemyEye"], head, sub=0)
box("EmberCore_WKMark", (0, -0.28, 0.3), (0.1, 0.18, 0.03), M["EmberCore"], head, bevel=0.0)
for emp, sx in ((al, -1), (ar, 1)):
    emp.location = (sx * 0.4, -0.72, 0.95)
    cyl("NfForeleg", (0, 0, -0.45), 0.1, 0.9, M["FoxFur"], emp, verts=7, r2=0.07)
    ball("NfPaw", (0, -0.05, -0.85), 0.13, M["FoxDark"], emp, scale=(1, 1.3, 0.6), sub=0)

# 2. 狍鴞 (北次二經 鉤吾之山): goat body, human face, eyes under its arms, tiger teeth, human claws — biped rig
P, body, head, al, ar = mini_rig(2, "Sentinel")
ball("PxTorso", (0, 0, 1.55), 0.8, M["Wool"], body, scale=(1.0, 0.8, 1.05), sub=2)
box("PxHips", (0, 0, 0.75), (1.0, 0.75, 0.5), M["Wool"], body, bevel=0.06)
for sx in (-1, 1):
    cyl(f"PxLeg{sx}", (sx * 0.38, 0, 0.32), 0.17, 0.65, M["Wool"], body, verts=8)
    box(f"PxHoof{sx}", (sx * 0.38, 0, 0.05), (0.36, 0.4, 0.1), M["Horn"], body, bevel=0.0)
    ball(f"EnemyEye_SG{sx}", (sx * 0.72, -0.35, 1.75), 0.11, M["EnemyEye"], body, sub=0)       # the eyes sit in the armpits
for i in range(4):
    a = i / 4 * math.tau
    box(f"EmberCore_SGRune{i}", (math.cos(a) * 0.55, -0.6, 1.4 + (i % 2) * 0.3), (0.2, 0.05, 0.1), M["EmberCore"], body, rot=(0, 0, a), bevel=0.0)
head.location = (0, 0, 2.4)
ball("PxHead", (0, 0, 0.3), 0.36, M["Skin"], head, scale=(0.9, 0.85, 1.0), sub=1)              # a human face, blind
ball("PxHair", (0, 0.08, 0.5), 0.36, M["Wool"], head, scale=(1, 1, 0.7), sub=1)
box("PxBrow", (0, -0.3, 0.42), (0.5, 0.1, 0.08), M["Skin"], head, bevel=0.02)
box("PxMouth", (0, -0.34, 0.14), (0.3, 0.06, 0.1), M["Gum"], head, bevel=0.0)
for k in range(4):
    cone(f"PxTooth{k}", (-0.12 + k * 0.08, -0.36, 0.1), 0.03, 0.12, M["Fang"], head, verts=4, rot=(math.pi, 0, 0))
for sx in (-1, 1):
    torus(f"PxHorn{sx}", (sx * 0.3, 0.05, 0.55), 0.22, 0.06, M["Horn"], head, rot=(0, math.pi / 2, sx * 0.4), segs=(10, 5))
for emp, sx in ((al, -1), (ar, 1)):
    emp.location = (sx * 0.95, 0, 2.05)
    cyl("PxArm", (sx * 0.05, 0, -0.55), 0.17, 1.1, M["Wool"], emp, verts=8)
    ball("PxHand", (sx * 0.08, -0.05, -1.15), 0.2, M["Skin"], emp, sub=1)
    for k in range(3):
        cone(f"PxClaw{k}", (sx * 0.08 + (k - 1) * 0.1, -0.2, -1.32), 0.03, 0.22, M["Fang"], emp, verts=4, rot=(0.3, 0, 0))

# 3. 蜚 (東次四經 太山): ox-like, white head, one eye, serpent tail; water dries and grass dies where it walks — low long rig
P, body, head, al, ar = mini_rig(3, "Salamander")
ball("FeBody", (0, 0.2, 0.6), 0.62, M["Ox"], body, scale=(1.0, 2.0, 0.75), sub=1)
for i in range(4):
    ball(f"FeTail{i}", (0, 1.55 + i * 0.35, 0.5 - i * 0.05), 0.22 - i * 0.04, M["Ox"], body, sub=0)
cone("FeTailTip", (0, 2.9, 0.32), 0.08, 0.35, M["Ox"], body, verts=5, rot=(-math.pi / 2, 0, 0))
for sx in (-1, 1):
    cyl(f"FeHind{sx}", (sx * 0.55, 0.85, 0.28), 0.13, 0.55, M["Ox"], body, rot=(0, sx * 0.5, 0), verts=6)
    box(f"FeHoofH{sx}", (sx * 0.7, 0.85, 0.04), (0.26, 0.3, 0.08), M["Horn"], body, bevel=0.0)
for i in range(5):
    box(f"EmberCore_FeSore{i}", (0.35 * (i % 2 - 0.5), -0.5 + i * 0.4, 1.05), (0.16, 0.16, 0.05), M["EmberCore"], body, rot=(0, 0, i * 0.7), bevel=0.0)   # plague sores
head.location = (0, -1.25, 0.7)
ball("FeHead", (0, -0.15, 0), 0.42, M["Bone"], head, scale=(0.95, 1.2, 0.85), sub=1)             # the white head
box("FeMuzzle", (0, -0.55, -0.1), (0.42, 0.4, 0.3), M["Bone"], head, bevel=0.03)
ball("EnemyEye_SL", (0, -0.36, 0.22), 0.13, M["EnemyEye"], head, sub=0)                          # a single eye
for sx in (-1, 1):
    cone(f"FeHorn{sx}", (sx * 0.28, 0.05, 0.3), 0.07, 0.4, M["Horn"], head, verts=5, rot=(-0.4, sx * 0.7, 0))
for emp, sx in ((al, -1), (ar, 1)):
    emp.location = (sx * 0.58, -0.6, 0.55)
    cyl("FeForeleg", (sx * 0.1, 0, -0.25), 0.13, 0.55, M["Ox"], emp, rot=(0, sx * 0.5, 0), verts=6)
    box("FeHoof", (sx * 0.22, 0, -0.5), (0.26, 0.3, 0.08), M["Horn"], emp, bevel=0.0)

# 4. 帝江 (西次三經 天山): a yellow sack red as cinnabar fire, six legs, four wings, no face; it knows song and dance — blob rig
P, body, head, al, ar = mini_rig(4, "Maw")
ball("DjSack", (0, 0, 0.95), 1.05, M["Sack"], body, scale=(1.15, 1.05, 0.9), sub=2)
for i in range(6):
    a = i / 6 * math.tau + 0.3
    box(f"Fire_DjGlow{i}", (math.cos(a) * 0.95, math.sin(a) * 0.85, 0.7 + (i % 2) * 0.5), (0.34, 0.08, 0.2), M["Fire"], body, rot=(0, 0, a + 0.5), bevel=0.0)   # cinnabar-fire blotches
for i in range(6):
    a = i / 6 * math.tau + 0.52
    cyl(f"DjLeg{i}", (math.cos(a) * 0.95, math.sin(a) * 0.85, 0.3), 0.09, 0.55, M["Gourd"], body, rot=(math.sin(a) * 0.35, -math.cos(a) * 0.35, 0), verts=6)
    ball(f"DjFoot{i}", (math.cos(a) * 1.1, math.sin(a) * 1.0, 0.06), 0.13, M["Sack"], body, scale=(1.2, 1.2, 0.5), sub=0)
head.location = (0, -0.8, 1.2)
ball("DjBulge", (0, -0.1, 0), 0.5, M["Sack"], head, scale=(1.1, 0.8, 0.7), sub=1)                 # no face, only a bulge
for emp, sx in ((al, -1), (ar, 1)):
    emp.location = (sx * 1.0, 0, 1.3)
    box("DjWingA", (sx * 0.55, -0.15, 0.25), (1.2, 0.5, 0.05), M["Gourd"], emp, rot=(0.2, sx * 0.35, 0), bevel=0.0)
    box("DjWingB", (sx * 0.5, 0.35, 0.05), (1.0, 0.45, 0.05), M["Sack"], emp, rot=(-0.2, sx * 0.45, 0), bevel=0.0)
    box("Fire_DjWingTip", (sx * 1.1, -0.15, 0.4), (0.22, 0.2, 0.04), M["Fire"], emp, rot=(0.2, sx * 0.35, 0), bevel=0.0)


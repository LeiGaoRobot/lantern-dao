"""Headless Blender script: build the Lantern Dao · Shanhai asset kit and export one GLB.

Run:  D:/AI/tools/Blender/blender.exe -b -P build_kit.py -- --out D:/AI/lantern_dao
Outputs: site/assets/kit.glb + preview.png (kit lineup render)

Re-skin of the Emberlight kit: every Kit_<Name>, rig node, material and clip name is unchanged.
Contract with the web side (site/world.js):
  * every kit item is an Empty named Kit_<Name>; its children are built in local
    coordinates (Z up, front = -Y).  The page detaches the Empty, zeroes its
    position and uses it as a template for instancing.
  * child objects whose name starts with Snow_ are winter-only.
  * emissive materials (WindowGlass, Fire, Lantern, EnemyEye, EmberCore, HotMetal,
    Crystal, ShardCrystal, PlayerLamp) are baked into separate "glow" instanced
    meshes so the page can drive their intensity (day/night, hit flash).
  * rigs (Kit_Player, Kit_Warden) keep named parts: P_Body, P_Head, P_ArmL, P_ArmR,
    P_Lantern, P_Blade, W_Body, W_Head, W_Blade, W_ArmL, W_ArmR.
"""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector

random.seed(11)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[argv.index("--out") + 1] if "--out" in argv else os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(OUT, "site", "assets"), exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
COL = bpy.context.collection

# ---------------------------------------------------------------- materials
MATS = {}
def srgb(hexstr):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b))

def mat(name, hexcol, rough=0.85, emit=None, strength=0.0, metal=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*srgb(hexcol), 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit is not None:
        bsdf.inputs["Emission Color"].default_value = (*srgb(emit), 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    m.diffuse_color = (*srgb(hexcol), 1.0)
    MATS[name] = m
    return m

# Lantern Dao palette: indigo #2b4a5a / cinnabar #c8422b / gilt #d9b04a / rice paper #f2e9d8 / ink #1c1a1f
M = dict(
    Wall=mat("Wall", "#efe6d3"), WallDark=mat("WallDark", "#d9ccb2"), Timber=mat("Timber", "#8a3326"),
    Roof=mat("Roof", "#3e4a54"), RoofLight=mat("RoofLight", "#4f5d68"), RoofDark=mat("RoofDark", "#2b343c"),
    RoofBlue=mat("RoofBlue", "#4c6a78"), RoofBlueDark=mat("RoofBlueDark", "#37505c"),
    Stone=mat("Stone", "#aeaba3"), StoneDark=mat("StoneDark", "#74716d"), StoneLight=mat("StoneLight", "#c3bfb6"), Cobble=mat("Cobble", "#8f8783"),
    Door=mat("Door", "#9b3a2b"), Frame=mat("Frame", "#3a2a22"), WoodLight=mat("WoodLight", "#c9a577"),
    WindowGlass=mat("WindowGlass", "#ffe3b8", rough=0.3, emit="#ffc878", strength=3.0),
    Trunk=mat("Trunk", "#6b4a35"), Leaves=mat("Leaves", "#3f7d4c"), LeavesDark=mat("LeavesDark", "#2f6440"),
    Pine=mat("Pine", "#7fb26a"), Bush=mat("Bush", "#5f9c5a"), Grass=mat("Grass", "#74ad62"),
    Moss=mat("Moss", "#6fa06a"), DeadWood=mat("DeadWood", "#4a3e3a"), Ash=mat("Ash", "#1d1a24"),
    AshLight=mat("AshLight", "#3b3547"), Fire=mat("Fire", "#ff8a3d", rough=0.4, emit="#ff6a1a", strength=6.0),
    Lantern=mat("Lantern", "#ffd08a", rough=0.3, emit="#ffb85a", strength=5.0),
    Iron=mat("Iron", "#3f424a", rough=0.5, metal=0.2), Snow=mat("Snow", "#f4f7ff", rough=0.95),
    Water=mat("Water", "#6fc4d8", rough=0.1), Rope=mat("Rope", "#b59a6a"), Hay=mat("Hay", "#c9a15a"),
    Mushroom=mat("Mushroom", "#a6402a"), MushroomStem=mat("MushroomStem", "#6b3a24"),
    Reed=mat("Reed", "#8fae5a"), HotMetal=mat("HotMetal", "#ffb24a", rough=0.4, emit="#ff7a1a", strength=4.0),
    EnemyEye=mat("EnemyEye", "#a8ffd8", rough=0.3, emit="#7dffc0", strength=8.0),
    EmberCore=mat("EmberCore", "#b27cff", rough=0.3, emit="#9a5cff", strength=6.0),
    Crystal=mat("Crystal", "#8ae8c4", rough=0.2, emit="#55d9a0", strength=3.0),
    ShardCrystal=mat("ShardCrystal", "#ffb24a", rough=0.2, emit="#ff7a26", strength=3.2),
    PlayerLamp=mat("PlayerLamp", "#fff0c0", rough=0.3, emit="#ffd58a", strength=6.0),
    Cloak=mat("Cloak", "#efe8d8"), CloakDark=mat("CloakDark", "#2b4a5a"), Skin=mat("Skin", "#f2c9a4"),
    Hair=mat("Hair", "#1c1a1f"), Belt=mat("Belt", "#d9b04a"), Boot=mat("Boot", "#2a2a30"),
    Horn=mat("Horn", "#8a7a70"), Bone=mat("Bone", "#e6ddcc"), Warden=mat("Warden", "#16141c"),
    WardenTrim=mat("WardenTrim", "#5a3fa0"), Flag=mat("Flag", "#c8422b"),
    # xianxia additions
    Bronze=mat("Bronze", "#8c6d3a", rough=0.45, metal=0.5), Steel=mat("Steel", "#c8ccd4", rough=0.3, metal=0.6),
    Bamboo=mat("Bamboo", "#8fbe6a"), BambooDark=mat("BambooDark", "#5e8a48"), BambooLeaf=mat("BambooLeaf", "#5f9e4f"),
    Blossom=mat("Blossom", "#f2a3bf"), PlumBlossom=mat("PlumBlossom", "#d8455e"), PeachTrunk=mat("PeachTrunk", "#6e5a4a"),
    Clay=mat("Clay", "#7a5a48"), Herb=mat("Herb", "#6f9c58"), HerbDark=mat("HerbDark", "#4f7a44"),
    LingzhiRim=mat("LingzhiRim", "#e0b46a"), Orchid=mat("Orchid", "#5f9c5a"), ReedHead=mat("ReedHead", "#e8dcc0"),
    Phosphor=mat("Phosphor", "#7ff5c8", rough=0.3, emit="#5cf0b8", strength=5.0),
    Chitin=mat("Chitin", "#2a2430"), ChitinLight=mat("ChitinLight", "#5a3f66"),
    Toad=mat("Toad", "#4a6a3a"), ToadBelly=mat("ToadBelly", "#c9b57a"), Ape=mat("Ape", "#3a2f2a"), ApeFace=mat("ApeFace", "#e6ddcc"),
    Pill=mat("Pill", "#e87078", rough=0.3, emit="#ff6068", strength=3.6), Gourd=mat("Gourd", "#c8903a"), Mist=mat("Mist", "#d8e0e8"),
    Fur=mat("Fur", "#e6e4de"), FurLight=mat("FurLight", "#c4ccd4"), Fang=mat("Fang", "#efe6d2"),
    Golem=mat("Golem", "#8a8f8a"), GolemDark=mat("GolemDark", "#5a605c"),
    Scale=mat("Scale", "#8a2a1e"), ScaleBelly=mat("ScaleBelly", "#d8783a"),
    Mud=mat("Mud", "#3f5a48"), MudLight=mat("MudLight", "#6a8a5a"), Gum=mat("Gum", "#7a2f3a"),
)


# ---------------------------------------------------------------- helpers
def link(o):
    COL.objects.link(o)
    return o

def _finish(o, name, material, bevel=0.0, parent=None, smooth=False):
    o.name = name
    if material is not None:
        o.data.materials.clear()
        o.data.materials.append(material)
    if bevel > 0:
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
        b.limit_method = "ANGLE"
    for p in o.data.polygons:
        p.use_smooth = smooth
    if parent is not None:
        o.parent = parent
    return o

def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    link(e)
    e.location = loc
    e.empty_display_size = 0.3
    return e

def box(name, loc, size, material, parent, rot=(0, 0, 0), bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    return _finish(o, name, material, bevel, parent)

def cyl(name, loc, r, h, material, parent, rot=(0, 0, 0), verts=12, r2=None, smooth=False):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.object, name, material, 0, parent, smooth)

def cone(name, loc, r1, h, material, parent, rot=(0, 0, 0), verts=10, r2=0.0):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=loc, rotation=rot)
    return _finish(bpy.context.object, name, material, 0, parent)

def ball(name, loc, r, material, parent, scale=(1, 1, 1), sub=2, rot=(0, 0, 0), smooth=False):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    return _finish(o, name, material, 0, parent, smooth)

def wedge(name, loc, w, d, h, material, parent, rot_z=0.0):
    """Gable roof prism, ridge along X."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    x, y = w / 2, d / 2
    v = [bm.verts.new(p) for p in [(-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0), (-x, 0, h), (x, 0, h)]]
    for f in [(0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4), (3, 2, 1, 0)]:
        bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me))
    o.location = loc
    o.rotation_euler = (0, 0, rot_z)
    return _finish(o, name, material, 0, parent)

def lean_to(name, loc, w, d, h_low, h_high, material, parent):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    x, y = w / 2, d / 2
    t = 0.12
    pts = [(-x, -y, h_low), (x, -y, h_high), (x, y, h_high), (-x, y, h_low)]
    top = [bm.verts.new(p) for p in pts]
    bot = [bm.verts.new((p[0], p[1], p[2] - t)) for p in pts]
    bm.faces.new(top); bm.faces.new(list(reversed(bot)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([bot[i], bot[j], top[j], top[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me))
    o.location = loc
    return _finish(o, name, material, 0, parent)

def arc(name, loc, r_in, r_out, a0, a1, t, material, parent, segs=14, rot=(0, 0, 0)):
    """Ring sector in the XY plane, thickness t along Z (used for crescent blades)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    top, bot = [], []
    for i in range(segs + 1):
        a = a0 + (a1 - a0) * i / segs
        k = math.sin(math.pi * i / segs)
        ro = r_in + (r_out - r_in) * (0.25 + 0.75 * k)
        for lst, z in ((top, t / 2), (bot, -t / 2)):
            lst.append((bm.verts.new((math.cos(a) * r_in, math.sin(a) * r_in, z)),
                        bm.verts.new((math.cos(a) * ro, math.sin(a) * ro, z))))
    for i in range(segs):
        bm.faces.new([top[i][0], top[i][1], top[i + 1][1], top[i + 1][0]])
        bm.faces.new([bot[i + 1][0], bot[i + 1][1], bot[i][1], bot[i][0]])
        bm.faces.new([top[i][1], bot[i][1], bot[i + 1][1], top[i + 1][1]])
        bm.faces.new([top[i + 1][0], bot[i + 1][0], bot[i][0], top[i][0]])
    bm.faces.new([top[0][0], bot[0][0], bot[0][1], top[0][1]])
    bm.faces.new([top[-1][1], bot[-1][1], bot[-1][0], top[-1][0]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me))
    o.location = loc
    o.rotation_euler = rot
    return _finish(o, name, material, 0, parent)

# kit registry: items laid out on a grid for the preview render
KIT = []
def kit(name):
    i = len(KIT)
    e = empty(f"Kit_{name}", ((i % 8) * 7.0, (i // 8) * 8.0, 0))
    KIT.append(e)
    return e

def torus(name, loc, R, r, material, parent, rot=(0, 0, 0), segs=(12, 6)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=segs[0], minor_segments=segs[1], location=loc, rotation=rot)
    return _finish(bpy.context.object, name, material, 0, parent)

def eave_roof(P, cx, cy, z, RW, RD, rh, mats=("Roof", "RoofLight", "RoofDark"), tiles=True, tag="", snow=True):
    """Chinese gable roof, ridge along X: wedge + tile rows + upturned corner tips + ridge with end ornaments."""
    RH = rh
    wedge(f"Roof{tag}", (cx, cy, z), RW, RD, RH, M[mats[0]], P)
    box(f"Ridge{tag}", (cx, cy, z + RH + 0.02), (RW + 0.2, 0.24, 0.16), M[mats[2]], P)
    box(f"Eave{tag}", (cx, cy, z - 0.03), (RW, RD, 0.1), M[mats[2]], P, bevel=0.0)
    for sx in (-1, 1):
        ball(f"RidgeEnd{tag}{sx}", (cx + sx * (RW / 2 + 0.1), cy, z + RH + 0.2), 0.14, M[mats[2]], P, sub=1)
        for sy in (-1, 1):
            box(f"EaveTip{tag}{sx}{sy}", (cx + sx * (RW / 2 - 0.05), cy + sy * (RD / 2 - 0.05), z + 0.16), (0.8, 0.8, 0.1), M[mats[2]], P, rot=(sy * 0.55, -sx * 0.55, 0), bevel=0.0)
            cone(f"RidgeBeast{tag}{sx}{sy}", (cx + sx * (RW / 2 - 0.35), cy + sy * (RD / 2 - 0.35), z + 0.3), 0.08, 0.28, M["Bronze"], P, verts=5, rot=(sy * 0.5, -sx * 0.5, 0))
    slope = math.atan2(RH, RD / 2)
    pitch_len = math.hypot(RD / 2, RH)
    if tiles:
        ROWS, TW = 3, 0.36
        tile_mats = [M[mats[0]], M[mats[1]], M[mats[2]]]
        for side in (-1, 1):
            n = Vector((0, side * RH, RD / 2)).normalized()
            for k in range(ROWS):
                f = (k + 0.5) / ROWS
                yy = side * (RD / 2) * (1 - f)
                zz = z + RH * f
                stag = (TW / 2) if k % 2 else 0.0
                count = int(RW / TW) + 2
                for t in range(count):
                    xx = -RW / 2 + stag + t * TW
                    if xx < -RW / 2 - 0.05 or xx > RW / 2 + 0.05:
                        continue
                    box(f"Tile{tag}{side}{k}{t}", (cx + xx, cy + yy + n.y * 0.05, zz + n.z * 0.05), (TW - 0.04, pitch_len / ROWS + 0.06, 0.07), tile_mats[(k + t) % 3], P, rot=(side * -slope, 0, 0), bevel=0.0)
    if snow:
        for side in (-1, 1):
            n = Vector((0, side * RH, RD / 2)).normalized()
            box(f"Snow_Roof{tag}{side}", (cx, cy + side * RD / 4 + n.y * 0.12, z + RH / 2 + n.z * 0.12), (RW + 0.05, pitch_len * 0.98, 0.12), M["Snow"], P, rot=(side * -slope, 0, 0), bevel=0.03)
    return RW, RD, RH

def red_columns(P, W, D, H, tag="", mids=True, z0=0.0):
    pts = [(sx * W / 2, sy * D / 2) for sx in (-1, 1) for sy in (-1, 1)]
    if mids:
        pts += [(0, -D / 2)]
    for i, (x, y) in enumerate(pts):
        cyl(f"Col{tag}{i}", (x, y, z0 + H / 2), 0.09, H + 0.1, M["Timber"], P, verts=8)
        cyl(f"ColBase{tag}{i}", (x, y, z0 + 0.08), 0.14, 0.16, M["StoneDark"], P, verts=8)

def double_door(P, x, y, z=0, rot_z=0.0, w=1.0, h=1.5):
    g = empty("DoorGrp"); g.parent = P; g.location = (x, y, z); g.rotation_euler = (0, 0, rot_z)
    box("DoorFrame", (0, -0.02, h / 2), (w + 0.16, 0.1, h + 0.1), M["Frame"], g, bevel=0.0)
    for sx in (-1, 1):
        box(f"Door{sx}", (sx * w / 4, -0.07, h / 2), (w / 2 - 0.03, 0.08, h - 0.06), M["Door"], g, bevel=0.0)
        ball(f"Knob{sx}", (sx * 0.1, -0.13, h * 0.55), 0.04, M["Bronze"], g, sub=1)
    box("Step", (0, -0.25, 0.06), (w + 0.3, 0.36, 0.12), M["Stone"], g, bevel=0.02)

def lattice(P, x, y, z, rot_z=0.0, w=0.7, h=0.7):
    g = empty("WinGrp"); g.parent = P; g.location = (x, y, z); g.rotation_euler = (0, 0, rot_z)
    box("WinFrame", (0, 0, 0), (w + 0.12, 0.1, h + 0.12), M["Frame"], g, bevel=0.0)
    box("WinGlass", (0, -0.03, 0), (w, 0.06, h), M["WindowGlass"], g, bevel=0.0)
    for i in (-1, 0, 1):
        box(f"MullV{i}", (i * w / 3, -0.06, 0), (0.035, 0.02, h), M["Frame"], g, bevel=0.0)
        box(f"MullH{i}", (0, -0.06, i * h / 3), (w, 0.02, 0.035), M["Frame"], g, bevel=0.0)

def hang_lantern(P, x, y, z, tag=""):
    cyl(f"LanString{tag}", (x, y, z + 0.16), 0.012, 0.16, M["Iron"], P, verts=4)
    ball(f"Lantern_Hang{tag}", (x, y, z), 0.15, M["Lantern"], P, scale=(1, 1, 1.25), sub=1)
    cyl(f"LanRing{tag}", (x, y, z + 0.17), 0.09, 0.03, M["Bronze"], P, verts=8)
    box(f"LanTassel{tag}", (x, y, z - 0.28), (0.04, 0.04, 0.16), M["Flag"], P, bevel=0.0)

# ---------------------------------------------------------------- 1. House_A: courtyard house with flying eaves
P = kit("House_A")
W, D, H = 3.2, 2.5, 2.1
box("Walls", (0, 0, H / 2), (W, D, H), M["Wall"], P)
box("Base", (0, 0, 0.16), (W + 0.3, D + 0.3, 0.32), M["Stone"], P)
box("Skirt", (0, 0, 0.5), (W + 0.04, D + 0.04, 0.4), M["StoneLight"], P, bevel=0.0)
red_columns(P, W + 0.02, D + 0.02, H)
box("FrontBeam", (0, -D / 2 - 0.08, H - 0.12), (W + 0.4, 0.14, 0.16), M["Timber"], P, bevel=0.0)
eave_roof(P, 0, 0, H - 0.05, W + 1.1, D + 1.0, 1.0)
double_door(P, -0.7, -D / 2 - 0.02)
lattice(P, 0.75, -D / 2 - 0.03, 1.25)
lattice(P, W / 2 + 0.03, 0.2, 1.25, rot_z=-math.pi / 2)
lattice(P, -W / 2 - 0.03, 0.2, 1.25, rot_z=math.pi / 2)
hang_lantern(P, -1.55, -D / 2 - 0.45, H - 0.5, "A")
hang_lantern(P, 1.55, -D / 2 - 0.45, H - 0.5, "B")
box("Planter", (0.75, -D / 2 - 0.25, 0.14), (0.9, 0.3, 0.28), M["Clay"], P)
for i in range(5):
    cone(f"Orchid{i}", (0.42 + i * 0.16, -D / 2 - 0.25, 0.45), 0.04, 0.4, M["Orchid"], P, rot=((i % 2 - 0.5) * 0.5, (i - 2) * 0.15, 0), verts=4)

# ---------------------------------------------------------------- 2. House_B: two-storey pavilion (double eaves)
P = kit("House_B")
W, D, H = 2.8, 2.8, 3.1
box("Lower", (0, 0, 0.75), (W + 0.2, D + 0.2, 1.5), M["WallDark"], P)
box("Base", (0, 0, 0.16), (W + 0.5, D + 0.5, 0.32), M["Stone"], P)
red_columns(P, W + 0.24, D + 0.24, 1.55, tag="L")
eave_roof(P, 0, 0, 1.55, W + 1.3, D + 1.3, 0.5, mats=("RoofBlue", "RoofBlue", "RoofBlueDark"), tiles=False, tag="L", snow=False)
box("Upper", (0, 0, 2.3), (W - 0.4, D - 0.4, 1.55), M["Wall"], P)
red_columns(P, W - 0.36, D - 0.36, 1.55, tag="U", mids=False, z0=1.55)
eave_roof(P, 0, 0, H - 0.02, W + 0.7, D + 0.7, 1.0, mats=("RoofBlue", "RoofBlue", "RoofBlueDark"), tag="U")
double_door(P, 0, -D / 2 - 0.12)
lattice(P, -0.55, -D / 2 + 0.17, 2.35, w=0.6, h=0.7)
lattice(P, 0.55, -D / 2 + 0.17, 2.35, w=0.6, h=0.7)
lattice(P, W / 2 - 0.17, 0, 2.35, rot_z=-math.pi / 2, w=0.6, h=0.7)
lattice(P, -W / 2 + 0.17, 0, 2.35, rot_z=math.pi / 2, w=0.6, h=0.7)
lattice(P, -0.8, -D / 2 - 0.13, 0.95, w=0.5, h=0.5)
lattice(P, 0.8, -D / 2 - 0.13, 0.95, w=0.5, h=0.5)
# balcony railing on the lower roof
for i in range(7):
    box(f"Rail{i}", (-1.2 + i * 0.4, -D / 2 - 0.35, 1.85), (0.06, 0.06, 0.5), M["Timber"], P, bevel=0.0)
box("RailTop", (0, -D / 2 - 0.35, 2.1), (2.5, 0.07, 0.07), M["Timber"], P, bevel=0.0)
hang_lantern(P, -1.5, -D / 2 - 0.5, H - 0.55, "A")
hang_lantern(P, 1.5, -D / 2 - 0.5, H - 0.55, "B")

# ---------------------------------------------------------------- 3. House_C: tea shed (open long pavilion)
P = kit("House_C")
W, D, H = 4.2, 2.4, 2.15
box("Floor", (0, 0, 0.08), (W + 0.6, D + 0.6, 0.16), M["Stone"], P, bevel=0.01)
box("BackWall", (0, D / 2 - 0.1, 0.65), (W, 0.2, 1.3), M["Wall"], P)
box("Counter", (1.0, D / 2 - 0.5, 0.45), (1.8, 0.5, 0.9), M["Timber"], P)
box("CounterTop", (1.0, D / 2 - 0.5, 0.92), (1.9, 0.6, 0.06), M["WoodLight"], P)
for i in range(3):
    ball(f"TeaJar{i}", (0.4 + i * 0.5, D / 2 - 0.5, 1.1), 0.16, M["Clay"], P, scale=(1, 1, 1.1), sub=1)
    cyl(f"TeaLid{i}", (0.4 + i * 0.5, D / 2 - 0.5, 1.27), 0.08, 0.04, M["Flag"], P, verts=8)
red_columns(P, W, D, H)
eave_roof(P, 0, 0, H, W + 1.0, D + 0.9, 0.9)
for tx in (-1.1, 0.3):
    cyl(f"Table{tx:.0f}", (tx, -0.3, 0.7), 0.45, 0.06, M["WoodLight"], P, verts=10)
    cyl(f"TableLeg{tx:.0f}", (tx, -0.3, 0.35), 0.07, 0.7, M["Timber"], P, verts=6)
    for k in range(3):
        a = k / 3 * math.tau + 0.5
        cyl(f"Stool{tx:.0f}{k}", (tx + math.cos(a) * 0.7, -0.3 + math.sin(a) * 0.7, 0.2), 0.14, 0.4, M["Timber"], P, verts=6)
    cyl(f"Teapot{tx:.0f}", (tx, -0.3, 0.8), 0.1, 0.14, M["Clay"], P, verts=8)
cyl("FlagPole", (-W / 2 - 0.35, -D / 2 - 0.3, 1.9), 0.04, 3.8, M["Timber"], P, verts=6)
box("FlagArm", (-W / 2 - 0.05, -D / 2 - 0.3, 3.7), (0.7, 0.04, 0.04), M["Timber"], P, bevel=0.0)
box("TeaFlag", (-W / 2 + 0.1, -D / 2 - 0.3, 3.2), (0.32, 0.03, 0.95), M["Flag"], P, bevel=0.0)
box("TeaFlagMark", (-W / 2 + 0.1, -D / 2 - 0.33, 3.2), (0.16, 0.01, 0.4), M["Wall"], P, bevel=0.0)
hang_lantern(P, 1.8, -D / 2 - 0.4, H - 0.5, "A")

# ---------------------------------------------------------------- 4. Tower: seven-storey stone pagoda
P = kit("Tower")
cyl("PagodaBase", (0, 0, 0.2), 1.5, 0.4, M["Stone"], P, verts=8)
cyl("PagodaStep", (0, 0, 0.5), 1.3, 0.2, M["StoneDark"], P, verts=8)
z0 = 0.6
for i in range(7):
    r = 1.05 - i * 0.09
    zb = z0 + i * 1.0
    cyl(f"Tier{i}", (0, 0, zb + 0.45), r, 0.9, M["Stone"] if i % 2 == 0 else M["StoneLight"], P, verts=8)
    cyl(f"TierEave{i}", (0, 0, zb + 0.95), r + 0.5, 0.3, M["RoofDark"], P, verts=8, r2=r - 0.08)
    cyl(f"TierEaveRim{i}", (0, 0, zb + 0.82), r + 0.52, 0.06, M["Roof"], P, verts=8)
    if i % 2 == 0:
        box(f"TierWin{i}", (0, -(r - 0.02), zb + 0.45), (0.3, 0.1, 0.42), M["WindowGlass"], P, bevel=0.0)
    if i < 6 and i % 2 == 1:
        cone(f"Snow_Tier{i}", (0, 0, zb + 1.02), r + 0.5, 0.2, M["Snow"], P, verts=8, r2=r - 0.05)
zt = z0 + 7.0
cone("PagodaRoof", (0, 0, zt + 0.5), 0.75, 1.0, M["RoofDark"], P, verts=8)
cone("Snow_PagodaRoof", (0, 0, zt + 0.6), 0.78, 1.0, M["Snow"], P, verts=8)
cyl("Finial", (0, 0, zt + 1.35), 0.05, 0.9, M["Bronze"], P, verts=6)
for k in range(3):
    cyl(f"FinialRing{k}", (0, 0, zt + 1.1 + k * 0.22), 0.16 - k * 0.04, 0.05, M["Bronze"], P, verts=8)
ball("FinialJewel", (0, 0, zt + 1.85), 0.09, M["Bronze"], P, sub=1)
double_door(P, 0, -1.05, w=0.8, h=1.3)

# ---------------------------------------------------------------- 5. Forge: alchemy / artefact workshop
P = kit("Forge")
W, D, H = 3.6, 2.6, 1.9
box("ForgeFloor", (0, 0, 0.06), (W + 0.6, D + 0.6, 0.12), M["StoneDark"], P, bevel=0.01)
cyl("Crystal_Array", (0, -0.1, 0.125), 1.35, 0.02, M["Crystal"], P, verts=16)
cyl("ArrayInner", (0, -0.1, 0.13), 1.15, 0.025, M["StoneDark"], P, verts=16)
for i in range(8):
    a = i / 8 * math.tau
    box(f"Crystal_Rune{i}", (math.cos(a) * 0.85, -0.1 + math.sin(a) * 0.85, 0.135), (0.22, 0.05, 0.02), M["Crystal"], P, rot=(0, 0, a + math.pi / 2), bevel=0.0)
box("BackWall", (0, D / 2 - 0.1, H / 2), (W, 0.2, H), M["Wall"], P)
box("SideWallL", (-W / 2 + 0.1, 0.3, H / 2), (0.2, D - 0.6, H), M["Wall"], P)
box("HalfWallR", (W / 2 - 0.1, 0.3, 0.3), (0.2, D - 0.6, 0.6), M["Wall"], P)
red_columns(P, W + 0.1, D + 0.1, H + 0.2)
eave_roof(P, 0, 0.1, H + 0.15, W + 1.0, D + 0.9, 0.85)
# cauldron furnace (ding)
FX, FY = -0.95, D / 2 - 0.75
for k in range(3):
    a = k / 3 * math.tau + 0.5
    cyl(f"DingLeg{k}", (FX + math.cos(a) * 0.35, FY + math.sin(a) * 0.35, 0.25), 0.07, 0.5, M["Bronze"], P, verts=6, rot=(math.sin(a) * 0.25, -math.cos(a) * 0.25, 0))
ball("DingBody", (FX, FY, 0.85), 0.58, M["Bronze"], P, scale=(1, 1, 0.85), sub=2)
cyl("DingRim", (FX, FY, 1.28), 0.5, 0.1, M["Bronze"], P, verts=12)
for sx in (-1, 1):
    torus(f"DingEar{sx}", (FX + sx * 0.5, FY, 1.4), 0.12, 0.03, M["Bronze"], P, rot=(0, math.pi / 2, 0))
cyl("Fire_Coals", (FX, FY, 1.3), 0.42, 0.06, M["Fire"], P, verts=12)
ball("Fire_Flame", (FX, FY, 1.5), 0.22, M["Fire"], P, scale=(1, 0.9, 1.6), sub=1)
box("DingBand", (FX, FY, 0.9), (1.2, 0.08, 0.14), M["EmberCore"], P, bevel=0.0)
box("EmberCore_Sigil", (FX, FY - 0.55, 0.9), (0.3, 0.04, 0.3), M["EmberCore"], P, bevel=0.0)
# forging table with a glowing sword blank
AX, AY = 0.55, -0.25
box("TableBody", (AX, AY, 0.35), (1.0, 0.5, 0.7), M["StoneDark"], P, bevel=0.02)
box("TableTop", (AX, AY, 0.73), (1.08, 0.58, 0.06), M["Stone"], P, bevel=0.01)
box("HotBlade", (AX, AY, 0.79), (0.7, 0.07, 0.04), M["HotMetal"], P, bevel=0.0)
box("HotGuard", (AX + 0.3, AY, 0.79), (0.05, 0.2, 0.05), M["Bronze"], P, bevel=0.0)
box("HammerHead", (AX + 0.15, AY + 0.17, 0.82), (0.14, 0.08, 0.1), M["Iron"], P, bevel=0.01)
cyl("HammerHandle", (AX + 0.15, AY + 0.37, 0.82), 0.02, 0.4, M["Timber"], P, rot=(math.pi / 2, 0, 0), verts=6)
cyl("Bucket", (W / 2 - 0.5, 0.5, 0.22), 0.18, 0.44, M["Timber"], P, verts=10)
cyl("BucketWater", (W / 2 - 0.5, 0.5, 0.42), 0.15, 0.03, M["Water"], P, verts=10)
box("Rack", (0.9, D / 2 - 0.2, 1.35), (1.4, 0.06, 0.08), M["Timber"], P, bevel=0.0)
for i in range(4):
    cyl(f"Tool{i}", (0.4 + i * 0.32, D / 2 - 0.24, 1.0), 0.02, 0.62, M["Steel"], P, verts=6)
    box(f"ToolHead{i}", (0.4 + i * 0.32, D / 2 - 0.24, 1.3), (0.16, 0.05, 0.05), M["Bronze"], P, bevel=0.0)
    ball(f"ToolPommel{i}", (0.4 + i * 0.32, D / 2 - 0.24, 1.36), 0.035, M["Bronze"], P, sub=0)
box("Bellows", (-1.4, 0.2, 0.22), (0.5, 0.8, 0.3), M["Timber"], P, bevel=0.02)
cyl("BellowsHandle", (-1.4, -0.35, 0.45), 0.03, 0.7, M["WoodLight"], P, rot=(0.9, 0, 0), verts=6)
box("Chest", (1.4, -0.9, 0.22), (0.6, 0.4, 0.44), M["Timber"], P)
box("ChestLid", (1.4, -0.9, 0.47), (0.64, 0.44, 0.08), M["WoodLight"], P)
box("SignArm", (-W / 2 - 0.3, -D / 2 + 0.15, 2.0), (0.6, 0.05, 0.05), M["Timber"], P, bevel=0.0)
box("Sign", (-W / 2 - 0.55, -D / 2 + 0.15, 1.65), (0.42, 0.04, 0.6), M["WoodLight"], P)
box("SignMark", (-W / 2 - 0.55, -D / 2 + 0.12, 1.65), (0.24, 0.01, 0.4), M["Flag"], P, bevel=0.0)

# ---------------------------------------------------------------- 6. Well: spirit spring with lotus
P = kit("Well")
cyl("WellRing", (0, 0, 0.3), 0.82, 0.6, M["Stone"], P, verts=8)
cyl("WellHole", (0, 0, 0.56), 0.64, 0.1, M["Water"], P, verts=8)
for i in range(8):
    a = i / 8 * math.tau + math.pi / 8
    box(f"WellStone{i}", (math.cos(a) * 0.8, math.sin(a) * 0.8, 0.62), (0.62, 0.22, 0.12), M["StoneDark"], P, rot=(0, 0, a + math.pi / 2), bevel=0.0)
for i, (lx, ly, lr) in enumerate(((0.2, 0.15, 0.2), (-0.25, 0.1, 0.16), (0.05, -0.3, 0.14))):
    cyl(f"LilyPad{i}", (lx, ly, 0.62), lr, 0.02, M["MudLight"], P, verts=9)
cyl("LotusStem", (-0.2, -0.15, 0.75), 0.02, 0.3, M["HerbDark"], P, verts=5)
cone("Lotus", (-0.2, -0.15, 0.95), 0.14, 0.24, M["Blossom"], P, verts=7, r2=0.05, rot=(math.pi, 0, 0))
ball("LotusHeart", (-0.2, -0.15, 1.0), 0.06, M["Hay"], P, sub=0)
box("WellPlaque", (0, 0.95, 0.5), (0.5, 0.1, 0.7), M["StoneLight"], P)
box("WellPlaqueMark", (0, 0.89, 0.55), (0.2, 0.02, 0.4), M["StoneDark"], P, bevel=0.0)
box("Snow_WellRing", (0, 0, 0.7), (1.7, 1.7, 0.06), M["Snow"], P, bevel=0.03)

# ---------------------------------------------------------------- 7. Lantern post: stone lantern (LPGlow stays the light)
P = kit("LanternPost")
box("LPBase", (0, 0, 0.08), (0.56, 0.56, 0.16), M["Stone"], P)
cyl("LPPost", (0, 0, 0.75), 0.09, 1.2, M["StoneLight"], P, verts=8)
cyl("LPTable", (0, 0, 1.4), 0.26, 0.08, M["StoneDark"], P, verts=6)
for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
    box(f"LPPillar{i}", (sx * 0.17, sy * 0.17, 1.62), (0.06, 0.06, 0.36), M["Stone"], P, bevel=0.0)
box("LPGlow", (0, 0, 1.62), (0.24, 0.24, 0.3), M["Lantern"], P, bevel=0.0)
cone("LPCap", (0, 0, 1.92), 0.34, 0.24, M["Stone"], P, verts=6)
ball("LPJewel", (0, 0, 2.08), 0.06, M["StoneDark"], P, sub=1)
cone("Snow_LPCap", (0, 0, 1.98), 0.34, 0.2, M["Snow"], P, verts=6)

# ---------------------------------------------------------------- 8. Fence: bamboo lattice fence
P = kit("Fence")
for i, fx in enumerate((-1.1, 0, 1.1)):
    cyl(f"FPost{i}", (fx, 0, 0.45), 0.05, 0.9, M["Bamboo"], P, verts=6)
    cone(f"FPostTop{i}", (fx, 0, 0.92), 0.05, 0.08, M["BambooDark"], P, verts=6)
for z in (0.3, 0.72):
    cyl(f"FRail{z}", (0, 0, z), 0.03, 2.3, M["Bamboo"], P, rot=(0, math.pi / 2, 0), verts=6)
for i in range(6):
    x = -0.95 + i * 0.38
    box(f"FLatA{i}", (x, 0, 0.51), (0.03, 0.03, 0.55), M["BambooDark"], P, rot=(0, 0.75, 0), bevel=0.0)
    box(f"FLatB{i}", (x, 0, 0.51), (0.03, 0.03, 0.55), M["BambooDark"], P, rot=(0, -0.75, 0), bevel=0.0)
box("Snow_FRail", (0, 0, 0.78), (2.3, 0.1, 0.06), M["Snow"], P, bevel=0.02)

# ---------------------------------------------------------------- 9. small props
P = kit("Crate")
box("CrateBody", (0, 0, 0.3), (0.6, 0.6, 0.6), M["WoodLight"], P)
for a in (0, math.pi / 2):
    box(f"CrateX{a:.1f}", (0, 0, 0.3), (0.64, 0.08, 0.64), M["Timber"], P, rot=(0, 0, a), bevel=0.0)
for sx in (-1, 1):
    box(f"CrateStrap{sx}", (0, 0, 0.3 + sx * 0.22), (0.66, 0.66, 0.05), M["Bronze"], P, bevel=0.0)
box("Snow_Crate", (0, 0, 0.63), (0.62, 0.62, 0.08), M["Snow"], P)

P = kit("Barrel")   # wine jar
ball("JarBody", (0, 0, 0.36), 0.3, M["Clay"], P, scale=(1, 1, 1.15), sub=2)
cyl("JarNeck", (0, 0, 0.7), 0.13, 0.12, M["Clay"], P, verts=10)
ball("JarCap", (0, 0, 0.77), 0.16, M["Flag"], P, scale=(1, 1, 0.45), sub=1)
cyl("JarRope", (0, 0, 0.72), 0.15, 0.04, M["Rope"], P, verts=10)
ball("JarSmall", (0.4, 0.15, 0.2), 0.18, M["Clay"], P, scale=(1, 1, 1.1), sub=1)
cyl("JarSmallNeck", (0.4, 0.15, 0.4), 0.08, 0.08, M["Clay"], P, verts=8)
box("Snow_Barrel", (0, 0, 0.6), (0.5, 0.5, 0.06), M["Snow"], P)

P = kit("Cart")     # wheelbarrow
box("CartBed", (0, 0, 0.55), (1.4, 0.8, 0.1), M["WoodLight"], P)
for sx in (-1, 1):
    box(f"CartSide{sx}", (0, sx * 0.38, 0.72), (1.4, 0.06, 0.26), M["Timber"], P, bevel=0.0)
cyl("Wheel", (0.15, 0, 0.36), 0.38, 0.09, M["Timber"], P, rot=(math.pi / 2, 0, 0), verts=12)
cyl("Hub", (0.15, 0, 0.36), 0.08, 0.14, M["Iron"], P, rot=(math.pi / 2, 0, 0), verts=8)
box("WheelGuard", (0.15, 0, 0.78), (0.6, 0.32, 0.3), M["Timber"], P, bevel=0.02)
for sy in (-0.3, 0.3):
    cyl(f"Shaft{sy}", (-1.1, sy, 0.5), 0.04, 1.0, M["Timber"], P, rot=(0, math.pi / 2, 0), verts=6)
    cyl(f"Leg{sy}", (-0.6, sy, 0.25), 0.04, 0.5, M["Timber"], P, verts=6)
for i, (hx, hy) in enumerate(((-0.35, 0.15), (-0.3, -0.2), (0.6, 0.0))):
    ball(f"CartHerb{i}", (hx, hy, 0.82), 0.22, M["Herb"] if i % 2 == 0 else M["HerbDark"], P, scale=(1.2, 1, 0.7), sub=1)
ball("CartJar", (0.45, 0.0, 0.85), 0.18, M["Clay"], P, scale=(1, 1, 1.1), sub=1)

P = kit("Campfire")   # bronze incense burner
cyl("CenserSlab", (0, 0, 0.05), 0.7, 0.1, M["Stone"], P, verts=8)
for k in range(3):
    a = k / 3 * math.tau + 0.5
    cyl(f"CenserLeg{k}", (math.cos(a) * 0.3, math.sin(a) * 0.3, 0.2), 0.06, 0.25, M["Bronze"], P, verts=6)
cyl("CenserBody", (0, 0, 0.55), 0.45, 0.5, M["Bronze"], P, verts=10)
cyl("CenserRim", (0, 0, 0.82), 0.5, 0.06, M["Bronze"], P, verts=10)
for sx in (-1, 1):
    torus(f"CenserEar{sx}", (sx * 0.47, 0, 0.9), 0.1, 0.03, M["Bronze"], P, rot=(0, math.pi / 2, 0))
cyl("Fire_CF", (0, 0, 0.83), 0.4, 0.05, M["Fire"], P, verts=10)
for i, (ix, iy) in enumerate(((0, 0), (-0.14, 0.08), (0.12, -0.1))):
    cyl(f"Incense{i}", (ix, iy, 1.15), 0.012, 0.6, M["DeadWood"], P, verts=4, rot=(ix * 0.5, iy * 0.5, 0))
    ball(f"Fire_CF{i + 2}", (ix, iy, 1.45), 0.03, M["Fire"], P, sub=0)

P = kit("Logpile")
for k in range(3):
    for j in range(3 - k):
        cyl(f"LPLog{k}{j}", (0, -0.3 + j * 0.3 + k * 0.15, 0.13 + k * 0.24), 0.13, 1.0, M["Trunk"], P, rot=(0, math.pi / 2, 0), verts=8)
box("Snow_Logs", (0, 0, 0.7), (1.0, 0.5, 0.06), M["Snow"], P)

P = kit("Hay")   # herb baskets
cyl("Basket", (0, 0, 0.25), 0.3, 0.5, M["Rope"], P, verts=10, r2=0.4)
cyl("BasketRim", (0, 0, 0.5), 0.42, 0.05, M["Hay"], P, verts=10)
for i, (hx, hy) in enumerate(((0, 0), (0.18, 0.1), (-0.15, 0.12), (0.05, -0.18))):
    ball(f"Herb{i}", (hx, hy, 0.6), 0.16, M["Herb"] if i % 2 else M["HerbDark"], P, scale=(1.1, 1, 0.8), sub=1)
cyl("Basket2", (0.6, 0.3, 0.16), 0.2, 0.32, M["Rope"], P, verts=8, r2=0.26)
for i in range(4):
    a = i / 4 * math.tau
    ball(f"Berry{i}", (0.6 + math.cos(a) * 0.1, 0.3 + math.sin(a) * 0.1, 0.36), 0.07, M["Mushroom"], P, sub=0)

P = kit("Signpost")   # hanging wooden plaque
cyl("SPPost", (0, 0, 0.9), 0.05, 1.8, M["Timber"], P, verts=8)
box("SPArm", (0.25, 0, 1.78), (0.6, 0.05, 0.05), M["Timber"], P, bevel=0.0)
box("SPBoard", (0.4, 0, 1.4), (0.3, 0.05, 0.6), M["WoodLight"], P)
box("SPMark", (0.4, -0.03, 1.4), (0.16, 0.01, 0.4), M["Frame"], P, bevel=0.0)
cone("SPCap", (0, 0, 1.85), 0.12, 0.12, M["RoofDark"], P, verts=6)

# ---------------------------------------------------------------- trees
P = kit("Oak")   # layered pine (welcoming-pine silhouette)
cyl("OakTrunk", (0, 0, 0.7), 0.21, 1.4, M["Trunk"], P, verts=8, r2=0.15, rot=(0.1, 0.12, 0))
cyl("OakTrunk2", (0.25, -0.12, 1.9), 0.14, 1.3, M["Trunk"], P, verts=8, r2=0.09, rot=(-0.15, 0.35, 0))
cyl("OakBranch", (0.55, -0.1, 1.55), 0.07, 1.2, M["Trunk"], P, rot=(0.2, 1.25, 0), verts=6, r2=0.04)
cyl("OakBranch2", (-0.45, 0.2, 1.95), 0.07, 1.0, M["Trunk"], P, rot=(-0.4, -1.15, 0), verts=6, r2=0.04)
cyl("OakBranch3", (0.1, 0.5, 2.35), 0.06, 0.8, M["Trunk"], P, rot=(-1.1, 0.2, 0), verts=6, r2=0.03)
pads = ((1.1, -0.2, 1.75, 0.62), (-0.9, 0.35, 2.2, 0.58), (0.15, 0.95, 2.55, 0.5), (0.5, -0.55, 2.55, 0.5), (0.35, -0.1, 3.05, 0.55))
for i, (dx, dy, dz, r) in enumerate(pads):
    ball(f"OakLeaves{i}", (dx, dy, dz), r, M["Leaves"] if i % 2 == 0 else M["LeavesDark"], P, scale=(1.5, 1.3, 0.38), sub=1)
    ball(f"Snow_Oak{i}", (dx, dy, dz + r * 0.24), r * 0.98, M["Snow"], P, scale=(1.45, 1.25, 0.2), sub=1)

P = kit("Oak2")   # peach in blossom
cyl("Oak2Trunk", (0, 0, 0.55), 0.14, 1.1, M["PeachTrunk"], P, verts=8, r2=0.1)
cyl("Oak2Branch", (0.2, 0, 1.2), 0.06, 0.6, M["PeachTrunk"], P, rot=(0.2, 0.9, 0), verts=6)
cyl("Oak2Branch2", (-0.2, 0.1, 1.25), 0.06, 0.6, M["PeachTrunk"], P, rot=(-0.3, -0.9, 0), verts=6)
for i, (dx, dy, dz, r) in enumerate(((0, 0, 1.6, 0.62), (-0.42, 0.25, 1.85, 0.45), (0.45, -0.2, 1.9, 0.42), (0.05, 0.1, 2.25, 0.4), (0.1, -0.45, 1.65, 0.3))):
    ball(f"Oak2Leaves{i}", (dx, dy, dz), r, M["Blossom"] if i != 4 else M["Leaves"], P, sub=1)
    ball(f"Snow_Oak2{i}", (dx, dy, dz + r * 0.55), r * 0.9, M["Snow"], P, scale=(1, 1, 0.35), sub=1)

P = kit("Pine")   # bamboo clump
for i in range(5):
    a = i / 5 * math.tau + 0.3
    bx, by = math.cos(a) * 0.22, math.sin(a) * 0.22
    h = 3.0 + (i % 3) * 0.35
    lean = (math.sin(a) * 0.06, -math.cos(a) * 0.06, 0)
    cyl(f"Culm{i}", (bx, by, h / 2), 0.05, h, M["Bamboo"], P, verts=6, rot=lean)
    cyl(f"Node{i}", (bx - lean[1] * 1.4, by + lean[0] * 1.4, 1.4), 0.065, 0.05, M["BambooDark"], P, verts=6)
    tx, ty = bx * 1.6, by * 1.6
    for k in range(2):
        b = a + k * 2.4
        cone(f"PineTier{i}{k}", (tx + math.cos(b) * 0.25, ty + math.sin(b) * 0.25, h - 0.3 + k * 0.15), 0.13, 0.6, M["BambooLeaf"], P, verts=4, rot=(math.sin(b) * 1.2, -math.cos(b) * 1.2, 0))
    ball(f"Snow_Pine{i}", (tx, ty, h + 0.05), 0.28, M["Snow"], P, scale=(1, 1, 0.35), sub=1)

P = kit("DeadTree")   # withered plum with a few red blossoms
cyl("DTTrunk", (0, 0, 0.9), 0.17, 1.8, M["DeadWood"], P, verts=7, r2=0.08, rot=(0.12, 0, 0))
branches = ((0.5, 0.0, 0.3, 1.1), (-0.5, 0.2, 2.2, 0.9), (0.2, -0.6, 4.2, 0.8), (0.0, 0.55, 1.4, 0.7))
for i, (rx, ry, rz, h) in enumerate(branches):
    cyl(f"DTBranch{i}", (math.cos(rz) * 0.35, math.sin(rz) * 0.35, 1.5 + i * 0.25), 0.06, h, M["DeadWood"], P, rot=(rx, ry, rz), verts=5, r2=0.02)
for i in range(6):
    a = i * 2.4
    cone(f"PlumBlossom{i}", (math.cos(a) * (0.45 + (i % 3) * 0.2), math.sin(a) * (0.4 + (i % 2) * 0.25), 1.7 + (i % 4) * 0.28), 0.07, 0.1, M["PlumBlossom"], P, verts=4, rot=(a, 0.5, 0))

P = kit("Stump")
cyl("StumpBody", (0, 0, 0.22), 0.32, 0.44, M["Trunk"], P, verts=9, r2=0.28)
cyl("StumpTop", (0, 0, 0.45), 0.26, 0.03, M["WoodLight"], P, verts=9)
for i in range(3):
    a = i * 2.1
    box(f"StumpRoot{i}", (math.cos(a) * 0.36, math.sin(a) * 0.36, 0.06), (0.3, 0.14, 0.12), M["Trunk"], P, rot=(0, 0, a), bevel=0.0)
cyl("StumpShoot", (0.2, -0.15, 0.7), 0.03, 0.5, M["Bamboo"], P, verts=5)

# ---------------------------------------------------------------- rocks & ruins
P = kit("Rock_S")   # small scholar's rock
ball("RockS", (0, 0, 0.3), 0.3, M["StoneLight"], P, scale=(0.9, 0.7, 1.3), sub=1, rot=(0.2, 0, 0.4))
ball("RockS2", (0.25, 0.1, 0.18), 0.2, M["Stone"], P, scale=(1.1, 0.9, 0.9), sub=0)
ball("RockS3", (-0.15, -0.12, 0.55), 0.16, M["StoneLight"], P, scale=(1, 0.8, 1.2), sub=0)
box("Snow_RockS", (0, 0, 0.66), (0.45, 0.4, 0.06), M["Snow"], P, bevel=0.02)

P = kit("Rock_L")   # tall pierced scholar's rock
ball("RockL", (0, 0, 0.7), 0.75, M["StoneLight"], P, scale=(1.0, 0.75, 1.5), sub=1, rot=(0.15, 0.1, 0.5))
torus("RockLHole", (0.1, 0, 1.15), 0.42, 0.22, M["Stone"], P, rot=(math.pi / 2, 0, 0.2), segs=(10, 6))
ball("RockL2", (0.8, -0.2, 0.35), 0.45, M["Stone"], P, scale=(1.0, 0.9, 1.1), sub=1)
ball("RockL3", (-0.7, 0.3, 0.3), 0.4, M["StoneLight"], P, scale=(1.0, 1.1, 0.9), sub=1)
ball("RockLMoss", (0.2, 0.0, 0.2), 0.5, M["Moss"], P, scale=(1.5, 1.2, 0.3), sub=1)
box("Snow_RockL", (0, 0, 1.75), (0.9, 0.7, 0.08), M["Snow"], P, bevel=0.03)

P = kit("Boulder")   # great pierced rock with moss cap
ball("Boulder", (0, 0, 0.9), 1.3, M["Stone"], P, scale=(1.2, 0.9, 1.1), sub=1, rot=(0.3, 0.2, 1.0))
torus("BoulderHole", (0.3, -0.1, 1.5), 0.6, 0.3, M["StoneLight"], P, rot=(math.pi / 2, 0, 0.6), segs=(12, 7))
ball("Boulder2", (-1.0, 0.4, 0.5), 0.7, M["StoneLight"], P, scale=(1.0, 1.0, 1.2), sub=1)
ball("BoulderMoss", (0.2, 0.1, 1.85), 0.9, M["Moss"], P, scale=(1.1, 0.9, 0.3), sub=1)
box("Snow_Boulder", (0, 0, 1.95), (2.2, 1.8, 0.1), M["Snow"], P, bevel=0.04)

P = kit("Column")   # great sword planted in the ground (sword tomb)
g = empty("SwordGrp"); g.parent = P; g.location = (0, 0, 0); g.rotation_euler = (0.18, -0.12, 0.4)
box("SwBlade", (0, 0, 1.5), (0.5, 0.12, 2.6), M["Steel"], g, bevel=0.02)
box("SwFuller", (0, -0.065, 1.5), (0.12, 0.01, 2.2), M["Iron"], g, bevel=0.0)
box("SwGuard", (0, 0, 2.85), (1.1, 0.28, 0.18), M["Bronze"], g, bevel=0.02)
cyl("SwGrip", (0, 0, 3.25), 0.1, 0.65, M["Rope"], g, verts=8)
ball("SwPommel", (0, 0, 3.65), 0.15, M["Bronze"], g, sub=1)
box("SwTassel", (0.2, 0, 3.4), (0.05, 0.05, 0.4), M["Flag"], g, bevel=0.0, rot=(0, 0.4, 0))
ball("ColMoss", (0.1, 0.1, 0.2), 0.45, M["Moss"], P, scale=(1.5, 1.2, 0.4), sub=1)
ball("ColRubble", (0.5, -0.3, 0.12), 0.2, M["StoneDark"], P, scale=(1.3, 1, 0.6), sub=0)

P = kit("BrokenColumn")   # cracked stele
box("BCBase", (0, 0, 0.15), (1.2, 0.8, 0.3), M["Stone"], P)
box("BCStele", (0, 0, 1.05), (0.8, 0.22, 1.5), M["StoneLight"], P, rot=(0.04, 0, 0.1), bevel=0.02)
cyl("BCCap", (0, 0, 1.8), 0.4, 0.22, M["StoneLight"], P, rot=(math.pi / 2, 0, 0.1), verts=12)
for i in range(3):
    box(f"BCLine{i}", (-0.2 + i * 0.2, -0.12, 1.0), (0.05, 0.02, 1.0), M["StoneDark"], P, rot=(0, 0, 0.1), bevel=0.0)
box("BCChunk", (0.9, 0.4, 0.2), (0.6, 0.25, 0.4), M["StoneLight"], P, rot=(0.3, 0.2, 0.6))
ball("BCMoss", (0.5, 0.4, 0.3), 0.35, M["Moss"], P, scale=(1.3, 1.0, 0.4), sub=1)

P = kit("RuinWall")   # broken white garden wall with tile coping
box("RWBase", (0, 0, 0.3), (3.0, 0.5, 0.6), M["Stone"], P)
box("RWLeft", (-1.1, 0, 1.3), (0.8, 0.4, 1.4), M["Wall"], P)
box("RWMid", (0.0, 0, 1.0), (0.9, 0.4, 0.8), M["WallDark"], P)
box("RWRight", (1.15, 0, 1.55), (0.7, 0.4, 1.9), M["Wall"], P)
wedge("RWCopeL", (-1.1, 0, 1.98), 0.9, 0.6, 0.18, M["RoofDark"], P)
wedge("RWCopeR", (1.15, 0, 2.48), 0.8, 0.6, 0.18, M["RoofDark"], P)
box("RWRubble", (1.9, 0.5, 0.2), (0.6, 0.5, 0.4), M["Stone"], P, rot=(0, 0, 0.5))
ball("RWMoss", (-0.6, -0.26, 0.9), 0.5, M["Moss"], P, scale=(1.3, 0.2, 1.0), sub=1)
box("Snow_RW", (0, 0, 0.63), (3.0, 0.5, 0.08), M["Snow"], P, bevel=0.02)

P = kit("RuinArch")   # stone paifang gateway
for sx in (-1, 1):
    box(f"RAPillar{sx}", (sx * 1.4, 0, 1.7), (0.45, 0.45, 3.4), M["Stone"], P)
    ball(f"RADrum{sx}", (sx * 1.4, -0.35, 0.3), 0.3, M["StoneLight"], P, scale=(1, 0.5, 1), sub=1)
    cyl(f"RAFoot{sx}", (sx * 1.4, 0, 0.15), 0.42, 0.3, M["StoneDark"], P, verts=8)
box("RABeam", (0, 0, 2.6), (3.7, 0.4, 0.35), M["StoneDark"], P)
box("RABeam2", (0, 0, 3.3), (3.5, 0.36, 0.3), M["StoneDark"], P)
box("RAPlaque", (0, 0, 2.95), (1.1, 0.14, 0.5), M["Wall"], P)
box("RAPlaqueMark", (0, -0.08, 2.95), (0.7, 0.02, 0.3), M["Flag"], P, bevel=0.0)
eave_roof(P, 0, 0, 3.45, 4.2, 1.0, 0.4, tiles=False, tag="G", snow=True)
ball("RAMoss", (-1.4, -0.3, 1.5), 0.4, M["Moss"], P, scale=(1.0, 0.3, 1.3), sub=1)

P = kit("Shrine")   # spirit-vein array
cyl("ShrineBase", (0, 0, 0.15), 1.35, 0.3, M["StoneDark"], P, verts=8)
cyl("ShrineStep", (0, 0, 0.42), 0.95, 0.24, M["Stone"], P, verts=8)
for i in range(8):
    a = i / 8 * math.tau + math.pi / 8
    for k in range(3):
        broken = (i + k) % 2 == 1
        for s in ((-1, 1) if broken else (0,)):
            L = 0.15 if broken else 0.34
            box(f"Trigram{i}{k}{s}", (math.cos(a) * (1.02 + k * 0.1) + math.sin(a) * s * 0.1, math.sin(a) * (1.02 + k * 0.1) - math.cos(a) * s * 0.1, 0.31), (0.06, L, 0.04), M["StoneLight"], P, rot=(0, 0, a), bevel=0.0)
cyl("ShrinePillar", (0, 0, 1.05), 0.3, 1.3, M["Stone"], P, verts=8, r2=0.24)
cone("Crystal_Gem", (0, 0, 2.35), 0.32, 1.3, M["Crystal"], P, verts=6)
cone("Crystal_GemBase", (0, 0, 1.55), 0.32, 0.4, M["Crystal"], P, verts=6, rot=(math.pi, 0, 0))
for i in range(3):
    a = i / 3 * math.tau + 0.6
    cone(f"Crystal_Orbit{i}", (math.cos(a) * 0.65, math.sin(a) * 0.65, 1.9 + (i % 2) * 0.3), 0.08, 0.35, M["Crystal"], P, verts=5, rot=(0.3, 0, a))
for i in range(4):
    a = i / 4 * math.tau + 0.4
    cyl(f"ShrinePost{i}", (math.cos(a) * 0.85, math.sin(a) * 0.85, 0.9), 0.06, 0.7, M["StoneLight"], P, verts=6)
    box(f"ShrineLamp{i}", (math.cos(a) * 0.85, math.sin(a) * 0.85, 1.35), (0.16, 0.16, 0.2), M["Lantern"], P, bevel=0.0)
    cone(f"ShrineLampCap{i}", (math.cos(a) * 0.85, math.sin(a) * 0.85, 1.52), 0.16, 0.12, M["StoneDark"], P, verts=6)

# ---------------------------------------------------------------- ground cover
P = kit("Bush")   # orchid clump
for i in range(8):
    a = i / 8 * math.tau
    cone(f"OrchidLeaf{i}", (math.cos(a) * 0.12, math.sin(a) * 0.12, 0.3), 0.05, 0.7, M["Orchid"], P, rot=(math.sin(a) * 0.7, -math.cos(a) * 0.7, 0), verts=4)
ball("OrchidBase", (0, 0, 0.12), 0.25, M["Bush"], P, scale=(1.2, 1.2, 0.5), sub=1)
for i in range(2):
    ball(f"OrchidFlower{i}", (0.15 - i * 0.35, 0.1 * i, 0.55 + i * 0.1), 0.05, M["Blossom"], P, sub=0)
ball("Snow_Bush", (0, 0, 0.35), 0.4, M["Snow"], P, scale=(1.1, 1, 0.3), sub=1)

P = kit("Tuft")
for i in range(5):
    a = i / 5 * math.tau
    cone(f"Blade{i}", (math.cos(a) * 0.1, math.sin(a) * 0.1, 0.22), 0.06, 0.5, M["Grass"] if i % 2 else M["Orchid"], P, rot=(math.sin(a) * 0.35, math.cos(a) * 0.35, 0), verts=4)

P = kit("Mushroom")   # lingzhi
cyl("MStem", (0, 0.08, 0.12), 0.05, 0.26, M["MushroomStem"], P, verts=7, rot=(0.3, 0, 0))
ball("MCap", (0, -0.08, 0.3), 0.22, M["Mushroom"], P, scale=(1.4, 1.0, 0.3), sub=1)
ball("MCapRim", (0, -0.14, 0.27), 0.22, M["LingzhiRim"], P, scale=(1.5, 1.05, 0.12), sub=1)
cyl("MStem2", (0.3, 0.12, 0.08), 0.035, 0.16, M["MushroomStem"], P, verts=7)
ball("MCap2", (0.3, 0.05, 0.18), 0.13, M["Mushroom"], P, scale=(1.4, 1.0, 0.3), sub=1)

P = kit("Reed")
for i in range(5):
    a = i / 5 * math.tau
    cyl(f"ReedStem{i}", (math.cos(a) * 0.18, math.sin(a) * 0.18, 0.55), 0.025, 1.1 + (i % 3) * 0.2, M["Reed"], P, rot=(math.sin(a) * 0.1, math.cos(a) * 0.1, 0), verts=4)
    cyl(f"ReedHead{i}", (math.cos(a) * 0.2, math.sin(a) * 0.2, 1.05 + (i % 3) * 0.2), 0.05, 0.25, M["ReedHead"], P, verts=5)

P = kit("EmberRock")   # lava rock with fire cracks
ball("ERock", (0, 0, 0.25), 0.5, M["Ash"], P, scale=(1.3, 1.0, 0.7), sub=1)
for i in range(4):
    a = i / 4 * math.tau
    box(f"Fire_Crack{i}", (math.cos(a) * 0.35, math.sin(a) * 0.3, 0.28), (0.25, 0.05, 0.12), M["Fire"], P, rot=(0, 0, a), bevel=0.0)

# ---------------------------------------------------------------- pickups
P = kit("Ember")   # spirit stone (octahedron)
cone("Crystal_EmberT", (0, 0, 0.5), 0.17, 0.32, M["Crystal"], P, verts=4)
cone("Crystal_EmberB", (0, 0, 0.18), 0.17, 0.32, M["Crystal"], P, verts=4, rot=(math.pi, 0, 0))

P = kit("Shard")   # gold spirit crystal
for i, (dx, dy, h, r) in enumerate(((0, 0, 0.5, 0.11), (0.14, 0.06, 0.34, 0.08), (-0.1, 0.1, 0.3, 0.07))):
    cone(f"Crystal_Shard{i}", (dx, dy, h / 2), r, h, M["ShardCrystal"], P, verts=5)

P = kit("Heart")   # elixir pill
ball("Fire_Pill", (0, 0, 0.4), 0.2, M["Pill"], P, sub=2)
box("Fire_PillBand", (0, 0, 0.4), (0.44, 0.44, 0.05), M["Pill"], P, bevel=0.0, rot=(0, 0, 0.5))

# ---------------------------------------------------------------- market & landmarks (polish pass)
P = kit("Stall")   # market stall with a cinnabar awning
box("StallTable", (0, 0, 0.7), (1.8, 0.9, 0.08), M["WoodLight"], P)
box("StallCloth", (0, -0.47, 0.35), (1.8, 0.04, 0.7), M["CloakDark"], P, bevel=0.0)
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl(f"StallLeg{sx}{sy}", (sx * 0.8, sy * 0.38, 0.35), 0.04, 0.7, M["Timber"], P, verts=6)
        cyl(f"StallPost{sx}{sy}", (sx * 0.95, sy * 0.52, 1.2), 0.04, 2.4, M["Timber"], P, verts=6)
wedge("StallAwning", (0, 0, 2.3), 2.3, 1.5, 0.4, M["Flag"], P)
box("StallAwningHem", (0, -0.74, 2.28), (2.3, 0.06, 0.14), M["Wall"], P, bevel=0.0)
box("StallAwningHem2", (0, 0.74, 2.28), (2.3, 0.06, 0.14), M["Wall"], P, bevel=0.0)
for i, (gx, gy) in enumerate(((-0.55, 0.1), (-0.2, -0.15))):
    ball(f"StallJar{i}", (gx, gy, 0.9), 0.15, M["Clay"], P, scale=(1, 1, 1.1), sub=1)
    cyl(f"StallJarLid{i}", (gx, gy, 1.06), 0.07, 0.04, M["Flag"], P, verts=8)
for i in range(3):
    ball(f"StallHerb{i}", (0.3 + i * 0.22, 0.12 - (i % 2) * 0.25, 0.82), 0.11, M["Herb"] if i % 2 else M["HerbDark"], P, scale=(1.2, 1, 0.7), sub=0)
for i in range(2):
    cyl(f"StallScroll{i}", (0.55, -0.25 + i * 0.16, 0.8), 0.05, 0.5, M["Wall"], P, rot=(0, math.pi / 2, 0), verts=7)
hang_lantern(P, -0.95, -0.6, 1.95, "S")

P = kit("Banner")   # tall vertical cloth banner
cyl("BnPole", (0, 0, 2.0), 0.05, 4.0, M["Timber"], P, verts=6)
box("BnArm", (0.35, 0, 3.9), (0.8, 0.04, 0.04), M["Timber"], P, bevel=0.0)
box("BnCloth", (0.45, 0, 2.7), (0.5, 0.03, 2.3), M["Flag"], P, bevel=0.0)
box("BnStripe", (0.45, -0.03, 2.7), (0.2, 0.01, 1.6), M["Wall"], P, bevel=0.0)
box("BnTassel", (0.45, 0, 1.45), (0.5, 0.03, 0.2), M["Belt"], P, bevel=0.0)
cyl("BnBase", (0, 0, 0.1), 0.2, 0.2, M["StoneDark"], P, verts=8)
cone("BnTop", (0, 0, 4.05), 0.06, 0.15, M["Bronze"], P, verts=6)

P = kit("SwordMonument")   # sword-tomb tablet ringed by planted blades
box("SMBase", (0, 0, 0.25), (3.0, 2.0, 0.5), M["Stone"], P)
box("SMTablet", (0, 0.3, 1.9), (1.6, 0.35, 2.8), M["StoneLight"], P, bevel=0.03)
cyl("SMCap", (0, 0.3, 3.3), 0.8, 0.35, M["StoneLight"], P, rot=(math.pi / 2, 0, 0), verts=12)
for i in range(3):
    box(f"SMLine{i}", (-0.4 + i * 0.4, 0.11, 1.7), (0.06, 0.02, 1.6), M["StoneDark"], P, bevel=0.0)
box("EmberCore_SMRune", (0, 0.11, 2.85), (0.5, 0.02, 0.5), M["EmberCore"], P, bevel=0.0, rot=(0, math.pi / 4, 0))
for i, (sx, sy, rz) in enumerate(((-1.15, -0.7, 0.3), (1.15, -0.6, -0.4), (-0.5, -1.25, 0.8), (0.7, -1.3, -0.9))):
    g = empty(f"SMSwordGrp{i}"); g.parent = P; g.location = (sx, sy, 0.5); g.rotation_euler = (0.15 * (i % 2), -0.1, rz)
    box(f"SMBlade{i}", (0, 0, 0.8), (0.22, 0.06, 1.5), M["Steel"], g, bevel=0.0)
    box(f"SMGuard{i}", (0, 0, 1.55), (0.5, 0.12, 0.1), M["Bronze"], g, bevel=0.0)
    cyl(f"SMGrip{i}", (0, 0, 1.78), 0.05, 0.36, M["Rope"], g, verts=6)
    ball(f"SMPommel{i}", (0, 0, 2.0), 0.07, M["Bronze"], g, sub=0)
ball("SMMoss", (0.9, 0.6, 0.55), 0.5, M["Moss"], P, scale=(1.3, 1, 0.3), sub=1)

P = kit("LavaFissure")   # cracked slab bleeding earth-fire
ball("LFSlab", (0, 0, 0.12), 1.6, M["Ash"], P, scale=(1.4, 1.0, 0.18), sub=1)
for i, (x, y, rz, l) in enumerate(((0, 0, 0.3, 2.4), (-0.6, 0.4, 1.4, 1.2), (0.7, -0.3, -0.9, 1.4), (0.2, 0.8, 0.1, 0.9))):
    box(f"Fire_LF{i}", (x, y, 0.3), (l, 0.12, 0.06), M["Fire"], P, rot=(0, 0, rz), bevel=0.0)
cyl("Fire_LFPool", (0.9, 0.7, 0.28), 0.45, 0.04, M["Fire"], P, verts=10)
for i in range(5):
    a = i * 1.3
    ball(f"LFRock{i}", (math.cos(a) * 1.9, math.sin(a) * 1.4, 0.22), 0.3, M["AshLight"], P, scale=(1.2, 1, 0.7), sub=0)

P = kit("LotusPond")   # stone-rimmed pond with lotus and a plank
cyl("LPWater", (0, 0, 0.06), 2.6, 0.12, M["Water"], P, verts=16)
for i in range(16):
    a = i / 16 * math.tau
    box(f"LPRim{i}", (math.cos(a) * 2.7, math.sin(a) * 2.7, 0.15), (1.1, 0.32, 0.3), M["Stone"], P, rot=(0, 0, a + math.pi / 2), bevel=0.0)
for i in range(7):
    a = i * 0.9 + 0.3; r = 0.6 + (i % 3) * 0.6
    cyl(f"LPPad{i}", (math.cos(a) * r, math.sin(a) * r, 0.14), 0.32 + (i % 2) * 0.1, 0.02, M["MudLight"], P, verts=9)
for i in range(3):
    a = i * 2.1 + 1.0; r = 1.1
    cyl(f"LPStem{i}", (math.cos(a) * r, math.sin(a) * r, 0.4), 0.02, 0.55, M["HerbDark"], P, verts=5)
    cone(f"LPLotus{i}", (math.cos(a) * r, math.sin(a) * r, 0.75), 0.18, 0.3, M["Blossom"], P, verts=7, r2=0.06, rot=(math.pi, 0, 0))
    ball(f"LPHeart{i}", (math.cos(a) * r, math.sin(a) * r, 0.82), 0.07, M["Hay"], P, sub=0)
box("LPPlank", (0, -1.6, 0.34), (0.5, 2.4, 0.08), M["WoodLight"], P)

P = kit("BambooGiant")   # three giant culms
for i in range(3):
    a = i / 3 * math.tau; bx, by = math.cos(a) * 0.5, math.sin(a) * 0.5; h = 6.5 + i * 0.6
    cyl(f"GCulm{i}", (bx, by, h / 2), 0.16, h, M["Bamboo"], P, verts=8)
    for k in range(5):
        cyl(f"GNode{i}{k}", (bx, by, 0.9 + k * 1.2), 0.19, 0.08, M["BambooDark"], P, verts=8)
    for k in range(4):
        b = a + k * 1.6
        cone(f"GLeaf{i}{k}", (bx + math.cos(b) * 0.5, by + math.sin(b) * 0.5, h - 0.6 + k * 0.25), 0.25, 1.2, M["BambooLeaf"], P, verts=4, rot=(math.sin(b) * 1.2, -math.cos(b) * 1.2, 0))

M["Jade"] = mat("Jade", "#8fc9b0"); M["JadeDark"] = mat("JadeDark", "#5f9a84"); M["ZheLeaf"] = mat("ZheLeaf", "#3b5a3a"); M["ZheBark"] = mat("ZheBark", "#3a2e28")
M["CassiaLeaf"] = mat("CassiaLeaf", "#4f7f4a"); M["CassiaGold"] = mat("CassiaGold", "#e8b83a"); M["ZhenLeaf"] = mat("ZhenLeaf", "#7fae62"); M["MiguBark"] = mat("MiguBark", "#2a2326")
M["MiguLeaf"] = mat("MiguLeaf", "#4a6040"); M["Zhuyu"] = mat("Zhuyu", "#6fa86a"); M["ZhuyuFlower"] = mat("ZhuyuFlower", "#5aa0d8"); M["BlackWater"] = mat("BlackWater", "#1c2230", rough=0.15)
M["Cinnabar"] = mat("Cinnabar", "#b8402a"); M["Twig"] = mat("Twig", "#5a4632"); M["SunGold"] = mat("SunGold", "#ffd36a", rough=0.3, emit="#ffb340", strength=5.0)
M["Feather"] = mat("Feather", "#6e4436"); M["FeatherDark"] = mat("FeatherDark", "#3f2a24"); M["Sack"] = mat("Sack", "#d9a441"); M["FoxFur"] = mat("FoxFur", "#e8d9b8"); M["FoxDark"] = mat("FoxDark", "#c9a56a")
M["Ox"] = mat("Ox", "#2e2a2c"); M["Wool"] = mat("Wool", "#cfc6b4"); M["Bristle"] = mat("Bristle", "#5a4a3c")
P = kit("Crane")   # 凤皇 (丹穴之山): five-coloured, "见则天下安宁" — flown by the page high over the valley
ball("FhBody", (0, 0, 0), 0.24, M["Flag"], P, scale=(0.7, 1.6, 0.6), sub=1)
cyl("FhNeck", (0, -0.45, 0.12), 0.05, 0.5, M["CassiaGold"], P, rot=(1.2, 0, 0), verts=6)
ball("FhHead", (0, -0.7, 0.28), 0.1, M["Flag"], P, sub=0)
for k in range(3):
    box(f"FhCrest{k}", (0, -0.7 - k * 0.04, 0.38 + k * 0.06), (0.03, 0.1, 0.04), M["CassiaGold"] if k % 2 else M["Jade"], P, bevel=0.0, rot=(0.5 + k * 0.3, 0, 0))
cone("FhBeak", (0, -0.86, 0.26), 0.03, 0.2, M["Belt"], P, verts=4, rot=(math.pi / 2, 0, 0))
for sx in (-1, 1):
    box(f"FhWing{sx}", (sx * 0.75, 0.05, 0.05), (1.3, 0.5, 0.04), M["CassiaGold"], P, bevel=0.0, rot=(0, sx * 0.12, 0))
    box(f"FhWingTip{sx}", (sx * 1.45, 0.1, 0.12), (0.4, 0.36, 0.03), M["Jade"], P, bevel=0.0, rot=(0, sx * 0.25, 0))
    box(f"FhWingBar{sx}", (sx * 0.75, 0.3, 0.06), (1.2, 0.08, 0.05), M["CloakDark"], P, bevel=0.0, rot=(0, sx * 0.12, 0))
for k, col in enumerate(("Flag", "Jade", "CloakDark", "CassiaGold", "Blossom")):
    box(f"FhTail{k}", (0.12 * (k - 2), 0.75 + abs(k - 2) * 0.1, 0.02), (0.08, 1.1, 0.03), M[col], P, bevel=0.0, rot=(0, 0, 0.18 * (k - 2)))
for sx in (-1, 1):
    cyl(f"FhLeg{sx}", (sx * 0.06, 0.15, -0.2), 0.015, 0.35, M["Belt"], P, rot=(-0.4, 0, 0), verts=4)

# ---------------------------------------------------------------- Shanhai scenery: trees, herbs and landmarks of the five mountain classics

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

# ---------------------------------------------------------------- Player rig: robed cultivator with a spirit lamp and a flying sword
P = kit("Player")
body = empty("P_Body"); body.parent = P
cone("Cloak", (0, 0, 0.55), 0.42, 1.1, M["Cloak"], body, verts=12, r2=0.22)
cyl("Hem", (0, 0, 0.04), 0.42, 0.07, M["CloakDark"], body, verts=12)
box("RobePanel", (0, -0.335, 0.5), (0.11, 0.02, 0.9), M["CloakDark"], body, bevel=0.0, rot=(0.18, 0, 0))
ball("JadePendant", (-0.2, -0.25, 0.66), 0.05, M["Crystal"], body, sub=0)
cyl("Belt", (0, 0, 0.78), 0.28, 0.1, M["Belt"], body, verts=12)
box("SashKnot", (0, -0.27, 0.74), (0.12, 0.05, 0.16), M["Belt"], body, bevel=0.0)
box("SashTail", (0.04, -0.27, 0.55), (0.06, 0.03, 0.3), M["Belt"], body, bevel=0.0)
box("Buckle", (0, -0.29, 0.79), (0.08, 0.03, 0.08), M["HotMetal"], body, bevel=0.0)
for sx in (-1, 1):
    box(f"Boot{sx}", (sx * 0.13, -0.03, 0.06), (0.14, 0.24, 0.12), M["Boot"], body, bevel=0.01)
cyl("Collar", (0, 0, 1.1), 0.24, 0.14, M["CloakDark"], body, verts=12, r2=0.32)
ball("GourdA", (0.3, 0.12, 0.66), 0.08, M["Gourd"], body, sub=1)
ball("GourdB", (0.3, 0.12, 0.78), 0.06, M["Gourd"], body, sub=1)
box("BackScroll", (-0.18, 0.28, 0.95), (0.1, 0.1, 0.5), M["WoodLight"], body, rot=(0, 0.3, 0.2), bevel=0.01)
head = empty("P_Head"); head.parent = body; head.location = (0, 0, 1.18)
ball("Head", (0, 0, 0.22), 0.24, M["Skin"], head, sub=1)
ball("Hair", (0, 0.04, 0.32), 0.25, M["Hair"], head, scale=(1, 1, 0.8), sub=1)
ball("Topknot", (0, 0.03, 0.52), 0.1, M["Hair"], head, sub=1)
cyl("Hairpin", (0, 0.03, 0.54), 0.015, 0.4, M["Bronze"], head, rot=(0, math.pi / 2, 0), verts=4)
box("HairTail", (0, 0.22, 0.05), (0.18, 0.08, 0.32), M["Hair"], head, bevel=0.01)
box("Ribbon", (0.12, 0.22, -0.02), (0.04, 0.02, 0.24), M["Flag"], head, bevel=0.0)
for sx in (-1, 1):
    ball(f"Eye{sx}", (sx * 0.09, -0.21, 0.22), 0.035, M["Hair"], head, sub=0)
arm_l = empty("P_ArmL"); arm_l.parent = body; arm_l.location = (-0.36, 0, 1.0)
cyl("ArmL", (0, -0.05, -0.28), 0.15, 0.55, M["Cloak"], arm_l, verts=8, rot=(-0.2, 0, 0), r2=0.08)
cyl("CuffL", (0, -0.1, -0.53), 0.16, 0.05, M["CloakDark"], arm_l, verts=8, rot=(-0.2, 0, 0))
ball("HandL", (0, -0.12, -0.56), 0.08, M["Skin"], arm_l, sub=0)
lan = empty("P_Lantern"); lan.parent = arm_l; lan.location = (0, -0.15, -0.6)
cyl("LanHook", (0, 0, -0.06), 0.015, 0.12, M["Bronze"], lan, verts=4)
cyl("LanRingT", (0, 0, -0.13), 0.1, 0.03, M["Bronze"], lan, verts=8)
ball("PlayerLamp_Glow", (0, 0, -0.27), 0.13, M["PlayerLamp"], lan, scale=(1, 1, 1.25), sub=1)
cyl("LanRingB", (0, 0, -0.42), 0.09, 0.03, M["Bronze"], lan, verts=8)
cyl("LanRingM", (0, 0, -0.27), 0.135, 0.015, M["Bronze"], lan, verts=8)
box("LanTassel", (0, 0, -0.52), (0.03, 0.03, 0.14), M["Flag"], lan, bevel=0.0)
arm_r = empty("P_ArmR"); arm_r.parent = body; arm_r.location = (0.36, 0, 1.0)
cyl("ArmR", (0, -0.05, -0.28), 0.15, 0.55, M["Cloak"], arm_r, verts=8, rot=(-0.2, 0, 0), r2=0.08)
cyl("CuffR", (0, -0.1, -0.53), 0.16, 0.05, M["CloakDark"], arm_r, verts=8, rot=(-0.2, 0, 0))
ball("HandR", (0, -0.12, -0.56), 0.08, M["Skin"], arm_r, sub=0)
blade = empty("P_Blade"); blade.parent = arm_r; blade.location = (0, -0.15, -0.58)
cyl("Hilt", (0, 0.05, 0), 0.03, 0.26, M["Belt"], blade, verts=6, rot=(math.pi / 2, 0, 0))
ball("Pommel", (0, 0.19, 0), 0.04, M["Bronze"], blade, sub=0)
box("Guard", (0, -0.1, 0), (0.22, 0.05, 0.05), M["Bronze"], blade, bevel=0.0)
box("SwordBlade", (0, -0.5, 0), (0.08, 0.72, 0.025), M["Steel"], blade, bevel=0.0)
cone("SwordTip", (0, -0.93, 0), 0.04, 0.16, M["Steel"], blade, verts=4, rot=(math.pi / 2, 0, 0))
box("PlayerLamp_Rune", (0, -0.5, 0), (0.02, 0.5, 0.035), M["PlayerLamp"], blade, bevel=0.0)
box("SwordTassel", (0.08, 0.14, -0.05), (0.03, 0.03, 0.14), M["Flag"], blade, bevel=0.0)
P_RIG = (body, head, arm_l, arm_r)

# ---------------------------------------------------------------- enemies (Z up; front = -Y) — Classic of Mountains and Seas
def eyes(P, y, z, sep=0.12, r=0.05):
    for sx in (-1, 1):
        ball(f"EnemyEye_{sx}", (sx * sep, y, z), r, M["EnemyEye"], P, sub=0)


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

# ---------------------------------------------------------------- animations (keyframes on the rig empties, one NLA track per clip)
# Every clip starts from the rest pose at frame 0 so the web side can play the one-shots additively.
scene.render.fps = 24
RIG_P = {"body": P_RIG[0], "head": P_RIG[1], "armL": P_RIG[2], "armR": P_RIG[3]}
RIG_W = {"body": wb, "head": wh, "armL": wl, "armR": wr}

def _rest(objs):
    for o in objs.values():
        o.rotation_euler = (0, 0, 0)
        o.location = (o.get("rest_x", o.location.x), o.get("rest_y", o.location.y), o.get("rest_z", o.location.z))

def clip(name, objs, frames, keys, loop=True):
    """keys: {objkey: {frame: {"rot": (x,y,z), "loc": (dx,dy,dz)}}} — loc is an offset from the rest location."""
    for o in objs.values():
        for k in ("rest_x", "rest_y", "rest_z"):
            if k not in o:
                o["rest_x"], o["rest_y"], o["rest_z"] = o.location.x, o.location.y, o.location.z
    for key, o in objs.items():
        if o.animation_data is None:
            o.animation_data_create()
        act = bpy.data.actions.new(f"{name}__{key}")
        o.animation_data.action = act
        kf = keys.get(key, {})
        frame_list = sorted(set([0, frames] + list(kf.keys())))
        for f in frame_list:
            rest = {"rot": (0, 0, 0), "loc": (0, 0, 0)}
            if f in kf:
                v = kf[f]
            elif f == 0 or not kf:
                v = rest
            else:
                # last frame: loops return to the frame-0 pose, one-shots hold the last authored pose
                v = kf.get(0, rest) if loop else kf[max(kf.keys())]
            rot = v.get("rot", (0, 0, 0)); loc = v.get("loc", (0, 0, 0))
            o.rotation_euler = rot
            o.location = (o["rest_x"] + loc[0], o["rest_y"] + loc[1], o["rest_z"] + loc[2])
            o.keyframe_insert(data_path="rotation_euler", frame=f)
            o.keyframe_insert(data_path="location", frame=f)
        o.animation_data.action = None
        track = o.animation_data.nla_tracks.new()
        track.name = name
        strip = track.strips.new(name, 0, act)
        strip.name = name
    _rest(objs)

R = lambda x=0, y=0, z=0: {"rot": (x, y, z)}
RL = lambda rot=(0, 0, 0), loc=(0, 0, 0): {"rot": rot, "loc": loc}

# ---- player
clip("P_idle", RIG_P, 48, {
    "body": {0: RL(), 24: RL((0.02, 0, 0), (0, 0, 0.02))},
    "head": {0: R(), 16: R(0, 0.12, 0), 36: R(0, -0.1, 0)},
    "armL": {0: R(-0.25), 24: R(-0.15)},
    "armR": {0: R(-0.2), 24: R(-0.3)},
})
clip("P_walk", RIG_P, 24, {
    "body": {0: RL((0.12, 0, 0.04), (0, 0, 0.0)), 6: RL((0.12, 0, 0), (0, 0, 0.07)), 12: RL((0.12, 0, -0.04), (0, 0, 0.0)), 18: RL((0.12, 0, 0), (0, 0, 0.07))},
    "head": {0: R(0.05, 0, 0), 12: R(-0.03, 0, 0)},
    "armL": {0: R(0.55), 12: R(-0.55)},
    "armR": {0: R(-0.55), 12: R(0.55)},
})
clip("P_attack", RIG_P, 14, {
    "armR": {0: R(), 3: R(0.7, 0.35, 0), 6: R(-2.1, -1.25, 0.2), 9: R(-1.6, -1.0, 0.1), 14: R()},
    "body": {0: R(), 3: R(0.0, -0.25, 0.05), 6: R(0.18, 0.35, -0.12), 14: R()},
    "armL": {0: R(), 6: R(0.5, 0, 0), 14: R()},
}, loop=False)
clip("P_dash", RIG_P, 12, {
    "body": {0: R(), 3: R(0.55, 0, 0), 9: R(0.5, 0, 0), 12: R()},
    "armL": {0: R(), 3: R(0.9, 0, 0), 12: R()},
    "armR": {0: R(), 3: R(0.9, 0, 0), 12: R()},
}, loop=False)

# ---- warden
clip("W_idle", RIG_W, 72, {
    "body": {0: RL(), 36: RL((0.03, 0, 0), (0, 0, 0.08))},
    "head": {0: R(), 24: R(0.05, 0.2, 0), 52: R(-0.05, -0.18, 0)},
    "armL": {0: R(-0.15), 36: R(-0.35, 0, 0.1)},
    "armR": {0: R(-0.15), 36: R(-0.3, 0, -0.1)},
})
clip("W_walk", RIG_W, 36, {
    "body": {0: RL((0.15, 0, 0.06), (0, 0, 0)), 9: RL((0.15, 0, 0), (0, 0, 0.16)), 18: RL((0.15, 0, -0.06), (0, 0, 0)), 27: RL((0.15, 0, 0), (0, 0, 0.16))},
    "head": {0: R(0.06), 18: R(-0.04)},
    "armL": {0: R(0.5), 18: R(-0.5)},
    "armR": {0: R(-0.5), 18: R(0.5)},
})
clip("W_slam", RIG_W, 24, {
    "armL": {0: R(), 12: R(-2.6, 0, 0.3), 16: R(-2.6, 0, 0.3), 19: R(0.9, 0, 0.1), 24: R(0.6, 0, 0)},
    "armR": {0: R(), 12: R(-2.6, 0, -0.3), 16: R(-2.6, 0, -0.3), 19: R(0.9, 0, -0.1), 24: R(0.6, 0, 0)},
    "body": {0: RL(), 12: RL((-0.15, 0, 0), (0, 0, 0.35)), 16: RL((-0.15, 0, 0), (0, 0, 0.35)), 19: RL((0.35, 0, 0), (0, 0, -0.45)), 24: RL((0.25, 0, 0), (0, 0, -0.3))},
    "head": {0: R(), 12: R(-0.4), 19: R(0.5), 24: R(0.4)},
}, loop=False)
clip("W_charge", RIG_W, 12, {
    "body": {0: RL((0.3, 0, 0), (0, 0, -0.1)), 6: RL((0.3, 0, 0), (0, 0, 0.0))},
    "armL": {0: R(1.3, 0, 0.2), 6: R(1.1, 0, 0.2)},
    "armR": {0: R(1.3, 0, -0.2), 6: R(1.1, 0, -0.2)},
    "head": {0: R(0.2), 6: R(0.25)},
})
clip("W_roar", RIG_W, 40, {
    "body": {0: RL(), 10: RL((-0.2, 0, 0), (0, 0, 0.7)), 26: RL((-0.25, 0, 0), (0, 0, 0.75)), 40: RL()},
    "armL": {0: R(), 10: R(-2.8, 0, 0.8), 26: R(-2.9, 0, 0.9), 40: R()},
    "armR": {0: R(), 10: R(-2.8, 0, -0.8), 26: R(-2.9, 0, -0.9), 40: R()},
    "head": {0: R(), 10: R(-0.55), 26: R(-0.6), 40: R()},
}, loop=False)
# ---- more player clips
clip("P_hurt", RIG_P, 10, {
    "body": {0: R(), 3: RL((-0.35, 0, 0), (0, 0.12, 0)), 10: R()},
    "armL": {0: R(), 3: R(-0.9, 0, 0.5), 10: R()},
    "armR": {0: R(), 3: R(-0.9, 0, -0.5), 10: R()},
    "head": {0: R(), 3: R(-0.4), 10: R()},
}, loop=False)
clip("P_death", RIG_P, 26, {
    "body": {0: RL(), 6: RL((-0.3, 0, 0), (0, 0, 0.06)), 16: RL((1.45, 0, 0.1), (0, -0.25, 0.22)), 26: RL((1.45, 0, 0.1), (0, -0.25, 0.22))},
    "armL": {0: R(), 6: R(-0.8, 0, 0.6), 16: R(1.3, 0, 0.9), 26: R(1.3, 0, 0.9)},
    "armR": {0: R(), 6: R(-0.8, 0, -0.6), 16: R(1.3, 0, -0.9), 26: R(1.3, 0, -0.9)},
    "head": {0: R(), 6: R(-0.5), 16: R(0.6), 26: R(0.6)},
}, loop=False)
clip("P_cheer", RIG_P, 22, {
    "armR": {0: R(), 6: R(-3.0, 0, -0.3), 14: R(-3.1, 0, 0.3), 22: R()},
    "armL": {0: R(), 6: R(-0.6, 0, 0.4), 22: R()},
    "body": {0: RL(), 6: RL((-0.1, 0, 0), (0, 0, 0.18)), 10: RL((-0.1, 0, 0), (0, 0, 0.0)), 14: RL((-0.1, 0, 0), (0, 0, 0.14)), 22: RL()},
    "head": {0: R(), 6: R(-0.35), 22: R()},
}, loop=False)
clip("P_heavy", RIG_P, 18, {
    "armR": {0: R(), 4: R(-2.9, 0.4, 0), 8: R(-2.9, 0.4, 0), 11: R(0.6, -0.9, 0.3), 18: R()},
    "armL": {0: R(), 4: R(-2.4, -0.4, 0), 8: R(-2.4, -0.4, 0), 11: R(0.5, 0.8, -0.3), 18: R()},
    "body": {0: RL(), 4: RL((-0.25, 0, 0), (0, 0, 0.1)), 8: RL((-0.25, 0, 0.3), (0, 0, 0.1)), 11: RL((0.45, 0, -0.35), (0, 0, -0.1)), 18: RL()},
    "head": {0: R(), 4: R(-0.3), 11: R(0.35), 18: R()},
}, loop=False)
clip("P_nova", RIG_P, 20, {
    "armR": {0: R(), 5: R(0.9, 0, -0.9), 10: R(-1.4, 0, -1.5), 20: R()},
    "armL": {0: R(), 5: R(0.9, 0, 0.9), 10: R(-1.4, 0, 1.5), 20: R()},
    "body": {0: RL(), 5: RL((0.25, 0, 0), (0, 0, -0.16)), 10: RL((-0.2, 0, 0), (0, 0, 0.22)), 20: RL()},
    "head": {0: R(), 5: R(0.3), 10: R(-0.45), 20: R()},
}, loop=False)
clip("P_look", RIG_P, 60, {
    "armL": {0: R(), 12: R(-0.9, 0, 0.35), 44: R(-0.9, 0, 0.35), 60: R()},
    "head": {0: R(), 12: R(0.25, 0, 0.45), 44: R(0.3, 0, 0.5), 60: R()},
    "body": {0: R(), 12: R(0.05, 0, 0.12), 44: R(0.05, 0, 0.12), 60: R()},
}, loop=False)

# ---- more warden clips
clip("W_hurt", RIG_W, 10, {
    "body": {0: R(), 3: RL((-0.2, 0, 0.08), (0, 0.15, 0)), 10: R()},
    "head": {0: R(), 3: R(-0.35, 0.2, 0), 10: R()},
    "armL": {0: R(), 3: R(-0.5, 0, 0.3), 10: R()},
    "armR": {0: R(), 3: R(-0.5, 0, -0.3), 10: R()},
}, loop=False)
clip("W_summon", RIG_W, 30, {
    "armL": {0: R(), 8: R(-3.0, 0, 0.5), 22: R(-3.05, 0, 0.6), 30: R()},
    "armR": {0: R(), 8: R(0.4, 0, -0.3), 30: R()},
    "body": {0: RL(), 8: RL((-0.15, 0, -0.2), (0, 0, 0.2)), 22: RL((-0.15, 0, -0.25), (0, 0, 0.2)), 30: RL()},
    "head": {0: R(), 8: R(-0.5, -0.3, 0), 22: R(-0.5, -0.3, 0), 30: R()},
}, loop=False)
clip("W_rage", RIG_W, 34, {
    "body": {0: RL(), 6: RL((0.3, 0, 0), (0, 0, -0.5)), 14: RL((-0.35, 0, 0), (0, 0, 0.9)), 26: RL((-0.3, 0, 0), (0, 0, 0.8)), 34: RL()},
    "armL": {0: R(), 6: R(0.8, 0, 0.3), 14: R(-2.4, 0, 1.4), 26: R(-2.5, 0, 1.4), 34: R()},
    "armR": {0: R(), 6: R(0.8, 0, -0.3), 14: R(-2.4, 0, -1.4), 26: R(-2.5, 0, -1.4), 34: R()},
    "head": {0: R(), 6: R(0.4), 14: R(-0.7), 26: R(-0.7), 34: R()},
}, loop=False)
clip("W_death", RIG_W, 40, {
    "body": {0: RL(), 10: RL((-0.3, 0, 0), (0, 0.2, 0.35)), 24: RL((1.35, 0, 0.15), (0, -0.7, 0.55)), 40: RL((1.35, 0, 0.15), (0, -0.7, 0.55))},
    "armL": {0: R(), 10: R(-2.2, 0, 0.7), 24: R(0.9, 0, 1.0), 40: R(0.9, 0, 1.0)},
    "armR": {0: R(), 10: R(-2.2, 0, -0.7), 24: R(0.9, 0, -1.0), 40: R(0.9, 0, -1.0)},
    "head": {0: R(), 10: R(-0.6), 24: R(0.7), 40: R(0.7)},
}, loop=False)
# ---- district elites: the same four clips for each rig (unique names per rig, exporter merges by track name)
for n, rig in MINI.items():
    pre = f"M{n}_"
    clip(pre + "idle", rig, 60, {
        "body": {0: RL(), 30: RL((0.03, 0, 0), (0, 0, 0.08))},
        "head": {0: R(), 20: R(0.05, 0.25, 0), 45: R(-0.05, -0.2, 0)},
        "armL": {0: R(-0.1), 30: R(-0.3, 0, 0.1)},
        "armR": {0: R(-0.1), 30: R(-0.3, 0, -0.1)},
    })
    clip(pre + "walk", rig, 24, {
        "body": {0: RL((0.08, 0, 0.05), (0, 0, 0)), 6: RL((0.08, 0, 0), (0, 0, 0.14)), 12: RL((0.08, 0, -0.05), (0, 0, 0)), 18: RL((0.08, 0, 0), (0, 0, 0.14))},
        "head": {0: R(0.05), 12: R(-0.05)},
        "armL": {0: R(0.6), 12: R(-0.6)},
        "armR": {0: R(-0.6), 12: R(0.6)},
    })
    clip(pre + "attack", rig, 16, {
        "body": {0: RL(), 4: RL((-0.25, 0, 0), (0, 0.3, 0.1)), 8: RL((0.45, 0, 0), (0, -0.5, -0.1)), 16: RL()},
        "head": {0: R(), 4: R(-0.5), 8: R(0.5), 16: R()},
        "armL": {0: R(), 4: R(-1.6, 0, 0.4), 8: R(0.9, 0, 0.2), 16: R()},
        "armR": {0: R(), 4: R(-1.6, 0, -0.4), 8: R(0.9, 0, -0.2), 16: R()},
    }, loop=False)
    clip(pre + "special", rig, 30, {
        "body": {0: RL(), 10: RL((-0.3, 0, 0), (0, 0, 0.5)), 20: RL((-0.3, 0, 0.2), (0, 0, 0.5)), 30: RL()},
        "head": {0: R(), 10: R(-0.7), 20: R(-0.7, 0.3, 0), 30: R()},
        "armL": {0: R(), 10: R(-2.6, 0, 0.7), 20: R(-2.7, 0, 0.9), 30: R()},
        "armR": {0: R(), 10: R(-2.6, 0, -0.7), 20: R(-2.7, 0, -0.9), 30: R()},
    }, loop=False)
    clip(pre + "death", rig, 32, {
        "body": {0: RL(), 8: RL((-0.25, 0, 0), (0, 0.2, 0.3)), 20: RL((1.25, 0, 0.2), (0, -0.5, 0.5)), 32: RL((1.25, 0, 0.2), (0, -0.5, 0.5))},
        "head": {0: R(), 8: R(-0.5), 20: R(0.6), 32: R(0.6)},
        "armL": {0: R(), 8: R(-1.8, 0, 0.6), 20: R(0.8, 0, 0.9), 32: R(0.8, 0, 0.9)},
        "armR": {0: R(), 8: R(-1.8, 0, -0.6), 20: R(0.8, 0, -0.9), 32: R(0.8, 0, -0.9)},
    }, loop=False)
scene.frame_set(0)

# ---------------------------------------------------------------- preview render (kit lineup)
cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 70.0
cam = link(bpy.data.objects.new("Cam", cam_data))
cols = min(8, len(KIT)); rows = (len(KIT) + 7) // 8
cx, cy = (cols - 1) * 3.5, (rows - 1) * 4.0
cam.location = (cx + 40, cy - 40, 42)
target = link(bpy.data.objects.new("CamTarget", None))
target.location = (cx, cy, 1.0)
tc = cam.constraints.new("TRACK_TO"); tc.target = target; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
scene.camera = cam
sun_data = bpy.data.lights.new("Sun", "SUN"); sun_data.energy = 3.0
sun = link(bpy.data.objects.new("Sun", sun_data))
sun.rotation_euler = (math.radians(50), math.radians(-15), math.radians(35))
world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.5, 0.55, 0.65, 1); bg.inputs[1].default_value = 0.8
scene.render.resolution_x, scene.render.resolution_y = (4000, 2500) if "--big" in argv else (1600, 1000)
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.join(OUT, "preview_big.png" if "--big" in argv else "preview.png")
for o in bpy.data.objects:
    if o.name.startswith("Snow_"):
        o.hide_render = True
for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
    try:
        scene.render.engine = engine
        break
    except TypeError:
        continue
if "--no-render" not in argv:
    try:
        bpy.ops.render.render(write_still=True)
        print("preview written:", scene.render.filepath)
    except Exception as e:
        print("render failed:", e)

# ---------------------------------------------------------------- export GLB (kit empties + all descendants)
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.data.objects:
    if o.type in ("MESH", "EMPTY") and o is not target:
        o.select_set(True)
glb = os.path.join(OUT, "site", "assets", "kit.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
                          export_materials="EXPORT", export_normals=False, export_animations=True, export_animation_mode="NLA_TRACKS",
                          export_force_sampling=True, export_lights=False, export_cameras=False)
meshes = sum(1 for o in bpy.data.objects if o.type == "MESH")
tris = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
print(f"exported {glb}: {len(KIT)} kit items, {meshes} meshes, ~{tris} polys, {os.path.getsize(glb)/1e6:.2f} MB")

# 《灯下问道》Lantern Dao · 美术与命名决定

从 Emberlight(`D:\AI\emberlight`)复制而来的仙侠版。原则:引擎、战斗、验证工具全部保留,只换资产、文案、规则语义。

## 定名

| 项 | 决定 |
|---|---|
| 名字 | 《灯下问道》/ Lantern Dao |
| 舞台 | 云隐灵谷:中心山门坊市;西北迷雾竹海、东北剑冢遗迹、东南焚天火域、西南云梦泽 |
| 核心意象 | 灵灯 = 主角命火;灵石 = 经验;灵晶 = 炼器币;丹药 = 回血;天劫 = 8 分钟 BOSS |
| 色板 | 青黛 #2b4a5a / 朱砂 #c8422b / 鎏金 #d9b04a / 宣纸 #f2e9d8 / 墨 #1c1a1f;青瓦 #3e4a54;白墙 #efe6d3 |
| 发光色 | 敌眼 磷绿 #7dffc0;劫主/煞纹 雷紫 #9a5cff;灵石 青 #5fe0c8;灵晶 金 #ffc040;丹药 朱 #ff3a2a;炉火/香火 橙 #ff6a1a;灯 暖黄 |

## 资产映射(会话 X1,`build_kit_xianxia.py`)

Kit 名、骨架节点名(P_*/W_*/M1_..M4_*)、发光材质名、39 条剪辑名全部不变,`site/` 零改动可加载。

| Kit | 仙侠件 | 备注 |
|---|---|---|
| House_A | 飞檐民居 | 白墙红柱、格子窗、双开朱门、檐下挂灯(`Lantern` 材质) |
| House_B | 两层重檐楼阁 | 青灰瓦,二层回廊栏杆 |
| House_C | 茶棚 | 开敞长亭,茶桌茶坛,"茶"幡(`Flag`) |
| Tower | 七层石塔 | 八角收分,每层挑檐,鎏金塔刹;单数层有窗灯 |
| Forge | 炼器坊 | 青铜丹炉(`Fire_Coals`/`Fire_Flame`)、器坯台(`HotBlade` 仍用 `HotMetal`)、地面灵阵 `Crystal_Array` |
| Well | 灵泉 | 八角石栏、荷叶莲花、石牌 |
| LanternPost | 石灯笼 | 四柱不封闭,`LPGlow` 直接可见,不再依赖 `LPCage` 剔除 |
| Fence / Crate / Barrel / Cart / Hay / Logpile | 竹篱笆 / 铜角木箱 / 酒坛 / 独轮车 / 药材筐 / 柴垛 | |
| Campfire | 青铜香炉 | 香灰 `Fire_CF` + 三炷香尖 `Fire_CF2..4` |
| Oak / Oak2 / Pine / DeadTree | 层叠松 / 桃花 / 竹丛 / 枯梅(带红梅) | 竹丛 5 竿 2 节 2 叶,三角面已压到 ~400 |
| Rock_S / Rock_L / Boulder | 太湖石(大件带穿孔 torus) | |
| Column / BrokenColumn | 剑冢插地巨剑 / 残碑 | |
| RuinWall / RuinArch | 断墙(瓦顶压檐)/ 石牌坊 | |
| Shrine | 灵脉法阵 | 八卦爻纹、中央双头灵晶 `Crystal_Gem`、四盏石灯 |
| Bush / Tuft / Mushroom / Reed / EmberRock | 兰草 / 灵草 / 灵芝 / 芦苇(白穗)/ 熔岩石(`Fire_Crack`) | |
| Ember / Shard / Heart | 灵石八面体 / 金灵晶 / 丹药(`Fire_Pill`,材质 `Pill`) | |
| Player | 道袍修士 | 白袍青缘金绦、发髻簪、葫芦、背卷;左手灵灯(`PlayerLamp_Glow`),右手飞剑(`P_Blade`,剑身刻 `PlayerLamp_Rune`) |
| Wisp / Cinder / Crawler / Spitter / Brute | 磷火(`Phosphor` 发光)/ 煞灵(黑雾袍)/ 蛊蜈蚣(5 节 + 4 对腿,`Leg`/`Leg2` 命名保留)/ 蟾妖(`Fire_Maw`)/ 山魈(白脸獠牙) | |
| WolkKing / Sentinel / Salamander / Maw | 雾狼王(白毛 + 雾团)/ 剑冢石傀(背插四剑)/ 赤炎火蜥(`HotMetal_SLCrest`)/ 泽底巨口(荷叶莲花伪装) | 骨架同名,剪辑复用 |
| Stall / Banner | 市集摊位 / 朱砂幡 | 坊市广场(打磨一) |
| SwordMonument / LavaFissure / LotusPond / BambooGiant | 剑碑 / 地火裂隙 / 荷塘 / 巨竹 | 四域地标(打磨一) |
| Crane | 灵鹤 | 上空盘旋的氛围飞禽(打磨三) |
| Warden | 劫主 | 黑袍雷紫纹、白面具、青铜冠、雷紫巨剑 `EmberCore_WBlade` |

顺手修掉的原版 bug:原 `build_kit.py` 的 `RIG_P` 用到的 `body/head` 变量已被精英骨架覆盖,所有 P_* 剪辑实际打在 `M4_Body/M4_Head` 上;本版改为 `P_RIG` 显式捕获,`P_idle` 目标为 `P_Body/P_Head`。

## UI 色板(X4)

| 用途 | 值 |
|---|---|
| 宣纸面板 | rgba(243,235,219,.94),弹窗 rgba(247,241,228,.98),纸纹 = 5px 点状径向渐变 + 135° 线性渐变 |
| 墨字 / 次级 | #1c1a1f / #6a6157 |
| 朱砂(按钮、命火、强调) | #c8422b,深边 #8f2d1f |
| 鎏金(标题、罗盘、灵晶) | #9c7b24(深)/ #b8922e(罗盘边) |
| 青黛(灵气、次级强调) | #2b4a5a,青 #3f8a7a |
| 悬浮文字(计时、横幅) | 米白 #f6efe2 / 金 #f2d27a 带阴影,不落在纸上 |

## 术语表(X2 起界面默认中文)

| 原 | 仙侠 |
|---|---|
| Level / XP / forge shards | 境界 / 灵气 / 灵晶 |
| talent / keystone / rare | 功法 / 本命功法 / 秘传 |
| weapon(crescent / bolt / lantern / bow / chain) | 法宝(飞剑 / 符箓 / 灵珠 / 落雁弓 / 缚灵索) |
| forge / EDGE / MAIL / CHARM | 炼器坊 / 剑锋 / 护体 / 纳灵 |
| shrine / ward | 灵脉法阵 / 护体功法(避雾诀 / 金钟罩 / 踏火诀 / 踏浪步) |
| districts | 山门坊市 / 迷雾竹海 / 剑冢遗迹 / 焚天火域 / 云梦泽 |
| enemies | 磷火 / 煞灵 / 蛊蜈蚣 / 蟾妖 / 山魈 |
| elites / Warden | 雾狼王 / 剑冢石傀 / 赤炎火蜥 / 泽底巨口 / 劫主 |
| dash / nova / heart | 踏云步 / 灵光爆 / 丹药 |
| archive / bestiary / unlock | 道藏 / 妖录 / 机缘 |
| difficulty | 清修 / 修行 / 劫难 |

## 后续会话

X1 资产层、X2 世界层(含中文默认与仙侠术语)、X3 规则层(境界名、天劫落雷)、X4 表现层(宣纸 UI、竖排标题、英文翻译层、去法线瘦身)、X5 音频(五声 pad + 古筝 + 箫,法宝分音)、X6 发布(仓库 lantern-dao、Pages、Artifact)已完成;后续为打磨期(人物 / 场景 / 数值 / 玩法深度),见 `PLAN_xianxia.md`。

from pygame.font import SysFont

SCREEN_WIDTH, SCREEN_HEIGHT = 960, 720

FONT_SMALL = SysFont('notosansscblack', 16)
FONT_MEDIUM = SysFont('notosansscblack', 22)
FONT_LARGE = SysFont('notosansscblack', 28)
FONT_TITLE = SysFont('notosansscblack', 38)

# 通用颜色定义
KURO           = (8, 8, 8) # 黑
SUMI           = (28, 28, 28) # 墨
SHIRONEZUMI    = (189, 192, 186) # 白鼠
SHIRONERI      = (252, 250, 242) # 白練

TEXT_LIGHT     = (235, 235, 245)        # 亮文字，用于标题或高对比文字
TEXT_FAINT     = (180, 180, 200)        # 次级文字，用于描述或注释
LIGHT_PANEL    = (56, 60, 72)           # 面板背景色（深灰 One Dark）
BG_DARK        = (40, 44, 52)           # 主背景色
ONE_DARK       = (22, 25, 29)

# 按钮颜色（基础/悬停）——视觉层级明确、带轻柔亮度变化
BTN_GREEN        = (152, 195, 121)
BTN_GREEN_HOVER  = (184, 218, 137)
BTN_BLUE         = (97, 175, 239)
BTN_BLUE_HOVER   = (135, 195, 255)
BTN_PURPLE       = (198, 120, 221)
BTN_PURPLE_HOVER = (225, 150, 245)
BTN_ORANGE       = (229, 192, 123)
BTN_ORANGE_HOVER = (255, 220, 150)
BTN_GRAY         = (110, 115, 125)
BTN_GRAY_LIGHT   = (165, 170, 180)
BTN_RED          = (224, 108, 117)
BTN_RED_HOVER    = (255, 135, 145)
BTN_CYAN         = (86, 182, 194)
BTN_CYAN_HOVER   = (120, 210, 220)

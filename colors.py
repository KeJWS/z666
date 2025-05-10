import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 960, 720

pygame.font.init()

FONT_SMALL = pygame.font.SysFont('notosansscblack', 16)
FONT_MEDIUM = pygame.font.SysFont('notosansscblack', 22)
FONT_LARGE = pygame.font.SysFont('notosansscblack', 28)
FONT_TITLE = pygame.font.SysFont('notosansscblack', 38)

# 通用颜色定义
KURO             = "#080808" # 黑
SUMI             = "#1C1C1C" # 墨
SHIRONEZUMI      = "#BDC0BA" # 白鼠
GINNEZUMI        = "#91989F" # 银鼠
SHIRONERI        = "#FCFAF2" # 白練
KOKIMURASAKI     = "#4A225D" # 深紫
LAN              = "#0D5661" # 蓝

SHEN_ZI_SE       = "#220c2c"
SHEN_LAN_SE      = "#08262b"
SHEN_ZONG_SE     = "#271f10"

TEXT_LIGHT       = "#EBEBF5"  # 亮文字，用于标题或高对比文字
TEXT_FAINT       = "#B4B4C8"  # 次级文字，用于描述或注释
LIGHT_PANEL      = "#383C48"  # 面板背景色（深灰 One Dark）
BG_DARK          = "#282C34"  # 主背景色
ONE_DARK         = "#16191D"

# 按钮颜色（基础/悬停）——视觉层级明确、带轻柔亮度变化
BTN_GREEN        = "#98C379"
BTN_GREEN_HOVER  = "#B8DA89"
BTN_BLUE         = "#61AFEF"
BTN_BLUE_HOVER   = "#87C3FF"
BTN_PURPLE       = "#C678DD"
BTN_PURPLE_HOVER = "#E196F5"
BTN_ORANGE       = "#E5C07B"
BTN_ORANGE_HOVER = "#FFDC96"
BTN_GRAY         = "#6E737D"
BTN_GRAY_LIGHT   = "#A5AAB4"
BTN_RED          = "#E06C75"
BTN_RED_HOVER    = "#FF8791"
BTN_CYAN         = "#56B6C2"
BTN_CYAN_HOVER   = "#78D2DC"

BTN_GREEN_DARK   = "#668755"
BTN_BLUE_DARK    = "#3C7DB4"
BTN_PURPLE_DARK  = "#82559B"
BTN_ORANGE_DARK  = "#9B8255"
BTN_GRAY_DARK    = "#4B505A"
BTN_RED_DARK     = "#8C3C46"
BTN_CYAN_DARK    = "#377D87"

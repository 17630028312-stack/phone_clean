"""
生成 ins 风格的图标
iOS 风格：简洁、圆角、渐变背景
"""

from PIL import Image, ImageDraw, ImageFilter
import os

def create_gradient(size, colors):
    """创建渐变背景"""
    base = Image.new('RGB', size, colors[0])
    draw = ImageDraw.Draw(base)
    
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
        g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
        b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    
    return base

def create_rounded_rect(draw, xy, radius, fill):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)

def draw_delete_icon(draw, center, size):
    """绘制删除图标（垃圾桶）"""
    cx, cy = center
    s = int(size)
    cx, cy = int(cx), int(cy)
    
    # 垃圾桶主体 - 圆角矩形
    body_w, body_h = int(s * 0.6), int(s * 0.5)
    body_x1 = cx - body_w // 2
    body_y1 = cy - body_h // 2 + int(s * 0.1)
    body_x2 = body_x1 + body_w
    body_y2 = body_y1 + body_h
    draw.rounded_rectangle([body_x1, body_y1, body_x2, body_y2], 
                          radius=int(s//10), outline='white', width=max(3, int(s//15)))
    
    # 垃圾桶盖子
    lid_w = int(s * 0.7)
    lid_x1 = cx - lid_w // 2
    lid_y1 = body_y1 - int(s * 0.12)
    lid_x2 = lid_x1 + lid_w
    lid_y2 = lid_y1 + int(s * 0.1)
    draw.rounded_rectangle([lid_x1, lid_y1, lid_x2, lid_y2], 
                          radius=int(s//20), fill='white')
    
    # 提手
    handle_w = int(s * 0.25)
    handle_h = int(s * 0.15)
    handle_x1 = cx - handle_w // 2
    handle_y1 = lid_y1 - handle_h
    handle_x2 = handle_x1 + handle_w
    draw.arc([handle_x1, handle_y1, handle_x2, lid_y1], 
             start=0, end=180, fill='white', width=max(3, int(s//15)))
    
    # 垃圾桶内部线条
    line_y1 = body_y1 + int(s * 0.12)
    line_y2 = body_y2 - int(s * 0.1)
    for offset in [int(-s*0.15), 0, int(s*0.15)]:
        draw.line([(cx + offset, line_y1), (cx + offset, line_y2)], 
                 fill='white', width=max(2, int(s//20)))

def draw_keep_icon(draw, center, size):
    """绘制保留图标（心形）"""
    cx, cy = center
    s = size
    
    # 使用贝塞尔曲线绘制心形
    # 简化为两个圆和一个三角形
    r = s * 0.25
    left_circle = (cx - r * 0.7, cy - r * 0.3)
    right_circle = (cx + r * 0.7, cy - r * 0.3)
    
    # 绘制填充心形（使用多边形近似）
    points = []
    # 上半部分两个弧线
    for i in range(180):
        angle = 3.14159 * i / 180
        x = left_circle[0] + r * 0.9 * (1 + 0.9 * (1 + 0.5 * (1 - 0.5)))
        # 简化：使用 polygon 绘制心形
    
    # 更简单的方法：使用路径绘制
    # 左弧
    draw.ellipse([cx - s*0.4, cy - s*0.35, cx - s*0.05, cy + s*0.1], 
                 fill='white')
    # 右弧
    draw.ellipse([cx + s*0.05, cy - s*0.35, cx + s*0.4, cy + s*0.1], 
                 fill='white')
    # 下三角
    triangle_points = [
        (cx - s*0.45, cy),
        (cx + s*0.45, cy),
        (cx, cy + s*0.45)
    ]
    draw.polygon(triangle_points, fill='white')
    
    # 内部高光小圆
    draw.ellipse([cx - s*0.25, cy - s*0.2, cx - s*0.1, cy - s*0.05], 
                 fill='white')

def draw_skip_icon(draw, center, size):
    """绘制跳过图标（向上箭头 + 时钟）"""
    cx, cy = center
    s = size
    
    # 向上的箭头
    arrow_w = s * 0.15
    arrow_h = s * 0.4
    
    # 箭头杆
    shaft_x1 = cx - arrow_w // 2
    shaft_y1 = cy + s * 0.15
    shaft_x2 = shaft_x1 + arrow_w
    shaft_y2 = shaft_y1 - arrow_h
    draw.polygon([
        (shaft_x1, shaft_y1),
        (shaft_x2, shaft_y1),
        (shaft_x2, shaft_y2),
        (shaft_x1, shaft_y2)
    ], fill='white')
    
    # 箭头头部（三角形）
    head_points = [
        (cx, cy - s * 0.35),  # 顶点
        (cx - s * 0.2, cy - s * 0.15),  # 左下
        (cx + s * 0.2, cy - s * 0.15)   # 右下
    ]
    draw.polygon(head_points, fill='white')
    
    # 时钟圆圈（右下方）
    clock_r = int(s * 0.18)
    clock_cx = int(cx + s * 0.25)
    clock_cy = int(cy + s * 0.2)
    draw.ellipse([int(clock_cx - clock_r), int(clock_cy - clock_r), 
                  int(clock_cx + clock_r), int(clock_cy + clock_r)], 
                 outline='white', width=max(3, int(s//18)))
    
    # 时钟指针
    draw.line([(clock_cx, clock_cy), (clock_cx, int(clock_cy - clock_r * 0.6))], 
             fill='white', width=max(2, int(s//20)))
    draw.line([(clock_cx, clock_cy), (int(clock_cx + clock_r * 0.4), clock_cy)], 
             fill='white', width=max(2, int(s//20)))

def generate_icon(name, colors, draw_func, size=512):
    """生成单个图标"""
    size = int(size)
    # 创建渐变背景
    img = create_gradient((size, size), colors)
    draw = ImageDraw.Draw(img)
    
    # 绘制图标
    draw_func(draw, (size//2, size//2), size * 0.5)
    
    # 添加圆角蒙版
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size, size], radius=int(size//8), fill=255)
    
    # 应用圆角
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0))
    output.putalpha(mask)
    
    return output

def draw_favorite_icon(draw, center, size):
    """绘制收藏图标（星星）"""
    cx, cy = int(center[0]), int(center[1])
    s = int(size)
    
    # 绘制五角星
    def get_star_point(cx, cy, r, angle):
        import math
        rad = math.radians(angle - 90)  # -90 使顶点朝上
        return (int(cx + r * math.cos(rad)), int(cy + r * math.sin(rad)))
    
    import math
    outer_r = s * 0.35  # 外半径
    inner_r = s * 0.15  # 内半径
    
    points = []
    for i in range(10):
        angle = i * 36
        r = outer_r if i % 2 == 0 else inner_r
        rad = math.radians(angle - 90)
        x = int(cx + r * math.cos(rad))
        y = int(cy + r * math.sin(rad))
        points.append((x, y))
    
    draw.polygon(points, fill='white')

def main():
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    # 定义 ins 风格渐变色
    gradients = {
        'delete': [(255, 107, 107), (238, 90, 82)],    # 珊瑚红到红色
        'keep': [(79, 172, 254), (0, 242, 254)],        # 蓝色到青色
        'skip': [(250, 112, 154), (254, 225, 64)],      # 粉色到黄色
        'favorite': [(255, 200, 50), (255, 150, 0)]     # 金色到橙色（收藏）
    }
    
    # 生成四个图标
    icons = [
        ('icon_delete.png', gradients['delete'], draw_delete_icon),
        ('icon_keep.png', gradients['keep'], draw_keep_icon),
        ('icon_skip.png', gradients['skip'], draw_skip_icon),
        ('icon_favorite.png', gradients['favorite'], draw_favorite_icon),
    ]
    
    for filename, colors, draw_func in icons:
        icon = generate_icon(filename, colors, draw_func)
        filepath = os.path.join(assets_dir, filename)
        icon.save(filepath, 'PNG')
        print(f"生成: {filepath}")
    
    print("所有图标生成完成！")

if __name__ == '__main__':
    main()

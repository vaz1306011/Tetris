import random
import tkinter as tk

FPS = 1000  # 畫面更新率(越小越快)
outline_set = True  # 方格框線是否開啟
space_move = True  # 落到最下是否可移動

C = 10  # 遊戲寬度格數
R = 20  # 遊戲高度格數
block_size = 30  # 每格像素
width = C*block_size  # 遊戲寬度像素
height = R*block_size  # 遊戲高度像素

cell_list = ["I", "J", "L", "O", "S", "T", "Z"]  # 方塊種類

cell_dic = {  # 方塊放置參數
    "I0": (4, 5, 6, 7), "I1": (2, 6, 10, 14), "I2": (8, 9, 10, 11), "I3": (1, 5, 9, 13),
    "J0": (0, 4, 5, 6), "J1": (1, 2, 5, 9), "J2": (4, 5, 6, 10), "J3": (1, 5, 8, 9),
    "L0": (2, 4, 5, 6), "L1": (1, 5, 9, 10), "L2": (4, 5, 6, 8), "L3": (0, 1, 5, 9),
    "O0": (0, 1, 4, 5), "O1": (0, 1, 4, 5), "O2": (0, 1, 4, 5), "O3": (0, 1, 4, 5),
    "S0": (1, 2, 4, 5), "S1": (1, 5, 6, 10), "S2": (5, 6, 8, 9), "S3": (0, 4, 5, 9),
    "T0": (1, 4, 5, 6), "T1": (1, 5, 6, 9), "T2": (4, 5, 6, 9), "T3": (1, 4, 5, 9),
    "Z0": (0, 1, 5, 6), "Z1": (2, 5, 6, 9), "Z2": (4, 5, 9, 10), "Z3": (1, 4, 5, 8)
}

cell_rotate_clockwise_dic = {  # 順轉test1~test5測試位置
    "I0": ((0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)),
    "I1": ((0, 0), (-1, 0), (2, 0), (-1, -2), (2, -1)),
    "I2": ((0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)),
    "I3": ((0, 0), (1, 0), (-2, 0), (1, -2), (-2, -1)),
    "other0": ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
    "other1": ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
    "other2": ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
    "other3": ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2))
}

cell_rotate_counter_clockwise_dic = {  # 逆轉test1~test5測試位置
    "I0": ((0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)),
    "I1": ((0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)),
    "I2": ((0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)),
    "I3": ((0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)),
    "other0": ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
    "other1": ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
    "other2": ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
    "other3": ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2))
}

cell_color = {  # 方塊顏色
    "S": "lightgreen",
    "Z": "red",
    "J": "blue",
    "L": "orange",
    "T": "purple",
    "O": "yellow",
    "I": "lightblue"
}

now_cell = None  # 目前方塊

block_list = []  # 已儲存方格

direction = 0  # 方塊型態


def check_and_clear():  # 檢查每一行有沒有滿
    row_complete = False
    for i in range(R):
        if check_row_complete(block_list[i]):  # 如果i行是滿的
            row_complete = True
            if i > 0:
                for j in range(i, 0, -1):  # i>0 把上面的往下補
                    block_list[j] = block_list[j-1]
            block_list[0] = ['' for j in range(C)]  # 最上面一行補空的
            global line
            line += 1
    if row_complete:  # 有滿就重畫
        draw_board(canvas, outline_set)
        line_canvas.itemconfig(score, text=line)


def check_move(cell: dict, way=[0, 0]):  # 檢查能不能動
    c, r = cell['cr']
    cell_type = cell['cell']
    for n in cell_type:  # 每一個方塊去檢查
        x = (n % 4) + c + way[0]
        y = (n // 4) + r + way[1]
        if x < 0 or x >= C or y >= R:  # 移動後超過左邊,右邊,下面
            return False
        if y >= 0 and block_list[y][x]:  # 除了從頂層補到底層的情況外 移動後的位置裡有東西
            return False
    return True


def check_row_complete(row):  # 檢查row行有沒有滿
    for i in row:
        if i == '':
            return False
    return True


def control(event):  # 鍵盤控制
    global now_cell
    if now_cell is None:
        return
    way = [0, 0]
    if event.keysym == 'Left':  # 左移
        way = [-1, 0]
    elif event.keysym == 'Right':  # 右移
        way = [1, 0]
    elif event.keysym == 'Down':  # 加速掉落
        way = [0, 1]
    elif event.keysym == 'Up':  # 順時鐘轉
        rotate(-1)
        return
    elif event.keysym == 'Control_L':
        rotate(1)
        return
    elif event.keysym == 'space':  # 直接到最下面
        global loop
        tetris_win.after_cancel(loop)
        if space_move and distance_bottom()[1] != 0:
            move(canvas, now_cell, distance_bottom())  # 移動目前方塊到底的位移
            loop = tetris_win.after(FPS, game_loop)
        else:
            move(canvas, now_cell, distance_bottom())
            loop = True
            game_loop()
        return
    else:
        return

    if check_move(now_cell, way):  # 檢查是否能夠位移
        draw_cell(canvas, foresee_cell(), outline=outline_set)   # 清除預視方塊
        move(canvas, now_cell, way)  # 移動目前方塊
        draw_cell(canvas, foresee_cell(), "gray",
                  outline=outline_set)  # 繪製預視方塊
        draw_cell(canvas, now_cell,
                  cell_color[now_cell['kind']], outline=outline_set)  # 繪製目前方塊


def create_cell():  # 製作新方塊
    kind = random.choice(cell_list)  # 隨機挑選方塊種類
    cr = [C//2-1, -1]  # 設定起始位置
    global direction  # 方向初始化
    direction = 0
    new_cell = {  # 製作方塊
        'kind': kind,
        'cell': cell_dic[kind+str(direction)],
        'cr': cr
    }
    return new_cell  # 回傳新方塊


def distance_bottom():  # 計算目前方塊往下可位移最大距離
    global now_cell
    if now_cell is None:
        return
    cell_type = now_cell['cell']  # 獲取目前方塊放置參數
    c, r = now_cell['cr']  # 獲取目前方塊位置
    min_height = R  # 位移量
    for n in cell_type:  # 每格方塊逐一檢查找最小的位移量
        x = c+n % 4
        y = r+n // 4
        h = 0
        for i in range(y+1, R):  # 計算方塊到底要位移多少距離
            if block_list[i][x]:
                break
            else:
                h += 1
        if h < min_height:  # 如果移動距離比目前位移量短 位移量改為目前距離
            min_height = h
    return [0, min_height]


def draw_block(canvas, c, r, color="#000000", outline=False):  # 繪製一個方格
    if outline:
        outline_color = "#2E2E2E"
    else:
        outline_color = color
    x1 = c*block_size
    y1 = r*block_size
    x2 = c*block_size+block_size-1
    y2 = r*block_size+block_size-1
    canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                            outline=outline_color)


def draw_board(canvas, outline=False):  # 繪製整版
    canvas.delete(tk.ALL)
    for i in range(R):
        for j in range(C):
            kind = block_list[i][j]
            if kind:
                draw_block(canvas, j, i, cell_color[kind], outline)
            else:
                draw_block(canvas, j, i, outline=True)


def draw_cell(canvas,  cell: dict, color="#000000", outline=False):  # 繪製方塊
    c, r = cell['cr']  # 獲取方塊位置
    for n in cell['cell']:  # 方格逐一繪製
        x = c+n % 4
        y = r+n // 4
        draw_block(canvas, x, y, color, outline)


def draw_next_cell(canvas,  kind: str, color="#000000", outline=False):
    canvas.delete(tk.ALL)
    if kind in 'JLSTZ':
        c, r = 1, 0.4
    elif kind == 'O':
        c, r = 1.5, 0.4
    elif kind == 'I':
        c, r = 0.5, 0
    else:
        return
    for n in cell_dic[kind+'0']:  # 方格逐一繪製
        x = c+n % 4
        y = r+n // 4
        draw_block(canvas, x, y, color, outline)


def foresee_cell():  # 製作預視方塊
    if now_cell is None:
        return None
    c, r = now_cell['cr']  # 獲取目前方塊位置
    way = distance_bottom()  # 獲取目前方塊往下可位移最大距離
    foresee_cell = {  # 預視方塊為目前方塊位移往下位移最大距離
        'kind': now_cell['kind'],
        'cell': now_cell['cell'],
        'cr': [c, r+way[1]]
    }
    return foresee_cell


def game_init():  # 遊戲初始化
    global line
    line = 0

    tetris_win.title("俄羅斯方塊")
    tetris_win.resizable(0, 0)
    tetris_win.geometry('+810+200')

    tetris_win.focus_force()  # 聚焦到目前視窗

    global block_list
    block_list = [['' for i in range(C)] for j in range(R)]  # 初始化所有方格

    top_frame = tk.Frame(tetris_win)
    top_frame.pack(side='top')

    global line_canvas
    line_canvas = tk.Canvas(top_frame, width=width /
                            2-3, height=80, bg="#000000")
    line_canvas.grid(row=0, column=0, sticky='w')
    line_canvas.create_text(75, 30, text="LINE", font=(
        'Hobo std', 20), fill='white', width=300)
    global score
    score = line_canvas.create_text(
        75, 60, text=line, font=('Hobo std', 20), fill='white')

    global next_cell_canvas
    next_cell_canvas = tk.Canvas(
        top_frame, width=width/2-3, height=80, bg="#000000")
    next_cell_canvas.grid(row=0, column=1, sticky='w')

    global canvas
    canvas = tk.Canvas(tetris_win, width=width, height=height)  # 初始化遊戲畫布
    canvas.pack(side='top')
    draw_board(canvas, outline_set)  # 繪製遊戲畫布

    global now_cell, next_cell
    now_cell = create_cell()
    next_cell = create_cell()
    draw_next_cell(next_cell_canvas, next_cell['kind'],
                   cell_color[next_cell['kind']], outline=outline_set)

    global loop
    loop = True

    tetris_win.protocol('WM_DELETE_WINDOW', game_quit)  # 連結鍵盤按鍵
    canvas.bind_all("<Key-Left>", control)
    canvas.bind_all("<Key-Right>", control)
    canvas.bind_all("<Key-Up>", control)
    canvas.bind_all("<Key-Down>", control)
    canvas.bind_all("<Key-Control_L>", control)
    canvas.bind_all("<space>", control)


def game_loop():  # 遊戲迴圈
    global now_cell, loop
    if now_cell is None:  # 如果無目前方塊
        global next_cell
        now_cell = next_cell  # 獲取新方塊
        if not check_move(now_cell):  # 如果不能移動 遊戲結束
            import tkinter.messagebox
            tkinter.messagebox.showinfo('遊戲結束', f'消除 {line} 行')
            game_quit()
            return
        next_cell = create_cell()
        draw_next_cell(next_cell_canvas, next_cell['kind'],
                       cell_color[next_cell['kind']], outline=outline_set)  # 繪製下一個方塊
        draw_board(canvas, outline=outline_set)  # 重新繪製遊戲畫面
        draw_cell(canvas, foresee_cell(), "gray",
                  outline=outline_set)  # 繪製預視方塊
        draw_cell(canvas, now_cell,
                  cell_color[now_cell['kind']], outline=outline_set)  # 繪製目前方塊
        if loop:
            loop = tetris_win.after(0, game_loop)

    else:  # 如果有目前方格
        if check_move(now_cell, [0, 1]):  # 檢查目前方格是否能往下移動
            move(canvas, now_cell, [0, 1])  # 向下移動一格
            draw_cell(canvas, foresee_cell(), "gray",
                      outline=outline_set)  # 繪製預視方塊
            draw_cell(canvas, now_cell,
                      cell_color[now_cell['kind']], outline=outline_set)  # 繪製目前方塊
            if loop:
                loop = tetris_win.after(FPS, game_loop)  # 延遲
        else:
            save_block(now_cell)  # 保存目前方塊
            now_cell = None  # 目前方塊清空
            if loop:
                loop = tetris_win.after(0, game_loop)


def game_quit():
    global loop
    tetris_win.after_cancel(loop)
    loop = None
    tetris_win.quit()
    tetris_win.destroy()


def move(canvas, cell: dict, way=[0, 0]):  # 移動

    kind = cell['kind']  # 獲取傳入方塊類型
    c, r = cell['cr']  # 獲取傳入方塊位置

    draw_board(canvas, outline_set)  # 重新繪製遊戲畫面

    new_c, new_r = c+way[0], r+way[1]  # 更新位置
    cell['cr'] = [new_c, new_r]

    draw_cell(canvas, cell, cell_color[kind], outline=outline_set)  # 繪製方塊


def rotate(side):
    global direction, now_cell
    d = direction
    kind = now_cell['kind']
    from copy import deepcopy
    new_cell = deepcopy(now_cell)  # 深複製現在控制的方塊給新方塊
    if side == 1:
        if d < 3:
            d += 1
        else:
            d = 0
    elif side == -1:
        if d > 0:
            d -= 1
        else:
            d = 3
    new_cell['cell'] = cell_dic[kind+str(d)]  # 修改形狀編號
    rotate_kind = 'other' if kind != 'I' else 'I'
    if side == 1:
        for i in range(5):
            # 檢查test1~test5能否移動
            if check_move(new_cell, cell_rotate_clockwise_dic[rotate_kind+str(d)][i]):
                direction = d
                now_cell['cell'] = new_cell['cell']  # 將目前方塊換成新的方塊
                move(canvas, now_cell,
                     cell_rotate_clockwise_dic[rotate_kind+str(d)][i])  # 移動到test
                draw_cell(canvas, foresee_cell(), "gray",
                          outline=outline_set)  # 繪製預視方塊
                draw_cell(canvas, now_cell,
                          cell_color[kind], outline=outline_set)  # 繪製目前方塊
                return
    elif side == -1:
        for i in range(5):
            # 檢查test1~test5能否移動
            if check_move(new_cell, cell_rotate_counter_clockwise_dic[rotate_kind+str(d)][i]):
                direction = d
                now_cell['cell'] = new_cell['cell']  # 將目前方塊換成新的方塊
                move(canvas, now_cell,
                     cell_rotate_counter_clockwise_dic[rotate_kind+str(d)][i])  # 移動到test
                draw_cell(canvas, foresee_cell(), "gray",
                          outline=outline_set)  # 繪製預視方塊
                draw_cell(canvas, now_cell,
                          cell_color[kind], outline=outline_set)  # 繪製目前方塊
                return
    else:
        return


def save_block(cell):  # 儲存傳入方塊
    kind = cell['kind']  # 獲取傳入方塊類型
    c, r = cell['cr']  # 獲取傳入方塊位置
    cell_type = cell['cell']   # 獲取目前方塊放置參數
    for n in cell_type:  # 逐一儲存方格
        x = c+n % 4
        y = r+n // 4
        block_list[y][x] = kind
    check_and_clear()  # 檢查每一行有沒有滿


def main():  # 主程式
    global tetris_win
    tetris_win = tk.Tk()  # 視窗製作
    game_init()  # 遊戲初始化
    game_loop()  # 遊戲迴圈
    tetris_win.mainloop()


if __name__ == "__main__":
    main()

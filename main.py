import tkinter as tk
import math
from math import sin, cos, radians, sqrt

# ЭЛЕМЕНТАРНЫЕ МАТРИЦЫ
def identity_matrix():
    """Единичная матрица 4×4"""
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def translation_matrix(tx, ty, tz):
    """  Матрица переноса
    При умножении (x, y, z, 1) · [T] получаем (x+tx, y+ty, z+tz, 1). """
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [tx,  ty,  tz,  1.0],
    ]


def rotation_x_matrix(angle_deg):
    """ Матрица вращения вокруг оси X  """
    a = radians(angle_deg)
    c, s = cos(a), sin(a)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c,   s,   0.0],
        [0.0, -s,  c,   0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_y_matrix(angle_deg):
    """  Матрица вращения вокруг оси Y  """
    a = radians(angle_deg)
    c, s = cos(a), sin(a)
    return [
        [c,   0.0, -s,  0.0],
        [0.0, 1.0, 0.0, 0.0],
        [s,   0.0, c,   0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_z_matrix(angle_deg):
    """ Матрица вращения вокруг оси Z """
    a = radians(angle_deg)
    c, s = cos(a), sin(a)
    return [
        [c,   s,   0.0, 0.0],
        [-s,  c,   0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def scale_matrix(sx, sy, sz):
    """ Матрица растяжения-сжатия """
    return [
        [sx,  0.0, 0.0, 0.0],
        [0.0, sy,  0.0, 0.0],
        [0.0, 0.0, sz,  0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


# УМНОЖЕНИЕ МАТРИЦ И ВЕКТОРОВ

def multiply_matrices(A, B):
    """ Умножение матриц: C = A · B """
    return [
        [sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)]
        for i in range(4)
    ]


def multiply_vector_matrix(v, M):
    """ Умножение вектора-строки на матрицу: v' = v · M """
    return [sum(v[j] * M[j][i] for j in range(4)) for i in range(4)]


def compose(*matrices):
    """ Композиция матриц: M = M1 · M2 · ... · Mk.."""
    result = identity_matrix()
    for M in matrices:
        result = multiply_matrices(result, M)
    return result


# МАТРИЦЫ ПРОЕКЦИЙ

def orthographic_xy_matrix():
    """ Ортографическая проекция на плоскость XY (вид спереди)  """
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def cabinet_matrix(angle_deg=45.0, factor=0.5):
    """ Косоугольная кабинетная проекция"""
    a = radians(angle_deg)
    dx = -factor * cos(a)
    dy = -factor * sin(a)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [dx,  dy,  0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]

def isometric_matrix():
    """ Изометрическая проекция
    Композиция: P_xy · R_x(φ) · R_y(45°),
    где φ = arcsin(1/√3.
    В соглашении с вектор-строкой это означает:
        p' = p · R_y(45°) · R_x(φ) · P_xy
    то есть сначала поворот вокруг Y, потом вокруг X, потом проекция."""
    phi = math.degrees(math.asin(1.0 / sqrt(3.0)))
    return compose(
        rotation_y_matrix(45.0),
        rotation_x_matrix(phi),
        orthographic_xy_matrix(),
    )


def perspective_matrix(c=18.0):
    """ Перспективное преобразование """
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, -1.0 / c],
        [0.0, 0.0, 0.0, 1.0],
    ]


# МОДЕЛЬ БУКВЫ «Я»

def create_letter_ya():

    vertices = []
    edges = []
    z_near = 1.0
    z_far = -1.0

    def add_contour(points):
        n = len(points)
        start = len(vertices)
        vertices.extend((x, y, z_near) for x, y in points)
        vertices.extend((x, y, z_far) for x, y in points)
        for i in range(n):
            edges.append((start + i, start + (i + 1) % n))
        for i in range(n):
            edges.append((start + n + i, start + n + (i + 1) % n))
        for i in range(n):
            edges.append((start + i, start + n + i))

    outer = [
        (0, 0), (2, 0), (6, 5), (6, 0), (8, 0),
        (8, 11), (0, 11), (0, 5), (4, 5),
    ]
    add_contour(outer)

    hole = [(2, 7), (6, 7), (6, 9), (2, 9)]
    add_contour(hole)

    return vertices, edges


# СЦЕНА

class Scene3D:

    def __init__(self):
        self.base_vertices, self.edges = create_letter_ya()

        self.tx = self.ty = self.tz = 0.0
        self.sx = self.sy = self.sz = 1.0

        # Накопленная матрица поворота (R_acc = R1 · R2 · ... · Rk).
        self.R_acc = identity_matrix()

        self.auto_rotate = False
        self.auto_angle = 0.0

        self.local_mode = False

        self.view_scale = 40.0
        self.view_center_x = 300.0
        self.view_center_y = 500.0

        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_button = None

        self.projection = 'cabinet'
        self.persp_c = 18.0
        self.oblique_alpha = 45.0
        self.oblique_k = 0.5

        self.camera_yaw  = 30.0
        self.camera_pitch = -20.0

    def get_geometric_center(self):
        """Среднее арифметическое координат всех вершин модели."""
        n = len(self.base_vertices)
        return tuple(sum(v[i] for v in self.base_vertices) / n for i in range(3))

    def get_model_matrix(self):
        """Модельная матрица M_model = S · R_acc · T. """
        S = scale_matrix(self.sx, self.sy, self.sz)
        T = translation_matrix(self.tx, self.ty, self.tz)
        return compose(S, self.R_acc, T)

    def get_auto_rotation_matrix(self):
        """ Матрица анимации:
        одновременное вращение вокруг центра координат
        и вокруг собственного геометрического центра буквы.

            M_auto = R_local_about_center · R_world

        R_world = R_y(a) · R_x(a·0.7) — вращение вокруг мирового центра координат.

        R_local_about_center = T(-C_world) · R_local · T(+C_world)
         — вращение вокруг собственного центра C_world.
            R_local = R_z(a·1.3) · R_y(a·0.5). """
        a = self.auto_angle
        M_model = self.get_model_matrix()

        cx, cy, cz = self.get_geometric_center()
        center_world = multiply_vector_matrix([cx, cy, cz, 1.0], M_model)
        cwx, cwy, cwz = center_world[:3]

        T_to_center   = translation_matrix(-cwx, -cwy, -cwz)
        T_from_center = translation_matrix(cwx, cwy, cwz)

        R_world = compose(
            rotation_y_matrix(a),
            rotation_x_matrix(a),
        )
        R_local = compose(
            rotation_z_matrix(a),
           rotation_y_matrix(a),
        )
        R_local_about_center = compose(
            T_to_center,
            R_local,
            T_from_center,
        )
        return compose(R_local_about_center, R_world)

    def get_total_matrix(self):
        """  Итоговая матрица: M_total = M_model · M_auto."""
        M_model = self.get_model_matrix()
        if not self.auto_rotate or abs(self.auto_angle) < 1e-12:
            return M_model
        M_auto = self.get_auto_rotation_matrix()
        return multiply_matrices(M_model, M_auto)

    def apply_rotation(self, axis, angle_deg):
        """ Пользовательский поворот вокруг оси 'x'|'y'|'z'. """
        if axis == 'x':
            R = rotation_x_matrix(angle_deg)
        elif axis == 'y':
            R = rotation_y_matrix(angle_deg)
        elif axis == 'z':
            R = rotation_z_matrix(angle_deg)
        else:
            return

        if self.local_mode:
            self.R_acc = multiply_matrices(R, self.R_acc)
        else:
            self.R_acc = multiply_matrices(self.R_acc, R)

    def apply_translation(self, dx, dy, dz):
        """  Пользовательский перенос. """
        if self.local_mode:
            direction = multiply_vector_matrix([dx, dy, dz, 0.0], self.R_acc)
            self.tx += direction[0]
            self.ty += direction[1]
            self.tz += direction[2]
        else:
            self.tx += dx
            self.ty += dy
            self.tz += dz

    def transform_vertices(self):
        """Прогоняет все вершины через M_total """
        M_total = self.get_total_matrix()
        transformed = []
        for x, y, z in self.base_vertices:
            r = multiply_vector_matrix([x, y, z, 1.0], M_total)
            transformed.append((r[0], r[1], r[2]))
        return transformed

    def get_projection_matrix(self):
        """Возвращает матрицу проекции P по текущему режиму."""
        if self.projection == 'isometric':
            return isometric_matrix()
        if self.projection == 'perspective':
            return perspective_matrix(self.persp_c)
        if self.projection == 'ortho_xy':
            return orthographic_xy_matrix()
        return cabinet_matrix(self.oblique_alpha, self.oblique_k)

    def get_view_matrix(self):
        """ Видовое преобразование камеры.
        V = R_y(yaw) · R_x(pitch).
        """
        if self.projection in ('perspective', 'ortho_xy'):
            return compose(
                rotation_y_matrix(self.camera_yaw),
                rotation_x_matrix(self.camera_pitch),
            )
        return identity_matrix()

    def project_points(self, points3d):
        """ Проецирует список 3D-точек на экран."""
        V = self.get_view_matrix()
        P = self.get_projection_matrix()
        VP = multiply_matrices(V, P)

        result = []
        for x, y, z in points3d:
            r = multiply_vector_matrix([x, y, z, 1.0], VP)
            w = r[3]
            if abs(w) < 1e-9:
                result.append((float('nan'), float('nan')))
                continue
            xp, yp = r[0] / w, r[1] / w
            screen_x = self.view_center_x + xp * self.view_scale
            screen_y = self.view_center_y - yp * self.view_scale
            result.append((screen_x, screen_y))
        return result

    def project(self, vertices):
        return self.project_points(vertices)

    def get_global_axes(self):
        """ Глобальные оси  """
        return self.project_points([
            (0.0, 0.0, 0.0),
            (3.5, 0.0, 0.0),
            (0.0, 3.5, 0.0),
            (0.0, 0.0, 3.5),
        ])

    def get_local_axes(self):
        """  Локальные оси """
        M_total = self.get_total_matrix()
        origin = multiply_vector_matrix([0.0, 0.0, 0.0, 1.0], M_total)[:3]

        def transformed_direction(v):
            r = multiply_vector_matrix([v[0], v[1], v[2], 0.0], M_total)
            length = sqrt(r[0] ** 2 + r[1] ** 2 + r[2] ** 2)
            if length < 1e-12:
                return (0.0, 0.0, 0.0)
            return tuple(r[i] / length * 3.5 for i in range(3))

        dx = transformed_direction((1.0, 0.0, 0.0))
        dy = transformed_direction((0.0, 1.0, 0.0))
        dz = transformed_direction((0.0, 0.0, 1.0))
        ox, oy, oz = origin
        return self.project_points([
            (ox, oy, oz),
            (ox + dx[0], oy + dx[1], oz + dx[2]),
            (ox + dy[0], oy + dy[1], oz + dy[2]),
            (ox + dz[0], oy + dz[1], oz + dz[2]),
        ])


# 6ИНТЕРФЕЙС

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Аффинные преобразования 3D-буквы 'Я' (вариант 10)")
        self.root.geometry("1100x780")
        self.scene = Scene3D()

        self.canvas = tk.Canvas(root, width=820, height=770, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.control_frame = tk.Frame(root, width=260, bg='lightgray')
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.create_controls()

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.focus_set()

        self.redraw()
        self.animate()

    def create_controls(self):
        tk.Label(
            self.control_frame, text="Управление",
            font=("Arial", 12, "bold"), bg='lightgray'
        ).pack(pady=5)

        info = """
W/S — вращение X
A/D — вращение Y
Q/E — вращение Z
Стрелки — перенос XY
PageUp/PageDown — перенос Z
+/- — масштаб
Пробел — анимация 
R — сброс
"""
        tk.Label(
            self.control_frame, text=info, justify=tk.LEFT,
            bg='lightgray', font=("Courier", 8)
        ).pack(pady=5, padx=5)

        tk.Label(
            self.control_frame, text="Оси для вращения/переноса:",
            bg='lightgray', font=("Arial", 9, "bold")
        ).pack(pady=(10, 0))
        self.mode_var = tk.BooleanVar(value=False)
        tk.Radiobutton(
            self.control_frame, text="Глобальные", variable=self.mode_var,
            value=False, bg='lightgray', command=self.change_mode
        ).pack(anchor='w', padx=10)
        tk.Radiobutton(
            self.control_frame, text="Собственные (локальные)",
            variable=self.mode_var, value=True, bg='lightgray',
            command=self.change_mode
        ).pack(anchor='w', padx=10)

        tk.Label(
            self.control_frame, text="Проекция:",
            bg='lightgray', font=("Arial", 9, "bold")
        ).pack(pady=(10, 0))
        self.proj_var = tk.StringVar(value='cabinet')
        for val, label in [
            ('cabinet', 'Кабинетная'),
            ('isometric', 'Изометрическая'),
            ('perspective', 'Перспективная'),
            ('ortho_xy', 'Ортографическая'),
        ]:
            tk.Radiobutton(
                self.control_frame, text=label, variable=self.proj_var,
                value=val, bg='lightgray', command=self.change_projection
            ).pack(anchor='w', padx=10)

        self.auto_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.control_frame, text="Анимация",
            variable=self.auto_var, bg='lightgray',
            command=self.toggle_auto_rotate
        ).pack(pady=5)
        tk.Button(
            self.control_frame, text="Сброс (R)", command=self.reset
        ).pack(pady=10)

        legend = """Проекции:
— Кабинетная 
— Изометрическая 
— Перспективная 
— Ортографическая


Обозначения осей:
— Красный: глобальная X
— Зелёный: глобальная Y
— Синий: глобальная Z
- - Оранжевый: локальная X
- - Фиолетовый: локальная Y
- - Бирюзовый: локальная Z

"""
        tk.Label(
            self.control_frame, text=legend, justify=tk.LEFT,
            bg='lightgray', font=("Courier", 8)
        ).pack(pady=5, padx=5)

    def change_mode(self):
        self.scene.local_mode = self.mode_var.get()
        self.redraw()

    def toggle_auto_rotate(self):
        self.scene.auto_rotate = self.auto_var.get()

    def change_projection(self):
        self.scene.projection = self.proj_var.get()
        self.redraw()

    def reset(self):
        self.scene.tx = self.scene.ty = self.scene.tz = 0.0
        self.scene.sx = self.scene.sy = self.scene.sz = 1.0
        self.scene.R_acc = identity_matrix()
        self.scene.auto_angle = 0.0
        self.scene.local_mode = False
        self.scene.auto_rotate = False
        self.mode_var.set(False)
        self.auto_var.set(False)
        self.scene.projection = 'cabinet'
        self.proj_var.set('cabinet')
        self.scene.camera_yaw = 30.0
        self.scene.camera_pitch = -20.0
        self.redraw()

    def clamp_scale(self):
        self.scene.sx = max(0.1, min(5.0, self.scene.sx))
        self.scene.sy = max(0.1, min(5.0, self.scene.sy))
        self.scene.sz = max(0.1, min(5.0, self.scene.sz))

    def change_uniform_scale(self, factor):
        self.scene.sx *= factor
        self.scene.sy *= factor
        self.scene.sz *= factor
        self.clamp_scale()

    # Мышь
    def on_mouse_press(self, event):
        self.scene.last_mouse_x = event.x
        self.scene.last_mouse_y = event.y
        self.scene.mouse_button = "left"

    def on_mouse_wheel(self, event):
        self.change_uniform_scale(1.1 if event.delta > 0 else 0.9)
        self.redraw()

    # Клавиатура
    def on_key_press(self, event):
        key = event.keysym.lower()
        step = 5.0

        if key == 'w':
            self.scene.apply_rotation('x', step)
        elif key == 's':
            self.scene.apply_rotation('x', -step)
        elif key == 'a':
            self.scene.apply_rotation('y', -step)
        elif key == 'd':
            self.scene.apply_rotation('y', step)
        elif key == 'q':
            self.scene.apply_rotation('z', step)
        elif key == 'e':
            self.scene.apply_rotation('z', -step)
        elif key == 'up':
            self.scene.apply_translation(0.0, 0.2, 0.0)
        elif key == 'down':
            self.scene.apply_translation(0.0, -0.2, 0.0)
        elif key == 'left':
            self.scene.apply_translation(-0.2, 0.0, 0.0)
        elif key == 'right':
            self.scene.apply_translation(0.2, 0.0, 0.0)
        elif key == 'prior':
            self.scene.apply_translation(0.0, 0.0, 0.2)
        elif key == 'next':
            self.scene.apply_translation(0.0, 0.0, -0.2)
        elif key == 'z':
            self.scene.camera_yaw -= step
        elif key == 'x':
            self.scene.camera_yaw += step
        elif key == 'c':
            self.scene.camera_pitch -= step
        elif key == 'v':
            self.scene.camera_pitch += step
        elif key in ('plus', 'equal', 'kp_add'):
            self.change_uniform_scale(1.1)
        elif key in ('minus', 'kp_subtract'):
            self.change_uniform_scale(0.9)
        elif key == 'space':
            self.auto_var.set(not self.auto_var.get())
            self.toggle_auto_rotate()
        elif key == 'r':
            self.reset()

        self.redraw()

    # Анимация
    def animate(self):
        if self.scene.auto_rotate:
            self.scene.auto_angle = (self.scene.auto_angle + 1.5) % 360.0
            self.redraw()
        self.root.after(30, self.animate)

    # Отрисовка
    def redraw(self):
        self.canvas.delete("all")

        transformed = self.scene.transform_vertices()
        projected = self.scene.project(transformed)

        axes = self.scene.get_global_axes()
        self.canvas.create_line(
            axes[0][0], axes[0][1], axes[1][0], axes[1][1],
            fill='red', width=3, arrow=tk.LAST
        )
        self.canvas.create_text(
            axes[1][0] + 8, axes[1][1], text="X",
            fill='red', font=("Arial", 10, "bold")
        )
        self.canvas.create_line(
            axes[0][0], axes[0][1], axes[2][0], axes[2][1],
            fill='green', width=3, arrow=tk.LAST
        )
        self.canvas.create_text(
            axes[2][0] + 8, axes[2][1], text="Y",
            fill='green', font=("Arial", 10, "bold")
        )
        self.canvas.create_line(
            axes[0][0], axes[0][1], axes[3][0], axes[3][1],
            fill='blue', width=3, arrow=tk.LAST
        )
        self.canvas.create_text(
            axes[3][0] + 8, axes[3][1], text="Z",
            fill='blue', font=("Arial", 10, "bold")
        )

        for i, j in self.scene.edges:
            x1, y1 = projected[i]
            x2, y2 = projected[j]
            self.canvas.create_line(x1, y1, x2, y2, fill='black', width=1.5)

        local_axes = self.scene.get_local_axes()
        self.canvas.create_line(
            local_axes[0][0], local_axes[0][1],
            local_axes[1][0], local_axes[1][1],
            fill='orange', width=2, arrow=tk.LAST, dash=(4, 2)
        )
        self.canvas.create_line(
            local_axes[0][0], local_axes[0][1],
            local_axes[2][0], local_axes[2][1],
            fill='purple', width=2, arrow=tk.LAST, dash=(4, 2)
        )
        self.canvas.create_line(
            local_axes[0][0], local_axes[0][1],
            local_axes[3][0], local_axes[3][1],
            fill='teal', width=2, arrow=tk.LAST, dash=(4, 2)
        )

        mode_str = 'ЛОКАЛЬНЫЕ' if self.scene.local_mode else 'ГЛОБАЛЬНЫЕ'
        proj_names = {
            'cabinet': 'КАБИНЕТНАЯ',
            'isometric': 'ИЗОМЕТРИЧЕСКАЯ',
            'perspective': 'ПЕРСПЕКТИВНАЯ',
            'ortho_xy': 'ОРТОГРАФИЧЕСКАЯ',
        }


# ЗАПУСК

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
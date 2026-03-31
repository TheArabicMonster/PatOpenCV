import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import app as app_module

# ─────────────────────────────────────────────
#  PALETTE DE COULEURS
# ─────────────────────────────────────────────
C = {
    # Fonds
    "bg_root":        "#0f1117",
    "bg_card":        "#1a1d27",
    "bg_card_hover":  "#1f2333",
    "bg_surface":     "#151820",

    # Accents
    "accent_blue":    "#4f8ef7",
    "accent_blue_h":  "#6aa3ff",   # hover
    "accent_blue_p":  "#3a72d4",   # pressed
    "accent_green":   "#3ecf8e",
    "accent_green_h": "#56e0a0",
    "accent_green_p": "#2fb378",
    "accent_orange":  "#f5a623",
    "accent_orange_h":"#ffba45",
    "accent_orange_p":"#d48e1a",

    # Textes
    "text_primary":   "#e8eaf0",
    "text_secondary": "#8b93a8",
    "text_muted":     "#4a5168",

    # Séparateurs / bordures
    "border":         "#252a3a",
    "border_active":  "#4f8ef7",

    # Statuts
    "status_idle":    "#3ecf8e",
    "status_running": "#4f8ef7",
    "status_error":   "#f5636d",
    "status_warning": "#f5a623",
}

# ─────────────────────────────────────────────
#  HELPERS : FORMES ARRONDIES SUR CANVAS
# ─────────────────────────────────────────────

def _round_rect(canvas, x1, y1, x2, y2, r=16, **kwargs):
    """Dessine un rectangle aux coins arrondis sur un Canvas."""
    pts = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
        x1 + r, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


# ─────────────────────────────────────────────
#  WIDGET : BOUTON MODERNE (Canvas-based)
# ─────────────────────────────────────────────

class ModernButton(tk.Canvas):
    """
    Bouton entièrement dessiné sur Canvas pour simuler des coins arrondis
    et offrir des transitions de couleur au survol / clic.
    """

    def __init__(self, parent, text, command=None,
                 bg=C["accent_blue"],
                 bg_hover=C["accent_blue_h"],
                 bg_press=C["accent_blue_p"],
                 fg=C["text_primary"],
                 icon="",
                 radius=10,
                 font=("SF Pro Display", 11, "bold"),
                 width=200, height=44, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=C["bg_root"], highlightthickness=0,
                         bd=0, cursor="hand2", **kwargs)

        self._text      = text
        self._icon      = icon
        self._command   = command
        self._bg        = bg
        self._bg_hover  = bg_hover
        self._bg_press  = bg_press
        self._fg        = fg
        self._radius    = radius
        self._font      = font
        self._btn_w     = width
        self._btn_h     = height
        self._current_bg = bg

        self._draw(bg)

        self.bind("<Enter>",          self._on_enter)
        self.bind("<Leave>",          self._on_leave)
        self.bind("<ButtonPress-1>",  self._on_press)
        self.bind("<ButtonRelease-1>",self._on_release)

    def _draw(self, color):
        self.delete("all")
        _round_rect(self, 0, 0, self._btn_w, self._btn_h,
                    r=self._radius, fill=color, outline="")
        label = f"{self._icon}  {self._text}" if self._icon else self._text
        self.create_text(self._btn_w // 2, self._btn_h // 2,
                         text=label, fill=self._fg,
                         font=self._font, anchor="center")

    def _on_enter(self, _):
        self._animate_to(self._bg_hover, steps=6)

    def _on_leave(self, _):
        self._animate_to(self._bg, steps=6)

    def _on_press(self, _):
        self._draw(self._bg_press)

    def _on_release(self, _):
        self._draw(self._bg_hover)
        if self._command:
            self._command()

    # Interpolation simple entre deux couleurs hex
    def _animate_to(self, target_hex, steps=8, delay=12):
        def _hex_to_rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        def _rgb_to_hex(r, g, b):
            return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

        r1, g1, b1 = _hex_to_rgb(self._current_bg)
        r2, g2, b2 = _hex_to_rgb(target_hex)

        def step(i=0):
            if i > steps:
                self._current_bg = target_hex
                return
            t = i / steps
            r = r1 + (r2 - r1) * t
            g = g1 + (g2 - g1) * t
            b = b1 + (b2 - b1) * t
            self._draw(_rgb_to_hex(r, g, b))
            self.after(delay, lambda: step(i + 1))

        step()


# ─────────────────────────────────────────────
#  WIDGET : ZONE DE DÉPÔT VISUELLE
# ─────────────────────────────────────────────

class DropZone(tk.Canvas):
    """Cadre visuel indiquant la zone de sélection de fichier."""

    def __init__(self, parent, textvariable, command, **kwargs):
        super().__init__(parent, bg=C["bg_root"],
                         highlightthickness=0, bd=0,
                         cursor="hand2", **kwargs)
        self._textvar  = textvariable
        self._command  = command
        self._hovered  = False
        self._selected = False

        self.bind("<Configure>",      self._redraw)
        self.bind("<Enter>",          self._on_enter)
        self.bind("<Leave>",          self._on_leave)
        self.bind("<ButtonRelease-1>",self._on_click)

    # ---- état ----
    def mark_selected(self, filename):
        self._selected = True
        self._filename = filename
        self._redraw()

    def _on_enter(self, _):
        self._hovered = True
        self._redraw()

    def _on_leave(self, _):
        self._hovered = False
        self._redraw()

    def _on_click(self, _):
        if self._command:
            self._command()

    # ---- rendu ----
    def _redraw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 4 or h < 4:
            return

        pad = 2
        if self._selected:
            border_color = C["accent_green"]
            bg_fill      = "#1a2e26"
        elif self._hovered:
            border_color = C["accent_blue"]
            bg_fill      = "#182030"
        else:
            border_color = C["border"]
            bg_fill      = C["bg_card"]

        # Fond arrondi
        _round_rect(self, pad, pad, w - pad, h - pad,
                    r=14, fill=bg_fill, outline="")

        # Bordure en tirets simulée via 4 arcs + lignes
        # (Tkinter ne supporte pas les dash sur polygon, on dessine un
        #  rectangle arrondi séparé avec outline)
        _round_rect(self, pad, pad, w - pad, h - pad,
                    r=14, fill="", outline=border_color,
                    width=2 if self._hovered or self._selected else 1,
                    dash=(6, 4))

        cx, cy = w // 2, h // 2

        if self._selected:
            # Icone checkmark
            self.create_text(cx, cy - 22, text="", font=("Arial", 28),
                             fill=C["accent_green"], anchor="center")
            self.create_text(cx, cy + 14, text=self._filename,
                             font=("SF Pro Display", 10, "bold"),
                             fill=C["accent_green"], anchor="center",
                             width=w - 40)
            self.create_text(cx, cy + 32, text="Cliquer pour changer",
                             font=("SF Pro Display", 9),
                             fill=C["text_muted"], anchor="center")
        else:
            # Icone dossier
            self.create_text(cx, cy - 20, text="", font=("Arial", 30),
                             fill=C["text_muted"] if not self._hovered else C["accent_blue"],
                             anchor="center")
            self.create_text(cx, cy + 12, text="Cliquer pour sélectionner une image",
                             font=("SF Pro Display", 10),
                             fill=C["text_secondary"] if not self._hovered else C["text_primary"],
                             anchor="center")
            self.create_text(cx, cy + 28, text="JPG  PNG  GIF  BMP",
                             font=("SF Pro Display", 9),
                             fill=C["text_muted"], anchor="center")


# ─────────────────────────────────────────────
#  WIDGET : INDICATEUR DE STATUT
# ─────────────────────────────────────────────

class StatusBar(tk.Canvas):
    """
    Bandeau de statut avec pastille colorée animée et texte.
    La pastille pulse via un timer quand l'état est 'running'.
    """

    STATES = {
        "idle":    (C["status_idle"],    "Prêt à démarrer"),
        "running": (C["status_running"], "En cours d'exécution…"),
        "error":   (C["status_error"],   "Erreur"),
        "warning": (C["status_warning"], "Attention"),
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=C["bg_root"],
                         highlightthickness=0, bd=0,
                         height=40, **kwargs)
        self._state   = "idle"
        self._text    = self.STATES["idle"][1]
        self._pulse   = 0
        self._job     = None

        self.bind("<Configure>", lambda e: self._draw())
        self._start_pulse()

    def set_state(self, state, text=None):
        self._state = state
        self._text  = text if text else self.STATES.get(state, ("", ""))[1]
        self._draw()

    def _start_pulse(self):
        def _tick():
            self._pulse = (self._pulse + 0.15) % (2 * 3.14159)
            self._draw()
            self._job = self.after(50, _tick)
        _tick()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 4:
            return

        color = self.STATES.get(self._state, self.STATES["idle"])[0]

        # Fond de la barre
        _round_rect(self, 0, 2, w, h - 2, r=8,
                    fill=C["bg_card"], outline=C["border"], width=1)

        # Pastille
        import math
        dot_x, dot_y, dot_r = 22, h // 2, 5
        if self._state == "running":
            alpha_factor = 0.5 + 0.5 * math.sin(self._pulse)
            r_hex = int(int(color[1:3], 16) * alpha_factor)
            g_hex = int(int(color[3:5], 16) * alpha_factor)
            b_hex = int(int(color[5:7], 16) * alpha_factor)
            glow_color = f"#{r_hex:02x}{g_hex:02x}{b_hex:02x}"
            # Halo
            self.create_oval(dot_x - dot_r - 3, dot_y - dot_r - 3,
                             dot_x + dot_r + 3, dot_y + dot_r + 3,
                             fill=glow_color, outline="")
        self.create_oval(dot_x - dot_r, dot_y - dot_r,
                         dot_x + dot_r, dot_y + dot_r,
                         fill=color, outline="")

        # Texte
        self.create_text(dot_x + dot_r + 12, h // 2,
                         text=self._text, fill=color,
                         font=("SF Pro Display", 10, "bold"),
                         anchor="w")


# ─────────────────────────────────────────────
#  WIDGET : SÉPARATEUR DÉCORATIF
# ─────────────────────────────────────────────

class Divider(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=C["bg_root"],
                         height=1, highlightthickness=0, bd=0, **kwargs)
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        if w < 4:
            return
        self.create_line(0, 0, w, 0, fill=C["border"], width=1)


# ─────────────────────────────────────────────
#  LOGIQUE MÉTIER
# ─────────────────────────────────────────────

image_path = None


def select_image():
    path = filedialog.askopenfilename(
        title="Sélectionner une image à superposer à gauche du GIF (JPG/PNG/GIF)",
        filetypes=[("Fichiers image", "*.jpg *.jpeg *.png *.gif *.bmp")]
    )
    if path:
        global image_path
        image_path = path
        name = os.path.basename(path)
        image_var.set(name)
        drop_zone.mark_selected(name)
        status_bar.set_state("idle", f"Image prête : {name}")


def _launch(image_path_arg=None):
    try:
        app_module.main(image_path=image_path_arg)
    except Exception as e:
        status_bar.set_state("error", f"Échec : {e}")


def run_app():
    if not image_path:
        messagebox.showwarning(
            "Aucune image",
            "Veuillez d'abord sélectionner une image dans la zone de dépôt."
        )
        return
    status_bar.set_state("running", "Superposition avec image démarrée")
    threading.Thread(target=_launch, args=(image_path,), daemon=True).start()


def run_no_image():
    status_bar.set_state("running", "Superposition GIF seul démarrée")
    threading.Thread(target=_launch, daemon=True).start()


# ─────────────────────────────────────────────
#  FENÊTRE PRINCIPALE
# ─────────────────────────────────────────────

root = tk.Tk()
root.title("PatOpenCV — Superposition")
root.geometry("520x600")
root.configure(bg=C["bg_root"])
root.resizable(False, False)

# Centrer la fenêtre
root.update_idletasks()
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()
x  = (sw - 520) // 2
y  = (sh - 600) // 2
root.geometry(f"520x600+{x}+{y}")

image_var = tk.StringVar(value="")

# ─── Conteneur principal avec marges ───────
main = tk.Frame(root, bg=C["bg_root"])
main.pack(fill="both", expand=True, padx=28, pady=20)

# ─── EN-TÊTE ────────────────────────────────
header = tk.Frame(main, bg=C["bg_root"])
header.pack(fill="x", pady=(0, 4))

# Ligne de badge "v2"
badge_frame = tk.Frame(header, bg=C["bg_root"])
badge_frame.pack(anchor="w", pady=(0, 8))

badge_canvas = tk.Canvas(badge_frame, width=54, height=20,
                          bg=C["bg_root"], highlightthickness=0, bd=0)
badge_canvas.pack()
_round_rect(badge_canvas, 0, 0, 54, 20, r=6,
            fill="#1e2a4a", outline=C["accent_blue"], width=1)
badge_canvas.create_text(27, 10, text="v 2.0", fill=C["accent_blue"],
                          font=("SF Pro Display", 8, "bold"), anchor="center")

tk.Label(header, text="Superposition PatOpenCV",
         font=("SF Pro Display", 20, "bold"),
         fg=C["text_primary"], bg=C["bg_root"]).pack(anchor="w")

tk.Label(header, text="Superposez une image personnalisée à gauche du GIF facial",
         font=("SF Pro Display", 10),
         fg=C["text_secondary"], bg=C["bg_root"]).pack(anchor="w", pady=(4, 0))

# ─── SÉPARATEUR ─────────────────────────────
Divider(main).pack(fill="x", pady=18)

# ─── SECTION : SÉLECTION DE FICHIER ─────────
section_label = tk.Label(main, text="IMAGE DE SUPERPOSITION",
                          font=("SF Pro Display", 9, "bold"),
                          fg=C["text_muted"], bg=C["bg_root"])
section_label.pack(anchor="w", pady=(0, 8))

drop_zone = DropZone(main, textvariable=image_var, command=select_image,
                     width=464, height=110)
drop_zone.pack(fill="x")

# Bouton secondaire "Parcourir"
browse_row = tk.Frame(main, bg=C["bg_root"])
browse_row.pack(fill="x", pady=(10, 0))

ModernButton(browse_row, text="Parcourir…", command=select_image,
             bg=C["bg_card"], bg_hover=C["bg_card_hover"],
             bg_press=C["border"],
             fg=C["text_secondary"],
             icon="",
             width=140, height=36,
             font=("SF Pro Display", 10)).pack(side="left")

tk.Label(browse_row, text="ou cliquez directement dans la zone",
         font=("SF Pro Display", 9),
         fg=C["text_muted"], bg=C["bg_root"]).pack(side="left", padx=12)

# ─── SÉPARATEUR ─────────────────────────────
Divider(main).pack(fill="x", pady=18)

# ─── SECTION : LANCEMENT ────────────────────
tk.Label(main, text="LANCER LA SUPERPOSITION",
         font=("SF Pro Display", 9, "bold"),
         fg=C["text_muted"], bg=C["bg_root"]).pack(anchor="w", pady=(0, 12))

btn_row = tk.Frame(main, bg=C["bg_root"])
btn_row.pack(fill="x")

ModernButton(btn_row,
             text="Démarrer avec image",
             command=run_app,
             bg=C["accent_green"],
             bg_hover=C["accent_green_h"],
             bg_press=C["accent_green_p"],
             icon="",
             width=220, height=48,
             font=("SF Pro Display", 11, "bold")).pack(side="left")

tk.Frame(btn_row, bg=C["bg_root"], width=12).pack(side="left")

ModernButton(btn_row,
             text="GIF seul",
             command=run_no_image,
             bg=C["accent_orange"],
             bg_hover=C["accent_orange_h"],
             bg_press=C["accent_orange_p"],
             icon="",
             width=160, height=48,
             font=("SF Pro Display", 11, "bold")).pack(side="left")

# ─── SÉPARATEUR ─────────────────────────────
Divider(main).pack(fill="x", pady=18)

# ─── BARRE DE STATUT ────────────────────────
status_bar = StatusBar(main)
status_bar.pack(fill="x")

# ─── FOOTER ─────────────────────────────────
footer = tk.Frame(main, bg=C["bg_root"])
footer.pack(fill="x", side="bottom", pady=(16, 0))

Divider(footer).pack(fill="x", pady=(0, 10))

shortcuts = tk.Label(footer,
                      text="ESC  Fermer la webcam      Ctrl+C  Quitter",
                      font=("SF Pro Display", 9),
                      fg=C["text_muted"], bg=C["bg_root"])
shortcuts.pack()

root.mainloop()

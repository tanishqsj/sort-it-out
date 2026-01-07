import pygame
import random
import numpy as np
import sys

# --- CONFIGURATION ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
UI_HEIGHT = 150
PLAY_AREA_HEIGHT = SCREEN_HEIGHT - UI_HEIGHT

# Colors (Cyberpunk / Retro Game Palette)
C_BG = (10, 10, 18)
C_UI_BG = (30, 30, 40)
C_BAR_DEFAULT = (0, 180, 255)
C_BAR_ACTIVE = (255, 0, 80)
C_BAR_SWAP = (50, 255, 50)
C_BAR_DONE = (0, 255, 0) # Bright Green for the sweep
C_TEXT = (200, 200, 200)
C_ACCENT = (255, 200, 0)
C_UI_BORDER = (80, 80, 100)

# Audio Config
SAMPLE_RATE = 44100
DURATION = 0.06

# --- SOUND ENGINE ---
class SoundEngine:
    def __init__(self):
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=256)
        self.sounds = {}
        self.last_n = 0

    def rebuild(self, n):
        if n == self.last_n: return
        self.sounds = {}
        min_freq = 220.0
        max_freq = 880.0
        n_samples = int(SAMPLE_RATE * DURATION)
        t = np.linspace(0, DURATION, n_samples, False)
        envelope = np.linspace(1.0, 0.0, n_samples)
        
        for i in range(1, n + 1):
            freq = min_freq + ((max_freq - min_freq) * (i / n))
            wave = np.sign(np.sin(2 * np.pi * freq * t))
            wave = wave * envelope
            wave_data = (wave * 32767 * 0.1).astype(np.int16)
            stereo_wave = np.column_stack((wave_data, wave_data))
            self.sounds[i] = pygame.sndarray.make_sound(stereo_wave)
        self.last_n = n

    def play(self, val):
        if val in self.sounds:
            self.sounds[val].play()

# --- UI ELEMENTS ---
class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.hover = False

    def draw(self, screen, font):
        color = C_ACCENT if self.hover else C_UI_BORDER
        pygame.draw.rect(screen, color, self.rect, 2)
        pygame.draw.rect(screen, C_UI_BG, self.rect.inflate(-4, -4))
        txt_surf = font.render(self.text, True, C_TEXT)
        screen.blit(txt_surf, (self.rect.centerx - txt_surf.get_width()//2, self.rect.centery - txt_surf.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover and event.button == 1:
                self.callback()

class Slider:
    def __init__(self, x, y, w, min_val, max_val, initial):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial
        self.dragging = False

    def draw(self, screen, font):
        label = font.render(f"Speed: {int(self.val)}", True, C_TEXT)
        screen.blit(label, (self.rect.x, self.rect.y - 25))
        pygame.draw.rect(screen, C_UI_BORDER, (self.rect.x, self.rect.centery - 2, self.rect.width, 4))
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        knob_x = self.rect.x + (self.rect.width * ratio)
        pygame.draw.circle(screen, C_ACCENT, (int(knob_x), self.rect.centery), 8)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                rel_x = event.pos[0] - self.rect.x
                rel_x = max(0, min(rel_x, self.rect.width))
                ratio = rel_x / self.rect.width
                self.val = self.min_val + (ratio * (self.max_val - self.min_val))

class InputBox:
    def __init__(self, x, y, w, text=''):
        self.rect = pygame.Rect(x, y, w, 32)
        self.color = C_UI_BORDER
        self.text = text
        self.active = False

    def handle_event(self, event, on_submit):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = C_ACCENT if self.active else C_UI_BORDER
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    on_submit(self.text)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.unicode.isdigit():
                        self.text += event.unicode
                        if len(self.text) > 4: self.text = self.text[:4]

    def draw(self, screen, font):
        label = font.render(f"Size:", True, C_TEXT)
        screen.blit(label, (self.rect.x, self.rect.y - 25))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        txt_surface = font.render(self.text, True, C_TEXT)
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))

# --- SORTING ALGOS ---
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            yield arr, [j, j+1], 0
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                yield arr, [j, j+1], 1

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            yield arr, [j, j+1], 0
            arr[j + 1] = arr[j]
            yield arr, [j, j+1], 1
            j -= 1
        arr[j + 1] = key
        yield arr, [j+1], 1

def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            yield arr, [j, min_idx], 0
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        yield arr, [i, min_idx], 1

def quick_sort(arr):
    size = len(arr)
    stack = [0] * size
    top = -1
    top += 1; stack[top] = 0
    top += 1; stack[top] = size - 1
    while top >= 0:
        h = stack[top]; top -= 1
        l = stack[top]; top -= 1
        i = (l - 1)
        x = arr[h]
        for j in range(l, h):
            yield arr, [j, h], 0
            if arr[j] <= x:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                yield arr, [i, j], 1
        arr[i + 1], arr[h] = arr[h], arr[i + 1]
        yield arr, [i+1, h], 1
        p = i + 1
        if p - 1 > l:
            top += 1; stack[top] = l
            top += 1; stack[top] = p - 1
        if p + 1 < h:
            top += 1; stack[top] = p + 1
            top += 1; stack[top] = h

def heap_sort(arr):
    n = len(arr)
    def heapify(arr, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < n:
            yield arr, [i, l], 0
            if arr[l] > arr[largest]: largest = l
        if r < n:
            yield arr, [largest, r], 0
            if arr[r] > arr[largest]: largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            yield arr, [i, largest], 1
            yield from heapify(arr, n, largest)
    for i in range(n // 2 - 1, -1, -1):
        yield from heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        yield arr, [i, 0], 1
        yield from heapify(arr, i, 0)

def cocktail_shaker_sort(arr):
    n = len(arr)
    swapped = True
    start = 0
    end = n - 1
    while (swapped == True):
        swapped = False
        for i in range(start, end):
            yield arr, [i, i+1], 0
            if (arr[i] > arr[i + 1]):
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
                yield arr, [i, i+1], 1
        if (swapped == False): break
        swapped = False
        end = end - 1
        for i in range(end - 1, start - 1, -1):
            yield arr, [i, i+1], 0
            if (arr[i] > arr[i + 1]):
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
                yield arr, [i, i+1], 1
        start = start + 1

def gnome_sort(arr):
    index = 0
    while index < len(arr):
        if index == 0: index += 1
        yield arr, [index, index-1], 0
        if arr[index] >= arr[index - 1]:
            index += 1
        else:
            arr[index], arr[index - 1] = arr[index - 1], arr[index]
            yield arr, [index, index-1], 1
            index -= 1

def bogo_sort(arr):
    def is_sorted(a):
        for i in range(len(a) - 1):
            if a[i] > a[i+1]: return False
        return True
    while not is_sorted(arr):
        x, y = random.randint(0, len(arr)-1), random.randint(0, len(arr)-1)
        arr[x], arr[y] = arr[y], arr[x]
        yield arr, [x, y], 1

# --- MAIN GAME CLASS ---
class AlgoGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Algo Sort Master")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Consolas', 18)
        self.large_font = pygame.font.SysFont('Consolas', 28, bold=True)
        
        self.sound_engine = SoundEngine()
        
        # UI Components
        self.btn_start = Button(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 80, 100, 40, "START", self.start_sort)
        self.btn_reset = Button(SCREEN_WIDTH - 130, SCREEN_HEIGHT - 80, 100, 40, "RESET", self.reset_array)
        self.btn_prev = Button(50, SCREEN_HEIGHT - 80, 40, 40, "<", self.prev_algo)
        self.btn_next = Button(350, SCREEN_HEIGHT - 80, 40, 40, ">", self.next_algo)
        self.slider_speed = Slider(450, SCREEN_HEIGHT - 60, 200, 1, 120, 60)
        self.input_size = InputBox(700, SCREEN_HEIGHT - 60, 100, "100")

        # Algos
        self.algos = [
            ("Bubble Sort", bubble_sort),
            ("Insertion Sort", insertion_sort),
            ("Selection Sort", selection_sort),
            ("Quick Sort", quick_sort),
            ("Heap Sort", heap_sort),
            ("Cocktail Shaker", cocktail_shaker_sort),
            ("Gnome Sort", gnome_sort),
            ("BOGO SORT (Chaos)", bogo_sort)
        ]
        self.algo_idx = 0
        
        # Internal State
        self.arr_size = 100
        self.arr = []
        self.running = False
        self.finished = False
        self.sweep_idx = -1 # New: Tracks the victory sweep
        self.generator = None
        self.ops_count = 0
        
        self.reset_array()

    def reset_array(self):
        self.running = False
        self.finished = False
        self.sweep_idx = -1
        self.generator = None
        self.ops_count = 0
        
        current_name = self.algos[self.algo_idx][0]
        try:
            val = int(self.input_size.text)
        except ValueError:
            val = 50
            
        if "BOGO" in current_name:
            self.arr_size = max(1, min(val, 7))
        else:
            self.arr_size = max(2, min(val, 600))
        
        self.input_size.text = str(self.arr_size)
        self.arr = list(range(1, self.arr_size + 1))
        random.shuffle(self.arr)
        self.sound_engine.rebuild(self.arr_size)

    def start_sort(self):
        if not self.running and not self.finished and self.sweep_idx == -1:
            algo_func = self.algos[self.algo_idx][1]
            self.generator = algo_func(self.arr)
            self.running = True
        elif self.finished:
            self.reset_array()
            self.start_sort()

    def prev_algo(self):
        self.algo_idx = (self.algo_idx - 1) % len(self.algos)
        self.reset_array()

    def next_algo(self):
        self.algo_idx = (self.algo_idx + 1) % len(self.algos)
        self.reset_array()

    def handle_input(self, text):
        self.reset_array()

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                self.btn_start.handle_event(event)
                self.btn_reset.handle_event(event)
                self.btn_prev.handle_event(event)
                self.btn_next.handle_event(event)
                self.slider_speed.handle_event(event)
                self.input_size.handle_event(event, self.handle_input)

            active_indices = []
            op_type = -1
            
            # 1. SORTING LOGIC
            if self.running and self.generator:
                try:
                    self.arr, active_indices, op_type = next(self.generator)
                    self.ops_count += 1
                    for idx in active_indices:
                        if 0 <= idx < len(self.arr):
                            self.sound_engine.play(self.arr[idx])
                except StopIteration:
                    self.running = False
                    self.sweep_idx = 0 # Start the victory sweep!

            # 2. SWEEP LOGIC (Victory Lap)
            if not self.running and self.sweep_idx != -1:
                if self.sweep_idx < len(self.arr):
                    self.sound_engine.play(self.arr[self.sweep_idx])
                    self.sweep_idx += 1
                else:
                    self.finished = True
                    self.sweep_idx = -1 # Stop sweeping, fully done

            # --- DRAWING ---
            self.screen.fill(C_BG)
            
            bar_w = SCREEN_WIDTH / len(self.arr)
            max_h = PLAY_AREA_HEIGHT - 50
            max_val = max(self.arr) if self.arr else 1
            
            for i, val in enumerate(self.arr):
                h = (val / max_val) * max_h
                x = i * bar_w
                y = PLAY_AREA_HEIGHT - h
                
                # Color Logic
                color = C_BAR_DEFAULT
                
                if self.finished:
                    color = C_BAR_DONE # All Green
                elif self.sweep_idx != -1:
                    # In sweep mode: Green if passed, Blue if waiting
                    if i < self.sweep_idx:
                        color = C_BAR_DONE
                    else:
                        color = C_BAR_DEFAULT
                elif i in active_indices:
                    color = C_BAR_SWAP if op_type == 1 else C_BAR_ACTIVE
                
                pygame.draw.rect(self.screen, color, (x, y, bar_w + 1, h))
            
            # UI Background
            pygame.draw.rect(self.screen, C_UI_BG, (0, PLAY_AREA_HEIGHT, SCREEN_WIDTH, UI_HEIGHT))
            pygame.draw.line(self.screen, C_ACCENT, (0, PLAY_AREA_HEIGHT), (SCREEN_WIDTH, PLAY_AREA_HEIGHT), 2)

            # Draw Buttons
            self.btn_start.draw(self.screen, self.font)
            self.btn_reset.draw(self.screen, self.font)
            self.btn_prev.draw(self.screen, self.large_font)
            self.btn_next.draw(self.screen, self.large_font)
            self.slider_speed.draw(self.screen, self.font)
            self.input_size.draw(self.screen, self.font)

            # Draw Text
            algo_name = self.algos[self.algo_idx][0]
            name_surf = self.large_font.render(algo_name, True, C_ACCENT)
            self.screen.blit(name_surf, (110, SCREEN_HEIGHT - 90))
            
            stats = f"Ops: {self.ops_count} | Elements: {len(self.arr)}"
            stat_surf = self.font.render(stats, True, C_TEXT)
            self.screen.blit(stat_surf, (110, SCREEN_HEIGHT - 50))

            pygame.display.flip()
            
            # Tick Clock
            # We use the slider speed for BOTH sorting and the victory sweep
            if self.running or self.sweep_idx != -1:
                self.clock.tick(self.slider_speed.val)
            else:
                self.clock.tick(60)

if __name__ == "__main__":
    game = AlgoGame()
    game.run()

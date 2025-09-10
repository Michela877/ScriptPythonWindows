import ctypes
import time
import random
from datetime import datetime

# Strutture e funzioni per Windows
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

def get_screen_size():
    """Ottiene le dimensioni dello schermo"""
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def get_cursor_pos():
    """Ottiene la posizione corrente del mouse"""
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def set_cursor_pos(x, y):
    """Imposta la posizione del mouse"""
    user32.SetCursorPos(x, y)

def simulate_real_mouse_input():
    """Simula un input mouse reale che viene registrato da GetLastInputInfo()"""
    # Ottieni la posizione corrente
    x, y = get_cursor_pos()
    
    # Muovi il mouse di 1 pixel e poi torna indietro
    user32.SetCursorPos(x + 1, y)
    user32.SetCursorPos(x, y)
    
    # Invia un input mouse falso che viene registrato come attività utente
    user32.mouse_event(0x0001, 0, 0, 0, 0)  # MOUSEEVENTF_MOVE

def get_last_input_time():
    """Ottiene il tempo dell'ultimo input utente"""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    user32.GetLastInputInfo(ctypes.byref(lii))
    return lii.dwTime

def get_idle_time():
    """Calcola il tempo di inattività in secondi"""
    current_tick = kernel32.GetTickCount()
    last_input = get_last_input_time()
    return (current_tick - last_input) // 1000

def reset_idle_time():
    """Resetta il timer di inattività simulando un input reale"""
    simulate_real_mouse_input()
    print(f"{datetime.now().strftime('%H:%M:%S')} - Timer inattività resettato")

def simulate_human_activity():
    """Simula attività umana realisticamente"""
    screen_width, screen_height = get_screen_size()
    
    # Tipi di attività umana
    activities = [
        lambda: simulate_scrolling(screen_width, screen_height),
        lambda: simulate_reading(screen_width, screen_height),
        lambda: simulate_window_switching(screen_width, screen_height),
        lambda: simulate_typing_breaks(screen_width, screen_height)
    ]
    
    # Esegui un'attività casuale
    random.choice(activities)()
    
    # Resetta sempre il timer di inattività
    reset_idle_time()

def simulate_scrolling(screen_width, screen_height):
    """Simula scrolling di una pagina"""
    print("Simulazione scrolling...")
    
    start_x = random.randint(200, screen_width - 200)
    start_y = random.randint(200, screen_height - 300)
    
    # Muovi alla posizione di partenza
    set_cursor_pos(start_x, start_y)
    time.sleep(0.5)
    
    # Scrolling verso il basso
    for y in range(start_y, start_y + 150, 3):
        set_cursor_pos(start_x, y)
        time.sleep(0.03)
    
    time.sleep(random.uniform(1.0, 2.0))
    
    # Scrolling verso l'alto
    for y in range(start_y + 150, start_y, -3):
        set_cursor_pos(start_x, y)
        time.sleep(0.03)

def simulate_reading(screen_width, screen_height):
    """Simula lettura di una pagina"""
    print("Simulazione lettura...")
    
    # Muovi il mouse come se stessi seguendo il testo con gli occhi
    for _ in range(3):
        start_x = random.randint(100, screen_width - 100)
        start_y = random.randint(100, screen_height - 100)
        
        set_cursor_pos(start_x, start_y)
        time.sleep(random.uniform(2.0, 4.0))
        
        # Piccolo movimento orizzontale (simula cambio riga)
        set_cursor_pos(start_x + 50, start_y)
        time.sleep(random.uniform(1.5, 3.0))

def simulate_window_switching(screen_width, screen_height):
    """Simula cambio tra finestre"""
    print("Simulazione cambio finestre...")
    
    # Aree dove potrebbero essere i pulsanti delle finestre
    areas = [
        (50, 50),  # Angolo superiore sinistro
        (screen_width - 100, 50),  # Angolo superiore destro
        (50, screen_height - 100),  # Angolo inferiore sinistro
        (screen_width - 100, screen_height - 100)  # Angolo inferiore destro
    ]
    
    for target_x, target_y in random.sample(areas, 2):
        current_x, current_y = get_cursor_pos()
        
        # Movimento diretto verso l'area
        steps = 15
        for i in range(steps):
            progress = i / (steps - 1)
            x = int(current_x + (target_x - current_x) * progress)
            y = int(current_y + (target_y - current_y) * progress)
            set_cursor_pos(x, y)
            time.sleep(0.05)
        
        time.sleep(random.uniform(2.0, 5.0))

def simulate_typing_breaks(screen_width, screen_height):
    """Simula pause durante la digitazione"""
    print("Simulazione pause digitazione...")
    
    for _ in range(random.randint(2, 4)):
        # Piccolo movimento casuale
        current_x, current_y = get_cursor_pos()
        target_x = current_x + random.randint(-20, 20)
        target_y = current_y + random.randint(-20, 20)
        
        target_x = max(10, min(target_x, screen_width - 10))
        target_y = max(10, min(target_y, screen_height - 10))
        
        set_cursor_pos(target_x, target_y)
        time.sleep(random.uniform(3.0, 8.0))

def main():
    print("SIMULATORE ATTIVITÀ UMANA - ANTI INATTIVITÀ")
    print("Il timer di inattività viene resettato ad ogni movimento")
    print("Premi Ctrl+C per interrompere")
    print("=" * 60)
    
    try:
        activity_count = 0
        
        while True:
            # Controlla lo stato di inattività
            idle_time = get_idle_time()
            print(f"\rInattività: {idle_time:3d} secondi | Attività: {activity_count:3d}", end="")
            
            # Se sta per essere considerato inattivo, agisci immediatamente
            if idle_time > 25:
                print(f"\n⚠️  Attenzione: inattività rilevata ({idle_time}s), attivando...")
                simulate_human_activity()
                activity_count += 1
            
            # Altrimenti, attività programmata ogni 10-20 secondi
            elif random.random() < 0.05:  # 5% di probabilità ogni secondo
                simulate_human_activity()
                activity_count += 1
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nProgramma interrotto")

if __name__ == "__main__":
    try:
        # Test delle funzioni
        get_cursor_pos()
        print("✓ Sistema Windows pronto")
        print("✓ Timer inattività attivo")
        main()
    except Exception as e:
        print(f"Errore: {e}")

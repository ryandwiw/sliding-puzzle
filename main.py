import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import pygame.freetype
import pygame.mixer


# Inisialisasi Pygame
pygame.init()
pygame.mixer.init()
pygame.freetype.init()

# Konstanta
SCREEN_SIZE = 600
GRID_SIZE = 4
CELL_SIZE = SCREEN_SIZE // GRID_SIZE
cube_size = 2.0
puzzle_solved = False
slide_sound = pygame.mixer.Sound("assets/move.wav")
win_sound = pygame.mixer.Sound("assets/win.wav")
win_sound_played = False

# Backsound initialization
pygame.mixer.music.load("assets/backsound.wav")
pygame.mixer.music.set_volume(0.5)  # Adjust the volume if needed

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

loaded_textures = {}

def load_texture(number):
    if number == "empty":
        # Load empty texture
        if number not in loaded_textures:
            empty_texture_path = 'assets/empty.png'
            empty_texture_surface = pygame.image.load(empty_texture_path)
            empty_texture_data = pygame.image.tostring(empty_texture_surface, 'RGBA', True)
            width, height = empty_texture_surface.get_width(), empty_texture_surface.get_height()

            glEnable(GL_TEXTURE_2D)
            tex_id = glGenTextures(1)

            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, empty_texture_data)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            loaded_textures[number] = tex_id

        return loaded_textures[number]
    else:
        # Load numbered texture
        if number not in loaded_textures:
            texture_path = f'assets/{number}.png'
            texture_surface = pygame.image.load(texture_path)
            texture_data = pygame.image.tostring(texture_surface, 'RGBA', True)
            width, height = texture_surface.get_width(), texture_surface.get_height()

            glEnable(GL_TEXTURE_2D)
            tex_id = glGenTextures(1)

            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            loaded_textures[number] = tex_id

        return loaded_textures[number]

def load_background_texture():

    background_texture_path = 'assets/back.png'

    if "background" not in loaded_textures:
        background_texture_surface = pygame.image.load(background_texture_path)
        background_texture_data = pygame.image.tostring(background_texture_surface, 'RGBA', True)
        width, height = background_texture_surface.get_width(), background_texture_surface.get_height()

        glEnable(GL_TEXTURE_2D)
        tex_id = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, background_texture_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


        loaded_textures["background"] = tex_id

    return loaded_textures["background"]

def shuffle_numbers():
    global numbers , puzzle_solved
    
    if not puzzle_solved:
            sorted_numbers = list(range(1, GRID_SIZE * GRID_SIZE))
            sorted_numbers.append(0)
        
            while True:
                random.shuffle(sorted_numbers)
                if is_solvable(sorted_numbers):
                    numbers = sorted_numbers
                    break

def is_solvable(nums):
    inversion_count = 0
    for i in range(len(nums) - 1):
        for j in range(i + 1, len(nums)):
            if nums[i] > nums[j] and nums[i] != 0 and nums[j] != 0:
                inversion_count += 1
    blank_row, _ = divmod(nums.index(0), GRID_SIZE)
    return (GRID_SIZE % 2 == 1 and inversion_count % 2 == 0) or \
           (GRID_SIZE % 2 == 0 and ((GRID_SIZE - blank_row) % 2 == 1) == (inversion_count % 2 == 0))
           
def draw_background(x, y, z, size):
    texture_id = load_background_texture()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glBegin(GL_QUADS)

    glTexCoord2f(0, 0)
    glVertex3f(x - size / 2, y - size / 2, z)

    glTexCoord2f(1, 0)
    glVertex3f(x + size / 2, y - size / 2, z)

    glTexCoord2f(1, 1)
    glVertex3f(x + size / 2, y + size / 2, z)

    glTexCoord2f(0, 1)
    glVertex3f(x - size / 2, y + size / 2, z)

    glEnd()

    glDisable(GL_TEXTURE_2D)
    
def draw_text(x, y, z, size, text):
    font_size = 12
    font = pygame.freetype.SysFont(None, font_size)
    text_surface, _ = font.render(text, (255, 255, 255), (0, 0, 0))

    text_data = pygame.image.tostring(text_surface, 'RGBA', True)

    glRasterPos3d(x - size / 4, y - size / 4, z + size)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
def draw_cube(x, y, z, size, number):
    glPushMatrix()
    draw_background(x, y, z, size)
    half_size = size / 2
    
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Material Properties
    glMaterialfv(GL_FRONT, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
    glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialf(GL_FRONT, GL_SHININESS, 100.0)
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, load_texture(number))

    glBegin(GL_QUADS)

    # Persegi depan
    glTexCoord2f(0, 0)
    glVertex3f(x - half_size, y - half_size, z + half_size)
    glTexCoord2f(1, 0)
    glVertex3f(x + half_size, y - half_size, z + half_size)
    glTexCoord2f(1, 1)
    glVertex3f(x + half_size, y + half_size, z + half_size)
    glTexCoord2f(0, 1)
    glVertex3f(x - half_size, y + half_size, z + half_size)

    glTexCoord2f(0, 0)
    glVertex3f(x - half_size, y - half_size, z - half_size)
    glTexCoord2f(1, 0)
    glVertex3f(x + half_size, y - half_size, z - half_size)
    glTexCoord2f(1, 1)
    glVertex3f(x + half_size, y + half_size, z - half_size)
    glTexCoord2f(0, 1)
    glVertex3f(x - half_size, y + half_size, z - half_size)
    
    glEnd()
    glDisable(GL_TEXTURE_2D)
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, load_texture("empty"))
    glBegin(GL_QUADS)

    # Persegi kiri
    glTexCoord2f(0, 0)
    glVertex3f(x - half_size, y - half_size, z - half_size)
    glTexCoord2f(1, 0)
    glVertex3f(x - half_size, y - half_size, z + half_size)
    glTexCoord2f(1, 1)
    glVertex3f(x - half_size, y + half_size, z + half_size)
    glTexCoord2f(0, 1)
    glVertex3f(x - half_size, y + half_size, z - half_size)

    # Persegi kanan
    glTexCoord2f(0, 0)
    glVertex3f(x + half_size, y - half_size, z - half_size)
    glTexCoord2f(1, 0)
    glVertex3f(x + half_size, y - half_size, z + half_size)
    glTexCoord2f(1, 1)
    glVertex3f(x + half_size, y + half_size, z + half_size)
    glTexCoord2f(0, 1)
    glVertex3f(x + half_size, y + half_size, z - half_size)

    # Persegi atas
    glTexCoord2f(0, 0)
    glVertex3f(x - half_size, y + half_size, z + half_size)
    glTexCoord2f(1, 0)
    glVertex3f(x + half_size, y + half_size, z + half_size)
    glTexCoord2f(1, 1)
    glVertex3f(x + half_size, y + half_size, z - half_size)
    glTexCoord2f(0, 1)
    glVertex3f(x - half_size, y + half_size, z - half_size)

    # Persegi bawah
    glTexCoord2f(0, 0)
    glVertex3f(x - half_size, y - half_size, z + half_size)
    glTexCoord2f(1, 0)
    glVertex3f(x + half_size, y - half_size, z + half_size)
    glTexCoord2f(1, 1)
    glVertex3f(x + half_size, y - half_size, z - half_size)
    glTexCoord2f(0, 1)
    glVertex3f(x - half_size, y - half_size, z - half_size)

    glEnd()

    glDisable(GL_TEXTURE_2D)
    # draw_text(x, y, z, size, str(number))
    glPopMatrix()

def draw_board():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    draw_background(0, 0.8, 1, SCREEN_SIZE)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            index = i * GRID_SIZE + j
            if index < len(numbers) and numbers[index] != 0:  # Abaikan angka 0
                x = j * cube_size * 1.5 - cube_size * 1.5 * (GRID_SIZE - 1) / 2
                y = i * cube_size * 1.5 - cube_size * 1.5 * (GRID_SIZE - 1) / 2
                z = 0
                number = numbers[index]
                draw_cube(x, y, z, cube_size, number)

    glDisable(GL_LIGHTING)
    glDisable(GL_LIGHT0)
                            
def find_empty():
    index = numbers.index(0)
    row = index // GRID_SIZE
    col = index % GRID_SIZE
    return row, col, index

def move_number(direction):
    global numbers
    row, col, index = find_empty()

    if direction == "UP" and row > 0:
        target_index = (row - 1) * GRID_SIZE + col
    elif direction == "DOWN" and row < GRID_SIZE - 1:
        target_index = (row + 1) * GRID_SIZE + col
    elif direction == "LEFT" and col > 0:
        target_index = row * GRID_SIZE + (col - 1)
    elif direction == "RIGHT" and col < GRID_SIZE - 1:
        target_index = row * GRID_SIZE + (col + 1)
    else:
        return

    # Tukar angka dengan kotak kosong
    numbers[index], numbers[target_index] = numbers[target_index], numbers[index]
    
def is_winner():
    expected_order = [
        13, 14, 15, 0,
        9, 10, 11, 12,
        5, 6, 7, 8,
        1, 2, 3, 4
    ]
    return numbers == expected_order

def draw_menu(texture_path='empty'):
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, load_texture(texture_path))
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(-SCREEN_SIZE / 2, -SCREEN_SIZE / 2, 1)
    glTexCoord2f(1, 0)
    glVertex3f(SCREEN_SIZE / 2, -SCREEN_SIZE / 2, 1)
    glTexCoord2f(1, 1)
    glVertex3f(SCREEN_SIZE / 2, SCREEN_SIZE / 2, 1)
    glTexCoord2f(0, 1)
    glVertex3f(-SCREEN_SIZE / 2, SCREEN_SIZE / 2, 1)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    draw_text(-2, 0, 0, cube_size, "Press Enter to Start")

def draw_game_over(texture_path='empty'):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, load_texture(texture_path))
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(-SCREEN_SIZE / 2, -SCREEN_SIZE / 2, 1)
    glTexCoord2f(1, 0)
    glVertex3f(SCREEN_SIZE / 2, -SCREEN_SIZE / 2, 1)
    glTexCoord2f(1, 1)
    glVertex3f(SCREEN_SIZE / 2, SCREEN_SIZE / 2, 1)
    glTexCoord2f(0, 1)
    glVertex3f(-SCREEN_SIZE / 2, SCREEN_SIZE / 2, 1)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    draw_text(-3, 1, 0, cube_size, "You Win. Press Enter to Play Again.")
    draw_text(-3, 0, 0, cube_size, "Press Esc to Exit.")

def handle_menu_input():
    # Logika input untuk menu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return True
    return False

def handle_game_over_input():
    # Logika input untuk layar game over
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            elif event.key == pygame.K_RETURN:
                return True
    return False

def initialize_correct_order():
    global numbers
    numbers = [
        13, 14, 0, 15,
        9, 10, 11, 12,
        5, 6, 7, 8,
        1, 2, 3, 4
    ]


def move_number(direction):
    global numbers
    row, col, index = find_empty()

    if direction == "UP" and row > 0:
        target_index = (row - 1) * GRID_SIZE + col
    elif direction == "DOWN" and row < GRID_SIZE - 1:
        target_index = (row + 1) * GRID_SIZE + col
    elif direction == "LEFT" and col > 0:
        target_index = row * GRID_SIZE + (col - 1)
    elif direction == "RIGHT" and col < GRID_SIZE - 1:
        target_index = row * GRID_SIZE + (col + 1)
    else:
        return

    # Tukar angka dengan kotak kosong
    numbers[index], numbers[target_index] = numbers[target_index], numbers[index]

    # Panggil suara slide setiap kali ada geser
    slide_sound.play()


def main():
    global puzzle_solved
    pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Sliding Puzzle Angka")
    gluPerspective(45, (SCREEN_SIZE / SCREEN_SIZE), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -15)

    # Enable Lighting
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Set Light Properties
    light_position = (5, 5, 5, 1)  # (x, y, z, w)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))  # White diffuse light
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))  # White specular light
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))  # Low intensity ambient light
    
    global numbers
    numbers = list(range(1, GRID_SIZE * GRID_SIZE))
    numbers.append(0)  # 0 akan dianggap sebagai kotak kosong
    shuffle_numbers()

    
    game_running = False  # Menandakan apakah permainan sedang berjalan

    clock = pygame.time.Clock()
    pygame.mixer.music.play(-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move_number("UP")
                elif event.key == pygame.K_DOWN:
                    move_number("DOWN")
                elif event.key == pygame.K_LEFT:
                    move_number("RIGHT")
                elif event.key == pygame.K_RIGHT:
                    move_number("LEFT")
                elif event.key == pygame.K_p:
                    initialize_correct_order()
                elif event.key == pygame.K_RETURN:
                    if not game_running or puzzle_solved:
                        game_running = True
                        puzzle_solved = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Tombol kiri mouse
                if not game_running:
                    game_running = True
                else:
                    # Logika untuk menghentikan permainan jika di klik mouse saat permainan berjalan
                    pass

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if game_running:
            # Menambahkan kondisi untuk berhenti putar saat kubus berada di depan layar
            if getattr(glRotatef, 'angle', 0) < 360:
                glRotatef(3, 3, 1, 1)
                glRotatef.angle = getattr(glRotatef, 'angle', 0) + 3

            draw_board()

            if is_winner() and not puzzle_solved and not win_sound_played:
                draw_game_over()
                win_sound.play()

                if handle_game_over_input():
                    game_running = True
                    puzzle_solved = False
                    shuffle_numbers()
                    

        else:
            draw_menu()

            if handle_menu_input():
                game_running = True

        pygame.display.flip()
        clock.tick(60)  # Batasi kecepatan frame ke 30 fps

if __name__ == "__main__":
    main()
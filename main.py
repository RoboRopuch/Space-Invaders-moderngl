import struct
from colorsys import hls_to_rgb as hls
from random import uniform
import numpy as np
from pyrr import Matrix44
import moderngl
from _main import SetupScene
from shaders import *
import pygame
from pygame import mixer
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def grid(size, steps):
    u = np.repeat(np.linspace(-size, size, steps), 2)
    v = np.tile([-size, size], steps)
    w = np.zeros(steps * 2)
    return np.concatenate([np.dstack([u, v, w]), np.dstack([v, u, w])])

def random_color():
    return hls(uniform(0.0, 1.0), 0.5, 0.5)

class Scene(SetupScene):
    title = "Combined Objects"
    gl_version = (3, 3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ship_position = np.array([0.0, 13, 0.0], dtype=np.float32)

        self.start_render_particles = False
        self.bullet_list = []
        self.bullets_positions = []

        self.enemies_position_list = []
        for i in np.arange(-12, 15, 3):
            for j in np.arange(0, 12, 3):
                self.enemies_position_list.append(np.array([i, -14, j], dtype=np.float32))

        self.grid_size = 15
        self.enemies_list = []

        self.points = 0
        self.game_end = False

        # Initialize Pygame mixer
        pygame.mixer.init()
        mixer.init()
        background_music_path = os.path.join(BASE_DIR, 'audio', 'background.mp3')

        pygame.mixer.music.load(background_music_path)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

        self.shoot_sound_path = background_music_path = os.path.join(BASE_DIR, 'audio', 'bullet.wav')
        self.death_sound_path = background_music_path = os.path.join(BASE_DIR, 'audio', 'death.wav')

        self.shoot_sound = mixer.Sound(self.shoot_sound_path)
        self.death_sound = mixer.Sound(self.death_sound_path)

        self.death_sound.set_volume(0.1)
        self.shoot_sound.set_volume(0.1)

        # initialize SimpleGrid
        self.prog_grid = self.ctx.program(
            vertex_shader=vertex_shader_grid,
            fragment_shader=fragment_shader_grid
        )
        self.mvp_grid = self.prog_grid['Mvp']
        self.vbo_grid = self.ctx.buffer(grid(self.grid_size, 10).astype('f4'))
        self.vao_grid = self.ctx.simple_vertex_array(self.prog_grid, self.vbo_grid, 'in_vert')

        # Initialize Bullet
        self.bullet_color = random_color()
        self.prog_bullet = self.ctx.program(
            vertex_shader=vertex_shader_bullet,
            fragment_shader=fragment_shader_bullet
        )

        self.mvp_bullet = self.prog_bullet['Mvp']
        self.prog_bullet['lightIntensity'] = 1.0
        obj = self.load_scene('bullet.obj')


        self.vbo_bullet = self.ctx.buffer(struct.pack(
            '15f',
            *self.bullet_color,
            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        ))
        self.vao_wrapper = obj.root_nodes[0].mesh.vao
        self.vao_wrapper.buffer(self.vbo_bullet, '3f 3f 9f/i', ['in_color', 'in_origin', 'in_basis'])

        self.vao_bullet = self.vao_wrapper.instance(self.prog_bullet)
        self.bullet_list.append(self.vao_wrapper.instance(self.prog_bullet))

        # initialize gwon
        self.gwon_color = random_color()
        self.prog_gwon = self.ctx.program(
            vertex_shader=vertex_shader_game_over,
            fragment_shader=fragment_shader_game_over
        )

        self.mvp_gwon = self.prog_gwon['Mvp']
        self.light_gwon = self.prog_gwon['Light']

        obj = self.load_scene('gwon.obj')
        self.vbo_gwon = self.ctx.buffer(struct.pack(
            '15f',
            *self.gwon_color,
            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        ))
        vao_wrapper = obj.root_nodes[0].mesh.vao
        vao_wrapper.buffer(self.vbo_gwon, '3f 3f 9f/i', ['in_color', 'in_origin', 'in_basis'])
        self.vao_gwon = vao_wrapper.instance(self.prog_gwon)


        # initialize gover
        self.gover_color = random_color()
        self.prog_gover = self.ctx.program(
            vertex_shader=vertex_shader_game_over,
            fragment_shader=fragment_shader_game_over
        )

        self.mvp_gover = self.prog_gover['Mvp']
        self.light_gover = self.prog_gover['Light']

        obj = self.load_scene('gover.obj')
        self.vbo_gover = self.ctx.buffer(struct.pack(
            '15f',
            *self.gover_color,
            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        ))
        vao_wrapper = obj.root_nodes[0].mesh.vao
        vao_wrapper.buffer(self.vbo_gover, '3f 3f 9f/i', ['in_color', 'in_origin', 'in_basis'])
        self.vao_gover = vao_wrapper.instance(self.prog_gover)

        # Initialize Ship
        self.ship_color = random_color()
        self.prog_ship = self.ctx.program(
            vertex_shader=vertex_shader_ship,
            fragment_shader=fragment_shader_ship
        )
        self.prog_ship['lightIntensity'] = 1.0
        self.mvp_ship = self.prog_ship['Mvp']

        obj = self.load_scene('spaceship_with_fire.obj')
        self.vbo_ship = self.ctx.buffer(struct.pack(
            '15f',
            *self.ship_color,
            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        ))
        vao_wrapper = obj.root_nodes[0].mesh.vao
        vao_wrapper.buffer(self.vbo_ship, '3f 3f 9f/i', ['in_color', 'in_origin', 'in_basis'])
        self.vao_ship = vao_wrapper.instance(self.prog_ship)

        # initialize enemies
        self.prog_enemy = self.ctx.program(
            vertex_shader=vertex_shader_enemy,
            fragment_shader=fragment_shader_enemy
        )
        self.prog_enemy['lightIntensity'] = 1.0
        self.mvp_enemy = self.prog_enemy['Mvp']

        obj = self.load_scene('enemy.obj')
        for i in range(36):
            self.enemy_color = random_color()
            self.vbo_enemy = self.ctx.buffer(struct.pack(
                '15f',
                *self.enemy_color,
                0.0, 0.0, 0.0,
                1.0, 0.0, 0.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 1.0,
            ))
            vao_wrapper = obj.root_nodes[0].mesh.vao
            vao_wrapper.buffer(self.vbo_enemy, '3f 3f 9f/i', ['in_color', 'in_origin', 'in_basis'])
            self.enemies_list.append(vao_wrapper.instance(self.prog_enemy))

        # initialize enemy movement variables
        self.enemy_current_step = 0
        self.enemy_time_since_last_step = 0
        self.enemy_step_interval = 1.0


    def particle(self, x, y):
        a = np.random.uniform(0.0, np.pi * 2.0)
        r = np.random.uniform(0.0, 0.004)
        return np.array([x, y, np.cos(a) * r, np.sin(a) * r]).astype('f4')


    def update_enemy_positions(self, frame_time):
        self.enemy_time_since_last_step += frame_time

        if self.enemy_time_since_last_step >= self.enemy_step_interval:
            self.enemy_time_since_last_step = 0

            if self.enemy_current_step == 0:
                for i in range(len(self.enemies_list)):
                    self.enemies_position_list[i][2] += 2.0

            elif 1 <= self.enemy_current_step <= 3:
                for i in range(len(self.enemies_list)):
                    self.enemies_position_list[i][0] -= 2.0

            elif self.enemy_current_step == 4:
                for i in range(len(self.enemies_list)):
                    self.enemies_position_list[i][2] -= 2.0

            elif 5 <= self.enemy_current_step <= 7:
                for i in range(len(self.enemies_list)):
                    self.enemies_position_list[i][0] += 2.0

            elif self.enemy_current_step == 8:
                for i in range(len(self.enemies_list)):
                    self.enemies_position_list[i][1] += 2.0

            self.enemy_current_step = (self.enemy_current_step + 1) % 9

    def key_event(self, key, action, modifiers):
        """Handle key events."""
        if self.vao_ship != None:
            if action == self.wnd.keys.ACTION_PRESS:
                step_size = 2 * self.grid_size / 10
                if key == self.wnd.keys.UP:
                    if self.ship_position[2] < 9:
                        self.ship_position[2] += step_size 
                    else:
                        print('CANT GO HIGHER')
                elif key == self.wnd.keys.DOWN:
                    if self.ship_position[2] > 0:
                        self.ship_position[2] -= step_size 
                    else:
                        print('CANT GO LOWER')
                elif key == self.wnd.keys.LEFT:
                    if self.ship_position[0] < 13:
                        self.ship_position[0] += step_size 
                    else:
                        print("CANNOT LEAVE THE BOARD ")
                elif key == self.wnd.keys.RIGHT:
                    if self.ship_position[0] > -13:
                        self.ship_position[0] -= step_size 
                    else:
                        print("CANNOT LEAVE THE BOARD ")
                elif key == self.wnd.keys.Z:
                    if self.ship_position[1] > -12:
                        self.ship_position[1] -= step_size 
                    else:
                        print("CANNOT LEAVE THE BOARD ")
                elif key == self.wnd.keys.X:
                    if self.ship_position[1] < 12:
                        self.ship_position[1] += step_size
                    else:
                        print("CANNOT LEAVE THE BOARD ")
                elif key == self.wnd.keys.SPACE:
                    self.shoot_sound.play()
                    bullet_position = self.ship_position.copy()
                    bullet_position[1] -= 2
                    self.bullets_positions.append(np.array(bullet_position, dtype=np.float32))
                    self.bullet_list.append(self.vao_wrapper.instance(self.prog_bullet))

    def update_bullet_positions(self, step_size):
        i = 0
        while i < len(self.bullets_positions):
            bullet_position = self.bullets_positions[i]
            bullet_position[1] -= step_size

            if bullet_position[1] < -20:
                del self.bullets_positions[i]
                del self.bullet_list[i]
            else:
                self.bullets_positions[i] = np.array(bullet_position, dtype=np.float32)
                i += 1


    def render(self, time, frame_time):
        self.ctx.clear(0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        if self.game_end:
            if len(self.enemies_list) == 0:
                self.game_won()
            else:
                self.game_over()

        self.prog_ship['lightIntensity'].value = 2.  
        self.prog_bullet['lightIntensity'].value = 1.0
        self.prog_enemy['lightIntensity'].value = 1.0

        if(self.start_render_particles):
            self.ctx.point_size = 4.0
            self.render_vao.render(moderngl.POINTS, 100)
            self.vao1_particles.transform(self.vbo2_particles, moderngl.POINTS, 100)
            self.ctx.copy_buffer(self.vbo1_particles, self.vbo2_particles)

        # Render SimpleGrid
        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (0.0, 30.0, 30.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
        )
        self.mvp_grid.write((proj * lookat).astype('f4'))
        self.vao_grid.render(moderngl.LINES)
        self.update_enemy_positions(frame_time)

        # Render Ship
        scale_factor = 0.1
        self.prog_ship['scale_factor'].value = scale_factor
        camera_pos =(-100, 10, -20.0)
        light_pos = (0, 0, -20.0)

        ship_model = Matrix44.from_translation(self.ship_position).astype('f4')
        ship_mvp = (proj * lookat * ship_model).astype('f4')
        self.mvp_ship.write(ship_mvp.tobytes())

        self.prog_ship['lightPos'].value = light_pos
        self.prog_ship['viewPos'].value = camera_pos

        if self.vao_ship != None:
            self.vao_ship.render()

        # Render Bullet
        scale_factor = 0.1
        self.prog_bullet['scale_factor'].value = scale_factor

        self.update_bullet_positions(frame_time*30)

        for i in range(len(self.bullets_positions)):

            bullet_model = Matrix44.from_translation(self.bullets_positions[i]).astype('f4')
            bullet_mvp = (proj * lookat * bullet_model).astype('f4')
            self.mvp_bullet.write(bullet_mvp.tobytes())
            self.prog_bullet['lightPos'].value = light_pos
            self.prog_bullet['viewPos'].value = camera_pos

            self.bullet_list[i].render()

        # Render Enemy
        for i in reversed(range(len(self.enemies_list))):

            scale_factor = 0.12
            self.prog_enemy['scale_factor'].value = scale_factor
            enemy_model = Matrix44.from_translation(self.enemies_position_list[i]).astype('f4')
            enemy_mvp = (proj * lookat * enemy_model).astype('f4')
            self.mvp_enemy.write(enemy_mvp.tobytes())
            self.prog_enemy['lightPos'].value = light_pos
            self.prog_enemy['viewPos'].value = camera_pos

            self.enemies_list[i].render()

            if self.vao_ship != None:

                ship_box = [self.ship_position[0] - 1, self.ship_position[0] + 1,
                            self.ship_position[1] - 1, self.ship_position[1] + 1,
                            self.ship_position[2] - 1, self.ship_position[2] + 1]

                enemy_box = [self.enemies_position_list[i][0] - 1, self.enemies_position_list[i][0] + 1,
                            self.enemies_position_list[i][1] - 1, self.enemies_position_list[i][1] + 1,
                            self.enemies_position_list[i][2] - 1, self.enemies_position_list[i][2] + 1]

                for j in range(len(self.bullets_positions)):
                    bullet_box = [self.bullets_positions[j][0] - 0.5, self.bullets_positions[j][0] + 0.5,
                                self.bullets_positions[j][1] - 0.5, self.bullets_positions[j][1] + 0.5,
                                self.bullets_positions[j][2] - 0.5, self.bullets_positions[j][2] + 0.5]

                    if check_collision(bullet_box, enemy_box):
                        self.death_sound.play()
                        self.points += 10
                        print(f"Points: {self.points}")

                        self.start_render_particles = True
                        self.prog_particles = self.ctx.program(
                            vertex_shader=vertex_shader_particle,
                            fragment_shader=fragment_shader_particle
                        )
                        self.transform_particles = self.ctx.program(
                            vertex_shader = vertex_shader_particle_transform_test,
                            varyings=['out_pos', 'out_vel']
                        )

                        self.acc_particles = self.transform_particles['Acc']
                        self.acc_particles.value = (0.0, -0.0001)
                        z = self.enemies_position_list[i][1]+14
                        x, y = self.enemies_position_list[i][0]/30 + 1/30,self.enemies_position_list[i][2]/30 + 14/30 -z/30
                        self.vbo1_particles = self.ctx.buffer(b''.join(self.particle(-x,y) for _ in range(100)))
                        self.vbo2_particles = self.ctx.buffer(b''.join(self.particle(0.1,0.1) for _ in range(100)))

                        self.vao1_particles = self.ctx.simple_vertex_array(self.transform_particles, self.vbo1_particles, 'in_pos', 'in_vel')
                        self.vao2_particles = self.ctx.simple_vertex_array(self.transform_particles, self.vbo2_particles, 'in_pos', 'in_vel')

                        self.render_vao = self.ctx.vertex_array(self.prog_particles, [
                            (self.vbo1_particles, '2f 2x4', 'in_vert'),
                        ])

                        self.idx = 0
                        del self.enemies_position_list[i]
                        del self.enemies_list[i]
                        if len(self.enemies_list) == 0:
                            self.game_end = True

                if check_collision(ship_box, enemy_box):
                    self.game_end = True

    def game_over(self):
        print("Game Over: Ship collided with an enemy!")
        self.vao_ship = None

        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (0.0, 30.0, 30.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
        )

        gover_model = Matrix44.from_translation((1.5, 13, 0.0)).astype('f4')
        gover_mvp = (proj * lookat * gover_model).astype('f4')
        self.mvp_gover.write(gover_mvp.tobytes())

        self.prog_gover['scale_factor'] = 0.2
        self.prog_gover['Light'] = (0.0, -18, 30.0)

        self.vao_gover.render()

    def game_won(self):
        print("Game WON!")
        self.vao_ship = None

        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (0.0, 30.0, 30.0),
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
        )

        gwon_model = Matrix44.from_translation((1.5, 13, 0.0)).astype('f4')
        gwon_mvp = (proj * lookat * gwon_model).astype('f4')
        self.mvp_gwon.write(gwon_mvp.tobytes())

        self.prog_gwon['scale_factor'] = 0.2
        self.prog_gwon['Light'] = (0.0, -18, 30.0)

        self.vao_gwon.render()


def check_collision(box1, box2):
    return not (box1[1] < box2[0] or
                box1[0] > box2[1] or
                box1[3] < box2[2] or
                box1[2] > box2[3] or
                box1[5] < box2[4] or
                box1[4] > box2[5])

if __name__ == '__main__':
    Scene.run()

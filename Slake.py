import pygame
import random
import time
import json
import os

width_height = (800, 600)
width, height = width_height
grid_size = 20
tile_count = width // grid_size
base_delay = 120

# Slake Colors
bg_color = (13, 13, 13)
green = (57, 255, 20)
blue = (0, 207, 255)
red = (255, 68, 68)
gold = (255, 215, 0)
purple = (255, 0, 255)
white = (255, 255, 255)
dark_gray = (34, 34, 34)

class Slake:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(width_height)
        pygame.display.set_caption("Slake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.large_font = pygame.font.SysFont("Arial", 48)
        self.high_scores = self.load_scores()
        self.state = "MENU"
        self.running = True
        self.reset_game_state()

    def reset_game_state(self):
        self.snake = [{"x": 15, "y": 15}]
        self.dx, self.dy = 0, 0
        self.next_dx, self.next_dy = 0, 0
        self.score = 0
        self.game_over = False
        self.delay = base_delay
        self.start_time = time.time()
        self.inverted = False
        self.shrink_pending = 0
        self.effect_text = ""
        self.effect_timer = 0
        self.flash_timer = 0
        self.place_food()

    def load_scores(self):
        if os.path.exists("scores.json"):
            with open("scores.json", "r") as f:
                return sorted(json.load(f), key=lambda x: x["s"], reverse=True)[:7]
        return []

    def save_scores(self):
        with open("scores.json", "w") as f:
            json.dump(self.high_scores, f)

    def place_food(self):
        self.food = {
            "x": random.randint(0, tile_count - 1),
            "y": random.randint(0, tile_count - 1),
            "c": random.choice([red, (57, 255, 20), purple, blue, gold])
        }

    def trigger_chaos(self):
        effects = ["SPEED UP!!!","slow down!","!DETREVNI|INVERTED!","SRRink!","*PORT!|TELE*","COLOR CHAOS!","RESET!|RESET!|RESET!|..."]
        eff = random.choice(effects)
        self.effect_text = eff
        self.effect_timer = 25
        if "speed" in eff:   self.delay = max(40, self.delay - 25)
        elif "slow" in eff:  self.delay = min(220, self.delay + 40)
        elif "invert" in eff: self.inverted = not self.inverted
        elif "shrink" in eff: self.shrink_pending = min(3, len(self.snake) - 1)
        elif "reset" in eff: self.delay = base_delay
        elif "tele" in eff:
            self.snake[0]["x"] = random.randint(0, tile_count - 1)
            self.snake[0]["y"] = random.randint(0, tile_count - 1)
        elif "color" in eff: self.flash_timer = 30

    def format_time(self, seconds):
        m = int(seconds / 60)
        s = int(seconds % 60)
        return f"{m}m {s:02d}s"

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU":
                    if event.key == pygame.K_RETURN: self.state = "PLAYING"; self.reset_game_state()
                    if event.key == pygame.K_s: self.state = "SCORES"
                elif self.state == "PLAYING":
                    if event.key in [pygame.K_UP, pygame.K_w]:    self.next_dx, self.next_dy = (0, -1)
                    if event.key in [pygame.K_DOWN, pygame.K_s]:  self.next_dx, self.next_dy = (0, 1)
                    if event.key in [pygame.K_LEFT, pygame.K_a]:  self.next_dx, self.next_dy = (-1, 0)
                    if event.key in [pygame.K_RIGHT, pygame.K_d]: self.next_dx, self.next_dy = (1, 0)
                elif self.state == "SCORES":
                    if event.key == pygame.K_BACKSPACE: self.state = "MENU"

    def update(self):
        if self.state != "PLAYING": return
        pdx = -self.next_dx if self.inverted else self.next_dx
        pdy = -self.next_dy if self.inverted else self.next_dy

        if (pdx != 0 or pdy != 0):
            if len(self.snake) > 1:
                if self.snake[0]['x'] + pdx == self.snake[1]['x'] and self.snake[0]['y'] + pdy == self.snake[1]['y']:
                    (pdx, pdy) = (self.dx, self.dy)
            (self.dx, self.dy) = (pdx, pdy)
        if self.dx == 0 and self.dy == 0: return
        new_head = {"x": self.snake[0]["x"] + self.dx, "y": self.snake[0]["y"] + self.dy}
        if (new_head["x"] < 0 or new_head["x"] >= tile_count or
                new_head["y"] < 0 or new_head["y"] >= tile_count or
                any(s["x"] == new_head["x"] and s["y"] == new_head["y"] for s in self.snake)):
            self.die()
            return
        self.snake.insert(0, new_head)
        if new_head["x"] == self.food["x"] and new_head["y"] == self.food["y"]:
            self.score += 10
            self.place_food()
            self.trigger_chaos()
        else:
            self.snake.pop()
        if (self.shrink_pending > 0) and (len(self.snake) > 1):
            self.snake.pop()
            self.shrink_pending -= 1
        if self.effect_timer > 0: self.effect_timer -= 1
        if self.flash_timer > 0: self.flash_timer -= 1

    def die(self):
        elapsed = time.time() - self.start_time
        if self.score > 0 or elapsed > 2:
            self.high_scores.append({"s": self.score, "t": elapsed})
            self.high_scores = sorted(self.high_scores, key=lambda x: x["s"], reverse=True)[:7]
            self.save_scores()
        self.screen.fill(red)
        msg = self.font.render("Game Over ... :(", True, white)
        self.screen.blit(msg, (width // 2 - msg.get_width() // 2, height // 2 - 20))
        pygame.display.flip()
        time.sleep(1)
        self.reset_game_state()

    def draw(self):
        self.screen.fill(bg_color)
        if self.state == "MENU":
            title = self.large_font.render("SLAKE", True, green)
            start = self.font.render("Press ENTER to Start", True, white)
            score_btn = self.font.render("Press S for High Scores", True, blue)
            self.screen.blit(title, (width // 2 - title.get_width() // 2, 200))
            self.screen.blit(start, (width // 2 - start.get_width() // 2, 300))
            self.screen.blit(score_btn, (width // 2 - score_btn.get_width() // 2, 350))
        elif self.state == "SCORES":
            title = self.large_font.render(" TOP SCORES ", True, gold)
            self.screen.blit(title, (width // 2 - title.get_width() // 2, 50))
            for i, h in enumerate(self.high_scores):
                txt = self.font.render(f"{i+1}. {h['s']} points - {self.format_time(h['t'])}", True, white)
                self.screen.blit(txt, (width // 2 - txt.get_width() // 2, 120 + 40 * i))
            back = self.font.render("Press BACKSPACE to return to the menu", True, dark_gray)
            self.screen.blit(back, (width // 2 - back.get_width() // 2, height - 50))
        elif self.state == "PLAYING":
            pygame.draw.circle(self.screen, self.food["c"], (self.food["x"] * grid_size + 10, self.food["y"] * grid_size + 10), 8)
            for i, s in enumerate(self.snake):
                color = green if i == 0 else (44, 179, 15)
                if self.flash_timer > 0: color = random.choice([blue, gold, purple])
                elif self.inverted: color = purple if i == 0 else (170, 0, 170)
                rect = (s["x"] * grid_size + 1, s["y"] * grid_size + 1, grid_size - 2, grid_size - 2)
                pygame.draw.rect(self.screen, color, rect)
            s_txt = self.font.render(f"Score: {self.score}", True, white)
            t_txt = self.font.render(f"Time: {self.format_time(time.time() - self.start_time)}", True, white)
            self.screen.blit(s_txt, (20, 20))
            self.screen.blit(t_txt, (width - t_txt.get_width() - 20, 20))
            if self.effect_timer > 0:
                e_txt = self.font.render(self.effect_text, True, gold)
                self.screen.blit(e_txt, (width // 2 - e_txt.get_width() // 2, height - 50))
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(1000 // self.delay if self.state == "PLAYING" else 60)
        pygame.quit()

if __name__ == "__main__":
    game = Slake()
    game.run()
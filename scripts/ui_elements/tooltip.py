import pygame

# use font_enhanced.formatted_text_gen if you want colors


class Tooltip:

    """
    Tooltips will pop up after <rect_reference> has been hovered for <visible_delay> seconds and will show <text>.
    They are bound by the display size and will adjust their placement automatically.
    <rect_reference> should be a reference to a Rect that should be used to trigger the tooltip (likely the Rect
    attribute of another UIElement).

    Please note that Rects can be resized and moved without creating a new instance. This will be necessary when
    binding to moving elements.
    In the event that an element is in world space rather than an absolute space, the element should have an
    alternative rect attribute that gets updated to the absolute rect position.
    """

    def __init__(self, game, text, font_id, rect_reference, width=200, padding=2, margin=2, alpha=100, visible_delay=1):
        self.game = game
        self.text = text
        self.font_id = font_id
        self.rect_reference = rect_reference
        self.width = width
        self.padding = padding
        self.margin = margin
        self.alpha = 100
        self.cursor_height = 10
        self.rect_hover_timer = 0
        self.visible_delay = visible_delay
        self.generate_text_surf()

    def change_text(self, text):
        self.text = text
        self.generate_text_surf()

    def generate_text_surf(self):
        text_block = TextBlock(
            self.text, self.game.assets.enhanced_fonts[self.font_id], max_width=self.width - self.padding * 2
        )
        self.text_surf = pygame.Surface(
            (text_block.used_width + self.padding * 2, text_block.height + self.padding * 2)
        )
        self.text_surf.fill((0, 0, 2))
        self.text_surf.set_colorkey((0, 0, 2))
        text_block.render(self.text_surf, (self.padding, self.padding))

    def update(self, delta_time):
        mouse_pos = self.game.input.mouse_pos
        if self.rect_reference.collidepoint(mouse_pos):
            self.rect_hover_timer += delta_time
        else:
            self.rect_hover_timer = 0

    def render(self, surf):
        if self.rect_hover_timer >= self.visible_delay:
            mouse_pos = self.game.input.mouse_pos
            display_size = self.game.window.base_resolution

            # prioritize placing the tooltip centered above the mouse
            base_pos = [
                mouse_pos[0] - self.text_surf.get_width() // 2,
                mouse_pos[1] - self.text_surf.get_height() - self.margin,
            ]

            # correct position on X axis if showing off of the screen
            base_pos[0] = max(base_pos[0], self.margin)
            base_pos[0] = min(base_pos[0], display_size[0] - self.text_surf.get_width() - self.margin)

            # show tooltip below mouse if it's clipping above the display
            if base_pos[1] < self.margin:
                base_pos[1] = mouse_pos[1] + self.margin + self.cursor_height

            # just render an image instead if you don't want a rectangle background
            bg_surf = pygame.Surface(self.text_surf.get_size())
            bg_surf.set_alpha(self.alpha)

            surf.blit(bg_surf, base_pos)
            surf.blit(self.text_surf, base_pos)

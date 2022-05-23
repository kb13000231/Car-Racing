import pygame


def scale_img(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rot_center(win, image, top_left, angle):
    rot_image = pygame.transform.rotate(image, angle)
    new_rect = rot_image.get_rect(
        center=image.get_rect(topleft=top_left).center
        )
    win.blit(rot_image, new_rect.topleft)


def blit_text_center(win, font, text):
    render = font.render(text, 1, (200, 200, 200))
    win.blit(render, (win.get_width()/2 - render.get_width()/2,
                      win.get_height()/2 - render.get_height()/2))

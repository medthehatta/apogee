from io import BytesIO

import pyglet


def pil_to_sprite_at_rect(pil, rect, batch=None):
    pil_file = BytesIO()
    pil.save(pil_file, "png")
    sprite = pyglet.sprite.Sprite(
        pyglet.image.load(
            "hint.png",
            file=pil_file,
            decoder=pyglet.image.codecs.pil.PILImageDecoder(),
        ),
        batch=batch,
    )
    sprite.update(
        x=rect.bottomleft.x,
        y=rect.bottomleft.y,
        scale_x=rect.width/sprite.width,
        scale_y=rect.height/sprite.height,
    )
    return sprite

from formal_vector import FormalVector


class Point(FormalVector):
    _ZERO = "Point.new(0, 0)"

    @classmethod
    def new(cls, x, y):
        return x*cls.named("x") + y*cls.named("y")

    @property
    def x(self):
        return self["x"]

    @property
    def y(self):
        return self["y"]

    def as_tuple(self):
        return (self["x"], self["y"])

    def integral(self):
        return self.from_triples([
            (name, int(value), basis)
            for (name, value, basis) in self.triples()
        ])

    def __repr__(self):
        return f"{self.__class__.__name__}.new({self['x']}, {self['y']})"


e_lr = Point.named("x")
e_tb = Point.named("y")
e_rl = -e_lr
e_bt = -e_tb


def _ensure_point(x):
    if not isinstance(x, Point):
        return Point.new(*x)
    else:
        return x


class Rect:

    @classmethod
    def ensure_point(cls, pt):
        return _ensure_point(pt)

    @classmethod
    def from_topleft_width_height(cls, topleft, width, height):
        return cls(cls.ensure_point(topleft), width, height)

    @classmethod
    def tlwh(cls, topleft, width, height):
        return cls.from_topleft_width_height(topleft, width, height)

    @classmethod
    def from_topright_width_height(cls, topright, width, height):
        return cls.from_topleft_width_height(
            cls.ensure_point(topright) - width * cls.e_right,
            width,
            height,
        )

    @classmethod
    def trwh(cls, topright, width, height):
        return cls.from_topright_width_height(topright, width, height)

    @classmethod
    def from_bottomleft_width_height(cls, bottomleft, width, height):
        return cls.from_topleft_width_height(
            cls.ensure_point(bottomleft) - height * cls.e_up,
            width,
            height,
        )

    @classmethod
    def blwh(cls, bottomleft, width, height):
        return cls.from_bottomleft_width_height(bottomleft, width, height)

    @classmethod
    def from_bottomright_width_height(cls, bottomright, width, height):
        return cls.from_topleft_width_height(
            cls.ensure_point(bottomright) - height * cls.e_up - width * cls.e_right,
            width,
            height,
        )

    @classmethod
    def brwh(cls, bottomright, width, height):
        return cls.from_bottomright_width_height(bottomright, width, height)

    @classmethod
    def from_center_width_height(cls, center, width, height):
        _topleft = cls.ensure_point(center) - width/2 * cls.e_right - height/2 * cls.e_up
        return cls.from_topleft_width_height(
            _topleft.integral(),
            width,
            height,
        )

    @classmethod
    def cwh(cls, center, width, height):
        return cls.from_center_width_height(center, width, height)

    @classmethod
    def from_topleft_bottomright(cls, topleft, bottomright):
        _topleft = cls.ensure_point(topleft)
        _bottomright = cls.ensure_point(bottomright)
        diag = _bottomright - _topleft
        width = diag.x
        height = diag.y
        return cls.from_topleft_width_height(
            _topleft,
            width,
            height,
        )

    @classmethod
    def tlbr(cls, topleft, bottomright):
        return cls.from_topleft_bottomright(topleft, bottomright)

    @classmethod
    def from_left_right_top_bottom(cls, left, right, top, bottom):
        topleft = cls.ensure_point((left, top))
        bottomright = cls.ensure_point((right, bottom))
        return cls.from_topleft_bottomright(topleft, bottomright)

    @classmethod
    def lrtb(cls, left, right, top, bottom):
        return cls.from_left_right_top_bottom(left, right, top, bottom)

    def __init__(self, topleft, width, height):
        self._topleft = self.ensure_point(topleft)
        self._width = width
        self._height = height

    @property
    def topleft(self):
        return self._topleft

    @property
    def tl(self):
        return self.topleft

    @property
    def topright(self):
        return self.topleft + self.width * self.e_right

    @property
    def tr(self):
        return self.topright

    @property
    def bottomleft(self):
        return self.topleft + self.height * self.e_up

    @property
    def bl(self):
        return self.bottomleft

    @property
    def bottomright(self):
        return self.topleft + self.height * self.e_up + self.width * self.e_right

    @property
    def br(self):
        return self.bottomright

    @property
    def width(self):
        return self._width

    @property
    def w(self):
        return self.width

    @property
    def height(self):
        return self._height

    @property
    def h(self):
        return self.height

    @property
    def center(self):
        actual_center = (
            self.topleft + 0.5 * (self.bottomright - self.topleft)
        )
        return actual_center.integral()

    @property
    def c(self):
        return self.center

    @property
    def left_right_top_bottom(self):
        return (
            self.topleft.x,
            self.topright.x,
            self.topleft.y,
            self.bottomleft.y,
        )

    def as_lrtb(self):
        return self.left_right_top_bottom

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f".tlwh({self.topleft}, {self.w}, {self.h})"
        )

    # Transformations

    def center_align(self, r2):
        return type(self).cwh(
            r2.center,
            self.width,
            self.height,
        )

    def topleft_align(self, r2):
        return type(self).tlwh(
            r2.topleft,
            self.width,
            self.height,
        )

    def topright_align(self, r2):
        return type(self).trwh(
            r2.topright,
            self.width,
            self.height,
        )

    def bottomleft_align(self, r2):
        return type(self).blwh(
            r2.bottomleft,
            self.width,
            self.height,
        )

    def bottomright_align(self, r2):
        return type(self).brwh(
            r2.bottomright,
            self.width,
            self.height,
        )

    def topleft_quadrant(self):
        return type(self).tlwh(
            self.topleft,
            self.w//2,
            self.h//2,
        )

    def topright_quadrant(self):
        return type(self).trwh(
            self.topright,
            self.w//2,
            self.h//2,
        )

    def bottomleft_quadrant(self):
        return type(self).blwh(
            self.bottomleft,
            self.w//2,
            self.h//2,
        )

    def bottomright_quadrant(self):
        return type(self).brwh(
            self.bottomright,
            self.w//2,
            self.h//2,
        )

    def displace(self, delta):
        d = self.ensure_point(delta)
        return type(self).tlwh(
            self.tl + d,
            self.w,
            self.h,
        )

    def in_grid(self, row, col, xpad=0, ypad=0):
        return type(self).tlwh(
            (
                self.topleft
                + col * (self.width + xpad) * self.e_right
                + row * (self.height + ypad) * self.e_up
            ),
            self.width,
            self.height,
        )

    def scale_width_centered_pct(self, pct):
        return type(self).cwh(
            self.c,
            self.w * pct//100,
            self.h,
        )

    def scale_height_centered_pct(self, pct):
        return type(self).cwh(
            self.c,
            self.w,
            self.h * pct//100,
        )

    def scale_centered_pct(self, pct):
        return type(self).cwh(
            self.c,
            self.w * pct//100,
            self.h * pct//100,
        )


class RectLRTB(Rect):

    e_right = Point.named("x")
    e_up = -Point.named("y")


class RectLRBT(Rect):

    e_right = Point.named("x")
    e_up = Point.named("y")

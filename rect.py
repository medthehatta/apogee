from formal_vector import FormalVector


class Point(FormalVector):
    _ZERO = "Point.new(0, 0)"

    @classmethod
    def from_pair(cls, pair):
        (x, y) = pair
        return cls.new(x, y)

    @classmethod
    def new(cls, x, y):
        return x*cls.named("x") + y*cls.named("y")

    @property
    def x(self):
        return self["x"]

    @property
    def y(self):
        return self["y"]

    def integral(self):
        return self.from_triples([
            (name, int(value), basis)
            for (name, value, basis) in self.triples()
        ])

    def __repr__(self):
        return f"{self.__class__.__name__}.new({self['x']}, {self['y']})"


xhat = Point.named("x")
yhat = Point.named("y")


def _ensure_point(x):
    if not isinstance(x, Point):
        return Point.from_pair(x)
    else:
        return x


class Rect:

    @classmethod
    def from_topleft_width_height(cls, topleft, width, height):
        return cls(_ensure_point(topleft), width, height)

    @classmethod
    def tlwh(cls, topleft, width, height):
        return cls.from_topleft_width_height(topleft, width, height)

    @classmethod
    def from_topright_width_height(cls, topright, width, height):
        return cls.from_topleft_width_height(
            _ensure_point(topright) - width * xhat,
            width,
            height,
        )

    @classmethod
    def trwh(cls, topright, width, height):
        return cls.from_topright_width_height(topright, width, height)

    @classmethod
    def from_bottomleft_width_height(cls, bottomleft, width, height):
        return cls.from_topleft_width_height(
            _ensure_point(bottomleft) - height * yhat,
            width,
            height,
        )

    @classmethod
    def blwh(cls, bottomleft, width, height):
        return cls.from_bottomleft_width_height(bottomleft, width, height)

    @classmethod
    def from_bottomright_width_height(cls, bottomright, width, height):
        return cls.from_topleft_width_height(
            _ensure_point(bottomright) - height * yhat - width * xhat,
            width,
            height,
        )

    @classmethod
    def brwh(cls, bottomright, width, height):
        return cls.from_bottomright_width_height(bottomright, width, height)

    @classmethod
    def from_center_width_height(cls, center, width, height):
        _topleft = _ensure_point(center) - width/2 * xhat - height/2 * yhat
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
        _topleft = _ensure_point(topleft)
        _bottomright = _ensure_point(bottomright)
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

    def __init__(self, topleft, width, height):
        self._topleft = _ensure_point(topleft)
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
        return self.topleft + self.width * xhat

    @property
    def tr(self):
        return self.topright

    @property
    def bottomleft(self):
        return self.topleft + self.height * yhat

    @property
    def bl(self):
        return self.bottomleft

    @property
    def bottomright(self):
        return self.topleft + self.height * yhat + self.width * xhat

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

    def __repr__(self):
        return f"Rect.tlwh({self.topleft}, {self.w}, {self.h})"

    # Transformations

    def center_align(self, r2):
        return Rect.cwh(
            r2.center,
            self.width,
            self.height,
        )

    def topleft_align(self, r2):
        return Rect.tlwh(
            r2.topleft,
            self.width,
            self.height,
        )

    def topright_align(self, r2):
        return Rect.trwh(
            r2.topright,
            self.width,
            self.height,
        )

    def bottomleft_align(self, r2):
        return Rect.blwh(
            r2.bottomleft,
            self.width,
            self.height,
        )

    def bottomright_align(self, r2):
        return Rect.brwh(
            r2.bottomright,
            self.width,
            self.height,
        )

    def topleft_quadrant(self):
        return Rect.tlwh(
            self.topleft,
            self.w//2,
            self.h//2,
        )

    def topright_quadrant(self):
        return Rect.trwh(
            self.topright,
            self.w//2,
            self.h//2,
        )

    def bottomleft_quadrant(self):
        return Rect.blwh(
            self.bottomleft,
            self.w//2,
            self.h//2,
        )

    def bottomright_quadrant(self):
        return Rect.brwh(
            self.bottomright,
            self.w//2,
            self.h//2,
        )

    def displace(self, delta):
        d = _ensure_point(delta)
        return Rect.tlwh(
            self.tl + d,
            self.w,
            self.h,
        )

    def scale_width_centered_pct(self, pct):
        return Rect.cwh(
            self.c,
            self.w * pct//100,
            self.h,
        )

    def scale_height_centered_pct(self, pct):
        return Rect.cwh(
            self.c,
            self.w,
            self.h * pct//100,
        )

    def scale_centered_pct(self, pct):
        return Rect.cwh(
            self.c,
            self.w * pct//100,
            self.h * pct//100,
        )


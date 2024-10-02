from itertools import chain

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


class Size(FormalVector):
    _ZERO = "Size.new(0, 0)"

    @classmethod
    def new(cls, w, h):
        return w*cls.named("w") + h*cls.named("h")

    @property
    def w(self):
        return self["w"]

    @property
    def h(self):
        return self["h"]

    def as_tuple(self):
        return (self["w"], self["h"])

    def integral(self):
        return self.from_triples([
            (name, int(value), basis)
            for (name, value, basis) in self.triples()
        ])

    def __repr__(self):
        return f"{self.__class__.__name__}.new({self['w']}, {self['h']})"


class RectCoord(FormalVector):
    _ZERO = "RectCoord.new(0, 0)"

    @classmethod
    def new(cls, u, v):
        return u*cls.named("u") + v*cls.named("v")

    @property
    def u(self):
        return self["u"]

    @property
    def v(self):
        return self["v"]

    def as_tuple(self):
        return (self["u"], self["v"])

    def integral(self):
        return self.from_triples([
            (name, int(value), basis)
            for (name, value, basis) in self.triples()
        ])

    def __repr__(self):
        return f"{self.__class__.__name__}.new({self['u']}, {self['v']})"


e_lr = Point.named("x")
e_tb = Point.named("y")
e_rl = -e_lr
e_bt = -e_tb


def _ensure_point(x):
    if not isinstance(x, Point):
        return Point.new(*x)
    else:
        return x


class RectSubdivisions:

    def __init__(self, rect, rows, columns):
        self.rect = rect
        self.rows = rows
        self.columns = columns

        self.cell_width = self.rect.width / columns
        self.cell_height = self.rect.height / rows

    def cell(self, row, column):
        if row >= self.rows or column >= self.columns:
            raise ValueError(
                f"Subdivision ({row=}, {column=}) is out of bounds "
                f"(0, 0) to (row={self.rows-1}, column={self.columns-1})"
            )

        return type(self.rect).blwh(
            (
                self.rect.bottomleft
                + column * self.cell_width * self.rect.e_right
                + row * self.cell_height * self.rect.e_up
            ),
            self.cell_width,
            self.cell_height,
        )

    def row(self, row):
        return [
            self.cell(row, c) for c in range(self.columns)
        ]

    def column(self, column):
        return [
            self.cell(r, column) for r in range(self.rows)
        ]

    def as_iter_rows_columns(self):
        return chain.from_iterable(self.column(c) for c in range(self.columns))

    def as_iter_columns_rows(self):
        return chain.from_iterable(self.row(r) for r in range(self.rows))

    def as_nested_rows_columns(self):
        return [self.column(c) for c in range(self.columns)]

    def as_nested_columns_rows(self):
        return [self.row(r) for r in range(self.rows)]


class RectTiled:

    def __init__(self, rect, rows=None, columns=None, xpad=0, ypad=0):
        self.rect = rect
        self.rows = rows
        self.columns = columns
        self.xpad = xpad
        self.ypad = ypad

    def cell(self, row, column):
        if (
            (self.rows is not None and row >= self.rows) or
            (self.columns is not None and column >= self.columns)
        ):
            raise ValueError(
                f"Subdivision ({row=}, {column=}) is out of bounds "
                f"(0, 0) to (row={self.rows}, column={self.columns}) "
                f"(not inclusive of the endpoint)"
            )

        return type(self.rect).blwh(
            (
                self.rect.bottomleft
                + column * (self.rect.width + self.xpad) * self.rect.e_right
                + row * (self.rect.height + self.ypad) * self.rect.e_up
            ),
            self.rect.width,
            self.rect.width,
        )

    def check_finite(self):
        if self.rows is None or self.columns is None:
            raise ValueError(
                f"Cannot iterate through a tiling if the number of rows or "
                f"columns has been left indeterminate.  Instantiate with "
                f"`rows` and `columns` to enable iteration.  This instance "
                f"has (rows={self.rows}, columns={self.columns})"
            )

    def row(self, row):
        if self.columns is None:
            raise ValueError(
                "Cannot iterate through a row if the tiling doesn't specify a "
                "number of columns"
            )
        return [
            self.cell(row, c) for c in range(self.columns)
        ]

    def column(self, column):
        if self.rows is None:
            raise ValueError(
                "Cannot iterate through a row if the tiling doesn't specify a "
                "number of rows"
            )
        return [
            self.cell(r, column) for r in range(self.rows)
        ]

    def as_iter_columns_rows(self):
        self.check_finite()
        return chain.from_iterable(self.column(c) for c in range(self.columns))

    def as_iter_rows_columns(self):
        self.check_finite()
        return chain.from_iterable(self.row(r) for r in range(self.rows))

    def as_nested_rows_columns(self):
        self.check_finite()
        return [self.column(c) for c in range(self.columns)]

    def as_nested_columns_rows(self):
        self.check_finite()
        return [self.row(r) for r in range(self.rows)]


class Rect:

    @classmethod
    def ensure_point(cls, pt):
        return _ensure_point(pt)

    @classmethod
    def from_topleft_width_height(cls, topleft, width, height):
        return cls(topleft, width, height)

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
            cls.ensure_point(bottomleft) + height * cls.e_up,
            width,
            height,
        )

    @classmethod
    def blwh(cls, bottomleft, width, height):
        return cls.from_bottomleft_width_height(bottomleft, width, height)

    @classmethod
    def from_bottomright_width_height(cls, bottomright, width, height):
        return cls.from_topleft_width_height(
            cls.ensure_point(bottomright) + height * cls.e_up - width * cls.e_right,
            width,
            height,
        )

    @classmethod
    def brwh(cls, bottomright, width, height):
        return cls.from_bottomright_width_height(bottomright, width, height)

    @classmethod
    def from_center_width_height(cls, center, width, height):
        _topleft = cls.ensure_point(center) - width/2 * cls.e_right + height/2 * cls.e_up
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
        width = abs(diag.x)
        height = abs(diag.y)
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

    @classmethod
    def aabb(cls, rects):
        raise NotImplementedError()

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
        return self.topleft - self.height * self.e_up

    @property
    def bl(self):
        return self.bottomleft

    @property
    def bottomright(self):
        return self.bottomleft + self.width * self.e_right

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

    def subdivisions(self, rows, columns):
        return RectSubdivisions(self, rows, columns)

    def tiled(self, rows=None, columns=None, xpad=0, ypad=0):
        return RectTiled(
            self,
            rows=rows,
            columns=columns,
            xpad=xpad,
            ypad=ypad,
        )

    def displace(self, delta):
        d = self.ensure_point(delta)
        return type(self).tlwh(
            self.tl + d,
            self.w,
            self.h,
        )

    def scale_width_centered_pct(self, pct):
        return type(self).cwh(
            self.c,
            self.w * pct//100,
            self.h,
        )

    def scale_width_to_left_pct(self, pct):
        return type(self).tlwh(
            self.topleft,
            self.w * pct//100,
            self.h,
        )

    def scale_width_to_right_pct(self, pct):
        return type(self).trwh(
            self.topright,
            self.w * pct//100,
            self.h,
        )

    def scale_height_centered_pct(self, pct):
        return type(self).cwh(
            self.c,
            self.w,
            self.h * pct//100,
        )

    def scale_height_to_top_pct(self, pct):
        return type(self).tlwh(
            self.topleft,
            self.w,
            self.h * pct//100,
        )

    def scale_height_to_bottom_pct(self, pct):
        return type(self).blwh(
            self.bottomleft,
            self.w,
            self.h * pct//100,
        )

    def scale_centered_pct(self, pct):
        return type(self).cwh(
            self.c,
            self.w * pct//100,
            self.h * pct//100,
        )

    def scale_to_topleft_pct(self, pct):
        return type(self).from_topleft_width_height(
            self.topleft,
            self.w * pct//100,
            self.h * pct//100,
        )

    def scale_to_topright_pct(self, pct):
        return type(self).from_topright_width_height(
            self.topright,
            self.w * pct//100,
            self.h * pct//100,
        )

    def scale_to_bottomleft_pct(self, pct):
        return type(self).from_bottomleft_width_height(
            self.bottomleft,
            self.w * pct//100,
            self.h * pct//100,
        )

    def scale_to_bottomright_pct(self, pct):
        return type(self).from_bottomright_width_height(
            self.bottomright,
            self.w * pct//100,
            self.h * pct//100,
        )

    def at_center_with_width_height(self, width, height):
        return type(self).from_center_width_height(
            self.center,
            width,
            height,
        )

    def at_topleft_with_width_height(self, width, height):
        return type(self).from_topleft_width_height(
            self.topleft,
            width,
            height,
        )

    def at_topright_with_width_height(self, width, height):
        return type(self).from_topright_width_height(
            self.topright,
            width,
            height,
        )

    def at_bottomleft_with_width_height(self, width, height):
        return type(self).from_bottomleft_width_height(
            self.bottomleft,
            width,
            height,
        )

    def at_bottomright_with_width_height(self, width, height):
        return type(self).from_bottomright_width_height(
            self.bottomright,
            width,
            height,
        )

    def contains_point(self, pt):
        raise NotImplementedError()


class RectLRTB(Rect):

    e_right = Point.named("x")
    e_up = -Point.named("y")

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f".tlwh({self.topleft}, {self.w}, {self.h})"
        )

    def contains_point(self, pt):
        pt = self.ensure_point(pt)
        return (
            self.topleft.x < pt.x < self.topright.x and
            self.topleft.y < pt.y < self.bottomleft.y
        )

    @classmethod
    def aabb(cls, rects):
        rects = list(rects)
        xmin = min(r.topleft.x for r in rects)
        xmax = max(r.topright.x for r in rects)
        ymin = min(r.topleft.y for r in rects)
        ymax = max(r.bottomleft.y for r in rects)
        return cls.lrtb(xmin, xmax, ymin, ymax)


class RectLRBT(Rect):

    e_right = Point.named("x")
    e_up = Point.named("y")

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f".blwh({self.bottomleft}, {self.w}, {self.h})"
        )

    def contains_point(self, pt):
        pt = self.ensure_point(pt)
        return (
            self.topleft.x < pt.x < self.topright.x and
            self.bottomleft.y < pt.y < self.topleft.y
        )

    @classmethod
    def aabb(cls, rects):
        rects = list(rects)
        xmin = min(r.topleft.x for r in rects)
        xmax = max(r.topright.x for r in rects)
        ymin = min(r.bottomleft.y for r in rects)
        ymax = max(r.topleft.y for r in rects)
        return cls.lrtb(xmin, xmax, ymax, ymin)


class Frame:

    def __init__(self, right, up):
        self._right = right
        self._up = up
        self._right_norm = None
        self._up_norm = None
        self._anchors = None

    @property
    def zero(self):
        return self._right.zero()

    @property
    def right(self):
        if self._right_norm is None:
            self._right_norm = self._right.normalized()
        return self._right_norm

    @property
    def left(self):
        return -self.right

    @property
    def up(self):
        if self._up_norm is None:
            self._up_norm = self._up.normalized()
        return self._up_norm

    @property
    def down(self):
        return -self.up

    @property
    def anchors(self):
        if self._anchors is None:
            self._anchors = Anchors(self)
        return self._anchors


class AnchorPoint:

    def __init__(self, name, frame, from_bottom_left):
        self.name = name
        self.frame = frame
        self.from_bottom_left = from_bottom_left
        self.to_bottom_left = -from_bottom_left


class Anchors:

    def __init__(self, frame):
        self.frame = frame
        self._by_name = {
            "top_left": self.top_left,
            "top_right": self.top_right,
            "bottom_left": self.bottom_left,
            "bottom_right": self.bottom_right,
            "center": self.center,
        }

    def __getitem__(self, key):
        return self.from_name(key)

    def from_name(self, anchor_name):
        return self._by_name[anchor_name]

    @property
    def top_left(self):
        return AnchorPoint(
            "top_left",
            frame=self.frame,
            from_bottom_left=self.frame.up,
        )

    @property
    def top_right(self):
        return AnchorPoint(
            "top_right",
            frame=self.frame,
            from_bottom_left=self.frame.up + self.frame.right,
        )

    @property
    def bottom_left(self):
        return AnchorPoint(
            "bottom_left",
            frame=self.frame,
            from_bottom_left=self.frame.zero,
        )

    @property
    def bottom_right(self):
        return AnchorPoint(
            "bottom_right",
            frame=self.frame,
            from_bottom_left=self.frame.right,
        )

    @property
    def center(self):
        return AnchorPoint(
            "center",
            frame=self.frame,
            from_bottomleft=0.5*self.top_right,
        )


class AnchorRect:

    @classmethod
    def from_anchor_point_size(cls, anchor, point, size):
        bottomleft = point + Point.componentwise(
            lambda x, y: x*y,
            anchor.to_bottomleft,
            size,
        )
        return cls(anchor.frame, bottomleft, size)

    @classmethod
    def from_bottomleft_topright(cls, bottom_left, top_right):
        diagonal = top_right - bottom_left
        frame = Frame(
            right=diagonal.project("x"),
            up=diagonal.project("y"),
        )
        size = Size.new(
            w=abs(diagonal.x),
            h=abs(diagonal.y),
        )
        return cls.from_anchor_point_size(
            frame.anchors.bottom_left,
            bottom_left,
            size,
        )

    @classmethod
    def from_left_right_top_bottom(cls, left, right, top, bottom):
        return cls.from_bottomleft_topright(
            Point.new(left, bottom),
            Point.new(right, top),
        )

    def __init__(self, frame, bottomleft, size):
        self.frame = frame
        self._bottomleft = bottomleft
        self.size = size

    @property
    def anchors(self):
        return self.frame.anchors

    @property
    def width(self):
        return self.size.w

    @property
    def height(self):
        return self.size.h

    def _uv(self, uv):
        return (
            uv.u * self.width * self.frame.right +
            uv.v * self.height * self.frame.up
        )

    def at(self, anchor):
        assert self.frame == anchor.frame
        return self._bottomleft + self._uv(anchor.from_bottomleft)

    def left_right_top_bottom(self):
        return (
            self.at(self.anchors.top_left).x,
            self.at(self.anchors.top_right).x,
            self.at(self.anchors.top_left).y,
            self.at(self.anchors.bottom_right).y,
        )

    # Convenience methods

    def __getitem__(self, anchor_name):
        return self.at(self.anchors[anchor_name])

    @property
    def w(self):
        return self.width

    @property
    def h(self):
        return self.height


class AnchorRectTransforms:

    @classmethod
    def scale_around_anchor(cls, anchor, percent):

        def _(rect):
            return AnchorRect.from_anchor_point_size(
                anchor,
                rect.at(anchor),
                rect.size * percent//100,
            )

        return _

    @classmethod
    def subdivisions(cls, rows, columns):

        def _(rect):
            return RectSubdivisions(rect, rows, columns)

        return _

    @classmethod
    def tiled(cls, rows=None, columns=None, xpad=0, ypad=0):

        def _(rect):
            return RectTiled(
                rect,
                rows=rows,
                columns=columns,
                xpad=xpad,
                ypad=ypad,
            )

        return _

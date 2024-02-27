"""OpenGL matrices."""

import numpy as np


def translate(tx: float, ty: float, tz: float, dtype=None) -> np.ndarray:
    """Return a 4x4 translation matrix."""

    if dtype is None:
        dtype = np.float64

    return np.array([
        [ 1, 0, 0, tx],
        [ 0, 1, 0, ty],
        [ 0, 0, 1, tz],
        [ 0, 0, 0,  1]
    ], dtype=dtype)


def scale_xyz(sx: float, sy: float, sz: float, dtype=None):
    """Return a 4x4 matrix for general scaling."""

    if dtype is None:
        dtype = np.float64

    return np.array([
        [ sx,  0,  0,  0],
        [  0, sy,  0,  0],
        [  0,  0, sz,  0],
        [  0,  0,  0,  1]
    ], dtype=dtype)


def scale(s: float, dtype=None):
    """Return a 4x4 matrix for uniform scaling."""
    return scale_xyz(s, s, s, dtype)


def rotate(rx: float, ry: float, rz: float, angle: float, dtype=None):
    """Return a rotation matrix."""

    if dtype is None:
        dtype = np.float64

    length = np.sqrt(rx * rx + ry * ry + rz * rz)
    if length == 0.0:
        raise ValueError()

    nx = rx / length
    ny = ry / length
    nz = rz / length

    ca = np.cos(angle)
    sa = np.sin(angle)

    cca = 1 - ca

    return np.array([
        [ cca * nx * nx +      ca , cca * ny * nx - nz * sa , cca * nz * nx + ny * sa , 0 ],
        [ cca * nx * ny + nz * sa , cca * ny * ny +      ca , cca * nz * ny - nx * sa , 0 ],
        [ cca * nx * nz - ny * sa , cca * ny * nz + nx * sa , cca * nz * nz +      ca , 0 ],
        [          0              ,          0              ,          0              , 1 ]
    ], dtype=dtype)


def frustum(left: float, right: float, bottom: float, top: float, near: float, far: float, dtype=None):
    """Return a frustum projection matrix."""
    return np.array([
        [ 2.0 * near / (right - left) ,            0                , (right + left) / (right - left) ,                 0               ],
        [            0                , 2.0 * near / (top - bottom) , (top + bottom) / (top - bottom) ,                 0               ],
        [            0                ,            0                , (far + near)   / (near - far)   , 2.0 * far * near / (near - far) ],
        [            0                ,            0                ,               -1                ,                 0               ]
    ], dtype=dtype)


def projection(framebuffer_width: int, framebuffer_height: int, fov_degrees: float, near: float, far: float, dtype=None):

    fov_radians = np.radians(fov_degrees)

    if framebuffer_width >= framebuffer_height:
        frustum_height = 2.0 * near * np.tan(0.5 * fov_radians)
        frustum_width = frustum_height * framebuffer_width / framebuffer_height
    else:
        frustum_width = 2.0 * near * np.tan(0.5 * fov_radians)
        frustum_height = frustum_width * framebuffer_height / framebuffer_width

    return frustum(
        -0.5 * frustum_width, +0.5 * frustum_width,
        -0.5 * frustum_height, +0.5 * frustum_height,
        near, far, dtype=dtype)


def apply_transform_to_vertices(m_xform, vertices):

    if m_xform is None:
        return vertices

    ok = m_xform.shape == (4, 4) and (vertices.ndim == 2) and (vertices.shape[1] == 3)
    if not ok:
        raise ValueError("Bad transform requested.")

    n = len(vertices)

    all_ones_column = np.ones((n, 1), dtype=vertices.dtype)

    vertices = np.hstack((vertices, all_ones_column))
    vertices = (m_xform @ vertices.T).T
    vertices = vertices[:, :-1]

    return vertices

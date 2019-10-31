import numpy as np
from collections import namedtuple
import time
import logging
from .mc import marching_cubes

IsosurfaceMesh = namedtuple("IsosurfaceMesh", "vertices faces normals vertex_prop")
LOG = logging.getLogger(__name__)


def promolecule_density_isosurface(promol, isovalue=0.002, sep=0.2, props=True):

    t1 = time.time()
    l, u = promol.bb()
    x_grid = np.arange(l[0], u[0], sep, dtype=np.float32)
    y_grid = np.arange(l[1], u[1], sep, dtype=np.float32)
    z_grid = np.arange(l[2], u[2], sep, dtype=np.float32)
    x, y, z = np.meshgrid(x_grid, y_grid, z_grid)
    separations = np.array((sep, sep, sep))
    shape = x.shape
    pts = np.c_[x.ravel(), y.ravel(), z.ravel()]
    d = promol.rho(pts).reshape(shape)
    verts, faces, normals, _ = marching_cubes(
        d, isovalue, spacing=(sep, sep, sep), gradient_direction="descent"
    )
    LOG.debug("Separation (x,y,z): %s", separations)
    verts = np.c_[verts[:, 1], verts[:, 0], verts[:, 2]] + l
    LOG.debug("Surface centroid: %s", np.mean(verts, axis=0))
    LOG.debug("Mol centroid: %s", np.mean(promol.positions, axis=0))
    LOG.debug("Max (x,y,z): %s", np.max(verts, axis=0))
    LOG.debug("Min (x,y,z): %s", np.min(verts, axis=0))
    vertex_props = {}
    if props:
        d_i, d_norm_i = promol.d_norm(verts)
        vertex_props["d_i"] = d_i
        vertex_props["d_norm_i"] = d_norm_i
        LOG.debug("d_i (min, max): (%.2f, %.2f)", np.min(d_i), np.max(d_i))
    t2 = time.time()
    LOG.info("promolecule surface took %.3fs, %d pts", t2 - t1, len(pts))
    return IsosurfaceMesh(verts, faces, normals, vertex_props)


def stockholder_weight_isosurface(s, isovalue=0.5, sep=0.2, props=True):

    t1 = time.time()
    l, u = s.bb()
    x_grid = np.arange(l[0], u[0], sep, dtype=np.float32)
    y_grid = np.arange(l[1], u[1], sep, dtype=np.float32)
    z_grid = np.arange(l[2], u[2], sep, dtype=np.float32)
    x, y, z = np.meshgrid(x_grid, y_grid, z_grid)
    separations = np.array((sep, sep, sep))
    shape = x.shape
    pts = np.c_[x.ravel(), y.ravel(), z.ravel()]
    pts = np.array(pts, dtype=np.float32)
    weights = s.weights(pts).reshape(shape)
    verts, faces, normals, _ = marching_cubes(
        weights, isovalue, spacing=separations, gradient_direction="descent"
    )
    LOG.debug("Separation (x,y,z): %s", separations)
    verts = np.c_[verts[:, 1], verts[:, 0], verts[:, 2]] + l
    LOG.debug("Surface centroid: %s", np.mean(verts, axis=0))
    LOG.debug("Mol centroid: %s", np.mean(s.dens_a.positions, axis=0))
    LOG.debug("Max (x,y,z): %s", np.max(verts, axis=0))
    LOG.debug("Min (x,y,z): %s", np.min(verts, axis=0))
    vertex_props = {}
    if props:
        d_i, d_e, d_norm_i, d_norm_e = s.d_norm(verts)
        vertex_props["d_i"] = d_i
        vertex_props["d_e"] = d_e
        vertex_props["d_norm_i"] = d_norm_i
        vertex_props["d_norm_e"] = d_norm_e
        d_norm = d_norm_i + d_norm_e
        vertex_props["d_norm"] = d_norm
        LOG.debug("d_norm (min, max): (%.2f, %.2f)", np.min(d_norm), np.max(d_norm))
    t2 = time.time()
    LOG.info("stockholder weight surface took %.3fs, %d pts", t2 - t1, len(pts))
    return IsosurfaceMesh(verts, faces, normals, vertex_props)

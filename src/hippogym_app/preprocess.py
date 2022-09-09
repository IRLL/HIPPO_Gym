import math
import xml.etree.ElementTree as ET
from itertools import combinations

import numpy as np


def discretize(tipo):
    if tipo == "End":
        return 0
    if tipo == "Bifurcation":
        return 1
    if tipo == "Unknown":
        return 3
    print(tipo)


def ang(x1, y1, x2, y2):
    deltax = abs(x1 - x2)
    deltay = abs(y1 - y2)
    if deltax == 0:
        return math.pi / 2
    else:
        return np.arctan(deltay / deltax)


def ad2pi(alpha, beta):
    diff = abs(alpha - beta)
    return min(diff, 2 * math.pi - diff)


def euclidian_distance(m1, m2):
    return math.sqrt((m1[0] - m2[0]) ** 2 + (m1[1] - m2[1]) ** 2)


def find_distances(minutiae_list, feature_norm):
    mn = len(minutiae_list)
    distances = np.zeros((mn, mn))
    for m1_idx, m2_idx in combinations(range(mn), 2):
        distances[m1_idx, m2_idx] = distances[m2_idx, m1_idx] = euclidian_distance(
            minutiae_list[m1_idx], minutiae_list[m2_idx]
        )
    m = distances.max() if feature_norm else 1
    return distances / m, 35 / m


def get_minutiae_from_xml(xml_path):
    tree = ET.parse(xml_path)

    rv = []
    for minutia in tree.getroot():
        m = minutia.attrib
        rv.append((int(m["X"]), int(m["Y"]), m["Angle"], m["Type"]))
    return rv


def expand_minutia(
    minutia_idx, minutiae, distances, argsorted_distances, factor, feature_norm
):
    # distance to the 3 closest minutiae
    near_dist = distances[argsorted_distances[1:4]]

    # distance to the 3 farthest minutiae
    far_dist = distances[argsorted_distances[-3:]]

    # number of neighbors in a radix
    neighbors_number = (
        np.searchsorted(
            distances[argsorted_distances],
            [factor, factor * 2, factor * 3, factor * 4],
            side="right",
        )
        - 1
    )

    # angles
    angles = []

    minutia = list(minutiae[minutia_idx])
    minutia[2] = math.radians(float(minutia[2].replace(",", ".")))

    div = math.pi if feature_norm else 1
    for neighbor_idx in np.concatenate(
        (argsorted_distances[1:4], argsorted_distances[-3:])
    ):
        neighbor = list(minutiae[neighbor_idx])
        neighbor[2] = math.radians(float(neighbor[2].replace(",", ".")))

        minutia_neighbor_angle = ang(minutia[0], minutia[1], neighbor[0], neighbor[1])

        minutia_neighbor_alpha_angle = ad2pi(minutia_neighbor_angle, minutia[2])
        angles.append(minutia_neighbor_alpha_angle / div)

        neighbor_minutia_alpha_angle = ad2pi(minutia_neighbor_angle, neighbor[2])
        angles.append(neighbor_minutia_alpha_angle / div)

        minutia_neighbor_beta_angle = ad2pi(minutia[2], neighbor[2])
        angles.append(minutia_neighbor_beta_angle / div)

    return (
        list(near_dist)
        + list(far_dist)
        + list(neighbors_number / (len(minutiae) - 1 if feature_norm else 1))
        + angles
        + [discretize(minutia[3])]
    )


def get_one_pair_regresor_data(xml_path, FEATURE_NORM=True):
    latent_xml = xml_path
    latent_minutiae = get_minutiae_from_xml(latent_xml)

    latent_minutiae_distances, latent_distances_factor = find_distances(
        latent_minutiae, FEATURE_NORM
    )

    argsorted_latent_minutiae_distances = np.argsort(latent_minutiae_distances, axis=1)

    rv = []
    for latent_minutia_idx in range(len(latent_minutiae)):
        argumented_latent_minutia = expand_minutia(
            latent_minutia_idx,
            latent_minutiae,
            latent_minutiae_distances[latent_minutia_idx],
            argsorted_latent_minutiae_distances[latent_minutia_idx],
            latent_distances_factor,
            FEATURE_NORM,
        )
        rv.append(argumented_latent_minutia)
    return rv, latent_minutiae

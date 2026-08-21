"""
spaces/anam_tuatha/chemistry_visual.py
Uisce theme: A small molecule renderer.

Renders simple 2D molecule diagrams from SMILES-like notation. Pure
SVG, no RDKit dep. Supports a curated set of common molecules from
the Irish LC Chemistry syllabus.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Atom:
    element: str  # "C", "H", "O", "N", "S", "Cl", "Na"
    x: float  # 0-100 coords
    y: float
    label: str | None = None  # override element label


@dataclass(frozen=True)
class Bond:
    a: int  # index into atoms
    b: int
    order: int = 1  # 1, 2, 3


@dataclass(frozen=True)
class Molecule:
    name: str
    name_ga: str
    formula: str
    atoms: tuple[Atom, ...]
    bonds: tuple[Bond, ...]
    description: str


# Curated 8 molecules from the Irish LC Chemistry syllabus
MOLECULES: dict[str, Molecule] = {
    "water": Molecule(
        "Water",
        "Uisce",
        "H2O",
        atoms=(
            Atom("O", 50, 25),
            Atom("H", 35, 50),
            Atom("H", 65, 50),
        ),
        bonds=(
            Bond(0, 1, 1),
            Bond(0, 2, 1),
        ),
        description=(
            "Bent geometry (104.5°). The oxygen has two lone pairs. "
            "Polar covalent bond; the molecule is polar overall."
        ),
    ),
    "methane": Molecule(
        "Methane",
        "Meatán",
        "CH4",
        atoms=(
            Atom("C", 50, 35),
            Atom("H", 50, 10),
            Atom("H", 25, 50),
            Atom("H", 75, 50),
            Atom("H", 50, 60),
        ),
        bonds=(
            Bond(0, 1, 1),
            Bond(0, 2, 1),
            Bond(0, 3, 1),
            Bond(0, 4, 1),
        ),
        description=(
            "Tetrahedral geometry (109.5°). sp3 hybridisation. "
            "The simplest alkane; the parent of organic chemistry."
        ),
    ),
    "ethanol": Molecule(
        "Ethanol",
        "Eatánól",
        "C2H5OH",
        atoms=(
            Atom("C", 25, 35),
            Atom("C", 55, 35),
            Atom("O", 80, 35),
            Atom("H", 25, 15),
            Atom("H", 25, 55),
            Atom("H", 55, 15),
            Atom("H", 55, 55),
            Atom("H", 90, 25),
        ),
        bonds=(
            Bond(0, 1, 1),
            Bond(1, 2, 1),
            Bond(0, 3, 1),
            Bond(0, 4, 1),
            Bond(1, 5, 1),
            Bond(1, 6, 1),
            Bond(2, 7, 1),
        ),
        description=(
            "Two sp3 carbons, one hydroxyl group. Hydrogen-bond donor "
            "and acceptor; miscible with water in all proportions."
        ),
    ),
    "ammonia": Molecule(
        "Ammonia",
        "Amóinia",
        "NH3",
        atoms=(
            Atom("N", 50, 25),
            Atom("H", 35, 50),
            Atom("H", 65, 50),
            Atom("H", 50, 60),
        ),
        bonds=(
            Bond(0, 1, 1),
            Bond(0, 2, 1),
            Bond(0, 3, 1),
        ),
        description=(
            "Trigonal pyramidal (107°). The nitrogen has one lone pair. "
            "Brønsted-Lowry base; conjugate acid is ammonium (NH4+)."
        ),
    ),
    "co2": Molecule(
        "Carbon Dioxide",
        "Dé-ocsaíd Charbóin",
        "CO2",
        atoms=(
            Atom("C", 50, 35),
            Atom("O", 25, 35),
            Atom("O", 75, 35),
        ),
        bonds=(
            Bond(0, 1, 2),
            Bond(0, 2, 2),
        ),
        description=(
            "Linear (180°). Two double bonds. sp hybridisation. "
            "Non-polar despite polar bonds (symmetric)."
        ),
    ),
    "benzene": Molecule(
        "Benzene",
        "Beinséin",
        "C6H6",
        atoms=(
            Atom("C", 50, 10),
            Atom("C", 80, 25),
            Atom("C", 80, 55),
            Atom("C", 50, 70),
            Atom("C", 20, 55),
            Atom("C", 20, 25),
        ),
        bonds=(
            Bond(0, 1, 2),
            Bond(1, 2, 1),
            Bond(2, 3, 2),
            Bond(3, 4, 1),
            Bond(4, 5, 2),
            Bond(5, 0, 1),
        ),
        description=(
            "Planar hexagonal ring, sp2 hybridisation. "
            "Delocalised pi system; aromatic by Huckel's 4n+2 rule."
        ),
    ),
    "methanol": Molecule(
        "Methanol",
        "Meatánól",
        "CH3OH",
        atoms=(
            Atom("C", 40, 35),
            Atom("O", 65, 35),
            Atom("H", 25, 25),
            Atom("H", 35, 55),
            Atom("H", 50, 50),
            Atom("H", 75, 30),
        ),
        bonds=(
            Bond(0, 1, 1),
            Bond(0, 2, 1),
            Bond(0, 3, 1),
            Bond(0, 4, 1),
            Bond(1, 5, 1),
        ),
        description=(
            "Simplest alcohol. Wood alcohol; toxic to drink. "
            "Industrial precursor to formaldehyde and acetic acid."
        ),
    ),
    "sodium_chloride": Molecule(
        "Sodium Chloride",
        "Clóiríd Sóidiam",
        "NaCl",
        atoms=(
            Atom("Na", 30, 35, label="Na+"),
            Atom("Cl", 70, 35, label="Cl-"),
        ),
        bonds=(Bond(0, 1, 1),),
        description=(
            "Ionic bond. The sodium donates an electron to the chlorine. "
            "Forms a face-centred cubic lattice in the solid state."
        ),
    ),
}


def _atom_color(element: str) -> str:
    """CPK color scheme for atoms."""
    return {
        "C": "#1a1d2e",  # dark
        "H": "#d8d4cc",  # bone
        "O": "#1e80c6",  # Uisce azure
        "N": "#5a4fcf",  # Aer indigo
        "S": "#d68c1c",  # Tine amber
        "Cl": "#28955e",  # Talamh emerald
        "Na": "#a83a2a",  # Pobal crimson
    }.get(element, "#cc9966")


def render_molecule_svg(molecule_key: str, size: int = 240) -> str:
    """Render a molecule as a self-contained SVG string."""
    mol = MOLECULES.get(molecule_key)
    if mol is None:
        return f'<div style="color:#a83a2a;">Unknown molecule: {molecule_key}</div>'

    # Scale 0-100 to 0-size
    def sx(x: float) -> int:
        return int(20 + x * (size - 40) / 100)

    def sy(y: float) -> int:
        return int(20 + y * (size - 40) / 100)

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {size} {size}" width="{size}" height="{size}" '
        f'style="background:#1d1d2f; border:1px solid #1e80c6; border-radius:4px;">',
    ]

    # Bonds
    for bond in mol.bonds:
        a, b = mol.atoms[bond.a], mol.atoms[bond.b]
        color = "#1e80c6" if bond.order == 1 else "#28955e"
        width = 2 if bond.order == 1 else 3
        if bond.order == 2:
            # Draw two parallel lines for double bond
            parts.append(
                f'<line x1="{sx(a.x)}" y1="{sy(a.y)}" '
                f'x2="{sx(b.x)}" y2="{sy(b.y)}" '
                f'stroke="{color}" stroke-width="{width}" />'
            )
            # Offset perpendicular
            dx = sx(b.x) - sx(a.x)
            dy = sy(b.y) - sy(a.y)
            length = max((dx * dx + dy * dy) ** 0.5, 1)
            ox = -dy / length * 3
            oy = dx / length * 3
            parts.append(
                f'<line x1="{sx(a.x) + ox}" y1="{sy(a.y) + oy}" '
                f'x2="{sx(b.x) + ox}" y2="{sy(b.y) + oy}" '
                f'stroke="{color}" stroke-width="{width}" />'
            )
        elif bond.order == 3:
            parts.append(
                f'<line x1="{sx(a.x)}" y1="{sy(a.y)}" '
                f'x2="{sx(b.x)}" y2="{sy(b.y)}" '
                f'stroke="{color}" stroke-width="{width}" />'
            )
            dx = sx(b.x) - sx(a.x)
            dy = sy(b.y) - sy(a.y)
            length = max((dx * dx + dy * dy) ** 0.5, 1)
            ox = -dy / length * 4
            oy = dx / length * 4
            parts.append(
                f'<line x1="{sx(a.x) + ox}" y1="{sy(a.y) + oy}" '
                f'x2="{sx(b.x) + ox}" y2="{sy(b.y) + oy}" '
                f'stroke="{color}" stroke-width="{width}" />'
            )
            parts.append(
                f'<line x1="{sx(a.x) - ox}" y1="{sy(a.y) - oy}" '
                f'x2="{sx(b.x) - ox}" y2="{sy(b.y) - oy}" '
                f'stroke="{color}" stroke-width="{width}" />'
            )
        else:
            parts.append(
                f'<line x1="{sx(a.x)}" y1="{sy(a.y)}" '
                f'x2="{sx(b.x)}" y2="{sy(b.y)}" '
                f'stroke="{color}" stroke-width="{width}" />'
            )

    # Atoms
    for atom in mol.atoms:
        color = _atom_color(atom.element)
        text_color = "#1a1d2e" if atom.element == "C" else "#d8d4cc"
        label = atom.label or atom.element
        parts.append(
            f'<circle cx="{sx(atom.x)}" cy="{sy(atom.y)}" r="14" '
            f'fill="{color}" stroke="#1a1d2e" stroke-width="1" />'
        )
        parts.append(
            f'<text x="{sx(atom.x)}" y="{sy(atom.y) + 4}" text-anchor="middle" '
            f'fill="{text_color}" font-family="Inter,sans-serif" '
            f'font-size="11" font-weight="bold">{label}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def list_molecules() -> list[dict[str, str]]:
    """Return a list of available molecules for the dropdown."""
    return [
        {"key": k, "name": m.name, "name_ga": m.name_ga, "formula": m.formula}
        for k, m in MOLECULES.items()
    ]

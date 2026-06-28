"""Celtic prompt generation for image models."""


from .models import AssetType, CelticStyle, ClanId, ItemRarity


class CelticPromptGenerator:
    """Generate prompts for Celtic-themed asset generation."""

    # Base style descriptors
    STYLE_DESCRIPTORS = {
        CelticStyle.LA_TENE: (
            "La Tène Celtic art style, flowing S-curves, vegetal motifs, "
            "Iron Age decorative patterns, organic flowing lines"
        ),
        CelticStyle.OGHAM: (
            "Ogham inscription style, linear marks, standing stone aesthetics, "
            "ancient Celtic script patterns, weathered stone texture"
        ),
        CelticStyle.KNOTWORK: (
            "Celtic knotwork, intricate interlacing patterns, endless loops, "
            "woven ribbon designs, Book of Kells inspired"
        ),
        CelticStyle.ZOOMORPHIC: (
            "Celtic zoomorphic art, stylized animal forms, serpentine creatures, "
            "intertwined beasts, mythical creature motifs"
        ),
        CelticStyle.SPIRAL: (
            "Celtic spiral patterns, triskelion motifs, Newgrange spirals, "
            "concentric circular designs, sacred geometry"
        ),
        CelticStyle.ILLUMINATED: (
            "Illuminated manuscript style, ornate borders, gold leaf accents, "
            "vibrant colors, medieval Celtic Christian art"
        ),
    }

    # Clan-specific aesthetics
    CLAN_AESTHETICS = {
        ClanId.TUATHA_DE_DANANN: (
            "divine radiance, silver and gold, magical aura, "
            "skilled craftsmanship, ethereal glow"
        ),
        ClanId.FIR_BOLG: (
            "earthy tones, agricultural motifs, warrior strength, "
            "bronze and iron, sturdy construction"
        ),
        ClanId.FOMORIANS: (
            "dark oceanic themes, chaotic patterns, monstrous elements, "
            "sea creature motifs, otherworldly darkness"
        ),
        ClanId.MILESIANS: (
            "Mediterranean influence, Mediterranean blues, "
            "navigation symbols, conquest imagery"
        ),
    }

    # Rarity enhancements
    RARITY_MODIFIERS = {
        ItemRarity.COMMON: "",
        ItemRarity.UNCOMMON: "slightly ornate, quality craftsmanship",
        ItemRarity.RARE: "elaborate details, masterwork quality, glowing accents",
        ItemRarity.EPIC: "legendary craftsmanship, magical aura, intricate engravings",
        ItemRarity.LEGENDARY: (
            "divine quality, radiant magical energy, impossibly detailed, "
            "mythical presence, awe-inspiring"
        ),
    }

    # Negative prompts for quality
    NEGATIVE_PROMPT_BASE = (
        "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
        "bad proportions, watermark, signature, text, logo, modern elements, "
        "photorealistic, photograph, 3d render"
    )

    def __init__(self):
        """Initialize the prompt generator."""
        pass

    def generate_prompt(
        self,
        asset_type: AssetType,
        style: CelticStyle,
        item_name: str | None = None,
        item_type: str | None = None,
        rarity: ItemRarity = ItemRarity.COMMON,
        clan: ClanId | None = None,
        power_level: int = 1,
        custom_elements: str | None = None,
    ) -> str:
        """Generate a complete prompt for the asset."""

        parts = []

        # Asset type specific base
        base = self._get_asset_base(asset_type, item_name, item_type)
        parts.append(base)

        # Style descriptor
        parts.append(self.STYLE_DESCRIPTORS[style])

        # Rarity modifier
        if rarity != ItemRarity.COMMON:
            parts.append(self.RARITY_MODIFIERS[rarity])

        # Clan aesthetics
        if clan:
            parts.append(self.CLAN_AESTHETICS[clan])

        # Power level (affects visual intensity)
        if power_level > 50:
            parts.append("powerful magical energy, intense glow")
        elif power_level > 25:
            parts.append("visible magical enhancement, subtle glow")

        # Custom elements
        if custom_elements:
            parts.append(custom_elements)

        # Quality boosters
        parts.append("high quality, detailed illustration, fantasy art, game asset")

        return ", ".join(filter(None, parts))

    def _get_asset_base(
        self,
        asset_type: AssetType,
        item_name: str | None,
        item_type: str | None,
    ) -> str:
        """Get base prompt for asset type."""

        if asset_type == AssetType.CHARACTER_PORTRAIT:
            return (
                f"Celtic warrior portrait{f' named {item_name}' if item_name else ''}, "
                "detailed face, historical Celtic attire, braided hair, "
                "fierce expression, torque necklace"
            )

        elif asset_type == AssetType.ITEM_ICON:
            type_str = item_type or "weapon"
            name_str = f"'{item_name}'" if item_name else ""
            return (
                f"Celtic {type_str} {name_str} icon, centered composition, "
                "game item icon, ornate details, fantasy weapon"
            )

        elif asset_type == AssetType.CLAN_HERALDRY:
            return (
                "Celtic clan shield emblem, heraldic design, "
                "symmetrical composition, coat of arms style"
            )

        elif asset_type == AssetType.TERRITORY_TILE:
            return (
                "Celtic landscape tile, isometric view, game terrain, "
                "Irish countryside, standing stones, ancient ruins"
            )

        elif asset_type == AssetType.SPELL_EFFECT:
            return (
                "Celtic magical effect, druidic spell, "
                "mystical energy, rune circle, nature magic"
            )

        elif asset_type == AssetType.CREATURE:
            return (
                f"Celtic mythical creature{f' {item_name}' if item_name else ''}, "
                "fantasy beast, Irish mythology, detailed illustration"
            )

        return "Celtic themed fantasy art"

    def get_negative_prompt(
        self,
        asset_type: AssetType,
        additional: str | None = None,
    ) -> str:
        """Get negative prompt for the asset type."""

        parts = [self.NEGATIVE_PROMPT_BASE]

        # Asset-specific negatives
        if asset_type == AssetType.CHARACTER_PORTRAIT:
            parts.append("extra limbs, extra fingers, mutated hands")
        elif asset_type == AssetType.ITEM_ICON:
            parts.append("multiple items, cluttered background, hands holding")
        elif asset_type == AssetType.TERRITORY_TILE:
            parts.append("characters, people, modern buildings")

        if additional:
            parts.append(additional)

        return ", ".join(parts)

    def generate_inpainting_prompt(
        self,
        base_description: str,
        edit_instruction: str,
        style: CelticStyle,
    ) -> str:
        """Generate prompt for inpainting/editing."""

        return (
            f"{edit_instruction}, maintaining {self.STYLE_DESCRIPTORS[style]}, "
            f"consistent with {base_description}, seamless integration"
        )

    def generate_style_transfer_prompt(
        self,
        target_style: CelticStyle,
        preserve_content: str,
    ) -> str:
        """Generate prompt for style transfer."""

        return (
            f"Transform to {self.STYLE_DESCRIPTORS[target_style]}, "
            f"preserving {preserve_content}, Celtic art adaptation"
        )


# Pre-generate common item prompts for caching
COMMON_WEAPON_PROMPTS = {
    "sword": "Celtic longsword, decorated blade, ornate pommel, warrior's weapon",
    "spear": "Celtic spear, leaf-shaped blade, decorated shaft, hunting weapon",
    "shield": "Celtic round shield, boss center, painted design, battle-worn",
    "axe": "Celtic battle axe, bronze head, carved handle, war weapon",
    "bow": "Celtic hunting bow, yew wood, carved nocks, leather wrapped",
    "sling": "Celtic sling, leather pouch, woven cord, ranged weapon",
}

COMMON_ARMOR_PROMPTS = {
    "helmet": "Celtic helmet, bronze, cheek guards, plume crest",
    "shield": "Celtic warrior shield, wooden with metal rim, painted design",
    "cloak": "Celtic cloak, wool fabric, brooch clasp, checkered pattern",
    "torque": "Celtic neck torque, twisted gold, terminal ends, status symbol",
    "greaves": "Celtic leg armor, bronze greaves, embossed patterns",
}

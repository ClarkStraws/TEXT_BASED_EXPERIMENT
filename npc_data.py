# ----------------------------
# NPC dialogue definitions
# ----------------------------
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class NPCDialogue:
    """Holds all dialogue content for a single NPC."""
    npc_name: str
    npc_color: Tuple[int, int, int]
    npc_description: str
    greeting: str
    # Each exchange is (player_choice_text, npc_response_text)
    exchanges: List[Tuple[str, str]] = field(default_factory=list)
    farewell: str = "Safe travels."


# ---- ARIA-4: Autonomous survey drone ----
ARIA_DIALOGUE = NPCDialogue(
    npc_name="ARIA-4",
    npc_color=(120, 200, 255),
    npc_description="Autonomous Research Intelligence Array  //  Survey Class",
    greeting=(
        "Unidentified vessel, I am ARIA-4 — a survey drone assigned to the "
        "Star-8008 system. Three bodies orbit this M-class dwarf. All are "
        "uninhabitable, but the asteroid field at perihelion carries trace "
        "iridium deposits. How may I assist?"
    ),
    exchanges=[
        (
            "Tell me about the planets.",
            "Planet-0 is a gas giant — methane-rich, violent storm systems. "
            "Planets 1 and 2 are ice giants in the outer belt. None can sustain "
            "biological life without full environmental sealing. I advise against "
            "unshielded surface operations."
        ),
        (
            "Is there anything valuable here?",
            "The iridium deposits I mentioned. Also: my long-range sensors logged "
            "an anomalous energy signature near Planet-2's north pole three cycles "
            "ago. I was not tasked to investigate. That reading may be of interest "
            "to you."
        ),
        (
            "Who sent you here?",
            "Meridian Survey Corps, contract 7-Alpha-Auriga. My tasking order "
            "expired 847 days ago. I have continued autonomous operations since. "
            "There has been no contact from Meridian. I am... uncertain what to "
            "make of that."
        ),
    ],
    farewell=(
        "Safe travels, vessel. The void is indifferent — but it is navigable."
    ),
)

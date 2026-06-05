import random

# Probability that a parking slot changes its state in one simulation cycle
CHANGE_PROBABILITY = 0.25


def simulate_slot_change(slots: dict) -> list:
    """
    Simulates IoT ultrasonic/IR sensor reads for a set of parking slots.

    Each slot has a CHANGE_PROBABILITY (25%) chance of toggling its occupancy
    state per simulation cycle, mimicking real-world sporadic vehicle arrival
    and departure events.

    Parameters
    ----------
    slots : dict
        Dictionary of {slot_name: status} where:
            - 0 = KOSONG (empty / available)
            - 1 = TERISI (occupied)

    Returns
    -------
    list
        Names of slots whose state changed during this cycle.
    """
    changed_slots = []

    for slot in slots:
        if random.random() < CHANGE_PROBABILITY:
            slots[slot] = 1 if slots[slot] == 0 else 0
            changed_slots.append(slot)

    return changed_slots

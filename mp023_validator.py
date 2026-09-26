import cv2
import numpy as np
from PIL import Image

# The supplied MP-F-023 sample renders to 1224 x 1584 at 2x.
# We normalize every uploaded MP-F-023 page to that coordinate system.
CANONICAL_W = 1224
CANONICAL_H = 1584

# Writable/value-only regions. These deliberately avoid printed labels and cell borders.
# x1, y1, x2, y2 in canonical pixels.
TOP_FIELDS = {
    "Donor #": (122, 104, 174, 132),
    "Verified By": (76, 160, 170, 205),
    "Cross Reference #": (190, 160, 285, 205),
    "Donor Sex": (305, 160, 355, 205),
    "Donor Age": (375, 160, 425, 205),
    "Date of Recovery": (445, 160, 525, 205),
    "Instruction Verification": (550, 160, 725, 205),
    "Date of Processing": (750, 160, 835, 205),
}

BY_DATE_FIELDS = {
    "Clean Room Log Review By / Date": {
        "initials": (855, 160, 985, 185),
        "date": (855, 185, 985, 207),
    },
    "Tissue Checked In By / Date": {
        "initials": (1010, 160, 1112, 185),
        "date": (1010, 185, 1112, 207),
    },
    "Operations Manager Review": {
        "initials": (592, 705, 635, 735),
        "date": (640, 705, 805, 735),
    },
}

# These are the named processing rows with writable Produced/Packaged cells
# in the supplied MP-F-023 form layout.
# Each tuple is (row label, y1, y2).
PROCESSING_ROWS = [
    ("Posterior Tibialis", 776, 791),
    ("Anterior Tibialis", 800, 816),
    ("Peroneus Longus", 825, 840),
    ("Gracilis", 849, 864),
    ("Semitendinosus", 873, 888),
    ("Patellar Ligament", 923, 948),
    ("Femoral Head", 982, 997),
    ("Humeral Head", 1006, 1022),
    ("Tri-Cortical Block", 1055, 1077),
    ("Cancellous 1-10 mm", 1113, 1129),
    ("Cancellous 4-10 mm", 1137, 1153),
    ("Cancellous 1-4 mm", 1162, 1178),
    ("Cancellous 3-6 mm", 1187, 1203),
    ("Tibia Shaft", 1237, 1253),
    ("Humerus Shaft", 1262, 1278),
    ("Femur Shaft", 1287, 1303),
    ("Fibula Shaft", 1312, 1328),
]

PRODUCED_X = (555, 657)
PACKAGED_X = (680, 790)


def _normalize(image: Image.Image) -> np.ndarray:
    arr = np.array(image.convert("RGB"))

    # Handle accidental landscape orientation.
    if arr.shape[1] > arr.shape[0]:
        arr = cv2.rotate(arr, cv2.ROTATE_90_CLOCKWISE)

    arr = cv2.resize(arr, (CANONICAL_W, CANONICAL_H), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)


def _occupancy(gray: np.ndarray, box):
    """
    Estimate whether a writable box contains ink.

    We use both dark-pixel ratio and connected-component size so faint handwriting
    can count while tiny scan speckles do not.
    """
    x1, y1, x2, y2 = box
    crop = gray[y1:y2, x1:x2]

    if crop.size == 0:
        return {"present": False, "dark_ratio": 0.0, "largest_component": 0}

    # Pencil/pen in the supplied scans can be light gray.
    mask = (crop < 220).astype(np.uint8)

    dark_ratio = float(mask.mean())

    count, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if count > 1:
        largest_component = int(stats[1:, cv2.CC_STAT_AREA].max())
    else:
        largest_component = 0

    # Tuned conservatively on the supplied MP-F-023 scan.
    present = dark_ratio >= 0.018 or largest_component >= 18

    return {
        "present": bool(present),
        "dark_ratio": round(dark_ratio, 4),
        "largest_component": largest_component,
    }


def validate_mp023(image: Image.Image):
    gray = _normalize(image)
    issues = []
    debug = []

    def check_box(location, box, message="Required field appears blank."):
        result = _occupancy(gray, box)
        debug.append({
            "Field": location,
            "Present": result["present"],
            "Dark ratio": result["dark_ratio"],
            "Largest component": result["largest_component"],
        })
        if not result["present"]:
            issues.append({"location": location, "message": message})

    # Rule 1: no blank fields in the top section.
    for label, box in TOP_FIELDS.items():
        check_box(f"Top / {label}", box)

    # Rule 1 + Rule 2: any By/Date field must contain both parts.
    for label, parts in BY_DATE_FIELDS.items():
        check_box(
            f"{label} / Initials",
            parts["initials"],
            "Initials appear blank.",
        )
        check_box(
            f"{label} / Date",
            parts["date"],
            "Date appears blank.",
        )

    # Rule 3: the Produced and Packaged writable cells must not be blank.
    for row_name, y1, y2 in PROCESSING_ROWS:
        produced_box = (PRODUCED_X[0], y1, PRODUCED_X[1], y2)
        packaged_box = (PACKAGED_X[0], y1, PACKAGED_X[1], y2)

        check_box(
            f"Processing Instructions / {row_name} / # Produced",
            produced_box,
            "# Produced appears blank.",
        )
        check_box(
            f"Processing Instructions / {row_name} / # Packaged",
            packaged_box,
            "# Packaged appears blank.",
        )

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "debug": debug,
    }

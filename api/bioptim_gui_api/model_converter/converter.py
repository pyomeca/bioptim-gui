from bioptim_gui_api.model_converter.converter_str_utils import BioModConverterUtils


class BioModConverter:
    """
    Base class for bioMod model converters, SHOULD NOT be used directly

    Attributes
    ----------
    segment_rotation: dict
        A dictionary containing the segment name as key and the rotation as value (e.g. "Pelvis" : "xyz")
        that the model should contain
    segment_translation: dict
        A dictionary containing the segment name as key and the translation as value (e.g. "Pelvis" : "xyz")
        that the model should contain
    markers: list
        A list of markers names that the model should contain
    """

    segment_rotation = {}
    segment_translation = {}
    markers = []

    @classmethod
    def _add_dofs(cls, segment_name: str, updated_lines: list[str], stripped: str):
        """
        This function is used to add them to the updated_lines list if needed.

        rotations and translations line in a bioMod are usually written after the rt line.
        """
        if stripped.startswith("rt"):
            if segment_name in cls.segment_translation:
                updated_lines.append(f"\ttranslations {cls.segment_translation[segment_name]}\n")
            if segment_name in cls.segment_rotation:
                updated_lines.append(f"\trotations {cls.segment_rotation[segment_name]}\n")

    @classmethod
    def _ignore_unused_markers(cls, lines: list[str], current_index: int) -> int:
        """
        This function is used to ignore the markers that are not used in the model.
        """
        stripped = lines[current_index].strip()

        if not stripped.startswith("marker"):
            return current_index

        marker_name = stripped.split()[1]
        if marker_name in cls.markers:
            # don't ignore the marker, it is used
            return current_index

        while not lines[current_index].strip().startswith("endmarker"):
            current_index += 1

        # recursive call to handle the case where there are multiple markers in a row without a new line
        return cls._ignore_unused_markers(lines, current_index + 1)

    @classmethod
    def _check_missing_segments(cls, lines: list[str]) -> None:
        """
        This function is used to check that the model contains all the required segments according to the converter.
        """
        utils = BioModConverterUtils(lines)
        existing_segments = set()
        segment_name = ""
        for i, _ in enumerate(lines):
            segment_name = utils.get_segment_name(i, segment_name)
            if segment_name in cls.segment_rotation or segment_name in cls.segment_translation:
                existing_segments.add(segment_name)

        missing_segments = (set(cls.segment_rotation) | set(cls.segment_translation)) - existing_segments

        if missing_segments:
            raise ValueError(f"Missing segments: {', '.join(missing_segments)}")

    @classmethod
    def _check_missing_markers(cls, lines: list[str]) -> None:
        """
        This function is used to check that the model contains all the required markers according to the converter.
        """
        utils = BioModConverterUtils(lines)
        existing_markers = set()
        for line in lines:
            marker_name = utils.get_marker_name(line)
            if marker_name in cls.markers:
                existing_markers.add(marker_name)

        missing_markers = set(cls.markers) - existing_markers
        if missing_markers:
            raise ValueError(f"Missing markers: {', '.join(missing_markers)}")

    @classmethod
    def convert(cls, model_content: str) -> str:
        """
        'Convert' a bioptim model

        - Checking that it contains all the required markers/segments according to the converter class attributes.
        - Missing markers/segments will raise a ValueError.
        - Not used segments will be ignored but will stay in the model (removing them would alter the inertia and mass).
        - Not used markers will be removed from the model.
        - Rotations and translations will be updated if needed:
            - If a segment rotation/translation is 'xzy' in the converter class and 'zx' in the model, it will be
            updated to 'xzy'.
            - If it contains more axes, the additional axes will be removed (e.g. 'xyz' -> 'xy'), or the line
            completely removed if the converter class does not contain this segment.
        - The order of the markers/segments is not changed.
        - All rangesQ are removed from the model.

        Parameters
        ----------
        model_content: str
            The path to the bioptim model

        Returns
        -------
        The updated bioMod model as a string

        Raises
        ------
        ValueError
            If the model does not contain all the required markers/segments
        """
        lines = [line + "\n" for line in model_content.split("\n")]

        utils = BioModConverterUtils(lines)
        cls._check_missing_segments(lines)
        cls._check_missing_markers(lines)

        n_lines = len(lines)
        updated_lines = []
        segment_name = ""

        i = 0

        while i < n_lines:
            segment_name = utils.get_segment_name(i, segment_name)

            i = cls._ignore_unused_markers(lines, i)

            i = utils.ignore_dofs_lines(i)
            # rangesQ tends to be just after the dofs
            i = utils.skip_ranges_q(i)

            stripped = lines[i].strip()
            # if condition in the case of dofs being after rangesQ
            if not stripped.startswith("rotations") and not stripped.startswith("translations"):
                updated_lines.append(lines[i])

            cls._add_dofs(segment_name, updated_lines, stripped)

            i += 1

        return "".join(updated_lines)


class StraightConverter(BioModConverter):
    segment_rotation = {
        "Pelvis": "xyz",
        "RightUpperArm": "zy",
        "LeftUpperArm": "zy",
    }

    segment_translation = {"Pelvis": "xyz"}


class PikeConverter(StraightConverter):
    segment_rotation = {
        "Pelvis": "xyz",
        "RightUpperArm": "zy",
        "RightForearm": "zx",
        "LeftUpperArm": "zy",
        "LeftForearm": "zx",
        "UpperLegs": "xy",
    }

    markers = [
        "MiddleRightHand",
        "PikeTargetRightHand",
        "MiddleLeftHand",
        "PikeTargetLeftHand",
    ]


class TuckConverter(StraightConverter):
    segment_rotation = {
        "Pelvis": "xyz",
        "RightUpperArm": "zy",
        "RightForearm": "zx",
        "LeftUpperArm": "zy",
        "LeftForearm": "zx",
        "UpperLegs": "xy",
        "LowerLegs": "x",
    }

    markers = [
        "MiddleRightHand",
        "TuckTargetRightHand",
        "MiddleLeftHand",
        "TuckTargetLeftHand",
    ]

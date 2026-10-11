"""Dynamic soil stiffness utilities for pipeline spanning calculations."""

import numpy as np


class PSIDynamic:
    """
    Class for dynamic soil stiffness calculations for pipeline spanning.

    Parameters
    ----------
    total_outer_diameter : float or array-like, optional
        Total outer diameter of the pipe. Default is 0.
    specific_mass_ratio :  float or array-like, optional
        Relative mass ratio of the pipe to displaced water. Default is 0.
    soil_type : str or array-like, optional
        Soil type for lookup: 'Loose Sand', 'Medium Sand', 'Dense Sand',
        'Very Soft Clay', 'Soft Clay', 'Firm Clay', 'Stiff Clay',
        'Very Stiff Clay', or 'Hard Clay'. Default is None.

    Notes
    -----
    All inputs support scalar and array-like values. When arrays are supplied,
    NumPy broadcasting rules apply.
    """

    CV = {
        "Loose Sand": 10500.0E+03,
        "Medium Sand": 14500.0E+03,
        "Dense Sand": 21000.0E+03,
        "Very Soft Clay": 600.0E+03,
        "Soft Clay": 1400.0E+03,
        "Firm Clay": 3000.0E+03,
        "Stiff Clay": 4500.0E+03,
        "Very Stiff Clay": 11000.0E+03,
        "Hard Clay": 12000.0E+03,
    }
    CL = {
        "Loose Sand": 9000.0E+03,
        "Medium Sand": 12500.0E+03,
        "Dense Sand": 18000.0E+03,
        "Very Soft Clay": 500.0E+03,
        "Soft Clay": 1200.0E+03,
        "Firm Clay": 2600.0E+03,
        "Stiff Clay": 3900.0E+03,
        "Very Stiff Clay": 9500.0E+03,
        "Hard Clay": 10500.0E+03,
    }
    KV = {
        "Loose Sand": 250.0E+03,
        "Medium Sand": 530.0E+03,
        "Dense Sand": 1350.0E+03,
        "Very Soft Clay": 100.0E+03,
        "Soft Clay": 260.0E+03,
        "Firm Clay": 800.0E+03,
        "Stiff Clay": 1600.0E+03,
        "Very Stiff Clay": 3000.0E+03,
        "Hard Clay": 4200.0E+03,
    }
    SOIL_POISSON = {
        "Loose Sand": 0.35,
        "Medium Sand": 0.35,
        "Dense Sand": 0.35,
        "Very Soft Clay": 0.5,
        "Soft Clay": 0.5,
        "Firm Clay": 0.5,
        "Stiff Clay": 0.5,
        "Very Stiff Clay": 0.5,
        "Hard Clay": 0.5,
    }

    def __init__(
            self,
            *,
            total_outer_diameter=0.0,
            specific_mass_ratio=0.0,
            soil_type=None
        ):
        """
        Initialize a PSIDynamic object with pipe and soil properties.
        """
        self.total_outer_diameter = np.asarray(total_outer_diameter, dtype=float)
        self.specific_mass_ratio = np.asarray(specific_mass_ratio, dtype=float)
        self.soil_type = np.asarray(soil_type, dtype=object)

    def _lookup_soil_property(self, property_name):
        """
        Return a soil property array mapped from the input soil types.

        Parameters
        ----------
        property_name : str
            One of 'Cv', 'Cl', 'Kv', or 'soil_poisson'.

        Returns
        -------
        np.ndarray
            Property values with shape compatible with ``soil_type``.

        Raises
        ------
        ValueError
            If a soil type or property name is not supported.
        """
        valid_properties = ("Cv", "Cl", "Kv", "soil_poisson")
        if property_name not in valid_properties:
            raise ValueError(
                "Unsupported property name. Expected one of: "
                + ", ".join(valid_properties)
            )

        flat_soil_types = np.ravel(self.soil_type)
        values = np.empty(flat_soil_types.shape[0], dtype=float)
        for i, soil in enumerate(flat_soil_types):
            try:
                values[i] = getattr(self, property_name.upper())[soil]
            except KeyError as exc:
                raise ValueError(
                    "Unsupported soil type. Expected one of: "
                    + ", ".join(self.CV)
                ) from exc

        return values.reshape(self.soil_type.shape)

    def soil_properties(self):
        """
        Return lookup properties for the configured soil type.

        Returns
        -------
        dict
            Dictionary with keys ``Cv``, ``Cl``, ``Kv``, and ``soil_poisson``.

        Examples
        --------
        >>> soil_type = ["Medium Sand", "Stiff Clay"]
        >>> spanning = PSIDynamic(soil_type=soil_type)
        >>> for name, values in spanning.soil_properties().items():
        ...     print(f"{name}: {values}")
        Cv: [14500000.  4500000.]
        Cl: [12500000.  3900000.]
        Kv: [ 530000. 1600000.]
        soil_poisson: [0.35 0.5 ]
        """
        return {
            "Cv": self._lookup_soil_property("Cv"),
            "Cl": self._lookup_soil_property("Cl"),
            "Kv": self._lookup_soil_property("Kv"),
            "soil_poisson": self._lookup_soil_property("soil_poisson"),
        }

    def dynamic_stiffness_horizontal(self):
        """
        Calculate the horizontal dynamic stiffness of the pipe based on soil type.

        Returns
        -------
        dynamic_stiffness_horizontal : np.ndarray
            Horizontal dynamic stiffness.

        Raises
        ------
        ValueError
            If the soil type is not supported.

        Notes
        -----
        The dynamic stiffness is calculated using the soil lookup tables for sand and clay.

        Examples
        --------
        >>> total_outer_diameter = [0.3221, 0.4719]
        >>> specific_mass_ratio = [1.78291962, 1.41489701]
        >>> soil_type = ["Medium Sand", "Stiff Clay"]
        >>> spanning = PSIDynamic(
        ...     total_outer_diameter=total_outer_diameter,
        ...     specific_mass_ratio=specific_mass_ratio,
        ...     soil_type=soil_type
        ... )
        >>> np.round(spanning.dynamic_stiffness_horizontal(), 1)
        array([14576004.9,  5130208.5])
        """
        tod = self.total_outer_diameter
        specific_mass_ratio = self.specific_mass_ratio
        properties = self.soil_properties()
        cl = properties["Cl"]
        soil_poisson = properties["soil_poisson"]

        return cl * (1.0 + soil_poisson) * (2.0 * specific_mass_ratio / 3.0 + 1.0 / 3.0) * tod**0.5

    def dynamic_stiffness_vertical(self):
        """
        Calculate the vertical dynamic stiffness of the pipe based on soil type.

        Returns
        -------
        k_vert_dynamic : np.ndarray
            Vertical dynamic stiffness.

        Raises
        ------
        ValueError
            If the soil type is not supported.

        Notes
        -----
        The dynamic stiffness is calculated using the soil lookup tables for sand and clay.

        Examples
        --------
        >>> total_outer_diameter = [0.3221, 0.4719]
        >>> specific_mass_ratio = [1.78291962, 1.41489701]
        >>> soil_type = ["Medium Sand", "Stiff Clay"]
        >>> spanning = PSIDynamic(
        ...     total_outer_diameter=total_outer_diameter,
        ...     specific_mass_ratio=specific_mass_ratio,
        ...     soil_type=soil_type
        ... )
        >>> np.round(spanning.dynamic_stiffness_vertical(), 1)
        array([19268564.9,  7892628.5])
        """
        tod = self.total_outer_diameter
        specific_mass_ratio = self.specific_mass_ratio
        properties = self.soil_properties()
        cv = properties["Cv"]
        soil_poisson = properties["soil_poisson"]
        return cv / (1.0 - soil_poisson) * (2.0 * specific_mass_ratio / 3.0 + 1.0 / 3.0) * tod**0.5

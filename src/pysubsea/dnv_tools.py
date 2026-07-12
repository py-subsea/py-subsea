'''
This module provides classes and functions for calculating DNV pipeline limit states, material
properties, and table-based soil parameters.

**Features:**

- The `DNVGeneral` class implements calculations for temperature derating, yield and tensile
  strength, and characteristic material burst strength, supporting both scalar and array-based
  inputs.
- The `DNVLimitStates` class extends `DNVGeneral` and provides burst pressure calculations for
    pipelines according to DNV standards.
- The `DNVSpanning` class returns the quantities from the attached DNV soil lookup tables for
    sand, clay, and clay L/D factors.
- Designed for use in subsea pipeline and riser engineering, but general enough for any DNV-based
  pipeline property calculations.

All calculations are vectorized using NumPy for efficiency and flexibility.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

'''

import numpy as np
from .linepipe_tools import Pipe

class DNVGeneral: # pylint: disable=too-many-instance-attributes, too-many-arguments
    """
    Base class for DNV pipeline limit state calculations. Provides methods for temperature
    derating, yield and tensile strength, and characteristic material burst strength,
    supporting both scalar and array-based inputs.

    Parameters
    ----------
    outer_diameter : float or array-like, optional
        The outer diameter of the pipeline.
    corroded_wall_thickness : float or array-like, optional
        The corroded wall thickness of the pipeline.
    material : float or array-like, optional
        Material types: 1 for 'CMn' or '13CR', 2 for '22Cr' or '25CR'.
    smys : float or array-like, optional
        Specified minimum yield strengths.
    smts : float or array-like, optional
        Specified minimum tensile strengths.
    temperature : float or array-like, optional
        Temperatures for calculations.
    material_strength_factor : float or array-like, optional
        Material strength factor.

    Notes
    -----
    All calculations are vectorized using NumPy for efficiency and flexibility.
    """

    def __init__(
            self,
            *,
            outer_diameter=0.0,
            corroded_wall_thickness=0.0,
            material=None,
            smys=0.0,
            smts=0.0,
            temperature=0.0,
            material_strength_factor=0.0
        ):
        """
        Initialize with material, strength, and geometric properties.
        """
        self.outer_diameter = np.asarray(outer_diameter, dtype = float)
        self.corroded_wall_thickness = np.asarray(corroded_wall_thickness, dtype = float)
        self.material = np.asarray(material, dtype = float)
        self.smys = np.asarray(smys, dtype = float)
        self.smts = np.asarray(smts, dtype = float)
        self.temperature = np.asarray(temperature, dtype = float)
        self.material_strength_factor = np.asarray(material_strength_factor, dtype = float)

    def temperature_derating_stress(self):
        """
        Calculate the temperature derating stress of a material.

        Returns
        -------
        temperature_derated_stress : np.ndarray
            The derating stress values for the given materials and temperatures.

        Raises
        ------
        ValueError
            If a material is not supported.

        Examples
        --------
        >>> materials = np.array([1, 1, 2, 2])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> dnv = DNVGeneral(
        ...     material=materials, 
        ...     temperature=temperatures
        ... )
        >>> dnv.temperature_derating_stress()
        array([18000000., 34000000., 70000000., 95000000.])
        """
        derating_array = np.empty(0)
        for mat, temp in zip(self.material, self.temperature):
            if mat == 1:
                derating_value = np.interp(temp,
                                           [50.0, 100.0, 200.0],
                                           [0.0, 30.0E+06, 70.0E+06])
            elif mat == 2:
                derating_value = np.interp(temp,
                                           [20.0, 50.0, 100.0, 200.0],
                                           [0.0, 40.0E+06, 90.0E+06, 140.0E+06])
            else:
                raise ValueError('Material not supported')
            derating_array = np.append(derating_array, derating_value)
        return derating_array

    def yield_stress(self):
        """
        Calculate the yield stress of a material.

        Returns
        -------
        yield_stress : np.ndarray
            The yield stress values of the materials at the given temperatures and strength factor.

        Examples
        --------
        >>> materials = np.array([1, 1, 2, 2])
        >>> smys = np.array([450.0E+06, 450.0E+06, 550.0E+06, 550.0E+06])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> material_strength_factor = np.array([0.96, 0.96, 0.96, 0.96])
        >>> dnv = DNVGeneral(
        ...     material=materials,
        ...     smys=smys,
        ...     temperature=temperatures,
        ...     material_strength_factor=material_strength_factor
        ... )
        >>> dnv.yield_stress()
        array([4.1472e+08, 3.9936e+08, 4.6080e+08, 4.3680e+08])
        """
        derating_value = self.temperature_derating_stress()
        return (self.smys - derating_value) * self.material_strength_factor

    def tensile_strength(self):
        """
        Calculate the tensile strength of a material.

        Returns
        -------
        tensile_strength : np.ndarray
            The tensile strength values of the materials at the given
            temperatures and strength factor.

        Examples
        --------
        >>> materials = np.array([1, 1, 2, 2])
        >>> smts = np.array([485.0E+06, 485.0E+06, 590.0E+06, 590.0E+06])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> material_strength_factor = np.array([0.96, 0.96, 0.96, 0.96])
        >>> dnv = DNVGeneral(
        ...     material=materials,
        ...     smts=smts,
        ...     temperature=temperatures,
        ...     material_strength_factor=material_strength_factor
        ... )
        >>> dnv.tensile_strength()
        array([4.4832e+08, 4.3296e+08, 4.9920e+08, 4.7520e+08])
        """
        derating_value = self.temperature_derating_stress()
        return (self.smts - derating_value) * self.material_strength_factor

    def characteristic_material_burst_strength(self):
        """
        Calculate the characteristic material burst strength.

        Returns
        -------
        characteristic_burst_strength : np.ndarray
            The characteristic material burst strength values at the given
            temperatures and strength factor.

        Examples
        --------
        >>> materials = np.array([1, 1, 2, 2])
        >>> smys = np.array([450.0E+06, 450.0E+06, 550.0E+06, 550.0E+06])
        >>> smts = np.array([600.0E+06, 600.0E+06, 700.0E+06, 700.0E+06])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> material_strength_factor = np.array([0.96, 0.96, 0.96, 0.96])
        >>> dnv = DNVGeneral(
        ...     material=materials,
        ...     smys=smys,
        ...     smts=smts,
        ...     temperature=temperatures,
        ...     material_strength_factor=material_strength_factor
        ... )
        >>> dnv.characteristic_material_burst_strength()
        array([4.1472e+08, 3.9936e+08, 4.6080e+08, 4.3680e+08])
        """
        yield_stress_value = self.yield_stress()
        tensile_strength_value = self.tensile_strength()
        return np.minimum(yield_stress_value, tensile_strength_value / 1.15)


class DNVLimitStates(DNVGeneral):
    """
    Class for DNV pipeline burst pressure limit state calculations.

    Extends `DNVGeneral` to provide burst pressure calculations for corroded pipelines
    according to DNV standards, using material, geometric, and strength properties.

    Parameters
    ----------
    outer_diameter : float or array-like, optional
        The outer diameter of the pipeline.
    corroded_wall_thickness : float or array-like, optional
        The corroded wall thickness of the pipeline.
    material : float or array-like, optional
        Material types: 1 for 'CMn' or '13CR', 2 for '22Cr' or '25CR'.
    smys : float or array-like, optional
        Specified minimum yield strengths.
    smts : float or array-like, optional
        Specified minimum tensile strengths.
    temperature : float or array-like, optional
        Temperatures for calculations.
    material_strength_factor : float or array-like, optional
        Material strength factor.

    Notes
    -----
    All parameters are passed to the parent class `DNVGeneral`.
    """

    def burst_pressure(self):
        """
        Calculate the burst pressure of a pipeline.

        Returns
        -------
        burst_pressure : np.ndarray
            The burst pressure values of the pipeline.

        Raises
        ------
        ValueError
            If a material is not supported.

        Examples
        --------
        >>> outer_diameter = np.array([0.2731, 0.3239, 0.2731, 0.3239])
        >>> corroded_wall_thickness = np.array([0.0097, 0.0129, 0.0097, 0.0129])
        >>> materials = np.array([1, 1, 2, 2])
        >>> smys = np.array([450.0E+06, 450.0E+06, 550.0E+06, 550.0E+06])
        >>> smts = np.array([600.0E+06, 600.0E+06, 700.0E+06, 700.0E+06])
        >>> temperatures = np.array([80.0, 110.0, 80.0, 110.0])
        >>> material_strength_factor = np.array([0.96, 0.96, 0.96, 0.96])
        >>> dnv = DNVLimitStates(
        ...     outer_diameter=outer_diameter,
        ...     corroded_wall_thickness=corroded_wall_thickness,
        ...     material=materials,
        ...     smys=smys,
        ...     smts=smts,
        ...     temperature=temperatures,
        ...     material_strength_factor=material_strength_factor
        ... )
        >>> dnv.burst_pressure()
        array([35270393.70222808, 38255444.18258572, 39189326.33580898, 41841892.07470313])
        """
        fcb = self.characteristic_material_burst_strength()
        return (
            (2.0 * self.corroded_wall_thickness)
            / (self.outer_diameter - self.corroded_wall_thickness)
            * fcb * 2.0 / np.sqrt(3.0)
        )


class DNVSpanning:
    """
    Class for DNV pipeline spanning calculations.

    Parameters
    ----------
    total_outer_diameter : float or array-like, optional
        Total outer diameter of the pipe. Default is 0.
    water_density : float or array-like, optional
        Density of water. Default is 0.
    submerged_weight : float or array-like, optional
        Submerged weight of the pipe. Default is 0.
    soil_type : str or array-like, optional
        Soil type for lookup: 'Loose Sand', 'Medium Sand', 'Dense Sand',
        'Very Soft Clay', 'Soft Clay', 'Firm Clay', 'Stiff Clay',
        'Very Stiff Clay', or 'Hard Clay'. Default is None.

    Notes
    -----
    All inputs support scalar and array-like values. When arrays are supplied,
    NumPy broadcasting rules apply.

    Examples
    --------
    >>> spanning = DNVSpanning(
    ...     total_outer_diameter=[0.2791, 0.3299],
    ...     water_density=[1025.0, 1025.0],
    ...     submerged_weight=[695.39794758, 1029.76124826],
    ...     soil_type=["Medium Sand", "Stiff Clay"]
    ... )
    >>> spanning.specific_mass_ratio()
    array([1.1307..., 1.1984...])
    >>> spanning.dynamic_stiffness_horizontal()
    array([9692100.2..., 3677788.3...])
    >>> spanning.dynamic_stiffness_vertical()
    array([12812348.9...,  5321131.0...])
    """

    SOIL_PROPERTIES = {
        "Loose Sand": {
            "Cv": 10500.0E+03,
            "Cl": 9000.0E+03,
            "Kv": 250.0E+03,
            "soil_poisson": 0.35,
        },
        "Medium Sand": {
            "Cv": 14500.0E+03,
            "Cl": 12500.0E+03,
            "Kv": 530.0E+03,
            "soil_poisson": 0.35,
        },
        "Dense Sand": {
            "Cv": 21000.0E+03,
            "Cl": 18000.0E+03,
            "Kv": 1350.0E+03,
            "soil_poisson": 0.35,
        },
        "Very Soft Clay": {
            "Cv": 600.0E+03,
            "Cl": 500.0E+03,
            "Kv": 100.0E+03,
            "soil_poisson": 0.45,
        },
        "Soft Clay": {
            "Cv": 1400.0E+03,
            "Cl": 1200.0E+03,
            "Kv": 260.0E+03,
            "soil_poisson": 0.45,
        },
        "Firm Clay": {
            "Cv": 3000.0E+03,
            "Cl": 2600.0E+03,
            "Kv": 800.0E+03,
            "soil_poisson": 0.45,
        },
        "Stiff Clay": {
            "Cv": 4500.0E+03,
            "Cl": 3900.0E+03,
            "Kv": 1600.0E+03,
            "soil_poisson": 0.45,
        },
        "Very Stiff Clay": {
            "Cv": 11000.0E+03,
            "Cl": 9500.0E+03,
            "Kv": 3000.0E+03,
            "soil_poisson": 0.45,
        },
        "Hard Clay": {
            "Cv": 12000.0E+03,
            "Cl": 10500.0E+03,
            "Kv": 4200.0E+03,
            "soil_poisson": 0.45,
        },
    }

    def __init__(
            self,
            *,
            total_outer_diameter=0.0,
            water_density=0.0,
            submerged_weight=0.0,
            soil_type=None
        ):
        """
        Initialize a DNVSpanning object with pipe and soil properties.
        """
        self.total_outer_diameter = np.asarray(total_outer_diameter, dtype = float)
        self.water_density = np.asarray(water_density, dtype = float)
        self.submerged_weight = np.asarray(submerged_weight, dtype = float)
        self.soil_type = np.asarray(soil_type, dtype = object)

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
        values = np.empty(flat_soil_types.shape[0], dtype = float)

        for i, soil in enumerate(flat_soil_types):
            try:
                values[i] = self.SOIL_PROPERTIES[soil][property_name]
            except KeyError as exc:
                raise ValueError(
                    "Unsupported soil type. Expected one of: "
                    + ", ".join(self.SOIL_PROPERTIES.keys())
                ) from exc

        return values.reshape(self.soil_type.shape)

    def specific_mass_ratio(self):
        """
        Calculate the specific mass ratio of the pipe.

        Returns
        -------
        specific_mass_ratio : np.ndarray
            The specific mass ratio of the pipe.

        Notes
        -----
        The specific mass ratio is calculated as the ratio of the submerged weight to the product
        of the water density and the total outer diameter of the pipe.
        """
        pipe = Pipe(
            outer_diameter=self.total_outer_diameter
        )
        total_outer_area = pipe.total_outer_area()
        return self.submerged_weight / (9.807 * self.water_density * total_outer_area)

    def soil_properties(self):
        """
        Return lookup properties for the configured soil type(s).

        Returns
        -------
        dict
            Dictionary with keys ``Cv``, ``Cl``, ``Kv``, and ``soil_poisson``.
        """
        return {
            "Cv": self._lookup_soil_property("Cv"),
            "Cl": self._lookup_soil_property("Cl"),
            "Kv": self._lookup_soil_property("Kv"),
            "soil_poisson": self._lookup_soil_property("soil_poisson"),
        }

    def dynamic_stiffness_horizontal(self):
        """
        Calculate the dynamic stiffness of the pipe based on soil type.

        Returns
        -------
        k_horiz_dynamic : float or array-like
            Horizontal dynamic stiffness.

        Raises
        ------
        ValueError
            If the soil type is not supported.

        Notes
        -----
        The dynamic stiffness is calculated using the DNV soil lookup tables for sand and clay.
        """
        specific_mass_ratio = self.specific_mass_ratio()
        tod = self.total_outer_diameter
        properties = self.soil_properties()
        cl = properties["Cl"]
        soil_poisson = properties["soil_poisson"]
        return cl * (1.0 + soil_poisson) * (2.0 * specific_mass_ratio / 3.0 + 1.0 / 3.0) * tod**0.5

    def dynamic_stiffness_vertical(self):
        """
        Calculate the dynamic stiffness of the pipe based on soil type.

        Returns
        -------
        k_vert_dynamic : float or array-like
            Vertical dynamic stiffness.

        Raises
        ------
        ValueError
            If the soil type is not supported.

        Notes
        -----
        The dynamic stiffness is calculated using the DNV soil lookup tables for sand and clay.
        """
        specific_mass_ratio = self.specific_mass_ratio()
        tod = self.total_outer_diameter
        properties = self.soil_properties()
        cv = properties["Cv"]
        soil_poisson = properties["soil_poisson"]
        return cv / (1.0 - soil_poisson) * (2.0 * specific_mass_ratio / 3.0 + 1.0 / 3.0) * tod**0.5

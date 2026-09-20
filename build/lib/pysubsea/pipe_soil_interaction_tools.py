"""
This module provides classes and functions for calculating the capacity of soils using various
models for a given pipe and soil configuration.

**Features:**

- The `PSI` class implements soil capacity calculations for different pipe and soil properties,
  supporting vectorized and model-based approaches.
- Designed for use in subsea pipeline and riser engineering, but general enough for any
  pipe-soil interaction analysis.
- All calculations are vectorized using NumPy for efficiency and flexibility.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

"""

import numpy as np

class PSI: # pylint: disable=too-many-arguments
    """
    Class for calculating the capacity of soils using various models
    for a given pipe and soil configuration.

    Parameters
    ----------
    total_outer_diameter : float, optional
        Total outer diameter of the pipe, including coating.
    surface_roughness : str, optional
        Surface roughness of the pipe ('Smooth' or 'Rough').
    undrained_shear_strength_at_seabed : float, optional
        Undrained shear strength at the seabed, Su,0, in Pa.
    undrained_shear_strength_gradient : float, optional
        Gradient of undrained shear strength with depth, in Pa/m.
    submerged_unit_weight : float, optional
        Submerged unit weight of the soil, gamma', in N/m3.
    """
    def __init__(
            self,
            *,
            total_outer_diameter=0.0,
            surface_roughness=None,
            undrained_shear_strength_at_seabed=0.0,
            undrained_shear_strength_gradient=0.0,
            submerged_unit_weight=0.0
        ):
        """
        Initialize a PipeSoilInteraction object with pipe and soil properties.
        """
        self.total_outer_diameter =  np.asarray(total_outer_diameter, dtype = float)
        self.surface_roughness =  np.asarray(surface_roughness, dtype = object)
        self.undrained_shear_strength_gradient = np.asarray(
            undrained_shear_strength_gradient, dtype = float
        )
        self.undrained_shear_strength_at_seabed = np.asarray(
            undrained_shear_strength_at_seabed, dtype = float
        )
        self.submerged_unit_weight = np.asarray(submerged_unit_weight, dtype = float)

    @staticmethod
    def _depth_geometry(outer_diameter):
        '''
        Calculate the depth, width, and penetrated area for a given pipe outer diameter.
        '''
        # Create an array of depth values from 0.001 m to 1.3 times the outer diameter
        # with 200 evenly spaced points.
        depth = np.linspace(0.001, 1.3 * outer_diameter, 200)

        # Calculate the width for a given pipe outer diameter (B).
        width = np.where(
            depth < outer_diameter / 2,
            2 * np.sqrt(np.maximum(outer_diameter * depth - depth ** 2, 0)),
            outer_diameter
        )

        # Calculate the penetrated area for a given pipe outer diameter (Abm)
        penetrated_area = np.where(
            depth < outer_diameter / 2,
            np.arcsin(width / outer_diameter) * outer_diameter ** 2 / 4
            - width * outer_diameter / 4 * np.cos(np.arcsin(width / outer_diameter)),
            np.pi * outer_diameter ** 2 / 8
            + outer_diameter * (depth - outer_diameter / 2)
        )
        return depth, width, penetrated_area

    def _model_inputs(self):
        '''
        Yield shared per-pipe inputs and depth geometry for the undrained models.
        '''
        for i, outer_diameter in enumerate(self.total_outer_diameter):
            depth, width, penetrated_area = self._depth_geometry(outer_diameter)
            yield (
                outer_diameter,
                self.surface_roughness[i],
                self.undrained_shear_strength_gradient[i],
                self.undrained_shear_strength_at_seabed[i],
                self.submerged_unit_weight[i],
                depth,
                width,
                penetrated_area
            )

    @staticmethod
    def _reference_shear_strength(
            outer_diameter,
            depth,
            width,
            shear_strength_gradient,
            seabed_shear_strength
        ):
        '''
        Calculate the reference depth and shear strength for Model 1.
        '''
        # Calculate the reference depth for Model 1 (zsu,0).
        reference_depth = np.where(
            depth < outer_diameter / 2 * (1 - np.sqrt(2) / 2),
            0.0,
            depth + outer_diameter / 2 * (np.sqrt(2) - 1) - width / 2
        )

        # Calculate the reference shear strength for Model 1 (su,0).
        reference_shear_strength = (
            seabed_shear_strength + shear_strength_gradient * reference_depth
        )
        return reference_depth, reference_shear_strength

    @staticmethod
    def _interpolated_friction_factor(
            width,
            shear_strength_gradient,
            seabed_shear_strength,
            surface_roughness
        ):
        '''
        Calculate the interpolated pipe-soil friction factor.
        '''
        friction_factor = np.divide(
            shear_strength_gradient * width,
            seabed_shear_strength,
            out=np.zeros_like(width),
            where=seabed_shear_strength != 0
        )
        friction_factor_reference = np.linspace(0, 16, 17)
        friction_factor_values = np.array(
            [1.00, 1.12, 1.19, 1.24, 1.28, 1.31, 1.34, 1.36, 1.38,
             1.39, 1.40, 1.41, 1.42, 1.43, 1.44, 1.445, 1.45]
            if surface_roughness == 'Smooth' else
            [1.00, 1.23, 1.36, 1.44, 1.50, 1.55, 1.59, 1.61, 1.64,
             1.66, 1.67, 1.69, 1.70, 1.71, 1.72, 1.730, 1.74]
        )
        return np.interp(
            friction_factor,
            friction_factor_reference,
            friction_factor_values
        )

    @staticmethod
    def _depth_correction_factor(
            seabed_shear_strength,
            reference_shear_strength,
            bearing_capacity,
            reference_depth,
            width,
            bearing_capacity_factor=5.14
        ):
        '''
        Calculate the depth correction factor for Model 1.
        '''
        average_shear_strength_above = (
            seabed_shear_strength + reference_shear_strength
        ) / 2
        average_shear_strength_below = (
            bearing_capacity / width / bearing_capacity_factor
        )
        return 0.3 * np.divide(
            average_shear_strength_above,
            average_shear_strength_below,
            out=np.zeros_like(width),
            where=average_shear_strength_below != 0
        ) * np.arctan2(reference_depth, width)

    def downward_undrained_model1(self): # pylint: disable=too-many-locals
        """
        Calculate vertical penetration resistance using undrained Model 1.

        The calculation follows the bearing-capacity formulation in the attached
        PDF. For each pipe, the method evaluates 200 depths from 0.001 m to
        ``1.3 * total_outer_diameter`` and prepends the zero-depth point to the returned arrays. The
        reference shear strength is calculated as ``Su,0 + rho * zsu,0`` and
        the buoyancy contribution uses the supplied submerged unit weight.

        Returns
        -------
        depth_arrays : np.ndarray
            Depth arrays with shape ``(n_pipes, 201)``.
        vertical_bearing_capacity_arrays : np.ndarray
            Vertical penetration resistance arrays with shape
            ``(n_pipes, 201)``, in N/m.
        Examples
        --------
        >>> psi = PSI(
        ...     total_outer_diameter=[0.2731],
        ...     surface_roughness=['Smooth'],
        ...     undrained_shear_strength_gradient=[1000.0],
        ...     undrained_shear_strength_at_seabed=[5000.0],
        ...     submerged_unit_weight=[5500.0]
        ... )
        >>> depths, capacities = psi.downward_undrained_model1()
        >>> depths.shape, capacities.shape, float(depths[0, 0]), round(float(depths[0, -1]), 5), float(capacities[0, 0])
        ((1, 201), (1, 201), 0.0, 0.35503, 0.0)
        """
        depth_arrays = []
        vertical_bearing_capacity_arrays = []

        for (
                outer_diameter,
                surface_roughness,
                shear_strength_gradient,
                seabed_shear_strength,
                submerged_unit_weight,
                depth,
                width,
                penetrated_area
            ) in self._model_inputs():

            # Calculate reference depth and shear strength for Model 1.
            reference_depth, reference_shear_strength = self._reference_shear_strength(
                outer_diameter,
                depth,
                width,
                shear_strength_gradient,
                seabed_shear_strength
            )

            # Calculate the interpolated pipe-soil friction factor based on surface roughness and shear strength.
            friction_factor = self._interpolated_friction_factor(
                width,
                shear_strength_gradient,
                seabed_shear_strength,
                surface_roughness
            )

            # Define the bearing capacity factor for Model 1.
            bearing_capacity_factor = 5.14


            # Calculate the bearing capacity for Model 1.
            bearing_capacity = friction_factor * (
                bearing_capacity_factor *
                reference_shear_strength + shear_strength_gradient * width / 4
            ) * width

            # Calculate the depth correction factor for Model 1.
            depth_correction_factor = self._depth_correction_factor(
                seabed_shear_strength,
                reference_shear_strength,
                bearing_capacity,
                reference_depth,
                width,
                bearing_capacity_factor
            )

            # Calculate the vertical bearing capacity for Model 1.
            vertical_bearing_capacity = (
                bearing_capacity * (1 + depth_correction_factor)
                + submerged_unit_weight * penetrated_area
            )

            # Append the calculated depth and vertical bearing capacity arrays to the results lists.
            depth_arrays.append(np.append(0, depth))
            vertical_bearing_capacity_arrays.append(
                np.append(0, vertical_bearing_capacity)
            )
        return np.array(depth_arrays), np.array(vertical_bearing_capacity_arrays)

    def downward_undrained_model2(self): # pylint: disable=too-many-locals
        """
        Calculate vertical penetration resistance using undrained Model 2.

        Model 2 follows the alternative formulation in the attached PDF. It
        combines the minimum of the two resistance-factor terms with the soil
        buoyancy contribution. For each pipe, the method evaluates 200 depths
        from 0.001 m to ``1.3 * total_outer_diameter`` and prepends the zero-depth
        point to the returned arrays. The shear strength at the pipe invert is calculated as
        ``Su,0 + rho * z``.

        Returns
        -------
        depth_arrays : np.ndarray
            Depth arrays with shape ``(n_pipes, 201)``.
        vertical_bearing_capacity_arrays : np.ndarray
            Vertical penetration resistance arrays with shape
            ``(n_pipes, 201)``, in N/m.

        Examples
        --------
        >>> psi = PSI(
        ...     total_outer_diameter=[0.2731],
        ...     surface_roughness=['Smooth'],
        ...     undrained_shear_strength_gradient=[1000.0],
        ...     undrained_shear_strength_at_seabed=[5000.0],
        ...     submerged_unit_weight=[5500.0]
        ... )
        >>> depths, capacities = psi.downward_undrained_model2()
        >>> depths.shape, capacities.shape, float(depths[0, 0]), round(float(depths[0, -1]), 5), float(capacities[0, 0])
        ((1, 201), (1, 201), 0.0, 0.35503, 0.0)
        """
        depth_arrays = []
        vertical_bearing_capacity_arrays = []

        for (
                outer_diameter,
                _,
                shear_strength_gradient,
                seabed_shear_strength,
                submerged_unit_weight,
                depth,
                _,
                penetrated_area
            ) in self._model_inputs():

            # Calculate the shear strength at the pipe invert for Model 2.
            shear_strength = seabed_shear_strength + shear_strength_gradient * depth

            # Calculate the resistance factor for Model 2 based on depth and outer diameter.
            resistance_factor = np.minimum(
                6 * (depth / outer_diameter) ** 0.25,
                3.4 * (10 * depth / outer_diameter) ** 0.5
            )

            # Calculate the vertical bearing capacity for Model 2.
            vertical_bearing_capacity = (
                resistance_factor
                + np.divide(
                    1.5 * submerged_unit_weight * penetrated_area,
                    outer_diameter * shear_strength,
                    out=np.zeros_like(depth),
                    where=shear_strength != 0
                )
            ) * outer_diameter * shear_strength

            # Append the calculated depth and vertical bearing capacity arrays to the results lists.
            depth_arrays.append(np.append(0, depth))
            vertical_bearing_capacity_arrays.append(
                np.append(0, vertical_bearing_capacity)
            )

        return np.array(depth_arrays), np.array(vertical_bearing_capacity_arrays)

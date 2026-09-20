'''
This module provides classes and functions for lateral buckling calculations and friction factor
distribution fitting for subsea pipelines.

**Features:**

- The `LBForceDistributions` class calculates lateral buckling forces.
- The `LBSoilDistributions` class implements lognormal distribution fitting for geotechnical
  friction factors, supporting low, best, and high estimates (LE, BE, HE) and multiple fit
  types.
  Designed for use in pipeline lateral buckling reliability analysis and geotechnical parameter
  estimation.
- All calculations are vectorized using NumPy and leverage SciPy for statistical fitting.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

'''

import numpy as np
from scipy.stats import lognorm
from scipy.optimize import minimize
from .linepipe_tools import Pipe

class LBForceDistributions: # pylint: disable=too-many-instance-attributes, too-many-arguments
    """
    Class for lateral buckling force calculations.

    Parameters
    ----------
    oos_section_type : str or array-like, optional
        Out-of-straightness (OOS) section type: 'straight', 'curve', or 'sleeper'.
    oos_factor_mean : float or array-like, optional
        Mean OOS factor for the condition of interest.
    oos_factor_std : float or array-like, optional
        Standard deviation of the OOS factor for the condition of interest.
    oos_reference_length : float or array-like, optional
        Reference length for the OOS section.
    friction_factor_mean : float or array-like, optional
        Mean friction factor for the condition of interest.
    friction_factor_std : float or array-like, optional
        Standard deviation of the friction factor for the condition of interest.
    outer_diameter : float or array-like, optional
        Pipe outer diameter, used to compute section properties from `Pipe`.
    wall_thickness : float or array-like, optional
        Pipe wall thickness, used to compute section properties from `Pipe`.
    youngs_modulus : float or array-like, optional
        Young's modulus of the material.
    submerged_weight : float or array-like, optional
        Submerged weight for the condition of interest.
    curve_radius : float or array-like, optional
        Curve radius for the OOS section, if applicable.
    sleeper_height : float or array-like, optional
        Sleeper height for the OOS section, if applicable.
    """

    def __init__(
            self,
            *,
            oos_section_type=None,
            oos_factor_mean=0.0,
            oos_factor_std=0.0,
            oos_reference_length=0.0,
            friction_factor_mean=0.0,
            friction_factor_std=0.0,
            outer_diameter=0.0,
            wall_thickness=0.0,
            youngs_modulus=0.0,
            submerged_weight=0.0,
            curve_radius=0.0,
            sleeper_height=0.0
        ):
        """
        Initialize with section, material, and submerged weight properties.
        """
        self.oos_section_type = np.asarray(oos_section_type, dtype = object)
        self.oos_factor_mean = np.asarray(oos_factor_mean, dtype = float)
        self.oos_factor_std = np.asarray(oos_factor_std, dtype = float)
        self.oos_reference_length = np.asarray(oos_reference_length, dtype = object)
        self.friction_factor_mean = np.asarray(friction_factor_mean, dtype = object)
        self.friction_factor_std = np.asarray(friction_factor_std, dtype = object)
        self.outer_diameter = np.asarray(outer_diameter, dtype = float)
        self.wall_thickness = np.asarray(wall_thickness, dtype = float)
        self.youngs_modulus = np.asarray(youngs_modulus, dtype = float)
        self.submerged_weight = np.asarray(submerged_weight, dtype = float)
        self.curve_radius = np.asarray(curve_radius, dtype = object)
        self.sleeper_height = np.asarray(sleeper_height, dtype = object)

    def _section_properties(self):
        """
        Calculate the steel cross-sectional area and area moment of inertia from `Pipe`.

        Returns
        -------
        steel_area : np.ndarray
            Steel cross-sectional area.
        area_moment_inertia : np.ndarray
            Area moment of inertia.
        """
        pipe = Pipe(
            outer_diameter=self.outer_diameter,
            wall_thickness=self.wall_thickness,
            youngs_modulus=self.youngs_modulus
        )
        steel_area = pipe.steel_area()
        bending_stiffness = pipe.bending_stiffness()

        return steel_area, bending_stiffness

    def characteristic_buckling_force(self):
        """
        Compute characteristic buckling force.

        Returns
        -------
        characteristic_buckling_force : np.ndarray
            Characteristic lateral buckling force.

        Examples
        --------
        >>> lb = LBForceDistributions(
        ...     outer_diameter=[0.2731, 0.3239],
        ...     wall_thickness=[0.0127, 0.0159],
        ...     youngs_modulus=[207.0e+09, 207.0e+09],
        ...     submerged_weight=[695.39794758, 1029.76124826]
        ... )
        >>> lb.characteristic_buckling_force()
        array([ 839099.6561..., 1351458.0306...])
        """
        steel_area, bending_stiffness = self._section_properties()
        return (
            2.26
            * (self.youngs_modulus * steel_area) ** 0.25
            * bending_stiffness ** 0.25
            * self.submerged_weight ** 0.5
        )

    def nominal_straight_section_buckling_force(self):
        """
        Compute the mean nominal straight-section buckling force.

        This is calculated as the product of the mean OOS factor, the square root of the
        mean friction factor, and the characteristic buckling force.
        """
        return (
            self.oos_factor_mean
            * np.sqrt(self.friction_factor_mean)
            * self.characteristic_buckling_force()
        )

    @staticmethod
    def _sqrt_lognorm_moments(mean_value, std_value):
        """
        Compute mean and standard deviation of sqrt(X) from mean and std of lognormal X.
        """
        sigma2_ln = np.log(1.0 + (std_value**2) / (mean_value**2))
        mu_ln = np.log(mean_value) - 0.5 * sigma2_ln

        sqrt_mean = np.exp(0.5 * mu_ln + 0.125 * sigma2_ln)
        sqrt_var = np.exp(mu_ln + 0.25 * sigma2_ln) * (np.exp(0.25 * sigma2_ln) - 1.0)
        sqrt_std = np.sqrt(np.maximum(sqrt_var, 0.0))

        return sqrt_mean, sqrt_std

    def route_curve_buckling_force(self):
        """
        Compute the mean route-curve buckling force.

        This is calculated as the product of the mean OOS factor, the mean friction factor,
        the submerged weight, and the curve radius.
        """
        return (
            self.oos_factor_mean
            * self.friction_factor_mean
            * self.submerged_weight
            * self.curve_radius
        )

    def sleeper_buckling_force(self):
        """
        Compute the mean sleeper buckling force.

        This is calculated as the product of the mean OOS factor and
        ``4 * sqrt(bending_stiffness * submerged_weight / sleeper_height)``.
        """
        _, bending_stiffness = self._section_properties()
        return (
            self.oos_factor_mean
            * 4.0
            * np.sqrt(
                bending_stiffness * self.submerged_weight / self.sleeper_height
            )
        )

    @staticmethod
    def _lognorm_parameters(mean_value, std_value):
        """
        Compute lognormal location and scale parameters from mean and standard deviation.
        """
        scale_param = np.sqrt(np.log(1 + std_value**2 / mean_value**2))
        location_param = np.log(mean_value**2 / np.sqrt(mean_value**2 + std_value**2))
        return location_param, scale_param

    @staticmethod
    def _fitted_values(location_param, scale_param, scale=1.0):
        """
        Compute LE/BE/HE fitted values from lognormal parameters.
        """
        le_fit = scale * lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
        be_fit = scale * lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
        he_fit = scale * lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)
        return le_fit, be_fit, he_fit

    @staticmethod
    def _calc_lognorm_product_distribution(mean_value, std_value):
        """
        Compute a lognormal distribution curve from mean and standard deviation.

        Returns
        -------
        distribution_range : np.ndarray
            Range spanning the 0.01% to 99.99% quantiles.
        distribution_cdf : np.ndarray
            CDF values corresponding to the returned range.
        distribution_pdf : np.ndarray
            PDF values corresponding to the returned range.
        """
        location_param, scale_param = LBForceDistributions._lognorm_parameters(
            mean_value, std_value
        )

        lower = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.0001)
        upper = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.9999)

        distribution_range = np.linspace(lower, upper, 10000)
        distribution_cdf = lognorm.cdf(
            distribution_range,
            scale_param,
            0.0,
            np.exp(location_param)
        )
        distribution_pdf = lognorm.pdf(
            distribution_range,
            scale_param,
            0.0,
            np.exp(location_param)
        )

        return distribution_range, distribution_cdf, distribution_pdf

    def _single_case_product_distribution(self, mean_value, std_value):
        """
        Compute one distribution from a mean and standard deviation.
        """
        location_param, scale_param = self._lognorm_parameters(mean_value, std_value)
        le_fit, be_fit, he_fit = self._fitted_values(location_param, scale_param)
        (
            distribution_range,
            distribution_cdf,
            distribution_pdf,
        ) = self._calc_lognorm_product_distribution(
            mean_value,
            std_value
        )

        return (
            mean_value,
            std_value,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            distribution_range,
            distribution_cdf,
            distribution_pdf
        )

    def nominal_straight_buckling_force_distribution_parameters(self):
        """
        Compute nominal straight-section buckling force distribution parameters.

        The nominal straight-section buckling force is treated as the product of the OOS factor,
        the square root of friction factor, and the characteristic buckling force.

        Returns
        -------
        mean_nominal_straight_section_buckling : np.ndarray
            Array of mean nominal straight-section buckling force values.
        std_nominal_straight_section_buckling : np.ndarray
            Array of standard deviation values.
        location_param : np.ndarray
            Array of location parameters of the lognormal distribution.
        scale_param : np.ndarray
            Array of scale parameters of the lognormal distribution.
        le_fit : np.ndarray
            Array of fitted 5th-percentile values.
        be_fit : np.ndarray
            Array of fitted 50th-percentile values.
        he_fit : np.ndarray
            Array of fitted 95th-percentile values.
        nominal_straight_section_buckling_range : np.ndarray
            2D array with shape (n_cases, 10000), one range per case.
        nominal_straight_section_buckling_cdf : np.ndarray
            2D array with shape (n_cases, 10000), one CDF per case.
        nominal_straight_section_buckling_pdf : np.ndarray
            2D array with shape (n_cases, 10000), one PDF per case.

        Notes
        -----
        This method mirrors the output structure of `LBOOSDistributions`, but the mean and
        standard deviation are propagated through the product of OOS factor, friction factor,
        and characteristic buckling force instead of being fitted from discrete estimates.
        """
        mean_value_list = []
        std_value_list = []
        location_param_list = []
        scale_param_list = []
        le_fit_list = []
        be_fit_list = []
        he_fit_list = []
        nominal_straight_section_buckling_range_list = []
        nominal_straight_section_buckling_cdf_list = []
        nominal_straight_section_buckling_pdf_list = []

        characteristic_force = self.characteristic_buckling_force()

        for oos_factor_mean, oos_factor_std in zip(
            self.oos_factor_mean,
            self.oos_factor_std
        ):
            sqrt_friction_mean, sqrt_friction_std = self._sqrt_lognorm_moments(
                self.friction_factor_mean,
                self.friction_factor_std
            )

            mean_value = characteristic_force * oos_factor_mean * sqrt_friction_mean
            variance_factor = (
                (oos_factor_std**2 + oos_factor_mean**2)
                * (sqrt_friction_std**2 + sqrt_friction_mean**2)
                - (oos_factor_mean**2 * sqrt_friction_mean**2)
            )
            variance_factor = np.maximum(variance_factor, 0.0)
            std_value = characteristic_force * np.sqrt(variance_factor)

            (
                mean_value,
                std_value,
                location_param,
                scale_param,
                le_fit,
                be_fit,
                he_fit,
                nominal_straight_section_buckling_range,
                nominal_straight_section_buckling_cdf,
                nominal_straight_section_buckling_pdf
            ) = self._single_case_product_distribution(mean_value, std_value)

            mean_value_list.append(mean_value)
            std_value_list.append(std_value)
            location_param_list.append(location_param)
            scale_param_list.append(scale_param)
            le_fit_list.append(le_fit)
            be_fit_list.append(be_fit)
            he_fit_list.append(he_fit)
            nominal_straight_section_buckling_range_list.append(
                nominal_straight_section_buckling_range
            )
            nominal_straight_section_buckling_cdf_list.append(
                nominal_straight_section_buckling_cdf
            )
            nominal_straight_section_buckling_pdf_list.append(
                nominal_straight_section_buckling_pdf
            )

        mean_value = np.array(mean_value_list)
        std_value = np.array(std_value_list)
        location_param = np.array(location_param_list)
        scale_param = np.array(scale_param_list)
        le_fit = np.array(le_fit_list)
        be_fit = np.array(be_fit_list)
        he_fit = np.array(he_fit_list)
        nominal_straight_section_buckling_range = np.array(
            nominal_straight_section_buckling_range_list
        )
        nominal_straight_section_buckling_cdf = np.array(
            nominal_straight_section_buckling_cdf_list
        )
        nominal_straight_section_buckling_pdf = np.array(
            nominal_straight_section_buckling_pdf_list
        )

        return (
            mean_value,
            std_value,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            nominal_straight_section_buckling_range,
            nominal_straight_section_buckling_cdf,
            nominal_straight_section_buckling_pdf
        )

    def route_curve_buckling_force_distribution_parameters(self):
        """
        Compute route-curve buckling forcedistribution parameters.

        The route-curve buckling force is treated as the product of the OOS factor,
        the friction factor, the submerged weight, and the curve radius.

        Returns
        -------
        mean_route_curve_buckling : np.ndarray
            Array of mean route-curve buckling force values.
        std_route_curve_buckling : np.ndarray
            Array of standard deviation values.
        location_param : np.ndarray
            Array of location parameters of the lognormal distribution.
        scale_param : np.ndarray
            Array of scale parameters of the lognormal distribution.
        le_fit : np.ndarray
            Array of fitted 5th-percentile values.
        be_fit : np.ndarray
            Array of fitted 50th-percentile values.
        he_fit : np.ndarray
            Array of fitted 95th-percentile values.
        route_curve_buckling_range : np.ndarray
            2D array with shape (n_cases, 10000), one range per case.
        route_curve_buckling_cdf : np.ndarray
            2D array with shape (n_cases, 10000), one CDF per case.
        route_curve_buckling_pdf : np.ndarray
            2D array with shape (n_cases, 10000), one PDF per case.

        Notes
        -----
        This method mirrors the output structure of `LBOOSDistributions`, but the mean and
        standard deviation are propagated through the product of OOS factor, friction factor,
        submerged weight, and curve radius instead of being fitted from discrete estimates.
        """
        mean_value_list = []
        std_value_list = []
        location_param_list = []
        scale_param_list = []
        le_fit_list = []
        be_fit_list = []
        he_fit_list = []
        route_curve_buckling_range_list = []
        route_curve_buckling_cdf_list = []
        route_curve_buckling_pdf_list = []

        for oos_factor_mean, oos_factor_std in zip(
            self.oos_factor_mean,
            self.oos_factor_std
        ):
            mean_value = (
                oos_factor_mean
                * self.friction_factor_mean
                * self.submerged_weight
                * self.curve_radius
            )
            variance_factor = (
                (oos_factor_std**2 + oos_factor_mean**2)
                * (self.friction_factor_std**2 + self.friction_factor_mean**2)
                - (oos_factor_mean**2 * self.friction_factor_mean**2)
            )
            variance_factor = np.maximum(variance_factor, 0.0)
            std_value = self.submerged_weight * self.curve_radius * np.sqrt(variance_factor)

            (
                mean_value,
                std_value,
                location_param,
                scale_param,
                le_fit,
                be_fit,
                he_fit,
                route_curve_buckling_range,
                route_curve_buckling_cdf,
                route_curve_buckling_pdf
            ) = self._single_case_product_distribution(mean_value, std_value)

            mean_value_list.append(mean_value)
            std_value_list.append(std_value)
            location_param_list.append(location_param)
            scale_param_list.append(scale_param)
            le_fit_list.append(le_fit)
            be_fit_list.append(be_fit)
            he_fit_list.append(he_fit)
            route_curve_buckling_range_list.append(route_curve_buckling_range)
            route_curve_buckling_cdf_list.append(route_curve_buckling_cdf)
            route_curve_buckling_pdf_list.append(route_curve_buckling_pdf)

        mean_value = np.array(mean_value_list)
        std_value = np.array(std_value_list)
        location_param = np.array(location_param_list)
        scale_param = np.array(scale_param_list)
        le_fit = np.array(le_fit_list)
        be_fit = np.array(be_fit_list)
        he_fit = np.array(he_fit_list)
        route_curve_buckling_range = np.array(route_curve_buckling_range_list)
        route_curve_buckling_cdf = np.array(route_curve_buckling_cdf_list)
        route_curve_buckling_pdf = np.array(route_curve_buckling_pdf_list)

        return (
            mean_value,
            std_value,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            route_curve_buckling_range,
            route_curve_buckling_cdf,
            route_curve_buckling_pdf
        )

    def sleeper_buckling_force_distribution_parameters(self):
        """
        Compute sleeper buckling force distribution parameters.

        The sleeper buckling force is treated as:
        ``oos_factor * 4 * sqrt(bending_stiffness * submerged_weight / sleeper_height)``.

        Returns
        -------
        mean_sleeper_buckling : np.ndarray
            Array of mean sleeper buckling force values.
        std_sleeper_buckling : np.ndarray
            Array of standard deviation values.
        location_param : np.ndarray
            Array of location parameters of the lognormal distribution.
        scale_param : np.ndarray
            Array of scale parameters of the lognormal distribution.
        le_fit : np.ndarray
            Array of fitted 5th-percentile values.
        be_fit : np.ndarray
            Array of fitted 50th-percentile values.
        he_fit : np.ndarray
            Array of fitted 95th-percentile values.
        sleeper_buckling_range : np.ndarray
            2D array with shape (n_cases, 10000), one range per case.
        sleeper_buckling_cdf : np.ndarray
            2D array with shape (n_cases, 10000), one CDF per case.
        sleeper_buckling_pdf : np.ndarray
            2D array with shape (n_cases, 10000), one PDF per case.
        """
        mean_value_list = []
        std_value_list = []
        location_param_list = []
        scale_param_list = []
        le_fit_list = []
        be_fit_list = []
        he_fit_list = []
        sleeper_buckling_range_list = []
        sleeper_buckling_cdf_list = []
        sleeper_buckling_pdf_list = []

        _, bending_stiffness = self._section_properties()
        base_factor = 4.0 * np.sqrt(
            bending_stiffness * self.submerged_weight / self.sleeper_height
        )

        for oos_factor_mean, oos_factor_std in zip(
            self.oos_factor_mean,
            self.oos_factor_std
        ):
            mean_value = oos_factor_mean * base_factor
            std_value = oos_factor_std * base_factor

            (
                mean_value,
                std_value,
                location_param,
                scale_param,
                le_fit,
                be_fit,
                he_fit,
                sleeper_buckling_range,
                sleeper_buckling_cdf,
                sleeper_buckling_pdf
            ) = self._single_case_product_distribution(mean_value, std_value)

            mean_value_list.append(mean_value)
            std_value_list.append(std_value)
            location_param_list.append(location_param)
            scale_param_list.append(scale_param)
            le_fit_list.append(le_fit)
            be_fit_list.append(be_fit)
            he_fit_list.append(he_fit)
            sleeper_buckling_range_list.append(sleeper_buckling_range)
            sleeper_buckling_cdf_list.append(sleeper_buckling_cdf)
            sleeper_buckling_pdf_list.append(sleeper_buckling_pdf)

        mean_value = np.array(mean_value_list)
        std_value = np.array(std_value_list)
        location_param = np.array(location_param_list)
        scale_param = np.array(scale_param_list)
        le_fit = np.array(le_fit_list)
        be_fit = np.array(be_fit_list)
        he_fit = np.array(he_fit_list)
        sleeper_buckling_range = np.array(sleeper_buckling_range_list)
        sleeper_buckling_cdf = np.array(sleeper_buckling_cdf_list)
        sleeper_buckling_pdf = np.array(sleeper_buckling_pdf_list)

        return (
            mean_value,
            std_value,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            sleeper_buckling_range,
            sleeper_buckling_cdf,
            sleeper_buckling_pdf
        )

    def buckling_force_distribution_parameters(self):
        """
        Compute section buckling force distribution parameters based on ``oos_section_type``.

        Valid values are ``Straight``, ``Curve``, and ``Sleeper`` (case-insensitive).

        Returns
        -------
        tuple
            Output from:
            - ``nominal_straight_buckling_force_distribution_parameters`` for ``Straight``
            - ``route_curve_buckling_force_distribution_parameters`` for ``Curve``
            - ``sleeper_buckling_force_distribution_parameters`` for ``Sleeper``

        Notes
        -----
        Mixed section types are supported in one call. Each case is evaluated with the
        corresponding section formula.
        """
        section_type = np.atleast_1d(np.asarray(self.oos_section_type, dtype=object))
        if section_type.size == 0:
            raise ValueError(
                "oos_section_type must be provided as 'Straight', 'Curve', or 'Sleeper'."
            )

        _, bending_stiffness = self._section_properties()
        characteristic_force = self.characteristic_buckling_force()

        (
            section_type,
            oos_mean,
            oos_std,
            friction_mean,
            friction_std,
            submerged_weight,
            curve_radius,
            sleeper_height,
            characteristic_force,
            bending_stiffness
        ) = np.broadcast_arrays(
            section_type,
            self.oos_factor_mean,
            self.oos_factor_std,
            self.friction_factor_mean,
            self.friction_factor_std,
            self.submerged_weight,
            self.curve_radius,
            self.sleeper_height,
            characteristic_force,
            bending_stiffness,
        )

        mean_value_list = []
        std_value_list = []
        location_param_list = []
        scale_param_list = []
        le_fit_list = []
        be_fit_list = []
        he_fit_list = []
        distribution_range_list = []
        distribution_cdf_list = []
        distribution_pdf_list = []

        for (
            section,
            oos_mean_i,
            oos_std_i,
            friction_mean_i,
            friction_std_i,
            submerged_weight_i,
            curve_radius_i,
            sleeper_height_i,
            characteristic_force_i,
            bending_stiffness_i,
        ) in zip(
            section_type,
            oos_mean,
            oos_std,
            friction_mean,
            friction_std,
            submerged_weight,
            curve_radius,
            sleeper_height,
            characteristic_force,
            bending_stiffness,
        ):
            section_lower = str(section).strip().lower()

            if section_lower == "straight":
                sqrt_friction_mean_i, sqrt_friction_std_i = self._sqrt_lognorm_moments(
                    friction_mean_i,
                    friction_std_i,
                )

                mean_value = characteristic_force_i * oos_mean_i * sqrt_friction_mean_i
                variance_factor = (
                    (oos_std_i**2 + oos_mean_i**2)
                    * (sqrt_friction_std_i**2 + sqrt_friction_mean_i**2)
                    - (oos_mean_i**2 * sqrt_friction_mean_i**2)
                )
                variance_factor = max(variance_factor, 0.0)
                std_value = characteristic_force_i * np.sqrt(variance_factor)
            elif section_lower == "curve":
                mean_value = (
                    oos_mean_i
                    * friction_mean_i
                    * submerged_weight_i
                    * curve_radius_i
                )
                variance_factor = (
                    (oos_std_i**2 + oos_mean_i**2)
                    * (friction_std_i**2 + friction_mean_i**2)
                    - (oos_mean_i**2 * friction_mean_i**2)
                )
                variance_factor = max(variance_factor, 0.0)
                std_value = submerged_weight_i * curve_radius_i * np.sqrt(variance_factor)
            elif section_lower == "sleeper":
                base_factor = 4.0 * np.sqrt(
                    bending_stiffness_i * submerged_weight_i / sleeper_height_i
                )
                mean_value = oos_mean_i * base_factor
                std_value = oos_std_i * base_factor
            else:
                raise ValueError(
                    "Invalid oos_section_type. Allowed values are 'Straight', 'Curve', or 'Sleeper'."
                )

            (
                mean_value,
                std_value,
                location_param,
                scale_param,
                le_fit,
                be_fit,
                he_fit,
                distribution_range,
                distribution_cdf,
                distribution_pdf,
            ) = self._single_case_product_distribution(mean_value, std_value)

            mean_value_list.append(mean_value)
            std_value_list.append(std_value)
            location_param_list.append(location_param)
            scale_param_list.append(scale_param)
            le_fit_list.append(le_fit)
            be_fit_list.append(be_fit)
            he_fit_list.append(he_fit)
            distribution_range_list.append(distribution_range)
            distribution_cdf_list.append(distribution_cdf)
            distribution_pdf_list.append(distribution_pdf)

        return (
            np.array(mean_value_list),
            np.array(std_value_list),
            np.array(location_param_list),
            np.array(scale_param_list),
            np.array(le_fit_list),
            np.array(be_fit_list),
            np.array(he_fit_list),
            np.array(distribution_range_list),
            np.array(distribution_cdf_list),
            np.array(distribution_pdf_list),
        )


class LBOOSDistributions: # pylint: disable=too-many-instance-attributes, too-many-arguments
    """
    Class for lateral buckling calculations, including out-of-straightness (OOS)
    distribution fitting.

    Parameters
    ----------
    oos_factor_mean : float, optional
        Mean OOS factor for the condition of interest.
    oos_factor_std : float, optional
        Standard deviation of the OOS factor for the condition of interest.
    """
    def __init__(
            self,
            *,
            oos_factor_mean,
            oos_factor_std
        ):
        """
        Initialize with OOS factor mean and standard deviation.
        """
        self.oos_factor_mean = np.asarray(oos_factor_mean, dtype = float)
        self.oos_factor_std = np.asarray(oos_factor_std, dtype = float)

    @staticmethod
    def _lognorm_parameters(oos_factor_mean, oos_factor_std):
        """
        Compute lognormal location and scale parameters from OOS mean and standard deviation.
        """
        scale_param = np.sqrt(np.log(1 + oos_factor_std**2 / oos_factor_mean**2))
        location_param = np.log(
            oos_factor_mean**2 / np.sqrt(oos_factor_mean**2 + oos_factor_std**2)
        )
        return location_param, scale_param

    @staticmethod
    def _fitted_values(location_param, scale_param):
        """
        Compute LE/BE/HE OOS values from lognormal parameters.
        """
        le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
        be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
        he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)
        return le_fit, be_fit, he_fit

    @staticmethod
    def _calc_lognorm_oos(oos_factor_mean, oos_factor_std):
        """
        Compute a lognormal OOS curve from mean and standard deviation.

        Parameters
        ----------
        oos_factor_mean : float
            Mean value of the OOS factor.
        oos_factor_std : float
            Standard deviation of the OOS factor.

        Returns
        -------
        oos_factor_range : np.ndarray
            OOS-factor range spanning the 0.01% to 99.99% quantiles.
        oos_factor_cdf : np.ndarray
            CDF values corresponding to `oos_factor_range`.
        """
        location_param, scale_param = LBOOSDistributions._lognorm_parameters(
            oos_factor_mean,
            oos_factor_std
        )

        oos_lower = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.0001)
        oos_upper = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.9999)

        oos_factor_range = np.linspace(oos_lower, oos_upper, 10000)
        oos_factor_cdf = lognorm.cdf(
            oos_factor_range,
            scale_param,
            0.0,
            np.exp(location_param)
        )

        return oos_factor_range, oos_factor_cdf

    def _single_case_distribution(self, oos_factor_mean, oos_factor_std):
        """
        Compute OOS distribution from mean and standard deviation.
        """
        location_param, scale_param = self._lognorm_parameters(
            oos_factor_mean,
            oos_factor_std
        )
        le_fit, be_fit, he_fit = self._fitted_values(location_param, scale_param)
        oos_factor_range, oos_factor_cdf = self._calc_lognorm_oos(
            oos_factor_mean,
            oos_factor_std
        )

        return (
            oos_factor_mean,
            oos_factor_std,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            oos_factor_range,
            oos_factor_cdf
        )

    def oos_distribution_parameters(self):
        """
        Compute the parameters of the OOS lognormal distribution
        directly from the specified mean and standard deviation.

        Returns
        -------
        mean_oos : np.ndarray
            Array of mean OOS-factor values.
        std_oos : np.ndarray
            Array of standard deviation OOS-factor values.
        location_param : np.ndarray
            Array of location parameters of the lognormal OOS distribution.
        scale_param : np.ndarray
            Array of scale parameters of the lognormal OOS distribution.
        le_fit : np.ndarray
            Array of fitted 5th-percentile OOS values.
        be_fit : np.ndarray
            Array of fitted 50th-percentile OOS values.
        he_fit : np.ndarray
            Array of fitted 95th-percentile OOS values.
        oos_factor_range : np.ndarray
            2D array with shape (n_cases, 10000), one range per case.
        oos_factor_cdf : np.ndarray
            2D array with shape (n_cases, 10000), one CDF per case.

        Notes
        -----
        This method mirrors the output structure of `LBSoilDistributions`, but it does not
        perform an optimization step because the OOS mean and standard deviation are already
        provided as inputs.

        Examples
        --------
        >>> lb = LBOOSDistributions(
        ...     oos_factor_mean=[1.26],
        ...     oos_factor_std=[0.33]
        ... )
        >>> result = lb.oos_distribution_parameters()
        >>> result[:7]
        (array([1.26]), array([0.33]), array([0.19793979]), array([0.25757303]), array([0.79793341]), array([1.218889]), array([1.86192279]))
        >>> result[7].shape, result[8].shape
        ((1, 10000), (1, 10000))
        """
        mean_oos_list = []
        std_oos_list = []
        location_param_list = []
        scale_param_list = []
        le_fit_list = []
        be_fit_list = []
        he_fit_list = []
        oos_factor_range_list = []
        oos_factor_cdf_list = []

        for oos_factor_mean, oos_factor_std in zip(
            self.oos_factor_mean,
            self.oos_factor_std
        ):
            (
                mean_oos,
                std_oos,
                location_param,
                scale_param,
                le_fit,
                be_fit,
                he_fit,
                oos_factor_range,
                oos_factor_cdf
            ) = self._single_case_distribution(oos_factor_mean, oos_factor_std)

            mean_oos_list.append(mean_oos)
            std_oos_list.append(std_oos)
            location_param_list.append(location_param)
            scale_param_list.append(scale_param)
            le_fit_list.append(le_fit)
            be_fit_list.append(be_fit)
            he_fit_list.append(he_fit)
            oos_factor_range_list.append(oos_factor_range)
            oos_factor_cdf_list.append(oos_factor_cdf)

        mean_oos = np.array(mean_oos_list)
        std_oos = np.array(std_oos_list)
        location_param = np.array(location_param_list)
        scale_param = np.array(scale_param_list)
        le_fit = np.array(le_fit_list)
        be_fit = np.array(be_fit_list)
        he_fit = np.array(he_fit_list)
        oos_factor_range = np.array(oos_factor_range_list)
        oos_factor_cdf = np.array(oos_factor_cdf_list)

        return (
            mean_oos,
            std_oos,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            oos_factor_range,
            oos_factor_cdf
        )


class LBSoilDistributions: # pylint: disable=too-many-instance-attributes, too-many-arguments
    """
    Class for lateral buckling calculations, including friction factor distribution fitting.

    Parameters
    ----------
    friction_factor_le : float, optional
        Low estimate (LE) friction factor, representing the 5th percentile.
    friction_factor_be : float, optional
        Best estimate (BE) friction factor, representing the 50th percentile.
    friction_factor_he : float, optional
        High estimate (HE) friction factor, representing the 95th percentile.
    friction_factor_fit_type : str, optional
        Type of fit to perform: 'LE_BE_HE', 'LE_BE', or 'BE_HE'.
    """
    def __init__(
            self,
            *,
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ):
        """
        Initialize with geotechnical friction factor estimates and fit type.
        """
        self.friction_factor_le = np.asarray(friction_factor_le, dtype = float)
        self.friction_factor_be = np.asarray(friction_factor_be, dtype = float)
        self.friction_factor_he = np.asarray(friction_factor_he, dtype = float)
        self.friction_factor_fit_type = np.asarray(friction_factor_fit_type, dtype = object)

    @staticmethod
    def _objective_rmse(
            params,
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ):
        """
        Objective function used to fit lognormal parameters by RMSE minimization.
        """
        location_param, scale_param = params
        if friction_factor_fit_type == 'LE_BE_HE':
            le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
            be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
            he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)
            error = np.sqrt(
                ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2
                 + (he_fit - friction_factor_he)**2) / 3.0
            )
        elif friction_factor_fit_type == 'LE_BE':
            le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
            be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
            error = np.sqrt(
                ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2) / 2.0
            )
        elif friction_factor_fit_type == 'BE_HE':
            be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
            he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)
            error = np.sqrt(
                ((be_fit - friction_factor_be)**2 + (he_fit - friction_factor_he)**2) / 2.0
            )
        else:
            error = np.nan
        return error

    @staticmethod
    def _initial_guess(friction_factor_le, friction_factor_be, friction_factor_he):
        """
        Compute initial guess for location and scale parameters.
        """
        initial_location = np.mean(
            [np.log(friction_factor_le),
             np.log(friction_factor_be),
             np.log(friction_factor_he)]
        )
        initial_scale = np.std(
            [np.log(friction_factor_le),
             np.log(friction_factor_be),
             np.log(friction_factor_he)],
            ddof=1
        )
        return [initial_location, initial_scale]

    @staticmethod
    def _fitted_values(location_param, scale_param):
        """
        Compute LE/BE/HE fitted values from lognormal parameters.
        """
        le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
        be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
        he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)
        return le_fit, be_fit, he_fit

    @staticmethod
    def _compute_rmse(
            le_fit,
            be_fit,
            he_fit,
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ):
        """
        Compute RMSE for the selected fit type.
        """
        if friction_factor_fit_type == 'LE_BE_HE':
            rmse = np.sqrt(
                ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2
                 + (he_fit - friction_factor_he)**2) / 3.0
            )
        elif friction_factor_fit_type == 'LE_BE':
            rmse = np.sqrt(
                ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2) / 2.0
            )
        elif friction_factor_fit_type == 'BE_HE':
            rmse = np.sqrt(
                ((be_fit - friction_factor_be)**2 + (he_fit - friction_factor_he)**2) / 2.0
            )
        else:
            rmse = np.nan
        return rmse

    @staticmethod
    def _compute_r2(
            le_fit,
            be_fit,
            he_fit,
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ):
        """
        Compute the coefficient of determination R² for the selected fit type.
        """
        if friction_factor_fit_type == 'LE_BE_HE':
            observed = np.array([friction_factor_le, friction_factor_be, friction_factor_he])
            fitted = np.array([le_fit, be_fit, he_fit])
        elif friction_factor_fit_type == 'LE_BE':
            observed = np.array([friction_factor_le, friction_factor_be])
            fitted = np.array([le_fit, be_fit])
        elif friction_factor_fit_type == 'BE_HE':
            observed = np.array([friction_factor_be, friction_factor_he])
            fitted = np.array([be_fit, he_fit])
        else:
            return np.nan

        sst = np.sum((observed - np.mean(observed))**2)
        if np.isclose(sst, 0.0):
            return np.nan

        ss_res = np.sum((observed - fitted)**2)
        return 1.0 - ss_res / sst

    def _fit_single_case(
            self,
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ):
        """
        Fit one LE/BE/HE set and return all derived values.
        """
        initial_guess = self._initial_guess(
            friction_factor_le,
            friction_factor_be,
            friction_factor_he
        )

        result = minimize(
            self._objective_rmse,
            initial_guess,
            args=(
                friction_factor_le,
                friction_factor_be,
                friction_factor_he,
                friction_factor_fit_type
            ),
            method='Nelder-Mead'
        )
        location_param, scale_param = result.x

        mean_friction = np.exp(location_param + scale_param**2 / 2)
        std_friction = np.sqrt(
            (np.exp(scale_param**2) - 1)
            * np.exp(2 * location_param + scale_param**2)
        )

        le_fit, be_fit, he_fit = self._fitted_values(location_param, scale_param)
        rmse = self._compute_rmse(
            le_fit,
            be_fit,
            he_fit,
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        )
        r2 = self._compute_r2(
            le_fit,
            be_fit,
            he_fit,
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        )

        return (
            mean_friction,
            std_friction,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            rmse,
            r2
        )

    @staticmethod
    def _calc_lognorm_soil(mu_mean, mu_std):
        """
        Compute a lognormal friction-factor curve from mean and standard deviation.

        Parameters
        ----------
        mu_mean : float
            Mean value of the friction factor.
        mu_std : float
            Standard deviation of the friction factor.

        Returns
        -------
        friction_factor_range : np.ndarray
            Friction-factor range spanning the 0.01% to 99.99% quantiles.
        friction_factor_cdf : np.ndarray
            CDF values corresponding to `friction_factor_range`.
        """

        mu_shape = np.sqrt(np.log(1 + mu_std**2 / mu_mean**2))
        mu_scale = np.log(mu_mean**2 / np.sqrt(mu_mean**2 + mu_std**2))

        mu_lower = lognorm(mu_shape, 0.0, np.exp(mu_scale)).ppf(0.0001)
        mu_upper = lognorm(mu_shape, 0.0, np.exp(mu_scale)).ppf(0.9999)

        friction_factor_range = np.linspace(mu_lower, mu_upper, 10000)
        friction_factor_cdf = lognorm.cdf(
            friction_factor_range,
            mu_shape,
            0.0,
            np.exp(mu_scale)
        )

        return friction_factor_range, friction_factor_cdf

    def friction_distribution_parameters(self):
        """
        Compute the parameters of the lognormal friction factor distribution (axial or lateral)
        by minimizing the root mean square error (RMSE) between geotechnical estimates and
        back-calculated friction factors from the lognormal distribution.

        Returns
        -------
        mean_friction : np.ndarray
            Array of mean values of the lognormal friction factor distribution.
        std_friction : np.ndarray
            Array of standard deviation values of the lognormal friction factor distribution.
        location_param : np.ndarray
            Array of location parameters of the lognormal friction factor distribution.
        scale_param : np.ndarray
            Array of scale parameters of the lognormal friction factor distribution.
        le_fit : np.ndarray
            Array of fitted LE values.
        be_fit : np.ndarray
            Array of fitted BE values.
        he_fit : np.ndarray
            Array of fitted HE values.
        rmse : np.ndarray
            Array of RMSE values for the best fit type.
        r2 : np.ndarray
            Array of R² values for the best fit type.
        friction_factor_range : np.ndarray
            2D array with shape (n_cases, 10000), one range per case.
        friction_factor_cdf : np.ndarray
            2D array with shape (n_cases, 10000), one CDF per case.
        Notes
        -----
        The function calculates the parameters of the lognormal friction factor distribution
        based on LE at 5th percentile, BE at 50th percentile, and HE at 95th percentile

        Examples
        --------
        >>> lb = LBSoilDistributions(
        ...     friction_factor_le=[0.5],
        ...     friction_factor_be=[1.0],
        ...     friction_factor_he=[1.5],
        ...     friction_factor_fit_type=['LE_BE_HE']
        ... )
        >>> result = lb.friction_distribution_parameters()
        >>> result[:8]
        (array([0.9684083]), array([0.30043236]), array([-0.07804666]), array([0.3031342]), array([0.56177265]), array([0.92492127]), array([1.52282131]), array([0.05765844]))
        >>> result[9].shape, result[10].shape
        ((1, 10000), (1, 10000))
        """
        # Initialize lists to store results
        mean_friction_list = []
        std_friction_list = []
        location_param_list = []
        scale_param_list = []
        le_fit_list = []
        be_fit_list = []
        he_fit_list = []
        rmse_list = []
        r2_list = []
        friction_factor_range_list = []
        friction_factor_cdf_list = []

        # Loop through the friction factor arrays
        for _, (
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ) in enumerate(
            zip(
                self.friction_factor_le,
                self.friction_factor_be,
                self.friction_factor_he,
                self.friction_factor_fit_type
            )
        ):
            (
                mean_friction,
                std_friction,
                location_param,
                scale_param,
                le_fit,
                be_fit,
                he_fit,
                rmse,
                r2
            ) = self._fit_single_case(
                friction_factor_le,
                friction_factor_be,
                friction_factor_he,
                friction_factor_fit_type
            )

            friction_factor_range, friction_factor_cdf = self._calc_lognorm_soil(
                mean_friction,
                std_friction
            )

            # Append results for this iteration
            mean_friction_list.append(mean_friction)
            std_friction_list.append(std_friction)
            location_param_list.append(location_param)
            scale_param_list.append(scale_param)
            le_fit_list.append(le_fit)
            be_fit_list.append(be_fit)
            he_fit_list.append(he_fit)
            rmse_list.append(rmse)
            r2_list.append(r2)
            friction_factor_range_list.append(friction_factor_range)
            friction_factor_cdf_list.append(friction_factor_cdf)

        # Convert lists to NumPy arrays
        mean_friction = np.array(mean_friction_list)
        std_friction = np.array(std_friction_list)
        location_param = np.array(location_param_list)
        scale_param = np.array(scale_param_list)
        le_fit = np.array(le_fit_list)
        be_fit = np.array(be_fit_list)
        he_fit = np.array(he_fit_list)
        rmse = np.array(rmse_list)
        r2 = np.array(r2_list)
        friction_factor_range = np.array(friction_factor_range_list)
        friction_factor_cdf = np.array(friction_factor_cdf_list)

        return (
            mean_friction,
            std_friction,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            rmse,
            r2,
            friction_factor_range,
            friction_factor_cdf
        )

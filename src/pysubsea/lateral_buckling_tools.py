'''
This module provides classes and functions for lateral buckling calculations and friction factor
distribution fitting for subsea pipelines.

**Features:**

- The `LBForces` class calculates lateral buckling forces.
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

class LBForces: # pylint: disable=too-many-instance-attributes, too-many-arguments
    """
    Class for lateral buckling force calculations.

    Parameters
    ----------
    outer_diameter : float or array-like, optional
        Pipe outer diameter, used to compute section properties from `Pipe`.
    wall_thickness : float or array-like, optional
        Pipe wall thickness, used to compute section properties from `Pipe`.
    youngs_modulus : float or array-like, optional
        Young's modulus of the material.
    submerged_weight : float or array-like, optional
        Submerged weight for the condition of interest.
    """

    def __init__(
            self,
            *,
            outer_diameter=0.0,
            wall_thickness=0.0,
            youngs_modulus=0.0,
            submerged_weight=0.0
        ):
        """
        Initialize with section, material, and submerged weight properties.
        """
        self.outer_diameter = np.asarray(outer_diameter, dtype = float)
        self.wall_thickness = np.asarray(wall_thickness, dtype = float)
        self.youngs_modulus = np.asarray(youngs_modulus, dtype = float)
        self.submerged_weight = np.asarray(submerged_weight, dtype = float)

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
            wall_thickness=self.wall_thickness
        )
        steel_area = pipe.steel_area()
        area_moment_inertia = pipe.area_moment_inertia()

        return steel_area, area_moment_inertia

    def characteristic_buckling_force(self):
        """
        Compute characteristic buckling force.

        Returns
        -------
        characteristic_buckling_force : np.ndarray
            Characteristic lateral buckling force.

        Examples
        --------
        >>> lb = LBForces(
        ...     youngs_modulus=[207.0e+09],
        ...     outer_diameter=[0.2731],
        ...     wall_thickness=[0.0127],
        ...     submerged_weight=[1000.0]
        ... )
        >>> lb.characteristic_buckling_force()
        array([1200711.7485...])
        """
        steel_area, area_moment_inertia = self._section_properties()
        return (
            2.26
            * (self.youngs_modulus * steel_area) ** 0.25
            * (self.youngs_modulus * area_moment_inertia) ** 0.25
            * self.submerged_weight ** 0.5
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

        return (
            mean_friction,
            std_friction,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            rmse
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
        >>> lb.friction_distribution_parameters()
        (array([0.9684083]), array([0.30043236]), array([-0.07804666]), array([0.3031342]), array([0.56177265]), array([0.92492127]), array([1.52282131]), array([0.05765844]), array([[...]]), array([[...]]))
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
                rmse
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
            friction_factor_range,
            friction_factor_cdf
        )

'''
This module provides the core class and functions for representing and calculating the main
geometric and material properties of pipeline sections.

**Features:**

- The `Pipe` class encapsulates the geometry and material characteristics of a pipeline section,
  supporting both scalar and array-based calculations for batch processing.
- Methods for computing inner/outer diameters, areas, steel and coating cross-sections, stiffness,
  and moments of inertia.
- Designed for use in subsea pipeline and riser engineering, but general enough for any pipeline
  property calculations.

All calculations are vectorized using NumPy for efficiency and flexibility.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />
'''

import numpy as np
class Pipe: # pylint: disable=too-many-arguments
    """
    Class representing a pipeline section with geometric and material properties.
    Supports both scalar and array inputs for calculations.

    Parameters
    ----------
    outer_diameter : float or array-like, optional
        Outer diameter of the pipe. Default is 0.
    wall_thickness : float or array-like, optional
        Wall thickness of the pipe. Default is 0.
    corrosion_allowance : float or array-like, optional
        Corrosion allowance. Default is 0.
    coating_thicknesses : array-like, optional
        Radial thicknesses, either one value per pipe with shape (n_pipes,)
        or layer values with shape (n_pipes, n_layers), ordered from steel
        outward. Requires a scalar or one-dimensional outer diameter and one
        row per pipe for multi-layer input. Use zero thickness for absent layers.
    youngs_modulus : float or array-like, optional
        Young's modulus of the material. Default is 0.
    poisson_ratio : float or array-like, optional
        Poisson's ratio of the material. Default is 0.
    water_density : float or array-like, optional
        Density of water. Default is 0.
    steel_density : float or array-like, optional
        Density of steel. Default is 0.
    content_density : float or array-like, optional
        Density of the pipe content. Default is 0.
    coating_densities : array-like, optional
        Density per pipe with shape (n_pipes,), applied to every coating
        layer, or layer densities with shape (n_pipes, n_layers).
        May be omitted for geometry-only calculations; required for weights.
    """
    def __init__(
            self,
            *,
            outer_diameter=0.0,
            wall_thickness=0.0,
            corrosion_allowance=0.0,
            coating_thicknesses=None,
            youngs_modulus=0.0,
            poisson_ratio=0.0,
            water_density=0.0,
            content_density=0.0,
            steel_density=0.0,
            coating_densities=None,
        ):
        """
        Initialize a Pipe object with geometric and material properties.
        """
        self.outer_diameter = np.asarray(outer_diameter, dtype = float)
        self.wall_thickness = np.asarray(wall_thickness, dtype = float)
        self.corrosion_allowance = np.asarray(corrosion_allowance, dtype = float)
        self.coating_thicknesses = (
            None if coating_thicknesses is None
            else np.asarray(coating_thicknesses, dtype = float)
        )
        self.youngs_modulus = np.asarray(youngs_modulus, dtype = float)
        self.poisson_ratio = np.asarray(poisson_ratio, dtype = float)
        self.water_density = np.asarray(water_density, dtype = float)
        self.content_density = np.asarray(content_density, dtype = float)
        self.steel_density = np.asarray(steel_density, dtype = float)
        self.coating_densities = (
            None if coating_densities is None
            else np.asarray(coating_densities, dtype = float)
        )

    def _coating_thickness_layers(self):
        """Return coating thicknesses with an explicit final layer axis."""
        if self.coating_thicknesses.ndim == 0:
            return self.coating_thicknesses.reshape(1, 1)
        if self.coating_thicknesses.ndim == 1:
            return self.coating_thicknesses[..., np.newaxis]
        return self.coating_thicknesses

    def _coating_density_layers(self):
        """Return coating densities broadcast to the coating-area shape."""
        if self.coating_thicknesses.ndim <= 1:
            return np.broadcast_to(
                self.coating_densities,
                self.total_coating_area().shape,
            )

        densities = self.coating_densities
        if densities.ndim == 1:
            densities = densities[..., np.newaxis]
        return np.broadcast_to(densities, self.coating_thicknesses.shape)

    def wall_thickness_corroded(self):
        """
        Calculate the corroded wall thickness.

        Returns
        -------
        corroded_wall_thickness : np.ndarray
            Corroded wall thickness of the pipe.

        Examples
        --------
        >>> wall_thickness = [0.0127, 0.0159]
        >>> corrosion_allowance = [0.003, 0.003]
        >>> pipe = Pipe(
        ...     wall_thickness=wall_thickness,
        ...     corrosion_allowance=corrosion_allowance
        ... )
        >>> pipe.wall_thickness_corroded()
        array([0.0097, 0.0129])
        """
        return self.wall_thickness - self.corrosion_allowance

    def outer_diameter_to_wall_thickness_ratio(self):
        """
        Calculate the outer-diameter-to-wall-thickness ratio (D/t).

        Returns
        -------
        outer_diameter_to_wall_thickness_ratio : np.ndarray
            Outer diameter divided by wall thickness.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.outer_diameter_to_wall_thickness_ratio()
        array([21.50393701, 20.37106918])
        """
        return self.outer_diameter / self.wall_thickness

    def mid_diameter(self):
        """
        Calculate the pipe mid diameter.

        Returns
        -------
        mid_diameter : np.ndarray
            Mid diameter of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.mid_diameter()
        array([0.2604, 0.308 ])
        """
        return self.outer_diameter - self.wall_thickness

    def inner_diameter(self):
        """
        Calculate the pipe inner diameter.

        Returns
        -------
        inner_diameter : np.ndarray
            Inner diameter of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.inner_diameter()
        array([0.2477, 0.2921])
        """
        return self.outer_diameter - 2.0 * self.wall_thickness

    def outer_wall_radius(self):
        """
        Calculate the radius at the outer surface of the steel pipe wall.

        Returns
        -------
        outer_wall_radius : np.ndarray
            Outer radius of the steel pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> pipe = Pipe(outer_diameter=outer_diameter)
        >>> pipe.outer_wall_radius()
        array([0.13655, 0.16195])
        """
        return self.outer_diameter / 2.0

    def mid_wall_radius(self):
        """
        Calculate the radius at the middle of the pipe wall.

        Returns
        -------
        mid_wall_radius : np.ndarray
            Radius at the middle of the pipe wall.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.mid_wall_radius()
        array([0.1302, 0.154 ])
        """
        return self.mid_diameter() / 2.0

    def inner_wall_radius(self):
        """
        Calculate the radius at the inner surface of the pipe wall.

        Returns
        -------
        inner_wall_radius : np.ndarray
            Inner radius of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.inner_wall_radius()
        array([0.12385, 0.14605])
        """
        return self.inner_diameter() / 2.0

    def total_coating_thickness(self):
        """
        Calculate the combined radial coating thickness.

        Returns
        -------
        total_coating_thickness : np.ndarray or np.float64
            Sum of the layer thicknesses per pipe.

        Examples
        --------
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> pipe = Pipe(
        ...     coating_thicknesses=coating_thicknesses
        ... )
        >>> pipe.total_coating_thickness()
        array([0.0245, 0.074 ])
        >>> Pipe(coating_thicknesses=[0.0032, 0.0032]).total_coating_thickness()
        array([0.0032, 0.0032])
        """
        return np.sum(self._coating_thickness_layers(), axis=-1)

    def total_outer_diameter(self):
        """
        Calculate the total outer diameter of steel and coating.

        Returns
        -------
        total_outer_diameter : np.ndarray
            Total outer diameter of steel and coating.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thicknesses=coating_thicknesses
        ... )
        >>> pipe.total_outer_diameter()
        array([0.3221, 0.4719])
        """
        return self.outer_diameter + 2.0 * self.total_coating_thickness()

    def inner_area(self):
        """
        Calculate the pipe inner area.

        Returns
        -------
        inner_area : np.ndarray
            Inner area of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.inner_area()
        array([0.04818833, 0.06701206])
        """
        return np.pi / 4.0 * self.inner_diameter() ** 2

    def outer_area(self):
        """
        Calculate the pipe outer area.

        Returns
        -------
        outer_area : np.ndarray
            Outer area of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter
        ... )
        >>> pipe.outer_area()
        array([0.05857783, 0.08239707])
        """
        return np.pi / 4.0 * self.outer_diameter ** 2

    def steel_area(self):
        """
        Calculate the steel cross-sectional area.

        Returns
        -------
        steel_area : np.ndarray
            Steel cross-sectional area.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.steel_area()
        array([0.0103895 , 0.01538501])
        """
        return self.outer_area() - self.inner_area()

    def coating_areas(self):
        """
        Calculate the annular area of each coating layer.

        Returns
        -------
        coating_areas : np.ndarray
            Areas ordered from steel outward, with a final layer axis.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thicknesses=coating_thicknesses
        ... )
        >>> pipe.coating_areas()
        array([[0.00025767, 0.0001721 , 0.00527976, 0.01123811, 0.00595834],
               [0.00030555, 0.00020402, 0.00623732, 0.07697405, 0.00878201]])
        >>> Pipe(outer_diameter=[1.0, 2.0], coating_thicknesses=[0.1, 0.2]).coating_areas().shape
        (2,)
        """
        coating_thickness_layers = self._coating_thickness_layers()
        outer_diameters = (
            self.outer_diameter[..., np.newaxis]
            + 2.0 * np.cumsum(coating_thickness_layers, axis=-1)
        )
        inner_diameters = outer_diameters - 2.0 * coating_thickness_layers
        areas = np.pi / 4.0 * (outer_diameters ** 2 - inner_diameters ** 2)
        if self.coating_thicknesses.ndim <= 1:
            return np.squeeze(areas, axis=-1)
        return areas

    def total_coating_area(self):
        """
        Calculate the combined cross-sectional area of all coating layers.

        Returns
        -------
        total_coating_area : np.ndarray
            Area between the coated and steel outer diameters per pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thicknesses=coating_thicknesses
        ... )
        >>> pipe.total_coating_area()
        array([0.02290598, 0.09250294])
        """
        return np.pi / 4.0 * (self.total_outer_diameter() ** 2 - self.outer_diameter ** 2)

    def total_outer_area(self):
        """
        Calculate the outer area of steel and coating.

        Returns
        -------
        total_outer_area : np.ndarray
            Outer area of steel and coating.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thicknesses=coating_thicknesses
        ... )
        >>> pipe.total_outer_area()
        array([0.08148381, 0.17490001])
        """
        return np.pi / 4.0 * self.total_outer_diameter() ** 2

    def area_moment_inertia(self):
        """
        Calculate the area moment inertia.

        Returns
        -------
        area_moment_inertia : np.ndarray
            Area moment inertia.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.area_moment_inertia()
        array([8.82710601e-05, 1.82921605e-04])
        """
        return np.pi / 64.0 * (self.outer_diameter ** 4 - self.inner_diameter() ** 4)

    def polar_moment_inertia(self):
        """
        Calculate the polar moment of inertia of the pipe cross-section.

        Returns
        -------
        polar_moment_inertia : np.ndarray
            Polar moment of inertia of the pipe cross-section.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.polar_moment_inertia()
        array([0.00017654, 0.00036584])
        """
        return 2.0 * self.area_moment_inertia()

    def axial_stiffness(self):
        """
        Calculate the axial stiffness.

        Returns
        -------
        axial_stiffness : np.ndarray
            Axial stiffness of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> youngs_modulus = [207.0e+09, 207.0e+09]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness,
        ...     youngs_modulus=youngs_modulus
        ... )
        >>> pipe.axial_stiffness()
        array([2.15062613e+09, 3.18469656e+09])
        """
        return self.youngs_modulus * self.steel_area()

    def bending_stiffness(self):
        """
        Calculate the bending stiffness.

        Returns
        -------
        bending_stiffness : np.ndarray
            Bending stiffness.


        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> youngs_modulus = [207.0e+09, 207.0e+09]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness,
        ...     youngs_modulus=youngs_modulus
        ... )
        >>> pipe.bending_stiffness()
        array([18272109.437121..., 37864772.21769765])
        """
        return self.youngs_modulus * self.area_moment_inertia()

    def shear_modulus(self):
        """
        Calculate the shear modulus assuming an isotropic material.

        Returns
        -------
        shear_modulus : np.ndarray
            Shear modulus of the material.

        Examples
        --------
        >>> youngs_modulus = [207.0e+09, 207.0e+09]
        >>> poisson_ratio = [0.3, 0.3]
        >>> pipe = Pipe(
        ...     youngs_modulus=youngs_modulus,
        ...     poisson_ratio=poisson_ratio
        ... )
        >>> pipe.shear_modulus()
        array([7.96153846e+10, 7.96153846e+10])
        """
        return self.youngs_modulus / (2.0 * (1.0 + self.poisson_ratio))

    def torsional_stiffness(self):
        """
        Calculate the torsional stiffness of the pipe.

        Returns
        -------
        torsional_stiffness : np.ndarray
            Torsional stiffness of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> youngs_modulus = [207.0e+09, 207.0e+09]
        >>> poisson_ratio = [0.3, 0.3]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness,
        ...     youngs_modulus=youngs_modulus,
        ...     poisson_ratio=poisson_ratio
        ... )
        >>> pipe.torsional_stiffness()
        array([14055468.79778538, 29126747.85976743])
        """
        return self.shear_modulus() * self.polar_moment_inertia()

    def section_modulus(self):
        """
        Calculate the section modulus of the steel pipe about its mid-wall diameter.

        Returns
        -------
        section_modulus : np.ndarray
            Elastic section modulus of the pipe.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness
        ... )
        >>> pipe.section_modulus()
        array([0.000677..., 0.001187...])
        """
        return self.area_moment_inertia() / self.mid_wall_radius()

    def equivalent_coating_density(self):
        """
        Calculate the area-weighted equivalent density of the coating.

        Returns
        -------
        equivalent_coating_density : np.ndarray or np.float64
            Sum of density times layer area divided by total coating area.
            A scalar pipe returns a scalar; pipe arrays return one value per pipe.

        Raises
        ------
        ValueError
            If total coating area is zero or multi-layer densities are missing.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> coating_densities = [
        ...     [1500, 900, 900, 650, 900],
        ...     [1500, 900, 900, 650, 900]
        ... ]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thicknesses=coating_thicknesses,
        ...     coating_densities=coating_densities
        ... )
        >>> pipe.equivalent_coating_density()
        array([784.09479921, 693.95053762])
        >>> Pipe(
        ...     outer_diameter=[1.0, 2.0],
        ...     coating_thicknesses=[[0.1, 0.2], [0.2, 0.3]],
        ...     coating_densities=[1000.0, 1200.0],
        ... ).equivalent_coating_density()
        array([1000., 1200.])
        """
        if self.coating_thicknesses.ndim <= 1:
            return self._coating_density_layers().copy()

        areas = self.coating_areas()
        total_area = self.total_coating_area()
        densities = self._coating_density_layers()
        weighted_area = np.sum(densities * areas, axis=-1)
        return (weighted_area / total_area).reshape(self.outer_diameter.shape)

    def steel_weight(self):
        """
        Calculate the steel weight per unit length.

        Returns
        -------
        steel_weight : np.ndarray
            Steel weight per unit length.

        Examples
        --------
        >>> pipe = Pipe(
        ...     outer_diameter=[0.2731, 0.3239],
        ...     wall_thickness=[0.0127, 0.0159],
        ...     steel_density=[7850.0, 7850.0]
        ... )
        >>> pipe.steel_weight()
        array([ 799.83500198, 1184.41403646])
        """
        return 9.807 * self.steel_density * self.steel_area()

    def coating_weights(self):
        """
        Calculate each coating layer's weight per unit length.

        Returns
        -------
        coating_weights : np.ndarray
            Weights with the same shape as coating_areas().

        Raises
        ------
        ValueError
            If multi-layer coatings were supplied without layer densities.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> coating_densities = [
        ...     [1500, 900, 900, 650, 900],
        ...     [1500, 900, 900, 650, 900]
        ... ]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thicknesses=coating_thicknesses,
        ...     coating_densities=coating_densities
        ... )
        >>> pipe.coating_weights()
        array([[  3.79050498,   1.51897486,  46.6007511 ,  71.63786376,
                 52.59013718],
               [  4.49481242,   1.80069783,  55.05244034, 490.67490851,
                 77.51263813]])
        >>> Pipe(
        ...     outer_diameter=[1.0, 2.0],
        ...     coating_thicknesses=[[0.1, 0.2], [0.2, 0.3]],
        ...     coating_densities=[1000.0, 1200.0],
        ... ).coating_weights().shape
        (2, 2)
        """
        areas = self.coating_areas()
        return 9.807 * self._coating_density_layers() * areas

    def total_coating_weight(self):
        """
        Calculate the coating weight per unit length.

        Returns
        -------
        total_coating_weight : np.ndarray
            Coating weight per unit length.

        Raises
        ------
        ValueError
            If multi-layer coatings were supplied without layer densities.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> coating_densities = [
        ...     [1500, 900, 900, 650, 900],
        ...     [1500, 900, 900, 650, 900]
        ... ]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thicknesses=coating_thicknesses,
        ...     coating_densities=coating_densities
        ... )
        >>> pipe.total_coating_weight()
        array([176.13823189, 629.53549723])
        """
        weights = self.coating_weights()
        if self.coating_thicknesses.ndim <= 1:
            return weights
        return np.sum(weights, axis=-1).reshape(self.outer_diameter.shape)

    def content_weight(self):
        """
        Calculate the pipe-content weight per unit length.

        Returns
        -------
        content_weight : np.ndarray
            Pipe-content weight per unit length.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> content_density = [1025.0, 1025.0]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness,
        ...     content_density=content_density
        ... )
        >>> pipe.content_weight()
        array([484.39754703, 673.61699555])
        """
        return 9.807 * self.content_density * self.inner_area()

    def water_displaced_weight(self):
        """
        Calculate the weight of displaced water per unit length.

        Returns
        -------
        water_displaced_weight : np.ndarray
            Displaced-water weight per unit length.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> water_density = [1025.0, 1025.0]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     coating_thicknesses=coating_thicknesses,
        ...     water_density=water_density
        ... )
        >>> pipe.water_displaced_weight()
        array([ 819.08952452, 1758.12551508])
        """
        return 9.807 * self.water_density * self.total_outer_area()

    def submerged_weight(self):
        """
        Calculate the submerged weight per unit length.

        Returns
        -------
        submerged_weight : np.ndarray
            Submerged weight per unit length.

        Examples
        --------
        >>> outer_diameter = [0.2731, 0.3239]
        >>> wall_thickness = [0.0127, 0.0159]
        >>> coating_thicknesses = [
        ...     [0.0003, 0.0002, 0.006, 0.0120, 0.006],
        ...     [0.0003, 0.0002, 0.006, 0.0615, 0.006]
        ... ]
        >>> water_density = [1025.0, 1025.0]
        >>> steel_density = [7850.0, 7850.0]
        >>> content_density = [1025.0, 1025.0]
        >>> coating_densities = [
        ...     [1500, 900, 900, 650, 900],
        ...     [1500, 900, 900, 650, 900]
        ... ]
        >>> pipe = Pipe(
        ...     outer_diameter=outer_diameter,
        ...     wall_thickness=wall_thickness,
        ...     coating_thicknesses=coating_thicknesses,
        ...     water_density=water_density,
        ...     steel_density=steel_density,
        ...     content_density=content_density,
        ...     coating_densities=coating_densities,
        ... )
        >>> pipe.submerged_weight()
        array([641.28125638, 729.44101417])
        """
        return (
            self.steel_weight()
            + self.total_coating_weight()
            + self.content_weight()
            - self.water_displaced_weight()
        )

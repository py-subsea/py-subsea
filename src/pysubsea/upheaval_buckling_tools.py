'''
This module provides classes and functions for upheaval buckling calculations
for subsea pipelines.

**Features:**

- The `PropType` class calculates the properties of natural prop-type imperfections.
- All calculations are vectorized using NumPy for efficiency.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

'''

import numpy as np

class PropType: # pylint: disable=too-many-instance-attributes, too-many-arguments
    """
    Class for calculating the properties of natural prop-type imperfections.

    Parameters
    ----------
    bending_stiffness : float or array-like, optional
        Bending stiffness for the condition of interest.
    submerged_weight : float or array-like, optional
        Submerged weight for the condition of interest.
    propped_shape_height: float or array-like, optional
        Imperfection height for the condition of interest.
    effective_length_factor : float or array-like, optional
        Effective length factor for the condition of interest. Default is 1.0 (pinned-pinned);
        common values are pinned-pinned=1.0, fixed-pinned=0.699, fixed-fixed=0.5,
        and fixed-free=2.0.
    euler_buckling_mode : int, optional
        Euler buckling mode for the condition of interest. Default is 1 (first mode).
    """

    def __init__(
            self,
            *,
            bending_stiffness=0.0,
            submerged_weight=0.0,
            propped_shape_height=0.0,
            effective_length_factor=1.0,
            euler_buckling_mode=1
        ):
        """
        Initialize with bending stiffness, submerged weight, and imperfection height.
        """
        self.bending_stiffness = np.asarray(bending_stiffness, dtype = float)
        self.submerged_weight = np.asarray(submerged_weight, dtype = float)
        self.propped_shape_height = np.asarray(propped_shape_height, dtype = float)
        self.effective_length_factor = np.asarray(effective_length_factor, dtype = float)
        self.euler_buckling_mode = np.asarray(euler_buckling_mode, dtype = int)

    def propped_type_length(self):
        """
        Compute natural prop-type imperfection length.

        Returns
        -------
        length : np.ndarray
            Natural prop-type imperfection length.

        Examples
        --------
        >>> prop = PropType(
        ...     bending_stiffness=[18272109.437121, 37864772.21769765],
        ...     submerged_weight=[695.39794758, 1029.76124826],
        ...     propped_shape_height=[0.5, 0.5]
        ... )
        >>> prop.propped_type_length()
        array([62.372..., 67.839...])
        """
        length = 2.0 * (
            72.0 * self.bending_stiffness * self.propped_shape_height / self.submerged_weight
        ) ** 0.25
        return length

    def propped_shape_buckling_force(self):
        """
        Compute propped shape buckling force.

        The equation used is:

        ``P = 4 * (EI * Ws / h)^(1/2)``

        where:

        - ``P`` is the propped-shape buckling force,
        - ``EI`` is the bending stiffness,
        - ``Ws`` is the submerged weight, and
        - ``h`` is the propped-shape imperfection height.

        Returns
        -------
        propped_shape_buckling_force : np.ndarray
            Propped shape lateral buckling force.

        Examples
        --------
        >>> prop = PropType(
        ...     bending_stiffness=[18272109.437121, 37864772.21769765],
        ...     submerged_weight=[695.39794758, 1029.76124826],
        ...     propped_shape_height=[0.5, 0.5]
        ... )
        >>> prop.propped_shape_buckling_force()
        array([ 637655.3903..., 1117019.9655...])
        """
        return (
            4.0
            * (self.bending_stiffness * self.submerged_weight / self.propped_shape_height) ** 0.5
        )

    def euler_buckling_force(self):
        """
        Compute Euler buckling force.

        The equation used is:

        ``Pcr = n^2 * pi^2 * EI / (K * L)^2``

        Returns
        -------
        euler_buckling_force : np.ndarray
            Euler critical buckling force, ``Pcr``.

        Examples
        --------
        >>> prop = PropType(
        ...     bending_stiffness=[18272109.4, 18272109.4, 37864772.2, 37864772.2],
        ...     submerged_weight=[695.4, 695.4, 1029.8, 1029.8],
        ...     propped_shape_height=[0.5, 0.5, 0.5, 0.5],
        ...     effective_length_factor=[1.0, 1.0, 1.0, 1.0],
        ...     euler_buckling_mode=[1, 2, 1, 2]
        ... )
        >>> prop.euler_buckling_force()
        array([ 46355.3847..., 185421.5390..., 81204.9721..., 324819.8885...])
        """
        length = self.propped_type_length()
        return (
            self.euler_buckling_mode ** 2
            * (np.pi ** 2 * self.bending_stiffness)
            / (self.effective_length_factor * length) ** 2
        )

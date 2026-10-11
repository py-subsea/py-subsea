Lateral Buckling Tools
======================

.. currentmodule:: pysubsea.lateral_buckling_tools

LB Soil Distributions Class
---------------------------

.. autoclass:: pysubsea.lateral_buckling_tools.LBSoilDistributions
   :show-inheritance:

.. _lb-soil-input-parameters:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: LBSoilDistributions.friction_factor_le

   Low estimate friction factor input, representing the 5th percentile,
   supplied as a scalar or array-like value and stored as a NumPy array.
   Required.

.. attribute:: LBSoilDistributions.friction_factor_be

   Best estimate friction factor input, representing the 50th percentile,
   supplied as a scalar or array-like value and stored as a NumPy array.
   Required.

.. attribute:: LBSoilDistributions.friction_factor_he

   High estimate friction factor input, representing the 95th percentile,
   supplied as a scalar or array-like value and stored as a NumPy array.
   Required.

.. attribute:: LBSoilDistributions.friction_factor_fit_type

   Fit type input, supplied as a string or array-like value and stored as a
   NumPy array. Accepts ``LE_BE_HE``, ``LE_BE``, or ``BE_HE``. Required.

Friction Distribution Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: LBSoilDistributions.friction_distribution_parameters

LB OOS Distributions Class
--------------------------

.. autoclass:: pysubsea.lateral_buckling_tools.LBOOSDistributions
   :show-inheritance:

.. _lb-oos-input-parameters:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: LBOOSDistributions.oos_factor_mean

   Mean out-of-straightness (OOS) factor input, supplied as a scalar or
   array-like value and stored as a NumPy array. Required.

.. attribute:: LBOOSDistributions.oos_factor_std

   OOS factor standard deviation input, supplied as a scalar or array-like
   value and stored as a NumPy array. Required.

OOS Distribution Outputs
~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: LBOOSDistributions.oos_distribution_parameters

LB Force Distributions Class
----------------------------

.. autoclass:: pysubsea.lateral_buckling_tools.LBForceDistributions
   :show-inheritance:

.. _lb-force-input-parameters:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: LBForceDistributions.oos_section_type

   OOS section type input, supplied as a string or array-like value and stored
   as a NumPy array. Accepts ``Straight``, ``Curve``, or ``Sleeper``
   (case-insensitive) for section-based distribution calculations.
   Optional. Default value is None.

.. attribute:: LBForceDistributions.oos_factor_mean

   Mean OOS factor input for the condition of interest, supplied as a scalar
   or array-like value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: LBForceDistributions.oos_factor_std

   OOS factor standard deviation input for the condition of interest, supplied
   as a scalar or array-like value and stored as a NumPy array.
   Optional. Default value is 0.

.. attribute:: LBForceDistributions.oos_reference_length

   Reference length input for the OOS section, supplied as a scalar or
   array-like value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: LBForceDistributions.friction_factor_mean

   Mean friction factor input for the condition of interest, supplied as a
   scalar or array-like value and stored as a NumPy array.
   Optional. Default value is 0.

.. attribute:: LBForceDistributions.friction_factor_std

   Friction factor standard deviation input for the condition of interest,
   supplied as a scalar or array-like value and stored as a NumPy array.
   Optional. Default value is 0.

.. attribute:: LBForceDistributions.outer_diameter

   Pipe outer diameter input used to calculate section properties, supplied
   as a scalar or array-like value and stored as a NumPy array.
   Optional. Default value is 0.

.. attribute:: LBForceDistributions.wall_thickness

   Pipe wall thickness input used to calculate section properties, supplied
   as a scalar or array-like value and stored as a NumPy array.
   Optional. Default value is 0.

.. attribute:: LBForceDistributions.youngs_modulus

   Young's modulus input for the pipe material, supplied as a scalar or
   array-like value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: LBForceDistributions.submerged_weight

   Submerged weight input for the condition of interest, supplied as a scalar
   or array-like value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: LBForceDistributions.curve_radius

   Curve radius input for route-curve calculations, supplied as a scalar or
   array-like value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: LBForceDistributions.sleeper_height

   Sleeper height input for sleeper calculations, supplied as a scalar or
   array-like value and stored as a NumPy array. Optional. Default value is 0.

Characteristic Force Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: LBForceDistributions.characteristic_buckling_force

Buckling Force Distribution Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The straight-section, route-curve, and sleeper distribution methods return the
mean buckling force as the first item of their result tuples. Use these methods
for mean-force results; standalone mean-force methods are no longer provided.

.. automethod:: LBForceDistributions.nominal_straight_buckling_force_distribution_parameters

.. automethod:: LBForceDistributions.route_curve_buckling_force_distribution_parameters

.. automethod:: LBForceDistributions.sleeper_buckling_force_distribution_parameters

Section-Based Buckling Force Distribution Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The section-based method delegates each case to the matching distribution method
based on ``oos_section_type``. Mixed section types are returned in input order,
with scalar inputs broadcast across cases.

.. automethod:: LBForceDistributions.buckling_force_distribution_parameters

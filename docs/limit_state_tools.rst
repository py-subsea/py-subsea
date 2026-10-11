Limit State Tools
=================

.. currentmodule:: pysubsea.limit_state_tools

Material Strength Class
-----------------------

.. autoclass:: pysubsea.limit_state_tools.MaterialStrength
   :show-inheritance:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: MaterialStrength.outer_diameter

   Outer diameter input for the pipe, supplied as a scalar or array-like value
   and stored as a NumPy array.

.. attribute:: MaterialStrength.corroded_wall_thickness

   Corroded wall thickness input, supplied as a scalar or array-like value and
   stored as a NumPy array.

.. attribute:: MaterialStrength.temperature

   Temperature input, supplied as a scalar or array-like value and stored as a
   NumPy array.

.. attribute:: MaterialStrength.material

   Material type input. Values identify the supported material groups and are
   stored as a NumPy array.
   Material types: 1 for ‘CMn’ or ‘13CR’, 2 for ‘22Cr’ or ‘25CR’.

.. attribute:: MaterialStrength.material_strength_factor

   Material strength factor input, supplied as a scalar or array-like value
   and stored as a NumPy array.

.. attribute:: MaterialStrength.smys

   Specified minimum yield strength input, supplied as a scalar or array-like
   value and stored as a NumPy array.

.. attribute:: MaterialStrength.smts

   Specified minimum tensile strength input, supplied as a scalar or
   array-like value and stored as a NumPy array.

Material Property Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: MaterialStrength.yield_stress

.. automethod:: MaterialStrength.tensile_strength

.. automethod:: MaterialStrength.temperature_derating_stress

Burst Strength Outputs
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: MaterialStrength.characteristic_material_burst_strength


Limit States Class
------------------

.. autoclass:: pysubsea.limit_state_tools.LimitStates
   :show-inheritance:

.. _limit-states-input-parameters:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: LimitStates.outer_diameter

   Outer diameter input for the pipe, supplied as a scalar or array-like value
   and stored as a NumPy array.

.. attribute:: LimitStates.corroded_wall_thickness

   Corroded wall thickness input, supplied as a scalar or array-like value and
   stored as a NumPy array.

.. attribute:: LimitStates.temperature

   Temperature input, supplied as a scalar or array-like value and stored as a
   NumPy array.

.. attribute:: LimitStates.material

   Material type input. Values identify the supported material groups and are
   stored as a NumPy array.
   Material types: 1 for ‘CMn’ or ‘13CR’, 2 for ‘22Cr’ or ‘25CR’.

.. attribute:: LimitStates.material_strength_factor

   Material strength factor input, supplied as a scalar or array-like value
   and stored as a NumPy array.

.. attribute:: LimitStates.smys

   Specified minimum yield strength input, supplied as a scalar or array-like
   value and stored as a NumPy array.

.. attribute:: LimitStates.smts

   Specified minimum tensile strength input, supplied as a scalar or
   array-like value and stored as a NumPy array.

Burst Pressure Outputs
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: LimitStates.burst_pressure

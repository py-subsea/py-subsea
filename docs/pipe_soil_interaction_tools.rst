Pipe-Soil Interaction Tools
===========================

.. currentmodule:: pysubsea.pipe_soil_interaction_tools

PSI Class
---------

.. autoclass:: pysubsea.pipe_soil_interaction_tools.PSI
   :show-inheritance:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: PSI.total_outer_diameter

   Total outer diameter input for the pipe, supplied as a scalar or array-like value and
   stored as a NumPy array. Optional. Default value is 0.

.. attribute:: PSI.surface_roughness

   Surface roughness input for the pipe, supplied as a scalar or array-like value and stored
   as a NumPy array. Accepted values are typically 'Smooth' or 'Rough'. Optional. Default
   value is None.

.. attribute:: PSI.undrained_shear_strength_depth_array

   Depth profile for the undrained shear strength, provided as a per-pipe array of depth
   values in metres and stored as a list of NumPy arrays.

.. attribute:: PSI.undrained_shear_strength_value_array

   Undrained shear strength profile values, provided as a per-pipe array matching the depth
   profile and stored as a list of NumPy arrays.

.. attribute:: PSI.submerged_unit_weight

   Submerged unit weight of the soil, supplied as a scalar or array-like value and stored as a
   NumPy array. Optional. Default value is 0.

Downward Undrained Model Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: PSI.downward_undrained_model1

.. automethod:: PSI.downward_undrained_model2

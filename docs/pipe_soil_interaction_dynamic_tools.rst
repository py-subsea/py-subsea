Pipe-Soil Interaction Dynamic Tools
===================================

.. currentmodule:: pysubsea.pipe_soil_interaction_dynamic_tools

PSI Dynamic Class
-----------------

.. autoclass:: pysubsea.pipe_soil_interaction_dynamic_tools.PSIDynamic
   :show-inheritance:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: PSIDynamic.total_outer_diameter

   Total outer diameter input for the pipe, supplied as a scalar or array-like value and
   stored as a NumPy array.

.. attribute:: PSIDynamic.specific_mass_ratio

   Pipe mass divided by displaced-water mass, supplied as a scalar or array-like value and
   stored as a NumPy array.

.. attribute:: PSIDynamic.soil_type

   Soil type input used to select lookup values. Accepts supported soil names as a scalar or
   array-like value and is stored as a NumPy array.

Soil Property Outputs
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: PSIDynamic.soil_properties

Dynamic Stiffness Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: PSIDynamic.dynamic_stiffness_horizontal

.. automethod:: PSIDynamic.dynamic_stiffness_vertical

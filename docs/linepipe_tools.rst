Linepipe Tools
==============

.. currentmodule:: pysubsea.linepipe_tools

Pipe Class
----------

.. autoclass:: pysubsea.linepipe_tools.Pipe
   :show-inheritance:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: Pipe.outer_diameter

   Outer diameter input for the pipe, supplied as a scalar or array-like value
   and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: Pipe.wall_thickness

   Steel wall thickness of the pipe, supplied as a scalar or array-like input
   and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: Pipe.corrosion_allowance

   Corrosion allowance input for the pipe, supplied as a scalar or array-like
   value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: Pipe.coating_thicknesses

   Coating thickness input for the pipe, supplied as an array-like value and
   stored as a NumPy array. Multiple layers are ordered from steel outward;
   omitted values represent an uncoated pipe.
   Optional. Default value is an empty array.

.. attribute:: Pipe.youngs_modulus

   Young's modulus input for the pipe material, supplied as a scalar or
   array-like value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: Pipe.poisson_ratio

   Poisson's ratio input for the pipe material, supplied as a scalar or
   array-like value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: Pipe.water_density

   Water density input, supplied as a scalar or array-like value and stored as
   a NumPy array. Optional. Default value is 0.

.. attribute:: Pipe.content_density

   Pipe~content density input, supplied as a scalar or array-like value and
   stored as a NumPy array. Optional. Default value is 0.

.. attribute:: Pipe.steel_density

   Steel density input, supplied as a scalar or array-like value and stored as
   a NumPy array. Optional. Default value is 0.

.. attribute:: Pipe.coating_densities

   Coating density input, supplied as a scalar or array-like value and stored
   as a NumPy array when provided. Optional. Default value is 0.

Diameter Outputs
~~~~~~~~~~~~~~~~

.. automethod:: Pipe.inner_diameter

.. automethod:: Pipe.mid_diameter

.. automethod:: Pipe.total_outer_diameter

.. automethod:: Pipe.outer_diameter_to_wall_thickness_ratio

Radius Ouputs
~~~~~~~~~~~~~

.. automethod:: Pipe.outer_radius

.. automethod:: Pipe.mid_radius

.. automethod:: Pipe.inner_radius

Thickness Outputs
~~~~~~~~~~~~~~~~~

.. automethod:: Pipe.wall_thickness_corroded

.. automethod:: Pipe.total_coating_thickness

Cross-Section Outputs
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: Pipe.inner_area

.. automethod:: Pipe.outer_area

.. automethod:: Pipe.steel_area

.. automethod:: Pipe.coating_areas

.. automethod:: Pipe.total_coating_area

.. automethod:: Pipe.total_outer_area

Moment of Inertia Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: Pipe.area_moment_inertia

.. automethod:: Pipe.polar_moment_inertia

Section Modulus Outputs
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: Pipe.section_modulus

Material Property Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: Pipe.shear_modulus

Density Outputs
~~~~~~~~~~~~~~~

.. automethod:: Pipe.equivalent_coating_density

Stiffness Outputs
~~~~~~~~~~~~~~~~~

.. automethod:: Pipe.axial_stiffness

.. automethod:: Pipe.bending_stiffness

.. automethod:: Pipe.torsional_stiffness

Weight Outputs
~~~~~~~~~~~~~~

.. automethod:: Pipe.steel_weight

.. automethod:: Pipe.coating_weights

.. automethod:: Pipe.total_coating_weight

.. automethod:: Pipe.content_weight

.. automethod:: Pipe.water_displaced_weight

.. automethod:: Pipe.submerged_weight

Mass Outputs
~~~~~~~~~~~~

.. automethod:: Pipe.mass

.. automethod:: Pipe.specific_mass

.. automethod:: Pipe.specific_mass_ratio

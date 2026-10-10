Linepipe Tools
==============

.. autoclass:: pysubsea.linepipe_tools.Pipe
   :show-inheritance:

.. currentmodule:: pysubsea.linepipe_tools

Diameters, radii, and thicknesses
---------------------------------

.. automethod:: Pipe.wall_thickness_corroded

.. automethod:: Pipe.outer_diameter_to_wall_thickness_ratio

.. automethod:: Pipe.mid_diameter

.. automethod:: Pipe.inner_diameter

.. automethod:: Pipe.outer_wall_radius

.. automethod:: Pipe.mid_wall_radius

.. automethod:: Pipe.inner_wall_radius

.. automethod:: Pipe.total_coating_thickness

.. automethod:: Pipe.total_outer_diameter

Cross-sectional areas
---------------------

.. automethod:: Pipe.inner_area

.. automethod:: Pipe.outer_area

.. automethod:: Pipe.steel_area

.. automethod:: Pipe.coating_areas

.. automethod:: Pipe.total_coating_area

.. automethod:: Pipe.total_outer_area

Moments of inertia and section modulus
--------------------------------------

.. automethod:: Pipe.area_moment_inertia

.. automethod:: Pipe.polar_moment_inertia

.. automethod:: Pipe.section_modulus

Material properties and stiffness
---------------------------------

.. automethod:: Pipe.shear_modulus

.. automethod:: Pipe.axial_stiffness

.. automethod:: Pipe.bending_stiffness

.. automethod:: Pipe.torsional_stiffness

Densities and weights
---------------------

.. automethod:: Pipe.equivalent_coating_density

.. automethod:: Pipe.steel_weight

.. automethod:: Pipe.coating_weights

.. automethod:: Pipe.total_coating_weight

.. automethod:: Pipe.content_weight

.. automethod:: Pipe.water_displaced_weight

.. automethod:: Pipe.submerged_weight
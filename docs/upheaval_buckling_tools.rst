Upheaval Buckling Tools
=======================

.. currentmodule:: pysubsea.upheaval_buckling_tools

Prop Type Shape Class
---------------------

.. autoclass:: pysubsea.upheaval_buckling_tools.PropType
   :show-inheritance:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: PropType.bending_stiffness

   Bending stiffness input for the condition of interest, supplied as a scalar
   or array-like value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: PropType.submerged_weight

   Submerged weight input for the condition of interest, supplied as a scalar
   or array-like value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: PropType.propped_shape_height

   Propped-shape imperfection height input, supplied as a scalar or array-like
   value and stored as a NumPy array. Optional. Default value is 0.

.. attribute:: PropType.euler_wave_number

   Euler wave-number input for the condition of interest, supplied as a scalar
   or array-like value and stored as a NumPy array. Optional. Default value is 1.

Span Length Outputs
~~~~~~~~~~~~~~~~~~~

.. automethod:: PropType.propped_type_shape_span_length

Buckling Force Outputs
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: PropType.propped_type_shape_lift_off_force

.. automethod:: PropType.span_euler_buckling_force

OOS Tools
=========

.. currentmodule:: pysubsea.oos_tools

OOS Despiker Class
------------------

.. autoclass:: pysubsea.oos_tools.OOSDespiker
   :show-inheritance:

.. _oos-despiker-input-parameters:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: OOSDespiker.development

   Development identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Optional. Defaults to ``Predefined`` for
   every point when omitted.

.. attribute:: OOSDespiker.survey_type

   Survey types for each survey point, supplied as an array-like value and stored
   as a NumPy array. Optional. Defaults to ``Predefined`` for every point when
   omitted.

.. attribute:: OOSDespiker.pipeline_group

   Pipeline group identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Optional. Defaults to ``Predefined`` for
   every point when omitted.

.. attribute:: OOSDespiker.group_section_type

   Group section types for each survey point, supplied as an array-like value
   and stored as a NumPy array. Optional. Defaults to ``Predefined`` for every
   point when omitted.

.. attribute:: OOSDespiker.x

   Coordinates associated with the signal, supplied as an array-like value and
   stored as a NumPy array. Required.

.. attribute:: OOSDespiker.y

   Signal values for each survey point, supplied as an array-like value and
   stored as a NumPy array. Required.

.. attribute:: OOSDespiker.window

   Rolling window size for the Hampel filter, supplied as an integer.
   Optional. Default value is 11.

.. _oos-despiked-coordinate-outputs:

Despiked Coordinate Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: OOSDespiker.get_x_y_despike_median_aligned

OOS Curvature Class
-------------------

.. autoclass:: pysubsea.oos_tools.OOSCurvature
   :show-inheritance:

.. _oos-curvature-input-parameters:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: OOSCurvature.development

   Development identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Optional. Defaults to ``Predefined`` for
   every point when omitted.

.. attribute:: OOSCurvature.survey_type

   Survey types for each survey point, supplied as an array-like value and stored
   as a NumPy array. Optional. Defaults to ``Predefined`` for every point when
   omitted.

.. attribute:: OOSCurvature.pipeline_group

   Pipeline group identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Optional. Defaults to ``Predefined`` for
   every point when omitted.

.. attribute:: OOSCurvature.group_section_type

   Group section types for each survey point, supplied as an array-like value
   and stored as a NumPy array. Optional. Defaults to ``Predefined`` for every
   point when omitted.

.. attribute:: OOSCurvature.x

   Easting or anonymised easting coordinates, supplied as an array-like value
   and stored as a NumPy array. Required.

.. attribute:: OOSCurvature.y

   Northing or anonymised northing coordinates, supplied as an array-like value
   and stored as a NumPy array. Required.

.. _oos-geometry-outputs:

Geometry Outputs
~~~~~~~~~~~~~~~~

.. automethod:: OOSCurvature.get_arc_length

.. automethod:: OOSCurvature.get_angle

.. automethod:: OOSCurvature.get_curvature

FFT Smoother Class
------------------

.. autoclass:: pysubsea.oos_tools.FFTSmoother
   :show-inheritance:

.. _oos-fft-input-parameters:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: FFTSmoother.development

   Development identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Optional. Defaults to ``Predefined`` for
   every point when omitted.

.. attribute:: FFTSmoother.survey_type

   Survey types for each survey point, supplied as an array-like value and stored
   as a NumPy array. Optional. Defaults to ``Predefined`` for every point when
   omitted.

.. attribute:: FFTSmoother.pipeline_group

   Pipeline group identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Optional. Defaults to ``Predefined`` for
   every point when omitted.

.. attribute:: FFTSmoother.group_section_type

   Group section types for each survey point, supplied as an array-like value
   and stored as a NumPy array. Optional. Defaults to ``Predefined`` for every
   point when omitted.

.. attribute:: FFTSmoother.x

   Coordinates associated with the signal, supplied as an array-like value and
   stored as a NumPy array. Required.

.. attribute:: FFTSmoother.y

   Signal values for each survey point, supplied as an array-like value and
   stored as a NumPy array. Required.

.. attribute:: FFTSmoother.cutoff

   Cutoff used for FFT filtering, supplied as a numeric value or None.
   Required. A value of None disables filtering.

.. _oos-fft-smoothed-signal-outputs:

Smoothed Signal Outputs
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: FFTSmoother.get_y_smooth

.. _oos-frequency-spectrum-outputs:

Frequency Spectrum Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: FFTSmoother.get_freqs

.. automethod:: FFTSmoother.get_fft

.. automethod:: FFTSmoother.get_freqs_raw

.. automethod:: FFTSmoother.get_fft_raw

.. _oos-power-spectral-density-outputs:

Power Spectral Density Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: FFTSmoother.get_psd_development

.. automethod:: FFTSmoother.get_psd_survey_type

.. automethod:: FFTSmoother.get_psd_pipeline_group

.. automethod:: FFTSmoother.get_psd_group_section_type

.. automethod:: FFTSmoother.get_psd_freqs

.. automethod:: FFTSmoother.get_psd_vals

.. _oos-reconstructed-coordinate-outputs:

Reconstructed Coordinate Outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: FFTSmoother.get_x_recon

.. automethod:: FFTSmoother.get_y_recon

Gaussian Smoother Class
-----------------------

.. autoclass:: pysubsea.oos_tools.GaussianSmoother
   :show-inheritance:

.. _oos-gaussian-input-parameters:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: GaussianSmoother.development

   Development identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Optional. Defaults to ``Predefined`` for
   every point when omitted.

.. attribute:: GaussianSmoother.survey_type

   Survey types for each survey point, supplied as an array-like value and stored
   as a NumPy array. Optional. Defaults to ``Predefined`` for every point when
   omitted.

.. attribute:: GaussianSmoother.pipeline_group

   Pipeline group identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Optional. Defaults to ``Predefined`` for
   every point when omitted.

.. attribute:: GaussianSmoother.group_section_type

   Group section types for each survey point, supplied as an array-like value
   and stored as a NumPy array. Optional. Defaults to ``Predefined`` for every
   point when omitted.

.. attribute:: GaussianSmoother.x

   Anonymised easting coordinates, supplied as an array-like value and stored as
   a NumPy array. Required.

.. attribute:: GaussianSmoother.y

   Anonymised northing coordinates, supplied as an array-like value and stored
   as a NumPy array. Required.

.. attribute:: GaussianSmoother.bandwidth

   Bandwidth input for the Gaussian kernel, supplied as a numeric value.
   Required.

.. _oos-gaussian-smoothed-signal-outputs:

Smoothed Signal Outputs
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: GaussianSmoother.get_y_smooth

OOS Anonymisation Class
-----------------------

.. autoclass:: pysubsea.oos_tools.OOSAnonymisation
   :show-inheritance:

.. _oos-anonymisation-input-parameters:

Input Parameters
~~~~~~~~~~~~~~~~

.. attribute:: OOSAnonymisation.route_development

   Development identifiers for each route section, supplied as an array-like
   value and stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.route_pipeline_group

   Pipeline group identifiers for each route section, supplied as an array-like
   value and stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.route_pipeline

   Pipeline identifiers for each route section, supplied as an array-like value
   and stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.route_kp_from

   Start chainage for each route section, supplied as an array-like value and
   stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.route_kp_to

   End chainage for each route section, supplied as an array-like value and
   stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.route_pipeline_section_type

   Section type for each route section, supplied as an array-like value and
   stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.route_curve_radius

   Design curve radius for each route section, supplied as an array-like value
   and stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.survey_development

   Development identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.survey_type

   Survey type for each survey point, supplied as an array-like value and stored
   as a NumPy array. Required.

.. attribute:: OOSAnonymisation.survey_pipeline_group

   Pipeline group identifiers for each survey point, supplied as an array-like
   value and stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.survey_pipeline

   Pipeline identifiers for each survey point, supplied as an array-like value
   and stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.survey_kp

   Chainage for each survey point, supplied as an array-like value and stored as
   a NumPy array. Required.

.. attribute:: OOSAnonymisation.survey_easting

   Easting coordinates for each survey point, supplied as an array-like value
   and stored as a NumPy array. Required.

.. attribute:: OOSAnonymisation.survey_northing

   Northing coordinates for each survey point, supplied as an array-like value
   and stored as a NumPy array. Required.

.. _oos-anonymisation-processing:

Processing
~~~~~~~~~~

Call ``process`` before retrieving processed survey outputs. Its ``anonymise``
argument controls whether the additional cleaning and grouping steps run.

.. automethod:: OOSAnonymisation.process

.. _oos-route-data-outputs:

Route Data Outputs
~~~~~~~~~~~~~~~~~~

.. automethod:: OOSAnonymisation.get_route_development

.. automethod:: OOSAnonymisation.get_route_pipeline_group

.. automethod:: OOSAnonymisation.get_route_pipeline

.. automethod:: OOSAnonymisation.get_route_kp_from

.. automethod:: OOSAnonymisation.get_route_kp_to

.. automethod:: OOSAnonymisation.get_route_pipeline_section_type

.. automethod:: OOSAnonymisation.get_route_curve_radius

.. _oos-survey-data-outputs:

Survey Data Outputs
~~~~~~~~~~~~~~~~~~~

.. automethod:: OOSAnonymisation.get_survey_development

.. automethod:: OOSAnonymisation.get_survey_type

.. automethod:: OOSAnonymisation.get_survey_pipeline_group

.. automethod:: OOSAnonymisation.get_survey_pipeline

.. automethod:: OOSAnonymisation.get_survey_kp

.. automethod:: OOSAnonymisation.get_survey_easting

.. automethod:: OOSAnonymisation.get_survey_northing

.. _oos-survey-section-outputs:

Survey Section Outputs
~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: OOSAnonymisation.get_survey_section_type

.. automethod:: OOSAnonymisation.get_survey_section_no

.. automethod:: OOSAnonymisation.get_survey_section_kp_mod

.. automethod:: OOSAnonymisation.get_survey_section_easting_mod

.. automethod:: OOSAnonymisation.get_survey_section_northing_mod

.. automethod:: OOSAnonymisation.get_survey_feature

.. automethod:: OOSAnonymisation.get_survey_design_route_curve_radius

.. automethod:: OOSAnonymisation.get_survey_actual_route_curve_radius

.. _oos-survey-group-outputs:

Survey Group Outputs
~~~~~~~~~~~~~~~~~~~~

These outputs are populated by ``process(anonymise=True)``.

.. automethod:: OOSAnonymisation.get_survey_group_section_no

.. automethod:: OOSAnonymisation.get_survey_group_section_type

.. automethod:: OOSAnonymisation.get_survey_group_section_kp_mod

.. automethod:: OOSAnonymisation.get_survey_group_section_easting_mod

.. automethod:: OOSAnonymisation.get_survey_group_section_northing_mod
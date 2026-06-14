########
PySubsea
########

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

******************
Project Philosophy
******************

 **PySubsea** is an open-source codebase for pipeline and riser design. It was initiated and is developed by `Subsea Energies <https://www.subseaenergies.com>`_ to consolidate and automate tasks frequently encountered in subsea engineering workflows, ensuring they remain version-controlled and accessible within a structured repository.

 The project follows a corporate open-source approach focused on collaboration, experimentation, and the systematic compilation of engineering knowledge. **PySubsea** is maintained independently from client-specific or confidential work; instead, it serves as a shared engineering tool that captures practical insights in an open and reusable framework.

 The repository is publicly available to encourage collaboration and knowledge sharing across the subsea industry, while ensuring that all proprietary or conditential information is excluded. By making the project open, the wider community can review it, contribute to it, and build upon it, allowing the repository to continue improving beyond its original scope.
 
  - **PySubsea** is completely free to use under the `MIT License <https://github.com/py-subsea/py-subsea/blob/main/LICENSE>`_, including for users who only want to run the code without modifying it. The MIT License allows anyone to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software with minimal restrictions.

  - **PySubsea** is also open to contributions from users who want to add features, fix bugs, or improve documentation.

  - **Source code**: The source code is available on `GitHub <https://github.com/py-subsea/py-subsea>`_.

  - **PyPI Wheel**: The available wheel is on `PyPI <https://pypi.org/project/py-subsea>`_. Install with ``pip install pysubsea``.

*******************
Coorporate Partners
*******************

 The management of this open-source project is carried out by `Subsea Energies <https://www.subseaenergies.com>`_, the project sponsor and current maintainer.

 While **PySubsea** is currently a led under a corporate open-source approach by `Subsea Energies <https://www.subseaenergies.com>`_, the project is hosted under the dedicated  **PySubsea** GitHub organisation rather than an individual account.
 
 Although there is no immediate intention to formally announce or release the project or expand the team, the organisational setup allows for scalable and well-governed collaboration should it occur.

 **PySubsea** is also open to new sponsorship opportunities. Support may be provided either through funding or by contributing engineering resources. Such partnerships help ensure the project's continued growth, stability, and long-term sustainability. Organisations interested in sponsoring the project are encouraged to contact `Subsea Energies <https://www.subseaenergies.com>`_ at `info@subseaenergies.com <mailto:info@subseaenergies.com>`_.

********************************
How to Contribute to the Project
********************************

 Interested in contributing to this open-source project?
 
  - If you have a contribution in mind, please add it in `Discussions <https://github.com/py-subsea/py-subsea/discussions>`_.
  - If you have identified an issue with the code, please add it in `Issues <https://github.com/py-subsea/py-subsea/issues>`_.

********************************
PySubsea Python Library Versions
********************************
 THE REQUIREMENTS.txt file contains the libraries for which the script has been developed and shown to run.

 If some of libraries imported by PySubsea lead to issues, before running PySubsea for first time, follow these steps to activate a virtual environment from the REQUIREMENTS.TXT file:

  1. Open a Command Prompt or PowerShell and navigate to the folder where PySubsea is cloned and copy REQUIREMENTS.txt file.

     `$ cd path/to/py-subsea`

  2. In the folder where the code that imports PySubsea is saved, to create the virtual environment, run:

     `$ python -m venv env`

  3. To activate the virtual environement, run: [This command works in the VSCode's PowerShell. Command may vary in other shells]

     `$ env/Scripts/Activate.ps1`

  4. To install the necessary libraries, run:

     `$ pip install -r ./REQUIREMENTS.txt`

 Afterwards, the virtual environement must be activated before running PySubsea by using the command in Step 3.

########
Contents
########
.. toctree::
   :maxdepth: 1

   getting_started
   api_reference

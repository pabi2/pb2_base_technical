.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Connector
=========

This is a framework designed to build connectors with external systems,
usually called `Backends` in the documentation.

Documentation: http://odoo-connector.com

It features:

* A jobs queue

    In which the connectors can push functions (synchronization tasks)
    to be executed later.

* An event pattern

    The connectors can subscribe listener functions on the events,
    executed when the events are fired.

* Connector base classes

    Called ``ConnectorUnit``.

    Include base classes for the use in connectors, ready to be extended:

    * ``Synchronizer``: flow of an import or export
    * ``Mapper``: transform a record according to mapping rules
    * ``Binder``: link external IDs with local IDS
    * ``BackendAdapter``: adapter interface for the exchanges with the backend
    * But ``ConnectorUnit`` can be extended to accomplish any task

* A multi-backend support

    Each ``ConnectorUnit`` can be registered amongst a backend type (eg.
    Magento) and a backend version (allow to have a different ``Mapper``
    for each backend's version for instance)

It is used for example used to connect Magento_ and Prestashop_, but
also used with Solr, CMIS, ...

* Add Feature after restart (Jakkrich Edition)

	At restart service odoo, change job state ``started`` and ``enqueue`` to ``pending`` again.

* Add Feature run timeout (Jakkrich Edition)
	
	Add variables ``channels_time_real`` in openerp-server.conf after ``[options-connector]``, Should not be over variables ``limit_time_real``
	If over time, system will notify error and stop working.
	Format ``chanal_name:time_secord,chanal_name_2:time_secord``
	Ex. ``channels_time_real = root:3600,root.report:7200``

* Fix Host Master PGpool (Jakkrich Edition)
    
    Add variables ``host`` in openerp-server.conf after ``[options-connector]``
   
* Add Feature Stop Worker Job Runner (Jakkrich Edition)
  
    Add variables ``stop_job_runner`` in openerp-server.conf after ``[options-connector]``
    Ex. ``stop_job_runner = True``
    
.. _Magento: http://odoo-magento-connector.com
.. _Prestashop: https://github.com/OCA/connector-prestashop

Configuration and usage
=======================

This module does nothing on its own.  It is a ground for developing
advanced connector modules. For further information, please go on:
http://odoo-connector.com


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/connector/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/connector/issues/new?body=module:%20connector%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

Read the `contributors list`_

.. _contributors list: ./AUTHORS

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

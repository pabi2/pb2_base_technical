
=======================
GTS Database Connection
=======================

This module makes connection with other database to balance the load on current databases.
This module allows to configure different databases which may be on different
servers. Administrator can choose which report models to serve from which database 

Reports are fetched from another databases only if connection is configured in report
models/objects.

Usage
=====

* Go to 'Settings > Technical > DB Connection' menu and enter the IP address
(Example: 192.168.43.62), Database name (Example: test), Database user (Example: odoo),
Database password(Example: odoo) and Database Port(Example: 5432)

For IP Address:
if you are running another database on the same server then find your ip address using ifconfig.
Don't use localhost or 127.0.0.1.
Also the ip address should not have any http:// or https:// with it.

Example:
192.168.43.62


Then go to 'Settings > Technical > Database Structure > Models' menu and select the connection 
there on desired report models.

Example
=======

If you want 'Purchase Analysis' report to be fetched/served from another database
then you have to find it's model first.

'Purchase Analysis' report's model is 'purchase.report'.
Now go to 'Settings > Technical > Database Structure > Models' menu
and search for 'purchase.report' model. on form view, we can assign your desired connection,
if already configured.

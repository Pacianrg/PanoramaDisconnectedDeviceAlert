# PanoramaDisconnectedDeviceAlert
Send an email when devices show a 'disconnected' status in Panorama, and keep record of this as to not alert on the same device, and to alert when it returns to connected.

Change config.py to have Panorama username, password, and hostname/IP. (Recommended to use a Global Reader admin as no changes are made.) from_email, to_email, and smtp_server will be the SMTP settings, and were built configured with anonymous SMTP to M365 in mind.

FILE_PATH will be where the file storing the device name and its downtime goes. \\disconnected_devices.pickle Should remain at the end of it, and was configured with a Windows host in mind.

Intended to be ran as often as wanted as a scheduled task on a server with SMTP access.

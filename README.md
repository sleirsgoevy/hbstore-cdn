# hbstore-cdn

This program allows you to host custom package repository for [PS4 Homebrew Store](https://orbismandl.darksoftware.xyz/store.pkg).

## Usage

From the directory containing `hbstore.py` file, run:

```
python3 hbstore.py /path/to/pkgs/
```

where `/path/to/pkgs` is the directory containing your package files.

On Windows, the command will look like this:

```
python hbstore.py c:\path\to\pkgs\
```

**Note: superuser privileges are required to bind to port 80**

To redirect the app to your server, create a settings.ini file with the following contents:

```
[Settings]
temppath=/user/app
CDN=http://yourip
```

Then insert a USB drive with this file into the left USB port of the PS4 and start the application.

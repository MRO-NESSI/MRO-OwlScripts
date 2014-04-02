OwlScripts
==========

scripts for running the NESSI instrument.

NESSI.bsh
---------

NESSI.bsh is a BeanShell script for Owl. It has three responsibilities:

* Manually disabling imager reset between continuous readout exposures
* Retrieving telemetry from the NESSI controller and configuring Owl's
  FITS header output appropriately
* Starting each ramp automatically

# Quick Guide to Science

1. Launch owl (`owl&`)
1. If the 'Supported Configuration' box is empty, click the Setup button
   under Controller. Check 'Reset', check 'TIM Download' and select a
   correct firmware file (ask a programmer), check 'Power On' and check
   'Image Size' and enter 2048x2048. Click Apply (upper left) and wait while
   while the controller intializes (5s or so). Close the Setup window.
1. For 'Exp Time' (upper left) enter the sampling interval in seconds.
1. In the 'Supported Configuration' box, click the button to the left of
   'Continuous readout' and in the window that appears check the box and,
   in the tet box on the right, enter the number of samples in each ramp.
   Note that ramp time will equal Exp Time * Continuous Readout count,
   plus the readout time of each frame (about 420ms). Click Run and then
   Close.
1. Now, in the Script section, click the folder icon to the right of the
   text box and open NESSI.bsh. Click the run icon (farthest right).
1. In the NESSI control window, enter the number of ramps you would like
   to take and then the number of exposures in each ramp (**important:**
   this must be the same as the number you entered for the continuous
   readout count).
1. The 'Interramp Delay' box allows you to set an extra time, in seconds,
   to wait between ramps. This extra time is to prevent readout failures
   due to a ramp starting before the previous ramp ended (in case readout
   of the previous ramp took longer than usual). 0.5, the default, should
   be more than enough.
1. Click 'Expose'. The NESSI control script will automatically start
   the correct number of ramps in Owl, you can watch its progress in
   the log output window.

Should you lose interest in an exposure process, you can click Abort in
the NESSI script window. This will cause exposures to end after the end
of the current ramp (the ramps up to that point will be saved). If you
don't even want to wait for the current ramp to finish, you can then
click Abort (upper left) in the main Owl window.

Notes on Owl Scripts
--------------------

I have been frustrated by the documentation for the Owl scripting environment,
so here are some helpful notes.

If you would like to break content up in to multiple files in the main script
that will be run from Owl use "interp.source()" on the file name of the other
scripts. interp is an object representing the interpreter environment itself,
the source method will cause it to read and execute another file. This is the
only way I can find to bring external classes in to the working environment,
typical 'import' and direct reference fails for custom classes.

You can indeed implement Java interfaces in BeanShell, for things like
launching threads. See
http://www.jedit.org/users-guide/macro-tips-BeanShell.html for an MWE of this.

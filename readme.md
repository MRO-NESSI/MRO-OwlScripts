OwlScripts
==========

Owl scripts for running the NESSI instrument.

NESSI_Runner.bsh
----------------

Implements "sampling up the ramp" and provides a UI to configure ramp time,
number of samples, etc.

Notes on Owl Scripts
--------------------

I have been frustrated by the documentation for the Owl scripting environment,
so here are some helpful notes.

If you would like to break content up in to multiple files (as is done with
NESSI_Runner), in the main script that will be run from Owl use
"interp.source()" on the file name of the other scripts. interp is an object
representing the interpreter environment itself, the source method will
cause it to read and execute another file. This is the only way I can find
to bring external classes in to the working environment, typical 'import'
and direct reference fails for custom classes.

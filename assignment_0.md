# Assignment 0: set up your environment and understand the code structure

Assignment 0 will be graded pass/fail (it's easy, but you will be asked to drop the class if you do not do it), and the learning objectives are for you to familiarize yourself with some coding tools, as well as coding style:

- git
- uv
- pytest
- VS Code (optional, highly recommended), Python debugger

## Git ready

If you don't already have it, install [git](https://github.com/git-guides).
We will use git a lot. You can use it in the command line interface (CLI) or with a graphical user interface (GUI).
Especially if you aren't very familiar with git, I strongly recommend you to start with the CLI; it's much simpler and will force you to understand what you're doing.

Once you're ready, clone this repo.

## Set up your UV environment.

In this class, we will use [uv](https://docs.astral.sh/uv/) as our environment manager. You should install it, then run `uv venv --python 3.14` and `uv sync` in this folder to set up your project.

If you're not familiar with environment managers, or why they are important, see [here](https://xkcd.com/1987/), and in all seriousness, read the [Why and How sections here](https://realpython.com/python-virtual-environments-a-primer/?utm_source=chatgpt.com#why-do-you-need-virtual-environments).

## Run pendulum

Read through and run the pendulum simulation in assignment_0.py.
Set up the [Python debugge in VS Code or your favorite editor](https://code.visualstudio.com/docs/python/debugging), and step through the code, see where the dynamics are written in.

Add a phase portrait.

## Create a module for numerical integrators.

In `assignment_0.py`, the integration step is currently written out explicitly in the script's simulation loop with a simple Explicit Euler method. This integration method works, but is very sensitive and typically requires a small timestep. Run a sweep and find the largest timestep where the integration stays stable. Think about how you would do this.

Next, look at how the pendulum model is encapsulated in the `models` module, and do the same thing for the Euler integrator.
You should be able to import it as `from integrators import explicit_euler as integrator`.
Before implementing, consider the inputs and outputs, and how you will use it.

Finally, implement the implicit Euler method with the same signature, so you can drop it into the script as `from integrators import implicit_euler as integrator`, and not have to change the rest of the script. Find the largest timestep, and then use [`timeit`](https://www.geeksforgeeks.org/python/timeit-python-examples/) to compare how fast the code is with each integrator. Do the comparison once for the same timestep, and once with _equivalent_ timesteps (timesteps with the same accuracy).

## Implement a new model: bouncing ball

Your final task is to implement the dynamics of a bouncing ball.
Similar to the pendulum, you'll want to run some sanity checks to make sure it works well.
Before implementing, briefly describe the dynamics you expect to see and what checks you think make sense.
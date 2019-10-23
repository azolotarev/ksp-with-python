## Script description
Launches the rocket to 5,000 meters and lands somewhere near the launchpad.

Please note that this is a work in progress, I'm not satisfied with the script's performance.

## Demonstration
![Demo](https://media.giphy.com/media/ZaX7mfjQ2tkVXFigdA/giphy.gif)

## Suicide Burn
**Suicide burn** (also known as **hoverslam**) - a method of landing a rocket vehicle using rocket thrust,
where a precisely timed and metered rocket burn, at the moments before touchdown, is used to soft-land a rocket on its tail.
Precise altitude calculation for the start of suicide burn requires a ton of parameters,
such as: specific impulse of the engines, rocket mass at the start of the burn, rocket mass on the end of the burn,
atmosphere drag, the planet's gravitation and it's gradient, etc.

KSP provides almost everything necessary for calculations, but for now I've used this method:

After the rocket detects that the vertical speed is less than 0 (i.e. the rocket has started to fall)

1. get the current altitude, drag, vertical speed and the rocket's mass from kRPC
2. calculate the maximum thrust with relation to the altitude
3. enter 'while' loop where the script simulates the burn, it'll not exit the loop until simulated vertical speed and altitude is higher than 0. After each step of the simulation, add the traveled distance to the target altitude.
This method is not ideal, it's error is around 1 second due to the nature of calculations.
4. if the current altitude is lower than the target altitude, turn on all the engines and burn like hell.

This is more of a hack than a legitimate calculation, so it'll be changed to some more mathy stuff. It works, but it's not ideal and it requires precision throttle control at the end of the burn.

## Fine-tuning
To fine-tune the script for your rocket, you'll need to change the parameters under 'Block 2':
1. g - gravity of the planet.
2. Fvac - maximum thrust of your engines in the vacuum
3. ISPsea, ISPvac - engines' specific impulse at the sea level and the vacuum
4. fc - fuel consumption rate. Note that this and 'oc' parameters are for a full thrust.
5. oc - oxidizer consumption rate
6. n_engines - number of engines, duh

And maybe you should change the calc_thrust function, specifically the '106000' number if your rocket's thrust is not calculated correctly.

This is a fun and challenging problem to solve, be ready to crash *a lot* of rockets.


## Rocket
This script was tested on a Falcon 9 replica from [Tundra Exploration](https://forum.kerbalspaceprogram.com/index.php?/topic/166915-17x-tundra-exploration-v160-august-17th-restockalike-spacex-falcon-9-dragon-v2-and-starship-ro-compatible/) pack.


## Proportional-Integral-Derivative controller
[PID controller](https://en.wikipedia.org/wiki/PID_controller) allows for much higher accuracy and flexibility than just simple if-else statements and hardcoding the parameters, but it comes with a price: it requires fine-tuning and testing.

Code copypasted from https://github.com/krpc/krpc-library/blob/master/Art_Whaleys_KRPC_Demos/pid.py

Some learning links about PID controllers:
* [KSP Tutorial: PID controlled hovering using KOS](https://www.youtube.com/watch?v=LTKkAnWRcmo) by James Burch
* [PID Control - A brief introduction](https://www.youtube.com/watch?v=UR0hOmjaHp0) by Brian Douglas

## Code explanation

There'll be detailed walkthrough after I've done messing with the numbers.

**Block 1**

Open connection to the kRPC server; establish telemetry streams for altitude, velocity, drag; create PID controller object for throttle control.

**Block 2**

Some parameters for fine-tuning.

**Block 3**

Engage kRPC autopilot (I use it for stability control, like a gyroscope), launch the rocket

**Block 4**

Some kRPC 'wait for the event' magic. Wait until rocket reaches the target altitude.

**Block 5**

Calculate the suicide burn altitude

**Block 6**

Relight the engines, deploy landing legs. After the altitude is less than a 100 meters, engage precision throttle control with a PID controller.

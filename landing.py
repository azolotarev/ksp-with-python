import krpc
import time
from simple_pid import PID

def extend_fins(vessel):
    for part in vessel.parts.all:
        if part.name == 'Grid Fin M Titanium':
            for module in part.modules:
                if module.events == ['Extend Fins']:
                    module.trigger_event('Extend Fins')

def retract_fins(vessel):
    for part in vessel.parts.all:
        if part.name == 'Grid Fin M Titanium':
            for module in part.modules:
                if module.events == ['Retract Fins']:
                    module.trigger_event('Retract Fins')
                    
def calc_thrust(Fvac, A, h):
    return Fvac - (106000*A)*2.718**(-0.0002*h)

def ca(thrust, mass, d=0, g=g):
    """
    Calculates acceleration
    """
    return thrust/mass - d - g

def sb_alt(v_speed, mass, Fvac=Fvac, wl=wl, A=A, target=0):
    """
    Calculates the altitude at which to start the suicide burn
    """

    h = altitude()
    thrust = calc_thrust(Fvac, A, h)
    d = drag()[0]/mass/2.3

    while h >= 0 and v_speed >= 0:
        target += v_speed
        accel = ca(thrust, mass, d=-d, g=g)
        v_speed -= accel
        mass -= wl
        h -= v_speed
        thrust = calc_thrust(Fvac, A, h)

    target -= h/2

    return target


#Block 1
name='Falcon'
conn = krpc.connect(name)
vessel = conn.space_center.active_vessel
ref_frame = conn.space_center.ReferenceFrame.create_hybrid(
    position=vessel.orbit.body.reference_frame,
    rotation=vessel.surface_reference_frame)
flight = vessel.flight()
altitude = conn.add_stream(getattr, flight, 'surface_altitude')
velocity = conn.add_stream(getattr, vessel.flight(ref_frame), 'velocity')
drag = conn.add_stream(getattr, flight, 'drag')
throttle_control = PID(P=.25, I=.025, D=.0025)
throttle_control.ClampI = 20

#Block 2
g = 9.80665 #gravity of the planet
Fvac = 7_054_530 #force at max throttle in vacuum
ISPsea = 282 #isp at sea level
ISPvac = 311 # isp in vacuum
fc = 22.545 #fuel consumption at max throttle 
oc = 27.555 #oxidizer consumption at max throttle
n_engines = 9 #number of engines
fo_utm = 200 #fuel and oxidizer KSP units to mass ratio, 200 units = 1 tonn
A = (Fvac/101325) * (1-ISPsea/ISPvac) #engine specific constant for thrust/alt calculations
wl = (((fc+oc) * n_engines) / fo_utm) * 1000 #summary weight loss in kilograms per second at max throttle


target_alt = 5000.0
print('Setting', target_alt, 'as target alt')



#Block 3
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch = 90

print('Igniting engines')
vessel.control.activate_next_stage()
vessel.control.throttle = 1

print('Retracting tower')
vessel.control.activate_next_stage()


#Block 4
alt = conn.get_call(getattr, flight, 'mean_altitude')
expr = conn.krpc.Expression.greater_than(
    conn.krpc.Expression.call(alt),
    conn.krpc.Expression.constant_double(target_alt))
event = conn.krpc.add_event(expr)
with event.condition:
    print('Reaching target altitude...')
    event.wait()

#Block 5
print('Altitude reached, engine cutoff')
vessel.control.throttle = 0

print('Sleeping until the vertical speed is negative')
while velocity()[0] > 3:
    time.sleep(0.2)

print('Deploying fins')
extend_fins(vessel)
for part in vessel.parts.control_surfaces:
    part.inverted = True

print('Calculating the suicide burn altitude')
while altitude()>target_alt:
    mass = vessel.mass
    v_speed = abs(velocity()[0])
    target_alt = sb_alt(v_speed, mass, n_engines=n_engines)
    #print(target_alt, v_speed)



#Block 6
print('Suicide burn')
vessel.control.throttle = 1

while altitude() > 100:
    if altitude() < 300 and not vessel.control.gear:
        vessel.control.gear = True
    time.sleep(0.05)

print('Landing burn')
throttle_control.setpoint(0)
while altitude() > 26:
    v_speed = velocity()[0]
    output = throttle_control.update(altitude()+(v_speed*6))*0.07
    vessel.control.throttle = output
    print(output, altitude(), v_speed)


print('The', name, 'has landed.')
vessel.control.throttle = 0
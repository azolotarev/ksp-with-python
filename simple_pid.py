import time

class PID(object):
    '''
    Generic PID Controller Class
    Based on the PID recipe at :
    http://code.activestate.com/recipes/577231-discrete-pid-controller/
    and the code and discussions in the blog at:
    http://brettbeauregard.com/blog/2011/04/
    improving-the-beginners-pid-introduction/
    An instance is created with the format
    your_pid=PID(P=.0001, I=0.00001, D=0.000001)
    Finding the right values for those three gain numbers is called 'tuning' and
    that's beyond the scope of this doc string!  
    Use your_pid.setpoint(X) to set the target output value of the controller. 


    Regularly call your_pid.update(Y), passing it the input data that the
    controller should respond to.
    output_data = your_pid.update(input_data)
    '''
    def __init__(self, P=1.0, I=0.1, D=0.01):   
        self.Kp = P    #P controls reaction to the instantaneous error
        self.Ki = I    #I controls reaction to the history of error
        self.Kd = D    #D prevents overshoot by considering rate of change
        self.P = 0.0
        self.I = 0.0
        self.D = 0.0
        self.SetPoint = 0.0  #Target value for controller
        self.ClampI = 1.0  #clamps i_term to prevent 'windup.'
        self.LastTime = time.time()
        self.LastMeasure = 0.0
                
    def update(self,measure):
        now = time.time()
        change_in_time = now - self.LastTime
        if not change_in_time:
            change_in_time = 1.0   #avoid potential divide by zero if PID just created.
       
        error = self.SetPoint - measure
        self.P = error
        self.I += self.clamp_i(error)
        self.D = (measure - self.LastMeasure) / (change_in_time)
        self.LastMeasure = measure  # store data for next update
        self.lastTime = now

        return (self.Kp * self.P) + (self.Ki * self.I) - (self.Kd * self.D)

    def clamp_i(self, i):   
        if i > self.ClampI:
            return self.ClampI
        elif i < -self.ClampI:
            return -self.ClampI
        else:
            return i
        
    def setpoint(self, value):
        self.SetPoint = value
        self.I = 0.0

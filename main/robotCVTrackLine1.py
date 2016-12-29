print "Importing libraries"
import time
import robotBuilder

##  Build Robot from robotBuilder (edit robotBuilder to customize robot)
print "Configuring robot"
rpb202 = robotBuilder.build(True)

##  Create direct pointer to camera object tracker
print "Connecting camera"
lineTracker = rpb202.camera.lineTracker
lineTracker.setDisplay(False)


try:

    print "Starting main program"
##  Initialization of turn and speed variables
    turn = 0  # Turn speed
    turnCorr = 0  # Turn speed correction factor
    lastTurn = 0  # Last turn speed

    fwd = 0  # Forward speed
    speedCorr = 1  # Forward speed correction factor

##  Error terms for PID controller
    err = 0  # Horizontal position error (target rel to camera center)
    errInt = 0  # Integral of position error
    errDer = 0  # Derivative of position error
    errPrev = 0  # Previous error (for derivative calculation)

##  PID controler gains
    Kp = .105  #.18 #.20 # Proportional term gain
    Ki = .03  #.06 #.04 # Integral term gain
    Kd = .007  #.012 #.007 # Derivative term gain

##  Main loop time step
    fps = 20.
    tStep = 1 / fps

##  Launch object tracker
    lineTracker.trackLines(fps)
    time.sleep(1)

##  Main loop
    end = False
    while not end:

        t0 = time.time()

##      Check if object in sight
        if lineTracker.hasLines():

##          Calculate error terms
            err = lineTracker.getLinesHPos(0)
            errInt += err * tStep
            errDer = (err - errPrev) / tStep
            errPrev = err

##      Otherwise reset error terms to zero
        else:
            err = 0
            errInt = 0
            errDer = 0
            errPrev = 0
            fwd = .15
            
##          Turn in last turn direction
            if lastTurn < 0:
                turn = -.15
            else:
                turn = .15

##      Calculate turn correction factor - PID controler
        turnCorr = Kp * err + Ki * errInt + Kd * errDer

##      Calculate speed correction factor (slow-down if large error)
        speedCorr = 1 - 0.75 * abs(err)

##      Apply speed and turn correction factors
        fwd = fwd * speedCorr
        turn = turn + turnCorr

##      Move robot
        rpb202.move(fwd, turn)

##      Reset turn and speed variables
        lastTurn = turn
        turn = 0
        turnCorr = 0
        fwd = .5
        speedCorr = 1

##      Calculate and apply delay to reach time step
        dt = time.time() - t0
        if dt < tStep:
            time.sleep(tStep - dt)

##  End of main loop. Stop robot and threads
    rpb202.stop()
    rpb202.camera.stop()
    lineTracker.stop()
        
##  Use Ctrl-C to end
except KeyboardInterrupt:
    rpb202.stop()
    rpb202.camera.stop()
    lineTracker.stop()
    print "\nExiting program"
    time.sleep(1)
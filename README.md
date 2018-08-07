# autoRC
Street is danger, why not making autonomous toy?

Autonomous Remote Controlled (toy) car using deep learning. Raspberry Pi, PiCar, Python

You can find hardware on [here](https://www.sunfounder.com/free/p1429u49266), I'm too lazy to build from scratch.

![PiCar](/docs/assets/picar-front.jpg)

## Design
Inspired by Robot Operating System ([ROS](http://www.ros.org/)) each components is a Node and run in it own process. A Node can be sensors, controller, motion planner, camera, Deep Learning pilot... which talk to each other via pub/sub like system.

![PiCar](/docs/assets/noaharch.png)

Current implementation using Python's built in multiprocessing manager that allow sharing objects, data between Processes. Pros: Utilize CPU cores, avoid PIL, run nodes over network from different machine. Cons: Data are being pickle/unpickle multiple time and send over network which is slower than thread. May consider using more decend message queue like Redis.

## Images

![First attempt](/docs/assets/noahcar-firsttry.gif)  |  [![Second attempt](/docs/assets/noahcar2ndtry.gif)](https://www.youtube.com/watch?v=BVkJ1vlqxoQ "Self driving car 2nd attempt")
:-------------------------:|:-------------------------:
Paper road            |  Duct tape border

![Control UI](/docs/assets/control-ui.png)

## Requirement
- Raspberry Model 2/3 or greater
- Python 3.5
- OpenCV (optional) or PyGame camera (just for capture video)
- SD card 8gb or more
- Car kit (robot HAT, mortor controller... mine just use picar)
- Webcam or Picamera

## Documents
1. Setup Hardware
  - [Raspberry Pi setup](/docs/rasp-setup.md)
  - [Car setup](/docs/car-setup.md)
2. [Setup software](/docs/software-setup.md)
3. Run, record
4. Training
5. Autopilot


## Run
```
cd noahcar
. env/bin/activate
python manage.py start
```

# Computer Simulation

what is the folder that should be unzipped?

Unzip this file:

mujoco_humanoid_workshop.zip

After extraction, it should create the folder:

mujoco_humanoid_workshop/

Run:

unzip mujoco_humanoid_workshop.zip
cd mujoco_humanoid_workshop

The folder should contain:

README.md
requirements.txt
common.py
exercise_01_inspect.py
exercise_02_pose.py
exercise_03_contacts.py
exercise_04_push_test.py
models/

Download it here:

exercise_01_inspect.py crashes with seg fault

I found a race-condition bug in the supplied scripts. exercise_01_inspect.py changed viewer.opt immediately after launching the passive viewer, without using viewer.lock(). MuJoCo requires passive-viewer state changes to be protected by that lock.

Download the corrected package:MuJoCo workshop](sandbox:/mnt/data/mujoco_humanoid_workshop_fixed.zip)

Replace your existing folder, then recreate the environment:

unzip mujoco_humanoid_workshop_fixed.zip
cd mujoco_humanoid_workshop

rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

First test without graphics:

python exercise_01_inspect.py --headless --duration 0.1

This should finish with:

Simulation completed at t=0.10 s

Then test the standalone MuJoCo viewer:

python -m mujoco.viewer --mjcf=models/simple_humanoid.xml

Finally run the corrected exercise:

python exercise_01_inspect.py

The essential correction in Exercise 1 is that this unsafe line was removed:

viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = True

Exercises 3 and 4 now use the required locking pattern:

with viewer.lock():
    viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = True
    viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTFORCE] = True

viewer.sync()

I verified the corrected XML and all four scripts in headless mode with MuJoCo 3.10.0. I could not verify the graphical window in this execution environment because it does not provide a usable desktop display.

If the standalone viewer command also segfaults, the workshop code is no longer the likely cause; that indicates an OpenGL/GLFW or mixed-environment problem. MuJoCo provides its interactive viewer through the Python package, while launch_passive uses a separate viewer thread. In that case, run:

python -X faulthandler exercise_01_inspect.py

and avoid mixing Conda-provided GLFW/OpenGL libraries with a pip-installed MuJoCo environment.

can you make a downloadable .md file out of this?


not the segfault fix, the tutorial


Library
/
ADC Prep
/mujoco_humanoid_workshop_tutorial.md

# Humanoid Robotics in MuJoCo

## Two-Hour Hands-On Workshop Tutorial

## 1. Workshop purpose

This workshop introduces the simulation concepts needed for humanoid robotics using MuJoCo.

The workshop focuses entirely on the simulator. It does not use:

- machine learning;
- reinforcement learning;
- Gymnasium;
- Stable-Baselines3;
- ROS;
- trajectory optimization.

The main topics are:

- MJCF model structure;
- floating-base humanoids;
- generalized coordinates;
- joint actuators;
- scripted posture changes;
- contact forces;
- friction;
- centre of mass;
- external disturbances;
- fall detection.

The workshop uses a simplified humanoid model first. A Unitree G1 model can be shown at the end as a more realistic example.

---

## 2. Learning outcomes

At the end of the workshop, students should be able to:

1. load an MJCF humanoid model;
2. identify bodies, joints, geoms, sites, actuators, sensors, and keyframes;
3. explain the difference between `MjModel` and `MjData`;
4. inspect `qpos`, `qvel`, and `ctrl`;
5. reset a simulation using a keyframe;
6. command position actuators;
7. generate a smooth scripted posture;
8. visualize and measure foot contact;
9. modify friction parameters;
10. apply an external force;
11. define a simple fall criterion;
12. explain why a valid humanoid pose is not necessarily dynamically stable.

---

## 3. Recommended workshop structure

| Time | Activity |
|---:|---|
| 0–10 min | Introduction and demonstration |
| 10–30 min | Exercise 1: Inspect the humanoid |
| 30–55 min | Exercise 2: Scripted posture control |
| 55–65 min | Discussion and short break |
| 65–90 min | Exercise 3: Contact, CoM, and friction |
| 90–115 min | Exercise 4: Push test and fall detection |
| 115–120 min | Unitree G1 comparison and conclusions |

---

# Part I — Installation and preparation

## 4. Recommended environment

Recommended system:

- Ubuntu 22.04 or newer;
- Python 3.10 or newer;
- working OpenGL desktop environment;
- one computer per student or student pair.

The workshop requires only:

```text
mujoco
numpy
```

---

## 5. Extract the workshop package

Unzip the workshop archive:

```bash
unzip mujoco_humanoid_workshop_fixed.zip
cd mujoco_humanoid_workshop
```

The folder should contain:

```text
mujoco_humanoid_workshop/
├── README.md
├── requirements.txt
├── common.py
├── exercise_01_inspect.py
├── exercise_02_pose.py
├── exercise_03_contacts.py
├── exercise_04_push_test.py
└── models/
    └── simple_humanoid.xml
```

---

## 6. Create a Python virtual environment

Create the environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Install the requirements:

```bash
python -m pip install -r requirements.txt
```

Verify MuJoCo:

```bash
python -c "import mujoco; print(mujoco.__version__)"
```

---

## 7. Test the model without graphics

Run:

```bash
python exercise_01_inspect.py --headless --duration 0.1
```

Expected final output:

```text
Simulation completed at t=0.10 s
```

This confirms that:

- MuJoCo is installed;
- the XML model compiles;
- the physics loop works.

---

## 8. Test the graphical viewer

Run:

```bash
python -m mujoco.viewer --mjcf=models/simple_humanoid.xml
```

A humanoid model should appear above the floor.

Close the viewer before continuing.

---

# Part II — Fundamental MuJoCo concepts

## 9. `MjModel` and `MjData`

A basic MuJoCo program begins with:

```python
import mujoco

model = mujoco.MjModel.from_xml_path(
    "models/simple_humanoid.xml"
)

data = mujoco.MjData(model)
```

### `MjModel`

`MjModel` contains the compiled model definition.

Examples include:

- body masses;
- joint types;
- actuator gains;
- geometry dimensions;
- friction coefficients;
- sensor definitions;
- simulation timestep.

The model is mostly constant during a simulation.

### `MjData`

`MjData` contains the changing simulation state.

Examples include:

- joint positions;
- joint velocities;
- actuator commands;
- body positions;
- contact information;
- sensor values;
- simulation time.

---

## 10. The simulation loop

A simple loop is:

```python
while simulation_is_running:
    data.ctrl[:] = control_command
    mujoco.mj_step(model, data)
```

`mj_step`:

1. evaluates forces;
2. solves contacts and constraints;
3. calculates accelerations;
4. integrates the state;
5. advances simulation time.

The simulation timestep is stored in:

```python
model.opt.timestep
```

For example:

```xml
<option timestep="0.002"
        gravity="0 0 -9.81"/>
```

A timestep of `0.002` seconds corresponds to:

\[
f = \frac{1}{0.002} = 500\ \text{Hz}
\]

---

# Part III — The humanoid model

## 11. Main MJCF sections

Open:

```text
models/simple_humanoid.xml
```

The major sections are:

```xml
<mujoco>
    <option/>
    <default/>
    <asset/>
    <worldbody/>
    <equality/>
    <actuator/>
    <sensor/>
    <keyframe/>
</mujoco>
```

---

## 12. Bodies

A body represents a rigid coordinate frame in the kinematic tree.

Example:

```xml
<body name="pelvis" pos="0 0 0.92">
```

A child body is positioned relative to its parent.

Example:

```xml
<body name="left_shin" pos="0 0 -0.36">
```

This means the shin frame is positioned 0.36 m below its parent body.

The simplified hierarchy is:

```text
pelvis
├── torso
│   ├── head
│   ├── left_arm
│   └── right_arm
├── left_thigh
│   └── left_shin
│       └── left_foot
└── right_thigh
    └── right_shin
        └── right_foot
```

---

## 13. Joints

A joint defines relative motion between a body and its parent.

Example hinge joint:

```xml
<joint name="left_knee"
       type="hinge"
       axis="0 1 0"
       range="0 2.1"/>
```

This joint:

- rotates around the local \(y\)-axis;
- has a minimum angle of 0 rad;
- has a maximum angle of 2.1 rad.

Convert the maximum to degrees:

\[
2.1 \cdot \frac{180}{\pi}
\approx 120.3^\circ
\]

---

## 14. The floating base

The pelvis has a free joint:

```xml
<freejoint name="root"/>
```

A free joint allows:

- translation in \(x\);
- translation in \(y\);
- translation in \(z\);
- rotation around all three axes.

A free joint occupies:

- 7 entries in `qpos`;
- 6 entries in `qvel`.

### Position representation

The free joint position uses:

- 3 Cartesian coordinates;
- 4 quaternion coordinates.

Therefore:

\[
n_{q,\mathrm{free}} = 3 + 4 = 7
\]

### Velocity representation

The free joint velocity uses:

- 3 linear velocities;
- 3 angular velocities.

Therefore:

\[
n_{v,\mathrm{free}} = 3 + 3 = 6
\]

The teaching humanoid has:

- one free joint;
- twelve hinge joints.

Therefore:

\[
n_q = 7 + 12 = 19
\]

\[
n_v = 6 + 12 = 18
\]

---

## 15. Geoms

A geom can provide:

- visual shape;
- collision shape;
- mass;
- inertia;
- contact properties.

Example:

```xml
<geom name="left_foot_geom"
      type="box"
      size="0.12 0.05 0.03"
      friction="0.9 0.005 0.0001"/>
```

A box `size` specifies half-dimensions.

Therefore, this foot has approximate full dimensions:

\[
0.24 \times 0.10 \times 0.06\ \text{m}
\]

---

## 16. Sites

A site is a reference location or volume.

Sites are often used for:

- sensors;
- end-effector markers;
- contact measurement regions;
- visualization;
- force application reference points.

Example:

```xml
<site name="left_foot_touch_site"
      type="box"
      size="0.12 0.05 0.015"/>
```

---

## 17. Actuators

The workshop uses position actuators.

Example:

```xml
<position name="left_knee_act"
          joint="left_knee"
          kp="140"
          ctrlrange="0 2.1"/>
```

The command is written to:

```python
data.ctrl
```

For a position actuator, the control value acts as a desired joint position.

However, the joint is not teleported to that position. The actuator generates force based on the actuator model.

The resulting motion also depends on:

- inertia;
- gravity;
- damping;
- contact;
- actuator gain;
- constraints;
- timestep.

---

## 18. Keyframes

Keyframes store predefined simulation states.

Example:

```xml
<keyframe>
    <key name="stand"
         qpos="..."
         ctrl="..."/>

    <key name="crouch"
         qpos="..."
         ctrl="..."/>
</keyframe>
```

Reset to a keyframe:

```python
key_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_KEY,
    "stand",
)

mujoco.mj_resetDataKeyframe(
    model,
    data,
    key_id,
)

mujoco.mj_forward(model, data)
```

`mj_forward` recalculates derived quantities after manually changing the state.

---

## 19. Pelvis weld

The model includes an equality constraint:

```xml
<equality>
    <weld name="pelvis_weld"
          body1="pelvis"/>
</equality>
```

This weld can connect the pelvis to the world.

### Fixed-base mode

Used in Exercises 1 and 2.

The humanoid cannot fall.

This allows students to focus on:

- model structure;
- joint coordinates;
- actuator commands;
- scripted posture changes.

### Floating-base mode

Used in Exercises 3 and 4.

The weld is disabled from Python:

```python
weld_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_EQUALITY,
    "pelvis_weld",
)

data.eq_active[weld_id] = 0
```

The humanoid can then:

- translate;
- rotate;
- slip;
- tip;
- fall.

---

# Part IV — Exercise 1: Inspect the humanoid

## 20. Objective

Understand how an MJCF description becomes an indexed numerical model.

## 21. Run the exercise

```bash
python exercise_01_inspect.py
```

The script prints:

- body count;
- joint count;
- number of position coordinates;
- number of velocity coordinates;
- actuator count;
- sensor count;
- joint names;
- joint ranges;
- `qpos` addresses;
- degree-of-freedom addresses;
- actuator names;
- sensor names.

---

## 22. Student task: inspect the model dimensions

Expected values are approximately:

```text
Bodies:               12
Joints:               13
Position coordinates: 19
Velocity coordinates: 18
Actuators:            12
Sensors:              6
Equality constraints: 1
```

Ask:

1. Why are there more bodies than actuators?
2. Why is `nq` different from `nv`?
3. Why does the head have no actuator?
4. Which joint represents the floating base?

---

## 23. Student task: inspect joint names

A typical inspection loop is:

```python
for joint_id in range(model.njnt):
    name = mujoco.mj_id2name(
        model,
        mujoco.mjtObj.mjOBJ_JOINT,
        joint_id,
    )

    print(joint_id, name)
```

Students should identify:

```text
root
left_hip_yaw
left_hip_roll
left_hip_pitch
left_knee
left_ankle_pitch
left_ankle_roll
right_hip_yaw
right_hip_roll
right_hip_pitch
right_knee
right_ankle_pitch
right_ankle_roll
```

---

## 24. Student task: modify a material

Find:

```xml
<material name="left_mat"
          rgba="0.25 0.65 0.35 1"/>
```

Change it to:

```xml
<material name="left_mat"
          rgba="0.8 0.2 0.8 1"/>
```

Restart:

```bash
python exercise_01_inspect.py
```

The model is compiled when loaded. XML changes do not affect a model that is already running.

---

## 25. Student task: modify one joint limit

Find:

```xml
<joint name="left_knee"
       range="0 2.1"/>
```

Change it temporarily:

```xml
<joint name="left_knee"
       range="0 1.2"/>
```

Restart the simulation and observe whether the crouching keyframe or commanded posture remains feasible.

Restore the original value afterward.

---

## 26. Exercise 1 discussion

Ask:

- Which parts are visual only?
- Which parts participate in collisions?
- Why does the pelvis need a free joint?
- Why are joint positions stored in an array?
- Why are names converted to integer IDs?

### Main takeaway

The XML is a human-readable model description. MuJoCo compiles it into numerical arrays used by the physics engine.

---

# Part V — Exercise 2: Scripted posture control

## 27. Objective

Command the humanoid to move smoothly between standing and crouching poses.

## 28. Run the exercise

```bash
python exercise_02_pose.py
```

The robot should repeatedly move:

```text
standing → crouching → standing
```

The pelvis is fixed during this exercise.

---

## 29. Actuator order

The control vector contains 12 values:

```text
0  left hip yaw
1  left hip roll
2  left hip pitch
3  left knee
4  left ankle pitch
5  left ankle roll
6  right hip yaw
7  right hip roll
8  right hip pitch
9  right knee
10 right ankle pitch
11 right ankle roll
```

A crouching reference may be:

```python
crouch = [
    0.0, 0.0, -0.45, 0.90, -0.45, 0.0,
    0.0, 0.0, -0.45, 0.90, -0.45, 0.0,
]
```

For each leg:

\[
q_{\mathrm{hip}}
+
q_{\mathrm{knee}}
+
q_{\mathrm{ankle}}
=
-0.45 + 0.90 - 0.45 = 0
\]

This helps keep the foot approximately parallel to the floor.

---

## 30. Linear interpolation

The simplest interpolation is:

\[
q_{\mathrm{ref}}(u)
=
q_{\mathrm{start}}
+
u
\left(
q_{\mathrm{goal}}
-
q_{\mathrm{start}}
\right)
\]

where:

\[
0 \leq u \leq 1
\]

Python:

```python
q_ref = q_start + u * (q_goal - q_start)
```

This creates a constant desired velocity during the segment, but the desired velocity changes abruptly at the beginning and end.

---

## 31. Smoothstep interpolation

The workshop uses:

\[
s(u)=3u^2-2u^3
\]

Then:

\[
q_{\mathrm{ref}}(u)
=
q_{\mathrm{start}}
+
s(u)
\left(
q_{\mathrm{goal}}
-
q_{\mathrm{start}}
\right)
\]

Properties:

\[
s(0)=0
\]

\[
s(1)=1
\]

\[
s'(0)=0
\]

\[
s'(1)=0
\]

Python:

```python
def smoothstep(value: float) -> float:
    value = float(np.clip(value, 0.0, 1.0))
    return 3.0 * value**2 - 2.0 * value**3
```

---

## 32. Student task: compare linear and smooth motion

Replace:

```python
return 3.0 * value**2 - 2.0 * value**3
```

with:

```python
return value
```

Run:

```bash
python exercise_02_pose.py
```

Compare:

- movement onset;
- movement termination;
- visible oscillation;
- tracking error;
- apparent smoothness.

Restore the smoothstep function afterward.

---

## 33. Student task: modify actuator gain

Find the position actuator default:

```xml
<position kp="140"
          ctrllimited="true"/>
```

Test:

```xml
<position kp="40"
          ctrllimited="true"/>
```

Then:

```xml
<position kp="300"
          ctrllimited="true"/>
```

Record:

| Gain | Tracking speed | Tracking error | Oscillation |
|---:|---|---|---|
| 40 | | | |
| 140 | | | |
| 300 | | | |

### Expected observations

Low gain:

- slower response;
- larger position error;
- softer movement.

High gain:

- faster response;
- smaller static error;
- possibly stronger oscillation;
- larger forces;
- greater numerical sensitivity.

---

## 34. Student task: modify joint damping

Find:

```xml
<joint damping="3"
       armature="0.02"
       limited="true"/>
```

Test:

```xml
damping="0.3"
```

Then:

```xml
damping="10"
```

Record the effect.

### Expected observations

Low damping:

- more oscillation;
- longer settling;
- freer motion.

High damping:

- reduced oscillation;
- slower motion;
- stronger resistance to rapid changes.

---

## 35. Exercise 2 discussion

Ask:

1. Does `data.ctrl` directly set `qpos`?
2. Why does the actual position lag behind the reference?
3. Why can high gains cause instability?
4. Why did we fix the pelvis?
5. Would the same command work if link masses were doubled?

### Main takeaway

An actuator command creates force. It does not directly replace the simulated joint state.

---

# Part VI — Discussion and short break

## 36. Suggested questions

1. Why did we fix the pelvis during the first two exercises?
2. What changes when the floating base is released?
3. Can a robot follow all joint commands and still fall?
4. Is joint-space tracking identical to balance control?
5. Why can an upright pose be dynamically unstable?

The central idea is:

> Good joint tracking does not automatically produce whole-body stability.

---

# Part VII — Exercise 3: Contact, centre of mass, and friction

## 37. Objective

Observe floor contact, foot forces, centre of mass, slipping, and load transfer.

## 38. Run the default experiment

```bash
python exercise_03_contacts.py --friction 0.9
```

The script:

1. loads the standing keyframe;
2. disables the pelvis weld;
3. enables contact visualization;
4. reads foot contact sensors;
5. reads the centre-of-mass sensor;
6. applies a small lateral force;
7. measures foot displacement.

---

## 39. Viewer locking

When using the passive viewer, modify viewer state while holding the viewer lock:

```python
with viewer.lock():
    viewer.opt.flags[
        mujoco.mjtVisFlag.mjVIS_CONTACTPOINT
    ] = True

    viewer.opt.flags[
        mujoco.mjtVisFlag.mjVIS_CONTACTFORCE
    ] = True

viewer.sync()
```

This avoids race conditions between the simulation thread and the viewer thread.

---

## 40. Foot touch sensors

The XML contains:

```xml
<touch name="left_foot_force"
       site="left_foot_touch_site"/>

<touch name="right_foot_force"
       site="right_foot_touch_site"/>
```

The touch sensor returns a non-negative scalar representing the summed normal contact force associated with contacts in the sensor site.

Read sensor data:

```python
sensor_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_SENSOR,
    "left_foot_force",
)

start = model.sensor_adr[sensor_id]
dimension = model.sensor_dim[sensor_id]

left_force = data.sensordata[
    start:start + dimension
]
```

---

## 41. Centre-of-mass sensor

The XML contains:

```xml
<subtreecom name="humanoid_com"
            body="pelvis"/>
```

The sensor returns:

\[
p_{\mathrm{CoM}}
=
\begin{bmatrix}
x_{\mathrm{CoM}}\\
y_{\mathrm{CoM}}\\
z_{\mathrm{CoM}}
\end{bmatrix}
\]

For a basic balance interpretation, use the horizontal projection:

\[
p_{\mathrm{CoM,xy}}
=
\begin{bmatrix}
x_{\mathrm{CoM}}\\
y_{\mathrm{CoM}}
\end{bmatrix}
\]

For static balance, the projected centre of mass should normally remain inside the support region formed by the contacting feet.

This is only an introductory approximation. Dynamic balance also depends on:

- velocity;
- angular momentum;
- contact forces;
- centre of pressure;
- future motion.

---

## 42. Student task: compare left and right foot force

Before the disturbance:

```text
left force ≈ right force
```

During a lateral disturbance:

```text
left force ≠ right force
```

Ask:

- Which foot becomes more loaded?
- Does the foot with greater force necessarily move less?
- Does force difference directly indicate body velocity?

The answer to the last question is no. Contact force and body velocity are related through dynamics, but they are not the same quantity.

---

## 43. Friction parameters

The floor geom contains:

```xml
friction="0.9 0.005 0.0001"
```

The three components correspond to:

1. sliding friction;
2. torsional friction;
3. rolling friction.

For this workshop, the first value is the most important.

---

## 44. Student task: friction experiment

Run:

```bash
python exercise_03_contacts.py --friction 0.9
```

Then:

```bash
python exercise_03_contacts.py --friction 0.3
```

Then:

```bash
python exercise_03_contacts.py --friction 0.05
```

Record:

| Sliding friction | Left-foot displacement | Right-foot displacement | Visible slipping |
|---:|---:|---:|---|
| 0.90 | | | |
| 0.30 | | | |
| 0.05 | | | |

Expected trend:

- high friction resists sliding;
- low friction allows larger foot displacement;
- very low friction may produce sliding before strong body tilt.

---

## 45. Student task: modify the lateral disturbance

Run:

```bash
python exercise_03_contacts.py \
    --friction 0.3 \
    --lateral-force 10
```

Then:

```bash
python exercise_03_contacts.py \
    --friction 0.3 \
    --lateral-force 40
```

Observe:

- load transfer;
- foot sliding;
- torso tilt;
- contact loss;
- whole-body translation.

---

## 46. Contact versus stability

A humanoid can have both feet touching the floor and still be unstable.

Possible situations include:

- centre of mass leaving the support region;
- insufficient friction;
- excessive angular velocity;
- one foot unloading;
- contact occurring only at an edge;
- feet sliding together.

### Main takeaway

Contact is not simply “on” or “off.” It has geometry, forces, friction, and motion.

---

# Part VIII — Exercise 4: Push test and fall detection

## 47. Objective

Apply a repeatable external disturbance and measure whether the humanoid falls.

## 48. Run the push test

```bash
python exercise_04_push_test.py --force 30
```

The script applies a horizontal force to the torso.

---

## 49. External force array

MuJoCo provides:

```python
data.xfrc_applied
```

Each body receives a six-component spatial force:

```text
Fx Fy Fz Tx Ty Tz
```

Apply a force in the world \(x\)-direction:

```python
torso_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_BODY,
    "torso",
)

data.xfrc_applied[torso_id, 0] = 30.0
```

Clear the force afterward:

```python
data.xfrc_applied[torso_id, :] = 0.0
```

---

## 50. Push timing

The force is applied only during a defined interval:

```python
if push_start <= data.time < push_start + push_duration:
    data.xfrc_applied[torso_id, 0] = push_force
else:
    data.xfrc_applied[torso_id, :] = 0.0
```

Typical settings:

```text
push_start    = 0.50 s
push_duration = 0.15 s
```

---

## 51. Force and impulse

Force magnitude alone does not fully describe the disturbance.

Impulse is:

\[
J = F \Delta t
\]

For a 30 N force applied for 0.15 s:

\[
J = 30 \cdot 0.15
  = 4.5\ \mathrm{N\,s}
\]

For 40 N:

\[
J = 40 \cdot 0.15
  = 6.0\ \mathrm{N\,s}
\]

---

## 52. Student task: force sweep

Run:

```bash
python exercise_04_push_test.py --force 20 --headless
python exercise_04_push_test.py --force 25 --headless
python exercise_04_push_test.py --force 30 --headless
python exercise_04_push_test.py --force 35 --headless
python exercise_04_push_test.py --force 40 --headless
```

Record:

| Force | Impulse | Fallen | Maximum tilt | Minimum pelvis height |
|---:|---:|---|---:|---:|
| 20 N | 3.00 N·s | | | |
| 25 N | 3.75 N·s | | | |
| 30 N | 4.50 N·s | | | |
| 35 N | 5.25 N·s | | | |
| 40 N | 6.00 N·s | | | |

---

## 53. Fall criterion based on pelvis height

Get the pelvis position:

```python
pelvis_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_BODY,
    "pelvis",
)

pelvis_height = data.xpos[pelvis_id, 2]
```

Simple criterion:

```python
pelvis_height < 0.55
```

### Advantages

- simple;
- easy to understand;
- computationally inexpensive.

### Limitations

- a deep crouch may be classified as a fall;
- a leaning robot may remain above the threshold;
- body orientation is ignored.

---

## 54. Fall criterion based on torso orientation

The body rotation matrix is stored in:

```python
data.xmat[torso_id]
```

Reshape it:

```python
rotation = data.xmat[torso_id].reshape(3, 3)
```

The local torso \(z\)-axis expressed in world coordinates is the third column.

For the workshop model:

```python
torso_up_z = rotation[2, 2]
```

For an upright torso:

\[
z_{\mathrm{up}} \approx 1
\]

For a horizontal torso:

\[
z_{\mathrm{up}} \approx 0
\]

A threshold of:

```python
torso_up_z < 0.65
```

corresponds approximately to:

\[
\theta >
\cos^{-1}(0.65)
\approx 49.5^\circ
\]

---

## 55. Combined fall criterion

Use:

```python
fallen = (
    pelvis_height < 0.55
    or torso_up_z < 0.65
)
```

This combines:

- body height;
- body orientation.

It is more robust than either condition alone.

---

## 56. Student task: change the fall threshold

Try:

```python
torso_up_z < 0.85
```

This corresponds to:

\[
\theta >
\cos^{-1}(0.85)
\approx 31.8^\circ
\]

Then try:

```python
torso_up_z < 0.30
```

This corresponds to:

\[
\theta >
\cos^{-1}(0.30)
\approx 72.5^\circ
\]

Discuss:

- false positives;
- false negatives;
- how the experimental definition changes the reported result.

---

## 57. Student task: compare equal impulses

Run:

```bash
python exercise_04_push_test.py \
    --force 40 \
    --push-duration 0.10 \
    --headless
```

Impulse:

\[
J = 40 \cdot 0.10
  = 4.0\ \mathrm{N\,s}
\]

Then:

```bash
python exercise_04_push_test.py \
    --force 20 \
    --push-duration 0.20 \
    --headless
```

Impulse:

\[
J = 20 \cdot 0.20
  = 4.0\ \mathrm{N\,s}
\]

Ask:

> Will the resulting motion be identical?

Not necessarily.

Even with equal impulse:

- the force magnitude differs;
- the body moves during the push;
- contact conditions change;
- joint velocities change;
- the model is nonlinear.

---

## 58. Student task: compare friction during the push

Run:

```bash
python exercise_04_push_test.py \
    --force 30 \
    --friction 0.9 \
    --headless
```

Then:

```bash
python exercise_04_push_test.py \
    --force 30 \
    --friction 0.1 \
    --headless
```

Determine whether failure occurs primarily through:

- sliding;
- tipping;
- contact loss;
- a combination of these.

---

## 59. Final engineering challenge

Find the largest horizontal push that the humanoid can survive for five seconds.

Students may modify:

- stance width;
- knee angle;
- actuator gain;
- joint damping;
- foot friction.

Students may not modify:

- gravity;
- body masses;
- push duration;
- fall criterion.

Suggested table:

| Configuration | Maximum force | Fell? | Maximum tilt | Minimum pelvis height |
|---|---:|---|---:|---:|
| Default | | | | |
| Wider stance | | | | |
| Bent knees | | | | |
| Higher damping | | | | |
| Final design | | | | |

---

# Part IX — Unitree G1 demonstration

## 60. Purpose

The G1 demonstration shows that the same concepts transfer to a detailed commercial humanoid model.

The detailed model still contains:

- bodies;
- joints;
- geoms;
- actuators;
- sensors;
- contacts;
- floating-base coordinates.

---

## 61. Obtain MuJoCo Menagerie

Clone the repository:

```bash
git clone https://github.com/google-deepmind/mujoco_menagerie.git
```

Open the G1 model:

```bash
python -m mujoco.viewer \
    --mjcf mujoco_menagerie/unitree_g1/scene.xml
```

---

## 62. Student observation tasks

Ask students to identify:

1. pelvis or trunk root;
2. floating base;
3. hip joints;
4. knee joints;
5. ankle joints;
6. foot collision geometry;
7. actuator definitions;
8. keyframes;
9. joint limits;
10. differences from the simplified model.

---

## 63. Discussion

Ask:

- Why is the G1 XML much longer?
- Which details are physical?
- Which details are visual?
- Which concepts are unchanged?
- Why is a simplified model useful for learning?
- Why is a detailed model useful for validation?

### Main takeaway

A realistic humanoid is more complex, but it is built from the same simulator concepts.

---

# Part X — Suggested instructor script

## 64. Opening explanation

> In this workshop, we will not design an intelligent controller. Our goal is to understand what a humanoid simulator actually represents. We will inspect the model, command the joints, release the floating base, observe contact, change friction, and finally apply a controlled push.

---

## 65. Before Exercise 1

> The XML file is the human-readable description. MuJoCo compiles it into indexed arrays. The simulator does not repeatedly search for a joint by name during every dynamics calculation.

---

## 66. Before Exercise 2

> A position actuator does not teleport a joint. It creates force according to the difference between the command and the simulated state. The motion still depends on physics.

---

## 67. Before Exercise 3

> Until now, the pelvis was fixed. This separated joint actuation from whole-body balance. We will now release the root and let the robot interact freely with the floor.

---

## 68. Before Exercise 4

> A push test is only useful if it is repeatable. We must define the force, duration, application point, friction, initial state, and fall criterion.

---

## 69. Final conclusion

> A valid pose is not automatically stable. A joint controller does not directly control the floating base. Humanoid simulation is the interaction of model structure, actuation, contacts, and measurable evaluation criteria.

---

# Part XI — Troubleshooting

## 70. MuJoCo is not installed

Error:

```text
ModuleNotFoundError: No module named 'mujoco'
```

Activate the environment:

```bash
source .venv/bin/activate
```

Install:

```bash
python -m pip install -r requirements.txt
```

---

## 71. Test without graphics

Run:

```bash
python exercise_01_inspect.py --headless --duration 0.1
```

If this works, the model and physics engine are functioning.

---

## 72. Viewer segmentation fault

First test the standalone viewer:

```bash
python -m mujoco.viewer \
    --mjcf=models/simple_humanoid.xml
```

If the standalone viewer also crashes, the issue is likely related to:

- OpenGL;
- GLFW;
- graphics drivers;
- remote desktop;
- WSL graphics;
- mixed Conda and pip libraries.

Use a clean virtual environment.

Avoid mixing:

- Conda OpenGL libraries;
- system MuJoCo installations;
- pip MuJoCo installations.

Run with fault reporting:

```bash
python -X faulthandler exercise_01_inspect.py
```

---

## 73. Viewer-state changes

When using:

```python
mujoco.viewer.launch_passive(...)
```

protect viewer changes:

```python
with viewer.lock():
    viewer.opt.flags[
        mujoco.mjtVisFlag.mjVIS_CONTACTPOINT
    ] = True

viewer.sync()
```

---

## 74. XML parse error

Run:

```bash
python exercise_01_inspect.py --headless
```

MuJoCo normally reports the XML line containing the problem.

Common causes:

- missing closing tag;
- misspelled attribute;
- wrong number of keyframe values;
- invalid joint range;
- invalid body reference.

---

## 75. Humanoid immediately falls

Check which exercise is running.

Exercises 1 and 2 should use the pelvis weld.

Exercises 3 and 4 should release the pelvis.

A released humanoid without whole-body balance control may eventually fall even when no push is applied.

---

## 76. Violent oscillation

Restore reasonable values:

```xml
<option timestep="0.002"
        integrator="implicitfast"/>
```

```xml
<joint damping="3"
       armature="0.02"/>
```

```xml
<position kp="140"/>
```

Very high gain and low damping can create oscillation and large contact forces.

---

## 77. Friction change has little visible effect

Ensure friction is changed for:

- the floor;
- the left foot;
- the right foot.

Also increase the lateral force if the disturbance is too small.

---

## 78. Touch sensor always reads zero

Check:

- whether the site overlaps the contact region;
- whether the feet actually contact the floor;
- whether the sensor name is correct;
- whether the sensor address is read correctly;
- whether the pelvis weld holds the feet slightly above the floor.

---

# Part XII — Assessment questions

## 79. Short questions

1. What is the difference between `MjModel` and `MjData`?
2. Why does a free joint use 7 position values and 6 velocity values?
3. What is the purpose of `mj_forward`?
4. What does `data.ctrl` contain?
5. Why is a position actuator not equivalent to assigning `qpos`?
6. What does a touch sensor measure?
7. Why does low friction increase slipping?
8. Why is projected centre of mass only a static approximation?
9. How can an external force be applied to a body?
10. Why must a fall criterion be defined by the experimenter?

---

## 80. Practical assessment

Ask students to:

1. load the standing keyframe;
2. command a crouching posture;
3. release the pelvis weld;
4. set friction to 0.2;
5. apply a 25 N push for 0.2 s;
6. report:
   - whether the robot fell;
   - maximum torso tilt;
   - minimum pelvis height;
   - left and right foot force;
   - approximate foot displacement.

---

# Part XIII — Core conclusions

The workshop should end with these statements:

1. **A valid humanoid pose is not automatically dynamically stable.**

2. **Joint commands create actuator forces; they do not directly replace the physical state.**

3. **A floating base makes whole-body balance fundamentally different from fixed-base joint control.**

4. **Contact includes geometry, normal forces, friction, and possible sliding.**

5. **Simulation results depend on both the physical model and the experimental definition.**

6. **A fall detector is an engineering criterion, not an automatic truth supplied by the simulator.**

7. **The same principles apply to simplified humanoids and detailed models such as the Unitree G1.**

Library
/
ADC Prep
/mujoco_humanoid_workshop_tutorial.md

# Humanoid Robotics in MuJoCo

## Two-Hour Hands-On Workshop Tutorial

## 1. Workshop purpose

This workshop introduces the simulation concepts needed for humanoid robotics using MuJoCo.

The workshop focuses entirely on the simulator. It does not use:

- machine learning;
- reinforcement learning;
- Gymnasium;
- Stable-Baselines3;
- ROS;
- trajectory optimization.

The main topics are:

- MJCF model structure;
- floating-base humanoids;
- generalized coordinates;
- joint actuators;
- scripted posture changes;
- contact forces;
- friction;
- centre of mass;
- external disturbances;
- fall detection.

The workshop uses a simplified humanoid model first. A Unitree G1 model can be shown at the end as a more realistic example.

---

## 2. Learning outcomes

At the end of the workshop, students should be able to:

1. load an MJCF humanoid model;
2. identify bodies, joints, geoms, sites, actuators, sensors, and keyframes;
3. explain the difference between `MjModel` and `MjData`;
4. inspect `qpos`, `qvel`, and `ctrl`;
5. reset a simulation using a keyframe;
6. command position actuators;
7. generate a smooth scripted posture;
8. visualize and measure foot contact;
9. modify friction parameters;
10. apply an external force;
11. define a simple fall criterion;
12. explain why a valid humanoid pose is not necessarily dynamically stable.

---

## 3. Recommended workshop structure

| Time | Activity |
|---:|---|
| 0–10 min | Introduction and demonstration |
| 10–30 min | Exercise 1: Inspect the humanoid |
| 30–55 min | Exercise 2: Scripted posture control |
| 55–65 min | Discussion and short break |
| 65–90 min | Exercise 3: Contact, CoM, and friction |
| 90–115 min | Exercise 4: Push test and fall detection |
| 115–120 min | Unitree G1 comparison and conclusions |

---

# Part I — Installation and preparation

## 4. Recommended environment

Recommended system:

- Ubuntu 22.04 or newer;
- Python 3.10 or newer;
- working OpenGL desktop environment;
- one computer per student or student pair.

The workshop requires only:

```text
mujoco
numpy
```

---

## 5. Extract the workshop package

Unzip the workshop archive:

```bash
unzip mujoco_humanoid_workshop_fixed.zip
cd mujoco_humanoid_workshop
```

The folder should contain:

```text
mujoco_humanoid_workshop/
├── README.md
├── requirements.txt
├── common.py
├── exercise_01_inspect.py
├── exercise_02_pose.py
├── exercise_03_contacts.py
├── exercise_04_push_test.py
└── models/
    └── simple_humanoid.xml
```

---

## 6. Create a Python virtual environment

Create the environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Upgrade `pip`:

```bash
python -m pip install --upgrade pip
```

Install the requirements:

```bash
python -m pip install -r requirements.txt
```

Verify MuJoCo:

```bash
python -c "import mujoco; print(mujoco.__version__)"
```

---

## 7. Test the model without graphics

Run:

```bash
python exercise_01_inspect.py --headless --duration 0.1
```

Expected final output:

```text
Simulation completed at t=0.10 s
```

This confirms that:

- MuJoCo is installed;
- the XML model compiles;
- the physics loop works.

---

## 8. Test the graphical viewer

Run:

```bash
python -m mujoco.viewer --mjcf=models/simple_humanoid.xml
```

A humanoid model should appear above the floor.

Close the viewer before continuing.

---

# Part II — Fundamental MuJoCo concepts

## 9. `MjModel` and `MjData`

A basic MuJoCo program begins with:

```python
import mujoco

model = mujoco.MjModel.from_xml_path(
    "models/simple_humanoid.xml"
)

data = mujoco.MjData(model)
```

### `MjModel`

`MjModel` contains the compiled model definition.

Examples include:

- body masses;
- joint types;
- actuator gains;
- geometry dimensions;
- friction coefficients;
- sensor definitions;
- simulation timestep.

The model is mostly constant during a simulation.

### `MjData`

`MjData` contains the changing simulation state.

Examples include:

- joint positions;
- joint velocities;
- actuator commands;
- body positions;
- contact information;
- sensor values;
- simulation time.

---

## 10. The simulation loop

A simple loop is:

```python
while simulation_is_running:
    data.ctrl[:] = control_command
    mujoco.mj_step(model, data)
```

`mj_step`:

1. evaluates forces;
2. solves contacts and constraints;
3. calculates accelerations;
4. integrates the state;
5. advances simulation time.

The simulation timestep is stored in:

```python
model.opt.timestep
```

For example:

```xml
<option timestep="0.002"
        gravity="0 0 -9.81"/>
```

A timestep of `0.002` seconds corresponds to:

\[
f = \frac{1}{0.002} = 500\ \text{Hz}
\]

---

# Part III — The humanoid model

## 11. Main MJCF sections

Open:

```text
models/simple_humanoid.xml
```

The major sections are:

```xml
<mujoco>
    <option/>
    <default/>
    <asset/>
    <worldbody/>
    <equality/>
    <actuator/>
    <sensor/>
    <keyframe/>
</mujoco>
```

---

## 12. Bodies

A body represents a rigid coordinate frame in the kinematic tree.

Example:

```xml
<body name="pelvis" pos="0 0 0.92">
```

A child body is positioned relative to its parent.

Example:

```xml
<body name="left_shin" pos="0 0 -0.36">
```

This means the shin frame is positioned 0.36 m below its parent body.

The simplified hierarchy is:

```text
pelvis
├── torso
│   ├── head
│   ├── left_arm
│   └── right_arm
├── left_thigh
│   └── left_shin
│       └── left_foot
└── right_thigh
    └── right_shin
        └── right_foot
```

---

## 13. Joints

A joint defines relative motion between a body and its parent.

Example hinge joint:

```xml
<joint name="left_knee"
       type="hinge"
       axis="0 1 0"
       range="0 2.1"/>
```

This joint:

- rotates around the local \(y\)-axis;
- has a minimum angle of 0 rad;
- has a maximum angle of 2.1 rad.

Convert the maximum to degrees:

\[
2.1 \cdot \frac{180}{\pi}
\approx 120.3^\circ
\]

---

## 14. The floating base

The pelvis has a free joint:

```xml
<freejoint name="root"/>
```

A free joint allows:

- translation in \(x\);
- translation in \(y\);
- translation in \(z\);
- rotation around all three axes.

A free joint occupies:

- 7 entries in `qpos`;
- 6 entries in `qvel`.

### Position representation

The free joint position uses:

- 3 Cartesian coordinates;
- 4 quaternion coordinates.

Therefore:

\[
n_{q,\mathrm{free}} = 3 + 4 = 7
\]

### Velocity representation

The free joint velocity uses:

- 3 linear velocities;
- 3 angular velocities.

Therefore:

\[
n_{v,\mathrm{free}} = 3 + 3 = 6
\]

The teaching humanoid has:

- one free joint;
- twelve hinge joints.

Therefore:

\[
n_q = 7 + 12 = 19
\]

\[
n_v = 6 + 12 = 18
\]

---

## 15. Geoms

A geom can provide:

- visual shape;
- collision shape;
- mass;
- inertia;
- contact properties.

Example:

```xml
<geom name="left_foot_geom"
      type="box"
      size="0.12 0.05 0.03"
      friction="0.9 0.005 0.0001"/>
```

A box `size` specifies half-dimensions.

Therefore, this foot has approximate full dimensions:

\[
0.24 \times 0.10 \times 0.06\ \text{m}
\]

---

## 16. Sites

A site is a reference location or volume.

Sites are often used for:

- sensors;
- end-effector markers;
- contact measurement regions;
- visualization;
- force application reference points.

Example:

```xml
<site name="left_foot_touch_site"
      type="box"
      size="0.12 0.05 0.015"/>
```

---

## 17. Actuators

The workshop uses position actuators.

Example:

```xml
<position name="left_knee_act"
          joint="left_knee"
          kp="140"
          ctrlrange="0 2.1"/>
```

The command is written to:

```python
data.ctrl
```

For a position actuator, the control value acts as a desired joint position.

However, the joint is not teleported to that position. The actuator generates force based on the actuator model.

The resulting motion also depends on:

- inertia;
- gravity;
- damping;
- contact;
- actuator gain;
- constraints;
- timestep.

---

## 18. Keyframes

Keyframes store predefined simulation states.

Example:

```xml
<keyframe>
    <key name="stand"
         qpos="..."
         ctrl="..."/>

    <key name="crouch"
         qpos="..."
         ctrl="..."/>
</keyframe>
```

Reset to a keyframe:

```python
key_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_KEY,
    "stand",
)

mujoco.mj_resetDataKeyframe(
    model,
    data,
    key_id,
)

mujoco.mj_forward(model, data)
```

`mj_forward` recalculates derived quantities after manually changing the state.

---

## 19. Pelvis weld

The model includes an equality constraint:

```xml
<equality>
    <weld name="pelvis_weld"
          body1="pelvis"/>
</equality>
```

This weld can connect the pelvis to the world.

### Fixed-base mode

Used in Exercises 1 and 2.

The humanoid cannot fall.

This allows students to focus on:

- model structure;
- joint coordinates;
- actuator commands;
- scripted posture changes.

### Floating-base mode

Used in Exercises 3 and 4.

The weld is disabled from Python:

```python
weld_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_EQUALITY,
    "pelvis_weld",
)

data.eq_active[weld_id] = 0
```

The humanoid can then:

- translate;
- rotate;
- slip;
- tip;
- fall.

---

# Part IV — Exercise 1: Inspect the humanoid

## 20. Objective

Understand how an MJCF description becomes an indexed numerical model.

## 21. Run the exercise

```bash
python exercise_01_inspect.py
```

The script prints:

- body count;
- joint count;
- number of position coordinates;
- number of velocity coordinates;
- actuator count;
- sensor count;
- joint names;
- joint ranges;
- `qpos` addresses;
- degree-of-freedom addresses;
- actuator names;
- sensor names.

---

## 22. Student task: inspect the model dimensions

Expected values are approximately:

```text
Bodies:               12
Joints:               13
Position coordinates: 19
Velocity coordinates: 18
Actuators:            12
Sensors:              6
Equality constraints: 1
```

Ask:

1. Why are there more bodies than actuators?
2. Why is `nq` different from `nv`?
3. Why does the head have no actuator?
4. Which joint represents the floating base?

---

## 23. Student task: inspect joint names

A typical inspection loop is:

```python
for joint_id in range(model.njnt):
    name = mujoco.mj_id2name(
        model,
        mujoco.mjtObj.mjOBJ_JOINT,
        joint_id,
    )

    print(joint_id, name)
```

Students should identify:

```text
root
left_hip_yaw
left_hip_roll
left_hip_pitch
left_knee
left_ankle_pitch
left_ankle_roll
right_hip_yaw
right_hip_roll
right_hip_pitch
right_knee
right_ankle_pitch
right_ankle_roll
```

---

## 24. Student task: modify a material

Find:

```xml
<material name="left_mat"
          rgba="0.25 0.65 0.35 1"/>
```

Change it to:

```xml
<material name="left_mat"
          rgba="0.8 0.2 0.8 1"/>
```

Restart:

```bash
python exercise_01_inspect.py
```

The model is compiled when loaded. XML changes do not affect a model that is already running.

---

## 25. Student task: modify one joint limit

Find:

```xml
<joint name="left_knee"
       range="0 2.1"/>
```

Change it temporarily:

```xml
<joint name="left_knee"
       range="0 1.2"/>
```

Restart the simulation and observe whether the crouching keyframe or commanded posture remains feasible.

Restore the original value afterward.

---

## 26. Exercise 1 discussion

Ask:

- Which parts are visual only?
- Which parts participate in collisions?
- Why does the pelvis need a free joint?
- Why are joint positions stored in an array?
- Why are names converted to integer IDs?

### Main takeaway

The XML is a human-readable model description. MuJoCo compiles it into numerical arrays used by the physics engine.

---

# Part V — Exercise 2: Scripted posture control

## 27. Objective

Command the humanoid to move smoothly between standing and crouching poses.

## 28. Run the exercise

```bash
python exercise_02_pose.py
```

The robot should repeatedly move:

```text
standing → crouching → standing
```

The pelvis is fixed during this exercise.

---

## 29. Actuator order

The control vector contains 12 values:

```text
0  left hip yaw
1  left hip roll
2  left hip pitch
3  left knee
4  left ankle pitch
5  left ankle roll
6  right hip yaw
7  right hip roll
8  right hip pitch
9  right knee
10 right ankle pitch
11 right ankle roll
```

A crouching reference may be:

```python
crouch = [
    0.0, 0.0, -0.45, 0.90, -0.45, 0.0,
    0.0, 0.0, -0.45, 0.90, -0.45, 0.0,
]
```

For each leg:

\[
q_{\mathrm{hip}}
+
q_{\mathrm{knee}}
+
q_{\mathrm{ankle}}
=
-0.45 + 0.90 - 0.45 = 0
\]

This helps keep the foot approximately parallel to the floor.

---

## 30. Linear interpolation

The simplest interpolation is:

\[
q_{\mathrm{ref}}(u)
=
q_{\mathrm{start}}
+
u
\left(
q_{\mathrm{goal}}
-
q_{\mathrm{start}}
\right)
\]

where:

\[
0 \leq u \leq 1
\]

Python:

```python
q_ref = q_start + u * (q_goal - q_start)
```

This creates a constant desired velocity during the segment, but the desired velocity changes abruptly at the beginning and end.

---

## 31. Smoothstep interpolation

The workshop uses:

\[
s(u)=3u^2-2u^3
\]

Then:

\[
q_{\mathrm{ref}}(u)
=
q_{\mathrm{start}}
+
s(u)
\left(
q_{\mathrm{goal}}
-
q_{\mathrm{start}}
\right)
\]

Properties:

\[
s(0)=0
\]

\[
s(1)=1
\]

\[
s'(0)=0
\]

\[
s'(1)=0
\]

Python:

```python
def smoothstep(value: float) -> float:
    value = float(np.clip(value, 0.0, 1.0))
    return 3.0 * value**2 - 2.0 * value**3
```

---

## 32. Student task: compare linear and smooth motion

Replace:

```python
return 3.0 * value**2 - 2.0 * value**3
```

with:

```python
return value
```

Run:

```bash
python exercise_02_pose.py
```

Compare:

- movement onset;
- movement termination;
- visible oscillation;
- tracking error;
- apparent smoothness.

Restore the smoothstep function afterward.

---

## 33. Student task: modify actuator gain

Find the position actuator default:

```xml
<position kp="140"
          ctrllimited="true"/>
```

Test:

```xml
<position kp="40"
          ctrllimited="true"/>
```

Then:

```xml
<position kp="300"
          ctrllimited="true"/>
```

Record:

| Gain | Tracking speed | Tracking error | Oscillation |
|---:|---|---|---|
| 40 | | | |
| 140 | | | |
| 300 | | | |

### Expected observations

Low gain:

- slower response;
- larger position error;
- softer movement.

High gain:

- faster response;
- smaller static error;
- possibly stronger oscillation;
- larger forces;
- greater numerical sensitivity.

---

## 34. Student task: modify joint damping

Find:

```xml
<joint damping="3"
       armature="0.02"
       limited="true"/>
```

Test:

```xml
damping="0.3"
```

Then:

```xml
damping="10"
```

Record the effect.

### Expected observations

Low damping:

- more oscillation;
- longer settling;
- freer motion.

High damping:

- reduced oscillation;
- slower motion;
- stronger resistance to rapid changes.

---

## 35. Exercise 2 discussion

Ask:

1. Does `data.ctrl` directly set `qpos`?
2. Why does the actual position lag behind the reference?
3. Why can high gains cause instability?
4. Why did we fix the pelvis?
5. Would the same command work if link masses were doubled?

### Main takeaway

An actuator command creates force. It does not directly replace the simulated joint state.

---

# Part VI — Discussion and short break

## 36. Suggested questions

1. Why did we fix the pelvis during the first two exercises?
2. What changes when the floating base is released?
3. Can a robot follow all joint commands and still fall?
4. Is joint-space tracking identical to balance control?
5. Why can an upright pose be dynamically unstable?

The central idea is:

> Good joint tracking does not automatically produce whole-body stability.

---

# Part VII — Exercise 3: Contact, centre of mass, and friction

## 37. Objective

Observe floor contact, foot forces, centre of mass, slipping, and load transfer.

## 38. Run the default experiment

```bash
python exercise_03_contacts.py --friction 0.9
```

The script:

1. loads the standing keyframe;
2. disables the pelvis weld;
3. enables contact visualization;
4. reads foot contact sensors;
5. reads the centre-of-mass sensor;
6. applies a small lateral force;
7. measures foot displacement.

---

## 39. Viewer locking

When using the passive viewer, modify viewer state while holding the viewer lock:

```python
with viewer.lock():
    viewer.opt.flags[
        mujoco.mjtVisFlag.mjVIS_CONTACTPOINT
    ] = True

    viewer.opt.flags[
        mujoco.mjtVisFlag.mjVIS_CONTACTFORCE
    ] = True

viewer.sync()
```

This avoids race conditions between the simulation thread and the viewer thread.

---

## 40. Foot touch sensors

The XML contains:

```xml
<touch name="left_foot_force"
       site="left_foot_touch_site"/>

<touch name="right_foot_force"
       site="right_foot_touch_site"/>
```

The touch sensor returns a non-negative scalar representing the summed normal contact force associated with contacts in the sensor site.

Read sensor data:

```python
sensor_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_SENSOR,
    "left_foot_force",
)

start = model.sensor_adr[sensor_id]
dimension = model.sensor_dim[sensor_id]

left_force = data.sensordata[
    start:start + dimension
]
```

---

## 41. Centre-of-mass sensor

The XML contains:

```xml
<subtreecom name="humanoid_com"
            body="pelvis"/>
```

The sensor returns:

\[
p_{\mathrm{CoM}}
=
\begin{bmatrix}
x_{\mathrm{CoM}}\\
y_{\mathrm{CoM}}\\
z_{\mathrm{CoM}}
\end{bmatrix}
\]

For a basic balance interpretation, use the horizontal projection:

\[
p_{\mathrm{CoM,xy}}
=
\begin{bmatrix}
x_{\mathrm{CoM}}\\
y_{\mathrm{CoM}}
\end{bmatrix}
\]

For static balance, the projected centre of mass should normally remain inside the support region formed by the contacting feet.

This is only an introductory approximation. Dynamic balance also depends on:

- velocity;
- angular momentum;
- contact forces;
- centre of pressure;
- future motion.

---

## 42. Student task: compare left and right foot force

Before the disturbance:

```text
left force ≈ right force
```

During a lateral disturbance:

```text
left force ≠ right force
```

Ask:

- Which foot becomes more loaded?
- Does the foot with greater force necessarily move less?
- Does force difference directly indicate body velocity?

The answer to the last question is no. Contact force and body velocity are related through dynamics, but they are not the same quantity.

---

## 43. Friction parameters

The floor geom contains:

```xml
friction="0.9 0.005 0.0001"
```

The three components correspond to:

1. sliding friction;
2. torsional friction;
3. rolling friction.

For this workshop, the first value is the most important.

---

## 44. Student task: friction experiment

Run:

```bash
python exercise_03_contacts.py --friction 0.9
```

Then:

```bash
python exercise_03_contacts.py --friction 0.3
```

Then:

```bash
python exercise_03_contacts.py --friction 0.05
```

Record:

| Sliding friction | Left-foot displacement | Right-foot displacement | Visible slipping |
|---:|---:|---:|---|
| 0.90 | | | |
| 0.30 | | | |
| 0.05 | | | |

Expected trend:

- high friction resists sliding;
- low friction allows larger foot displacement;
- very low friction may produce sliding before strong body tilt.

---

## 45. Student task: modify the lateral disturbance

Run:

```bash
python exercise_03_contacts.py \
    --friction 0.3 \
    --lateral-force 10
```

Then:

```bash
python exercise_03_contacts.py \
    --friction 0.3 \
    --lateral-force 40
```

Observe:

- load transfer;
- foot sliding;
- torso tilt;
- contact loss;
- whole-body translation.

---

## 46. Contact versus stability

A humanoid can have both feet touching the floor and still be unstable.

Possible situations include:

- centre of mass leaving the support region;
- insufficient friction;
- excessive angular velocity;
- one foot unloading;
- contact occurring only at an edge;
- feet sliding together.

### Main takeaway

Contact is not simply “on” or “off.” It has geometry, forces, friction, and motion.

---

# Part VIII — Exercise 4: Push test and fall detection

## 47. Objective

Apply a repeatable external disturbance and measure whether the humanoid falls.

## 48. Run the push test

```bash
python exercise_04_push_test.py --force 30
```

The script applies a horizontal force to the torso.

---

## 49. External force array

MuJoCo provides:

```python
data.xfrc_applied
```

Each body receives a six-component spatial force:

```text
Fx Fy Fz Tx Ty Tz
```

Apply a force in the world \(x\)-direction:

```python
torso_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_BODY,
    "torso",
)

data.xfrc_applied[torso_id, 0] = 30.0
```

Clear the force afterward:

```python
data.xfrc_applied[torso_id, :] = 0.0
```

---

## 50. Push timing

The force is applied only during a defined interval:

```python
if push_start <= data.time < push_start + push_duration:
    data.xfrc_applied[torso_id, 0] = push_force
else:
    data.xfrc_applied[torso_id, :] = 0.0
```

Typical settings:

```text
push_start    = 0.50 s
push_duration = 0.15 s
```

---

## 51. Force and impulse

Force magnitude alone does not fully describe the disturbance.

Impulse is:

\[
J = F \Delta t
\]

For a 30 N force applied for 0.15 s:

\[
J = 30 \cdot 0.15
  = 4.5\ \mathrm{N\,s}
\]

For 40 N:

\[
J = 40 \cdot 0.15
  = 6.0\ \mathrm{N\,s}
\]

---

## 52. Student task: force sweep

Run:

```bash
python exercise_04_push_test.py --force 20 --headless
python exercise_04_push_test.py --force 25 --headless
python exercise_04_push_test.py --force 30 --headless
python exercise_04_push_test.py --force 35 --headless
python exercise_04_push_test.py --force 40 --headless
```

Record:

| Force | Impulse | Fallen | Maximum tilt | Minimum pelvis height |
|---:|---:|---|---:|---:|
| 20 N | 3.00 N·s | | | |
| 25 N | 3.75 N·s | | | |
| 30 N | 4.50 N·s | | | |
| 35 N | 5.25 N·s | | | |
| 40 N | 6.00 N·s | | | |

---

## 53. Fall criterion based on pelvis height

Get the pelvis position:

```python
pelvis_id = mujoco.mj_name2id(
    model,
    mujoco.mjtObj.mjOBJ_BODY,
    "pelvis",
)

pelvis_height = data.xpos[pelvis_id, 2]
```

Simple criterion:

```python
pelvis_height < 0.55
```

### Advantages

- simple;
- easy to understand;
- computationally inexpensive.

### Limitations

- a deep crouch may be classified as a fall;
- a leaning robot may remain above the threshold;
- body orientation is ignored.

---

## 54. Fall criterion based on torso orientation

The body rotation matrix is stored in:

```python
data.xmat[torso_id]
```

Reshape it:

```python
rotation = data.xmat[torso_id].reshape(3, 3)
```

The local torso \(z\)-axis expressed in world coordinates is the third column.

For the workshop model:

```python
torso_up_z = rotation[2, 2]
```

For an upright torso:

\[
z_{\mathrm{up}} \approx 1
\]

For a horizontal torso:

\[
z_{\mathrm{up}} \approx 0
\]

A threshold of:

```python
torso_up_z < 0.65
```

corresponds approximately to:

\[
\theta >
\cos^{-1}(0.65)
\approx 49.5^\circ
\]

---

## 55. Combined fall criterion

Use:

```python
fallen = (
    pelvis_height < 0.55
    or torso_up_z < 0.65
)
```

This combines:

- body height;
- body orientation.

It is more robust than either condition alone.

---

## 56. Student task: change the fall threshold

Try:

```python
torso_up_z < 0.85
```

This corresponds to:

\[
\theta >
\cos^{-1}(0.85)
\approx 31.8^\circ
\]

Then try:

```python
torso_up_z < 0.30
```

This corresponds to:

\[
\theta >
\cos^{-1}(0.30)
\approx 72.5^\circ
\]

Discuss:

- false positives;
- false negatives;
- how the experimental definition changes the reported result.

---

## 57. Student task: compare equal impulses

Run:

```bash
python exercise_04_push_test.py \
    --force 40 \
    --push-duration 0.10 \
    --headless
```

Impulse:

\[
J = 40 \cdot 0.10
  = 4.0\ \mathrm{N\,s}
\]

Then:

```bash
python exercise_04_push_test.py \
    --force 20 \
    --push-duration 0.20 \
    --headless
```

Impulse:

\[
J = 20 \cdot 0.20
  = 4.0\ \mathrm{N\,s}
\]

Ask:

> Will the resulting motion be identical?

Not necessarily.

Even with equal impulse:

- the force magnitude differs;
- the body moves during the push;
- contact conditions change;
- joint velocities change;
- the model is nonlinear.

---

## 58. Student task: compare friction during the push

Run:

```bash
python exercise_04_push_test.py \
    --force 30 \
    --friction 0.9 \
    --headless
```

Then:

```bash
python exercise_04_push_test.py \
    --force 30 \
    --friction 0.1 \
    --headless
```

Determine whether failure occurs primarily through:

- sliding;
- tipping;
- contact loss;
- a combination of these.

---

## 59. Final engineering challenge

Find the largest horizontal push that the humanoid can survive for five seconds.

Students may modify:

- stance width;
- knee angle;
- actuator gain;
- joint damping;
- foot friction.

Students may not modify:

- gravity;
- body masses;
- push duration;
- fall criterion.

Suggested table:

| Configuration | Maximum force | Fell? | Maximum tilt | Minimum pelvis height |
|---|---:|---|---:|---:|
| Default | | | | |
| Wider stance | | | | |
| Bent knees | | | | |
| Higher damping | | | | |
| Final design | | | | |

---

# Part IX — Unitree G1 demonstration

## 60. Purpose

The G1 demonstration shows that the same concepts transfer to a detailed commercial humanoid model.

The detailed model still contains:

- bodies;
- joints;
- geoms;
- actuators;
- sensors;
- contacts;
- floating-base coordinates.

---

## 61. Obtain MuJoCo Menagerie

Clone the repository:

```bash
git clone https://github.com/google-deepmind/mujoco_menagerie.git
```

Open the G1 model:

```bash
python -m mujoco.viewer \
    --mjcf mujoco_menagerie/unitree_g1/scene.xml
```

---

## 62. Student observation tasks

Ask students to identify:

1. pelvis or trunk root;
2. floating base;
3. hip joints;
4. knee joints;
5. ankle joints;
6. foot collision geometry;
7. actuator definitions;
8. keyframes;
9. joint limits;
10. differences from the simplified model.

---

## 63. Discussion

Ask:

- Why is the G1 XML much longer?
- Which details are physical?
- Which details are visual?
- Which concepts are unchanged?
- Why is a simplified model useful for learning?
- Why is a detailed model useful for validation?

### Main takeaway

A realistic humanoid is more complex, but it is built from the same simulator concepts.

---

# Part X — Suggested instructor script

## 64. Opening explanation

> In this workshop, we will not design an intelligent controller. Our goal is to understand what a humanoid simulator actually represents. We will inspect the model, command the joints, release the floating base, observe contact, change friction, and finally apply a controlled push.

---

## 65. Before Exercise 1

> The XML file is the human-readable description. MuJoCo compiles it into indexed arrays. The simulator does not repeatedly search for a joint by name during every dynamics calculation.

---

## 66. Before Exercise 2

> A position actuator does not teleport a joint. It creates force according to the difference between the command and the simulated state. The motion still depends on physics.

---

## 67. Before Exercise 3

> Until now, the pelvis was fixed. This separated joint actuation from whole-body balance. We will now release the root and let the robot interact freely with the floor.

---

## 68. Before Exercise 4

> A push test is only useful if it is repeatable. We must define the force, duration, application point, friction, initial state, and fall criterion.

---

## 69. Final conclusion

> A valid pose is not automatically stable. A joint controller does not directly control the floating base. Humanoid simulation is the interaction of model structure, actuation, contacts, and measurable evaluation criteria.

---

# Part XI — Troubleshooting

## 70. MuJoCo is not installed

Error:

```text
ModuleNotFoundError: No module named 'mujoco'
```

Activate the environment:

```bash
source .venv/bin/activate
```

Install:

```bash
python -m pip install -r requirements.txt
```

---

## 71. Test without graphics

Run:

```bash
python exercise_01_inspect.py --headless --duration 0.1
```

If this works, the model and physics engine are functioning.

---

## 72. Viewer segmentation fault

First test the standalone viewer:

```bash
python -m mujoco.viewer \
    --mjcf=models/simple_humanoid.xml
```

If the standalone viewer also crashes, the issue is likely related to:

- OpenGL;
- GLFW;
- graphics drivers;
- remote desktop;
- WSL graphics;
- mixed Conda and pip libraries.

Use a clean virtual environment.

Avoid mixing:

- Conda OpenGL libraries;
- system MuJoCo installations;
- pip MuJoCo installations.

Run with fault reporting:

```bash
python -X faulthandler exercise_01_inspect.py
```

---

## 73. Viewer-state changes

When using:

```python
mujoco.viewer.launch_passive(...)
```

protect viewer changes:

```python
with viewer.lock():
    viewer.opt.flags[
        mujoco.mjtVisFlag.mjVIS_CONTACTPOINT
    ] = True

viewer.sync()
```

---

## 74. XML parse error

Run:

```bash
python exercise_01_inspect.py --headless
```

MuJoCo normally reports the XML line containing the problem.

Common causes:

- missing closing tag;
- misspelled attribute;
- wrong number of keyframe values;
- invalid joint range;
- invalid body reference.

---

## 75. Humanoid immediately falls

Check which exercise is running.

Exercises 1 and 2 should use the pelvis weld.

Exercises 3 and 4 should release the pelvis.

A released humanoid without whole-body balance control may eventually fall even when no push is applied.

---

## 76. Violent oscillation

Restore reasonable values:

```xml
<option timestep="0.002"
        integrator="implicitfast"/>
```

```xml
<joint damping="3"
       armature="0.02"/>
```

```xml
<position kp="140"/>
```

Very high gain and low damping can create oscillation and large contact forces.

---

## 77. Friction change has little visible effect

Ensure friction is changed for:

- the floor;
- the left foot;
- the right foot.

Also increase the lateral force if the disturbance is too small.

---

## 78. Touch sensor always reads zero

Check:

- whether the site overlaps the contact region;
- whether the feet actually contact the floor;
- whether the sensor name is correct;
- whether the sensor address is read correctly;
- whether the pelvis weld holds the feet slightly above the floor.

---

# Part XII — Assessment questions

## 79. Short questions

1. What is the difference between `MjModel` and `MjData`?
2. Why does a free joint use 7 position values and 6 velocity values?
3. What is the purpose of `mj_forward`?
4. What does `data.ctrl` contain?
5. Why is a position actuator not equivalent to assigning `qpos`?
6. What does a touch sensor measure?
7. Why does low friction increase slipping?
8. Why is projected centre of mass only a static approximation?
9. How can an external force be applied to a body?
10. Why must a fall criterion be defined by the experimenter?

---

## 80. Practical assessment

Ask students to:

1. load the standing keyframe;
2. command a crouching posture;
3. release the pelvis weld;
4. set friction to 0.2;
5. apply a 25 N push for 0.2 s;
6. report:
   - whether the robot fell;
   - maximum torso tilt;
   - minimum pelvis height;
   - left and right foot force;
   - approximate foot displacement.

---

# Part XIII — Core conclusions

The workshop should end with these statements:

1. **A valid humanoid pose is not automatically dynamically stable.**

2. **Joint commands create actuator forces; they do not directly replace the physical state.**

3. **A floating base makes whole-body balance fundamentally different from fixed-base joint control.**

4. **Contact includes geometry, normal forces, friction, and possible sliding.**

5. **Simulation results depend on both the physical model and the experimental definition.**

6. **A fall detector is an engineering criterion, not an automatic truth supplied by the simulator.**

7. **The same principles apply to simplified humanoids and detailed models such as the Unitree G1.**


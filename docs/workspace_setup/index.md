# Workspace Setup

This section explains how to prepare the development environment used in the humanoid robotics examples.

The examples are mainly intended for Linux-based systems. The recommended setup is **Ubuntu 22.04 LTS** or a similar recent Linux distribution.

The first reinforcement learning examples use **MuJoCo**, **Gymnasium**, and **Stable-Baselines3**. The development path starts with a simplified 3-link throwing arm and then moves toward a full Unitree G1 humanoid model where only one arm is controlled and the rest of the robot is kept fixed.

---

## 1. System requirements

Recommended operating system:

- Ubuntu 22.04 LTS
- Python 3.10 or newer
- Git
- A working terminal environment
- A dedicated Python virtual environment

Recommended hardware:

- A modern laptop or desktop computer
- At least 8 GB RAM
- Intel Core i5 or better
- A dedicated GPU is useful for larger learning tasks, but it is not required for the first examples

The first examples are designed to work on CPU-only systems. For example, an Intel Core i5 platform with Intel Iris Xe graphics is sufficient for the simplified 3-link arm and fixed-body humanoid arm throwing experiments.

---

## 2. Install basic system packages

Update the package list:

```bash
sudo apt update
```

Install the basic development tools:

```bash
sudo apt install -y git unzip python3 python3-pip python3-venv build-essential
```

Install packages commonly needed by MuJoCo and the viewer:

```bash
sudo apt install -y libgl1 libglfw3 libglew-dev libosmesa6-dev mesa-utils patchelf
```

Check the installed versions:

```bash
python3 --version
pip3 --version
git --version
```

---

## 3. Clone and prepare the repository

Create a workspace folder:

```bash
mkdir -p ~/humanoid_ws
cd ~/humanoid_ws
```

Clone the repository:

```bash
git clone https://github.com/robotlabor/humanoid-robot-fundamentals.git
cd humanoid-robot-fundamentals
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Upgrade the Python packaging tools:

```bash
pip install --upgrade pip setuptools wheel
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Check the active Python environment:

```bash
which python
which pip
```

The paths should contain `.venv`.

Example:

```text
/home/user/humanoid_ws/humanoid-robot-fundamentals/.venv/bin/python
/home/user/humanoid_ws/humanoid-robot-fundamentals/.venv/bin/pip
```

---

## 4. Test the setup

Run the basic Python test:

```bash
python3 scripts/test_python_setup.py
```

Run the basic MuJoCo simulation test:

```bash
python3 scripts/test_mujoco_setup.py
```

Check that MuJoCo can be imported:

```bash
python3 -c "import mujoco; print(mujoco.__version__)"
```

To test graphical rendering, run the random 3-link viewer:

```bash
python3 scripts/random_policy_viewer.py
```

If a MuJoCo window appears with a simple arm, ball, and target, the graphical viewer is working.

---

## 5. Check the starter repository structure

After installing the starter files, the repository should contain the main folders for assets, environments, scripts, documentation, logs, and policies.

From the workspace folder, inspect the structure with:

```bash
cd ~/humanoid_ws
tree humanoid-robot-fundamentals
```

A typical structure after running the 3-link example may look similar to:

```text
humanoid-robot-fundamentals
├── assets
│   ├── README.md
│   ├── three_link_throw.xml
│   └── unitree_g1_throw
│       └── README.md
├── docs
│   ├── computer_simulation
│   │   └── index.md
│   ├── fundamentals
│   │   └── index.md
│   ├── index.md
│   ├── reinforcement_learning
│   │   └── index.md
│   └── workspace_setup
│       └── index.md
├── envs
│   ├── g1_fixed_body_throw_env.py
│   ├── __init__.py
│   └── three_link_throw_env.py
├── external
├── logs
├── mkdocs.yml
├── policies
├── README.md
├── requirements.txt
└── scripts
    ├── create_g1_throw_scene.py
    ├── evaluate_g1_throw.py
    ├── evaluate_throw.py
    ├── inspect_g1_bodies.py
    ├── inspect_g1.py
    ├── play_g1_throw.py
    ├── play_throw.py
    ├── random_g1_throw_viewer.py
    ├── random_policy_viewer.py
    ├── test_mujoco_setup.py
    ├── test_python_setup.py
    ├── train_g1_throw.py
    ├── train_throw.py
    └── view_g1.py
```

The folder:

```text
assets/unitree_g1_throw/
```

is only a placeholder at first. It will later contain the generated G1 throwing scene:

```text
assets/unitree_g1_throw/scene_throw.xml
```

The folder:

```text
assets/unitree_g1/
```

is not included initially. It is created only after copying the Unitree G1 model from MuJoCo Menagerie.

Therefore, if this folder is missing at this stage, that is normal:

```text
assets/unitree_g1/
```

It will be created later with:

```bash
mkdir -p assets/unitree_g1
cp -r external/mujoco_menagerie/unitree_g1/* assets/unitree_g1/
```

After training examples, additional generated files may appear, such as:

```text
logs/
policies/three_link_throw_ppo.zip
envs/__pycache__/
```

These are runtime outputs and should normally not be committed to Git.

If needed, clean generated files with:

```bash
rm -rf logs
rm -rf envs/__pycache__
```

The repository `.gitignore` should exclude generated folders such as:

```text
.venv/
__pycache__/
logs/
external/
policies/*.zip
```

---

# Part A — Simplified 3-link arm throwing

The first reinforcement learning task uses a planar 3-link arm that throws a ball toward a fixed target.

This verifies:

- MuJoCo model loading,
- Gymnasium environment creation,
- PPO training,
- policy saving,
- policy playback,
- ball weld and release logic,
- reward debugging.

The simplified throwing scene is stored in:

```text
assets/three_link_throw.xml
```

The corresponding Gymnasium environment is:

```text
envs/three_link_throw_env.py
```

---

## 6. Run the random 3-link viewer

Run:

```bash
python3 scripts/random_policy_viewer.py
```

Expected behavior:

```text
3-link arm appears
ball appears
target appears
arm moves
ball releases after the scripted release time
```

This step does not use reinforcement learning yet. It only verifies that the scene, environment, viewer, and release logic are working.

---

## 7. Train the 3-link throwing policy

Run:

```bash
python3 scripts/train_throw.py
```

Training runs in the terminal and usually does not open a simulator window.

Expected saved policy:

```text
policies/three_link_throw_ppo.zip
```

If you want to stop training early, press:

```text
Ctrl+C
```

The training script is designed to save the current policy when interrupted.

---

## 8. Play the trained 3-link policy

After training, run:

```bash
python3 scripts/play_throw.py
```

Expected behavior:

```text
The MuJoCo viewer opens
The trained arm motion is shown
The ball releases and moves toward the target
```

---

## 9. Evaluate the 3-link policy

Run:

```bash
python3 scripts/evaluate_throw.py
```

The script reports basic numerical results, such as the mean best distance to the target and hit rates.

A useful first success criterion is:

```text
Mean best distance below 0.5 m
```

A better result is:

```text
Hit rate below 30 cm above 50%
```

---

# Part B — Unitree G1 fixed-body throwing

After the 3-link task works, the next step is to use the full Unitree G1 humanoid model while keeping the RL problem simple.

The goal is:

```text
Full Unitree G1 model visible in MuJoCo
Only one arm is controlled by RL
All other joints are held fixed at nominal values
Ball is attached to the hand
Ball is released at a scripted time
Target is fixed
```

This is not yet full-body humanoid throwing. It is an intermediate step between the simple 3-link arm and a full humanoid controller.

---

## 10. Fetch the Unitree G1 model

The starter repository contains the simulation scripts and reinforcement learning environments, but it does **not** include the Unitree G1 model assets.

The Unitree G1 MuJoCo model should be copied from MuJoCo Menagerie into:

```text
assets/unitree_g1/
```

From the repository root, run:

```bash
cd ~/humanoid_ws/humanoid-robot-fundamentals
source .venv/bin/activate
```

Clone MuJoCo Menagerie:

```bash
mkdir -p external
git clone https://github.com/google-deepmind/mujoco_menagerie.git external/mujoco_menagerie
```

Copy the Unitree G1 model into the local assets folder:

```bash
mkdir -p assets/unitree_g1
cp -r external/mujoco_menagerie/unitree_g1/* assets/unitree_g1/
```

Check the copied files:

```bash
ls assets/unitree_g1
```

Typical files include:

```text
g1.xml
scene.xml
scene_mjx.xml
assets/
```

The most important file for the next step is:

```text
assets/unitree_g1/scene.xml
```

If `scene.xml` is missing, `scripts/view_g1.py` will stop with an error such as:

```text
FileNotFoundError: Copy Unitree G1 assets to assets/unitree_g1 first.
```

If you already cloned MuJoCo Menagerie earlier and the folder `external/mujoco_menagerie` already exists, you do not need to clone it again. Just copy the G1 assets:

```bash
mkdir -p assets/unitree_g1
cp -r external/mujoco_menagerie/unitree_g1/* assets/unitree_g1/
```

---

## 11. View the Unitree G1 model

Run:

```bash
python3 scripts/view_g1.py
```

If the full G1 humanoid appears in the MuJoCo viewer, the model assets are loaded correctly.

If you get this error:

```text
FileNotFoundError: Copy Unitree G1 assets to assets/unitree_g1 first.
```

go back to the previous step and make sure that `assets/unitree_g1/scene.xml` exists:

```bash
ls assets/unitree_g1/scene.xml
```

---

## 12. Inspect G1 joint and actuator names

Run:

```bash
python3 scripts/inspect_g1.py
```

This prints all joint and actuator names in the model.

Look for the right arm joints. They may have names similar to:

```text
right_shoulder_pitch_joint
right_shoulder_roll_joint
right_shoulder_yaw_joint
right_elbow_joint
right_wrist_roll_joint
right_wrist_pitch_joint
right_wrist_yaw_joint
```

The exact names depend on the copied G1 model version.

---

## 13. Inspect G1 body names

Run:

```bash
python3 scripts/inspect_g1_bodies.py
```

This prints candidate body names containing words such as:

```text
right
wrist
hand
```

You need one of these body names to attach the ball to the right hand or wrist.

Example output may include a body such as:

```text
right_wrist_yaw_link
```

Use the body name that best corresponds to the right hand or wrist.

---

## 14. Create the G1 throwing scene

Generate the throwing scene using the selected hand or wrist body:

```bash
python3 scripts/create_g1_throw_scene.py --hand-body RIGHT_HAND_OR_WRIST_BODY_NAME
```

Replace:

```text
RIGHT_HAND_OR_WRIST_BODY_NAME
```

with the body name printed by `inspect_g1_bodies.py`.

Example:

```bash
python3 scripts/create_g1_throw_scene.py --hand-body right_wrist_yaw_link
```

This creates:

```text
assets/unitree_g1_throw/scene_throw.xml
```

The generated scene contains:

```text
Full Unitree G1 model
throw_ball
throw_target
hold_throw_ball weld constraint
```

Test the generated XML:

```bash
python3 -c "import mujoco; mujoco.MjModel.from_xml_path('assets/unitree_g1_throw/scene_throw.xml'); print('G1 throw XML OK')"
```

Expected output:

```text
G1 throw XML OK
```

---

## 15. Run the random G1 throwing viewer

Run:

```bash
python3 scripts/random_g1_throw_viewer.py
```

Expected behavior:

```text
Full G1 appears
Only the selected arm moves
The ball starts near the hand
The ball is released after the scripted release time
The target is visible
The body and legs remain mostly fixed
```

This step is important before training. If the ball is not attached to the hand or the wrong body moves, fix the scene or joint mapping before continuing.

---

## 16. Train the G1 fixed-body throwing policy

Run:

```bash
python3 scripts/train_g1_throw.py
```

This script trains headlessly. It does not normally open a simulator window.

Expected saved policy:

```text
policies/g1_fixed_body_throw_ppo.zip
```

The first version uses:

```text
scripted release
fixed target
right arm actions only
all other joints held at nominal values
```

---

## 17. Play the trained G1 policy

After training, run:

```bash
python3 scripts/play_g1_throw.py
```

This should open the MuJoCo viewer and show the trained policy.

Check:

```text
Does the full G1 load correctly?
Is the ball attached to the hand at the beginning?
Does only the selected arm move?
Does the ball release?
Does the ball fly toward the target?
Do the legs and body remain mostly fixed?
Does the simulation remain stable?
```

---

## 18. Evaluate the trained G1 policy

Run:

```bash
python3 scripts/evaluate_g1_throw.py
```

Suggested first success criterion:

```text
Mean best distance < 0.8 m
```

Good result:

```text
Hit rate below 50 cm > 50%
```

Very good result:

```text
Hit rate below 30 cm > 50%
```

Save a good policy before overwriting it:

```bash
cp policies/g1_fixed_body_throw_ppo.zip policies/g1_fixed_body_throw_scripted_release_good.zip
```

---

# Part C — Important modeling notes

## Controlled fixed joints versus physically locked joints

There are two ways to interpret “fixed joints.”

### Controlled fixed joints

This is the recommended first approach.

```text
All joints still exist.
The full humanoid remains in the simulation.
Non-arm joints are commanded to stay at nominal positions.
Only the throwing arm receives RL actions.
```

This is easier, more flexible, and usually sufficient for the first humanoid throwing experiment.

### Physically locked joints

This means the joints cannot move at all. This requires more MJCF editing, such as:

```text
removing joints
removing the floating base
adding equality constraints
using very tight joint ranges
using very high stiffness and damping
```

For the first G1 throwing task, use controlled fixed joints. If the body falls or moves too much, the floating base or torso can be fixed later.

---

## Scripted release versus learned release

The first throwing examples use a scripted ball release.

This means:

```text
The ball is welded to the hand at the beginning.
At a predefined time, the weld is disabled.
The ball then flies freely.
```

This is easier than learning both the arm motion and the release timing at the same time.

After the scripted-release version works, the next step is learned release. In that version, the policy action includes a release command.

The intended progression is:

```text
scripted release, fixed target
learned release, fixed target
learned release, random target
partially unlocked torso
full humanoid throwing
```

---

# Troubleshooting

## `ModuleNotFoundError: No module named 'mujoco'`

This means MuJoCo is not installed in the currently active Python environment.

Activate the virtual environment and install dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python3 -c "import mujoco; print(mujoco.__version__)"
```

If needed, run scripts explicitly with the virtual environment Python:

```bash
.venv/bin/python scripts/inspect_g1.py
```

---

## Wrong Python environment is used

Check which Python executable is currently active:

```bash
which python
```

If the virtual environment is active, the path should contain `.venv`.

Example:

```text
/home/user/humanoid_ws/humanoid-robot-fundamentals/.venv/bin/python
```

---

## `ModuleNotFoundError: No module named 'envs...'`

Run scripts from the repository root:

```bash
cd ~/humanoid_ws/humanoid-robot-fundamentals
```

The provided scripts add the repository root to `sys.path` automatically.

---

## `FileNotFoundError: Copy Unitree G1 assets to assets/unitree_g1 first.`

This means the repository scripts are installed, but the Unitree G1 model files have not been copied yet.

Run:

```bash
cd ~/humanoid_ws/humanoid-robot-fundamentals
mkdir -p external
git clone https://github.com/google-deepmind/mujoco_menagerie.git external/mujoco_menagerie

mkdir -p assets/unitree_g1
cp -r external/mujoco_menagerie/unitree_g1/* assets/unitree_g1/
```

Then verify:

```bash
ls assets/unitree_g1/scene.xml
```

If this command prints the file path, retry:

```bash
python3 scripts/view_g1.py
```

If `external/mujoco_menagerie` already exists, skip the `git clone` command and only copy the G1 files:

```bash
mkdir -p assets/unitree_g1
cp -r external/mujoco_menagerie/unitree_g1/* assets/unitree_g1/
```

---

## MuJoCo error: `free joint can only be used on top level`

This happens when a body with a `freejoint` is nested inside another moving body.

For throwing tasks, the ball must be a top-level body under `<worldbody>` and temporarily attached to the hand with a weld equality constraint.

Correct concept:

```text
worldbody
├── robot
├── throw_ball with freejoint
└── throw_target
```

Incorrect concept:

```text
robot
└── hand
    └── throw_ball with freejoint
```

---

## XML parse error on line 1

If MuJoCo reports an XML parse error on line 1, the XML file may contain invalid copied text, markdown backticks, or invisible characters.

Check the first lines:

```bash
head -n 5 assets/three_link_throw.xml
```

The first line should start directly with:

```xml
<mujoco model="...">
```

---

## Training script does not open a simulator window

This is normal.

Training scripts usually run headlessly:

```bash
python3 scripts/train_throw.py
python3 scripts/train_g1_throw.py
```

Viewer scripts are used separately:

```bash
python3 scripts/random_policy_viewer.py
python3 scripts/random_g1_throw_viewer.py
python3 scripts/play_throw.py
python3 scripts/play_g1_throw.py
```

This is faster and more practical, especially on CPU-only systems.

---

## Training does not stop immediately after reducing `total_timesteps`

PPO collects full rollout batches. For example, with:

```python
num_envs = 4
n_steps = 128
```

one rollout contains:

```text
4 x 128 = 512 timesteps
```

Therefore, very small values such as:

```python
model.learn(total_timesteps=30)
```

may still run for at least one rollout.

For a quick debug run, use smaller rollout settings:

```python
num_envs = 1
n_steps = 16
batch_size = 16
model.learn(total_timesteps=30)
```

---

## Ball is not attached to the hand

The weld constraint probably uses the wrong body name.

Run:

```bash
python3 scripts/inspect_g1_bodies.py
```

Then regenerate the scene:

```bash
python3 scripts/create_g1_throw_scene.py --hand-body RIGHT_HAND_OR_WRIST_BODY_NAME
```

---

## Robot body falls during G1 throwing

Possible causes:

```text
floating base is not fixed
lower-body actuators are not strong enough
nominal pose is unstable
```

Possible solutions:

```text
increase non-arm actuator stiffness
use a better keyframe or nominal pose
fix the pelvis or torso for the first throwing experiment
remove the root freejoint in a copied XML
add a weld constraint from torso or pelvis to the world
```

For the first fixed-body throwing task, it is acceptable to fix the base.

---

## Arm barely moves

Increase the action scale in both training and playback scripts.

Example:

```python
action_scale=0.5
```

can be changed to:

```python
action_scale=0.8
```

Then retrain the policy.

---

## Ball releases too early or too late

Tune the scripted release time.

Example values:

```python
scripted_release_time=0.45
scripted_release_time=0.55
scripted_release_time=0.65
scripted_release_time=0.75
```

After changing the release time, retrain the policy.

---

# Recommended learning path

```text
1. Verify Python and MuJoCo installation
2. Run a minimal MuJoCo simulation
3. Run the 3-link random throwing viewer
4. Train the 3-link scripted-release throwing policy
5. Play and evaluate the 3-link policy
6. Load and inspect the Unitree G1 model
7. Add a ball and target to the G1 scene
8. Weld the ball to the right hand or wrist
9. Run the random G1 throwing viewer
10. Train the G1 fixed-body scripted-release throwing policy
11. Play and evaluate the G1 policy
12. Save a successful policy checkpoint
13. Switch from scripted release to learned release
14. Add random target positions
15. Gradually unlock additional humanoid joints
```
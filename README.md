# Humanoid Robot Fundamentals

Starter workspace for humanoid robotics examples using MuJoCo, Gymnasium, and Stable-Baselines3.

## Quick start

```bash
cd ~/humanoid_ws/humanoid-robot-fundamentals
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python scripts/test_python_setup.py
python scripts/test_mujoco_setup.py
python scripts/random_policy_viewer.py
```

## Unitree G1 setup

The Unitree G1 assets are not bundled. Fetch them from MuJoCo Menagerie:

```bash
mkdir -p external
git clone https://github.com/google-deepmind/mujoco_menagerie.git external/mujoco_menagerie
mkdir -p assets/unitree_g1
cp -r external/mujoco_menagerie/unitree_g1/* assets/unitree_g1/
```

Then run:

```bash
python scripts/view_g1.py
python scripts/inspect_g1.py
python scripts/inspect_g1_bodies.py
python scripts/create_g1_throw_scene.py --hand-body RIGHT_HAND_OR_WRIST_BODY_NAME
python scripts/random_g1_throw_viewer.py
```

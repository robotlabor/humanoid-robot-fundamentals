# Assets

The starter package includes `three_link_throw.xml`.

The Unitree G1 model should be copied here from MuJoCo Menagerie:

```bash
mkdir -p external
git clone https://github.com/google-deepmind/mujoco_menagerie.git external/mujoco_menagerie
mkdir -p assets/unitree_g1
cp -r external/mujoco_menagerie/unitree_g1/* assets/unitree_g1/
```

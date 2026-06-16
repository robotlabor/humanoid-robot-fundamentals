#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import time, numpy as np, mujoco, mujoco.viewer
from envs.g1_fixed_body_throw_env import G1FixedBodyThrowEnv
if __name__ == '__main__':
    env=G1FixedBodyThrowEnv(xml_path=str(ROOT/'assets'/'unitree_g1'/'scene_throw.xml'))
    print('Detected right arm joints:'); [print('  ',n) for n in env.arm_joint_names]
    obs,info=env.reset()
    with mujoco.viewer.launch_passive(env.model,env.data) as viewer:
        while viewer.is_running():
            t=env.step_count*env.control_dt; action=np.zeros(env.action_space.shape[0],dtype=np.float32)
            for i in range(min(env.n_arm,7)): action[i]=0.5*np.sin((4.0+0.4*i)*t+0.5*i)
            obs,reward,terminated,truncated,info=env.step(action); viewer.sync(); time.sleep(env.control_dt)
            if terminated or truncated: print(info); obs,info=env.reset()

#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from stable_baselines3 import PPO
from envs.three_link_throw_env import ThreeLinkThrowEnv
if __name__ == '__main__':
    env=ThreeLinkThrowEnv(xml_path=str(ROOT/'assets'/'three_link_throw.xml')); model=PPO.load(str(ROOT/'policies'/'three_link_throw_ppo.zip'))
    best=[]; final=[]
    for _ in range(50):
        obs,_=env.reset(); done=False; info={}
        while not done:
            action,_=model.predict(obs,deterministic=True); obs,reward,terminated,truncated,info=env.step(action); done=terminated or truncated
        best.append(info.get('best_dist',np.inf)); final.append(info.get('dist_to_target',np.inf))
    best=np.array(best); final=np.array(final)
    print('3-link throw evaluation'); print('-----------------------')
    print(f'Mean best distance: {best.mean():.3f} m'); print(f'Hit rate < 30 cm: {100*np.mean(best<0.30):.1f}%')

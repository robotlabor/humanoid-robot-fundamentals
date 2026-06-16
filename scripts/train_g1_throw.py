#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from envs.g1_fixed_body_throw_env import G1FixedBodyThrowEnv

def make_env(rank, learned_release=False):
    def _init(): return G1FixedBodyThrowEnv(xml_path=str(ROOT/'assets'/'unitree_g1'/'scene_throw.xml'), learned_release=learned_release)
    return _init
if __name__=='__main__':
    test_env=make_env(0)(); check_env(test_env,warn=True); print('Detected right arm joints:'); [print('  ',n) for n in test_env.arm_joint_names]
    num_envs=1; learned_release=False; env=DummyVecEnv([make_env(0,learned_release)])
    model=PPO('MlpPolicy',env,learning_rate=3e-4,n_steps=64,batch_size=64,gamma=0.98,gae_lambda=0.95,clip_range=0.2,policy_kwargs=dict(net_arch=[128,128]),verbose=1,tensorboard_log=str(ROOT/'logs'/'tb_g1'))
    (ROOT/'policies').mkdir(exist_ok=True)
    try: model.learn(total_timesteps=200_000)
    except KeyboardInterrupt: print('\nInterrupted. Saving current policy...')
    model.save(str(ROOT/'policies'/'g1_fixed_body_throw_ppo')); print('Saved policy to policies/g1_fixed_body_throw_ppo.zip')


from __future__ import annotations
from pathlib import Path
import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces

class ThreeLinkThrowEnv(gym.Env):
    metadata = {"render_modes": []}
    def __init__(self, xml_path=None, episode_time=1.6, control_dt=0.02, action_scale=1.1, learned_release=False, scripted_release_time=0.55, target_pos=(2.0,0.0,0.65), debug_print=False):
        super().__init__()
        if xml_path is None:
            xml_path = Path(__file__).resolve().parents[1] / 'assets' / 'three_link_throw.xml'
        self.model = mujoco.MjModel.from_xml_path(str(xml_path)); self.data = mujoco.MjData(self.model)
        self.episode_time=float(episode_time); self.control_dt=float(control_dt); self.frame_skip=max(1,int(round(self.control_dt/self.model.opt.timestep)))
        self.action_scale=float(action_scale); self.learned_release=bool(learned_release); self.scripted_release_time=float(scripted_release_time); self.debug_print=bool(debug_print)
        self.target_pos=np.array(target_pos,dtype=np.float64)
        self.target_body_id=mujoco.mj_name2id(self.model,mujoco.mjtObj.mjOBJ_BODY,'target')
        self.ball_body_id=mujoco.mj_name2id(self.model,mujoco.mjtObj.mjOBJ_BODY,'ball')
        self.hold_eq_id=mujoco.mj_name2id(self.model,mujoco.mjtObj.mjOBJ_EQUALITY,'hold_ball')
        self.joint_names=['shoulder','elbow','wrist']
        self.joint_qpos_adr=np.array([self.model.jnt_qposadr[mujoco.mj_name2id(self.model,mujoco.mjtObj.mjOBJ_JOINT,n)] for n in self.joint_names])
        self.joint_qvel_adr=np.array([self.model.jnt_dofadr[mujoco.mj_name2id(self.model,mujoco.mjtObj.mjOBJ_JOINT,n)] for n in self.joint_names])
        self.q_nominal=np.array([-0.65,1.15,0.35],dtype=np.float64)
        self.action_space=spaces.Box(-1.0,1.0,shape=(4,),dtype=np.float32)
        self.observation_space=spaces.Box(-np.inf,np.inf,shape=(21,),dtype=np.float32)
        self.prev_action=np.zeros(4,dtype=np.float64); self.released=False; self.step_count=0; self.best_dist=np.inf; self.release_time=None
    def reset(self, seed=None, options=None):
        super().reset(seed=seed); mujoco.mj_resetData(self.model,self.data); self.model.body_pos[self.target_body_id]=self.target_pos
        self.data.qpos[self.joint_qpos_adr]=self.q_nominal+self.np_random.uniform(-0.05,0.05,3); self.data.qvel[self.joint_qvel_adr]=self.np_random.uniform(-0.02,0.02,3)
        if self.hold_eq_id>=0: self.data.eq_active[self.hold_eq_id]=1
        self.data.ctrl[:]=self.q_nominal; mujoco.mj_forward(self.model,self.data)
        self.prev_action[:]=0; self.released=False; self.step_count=0; self.best_dist=np.inf; self.release_time=None
        return self._get_obs(), {}
    def step(self, action):
        action=np.clip(np.asarray(action,dtype=np.float64),-1,1); self.data.ctrl[:]=np.clip(self.q_nominal+self.action_scale*action[:3],-2.8,2.8)
        t=self.step_count*self.control_dt
        if not self.released:
            do_release = action[3]>0.5 if self.learned_release else t>=self.scripted_release_time
            if do_release:
                if self.hold_eq_id>=0: self.data.eq_active[self.hold_eq_id]=0
                self.released=True; self.release_time=t
        for _ in range(self.frame_skip): mujoco.mj_step(self.model,self.data)
        self.step_count+=1
        if self.debug_print and self.step_count%10==0: print(f"step={self.step_count}, time={self.step_count*self.control_dt:.3f}, released={self.released}")
        obs=self._get_obs(); reward=self._compute_reward(action); dist=np.linalg.norm(self._ball_pos()-self.target_pos); self.best_dist=min(self.best_dist,dist)
        terminated=bool(self._ball_pos()[2]<0.02 or self._ball_pos()[0]>3.5 or abs(self._ball_pos()[1])>1.5); truncated=bool(self.step_count*self.control_dt>=self.episode_time)
        info={'dist_to_target':float(dist),'best_dist':float(self.best_dist),'released':self.released,'release_time':self.release_time}
        self.prev_action=action.copy(); return obs,float(reward),terminated,truncated,info
    def _compute_reward(self, action):
        ball_pos=self._ball_pos(); ball_vel=self._ball_vel(); to_target=self.target_pos-ball_pos; dist=np.linalg.norm(to_target)+1e-6; direction=to_target/dist
        vtt=np.dot(ball_vel,direction); acc=np.exp(-2.5*dist); q=self.data.qpos[self.joint_qpos_adr]; dq=self.data.qvel[self.joint_qvel_adr]
        r=0.03*max(vtt,0.0) if not self.released else 1.5*acc+0.02*max(vtt,0.0)
        if self.learned_release and not self.released: r-=0.001
        if dist<0.15: r+=10.0
        elif dist<0.30: r+=3.0
        r-=0.005*np.linalg.norm(action-self.prev_action)+0.002*np.linalg.norm(q-self.q_nominal)+0.0005*np.linalg.norm(dq)+0.0005*np.linalg.norm(action[:3])
        return r
    def _get_obs(self):
        return np.concatenate([self.data.qpos[self.joint_qpos_adr], self.data.qvel[self.joint_qvel_adr], self._ball_pos(), self._ball_vel(), self.target_pos, self.prev_action, [1.0 if self.released else 0.0], [max(0.0,self.episode_time-self.step_count*self.control_dt)]]).astype(np.float32)
    def _ball_pos(self): return self.data.xpos[self.ball_body_id].copy()
    def _ball_vel(self):
        vel=np.zeros(6); mujoco.mj_objectVelocity(self.model,self.data,mujoco.mjtObj.mjOBJ_BODY,self.ball_body_id,vel,0); return vel[:3].copy()

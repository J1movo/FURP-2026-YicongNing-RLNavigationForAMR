"""PointNav smoke test — shortest-path follower.

Based on official Habitat example, runs 3 episodes with optimal path planning.
Outputs trajectory videos for visual verification.
"""
import os
import shutil

import numpy as np

import habitat
from habitat.tasks.nav.shortest_path_follower import ShortestPathFollower
from habitat.utils.visualizations import maps
from habitat.utils.visualizations.utils import images_to_video

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "results", "shortest_path")
os.makedirs(OUTPUT_DIR, exist_ok=True)


class SimpleRLEnv(habitat.RLEnv):
    def get_reward_range(self):
        return [-1, 1]

    def get_reward(self, observations):
        return 0

    def get_done(self, observations):
        return self.habitat_env.episode_over

    def get_info(self, observations):
        return self.habitat_env.get_metrics()


def draw_top_down_map(info, output_size):
    return maps.colorize_draw_agent_and_fit_to_height(
        info["top_down_map"], output_size
    )


def main():
    print("=" * 60)
    print("POINTNAV SMOKE TEST (shortest-path follower)")
    print("=" * 60)

    config = habitat.get_config(
        config_path="benchmark/nav/pointnav/pointnav_habitat_test.yaml",
        overrides=[
            "+habitat/task/measurements@habitat.task.measurements.top_down_map=top_down_map"
        ],
    )

    with SimpleRLEnv(config=config) as env:
        goal_radius = env.episodes[0].goals[0].radius
        if goal_radius is None:
            goal_radius = config.habitat.simulator.forward_step_size
        follower = ShortestPathFollower(
            env.habitat_env.sim, goal_radius, False
        )

        print("Environment creation successful")
        print(f"  Output: {OUTPUT_DIR}")

        successes = 0

        for episode in range(3):
            env.reset()

            start_dist = env.habitat_env.current_episode.info["geodesic_distance"]
            scene = env.habitat_env.current_episode.scene_id.split("/")[-1]
            print(f"\n--- Episode {episode + 1}: {scene} ---")
            print(f"  Start → Goal: {start_dist:.2f}m")

            dirname = os.path.join(OUTPUT_DIR, f"{episode:02d}")
            if os.path.exists(dirname):
                shutil.rmtree(dirname)
            os.makedirs(dirname)

            images = []
            steps = 0
            while not env.habitat_env.episode_over:
                best_action = follower.get_next_action(
                    env.habitat_env.current_episode.goals[0].position
                )
                if best_action is None:
                    break

                observations, reward, done, info = env.step(best_action)
                steps += 1

                im = observations["rgb"]
                top_down_map = draw_top_down_map(info, im.shape[0])
                output_im = np.concatenate((im, top_down_map), axis=1)
                images.append(output_im)

            metrics = env.habitat_env.get_metrics()
            dist_to_goal = metrics["distance_to_goal"]
            success = metrics["success"]

            if success:
                successes += 1

            images_to_video(images, dirname, "trajectory")
            print(f"  Steps: {steps}")
            print(f"  Dist to goal: {dist_to_goal:.3f}m")
            print(f"  SUCCESS: {bool(success)}")
            print(f"  Video: {dirname}/trajectory.mp4")

    print("\n" + "=" * 60)
    print(f"RESULT: {successes}/3 episodes reached goal")
    if successes >= 2:
        print("POINTNAV SMOKE TEST PASSED")
    else:
        print("POINTNAV SMOKE TEST FAILED")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""
在 import 任何 habitat / habitat_baselines 策略代码之前，先运行这个模块，
往 sys.modules 里注入若干假模块，绕开两处"意外硬依赖 habitat_sim/magnum"的
死代码路径（详见 02-技术栈.md 的排查记录）。

背景：
1. resnet_policy.py 顶部
       from habitat.tasks.nav.instance_image_nav_task import InstanceImageGoalSensor
   instance_image_nav_task.py 顶部无条件 `import habitat_sim`。
   我们的 checkpoint 不用 InstanceImageGoal 传感器，这是死代码路径。

2. nav.py 顶部
       from habitat.sims.habitat_simulator.actions import HabitatSimActions
   这行会先执行 habitat/sims/habitat_simulator/__init__.py，它顶部无条件
       from habitat.sims.habitat_simulator.object_state_machine import ObjectStateMachine
   而 object_state_machine.py 顶部无条件 `import magnum as mn`（habitat_sim的
   C++图形绑定库）。ObjectStateMachine 只在这个 __init__.py 里被 import，
   没有在我们真正用到的代码路径（registration.py/nav.py/env.py）里被调用，
   同样是死代码路径。真正的 habitat_sim 可用性检测在 registration.py 的
   `_try_register_habitat_sim()` 里，那里本身就有 try/except 保护，
   不受这个 stub 影响。

3. habitat/core/env.py 顶部
       from habitat.tasks.registration import make_task
   这行会触发 habitat/tasks/registration.py 末尾无条件调用的
       _try_register_rearrange_task()
   这个函数名叫"try"，但函数体本身**没有** try/except 保护（不同于同目录下
   eqa/nav/vln 三个任务和 habitat/datasets/*/__init__.py 里的注册函数——那些
   都规范地用 try/except 包住了），直接无条件 import 了24个 rearrange 子模块
   （机械臂抓取/放置/搬运任务专用），其中多个会 import magnum。
   PointNav 任务与 rearrange 任务体系完全独立、不共享代码，我们真正用到的
   路径（nav.py/object_nav_task.py/resnet_policy.py 等）都不依赖
   habitat.tasks.rearrange 的任何实际内容，所以直接把整个
   habitat.tasks.rearrange 包 stub 成一个空注册函数，一次性绕开这24个
   子模块的传递依赖，而不是逐个排查它们各自还缺什么包。

4. habitat/__init__.py 顶部
       from habitat.core.vector_env import ThreadedVectorEnv, VectorEnv
   vector_env.py 顶部无条件
       from habitat.core.batch_rendering.env_batch_renderer import EnvBatchRenderer
   这是训练时用于 GPU 批量并行渲染多个仿真环境的加速功能，只在
   `VectorEnv.initialize_batch_renderer()` 这一个方法里被实例化，且该方法
   要求 config 开启 `enable_batch_renderer` 才会被调用——我们的推理脚本
   根本不会创建 VectorEnv 实例，更不会调用这个方法，是死代码路径。

已对整个 habitat-lab 代码库做过全量排查（`grep -rl "^import magnum\|^import habitat_sim"`），
确认其余含这两个硬依赖的文件（`articulated_agents/*`、`tasks/rearrange/*`、
`datasets/rearrange/*`、`sims/habitat_simulator/{habitat_simulator,debug_visualizer,
sim_utilities,kinematic_relationship_manager}.py` 等）都只能通过上述已 stub
的路径或 `_try_register_habitat_sim()`（本身有 try/except 保护）间接到达，
不会在我们的推理 import 链上被直接触发。

Jetson 上不装 habitat_sim / magnum（GPU渲染仿真器相关，机器人推理用不到），
所以在真正 import habitat 相关代码之前，先用这些 stub 模块占位。

用法（必须在 import 任何 habitat / habitat_baselines 代码之前调用一次）：
    import habitat_stub
    habitat_stub.install()
"""
import sys
import types


def install():
    _install_instance_image_nav_task_stub()
    _install_object_state_machine_stub()
    _install_rearrange_task_stub()
    _install_env_batch_renderer_stub()
    _install_rearrange_sim_stub()


def _install_instance_image_nav_task_stub():
    module_name = "habitat.tasks.nav.instance_image_nav_task"
    if module_name in sys.modules:
        return  # 已经装过了，或者真实模块已经被 import 过

    stub_module = types.ModuleType(module_name)

    class InstanceImageGoalSensor:
        """占位类，只提供 resnet_policy.py 运行时需要用到的 cls_uuid 字符串。
        真实定义见 habitat/tasks/nav/instance_image_nav_task.py，这里不需要
        它的任何实际行为，因为我们的 checkpoint 训练时没用这个传感器。"""

        cls_uuid: str = "instance_imagegoal"

    stub_module.InstanceImageGoalSensor = InstanceImageGoalSensor
    sys.modules[module_name] = stub_module


def _install_object_state_machine_stub():
    module_name = "habitat.sims.habitat_simulator.object_state_machine"
    if module_name in sys.modules:
        return

    stub_module = types.ModuleType(module_name)

    class ObjectStateMachine:
        """占位类。真实定义见 habitat/sims/habitat_simulator/
        object_state_machine.py，管理仿真里物体的非几何状态（如"开/关"），
        我们的推理链路（registration.py/nav.py/env.py）不会用到它，
        只是被 habitat_simulator/__init__.py 顺带 import 了一下。"""

        def __init__(self, *args, **kwargs):
            pass

    stub_module.ObjectStateMachine = ObjectStateMachine
    sys.modules[module_name] = stub_module


def _install_rearrange_task_stub():
    module_name = "habitat.tasks.rearrange"
    if module_name in sys.modules:
        return

    stub_module = types.ModuleType(module_name)

    def _try_register_rearrange_task():
        """空注册函数。真实版本会 import 24 个 rearrange 子模块（机械臂抓取/
        放置/搬运任务，多个直接依赖 magnum），我们的 PointNav 推理链路完全
        用不到 rearrange 任务体系，直接跳过注册。"""
        pass

    stub_module._try_register_rearrange_task = _try_register_rearrange_task
    sys.modules[module_name] = stub_module


def _install_env_batch_renderer_stub():
    module_name = "habitat.core.batch_rendering.env_batch_renderer"
    if module_name in sys.modules:
        return

    stub_module = types.ModuleType(module_name)

    class EnvBatchRenderer:
        """占位类。真实定义见 habitat/core/batch_rendering/
        env_batch_renderer.py，用于训练时GPU批量并行渲染多个仿真环境，
        只在 VectorEnv.initialize_batch_renderer() 里被实例化（且要求
        config.enable_batch_renderer=True 才会调用）。我们的推理脚本
        不创建 VectorEnv 实例，用不到这个类。"""

        def __init__(self, *args, **kwargs):
            pass

    stub_module.EnvBatchRenderer = EnvBatchRenderer
    sys.modules[module_name] = stub_module


def _install_rearrange_sim_stub():
    """gym_wrapper.py（被 habitat/gym/__init__.py 无条件 import）需要从
    habitat.tasks.rearrange.rearrange_sim 借用一个跟渲染/仿真无关的纯装饰器
    函数 add_perf_timing_func（性能计时用）。真实定义其实在
    habitat/tasks/rearrange/utils.py 里，rearrange_sim.py 只是转手 import
    它。我们已经把 habitat.tasks.rearrange 整个包 stub 掉了（见上方
    _install_rearrange_task_stub 的说明），所以这里要单独把
    habitat.tasks.rearrange.rearrange_sim 这个子模块也补上，否则
    `from habitat.tasks.rearrange.rearrange_sim import add_perf_timing_func`
    会报 "rearrange 不是一个包" 的错误。"""
    module_name = "habitat.tasks.rearrange.rearrange_sim"
    if module_name in sys.modules:
        return

    from functools import wraps

    def add_perf_timing_func(name=None):
        """占位实现：直接返回原函数，不做任何计时。真实版本会把耗时记录到
        RearrangeSim 实例上，我们的推理链路不创建 RearrangeSim，不需要这个
        功能，但装饰器本身必须存在且可调用，否则 `@add_perf_timing_func()`
        这行装饰器语法会报错。"""

        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            return wrapper

        return decorator

    stub_module = types.ModuleType(module_name)
    stub_module.add_perf_timing_func = add_perf_timing_func
    sys.modules[module_name] = stub_module


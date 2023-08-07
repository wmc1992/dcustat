# `gcustat`

一个能够简洁的显示海光 DCU 设备状态的命令行工具；

之前使用GPU时习惯了使用工具 [`gpustat`](https://github.com/wookayin/gpustat) 查看GPU状态，使用海光的 DCU 设备之后发现并没有类似的工具，于是仿照  [`gpustat`](https://github.com/wookayin/gpustat) 自己写了一个；
显示效果如下图：

<div align=center><img src="./docs/dcustat.png" width=40% alt="dcustat png" /></div>

## 依赖说明

python版本要求：`python>=3.6`；

## 安装说明

```
pip install dcustat
```

## 使用说明

使用如下命令单次获取当前 dcu 设备信息：

```shell
dcustat
```

使用如下命令动态刷新当前 dcu 设备信息，默认每2秒刷新一次：

```
dcustat --watch
```

可选参数如下：

```
usage: cli.py [-h] [-i [INTERVAL]] [--light] [--debug] [-v]

optional arguments:

  -h, --help            show this help message and exit

  -i [INTERVAL], --interval [INTERVAL], --watch [INTERVAL]
                        动态刷新模式；INTERVAL为刷新间隔，单位：秒；默认每2秒刷新一次；

  --light               使用较亮的模式显示，如果显示器渲染出来的结果较暗，可以打开该参数；

  --debug               Debug模式时允许在程序出错的情况下打印更多的调试信息；

  -v, --version         show program's version number and exit
```



|默认|加--light参数|
|---|---|
|<img src="./docs/dcustat_dark.png" width="100%" align=center />|<img src="./docs/dcustat_light.png" width="100%" align=center />|

## 显示内容说明

```
machine_name  Mon Dec 20 22:38:59 2021  ascend-dmi version: 2.0.3
========================================================
[加速卡ID], 加速卡类型, 功率
[芯片ID] [DeviceID] Health, 芯片名称 | 温度, AICore, 内存
========================================================

[1], Atlas 300I-3000, 16.30 W
[0] [1] OK, Ascend 310 | 51°C,   0 %, 2621 MB / 8192 MB
```

* header：第1行为header，可以使用参数 `--no-header` 不展示该信息；展示的信息从左到右依次为机器名称、当前时间、软件 `ascend-dmi/npu-smi` 的版本；

* title：第2~5行为title，可以使用参数 `--no-title` 不展示该信息；title是对后面展示的信息的各字段的说明；

*  `[1], Atlas 300I-3000, 16.30 W`：每个加速卡的信息：
    * `[1]`：加速卡ID；
    * `Atlas 300I-3000`：加速卡类型；
    * `16.30 W`： 加速卡实时功率；

*  `[0] [1] OK, Ascend 310 | 51°C,   0 %, 2621 MB / 8192 MB`：每个芯片的信息：
    * `[0]`：芯片ID；
    * `[1]`：DeviceID；
    * `OK`：芯片健康状态；
    * `Ascend 310`：芯片名称；
    * `51°C`：温度；
    * `0 %`：AICore；
    * `2621 MB / 8192 MB`：内存；

## Reference

本项目的灵感、排版展示、以及代码的整体结构都是源自 [`gpustat`](https://github.com/wookayin/gpustat)，本项目只是将其工作适配到了华为Atlas设备上；

## License

[MIT License](./LICENSE)

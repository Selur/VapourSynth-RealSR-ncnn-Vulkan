# VapourSynth-RealSR-ncnn-Vulkan

[![Build Status](https://github.com/Kiyamou/VapourSynth-RealSR-ncnn-Vulkan/workflows/CI/badge.svg)](https://github.com/Kiyamou/VapourSynth-RealSR-ncnn-Vulkan/actions)

RealSR super resolution for VapourSynth, based on [realsr-ncnn-vulkan](https://github.com/nihui/realsr-ncnn-vulkan). Some code is from [vapoursynth-waifu2x-ncnn-vulkan](https://github.com/Nlzy/vapoursynth-waifu2x-ncnn-vulkan).

Due to only supporting 4x scale, the filter is slow.

## Usage

```python
core.rsnv.RealSR(clip clip, [int scale, int tilesize_x, int tilesize_y,
                 int model, int gpu_id, int gpu_thread, bool tta])
```

Models should be located in folder `models`, and folder `models` should be located in the same folder as dynamic link library.

* ***clip***
  * Required parameter.
  * Clip to process.
  * Only 32bit RGB is supported.
* ***scale***
  * Optional parameter. Only support 4x scale.
* ***tilesize_x***
  * Optional parameter. *Default: 100*.
  * The tilesize for horizontal.
  * **Recommend to set as 100** to make sure the plugin run normally (#issue 1).
  * ~~Recommend to set a value that can divide the width.~~
  * Due to only supporting 4x scale, it is not recommended to set too large.
* ***tilesize_y***
  * Optional parameter. *Default: same as tilesize_x*.
  * The tilesize for vertical.
  * **Recommend to set as 100.**
  * ~~Recommend to set a value that can divide the height.~~
  * Due to only supporting 4x scale, it is not recommended to set too large.
* ***model***
  * Optional parameter. *Default: 1*.
  * Select pre-trained model:
    * model = 0: models-DF2K
    * model = 1: models-DF2K_JPEG
* ***gpu_id***
  * Optional parameter. *Default: 0*.
  * If you have more than one gpu devices, you can select gpu device by the parameter.
* ***tta***
  * Optional parameter. *Default: False*.
  * If true, quality will be improved, but speed will be significantly slower.

## VapourSynth API 4 and wheels

This fork targets the VapourSynth API 4 (R55 and newer, required since R80). The namespace `rsnv`, the function and
its arguments are unchanged. It builds against ncnn 20260526, which loads the Vulkan driver itself, so no Vulkan SDK is
needed.

Each instance compiles its own shaders: with a shader cache shared by all instances, a `tta=True` instance after a
non-TTA one in the same process got the non-TTA shader and failed with `binding_count not match`.

Wheels for Windows x64, Linux x86_64 and macOS arm64 are attached to the GitHub releases. They contain the models of
[realsr-ncnn-vulkan 20220728](https://github.com/nihui/realsr-ncnn-vulkan/releases/tag/20220728):

```
pip install vapoursynth_realsr_ncnn_vulkan-<version>-py3-none-<platform>.whl
```

The plugin and its `models` folder go to `site-packages/vapoursynth/plugins/realsr`.

## Compilation

```
git clone --recursive https://github.com/Selur/VapourSynth-RealSR-ncnn-Vulkan
cd VapourSynth-RealSR-ncnn-Vulkan
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

The VapourSynth API 4 headers are vendored in `include/vapoursynth`. For the tests, put the `models-*` folders of the
realsr-ncnn-vulkan release into `build/models` and run `python3 test/test_realsr.py build/librealsrnv.so`.

## Reference Code

* realsr-ncnn-vulkan: https://github.com/nihui/realsr-ncnn-vulkan
* vapoursynth-waifu2x-ncnn-vulkan: https://github.com/Nlzy/vapoursynth-waifu2x-ncnn-vulkan

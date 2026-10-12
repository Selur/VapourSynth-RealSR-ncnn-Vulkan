#!/usr/bin/env python3
"""Functional tests for the RealSR ncnn Vulkan VapourSynth plugin.

Usage: python3 test/test_realsr.py [path/to/librealsrnv.so]

Without an argument the plugin is expected to be autoloaded (e.g. from the
installed wheel) or to be found below site-packages/vapoursynth/plugins.
The models have to lie in a folder 'models' next to the plugin.

Without a Vulkan device the test checks loading, the models and the errors;
with one it also upscales a small clip.

Requires the vapoursynth Python module (R55 or newer).
"""
import glob
import os
import sys

import vapoursynth as vs

core = vs.core


def load_plugin(args):
    if args:
        core.std.LoadPlugin(args[0])
        return
    if hasattr(core, "rsnv"):
        return
    # Wheel layout: site-packages/vapoursynth/plugins/realsr/<plugin> with models/ next to it
    plugin_dir = os.path.join(os.path.dirname(vs.__file__), "plugins")
    for ext in ("so", "dll", "dylib"):
        for path in glob.glob(os.path.join(plugin_dir, "**", "*realsrnv." + ext), recursive=True):
            core.std.LoadPlugin(path)
            return
    raise SystemExit("FAIL: rsnv plugin is neither autoloaded nor found below " + plugin_dir)


def check(cond, msg):
    if not cond:
        raise SystemExit("FAIL: " + msg)
    print("ok  ", msg)


def error_of(fn):
    try:
        fn()
    except vs.Error as e:
        return str(e).strip().splitlines()[-1]
    return None


def expect_error(fn, msg, contains=""):
    error = error_of(fn)
    check(error is not None and contains in error, "%s (%s)" % (msg, error))


def main():
    load_plugin(sys.argv[1:])
    check(hasattr(core, "rsnv"), "plugin loaded (namespace rsnv)")

    clip = core.std.BlankClip(width=96, height=64, format=vs.RGBS, length=2, color=[0.2, 0.5, 0.8])
    expect_error(lambda: core.rsnv.RealSR(clip.resize.Point(format=vs.RGB24)), "integer input rejected", "32 bits float")
    expect_error(lambda: core.rsnv.RealSR(clip, scale=2), "scale 2 rejected", "4 scale")
    expect_error(lambda: core.rsnv.RealSR(clip, model=2), "model 2 rejected", "0 or 1")

    gpu_error = error_of(lambda: core.rsnv.RealSR(clip, gpu_id=0).get_frame(0))
    if gpu_error is not None and "gpu_id" in gpu_error:
        # The model files were found, otherwise the call would have failed before the GPU check.
        check(True, "no Vulkan device: models found, error '%s'" % gpu_error)
    else:
        check(gpu_error is None, "upscale on the GPU runs (%s)" % gpu_error)
        for model in (0, 1):
            out = core.rsnv.RealSR(clip, model=model, gpu_id=0)
            f = out.get_frame(1)
            check((out.width, out.height, f.format.id) == (384, 256, vs.RGBS), "model %d: %dx%d RGBS" % (model, out.width, out.height))
        out = core.rsnv.RealSR(clip, tta=1, gpu_id=0)
        check(out.get_frame(0).width == 384, "tta after a non-tta instance in the same process")

    print("all tests passed")

if __name__ == "__main__":
    main()

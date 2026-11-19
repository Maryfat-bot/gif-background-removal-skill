# GIF Background Removal Skill

A Codex skill and helper script for removing backgrounds from animated GIFs while keeping the subject, frame timing, and loop behavior.

## Use

```bash
python -m pip install -r requirements.txt
python scripts/remove_gif_background.py input.gif output_transparent.gif
```

The first run downloads the selected `rembg` model weights. The model is not included in this repository. The script uses CPU inference for broad compatibility and writes a checkerboard preview beside the output GIF.

## Files

- `SKILL.md` — instructions for using the skill.
- `scripts/remove_gif_background.py` — frame-by-frame processing script.
- `requirements.txt` — Python dependencies.
- `LICENSE` — custom limited-use terms.

## License and public GitHub behavior

This repository is publicly viewable and uses a custom, restrictive license. It allows downloading and using an unmodified copy in personal or commercial projects. It does not grant permission to modify or redistribute the skill. This is not a standard open-source license.

A public GitHub repository can still be viewed and forked under GitHub's platform terms. The license cannot disable GitHub's fork feature. It governs the permissions beyond GitHub's platform features; read `LICENSE` before using the files.

The license covers only the skill and helper script. It does not claim rights in input images or files produced by running the tool; rights in those materials remain with their respective owners.

## 中文说明

这是一个 Codex GIF 去背 skill 和配套脚本。安装依赖后，运行脚本即可逐帧去背，并保留动画时长与循环设置。首次运行会下载模型权重；仓库不包含模型文件。

当前许可证允许下载未修改版本，并用于个人或商业项目；不允许修改、再发布或转售 skill 本身。仓库设为公开后，GitHub 仍允许用户查看和 fork。详见根目录 `LICENSE`。

版权署名沿用 `Maryfat-bot`。如果这不是你希望公开使用的账号名称，请在上传前调整 `LICENSE` 和本文件。

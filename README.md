# Voxta ComfyUI Nodes

ComfyUI nodes to create and integrate with Voxta

## Quickstart

1. Install [ComfyUI](https://docs.comfy.org/get_started).
1. Install [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
1. Look up this extension in ComfyUI-Manager. If you are installing manually, clone this repository under `ComfyUI/custom_nodes`.
1. Restart ComfyUI.

## Develop

To install the dev dependencies and pre-commit (will run the ruff hook), do:

```bash
pip install -e .[dev]
pre-commit install
```

The `-e` flag above will result in a "live" install, in the sense that any changes you make to your node extension will automatically be picked up the next time you run ComfyUI.

## Sample Workflow

[Voxta Character Generator Template.json](workflows/Voxta Character Generator Template.json) contains a sample workflow that uses the Voxta nodes.

## License

MIT License. See [LICENSE](LICENSE) for details.

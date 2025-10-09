import os
from .helpers import ComfyHelper, FolderHelper
from aiohttp import web
import server


class VoxtaOutputFolder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_path": ("STRING", {"default": "", "multiline": False}),
                "subfolder": ("STRING", {"default": "Avatars/Default", "multiline": False}),
            }
        }

    OUTPUT_IS_LIST = (False, False)
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("output_path", "subfolder")

    FUNCTION = "execute"
    CATEGORY = "Voxta"

    # noinspection PyMethodMayBeStatic
    def execute(self, output_path: list[str] | str, subfolder: list[str] | str):
        # Unwrap comfy list inputs to scalars
        root_raw = ComfyHelper.comfy_input_to_str(output_path, "")
        sub_raw = ComfyHelper.comfy_input_to_str(subfolder, "")
        if root_raw:
            # Create directory (sanitization + creation handled by FolderHelper)
            FolderHelper.get_output_directory(root_raw, sub_raw)
        return root_raw, sub_raw

    @staticmethod
    def find_thumbnail(base_path: str) -> str | None:
        """Find thumbnail file in the given directory."""
        if not base_path or not os.path.isdir(base_path):
            return None

        thumbnail_names = ["thumbnail.png", "thumbnail.webp", "thumbnail.jpg", "thumbnail.jpeg"]

        for name in thumbnail_names:
            full_path = os.path.join(base_path, name)
            if os.path.isfile(full_path):
                return full_path

        return None


# Web API endpoints for thumbnail functionality
async def check_thumbnail_endpoint(request):
    """API endpoint to check if thumbnail exists."""
    try:
        data = await request.json()
        path = data.get("path", "")

        if not path:
            return web.json_response({"found": False})

        # Sanitize and resolve the path
        safe_path = FolderHelper.sanitize_full_path(path)
        if not safe_path or not os.path.isdir(safe_path):
            return web.json_response({"found": False})

        # Look for thumbnail
        thumbnail_path = VoxtaOutputFolder.find_thumbnail(safe_path)

        if thumbnail_path:
            return web.json_response({"found": True, "thumbnail_path": thumbnail_path})
        else:
            return web.json_response({"found": False})

    except Exception as e:
        print(f"[VoxtaOutputFolder] Error in check_thumbnail_endpoint: {e}")
        return web.json_response({"found": False})


async def serve_thumbnail_endpoint(request):
    """API endpoint to serve thumbnail images."""
    try:
        thumbnail_path = request.query.get("path", "")

        if not thumbnail_path or not os.path.isfile(thumbnail_path):
            return web.Response(status=404, text="Thumbnail not found")

        # Security check - ensure it's actually a thumbnail file
        filename = os.path.basename(thumbnail_path).lower()
        if not any(filename.startswith("thumbnail.") and filename.endswith(ext) for ext in [".png", ".webp", ".jpg", ".jpeg"]):
            return web.Response(status=403, text="Access denied")

        # Determine content type
        content_type = "image/png"
        if filename.endswith(".webp"):
            content_type = "image/webp"
        elif filename.endswith((".jpg", ".jpeg")):
            content_type = "image/jpeg"

        # Serve the file
        with open(thumbnail_path, "rb") as f:
            data = f.read()

        return web.Response(body=data, content_type=content_type)

    except Exception as e:
        print(f"[VoxtaOutputFolder] Error in serve_thumbnail_endpoint: {e}")
        return web.Response(status=500, text="Server error")


def register_thumbnail_routes():
    if server.PromptServer.instance:
        server.PromptServer.instance.routes.post("/voxta/check_thumbnail")(check_thumbnail_endpoint)
        server.PromptServer.instance.routes.get("/voxta/thumbnail")(serve_thumbnail_endpoint)


register_thumbnail_routes()

NODE_CLASS_MAPPINGS = {"VoxtaOutputFolder": VoxtaOutputFolder}
NODE_DISPLAY_NAME_MAPPINGS = {"VoxtaOutputFolder": "Voxta: Output Folder"}

__all__ = [
    "VoxtaOutputFolder",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]

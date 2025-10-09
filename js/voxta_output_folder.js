import { app } from "/scripts/app.js";

app.registerExtension({
  name: "Voxta.OutputFolder",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    const matchesTarget = (
      nodeData?.name === "VoxtaOutputFolder" ||
      nodeData?.name === "Voxta: Output Folder"
    );

    if (matchesTarget) {
      console.log(`[Voxta.OutputFolder] Matched target node: ${nodeData.name}. Applying custom widget.`);

      const onNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        onNodeCreated?.apply(this, arguments);

        // Create our custom widget and add it to the node
        const widget = {
          type: "custom",
          name: "voxta_thumbnail_widget",
          draw: (ctx, node, widget_width, y, widget_height) => {
            // The widget's draw function, which is called by LiteGraph
            // We can draw anything we want into the canvas context (ctx)
            const margin = 10;
            const width = widget_width - margin * 2;
            const height = 150; // Fixed height for our thumbnail

            // Draw the image if it's loaded
            if (widget.image && widget.image.complete) {
              const ratio = widget.image.width / widget.image.height;
              let w = width;
              let h = w / ratio;
              if (h > height) {
                h = height;
                w = h * ratio;
              }
              const x = margin + (width - w) / 2;
              ctx.drawImage(widget.image, x, y + (height - h) / 2, w, h);
            } else {
              // Draw a placeholder/status text
              ctx.fillStyle = "#333";
              ctx.fillRect(margin, y, width, height);
              ctx.fillStyle = "#888";
              ctx.font = "14px Arial";
              ctx.textAlign = "center";
              ctx.fillText(widget.status || "...", widget_width / 2, y + height / 2);
            }

            // Set the widget height
            node.setSize([node.size[0], Math.max(node.size[1], y + height + margin)]);
            return height + margin;
          },
          // Custom properties for our widget
          image: null,
          status: "Initializing...",
        };

        this.addCustomWidget(widget);

        // Function to update the thumbnail
        const updateThumbnail = () => {
          const outputPath = this.widgets.find(w => w.name === "output_path")?.value || "";
          const subfolder = this.widgets.find(w => w.name === "subfolder")?.value || "";

          if (!outputPath.trim()) {
            widget.status = "Enter path";
            widget.image = null;
            this.setDirtyCanvas(true, true);
            return;
          }

          widget.status = "Loading...";
          this.setDirtyCanvas(true, true);

          let basePath = outputPath.trim();
          const commonSubfolders = ['Assets', 'Avatars', 'Audio', 'Portraits'];
          for (const folder of commonSubfolders) {
            if (basePath.endsWith('\\' + folder) || basePath.endsWith('/' + folder)) {
              const lastSeparator = Math.max(basePath.lastIndexOf('\\'), basePath.lastIndexOf('/'));
              if (lastSeparator > 0) {
                basePath = basePath.substring(0, lastSeparator);
              }
              break;
            }
          }

          fetch('/voxta/check_thumbnail', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: basePath })
          })
          .then(response => response.json())
          .then(data => {
            if (data.found && data.thumbnail_path) {
              widget.status = "Image Found";
              widget.image = new Image();
              widget.image.src = `/voxta/thumbnail?path=${encodeURIComponent(data.thumbnail_path)}`;
              widget.image.onload = () => {
                this.setDirtyCanvas(true, true);
              };
            } else {
              widget.status = "Not a Voxta character";
              widget.image = null;
              this.setDirtyCanvas(true, true);
            }
          })
          .catch(error => {
            widget.status = "Error";
            widget.image = null;
            this.setDirtyCanvas(true, true);
            console.error('[Voxta.OutputFolder] Error checking thumbnail:', error);
          });
        };

        // Hook into input changes
        const outputPathWidget = this.widgets.find(w => w.name === "output_path");
        if (outputPathWidget) {
          const origCallback = outputPathWidget.callback;
          outputPathWidget.callback = (...args) => {
            origCallback?.apply(this, args);
            updateThumbnail();
          };
        }

        const subfolderWidget = this.widgets.find(w => w.name === "subfolder");
        if (subfolderWidget) {
          const origCallback = subfolderWidget.callback;
          subfolderWidget.callback = (...args) => {
            origCallback?.apply(this, args);
            updateThumbnail();
          };
        }

        // Initial check
        setTimeout(updateThumbnail, 100);
      };
    }
  }
});

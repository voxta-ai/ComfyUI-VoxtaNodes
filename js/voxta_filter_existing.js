import { app } from "/scripts/app.js";

app.registerExtension({
  name: "Voxta.FilterExistingCombinations",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData?.name?.includes("Voxta") && !nodeType.__voxtaLogged) {
      console.log("[VoxtaFilterExistingCombinations] Observed node registration:", nodeData);
      nodeType.__voxtaLogged = true;
    }

    const matchesTarget = (
      nodeData?.name === "VoxtaFilterExistingCombinations" ||
      nodeData?.name === "Voxta: Filter Existing Combinations" ||
      /Filter Existing Combinations/i.test(nodeData?.name || "")
    );

    if (matchesTarget) {
      const origOnNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        origOnNodeCreated?.apply(this, arguments);
        if (!this.widgets) this.widgets = [];
        let widget = this.widgets.find((w) => ["Summary", "execution_summary_widget"].includes(w.name));
        if (!widget) {
          widget = this.addWidget("text", "Summary", "Waiting for execution...");
          widget.serialize = false;
        } else if (widget.name === "execution_summary_widget") {
          widget.name = "Summary";
        }
      };

      const prevExecuted = nodeType.prototype.onExecuted;
      nodeType.prototype.onExecuted = function (message) {
        prevExecuted?.apply(this, arguments);

        if (!this.__voxtaLoggedMessageOnce) {
          console.log("[VoxtaFilterExistingCombinations] onExecuted message received:", message);
          this.__voxtaLoggedMessageOnce = true;
        }

        const candidates = [];
        if (message) {
          candidates.push(message.ui);
          candidates.push(message.UI);
          candidates.push(message.output);
          candidates.push(message.result); // raw dict return pattern
          if (message.result && typeof message.result === 'object') {
            candidates.push(message.result.ui); // nested ui (just in case)
          }
          if (Array.isArray(message.outputs)) {
            for (const o of message.outputs) candidates.push(o?.ui || o);
          }
          candidates.push(message);
        }

        let ui = null;
        for (const c of candidates) {
          if (c && (c.summary || c.skipped || c.kept)) {
            ui = c;
            break;
          }
        }

        let widget = this.widgets?.find((w) => ["Summary", "execution_summary_widget"].includes(w.name));
        if (!widget) {
          widget = this.addWidget("text", "Summary", "Waiting for execution...");
          widget.serialize = false;
        }

        if (!ui) {
          widget.value = "(No UI payload yet)";
          this.setDirtyCanvas(true, true);
          console.debug("[VoxtaFilterExistingCombinations] No UI-like payload found. Candidates inspected:", candidates);
          return;
        }

        let summaryText = "";
        if (Array.isArray(ui.summary)) summaryText = ui.summary.join(" ");
        else if (typeof ui.summary === "string") summaryText = ui.summary;

        if (!summaryText) {
          widget.value = "(Summary missing in UI payload)";
          this.setDirtyCanvas(true, true);
          console.debug("[VoxtaFilterExistingCombinations] UI payload present but summary missing/empty", ui);
          return;
        }

        const skipped = Array.isArray(ui.skipped) ? ui.skipped[0] : ui.skipped ?? "?";
        const kept = Array.isArray(ui.kept) ? ui.kept[0] : ui.kept ?? "?";
        widget.value = `${summaryText} (Skipped: ${skipped}, Kept: ${kept})`;
        if (widget.name === "execution_summary_widget") widget.name = "Summary";
        this.setDirtyCanvas(true, true);
      };
    }
  },
});

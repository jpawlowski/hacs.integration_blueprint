/**
 * Runs the shared .agents/hooks/ scripts for OpenCode 2, as .claude/settings.json and .codex/hooks.json do for their
 * agents. Both scripts receive the Claude-shaped payload they are written against.
 */

import { execFile } from "node:child_process";

const EDIT_TOOLS = new Set(["edit", "write", "patch"]);

const runHook = (root, script, payload) =>
  new Promise((resolve) => {
    const child = execFile("bash", [`${root}/${script}`], { cwd: root }, (error, stdout, stderr) => {
      resolve({ stdout, stderr: stderr || error?.message || "", exitCode: error ? 1 : 0 });
    });
    child.stdin.on("error", () => {});
    child.stdin.end(JSON.stringify(payload));
  });

export default {
  id: "agent-hooks",
  async setup(ctx) {
    const root = ctx.location.project.directory;

    await ctx.tool.hook("execute.before", async (event) => {
      if (event.tool !== "shell") return;
      const { stderr, exitCode } = await runHook(root, ".agents/hooks/pre-push-check.sh", { tool_input: event.input });
      if (exitCode !== 0) {
        throw new Error(stderr.trim() || "the push command was blocked by .agents/hooks/pre-push-check.sh");
      }
    });

    await ctx.tool.hook("execute.after", async (event) => {
      if (event.status !== "completed" || !EDIT_TOOLS.has(event.tool)) return;
      const { stdout } = await runHook(root, ".agents/hooks/remind-dependency-sync.sh", { tool_input: event.input });
      let additionalContext;
      try {
        additionalContext = JSON.parse(stdout)?.hookSpecificOutput?.additionalContext;
      } catch {
        return;
      }
      if (!additionalContext) return;
      const content = event.result.content;
      event.result = {
        ...event.result,
        content:
          typeof content === "string"
            ? `${content}\n\n${additionalContext}`
            : [...(content ?? []), { type: "text", text: additionalContext }],
      };
    });
  },
};

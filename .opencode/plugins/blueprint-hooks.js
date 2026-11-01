/**
 * Ports the blueprint's Claude Code hooks (.claude/settings.json) to the OpenCode 2 plugin API.
 *
 * - `tool.execute.before` (shell): runs `.agents/hooks/pre-push-check.sh`, which gates `git push`
 *   on a clean worktree, the checked-out HEAD refspec and a green `script/lint-check` +
 *   `script/type-check` run. Blocking works by throwing, which fails the tool call with the
 *   script's reason.
 * - `tool.execute.after` (edit/write/patch): runs `.agents/hooks/remind-dependency-sync.sh` and
 *   appends its reminder to the tool result when exactly one side of the
 *   manifest.json/requirements.txt dependency pair was edited.
 *
 * Both hook scripts are the single source of truth and receive the same Claude-shaped payload
 * they get from Claude Code, so the two agents stay in sync on policy.
 */

import { spawn } from "node:child_process";

const EDIT_TOOLS = new Set(["edit", "write", "patch"]);

const runHook = (root, script, payload) =>
  new Promise((resolve) => {
    const child = spawn("bash", [`${root}/${script}`], {
      cwd: root,
      stdio: ["pipe", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("error", (error) => {
      resolve({ stdout: "", stderr: error.message, exitCode: 1 });
    });
    child.on("close", (code) => {
      resolve({ stdout, stderr, exitCode: code ?? 0 });
    });
    child.stdin.on("error", () => {});
    child.stdin.end(JSON.stringify(payload));
  });

export default {
  id: "hacs.integration_blueprint-hooks",
  async setup(ctx) {
    const root = ctx.location.project.directory;

    await ctx.tool.hook("execute.before", async (event) => {
      if (event.tool !== "shell") return;
      const command = event.input?.command;
      // Cheap pre-filter; the hook script does the real parsing and passes every non-push
      // command through.
      if (typeof command !== "string" || !command.includes("push")) return;
      const { stderr, exitCode } = await runHook(root, ".agents/hooks/pre-push-check.sh", {
        tool_input: { command },
        cwd: root,
      });
      if (exitCode !== 0) {
        throw new Error(stderr.trim() || "the push command was blocked by .agents/hooks/pre-push-check.sh");
      }
    });

    await ctx.tool.hook("execute.after", async (event) => {
      if (event.status !== "completed" || !EDIT_TOOLS.has(event.tool)) return;
      const { stdout } = await runHook(root, ".agents/hooks/remind-dependency-sync.sh", {
        tool_input: event.input ?? {},
      });
      if (!stdout.trim()) return;
      try {
        const additionalContext = JSON.parse(stdout)?.hookSpecificOutput?.additionalContext;
        if (!additionalContext) return;
        const content = event.result.content;
        event.result = {
          ...event.result,
          content:
            typeof content === "string"
              ? `${content}\n\n${additionalContext}`
              : [...(content ?? []), { type: "text", text: additionalContext }],
        };
      } catch {
        // Malformed hook output is not worth failing the tool over.
      }
    });
  },
};

// Thin VS Code shim (VS Code requires JS/TS). All logic lives in ../cli.py and ../core.
const vscode = require("vscode");
const path = require("path");
const { execFile } = require("child_process");

function activate(context) {
  const diagnostics = vscode.languages.createDiagnosticCollection("mistakeTracker");
  const status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 10);
  status.command = "mistakeTracker.openDashboard";
  status.text = "$(bug) Mistakes: --";
  status.show();
  context.subscriptions.push(diagnostics, status);

  const cfg = () => vscode.workspace.getConfiguration("mistakeTracker");
  const cli = path.join(context.extensionPath, "..", "cli.py");

  function analyse(doc) {
    if (doc.languageId !== "python") return;
    execFile(cfg().get("pythonPath"), [cli, doc.fileName],
      { cwd: path.dirname(cli) }, (err, stdout, stderr) => {
        if (err) { status.text = "$(warning) Mistake Tracker error"; status.tooltip = stderr || err.message; return; }
        const out = JSON.parse(stdout);
        diagnostics.set(doc.uri, out.issues.map(i => {
          const line = Math.max(0, i.line - 1);
          const range = doc.lineAt(Math.min(line, doc.lineCount - 1)).range;
          const repeat = i.times_made > 1 ? ` (you have made this ${i.times_made} times)` : "";
          const d = new vscode.Diagnostic(range, `${i.message}${repeat}. Fix: ${i.hint}`, vscode.DiagnosticSeverity.Warning);
          d.source = "Mistake Tracker"; d.code = i.rule; return d;
        }));
        const s = out.stats;
        status.text = `$(bug) Score ${s.score ?? "--"} | ${s.status}`;
        status.tooltip = `Total mistakes: ${s.total_mistakes}. Click to open the dashboard.`;
      });
  }

  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(analyse),
    vscode.workspace.onDidOpenTextDocument(analyse),
    vscode.commands.registerCommand("mistakeTracker.openDashboard",
      () => vscode.env.openExternal(vscode.Uri.parse(cfg().get("dashboardUrl"))))
  );
  vscode.workspace.textDocuments.forEach(analyse);
}
exports.activate = activate;
exports.deactivate = () => {};

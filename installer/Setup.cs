using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Windows.Forms;

internal static class Setup
{
    private static void Extract(string resource, string destination)
    {
        using (Stream input = Assembly.GetExecutingAssembly().GetManifestResourceStream(resource))
        {
            if (input == null) throw new InvalidOperationException("The setup package is incomplete.");
            using (FileStream output = new FileStream(destination, FileMode.CreateNew, FileAccess.Write)) input.CopyTo(output);
        }
    }

    [STAThread]
    private static int Main(string[] args)
    {
        string directory = Path.Combine(Path.GetTempPath(), "WriterSetup-" + Guid.NewGuid().ToString("N"));
        string script = Path.Combine(directory, "Install-Writer.ps1");
        string payload = Path.Combine(directory, "payload.zip");
        try
        {
            Directory.CreateDirectory(directory);
            Extract("writer.setup", script);
            Extract("writer.payload", payload);
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System), @"WindowsPowerShell\v1.0\powershell.exe");
            start.Arguments = "-NoProfile -ExecutionPolicy Bypass -File \"" + script + "\"";
            bool verify = args.Length == 2 && args[0] == "--verify-dir";
            if (args.Length > 0 && !verify) throw new ArgumentException("Unsupported setup option.");
            if (verify)
            {
                if (!Path.IsPathRooted(args[1]) || args[1].Contains("\"")) throw new ArgumentException("Invalid verification directory.");
                start.Arguments += " -VerifyDestination \"" + args[1] + "\"";
            }
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.RedirectStandardError = true;
            using (Process process = Process.Start(start))
            {
                string error = process.StandardError.ReadToEnd();
                process.WaitForExit();
                if (process.ExitCode != 0 && !verify) MessageBox.Show("Setup could not start: " + error, "Writer & Translator Setup", MessageBoxButtons.OK, MessageBoxIcon.Error);
                if (process.ExitCode != 0 && verify) Console.Error.WriteLine(error);
                return process.ExitCode;
            }
        }
        catch (Exception error)
        {
            MessageBox.Show("Setup could not start: " + error.Message, "Writer & Translator Setup", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
        finally
        {
            try { if (File.Exists(script)) File.Delete(script); if (File.Exists(payload)) File.Delete(payload); if (Directory.Exists(directory)) Directory.Delete(directory); }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
        }
    }
}

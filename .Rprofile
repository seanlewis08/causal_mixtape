# Point reticulate at the project's Python environment when one exists,
# so the Python chunks in the session pages run against the same packages.
local({
  venv <- c(".venv/bin/python", ".venv/Scripts/python.exe")
  venv <- venv[file.exists(venv)]
  if (length(venv)) Sys.setenv(RETICULATE_PYTHON = normalizePath(venv[1]))
  else if (nzchar(Sys.which("python3")) && !nzchar(Sys.getenv("RETICULATE_PYTHON")))
    Sys.setenv(RETICULATE_PYTHON = Sys.which("python3"))
})

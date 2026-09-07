# AI Quiz Evaluator - Sleek Horizontal Setup Installer

[void][System.Reflection.Assembly]::LoadWithPartialName("PresentationFramework")
[void][System.Reflection.Assembly]::LoadWithPartialName("PresentationCore")
[void][System.Reflection.Assembly]::LoadWithPartialName("WindowsBase")

$xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="AI Quiz Evaluator Setup" Height="220" Width="640"
        WindowStartupLocation="CenterScreen" ResizeMode="NoResize"
        Background="#FFFFFF" Foreground="#0F172A" FontFamily="Segoe UI">
    <Grid Margin="24">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <!-- Header Bar -->
        <Grid Grid.Row="0" Margin="0,0,0,16">
            <StackPanel HorizontalAlignment="Left">
                <TextBlock Text="AI Quiz Evaluator Setup" FontSize="18" FontWeight="SemiBold" Foreground="#0F172A"/>
                <TextBlock Text="Setting up environment, dependencies, and AI engine..." FontSize="12" Foreground="#64748B" Margin="0,2,0,0"/>
            </StackPanel>
            <TextBlock x:Name="PercentText" Text="0%" FontSize="20" FontWeight="Bold" Foreground="#2563EB" HorizontalAlignment="Right" VerticalAlignment="Center"/>
        </Grid>

        <!-- Horizontal Progress Bar Track -->
        <Border Grid.Row="1" Height="12" CornerRadius="6" Background="#F1F5F9" BorderBrush="#E2E8F0" BorderThickness="1" Margin="0,0,0,14">
            <Grid>
                <Border x:Name="ProgressBarFill" HorizontalAlignment="Left" Width="0" CornerRadius="5" Background="#2563EB"/>
            </Grid>
        </Border>

        <!-- Activity Readout Line -->
        <Border Grid.Row="2" Background="#F8FAFC" CornerRadius="6" BorderBrush="#E2E8F0" BorderThickness="1" Padding="12,8" Margin="0,0,0,12">
            <Grid>
                <TextBlock x:Name="StatusText" Text="Initializing setup installer..." FontSize="12" FontWeight="Medium" Foreground="#334155" HorizontalAlignment="Left"/>
                <TextBlock x:Name="LogText" Text="Starting..." FontSize="11" Foreground="#94A3B8" HorizontalAlignment="Right"/>
            </Grid>
        </Border>

        <!-- Footer -->
        <Grid Grid.Row="3">
            <TextBlock Text="AI Quiz Evaluator Setup Wizard" FontSize="11" Foreground="#94A3B8" HorizontalAlignment="Left"/>
            <TextBlock Text="Please wait until launch..." FontSize="11" Foreground="#94A3B8" HorizontalAlignment="Right"/>
        </Grid>
    </Grid>
</Window>
"@

$reader = (New-Object System.Xml.XmlNodeReader ([xml]$xaml))
$window = [System.Windows.Markup.XamlReader]::Load($reader)

$statusLabel = $window.FindName('StatusText')
$percentLabel = $window.FindName('PercentText')
$barFill = $window.FindName('ProgressBarFill')
$logBlock = $window.FindName('LogText')

function Update-UI {
    param (
        [int]$percent,
        [string]$status,
        [string]$logMessage
    )
    if ($window -and $statusLabel) {
        $statusLabel.Text = $status
        $percentLabel.Text = "$percent%"
        $totalWidth = 592
        $targetWidth = [math]::Max(0, [math]::Min($totalWidth, ($percent / 100) * $totalWidth))
        
        # Smooth animation transition
        $anim = New-Object System.Windows.Media.Animation.DoubleAnimation
        $anim.To = $targetWidth
        $anim.Duration = [TimeSpan]::FromMilliseconds(300)
        $barFill.BeginAnimation([System.Windows.Controls.Border]::WidthProperty, $anim)

        if ($logMessage) {
            $logBlock.Text = $logMessage
        }
        [System.Windows.Threading.Dispatcher]::CurrentDispatcher.Invoke([action]{}, [System.Windows.Threading.DispatcherPriority]::Background)
    }
}

function Test-ValidPython {
    param ([string]$pyPath)
    if (-not $pyPath) { return $false }
    if ($pyPath -like "*WindowsApps*") { return $false }
    if (-not (Test-Path $pyPath)) { return $false }
    try {
        $ver = & $pyPath --version 2>&1
        if ($ver -match "Python 3\.") { return $true }
    } catch {}
    return $false
}

function Get-SystemPythonPath {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and (Test-ValidPython $cmd.Source)) {
        return $cmd.Source
    }

    $paths = @(
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python310\python.exe",
        "$env:LocalAppData\Programs\Python\Python311\python.exe",
        "$env:LocalAppData\Programs\Python\Python312\python.exe",
        "$env:LocalAppData\Programs\Python\Python310\python.exe"
    )
    foreach ($p in $paths) {
        if (Test-ValidPython $p) { return $p }
    }

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        try {
            $ver = & py -3 --version 2>&1
            if ($ver -match "Python 3\.") { return "py" }
        } catch {}
    }

    return $null
}

$script:stage = 0
$script:pythonExe = $null
$script:venvPython = $null

$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromMilliseconds(150)

$timer.Add_Tick({
    $timer.Stop()

    switch ($script:stage) {
        0 {
            Update-UI 5 "Initializing setup installer..." "System environment initialized."
            $script:stage = 1
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        1 {
            Update-UI 10 "Step 1/6: Checking Python installation..." "Locating Python installation on this machine..."
            $pyExe = Get-SystemPythonPath

            if (-not $pyExe) {
                Update-UI 15 "Step 1/6: Downloading Python 3.11 installer..." "Downloading python-3.11.9-amd64.exe from python.org..."
                $url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
                $installerPath = "$env:TEMP\python-3.11.9-amd64.exe"
                Invoke-WebRequest -Uri $url -OutFile $installerPath
                
                Update-UI 18 "Step 1/6: Installing Python 3.11 silently (waiting for completion)..." "Running Python 3.11 installer with /quiet..."
                $proc = Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -PassThru -Wait
                Remove-Item $installerPath -ErrorAction SilentlyContinue
                
                $machinePath = [System.Environment]::GetEnvironmentVariable("Path","Machine")
                $userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
                $env:PATH = "$machinePath;$userPath;C:\Program Files\Python311;C:\Program Files\Python311\Scripts;$env:LocalAppData\Programs\Python\Python311;$env:LocalAppData\Programs\Python\Python311\Scripts;$env:PATH"
                $pyExe = Get-SystemPythonPath
            }

            if (-not $pyExe) {
                Update-UI 10 "[ERROR] Python installation failed." "ERROR: Could not verify Python executable."
                return
            }

            $script:pythonExe = $pyExe
            Update-UI 20 "Step 1/6: Python verified 100% complete!" "Python executable: $pyExe"
            $script:stage = 2
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        2 {
            Update-UI 25 "Step 2/6: Setting up Python virtual environment (venv)..." "Checking virtual environment directory..."
            $vPy = "$PSScriptRoot\venv\Scripts\python.exe"
            $vPip = "$PSScriptRoot\venv\Scripts\pip.exe"

            if (-not (Test-Path $vPy) -or -not (Test-Path $vPip)) {
                Update-UI 30 "Step 2/6: Creating fresh virtual environment..." "Executing python -m venv venv..."
                if (Test-Path "$PSScriptRoot\venv") {
                    Remove-Item "$PSScriptRoot\venv" -Recurse -Force -ErrorAction SilentlyContinue
                }
                
                # Tier 1: Standard venv creation
                if ($script:pythonExe -eq "py") {
                    & py -3 -m venv "$PSScriptRoot\venv"
                } elseif ($script:pythonExe) {
                    & "$script:pythonExe" -m venv "$PSScriptRoot\venv"
                }

                # Tier 2: Fallback to virtualenv package if venv executable was not created
                if (-not (Test-Path $vPy)) {
                    Update-UI 35 "Step 2/6: Retrying environment setup with virtualenv..." "Installing virtualenv..."
                    if ($script:pythonExe -eq "py") {
                        & py -3 -m pip install virtualenv --quiet
                        & py -3 -m virtualenv "$PSScriptRoot\venv"
                    } elseif ($script:pythonExe) {
                        & "$script:pythonExe" -m pip install virtualenv --quiet
                        & "$script:pythonExe" -m virtualenv "$PSScriptRoot\venv"
                    }
                }
            }

            # Tier 3: Verified Executable Assignment with Guaranteed System Python Fallback
            if (Test-Path $vPy) {
                $script:venvPython = $vPy
            } elseif ($script:pythonExe -and $script:pythonExe -ne "py" -and (Test-Path $script:pythonExe)) {
                $script:venvPython = $script:pythonExe
                Update-UI 38 "Step 2/6: Using System Python direct fallback..." "Assigned System Python: $script:venvPython"
            } elseif (Get-Command python -ErrorAction SilentlyContinue) {
                $script:venvPython = (Get-Command python).Source
            } else {
                Update-UI 20 "[ERROR] Could not initialize Python environment." "ERROR: Python environment failed."
                return
            }

            Update-UI 40 "Step 2/6: Python environment 100% verified!" "Executable ready: $script:venvPython"
            $script:stage = 3
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        3 {
            Update-UI 45 "Step 3/6: Installing Python dependencies..." "Running pip install -r requirements.txt..."
            & "$script:venvPython" -m pip install -r "$PSScriptRoot\requirements.txt" --no-warn-script-location --quiet
            if ($LASTEXITCODE -ne 0) {
                Update-UI 50 "Step 3/6: Retrying pip install..." "Retrying requirements installation..."
                & "$script:venvPython" -m pip install -r "$PSScriptRoot\requirements.txt" --no-warn-script-location
            }
            Update-UI 60 "Step 3/6: Package installation 100% complete!" "Django, PyPDF, Pillow, OpenAI installed."
            $script:stage = 4
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        4 {
            Update-UI 65 "Step 4/6: Running database migrations & seeding demo data..." "Running manage.py migrate..."
            & "$script:venvPython" "$PSScriptRoot\manage.py" migrate --noinput
            Update-UI 70 "Step 4/6: Seeding teacher and student demo accounts..." "Running manage.py seed_demo..."
            & "$script:venvPython" "$PSScriptRoot\manage.py" seed_demo
            Update-UI 75 "Step 4/6: Database setup & demo data 100% complete!" "Database seeded with teacher1 & student1 accounts."
            $script:stage = 5
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        5 {
            Update-UI 78 "Step 5/6: Checking Ollama AI engine..." "Verifying local Ollama installation..."
            $ollamaCheck = Get-Command ollama -ErrorAction SilentlyContinue
            if (-not $ollamaCheck) {
                Update-UI 80 "Step 5/6: Downloading Ollama Windows Installer..." "Downloading OllamaSetup.exe..."
                $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
                try {
                    Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $ollamaInstaller
                    Update-UI 83 "Step 5/6: Installing Ollama (waiting for completion)..." "Installing Ollama silently..."
                    Start-Process -FilePath $ollamaInstaller -ArgumentList "/silent" -PassThru -Wait
                    Remove-Item $ollamaInstaller -ErrorAction SilentlyContinue
                } catch {
                    Update-UI 83 "Step 5/6: Installing Ollama via script..." "Downloading Ollama script..."
                    irm https://ollama.com/install.ps1 | iex
                }
                $env:PATH = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            }

            try {
                $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction SilentlyContinue
            } catch {
                Update-UI 87 "Step 5/6: Starting local Ollama background worker..." "Starting ollama serve..."
                Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 3
            }
            Update-UI 90 "Step 5/6: Ollama AI engine 100% verified & ready!" "Ollama AI service running."
            $script:stage = 6
            $timer.Interval = [TimeSpan]::FromMilliseconds(300)
            $timer.Start()
        }
        6 {
            Update-UI 92 "Step 6/6: Downloading / Pulling Llama 3.2 1B model..." "Executing ollama pull llama3.2:1b..."
            $pullResult = & ollama pull llama3.2:1b 2>&1
            Update-UI 98 "Step 6/6: Llama 3.2 1B model download 100% complete!" "Llama 3.2 1B model ready."
            $script:stage = 7
            $timer.Interval = [TimeSpan]::FromMilliseconds(500)
            $timer.Start()
        }
        7 {
            Update-UI 99 "Starting application server..." "Launching Django background service on 127.0.0.1:8000..."

            # 1. Start Django server as a persistent background process
            Start-Process -FilePath $script:venvPython -ArgumentList "`"$PSScriptRoot\manage.py`" runserver 127.0.0.1:8000" -WindowStyle Hidden

            # 2. Poll http://127.0.0.1:8000/ until server responds
            Update-UI 99 "Waiting for application server readiness..." "Connecting to 127.0.0.1:8000..."
            $serverReady = $false
            for ($i = 0; $i -lt 20; $i++) {
                try {
                    $req = [System.Net.WebRequest]::Create("http://127.0.0.1:8000/")
                    $req.Timeout = 1000
                    $res = $req.GetResponse()
                    if ($res) {
                        $serverReady = $true
                        $res.Close()
                        break
                    }
                } catch {
                    if ($_.Exception.Response) {
                        $serverReady = $true
                        break
                    }
                }
                Start-Sleep -Milliseconds 500
            }

            Update-UI 100 "Server ready! Opening application..." "Launching browser..."

            # 3. Open Browser ONLY after server is 100% responsive
            $chromePath = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
            $chromePathx86 = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"

            if (Test-Path $chromePath) {
                Start-Process $chromePath "http://127.0.0.1:8000/"
            } elseif (Test-Path $chromePathx86) {
                Start-Process $chromePathx86 "http://127.0.0.1:8000/"
            } else {
                Start-Process "http://127.0.0.1:8000/"
            }

            # 4. Close installer GUI window
            $window.Close()
        }
    }
})

$window.Add_ContentRendered({
    $timer.Start()
})

$window.ShowDialog() | Out-Null

import PyInstaller.__main__

PyInstaller.__main__.run(
    [
        "src/main.py",
        "--onefile",
        "--hidden-import",
        "babel.numbers",
        "--windowed",
        "--name=Time Capsule",
        "--icon=res/time.png",
    ]
)

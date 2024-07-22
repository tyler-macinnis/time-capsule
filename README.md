# Time Capsule

Application to help you track important dates and milestones.

## Setup Instructions

1. **Install Python**  
   Ensure Python is installed on your system. You can download it from [python.org](https://www.python.org/).

2. **Set Up a Virtual Environment**  
   Create a virtual environment with the command:

   ```bash
   python -m venv .venv
   ```

3. **Activate the Virtual Environment**  
   On Windows, activate the virtual environment with:

   ```bash
   .venv\Scripts\activate
   ```

   On Unix or MacOS, use:

   ```bash
   source .venv/bin/activate
   ```

4. **Update Pip**  
   Upgrade pip to the latest version:

   ```bash
   python -m pip install --upgrade pip
   ```

5. **Install Requirements**  
   Install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. **Run the Application**

   Start the application with:

   ```bash
   python src/main.py
   ```

## Update `requirements.txt`

To update `requirements.txt`, run the following command from within the virtual environment:

```bash
pipdeptree --warn silence > requirements.txt
```

## Update Dependencies

Dependencies can be updated using `pur`. Run the following command within the virtual environment:

```bash
pur
```

## Build a Windows Executable

To build a Windows executable, run the following command from within the virtual environment:

```bash
python build_release.py
```

## Attribution

[Dose icons created by Pixel perfect - Flaticon](https://www.flaticon.com/free-icons/dose "dose icons")

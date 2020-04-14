# Script to get info from RescueTime

## How To Use
1. Get your API key from [RescueTime](https://www.rescuetime.com/anapi/manage).
It will be good to create a new API key.
2. Save it to:
    - C:\\Users\\%username%\\.rescuetime (on Windows)
    - ~/.local/share/rescuetime.key (on Linux and Windows)
    - any other path. Pass this path as the `-k` parameter to the script
3. Install dependecies via pip:
```bash
pip install --user colorama requests
```
4. Run the script
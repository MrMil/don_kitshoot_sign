# don_kitshoot_sign

## Initialize env

```sh
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run once

While the board is connected to the computer:

```sh
mpremote run main.py
```

## Send the code to the board

So it can run many times

```sh
mpremote cp main.py :main.py
```

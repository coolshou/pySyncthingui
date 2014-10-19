syncthingui
===========

SyncthinGUI Python3 Qt5 GUI for Syncthing !

- Python 3 + Qt 5, No Dependencies, easy to use, Minimalistic ~250 Lines.
- KISS, DRY, YAGNI, SingleFile, Async, CrossDesktop, CrossDistro, SelfUpdating !


![screenshot](https://raw.githubusercontent.com/juancarlospaco/syncthingui/master/syncthingui.jpg)


# Try it !:

```
wget -O - https://raw.githubusercontent.com/juancarlospaco/syncthingui/master/syncthingui.py | python3
```

# Install permanently on the system:

```
sudo apt-get install python3-pyqt5  # OR  sudo yum install python3-qt5  OR  sudo pacman -S python-pyqt5
sudo wget -O /usr/bin/syncthingui https://raw.githubusercontent.com/juancarlospaco/syncthingui/master/syncthingui.py
sudo chmod +x /usr/bin/syncthingui
syncthingui
```


# Ubuntu and Mint:

- Ubuntu, Mint, and derivatives have to change the default scheduler. **This step is OPTIONAL** but recommended.
- Since it uses DeadLine that tries everything ASAP BUT ignores priorities (nice and ionice dont really work there).
- Asuming your Disk is **sda** run on a Bash Terminal Command Line:

```bash
echo cfq | sudo tee /sys/block/sda/queue/scheduler
```


# Requisites:

- [Python 3.x](https://www.python.org "Python Homepage")
- [PyQt 5.x](http://www.riverbankcomputing.co.uk/software/pyqt/download5 "PyQt5 Homepage")


Donate, Charityware :
---------------------

- [Charityware](https://en.wikipedia.org/wiki/Donationware) is a licensing model that supplies fully operational unrestricted software to the user and requests an optional donation be paid to a third-party beneficiary non-profit. The amount of donation may be left to the discretion of the user. Its GPL-compatible and Enterprise ready.
- If you want to Donate please [click here](http://www.icrc.org/eng/donations/index.jsp) or [click here](http://www.atheistalliance.org/support-aai/donate) or [click here](http://www.msf.org/donate) or [click here](http://richarddawkins.net/) or [click here](http://www.supportunicef.org/) or [click here](http://www.amnesty.org/en/donate)

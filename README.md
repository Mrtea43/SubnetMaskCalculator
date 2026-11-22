# Subnet Mask Calculator

An IPv4 subnet calculator built while preparing for the CCNA.

## Run it

- **Python desktop app:** Run `python subnet_calculator.py` with Python 3 and Tkinter.
- **Browser version:** Open `index.html` directly in a browser.

Enter an IPv4 address and select a subnet mask, mask length, or any of the linked dropdown values. The calculator updates the subnet ID, broadcast address, usable host range, wildcard mask, and bit map as you work.

## How it works

The network class supplies the default prefix (A = /8, B = /16, C = /24). The selected prefix determines how many bits are used for subnetting and how many remain for hosts.

The subnet ID is the first address in the block, and the broadcast field shows its last address. For prefixes through /30, the usable range excludes those two addresses. A /31 has two usable endpoints, and a /32 contains a single address.

For example, `10.0.0.0/16` has mask `255.255.0.0`, wildcard `0.0.255.255`, and a usable range of `10.0.0.1` through `10.0.255.254`.
